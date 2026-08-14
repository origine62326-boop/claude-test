"""
損切りトレードを、エントリー時点の相場構造（トレンド成熟度・ボラティリティ・EMA間距離の
収束/拡散）で分類し、どの構造タイプの失敗が多いかを集計する。

目的: 新しいEntry側特徴量を探索する前に、まず「どの失敗パターンが多いか」を把握し、
場当たり的に指標を試すのではなく失敗の実態から出発する（結果を見た後の特徴量選びを避ける）。

【この分析が答えないこと】
- 「この特徴量を使えば勝てる」という主張はしない。あくまで失敗トレードの構造の記述(Observation)。
- ADXは`DIAG-001`で検証に失敗し除外されているため、本分析では使用しない
  (`analysis/feature_extraction.py`のdocstring・`OBSERVATION_REGISTRY.md`のO-002参照)。

【分類軸の定義（恣意的に後から変えない）】
- trend_duration_bars: entry判定バー(shift=1)から遡り、EAのGetTrendDirection()と同じ条件
  (close>slow && fast>mid && mid>slow、売りは不等号反転)が連続して成立していたバー数。
  トレンド成熟度の代理指標として使う。データ由来の三分位(tertile)で
  Fresh(浅い)/Established(中間)/Extended(長い)に区分する
- atr_quartile: ATR14(pips)のデータ由来四分位。Q1(低ボラ)〜Q4(高ボラ)
- ema_distance_direction: |EMA20-75間距離|の、直近5本前と比較した変化方向。
  拡大していればDiverging、縮小していればConverging
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from feature_extraction import compute_atr_series, compute_ema_series  # noqa: E402
from mfe_mae_reconstruction import load_h1_csv, reconstruct_trade  # noqa: E402
from parse_mt4_trades import parse_trades_html  # noqa: E402

PIP_SIZE = 0.01


def _trend_ok(direction: str, close: float, fast: float, mid: float, slow: float) -> bool:
    if direction == "buy":
        return close > slow and fast > mid and mid > slow
    return close < slow and fast < mid and mid < slow


def compute_trend_duration(bars: list[dict], decision_idx: int, direction: str,
                            ema20: list, ema75: list, ema200: list, closes: list,
                            max_lookback: int = 200) -> int | None:
    """decision_idxから遡り、同じトレンド条件が連続して成立していたバー数を数える。"""
    if decision_idx is None or decision_idx < 0:
        return None
    if ema20[decision_idx] is None or ema75[decision_idx] is None or ema200[decision_idx] is None:
        return None
    if not _trend_ok(direction, closes[decision_idx], ema20[decision_idx], ema75[decision_idx], ema200[decision_idx]):
        return 0
    count = 0
    i = decision_idx
    while i >= 0 and count < max_lookback:
        if ema20[i] is None or ema75[i] is None or ema200[i] is None:
            break
        if not _trend_ok(direction, closes[i], ema20[i], ema75[i], ema200[i]):
            break
        count += 1
        i -= 1
    return count


def quartile_labels(values: list[float]) -> list[str]:
    sorted_v = sorted(values)
    n = len(sorted_v)
    q1 = sorted_v[n // 4]
    q2 = sorted_v[n // 2]
    q3 = sorted_v[(3 * n) // 4]

    def label(v):
        if v <= q1:
            return "Q1(低)"
        if v <= q2:
            return "Q2"
        if v <= q3:
            return "Q3"
        return "Q4(高)"
    return [label(v) for v in values], (q1, q2, q3)


def tertile_labels(values: list[float]) -> tuple[list[str], tuple]:
    sorted_v = sorted(values)
    n = len(sorted_v)
    t1 = sorted_v[n // 3]
    t2 = sorted_v[(2 * n) // 3]

    def label(v):
        if v <= t1:
            return "Fresh(浅い)"
        if v <= t2:
            return "Established(中間)"
        return "Extended(長い)"
    return [label(v) for v in values], (t1, t2)


def build_rows(trades: list[dict], bars: list[dict]) -> list[dict]:
    bar_index = {b["time"]: i for i, b in enumerate(bars)}
    closes = [b["close"] for b in bars]
    ema20 = compute_ema_series(closes, 20)
    ema75 = compute_ema_series(closes, 75)
    ema200 = compute_ema_series(closes, 200)
    atr14 = compute_atr_series(bars, 14)

    rows = []
    for t in trades:
        if not t.get("close_time") or not t.get("open_time"):
            continue
        entry_time = datetime.fromisoformat(t["open_time"])
        entry_bar_time = entry_time.replace(minute=0, second=0, microsecond=0)
        entry_idx = bar_index.get(entry_bar_time)
        decision_idx = entry_idx - 1 if (entry_idx is not None and entry_idx > 0) else None

        row = {
            "ticket": t.get("ticket"),
            "direction": t.get("type"),
            "profit": t.get("profit"),
            "result": "win" if t.get("profit", 0) > 0 else "loss",
            "trend_duration_bars": None,
            "atr14_pips": None,
            "ema_distance_direction": None,
            "mfe_R": None,
        }

        if decision_idx is not None and decision_idx >= 200:
            row["trend_duration_bars"] = compute_trend_duration(
                bars, decision_idx, t["type"], ema20, ema75, ema200, closes)
            if atr14[decision_idx] is not None:
                row["atr14_pips"] = atr14[decision_idx] / PIP_SIZE
            if (decision_idx - 5 >= 0 and ema20[decision_idx] is not None and ema75[decision_idx] is not None
                    and ema20[decision_idx - 5] is not None and ema75[decision_idx - 5] is not None):
                dist_now = abs(ema20[decision_idx] - ema75[decision_idx])
                dist_prev = abs(ema20[decision_idx - 5] - ema75[decision_idx - 5])
                row["ema_distance_direction"] = "Diverging(拡散)" if dist_now > dist_prev else "Converging(収束)"

        mfe = reconstruct_trade(t, bars)
        row["mfe_R"] = mfe.get("mfe_R")

        rows.append(row)
    return rows


def main():
    import argparse
    import json
    from collections import Counter

    parser = argparse.ArgumentParser(description="損切りトレードの相場構造分類(Entry失敗パターンの記述、O-005)")
    parser.add_argument("report_htm")
    parser.add_argument("h1_csv")
    parser.add_argument("-o", "--output", help="トレード単位の結果を出力するJSONパス(省略可)")
    args = parser.parse_args()

    trades = parse_trades_html(args.report_htm)
    bars = load_h1_csv(args.h1_csv)
    rows = build_rows(trades, bars)

    available = [r for r in rows if r["trend_duration_bars"] is not None and r["atr14_pips"] is not None
                 and r["ema_distance_direction"] is not None]
    trend_labels, trend_cuts = tertile_labels([r["trend_duration_bars"] for r in available])
    atr_labels, atr_cuts = quartile_labels([r["atr14_pips"] for r in available])
    for r, tl, al in zip(available, trend_labels, atr_labels):
        r["trend_tertile"] = tl
        r["atr_quartile"] = al

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        print(f"保存しました: {args.output}")

    losses = [r for r in available if r["result"] == "loss"]
    print(f"n_total_available={len(available)} n_losses_available={len(losses)}")
    print(f"trend_duration_bars tertile cuts: {trend_cuts}")
    print(f"atr14_pips quartile cuts: {atr_cuts}")
    print()
    print("=== 損切りトレードの分布(全体) ===")
    print("trend_tertile:", dict(Counter(r["trend_tertile"] for r in losses)))
    print("atr_quartile:", dict(Counter(r["atr_quartile"] for r in losses)))
    print("ema_distance_direction:", dict(Counter(r["ema_distance_direction"] for r in losses)))
    for direction in ("buy", "sell"):
        sub = [r for r in losses if r["direction"] == direction]
        print(f"\n=== {direction} (n={len(sub)}) ===")
        print("trend_tertile:", dict(Counter(r["trend_tertile"] for r in sub)))
        print("atr_quartile:", dict(Counter(r["atr_quartile"] for r in sub)))
        print("ema_distance_direction:", dict(Counter(r["ema_distance_direction"] for r in sub)))


if __name__ == "__main__":
    main()

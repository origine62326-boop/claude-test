"""
トレンド成熟度(trend_duration_bars)を、固定バー数ではなく「その時点の相場に対する相対位置」
として表現し直し、固定閾値との構造的な安定性を比較する。

背景: `H006`/`EXP-008`〜`EXP-010`で、固定閾値`MaxBuyTrendDurationBars=50`は3期間とも効果の
符号はプラスだったが、買いシグナルの削減率が-36.9% / -53.8% / -71.1%と大きく変動した。
これは「50バー」が絶対的な水準ではなく、各期間のトレンド継続長分布に対する相対位置で
効き方が決まっていることを示唆する（`EXP-010`のdecision参照）。

本スクリプトは、その示唆を検証するために相対指標を計算する。

【相対指標の定義（結果を見る前に固定。恣意的に後から変えない）】
- `trend_duration_bars`: `analysis/loss_regime_classification.py`の`compute_trend_duration()`と
  同一ロジック（EAの`GetTrendDirection()`条件が連続成立したバー数）
- `trend_duration_percentile`: 判定バーから遡る`lookback_bars`本の各バーで観測された
  trend_duration値の分布に対する、現在値のパーセンタイル順位(0-100)
- **lookback窓は判定バーより前のバーのみを使用する（未来データ不使用、`RESEARCH_RULES.md`第2節）**
- 除外閾値は`H006`の三分位定義（Extended = 上位1/3）の直接的な相対版として
  **67パーセンタイル以上**を既定とする。新たに閾値を探索して選んだ値ではない

【本スクリプトが答えないこと】
- 相対化すれば成績が良くなる、という主張はしない。本スクリプトの主目的は
  **「削減率（フィルター強度）が期間をまたいで安定するか」という構造的性質の確認**であり、
  損益指標の最適化ではない。
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from feature_extraction import compute_ema_series  # noqa: E402
from mfe_mae_reconstruction import load_h1_csv  # noqa: E402
from parse_mt4_trades import parse_trades_html  # noqa: E402

DEFAULT_LOOKBACK_BARS = 1000  # 約6週間(H1)。判定バーより前のみ使用
DEFAULT_PERCENTILE_CUT = 67.0  # H006の三分位(上位1/3)の相対版


def _trend_ok(direction: str, close: float, fast: float, mid: float, slow: float) -> bool:
    if direction == "buy":
        return close > slow and fast > mid and mid > slow
    return close < slow and fast < mid and mid < slow


def compute_trend_duration_series(bars: list[dict], direction: str,
                                   ema_fast: list, ema_mid: list, ema_slow: list,
                                   closes: list[float]) -> list[int | None]:
    """各バー時点での「そのバーまで連続して同方向トレンドが成立していたバー数」を系列で返す。

    逐次的に前バーの値へ+1していくため、O(n)で計算できる（バーごとに遡らない）。
    """
    out: list[int | None] = [None] * len(bars)
    run = 0
    for i in range(len(bars)):
        if ema_fast[i] is None or ema_mid[i] is None or ema_slow[i] is None:
            out[i] = None
            run = 0
            continue
        if _trend_ok(direction, closes[i], ema_fast[i], ema_mid[i], ema_slow[i]):
            run += 1
        else:
            run = 0
        out[i] = run
    return out


def percentile_rank(values: list[int], target: int) -> float:
    """valuesの中でtarget以下の値が占める割合(0-100)。同値は「以下」に含める。"""
    if not values:
        return float("nan")
    n_le = sum(1 for v in values if v <= target)
    return 100.0 * n_le / len(values)


def build_rows(trades: list[dict], bars: list[dict],
               lookback_bars: int = DEFAULT_LOOKBACK_BARS) -> list[dict]:
    bar_index = {b["time"]: i for i, b in enumerate(bars)}
    closes = [b["close"] for b in bars]
    ema20 = compute_ema_series(closes, 20)
    ema75 = compute_ema_series(closes, 75)
    ema200 = compute_ema_series(closes, 200)

    dur_buy = compute_trend_duration_series(bars, "buy", ema20, ema75, ema200, closes)

    rows = []
    for t in trades:
        if t.get("type") != "buy" or not t.get("open_time"):
            continue
        entry_time = datetime.fromisoformat(t["open_time"])
        entry_bar_time = entry_time.replace(minute=0, second=0, microsecond=0)
        entry_idx = bar_index.get(entry_bar_time)
        decision_idx = entry_idx - 1 if (entry_idx is not None and entry_idx > 0) else None

        row = {
            "ticket": t.get("ticket"),
            "profit": t.get("profit"),
            "trend_duration_bars": None,
            "trend_duration_percentile": None,
        }
        if decision_idx is not None and decision_idx >= 200:
            cur = dur_buy[decision_idx]
            row["trend_duration_bars"] = cur
            lo = max(0, decision_idx - lookback_bars)
            # 判定バー自身を含めない（lookbackは過去のみ）
            window = [v for v in dur_buy[lo:decision_idx] if v is not None]
            if cur is not None and window:
                row["trend_duration_percentile"] = round(percentile_rank(window, cur), 2)
        rows.append(row)
    return rows


def summarize_filter(rows: list[dict], fixed_bars: int, percentile_cut: float) -> dict:
    usable = [r for r in rows if r["trend_duration_bars"] is not None
              and r["trend_duration_percentile"] is not None]
    n = len(usable)
    if n == 0:
        return {"n": 0}
    excl_fixed = [r for r in usable if r["trend_duration_bars"] > fixed_bars]
    excl_rel = [r for r in usable if r["trend_duration_percentile"] >= percentile_cut]
    return {
        "n": n,
        "fixed_excluded": len(excl_fixed),
        "fixed_reduction_pct": round(100.0 * len(excl_fixed) / n, 1),
        "relative_excluded": len(excl_rel),
        "relative_reduction_pct": round(100.0 * len(excl_rel) / n, 1),
    }


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="トレンド成熟度の相対化指標を計算し、固定閾値とのフィルター強度の安定性を比較する")
    parser.add_argument("h1_csv", help="H1 OHLC CSV (DS011相当)")
    parser.add_argument("reports", nargs="+", help="label:report.htm を複数指定")
    parser.add_argument("--lookback-bars", type=int, default=DEFAULT_LOOKBACK_BARS)
    parser.add_argument("--fixed-bars", type=int, default=50)
    parser.add_argument("--percentile-cut", type=float, default=DEFAULT_PERCENTILE_CUT)
    parser.add_argument("-o", "--output", help="トレード単位の結果を出力するJSONパス(省略可)")
    args = parser.parse_args()

    bars = load_h1_csv(args.h1_csv)
    all_rows = {}
    for spec in args.reports:
        label, path = spec.split(":", 1)
        trades = parse_trades_html(path)
        rows = build_rows(trades, bars, args.lookback_bars)
        all_rows[label] = rows
        s = summarize_filter(rows, args.fixed_bars, args.percentile_cut)
        print(f"{label}: {json.dumps(s, ensure_ascii=False)}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(all_rows, f, ensure_ascii=False, indent=2)
        print(f"保存しました: {args.output}")


if __name__ == "__main__":
    main()

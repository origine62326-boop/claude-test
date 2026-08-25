"""
決済後も価格を追い続け、「決済で打ち切らなければトレードはどこまで走ったか」を測る。

【この分析が答える問い（H-β）】
現行EAはTP=2R固定であり、`mfe_mae_reconstruction.py`のMFEは entry_time〜exit_time の
区間しか見ていない。したがって「2Rで閉じた勝ちトレードがその後どこまで伸びたか」は
これまで一度も観測されていない。トレンドフォローの収益源とされる右の裾（少数の巨大な
勝ち）が、このロジックのエントリーに存在するのかどうかが判定できていない。

本スクリプトは決済時刻で打ち切らず、決済後Nバーまで同じ方向の有利変動を測る。

【測定内容（結果を見る前に確定。後から変更しない）】
- `max_R_extended`: エントリー価格を基準とした最大有利変動を、
  entry_time 〜 (exit_time + N本) の全H1バーで測る（R = stop_distance_pips で正規化）
- `max_adverse_R_extended`: 同区間の最大不利変動。保有継続のリスク側を併記するため
- `giveback_R`: ピーク到達後、区間終端までにどれだけ戻したか（peak - 終端時点の含み損益）
- 観測ホライズン N は {24, 72, 168, 336} バー（H1なので約1日 / 3日 / 1週 / 2週）の
  **全てを併記する**。良く見えた1つを選ぶことはしない
- 分類: exit_type は close_price が tp / sl のどちらに一致するかで決める（許容10pips）

【この分析が答えないこと・重大な限界】
1. **これは「取れたはずの利益」ではない。** 保有を延長すれば、その間に発生した後続
   トレードは執行されない（経路依存）。O-004で確認済みの効果がここでも働く
2. **トレーリングストップ等の決済ルールを設計していない。** 本スクリプトは観察であり、
   取引ルールの提案ではない（`RESEARCH_RULES.md`）
3. H1バー粒度の近似。バー内の順序（高値と安値のどちらが先か）は判別できない
4. 決済後の区間に週末ギャップ・データ欠損があっても、存在するバーのみで測る
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mfe_mae_reconstruction import load_h1_csv  # noqa: E402
from parse_mt4_trades import parse_trades_html  # noqa: E402

PIP_SIZE = 0.01
HORIZONS = [24, 72, 168, 336]  # 結果を見る前に固定
EXIT_MATCH_TOL_PIPS = 10.0


def classify_exit(trade: dict) -> str:
    cp, sl, tp = trade.get("close_price"), trade.get("sl"), trade.get("tp")
    if cp is None:
        return "unknown"
    tol = EXIT_MATCH_TOL_PIPS * PIP_SIZE
    if tp and abs(cp - tp) <= tol:
        return "tp"
    if sl and abs(cp - sl) <= tol:
        return "sl"
    return "other"


def favorable_pips(direction: str, entry: float, bar: dict) -> float:
    return (bar["high"] - entry) / PIP_SIZE if direction == "buy" else (entry - bar["low"]) / PIP_SIZE


def adverse_pips(direction: str, entry: float, bar: dict) -> float:
    return (entry - bar["low"]) / PIP_SIZE if direction == "buy" else (bar["high"] - entry) / PIP_SIZE


def close_pips(direction: str, entry: float, bar: dict) -> float:
    return (bar["close"] - entry) / PIP_SIZE if direction == "buy" else (entry - bar["close"]) / PIP_SIZE


def analyze_trade(trade: dict, bars: list[dict], horizons=None) -> dict | None:
    horizons = horizons or HORIZONS
    direction = trade.get("type")
    entry, sl = trade.get("open_price"), trade.get("sl")
    if direction not in ("buy", "sell") or entry is None or sl is None:
        return None
    if not trade.get("open_time") or not trade.get("close_time"):
        return None

    stop_pips = abs(entry - sl) / PIP_SIZE
    if stop_pips <= 0:
        return None

    t_in = datetime.fromisoformat(trade["open_time"])
    t_out = datetime.fromisoformat(trade["close_time"])

    # 決済バー以降のインデックスを求める
    exit_idx = None
    for i, b in enumerate(bars):
        if b["time"] >= t_out:
            exit_idx = i
            break
    if exit_idx is None:
        return None
    start_idx = None
    for i, b in enumerate(bars):
        if b["time"] >= t_in:
            start_idx = i
            break
    if start_idx is None:
        return None

    row = {
        "ticket": trade.get("ticket"),
        "type": direction,
        "profit": trade.get("profit"),
        "exit_type": classify_exit(trade),
        "stop_pips": round(stop_pips, 2),
        "held_bars": exit_idx - start_idx,
        "_start_idx": start_idx,
        "_exit_idx": exit_idx,
    }

    for n in horizons:
        window = bars[start_idx: exit_idx + n + 1]
        if not window:
            row[f"max_R_{n}"] = None
            continue
        peak = max(favorable_pips(direction, entry, b) for b in window)
        worst = max(adverse_pips(direction, entry, b) for b in window)
        # ピーク到達バーを特定し、そこから区間終端までの戻し幅を測る
        peak_i = max(range(len(window)), key=lambda k: favorable_pips(direction, entry, window[k]))
        end_close = close_pips(direction, entry, window[-1])
        row[f"max_R_{n}"] = round(peak / stop_pips, 4)
        row[f"adverse_R_{n}"] = round(worst / stop_pips, 4)
        row[f"giveback_R_{n}"] = round((peak / stop_pips) - (end_close / stop_pips), 4)
        row[f"bars_to_peak_{n}"] = peak_i
    return row


def pct(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    s = sorted(values)
    k = (len(s) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def summarize(rows: list[dict], n: int, label: str) -> dict:
    vals = [r[f"max_R_{n}"] for r in rows if r.get(f"max_R_{n}") is not None]
    if not vals:
        return {"label": label, "n": 0}
    return {
        "label": label,
        "n": len(vals),
        "mean": round(sum(vals) / len(vals), 3),
        "median": round(pct(vals, 0.5), 3),
        "p75": round(pct(vals, 0.75), 3),
        "p90": round(pct(vals, 0.90), 3),
        "max": round(max(vals), 3),
        "ge_3R": sum(1 for v in vals if v >= 3.0),
        "ge_5R": sum(1 for v in vals if v >= 5.0),
        "ge_8R": sum(1 for v in vals if v >= 8.0),
    }


def random_benchmark(rows: list[dict], bars: list[dict], n: int,
                     samples: int = 200, seed: int = 20260825) -> dict:
    """帰無基準: 同じ方向・同じstop幅・同じ窓長で、ランダムな時点から入った場合のmax_R。

    USDJPYは観測期間中に大きな上昇ドリフトを持つため、「長く待てば含み益が出る」のは
    エントリーの選別力ではなくドリフトとボラティリティだけで説明できる可能性がある。
    実測値をこの基準と比較しない限り、右の裾の有無は判定できない。

    シードを固定し、結果を見てから再抽選しない。
    """
    import random
    rng = random.Random(seed)
    out = []
    # 期間交絡の除去: 標本はトレードが実在した期間内からのみ抽出する。
    # 全履歴(2016-2026)から抽出すると、2021-2024の大相場が帰無側にだけ混入する。
    lo = min(r["_start_idx"] for r in rows)
    hi = max(r["_exit_idx"] for r in rows)
    for r in rows:
        win_len = r["held_bars"] + n
        if win_len <= 0:
            continue
        top = min(hi, len(bars) - win_len - 1)
        if top <= lo:
            continue
        direction, stop_pips = r["type"], r["stop_pips"]
        for _ in range(samples):
            i = rng.randrange(lo, top)
            entry = bars[i]["open"]
            w = bars[i: i + win_len + 1]
            peak = max(favorable_pips(direction, entry, b) for b in w)
            out.append(peak / stop_pips)
    if not out:
        return {"n": 0}
    return {
        "n": len(out),
        "mean": round(sum(out) / len(out), 3),
        "median": round(pct(out, 0.5), 3),
        "p75": round(pct(out, 0.75), 3),
        "p90": round(pct(out, 0.90), 3),
        "ge_3R_pct": round(100.0 * sum(1 for v in out if v >= 3.0) / len(out), 1),
        "ge_5R_pct": round(100.0 * sum(1 for v in out if v >= 5.0) / len(out), 1),
        "ge_8R_pct": round(100.0 * sum(1 for v in out if v >= 8.0) / len(out), 1),
    }


def main():
    import argparse
    import json

    ap = argparse.ArgumentParser(description="決済後も追跡し、右の裾の有無を観察する(H-β)")
    ap.add_argument("report_htm")
    ap.add_argument("h1_csv")
    ap.add_argument("-o", "--output")
    ap.add_argument("--benchmark", action="store_true", help="ランダムエントリーの帰無基準を併算する")
    args = ap.parse_args()

    trades = parse_trades_html(args.report_htm)
    bars = load_h1_csv(args.h1_csv)
    rows = [r for r in (analyze_trade(t, bars) for t in trades) if r]

    print(f"対象トレード: {len(rows)}件 / 明細{len(trades)}件")
    by_exit = {}
    for r in rows:
        by_exit.setdefault(r["exit_type"], []).append(r)
    print("exit_type内訳: " + ", ".join(f"{k}={len(v)}" for k, v in sorted(by_exit.items())))

    groups = [
        ("TP決済(勝ち)", [r for r in rows if r["exit_type"] == "tp"]),
        ("  うち買い", [r for r in rows if r["exit_type"] == "tp" and r["type"] == "buy"]),
        ("  うち売り", [r for r in rows if r["exit_type"] == "tp" and r["type"] == "sell"]),
        ("SL決済(負け)", [r for r in rows if r["exit_type"] == "sl"]),
        ("  うち買い", [r for r in rows if r["exit_type"] == "sl" and r["type"] == "buy"]),
        ("  うち売り", [r for r in rows if r["exit_type"] == "sl" and r["type"] == "sell"]),
    ]

    for n in HORIZONS:
        print(f"\n### 決済後 +{n}本 まで追跡（max_R、エントリー基準・R正規化）")
        print(f"{'group':<14}{'n':>5}{'mean':>8}{'median':>8}{'p75':>8}{'p90':>8}{'max':>8}"
              f"{'>=3R':>7}{'>=5R':>7}{'>=8R':>7}")
        for label, g in groups:
            s = summarize(g, n, label)
            if s["n"] == 0:
                continue
            print(f"{label:<14}{s['n']:>5}{s['mean']:>8.3f}{s['median']:>8.3f}{s['p75']:>8.3f}"
                  f"{s['p90']:>8.3f}{s['max']:>8.3f}{s['ge_3R']:>7}{s['ge_5R']:>7}{s['ge_8R']:>7}")
        if args.benchmark:
            for label, g in [("[帰無]TP相当", [r for r in rows if r["exit_type"] == "tp"]),
                             ("[帰無]SL相当", [r for r in rows if r["exit_type"] == "sl"])]:
                b = random_benchmark(g, bars, n)
                if b.get("n"):
                    print(f"{label:<14}{b['n']:>5}{b['mean']:>8.3f}{b['median']:>8.3f}"
                          f"{b['p75']:>8.3f}{b['p90']:>8.3f}{'-':>8}"
                          f"{b['ge_3R_pct']:>6.1f}%{b['ge_5R_pct']:>6.1f}%{b['ge_8R_pct']:>6.1f}%")

    if args.output:
        Path(args.output).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n保存しました: {args.output}")


if __name__ == "__main__":
    main()

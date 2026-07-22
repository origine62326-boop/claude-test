"""
正規化済みトレードリスト（parse_mt4_trades.pyの出力）から性能指標を計算する。

MT4レポートのサマリー値(parse_mt4_report.pyの出力)と、ここで独立に再計算した値を
突き合わせることで、パーサーのバグやMT4レポートの見落としを検出できる
(cross_check_against_report を参照)。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

MIN_TRADES_FOR_CONFIDENCE = 200  # これ未満は統計的信頼性が低いと見なす目安


def _closed_trades(trades: list[dict]) -> list[dict]:
    return [t for t in trades if t.get("profit") is not None]


def compute_metrics_from_trades(trades: list[dict]) -> dict:
    closed = _closed_trades(trades)
    n = len(closed)

    if n == 0:
        return {"total_trades": 0, "note": "決済済みトレードがありません"}

    profits = [t["profit"] for t in closed]
    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p < 0]
    breakeven = [p for p in profits if p == 0]

    net_profit = sum(profits)
    gross_profit = sum(wins)
    gross_loss = sum(losses)  # 負の値

    win_count = len(wins)
    loss_count = len(losses)

    average_win = (gross_profit / win_count) if win_count else 0.0
    average_loss = (gross_loss / loss_count) if loss_count else 0.0

    profit_factor = (gross_profit / abs(gross_loss)) if gross_loss != 0 else None
    expected_payoff = net_profit / n
    win_rate_pct = (win_count / n) * 100

    risk_reward_ratio = (average_win / abs(average_loss)) if average_loss != 0 else None

    max_consec_wins, max_consec_losses = _max_consecutive(profits)

    return {
        "total_trades": n,
        "breakeven_trades": len(breakeven),
        "win_trades": win_count,
        "loss_trades": loss_count,
        "win_rate_pct": round(win_rate_pct, 2),
        "net_profit": round(net_profit, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "profit_factor": round(profit_factor, 3) if profit_factor is not None else None,
        "expected_payoff": round(expected_payoff, 3),
        "average_win": round(average_win, 2),
        "average_loss": round(average_loss, 2),
        "risk_reward_ratio": round(risk_reward_ratio, 3) if risk_reward_ratio is not None else None,
        "largest_win": round(max(wins), 2) if wins else None,
        "largest_loss": round(min(losses), 2) if losses else None,
        "max_consecutive_wins": max_consec_wins,
        "max_consecutive_losses": max_consec_losses,
        "sample_size_reliable": n >= MIN_TRADES_FOR_CONFIDENCE,
        "min_trades_for_confidence": MIN_TRADES_FOR_CONFIDENCE,
    }


def _max_consecutive(profits: list[float]) -> tuple[int, int]:
    max_wins = cur_wins = 0
    max_losses = cur_losses = 0
    for p in profits:
        if p > 0:
            cur_wins += 1
            cur_losses = 0
        elif p < 0:
            cur_losses += 1
            cur_wins = 0
        else:
            cur_wins = cur_losses = 0
        max_wins = max(max_wins, cur_wins)
        max_losses = max(max_losses, cur_losses)
    return max_wins, max_losses


# 突き合わせを行う際、四捨五入誤差を許容する相対誤差
CROSS_CHECK_TOLERANCE = 0.01  # 1%


def cross_check_against_report(computed: dict, report: dict) -> list[dict]:
    """トレードから再計算した値と、MT4レポートの値を比較し、乖離が大きい項目を返す。
    パーサーのバグ検出や、レポートの見落とし発見のために使う。"""
    pairs = [
        ("total_trades", "total_trades"),
        ("net_profit", "net_profit"),
        ("gross_profit", "gross_profit"),
        ("gross_loss", "gross_loss"),
        ("profit_factor", "profit_factor"),
        ("expected_payoff", "expected_payoff"),
    ]

    mismatches = []
    for computed_key, report_key in pairs:
        c = computed.get(computed_key)
        r = report.get(report_key)
        if c is None or r is None:
            continue
        if r == 0:
            diff_ok = (c == 0)
        else:
            diff_ok = abs(c - r) / abs(r) <= CROSS_CHECK_TOLERANCE
        if not diff_ok:
            mismatches.append({"field": computed_key, "computed": c, "report": r})

    return mismatches


def main():
    import argparse
    import json

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import load_json, save_json

    parser = argparse.ArgumentParser(description="正規化トレードJSONから性能指標を計算する")
    parser.add_argument("trades_json", help="parse_mt4_trades.pyが出力したトレードJSON")
    parser.add_argument("--report-json", help="parse_mt4_report.pyが出力したサマリーJSON(突き合わせ用、任意)")
    parser.add_argument("-o", "--output", help="出力先JSONパス（省略時は標準出力）")
    args = parser.parse_args()

    trades = load_json(args.trades_json)
    metrics = compute_metrics_from_trades(trades)

    if args.report_json:
        report = load_json(args.report_json)
        mismatches = cross_check_against_report(metrics, report)
        metrics["_cross_check_mismatches"] = mismatches
        if mismatches:
            print(f"[WARN] レポートとの乖離を検出: {mismatches}")

    if args.output:
        save_json(args.output, metrics)
        print(f"保存しました: {args.output}")
    else:
        print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

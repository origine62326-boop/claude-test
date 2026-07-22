"""
2つの分析結果(performance_metrics.pyの出力)を比較し、指標ごとの差分を出す。

EA改善(Phase5→6→7...)の効果を数値で確認するため、および
「パラメータを変えたら本当に良くなったのか、それとも特定期間にだけ
都合が良くなっただけか」を確認する材料として使う。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

COMPARE_FIELDS = [
    "total_trades",
    "win_rate_pct",
    "net_profit",
    "profit_factor",
    "expected_payoff",
    "average_win",
    "average_loss",
    "risk_reward_ratio",
    "max_consecutive_wins",
    "max_consecutive_losses",
]

# 値が大きいほど良いとは限らない指標(小さいほど良い、または解釈に注意が必要なもの)
LOWER_IS_BETTER = set()  # 現状は対象なし。max_drawdown等を比較対象に含める場合はここに追加


def compare_metrics(baseline: dict, candidate: dict, baseline_label="baseline", candidate_label="candidate") -> dict:
    diffs = {}
    for field in COMPARE_FIELDS:
        b = baseline.get(field)
        c = candidate.get(field)
        if b is None or c is None:
            diffs[field] = {"baseline": b, "candidate": c, "diff": None, "diff_pct": None}
            continue

        diff = c - b
        diff_pct = (diff / abs(b) * 100) if b != 0 else None

        improved = diff > 0
        if field in LOWER_IS_BETTER:
            improved = diff < 0

        diffs[field] = {
            "baseline": b,
            "candidate": c,
            "diff": round(diff, 4),
            "diff_pct": round(diff_pct, 2) if diff_pct is not None else None,
            "improved": improved if diff != 0 else None,
        }

    return {
        "baseline_label": baseline_label,
        "candidate_label": candidate_label,
        "fields": diffs,
    }


def main():
    import argparse
    import json

    from common import load_json, save_json

    parser = argparse.ArgumentParser(description="2つの分析結果(performance_metrics出力)を比較する")
    parser.add_argument("baseline_json", help="比較元(現行バージョン)のJSON")
    parser.add_argument("candidate_json", help="比較先(新バージョン)のJSON")
    parser.add_argument("--baseline-label", default="baseline")
    parser.add_argument("--candidate-label", default="candidate")
    parser.add_argument("-o", "--output", help="出力先JSONパス（省略時は標準出力）")
    args = parser.parse_args()

    baseline = load_json(args.baseline_json)
    candidate = load_json(args.candidate_json)
    result = compare_metrics(baseline, candidate, args.baseline_label, args.candidate_label)

    if args.output:
        save_json(args.output, result)
        print(f"保存しました: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

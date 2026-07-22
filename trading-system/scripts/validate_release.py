"""
1回の分析結果(metrics.json + anomalies.json)を configs/acceptance_criteria.yaml の
基準と照合し、PASS/FAILを機械的に判定する。

これは「人間の承認」を代替するものではなく、承認の前に明らかな問題を機械的に
弾くためのゲートである。PASSであっても、最終的な実口座投入判断は必ず人間が行うこと。

使い方:
    python scripts/validate_release.py \
        --metrics reports/analyzed/v0.1_1y_metrics.json \
        --anomalies reports/analyzed/v0.1_1y_anomalies.json
"""

import argparse
import sys
from pathlib import Path

import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from analysis.common import CONFIGS_DIR, load_json  # noqa: E402


def load_criteria(path=None) -> dict:
    path = Path(path) if path else CONFIGS_DIR / "acceptance_criteria.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate(metrics: dict, anomalies: dict, criteria: dict) -> dict:
    checks = []

    def add_check(name, passed, detail):
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    total_trades = metrics.get("total_trades", 0)
    add_check(
        "min_trades",
        total_trades >= criteria["min_trades"],
        f"取引数={total_trades} (基準: {criteria['min_trades']}以上)",
    )

    pf = metrics.get("profit_factor")
    add_check(
        "min_profit_factor",
        pf is not None and pf >= criteria["min_profit_factor"],
        f"プロフィットファクター={pf} (基準: {criteria['min_profit_factor']}以上)",
    )

    payoff = metrics.get("expected_payoff")
    add_check(
        "min_expected_payoff",
        payoff is not None and payoff >= criteria["min_expected_payoff"],
        f"期待利得={payoff} (基準: {criteria['min_expected_payoff']}以上)",
    )

    max_losses = metrics.get("max_consecutive_losses", 0)
    add_check(
        "max_consecutive_losses_hard_limit",
        max_losses <= criteria["max_consecutive_losses_hard_limit"],
        f"最大連敗={max_losses} (基準: {criteria['max_consecutive_losses_hard_limit']}以下)",
    )

    rr = metrics.get("risk_reward_ratio")
    add_check(
        "min_risk_reward_ratio",
        rr is not None and rr >= criteria["min_risk_reward_ratio"],
        f"リスクリワード比={rr} (基準: {criteria['min_risk_reward_ratio']}以上)",
    )

    if criteria.get("require_anomaly_free"):
        is_clean = anomalies.get("_summary", {}).get("is_clean", False)
        add_check("require_anomaly_free", is_clean, f"異常検知結果: {'クリーン' if is_clean else '異常あり'}")

    overall_pass = all(c["passed"] for c in checks)

    return {
        "overall": "PASS" if overall_pass else "FAIL",
        "checks": checks,
        "disclaimer": "PASSは機械的な基準クリアを意味するのみで、実口座投入の推奨ではない。"
                       "最終判断は必ず人間が行うこと。",
    }


def main():
    parser = argparse.ArgumentParser(description="分析結果を合格基準と照合する")
    parser.add_argument("--metrics", required=True, help="performance_metrics.py出力JSON")
    parser.add_argument("--anomalies", required=True, help="trade_anomaly_check.py出力JSON")
    parser.add_argument("--criteria", help="acceptance_criteria.yamlのパス(省略時はconfigs/配下の既定値)")
    args = parser.parse_args()

    metrics = load_json(args.metrics)
    anomalies = load_json(args.anomalies)
    criteria = load_criteria(args.criteria)

    result = validate(metrics, anomalies, criteria)

    print(f"=== 判定結果: {result['overall']} ===")
    for c in result["checks"]:
        mark = "○" if c["passed"] else "×"
        print(f"  [{mark}] {c['check']}: {c['detail']}")
    print(f"\n{result['disclaimer']}")

    sys.exit(0 if result["overall"] == "PASS" else 1)


if __name__ == "__main__":
    main()

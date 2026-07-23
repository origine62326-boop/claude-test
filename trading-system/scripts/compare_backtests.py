"""
2つの run_analysis.py 実行結果(*_metrics.json)を比較し、Markdown比較レポートを
outputs/comparisons/ へ出力する。

使い方:
    python scripts/compare_backtests.py \
        --baseline reports/analyzed/v0.1_2y_metrics.json \
        --candidate reports/analyzed/v0.1_1y_metrics.json \
        --baseline-label "v0.1 2年間" --candidate-label "v0.1 直近1年"
"""

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from analysis import compare_versions  # noqa: E402
from analysis.common import OUTPUTS_COMPARISONS_DIR, load_json, save_json  # noqa: E402


def render_comparison_md(result: dict) -> str:
    lines = [f"# バックテスト比較: {result['baseline_label']} vs {result['candidate_label']}", ""]
    lines.append("| 指標 | " + result["baseline_label"] + " | " + result["candidate_label"] + " | 差分 | 差分% | 改善? |")
    lines.append("|---|---|---|---|---|---|")
    for field, d in result["fields"].items():
        improved = "-" if d["improved"] is None else ("○" if d["improved"] else "×")
        lines.append(f"| {field} | {d['baseline']} | {d['candidate']} | {d['diff']} | {d['diff_pct']} | {improved} |")
    lines.append("")
    lines.append("*改善?列は機械的な大小比較のみ。取引数が大きく減っている場合、"
                  "その他の指標の改善は統計的信頼性が低い可能性がある点に注意。*")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="2つのバックテスト分析結果を比較する")
    parser.add_argument("--baseline", required=True, help="比較元のmetrics JSON")
    parser.add_argument("--candidate", required=True, help="比較先のmetrics JSON")
    parser.add_argument("--baseline-label", default="baseline")
    parser.add_argument("--candidate-label", default="candidate")
    parser.add_argument("--run-id", required=True, help="出力ファイル名に使う識別子")
    args = parser.parse_args()

    baseline = load_json(args.baseline)
    candidate = load_json(args.candidate)
    result = compare_versions.compare_metrics(baseline, candidate, args.baseline_label, args.candidate_label)

    save_json(OUTPUTS_COMPARISONS_DIR / f"{args.run_id}_compare.json", result)

    md_path = OUTPUTS_COMPARISONS_DIR / f"{args.run_id}_compare.md"
    md_path.write_text(render_comparison_md(result), encoding="utf-8")
    print(f"保存しました: {md_path}")


if __name__ == "__main__":
    main()

"""
1回のバックテスト結果(レポートHTML + 操作履歴HTML)を入力として、
パイプライン全体(パース→正規化→指標計算→異常検知→期間/方向/時間/レジーム分析→
Markdownサマリー生成)を一括実行する。

使い方:
    python scripts/run_analysis.py \
        --report reports/raw/report_xxx.htm \
        --trades reports/raw/trades_xxx.htm \
        --run-id v0.1_1y_20250721-20260721
"""

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from analysis import (  # noqa: E402
    direction_analysis,
    generate_summary,
    parse_mt4_report,
    parse_mt4_trades,
    performance_metrics,
    period_analysis,
    regime_analysis,
    time_analysis,
    trade_anomaly_check,
)
from analysis.common import (  # noqa: E402
    OUTPUTS_SUMMARIES_DIR,
    REPORTS_ANALYZED_DIR,
    REPORTS_NORMALIZED_DIR,
    save_json,
)


def run(report_html: str, trades_html: str, run_id: str, max_lot: float | None) -> dict:
    normalized_dir = REPORTS_NORMALIZED_DIR
    analyzed_dir = REPORTS_ANALYZED_DIR

    print(f"[1/8] レポートHTMLをパース中: {report_html}")
    report_data = parse_mt4_report.parse_report_html(report_html)
    save_json(normalized_dir / f"{run_id}_report.json", report_data)
    if report_data["_missing_fields"]:
        print(f"  [WARN] 抽出できなかったフィールド: {report_data['_missing_fields']}")

    print(f"[2/8] 操作履歴HTMLをパース中: {trades_html}")
    trades = parse_mt4_trades.parse_trades_html(trades_html)
    save_json(normalized_dir / f"{run_id}_trades.json", trades)
    print(f"  {len(trades)}トレードを正規化しました")

    print("[3/8] 性能指標を計算中")
    metrics = performance_metrics.compute_metrics_from_trades(trades)
    mismatches = performance_metrics.cross_check_against_report(metrics, report_data)
    metrics["_cross_check_mismatches"] = mismatches
    if mismatches:
        print(f"  [WARN] レポートとの乖離を検出: {mismatches}")
    save_json(analyzed_dir / f"{run_id}_metrics.json", metrics)

    print("[4/8] 安全設計チェック(異常検知)を実行中")
    anomalies = trade_anomaly_check.run_all_checks(trades, max_lot=max_lot)
    anomalies["_summary"] = trade_anomaly_check.summarize(anomalies)
    if not anomalies["_summary"]["is_clean"]:
        print(f"  [WARN] 異常を検出: {anomalies['_summary']['issue_counts']}")
    save_json(analyzed_dir / f"{run_id}_anomalies.json", anomalies)

    print("[5/8] 年別/月別分析中")
    period = period_analysis.analyze_by_period(trades)
    save_json(analyzed_dir / f"{run_id}_period.json", period)

    print("[6/8] 買い/売り別分析中")
    direction = direction_analysis.analyze_by_direction(trades)
    save_json(analyzed_dir / f"{run_id}_direction.json", direction)

    print("[7/8] 時間帯/曜日別・レジーム近似分析中")
    time_result = time_analysis.analyze_by_time(trades)
    save_json(analyzed_dir / f"{run_id}_time.json", time_result)
    regime = regime_analysis.analyze_regime(trades)
    save_json(analyzed_dir / f"{run_id}_regime.json", regime)

    print("[8/8] Markdownサマリーを生成中")
    md = generate_summary.render_summary(report_data, metrics, anomalies, period, direction, time_result, regime)
    summary_path = OUTPUTS_SUMMARIES_DIR / f"{run_id}_summary.md"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(md, encoding="utf-8")
    print(f"完了: {summary_path}")

    return {
        "report": report_data,
        "metrics": metrics,
        "anomalies": anomalies,
        "period": period,
        "direction": direction,
        "time": time_result,
        "regime": regime,
        "summary_path": str(summary_path),
    }


def main():
    parser = argparse.ArgumentParser(description="バックテスト結果の分析パイプラインを一括実行する")
    parser.add_argument("--report", required=True, help="MT4レポートHTMLのパス")
    parser.add_argument("--trades", required=True, help="MT4操作履歴HTMLのパス")
    parser.add_argument("--run-id", required=True, help="この実行を識別する任意のID(出力ファイル名に使う)")
    parser.add_argument("--max-lot", type=float, default=None, help="MaximumLot入力パラメータの値(異常検知用、任意)")
    args = parser.parse_args()

    run(args.report, args.trades, args.run_id, args.max_lot)


if __name__ == "__main__":
    main()

"""
バックテスト結果を分析するパイプライン。

最小構成(レポートHTMLのみ): レポートの解析→検証→初心者向けMarkdownサマリー生成
    python scripts/run_analysis.py reports/raw/sample_report.htm

フル版(操作履歴HTMLも渡した場合): 上記に加えて、トレード明細からの指標再計算・
安全設計チェック・年別/月別/買売別/時間帯別/レジーム分析も実行する
    python scripts/run_analysis.py reports/raw/sample_report.htm --trades reports/raw/sample_trades.htm

--run-id を省略した場合は、レポートHTMLのファイル名(拡張子抜き)がそのまま使われる。
入力ファイル(reports/raw/配下)は一切書き換えない。出力は reports/normalized/,
reports/analyzed/, outputs/summaries/ 配下に <run-id>_* という名前で保存される。
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


def run_minimal(report_html: str, run_id: str) -> dict:
    """レポートHTMLのみを入力とする最小構成の分析フロー。"""
    print(f"[1/3] レポートHTMLをパース中: {report_html}")
    report_data = parse_mt4_report.parse_report_html(report_html)
    save_json(REPORTS_NORMALIZED_DIR / f"{run_id}_report.json", report_data)
    if report_data["_missing_required_fields"]:
        print(f"  [WARN] 抽出できなかった必須フィールド: {report_data['_missing_required_fields']}")

    print("[2/3] データを検証中(欠損値・異常値チェック)")
    validation = performance_metrics.validate_report_data(report_data)
    save_json(REPORTS_ANALYZED_DIR / f"{run_id}_validation.json", validation)
    if not validation["is_valid"]:
        print(f"  [ERROR] {validation['error_count']}件のエラーを検出しました")
    if validation["warnings"]:
        print(f"  [WARN] {validation['warning_count']}件の注意事項があります")

    print("[3/3] Markdownサマリーを生成中")
    md = generate_summary.render_minimal_summary(report_data, validation)
    summary_path = OUTPUTS_SUMMARIES_DIR / f"{run_id}_summary.md"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(md, encoding="utf-8")
    print(f"完了: {summary_path}")

    return {"report": report_data, "validation": validation, "summary_path": str(summary_path)}


def run_full(report_html: str, trades_html: str, run_id: str, max_lot: float | None) -> dict:
    """レポートHTML＋操作履歴HTMLを入力とするフル版の分析フロー。"""
    result = run_minimal(report_html, run_id)
    report_data = result["report"]

    print(f"[4/8] 操作履歴HTMLをパース中: {trades_html}")
    trades = parse_mt4_trades.parse_trades_html(trades_html)
    save_json(REPORTS_NORMALIZED_DIR / f"{run_id}_trades.json", trades)
    print(f"  {len(trades)}トレードを正規化しました")

    print("[5/8] トレード明細から指標を再計算中")
    metrics = performance_metrics.compute_metrics_from_trades(trades)
    mismatches = performance_metrics.cross_check_against_report(metrics, report_data)
    metrics["_cross_check_mismatches"] = mismatches
    if mismatches:
        print(f"  [WARN] レポートとの乖離を検出: {mismatches}")
    save_json(REPORTS_ANALYZED_DIR / f"{run_id}_metrics.json", metrics)

    print("[6/8] 安全設計チェック(異常検知)を実行中")
    anomalies = trade_anomaly_check.run_all_checks(trades, max_lot=max_lot)
    anomalies["_summary"] = trade_anomaly_check.summarize(anomalies)
    if not anomalies["_summary"]["is_clean"]:
        print(f"  [WARN] 異常を検出: {anomalies['_summary']['issue_counts']}")
    save_json(REPORTS_ANALYZED_DIR / f"{run_id}_anomalies.json", anomalies)

    print("[7/8] 年別/月別・買い/売り別分析中")
    period = period_analysis.analyze_by_period(trades)
    save_json(REPORTS_ANALYZED_DIR / f"{run_id}_period.json", period)
    direction = direction_analysis.analyze_by_direction(trades)
    save_json(REPORTS_ANALYZED_DIR / f"{run_id}_direction.json", direction)

    print("[8/8] 時間帯/曜日別・レジーム近似分析中、詳細サマリーを生成中")
    time_result = time_analysis.analyze_by_time(trades)
    save_json(REPORTS_ANALYZED_DIR / f"{run_id}_time.json", time_result)
    regime = regime_analysis.analyze_regime(trades)
    save_json(REPORTS_ANALYZED_DIR / f"{run_id}_regime.json", regime)

    md = generate_summary.render_summary(report_data, metrics, anomalies, period, direction, time_result, regime)
    summary_path = OUTPUTS_SUMMARIES_DIR / f"{run_id}_summary_full.md"
    summary_path.write_text(md, encoding="utf-8")
    print(f"完了(フル版): {summary_path}")

    result.update({
        "metrics": metrics, "anomalies": anomalies, "period": period,
        "direction": direction, "time": time_result, "regime": regime,
        "full_summary_path": str(summary_path),
    })
    return result


def main():
    parser = argparse.ArgumentParser(description="バックテスト結果の分析パイプラインを実行する")
    parser.add_argument("report", help="MT4レポートHTMLのパス (例: reports/raw/sample_report.htm)")
    parser.add_argument("--trades", help="MT4操作履歴HTMLのパス(任意。指定するとフル版パイプラインも実行)")
    parser.add_argument("--run-id", help="この実行を識別するID(省略時はレポートファイル名から自動生成)")
    parser.add_argument("--max-lot", type=float, default=None, help="MaximumLot入力パラメータの値(異常検知用、任意)")
    args = parser.parse_args()

    run_id = args.run_id or Path(args.report).stem

    if args.trades:
        run_full(args.report, args.trades, run_id, args.max_lot)
    else:
        run_minimal(args.report, run_id)


if __name__ == "__main__":
    main()

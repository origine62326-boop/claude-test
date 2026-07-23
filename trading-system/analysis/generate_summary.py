"""
2種類のサマリー生成関数を持つ。

1. render_minimal_summary(): レポートデータ+検証結果だけから、初心者向けの
   日本語Markdownサマリーを生成する（最小構成パイプラインの出力）
2. render_summary(): report/metrics/anomaly/period/direction/time/regime の
   全分析結果をまとめた詳細版サマリーを生成する（フル版パイプライン向け）

いずれも「人間の承認」ステップで実際に読む主要な成果物になる想定。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


# ====================================================================
# 1. 最小構成パイプライン向け: レポートデータのみからの簡易サマリー
# ====================================================================

def render_minimal_summary(report: dict, validation: dict) -> str:
    lines = []
    lines.append(f"# バックテスト結果サマリー: {report.get('ea_name') or '(EA名不明)'}")
    lines.append("")

    lines.append("## バックテスト条件")
    lines.append("")
    lines.append(f"- 通貨ペア: {report.get('symbol', 'N/A')} / 時間足: {report.get('period', 'N/A')}")
    lines.append(f"- テスト期間: {report.get('test_start', 'N/A')} 〜 {report.get('test_end', 'N/A')}")
    deposit = report.get("initial_deposit")
    currency = report.get("currency") or ""
    lines.append(f"- 初期証拠金: {deposit if deposit is not None else 'N/A'} {currency}")
    lines.append(f"- 元ファイル: `{report.get('source_file', 'N/A')}`")
    lines.append("")

    lines.append("## 成績")
    lines.append("")
    lines.append("| 項目 | 値 |")
    lines.append("|---|---|")
    lines.append(f"| 純利益 | {_fmt(report.get('net_profit'))} |")
    lines.append(f"| プロフィットファクター(PF) | {_fmt(report.get('profit_factor'))} |")
    lines.append(f"| 最大ドローダウン | {_fmt(report.get('max_drawdown_amount'))} ({_fmt(report.get('max_drawdown_pct'), '%')}) |")
    lines.append(f"| 勝率 | {_fmt(report.get('win_rate_pct'), '%')} |")
    lines.append(f"| 取引回数 | {_fmt(report.get('total_trades'))} |")
    lines.append(f"| 最大連敗 | {_fmt(report.get('max_consecutive_losses'))} |")
    lines.append(f"| モデリング品質 | {_fmt(report.get('modelling_quality_pct'), '%')} |")
    lines.append("")

    lines.append("## 注意点")
    lines.append("")
    if validation.get("errors"):
        lines.append("**データにエラーがあります。以下を確認してください:**")
        lines.append("")
        for e in validation["errors"]:
            lines.append(f"- ❌ [{e['field']}] {e['detail']}")
        lines.append("")
    if validation.get("warnings"):
        for w in validation["warnings"]:
            lines.append(f"- ⚠️ [{w['field']}] {w['detail']}")
        lines.append("")
    if not validation.get("errors") and not validation.get("warnings"):
        lines.append("特に注意すべき点は検出されませんでした。")
        lines.append("")

    lines.append("## 次に確認すべきこと")
    lines.append("")
    next_steps = []
    if validation.get("errors"):
        next_steps.append("上記のエラーを解消してから、この結果を評価してください（レポートHTMLの再確認、"
                           "パーサーの調整が必要な可能性があります）")
    if report.get("total_trades") is not None and report["total_trades"] < 200:
        next_steps.append("取引数が少ないため、より長いテスト期間で再実行し、傾向が変わらないか確認してください")
    if report.get("modelling_quality_pct") is not None and report["modelling_quality_pct"] < 70:
        next_steps.append("モデリング品質が低いため、実ティックデータが厚い期間（直近1年程度）でも"
                           "再テストして結果を比較してください")
    if report.get("profit_factor") is not None and report["profit_factor"] < 1.0:
        next_steps.append("プロフィットファクターが1.0未満（損失超過）です。売買ロジックの見直しが必要か検討してください")
    if not next_steps:
        next_steps.append("複数の期間・条件でバックテストを繰り返し、結果が安定しているか確認してください")
    for step in next_steps:
        lines.append(f"- {step}")
    lines.append("")

    lines.append("---")
    lines.append("*このサマリーは自動生成です。利益を保証するものではありません。"
                  "実口座投入前に十分な検証と人間による承認が必要です。*")

    return "\n".join(lines)


# ====================================================================
# 2. フル版パイプライン向け: 全分析結果を統合した詳細サマリー
# ====================================================================

def _fmt(value, suffix=""):
    if value is None:
        return "N/A"
    return f"{value}{suffix}"


def render_summary(
    report_meta: dict,
    metrics: dict,
    anomalies: dict,
    period: dict,
    direction: dict,
    time_result: dict,
    regime: dict,
) -> str:
    lines = []
    lines.append(f"# バックテスト分析サマリー: {report_meta.get('ea_name', '(EA名不明)')}")
    lines.append("")
    lines.append(f"- 通貨ペア: {report_meta.get('symbol', 'N/A')} / 時間足: {report_meta.get('period', 'N/A')}")
    lines.append(f"- テスト期間: {report_meta.get('test_start', 'N/A')} 〜 {report_meta.get('test_end', 'N/A')}")
    lines.append(f"- 元ファイル: `{report_meta.get('source_file', 'N/A')}`")
    lines.append("")

    lines.append("## 全体成績")
    lines.append("")
    lines.append("| 項目 | 値 |")
    lines.append("|---|---|")
    lines.append(f"| 総取引数 | {_fmt(metrics.get('total_trades'))} |")
    lines.append(f"| 統計的信頼性 | {'十分(200件以上)' if metrics.get('sample_size_reliable') else '不十分の可能性あり(200件未満)'} |")
    lines.append(f"| 純利益 | {_fmt(metrics.get('net_profit'))} |")
    lines.append(f"| プロフィットファクター | {_fmt(metrics.get('profit_factor'))} |")
    lines.append(f"| 期待利得 | {_fmt(metrics.get('expected_payoff'))} |")
    lines.append(f"| 勝率 | {_fmt(metrics.get('win_rate_pct'), '%')} |")
    lines.append(f"| 平均勝ち/平均負け | {_fmt(metrics.get('average_win'))} / {_fmt(metrics.get('average_loss'))} |")
    lines.append(f"| リスクリワード比 | {_fmt(metrics.get('risk_reward_ratio'))} |")
    lines.append(f"| 最大連勝/最大連敗 | {_fmt(metrics.get('max_consecutive_wins'))} / {_fmt(metrics.get('max_consecutive_losses'))} |")
    lines.append("")

    lines.append("## 安全設計チェック(異常検知)")
    lines.append("")
    summary = anomalies.get("_summary", {})
    if summary.get("is_clean"):
        lines.append("異常は検出されませんでした。")
    else:
        lines.append(f"**{summary.get('total_issues')}件の異常を検出しました。要調査。**")
        lines.append("")
        for check_name, count in summary.get("issue_counts", {}).items():
            if count:
                lines.append(f"- {check_name}: {count}件")
    lines.append("")

    lines.append("## 年別成績")
    lines.append("")
    lines.append("| 年 | 取引数 | 純利益 | PF | 勝率 |")
    lines.append("|---|---|---|---|---|")
    for year, m in period.get("yearly", {}).items():
        lines.append(f"| {year} | {_fmt(m.get('total_trades'))} | {_fmt(m.get('net_profit'))} | "
                      f"{_fmt(m.get('profit_factor'))} | {_fmt(m.get('win_rate_pct'), '%')} |")
    lines.append("")

    lines.append("## 買い/売り別成績")
    lines.append("")
    lines.append("| 方向 | 取引数 | 純利益 | PF | 勝率 |")
    lines.append("|---|---|---|---|---|")
    for direction_name in ("buy", "sell"):
        m = direction.get(direction_name, {})
        label = "買い" if direction_name == "buy" else "売り"
        lines.append(f"| {label} | {_fmt(m.get('total_trades'))} | {_fmt(m.get('net_profit'))} | "
                      f"{_fmt(m.get('profit_factor'))} | {_fmt(m.get('win_rate_pct'), '%')} |")
    lines.append("")

    lines.append("## 時系列ブロック分析(レジーム近似)")
    lines.append("")
    lines.append(regime.get("note", ""))
    lines.append("")
    lines.append("| ブロック | 期間 | 取引数 | 純利益 | PF |")
    lines.append("|---|---|---|---|---|")
    for block_name, m in regime.get("blocks", {}).items():
        lines.append(f"| {block_name} | {m.get('period_start', 'N/A')}〜{m.get('period_end', 'N/A')} | "
                      f"{_fmt(m.get('total_trades'))} | {_fmt(m.get('net_profit'))} | {_fmt(m.get('profit_factor'))} |")
    lines.append("")

    lines.append("---")
    lines.append("*このサマリーは自動生成です。利益を保証するものではありません。"
                  "実口座投入前に十分な検証と人間による承認が必要です。*")

    return "\n".join(lines)


def main():
    import argparse

    from common import load_json

    parser = argparse.ArgumentParser(description="分析結果を統合してMarkdownサマリーを生成する")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    minimal_parser = subparsers.add_parser("minimal", help="レポートデータのみからの簡易サマリー(最小構成パイプライン向け)")
    minimal_parser.add_argument("--report", required=True, help="parse_mt4_report.py出力JSON")
    minimal_parser.add_argument("--validation", required=True, help="performance_metrics.py validate出力JSON")
    minimal_parser.add_argument("-o", "--output", required=True, help="出力先Markdownパス")

    full_parser = subparsers.add_parser("full", help="全分析結果を統合した詳細サマリー(フル版パイプライン向け)")
    full_parser.add_argument("--report", required=True, help="parse_mt4_report.py出力JSON")
    full_parser.add_argument("--metrics", required=True, help="performance_metrics.py from-trades出力JSON")
    full_parser.add_argument("--anomalies", required=True, help="trade_anomaly_check.py出力JSON")
    full_parser.add_argument("--period", required=True, help="period_analysis.py出力JSON")
    full_parser.add_argument("--direction", required=True, help="direction_analysis.py出力JSON")
    full_parser.add_argument("--time", required=True, help="time_analysis.py出力JSON")
    full_parser.add_argument("--regime", required=True, help="regime_analysis.py出力JSON")
    full_parser.add_argument("-o", "--output", required=True, help="出力先Markdownパス")

    args = parser.parse_args()

    if args.mode == "minimal":
        md = render_minimal_summary(load_json(args.report), load_json(args.validation))
    else:
        md = render_summary(
            load_json(args.report),
            load_json(args.metrics),
            load_json(args.anomalies),
            load_json(args.period),
            load_json(args.direction),
            load_json(args.time),
            load_json(args.regime),
        )

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(md, encoding="utf-8")
    print(f"保存しました: {args.output}")


if __name__ == "__main__":
    main()

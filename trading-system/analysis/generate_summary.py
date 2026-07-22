"""
report/metrics/anomaly/period/direction/time/regime の各分析結果をまとめ、
人間が読めるMarkdownサマリーを生成する。

このファイルが「人間の承認」ステップで実際に読む主要な成果物になる想定。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


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

    parser = argparse.ArgumentParser(description="各種分析結果を統合してMarkdownサマリーを生成する")
    parser.add_argument("--report", required=True, help="parse_mt4_report.py出力JSON")
    parser.add_argument("--metrics", required=True, help="performance_metrics.py出力JSON")
    parser.add_argument("--anomalies", required=True, help="trade_anomaly_check.py出力JSON")
    parser.add_argument("--period", required=True, help="period_analysis.py出力JSON")
    parser.add_argument("--direction", required=True, help="direction_analysis.py出力JSON")
    parser.add_argument("--time", required=True, help="time_analysis.py出力JSON")
    parser.add_argument("--regime", required=True, help="regime_analysis.py出力JSON")
    parser.add_argument("-o", "--output", required=True, help="出力先Markdownパス")
    args = parser.parse_args()

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

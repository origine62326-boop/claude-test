"""
parse_mt4_report.py のテスト。

注意: fixtures/sample_report.htm は「実際にMT4が出力したファイル」ではなく、
このプロジェクトの会話中にスクリーンショットで確認できたラベル・数値を元に
手作業で再現したものである。したがって、このテストが通ることは「パーサーが
自分自身の想定フォーマットを正しく読める」ことの確認にしかならず、
「実際のMT4出力を正しく読める」ことの保証にはならない(TODO.md参照)。
"""

from conftest import FIXTURES_DIR

from analysis.parse_mt4_report import parse_report_html


def test_parse_report_extracts_summary_fields():
    result = parse_report_html(FIXTURES_DIR / "sample_report.htm")

    assert result["bars_in_test"] == 7990
    assert result["ticks_modelled"] == 33824498
    assert result["modelling_quality_pct"] == 57.30
    assert result["mismatched_chart_errors"] == 0
    assert result["initial_deposit"] == 100000.00
    assert result["net_profit"] == -1583.42
    assert result["gross_profit"] == 4985.79
    assert result["gross_loss"] == -6569.21
    assert result["profit_factor"] == 0.76
    assert result["expected_payoff"] == -8.25
    assert result["max_drawdown"] == 1684.49
    assert result["total_trades"] == 192
    assert result["short_trades"] == 54
    assert result["long_trades"] == 138
    assert result["win_trades"] == 53
    assert result["loss_trades"] == 139
    assert result["largest_win"] == 106.10
    assert result["largest_loss"] == -54.56
    assert result["average_win"] == 94.07
    assert result["average_loss"] == -47.26
    assert result["max_consecutive_wins_count"] == 3
    assert result["max_consecutive_losses_count"] == 8
    assert result["average_consecutive_wins"] == 1
    assert result["average_consecutive_losses"] == 3


def test_parse_report_extracts_header_metadata():
    result = parse_report_html(FIXTURES_DIR / "sample_report.htm")

    assert result["symbol"] == "USDJPY"
    assert result["period"] == "H1"
    assert result["test_start"] == "2025-07-21"
    assert result["test_end"] == "2026-07-21"


def test_parse_report_reports_no_missing_fields_on_well_formed_input():
    result = parse_report_html(FIXTURES_DIR / "sample_report.htm")
    assert result["_missing_fields"] == []

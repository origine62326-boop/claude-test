"""
parse_mt4_report.py のテスト。日本語版・英語版MT4双方のレポート形式を確認する。

注意: fixtures/sample_report*.htm は「実際にMT4が出力したファイル」ではなく、
このプロジェクトの会話中にスクリーンショットで確認できたラベル・数値と、
MT4の標準的な英語表記を元に手作業で再現したものである。したがって、このテストが
通ることは「パーサーが自分自身の想定フォーマットを正しく読める」ことの確認にしかならず、
「実際のMT4出力を正しく読める」ことの保証にはならない(TODO.md参照)。
"""

import pytest
from conftest import FIXTURES_DIR

from analysis.parse_mt4_report import parse_report_html

FIXTURE_FILES = ["sample_report.htm", "sample_report_en.htm"]


@pytest.mark.parametrize("filename", FIXTURE_FILES)
def test_parse_report_extracts_all_required_fields(filename):
    result = parse_report_html(FIXTURES_DIR / filename)
    assert result["_missing_required_fields"] == [], (
        f"{filename}: 抽出できなかった必須フィールド: {result['_missing_required_fields']}"
    )


@pytest.mark.parametrize("filename", FIXTURE_FILES)
def test_parse_report_header_metadata(filename):
    result = parse_report_html(FIXTURES_DIR / filename)
    assert result["ea_name"] == "USDJPY_LowRisk_Trend_EA"
    assert result["symbol"] == "USDJPY"
    assert result["period"] == "H1"
    assert result["test_start"] == "2025-07-21"
    assert result["test_end"] == "2026-07-21"
    assert result["currency"] == "JPY"


@pytest.mark.parametrize("filename", FIXTURE_FILES)
def test_parse_report_core_metrics(filename):
    result = parse_report_html(FIXTURES_DIR / filename)

    assert result["initial_deposit"] == 100000.00
    assert result["modelling_quality_pct"] == 57.30
    assert result["mismatched_chart_errors"] == 0
    assert result["total_trades"] == 192
    assert result["net_profit"] == -1583.42
    assert result["gross_profit"] == 4985.79
    assert result["gross_loss"] == -6569.21
    assert result["profit_factor"] == 0.76
    assert result["expected_payoff"] == -8.25


@pytest.mark.parametrize("filename", FIXTURE_FILES)
def test_parse_report_drawdown(filename):
    result = parse_report_html(FIXTURES_DIR / filename)
    assert result["max_drawdown_amount"] == 1684.49
    assert result["max_drawdown_pct"] == 16.72


@pytest.mark.parametrize("filename", FIXTURE_FILES)
def test_parse_report_win_rate(filename):
    result = parse_report_html(FIXTURES_DIR / filename)
    assert result["win_trades"] == 53
    assert result["win_rate_pct"] == 27.60
    assert result["loss_trades"] == 139


@pytest.mark.parametrize("filename", FIXTURE_FILES)
def test_parse_report_consecutive_streaks(filename):
    result = parse_report_html(FIXTURES_DIR / filename)
    assert result["max_consecutive_wins"] == 3
    assert result["max_consecutive_wins_amount"] == 297.58
    assert result["max_consecutive_losses"] == 8
    assert result["max_consecutive_losses_amount"] == -401.99


@pytest.mark.parametrize("filename", FIXTURE_FILES)
def test_parse_report_bonus_fields(filename):
    result = parse_report_html(FIXTURES_DIR / filename)
    assert result["bars_in_test"] == 7990
    assert result["ticks_modelled"] == 33824498
    assert result["largest_win"] == 106.10
    assert result["largest_loss"] == -54.56
    assert result["average_win"] == 94.07
    assert result["average_loss"] == -47.26

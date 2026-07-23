"""
parse_mt4_trades.py と performance_metrics.py のテスト。
"""

from conftest import FIXTURES_DIR

from analysis.parse_mt4_report import parse_report_html
from analysis.parse_mt4_trades import parse_trades_html
from analysis.performance_metrics import (
    compute_metrics_from_trades,
    cross_check_against_report,
    validate_report_data,
)


def test_parse_trades_pairs_open_and_close_rows():
    trades = parse_trades_html(FIXTURES_DIR / "sample_trades.htm")

    assert len(trades) == 3

    buy_trade = next(t for t in trades if t["ticket"] == "1")
    assert buy_trade["type"] == "buy"
    assert buy_trade["lots"] == 0.10
    assert buy_trade["open_price"] == 163.072
    assert buy_trade["sl"] == 162.500
    assert buy_trade["tp"] == 164.200
    assert buy_trade["close_reason"] == "t/p"
    assert buy_trade["profit"] == 1128.00
    assert buy_trade["balance_after"] == 101128.00
    assert buy_trade["_unmatched_open"] is False


def test_parse_trades_handles_sell_and_close_reasons():
    trades = parse_trades_html(FIXTURES_DIR / "sample_trades.htm")

    sell_trade = next(t for t in trades if t["ticket"] == "2")
    assert sell_trade["type"] == "sell"
    assert sell_trade["close_reason"] == "s/l"
    assert sell_trade["profit"] == -600.00

    manual_close = next(t for t in trades if t["ticket"] == "3")
    assert manual_close["close_reason"] == "close"
    assert manual_close["profit"] == 350.00


def test_compute_metrics_from_sample_trades():
    trades = parse_trades_html(FIXTURES_DIR / "sample_trades.htm")
    metrics = compute_metrics_from_trades(trades)

    assert metrics["total_trades"] == 3
    assert metrics["win_trades"] == 2
    assert metrics["loss_trades"] == 1
    assert round(metrics["net_profit"], 2) == 878.00  # 1128 - 600 + 350
    assert metrics["gross_profit"] == 1478.00
    assert metrics["gross_loss"] == -600.00


def test_compute_metrics_empty_trades_does_not_crash():
    metrics = compute_metrics_from_trades([])
    assert metrics["total_trades"] == 0


def test_compute_metrics_max_consecutive_losses():
    synthetic = [
        {"profit": 10}, {"profit": -5}, {"profit": -5}, {"profit": -5},
        {"profit": 20}, {"profit": -1},
    ]
    metrics = compute_metrics_from_trades(synthetic)
    assert metrics["max_consecutive_losses"] == 3
    assert metrics["max_consecutive_wins"] == 1


def test_compute_metrics_breakeven_trade_excluded_from_win_loss():
    synthetic = [{"profit": 10}, {"profit": 0}, {"profit": -10}]
    metrics = compute_metrics_from_trades(synthetic)
    assert metrics["win_trades"] == 1
    assert metrics["loss_trades"] == 1
    assert metrics["breakeven_trades"] == 1
    assert metrics["total_trades"] == 3


def test_sample_size_reliable_flag():
    few_trades = [{"profit": 1}] * 10
    many_trades = [{"profit": 1}] * 250
    assert compute_metrics_from_trades(few_trades)["sample_size_reliable"] is False
    assert compute_metrics_from_trades(many_trades)["sample_size_reliable"] is True


def test_cross_check_detects_mismatch():
    computed = {"total_trades": 192, "net_profit": -1583.42, "profit_factor": 0.76}
    report_matching = {"total_trades": 192, "net_profit": -1583.42, "profit_factor": 0.76}
    report_mismatched = {"total_trades": 200, "net_profit": -1583.42, "profit_factor": 0.76}

    assert cross_check_against_report(computed, report_matching) == []

    mismatches = cross_check_against_report(computed, report_mismatched)
    assert len(mismatches) == 1
    assert mismatches[0]["field"] == "total_trades"


# ==== validate_report_data のテスト ====

def test_validate_report_data_clean_report_is_valid():
    report = parse_report_html(FIXTURES_DIR / "sample_report.htm")
    result = validate_report_data(report)
    assert result["is_valid"] is True
    assert result["errors"] == []
    # 取引数192件・モデリング品質57.30%はどちらも目安未満のため、警告は出る想定
    assert result["warning_count"] >= 1


def test_validate_report_data_detects_missing_required_field():
    report = parse_report_html(FIXTURES_DIR / "sample_report.htm")
    report["profit_factor"] = None
    result = validate_report_data(report)
    assert result["is_valid"] is False
    assert any(e["field"] == "profit_factor" for e in result["errors"])


def test_validate_report_data_detects_out_of_range_values():
    report = parse_report_html(FIXTURES_DIR / "sample_report.htm")
    report["win_rate_pct"] = 150.0  # あり得ない値
    result = validate_report_data(report)
    assert result["is_valid"] is False
    assert any(e["field"] == "win_rate_pct" for e in result["errors"])


def test_validate_report_data_detects_inconsistent_net_profit():
    report = parse_report_html(FIXTURES_DIR / "sample_report.htm")
    report["net_profit"] = 999999.0  # gross_profit+gross_lossと矛盾させる
    result = validate_report_data(report)
    assert result["is_valid"] is False
    assert any(e["field"] == "net_profit" for e in result["errors"])


def test_validate_report_data_warns_on_low_trade_count_and_quality():
    report = parse_report_html(FIXTURES_DIR / "sample_report.htm")
    result = validate_report_data(report)
    warning_fields = {w["field"] for w in result["warnings"]}
    assert "total_trades" in warning_fields  # 192件 < 200件の目安
    assert "modelling_quality_pct" in warning_fields  # 57.30% < 70%の目安


def test_validate_report_data_no_warning_when_thresholds_met():
    report = parse_report_html(FIXTURES_DIR / "sample_report.htm")
    report["total_trades"] = 500
    report["win_trades"] = 200
    report["loss_trades"] = 300
    report["modelling_quality_pct"] = 95.0
    report["mismatched_chart_errors"] = 0
    result = validate_report_data(report)
    assert result["warnings"] == []

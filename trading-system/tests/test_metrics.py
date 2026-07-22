"""
parse_mt4_trades.py と performance_metrics.py のテスト。
"""

from conftest import FIXTURES_DIR

from analysis.parse_mt4_trades import parse_trades_html
from analysis.performance_metrics import compute_metrics_from_trades, cross_check_against_report


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

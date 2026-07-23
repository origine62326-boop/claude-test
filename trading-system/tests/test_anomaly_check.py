"""
trade_anomaly_check.py のテスト。EAの安全設計違反を検出できるかを確認する。
"""

from analysis.trade_anomaly_check import (
    check_duplicate_entries_same_bar,
    check_lot_size_bounds,
    check_missing_stop_loss,
    check_overlapping_positions,
    check_weekend_entries,
    run_all_checks,
    summarize,
)

CLEAN_TRADES = [
    {"ticket": "1", "open_time": "2025-07-22T09:00:00", "close_time": "2025-07-22T15:00:00",
     "sl": 162.5, "lots": 0.10},
    {"ticket": "2", "open_time": "2025-07-23T10:00:00", "close_time": "2025-07-23T18:00:00",
     "sl": 164.1, "lots": 0.10},
]


def test_clean_trades_produce_no_violations():
    results = run_all_checks(CLEAN_TRADES, max_lot=1.0)
    summary = summarize(results)
    assert summary["is_clean"] is True
    assert summary["total_issues"] == 0


def test_missing_stop_loss_detected():
    trades = [{"ticket": "1", "open_time": "2025-07-22T09:00:00", "sl": None, "lots": 0.10}]
    violations = check_missing_stop_loss(trades)
    assert len(violations) == 1
    assert violations[0]["ticket"] == "1"


def test_zero_stop_loss_detected():
    trades = [{"ticket": "1", "open_time": "2025-07-22T09:00:00", "sl": 0, "lots": 0.10}]
    violations = check_missing_stop_loss(trades)
    assert len(violations) == 1


def test_overlapping_positions_detected():
    trades = [
        {"ticket": "1", "open_time": "2025-07-22T09:00:00", "close_time": "2025-07-22T15:00:00"},
        {"ticket": "2", "open_time": "2025-07-22T12:00:00", "close_time": "2025-07-22T18:00:00"},
    ]
    overlaps = check_overlapping_positions(trades)
    assert len(overlaps) == 1


def test_non_overlapping_positions_not_flagged():
    overlaps = check_overlapping_positions(CLEAN_TRADES)
    assert overlaps == []


def test_duplicate_entries_same_bar_detected():
    trades = [
        {"ticket": "1", "open_time": "2025-07-22T09:00:00"},
        {"ticket": "2", "open_time": "2025-07-22T09:00:00"},
    ]
    dupes = check_duplicate_entries_same_bar(trades)
    assert len(dupes) == 1
    assert set(dupes[0]["tickets"]) == {"1", "2"}


def test_lot_size_violations():
    trades = [
        {"ticket": "1", "lots": 0.0},
        {"ticket": "2", "lots": -0.5},
        {"ticket": "3", "lots": 2.0},
        {"ticket": "4", "lots": 0.10},
    ]
    violations = check_lot_size_bounds(trades, max_lot=1.0)
    assert len(violations) == 3


def test_weekend_entries_detected():
    trades = [
        {"ticket": "1", "open_time": "2026-07-25T09:00:00"},  # 2026-07-25は土曜
        {"ticket": "2", "open_time": "2026-07-22T09:00:00"},  # 2026-07-22は水曜
    ]
    violations = check_weekend_entries(trades)
    assert len(violations) == 1
    assert violations[0]["ticket"] == "1"

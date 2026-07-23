"""
トレード履歴を年別・月別に集計し、期間ごとの成績を比較する。

「勝率だけで判断しない」「複数期間で確認する」という評価方針(README_JP.md参照)を
実データで検証するためのモジュール。年によって成績が大きく異なる場合、
特定の相場環境に依存した(過剰最適化された)戦略である疑いがある。
"""

import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from performance_metrics import compute_metrics_from_trades  # noqa: E402


def _closed_with_open_time(trades: list[dict]) -> list[dict]:
    return [t for t in trades if t.get("profit") is not None and t.get("open_time")]


def group_by_year(trades: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for t in _closed_with_open_time(trades):
        year = datetime.fromisoformat(t["open_time"]).strftime("%Y")
        groups[year].append(t)
    return dict(sorted(groups.items()))


def group_by_month(trades: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for t in _closed_with_open_time(trades):
        month = datetime.fromisoformat(t["open_time"]).strftime("%Y-%m")
        groups[month].append(t)
    return dict(sorted(groups.items()))


def analyze_by_period(trades: list[dict]) -> dict:
    yearly = {year: compute_metrics_from_trades(group) for year, group in group_by_year(trades).items()}
    monthly = {month: compute_metrics_from_trades(group) for month, group in group_by_month(trades).items()}
    return {"yearly": yearly, "monthly": monthly}


def main():
    import argparse
    import json

    from common import load_json, save_json

    parser = argparse.ArgumentParser(description="トレード履歴を年別/月別に集計する")
    parser.add_argument("trades_json", help="parse_mt4_trades.pyが出力したトレードJSON")
    parser.add_argument("-o", "--output", help="出力先JSONパス（省略時は標準出力）")
    args = parser.parse_args()

    trades = load_json(args.trades_json)
    result = analyze_by_period(trades)

    if args.output:
        save_json(args.output, result)
        print(f"保存しました: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

"""
トレードを曜日別・時間帯別(サーバー時間)に集計する。

将来のPhase7(取引時間フィルター)のパラメータ(TradingStartHour等)を決める際の
実データに基づく参考情報として使う。特定の時間帯だけ極端に成績が悪い場合、
その時間帯を除外候補にできる。

注意: MT4のバックテストではサーバー時間=open_timeのタイムゾーンをそのまま使う。
夏時間の影響でブローカーのサーバー時間帯がシーズンによりずれる可能性がある点は
READMEにも記載の既知の制約。
"""

import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from performance_metrics import compute_metrics_from_trades  # noqa: E402

WEEKDAY_JP = ["月", "火", "水", "木", "金", "土", "日"]


def _closed_with_open_time(trades: list[dict]) -> list[dict]:
    return [t for t in trades if t.get("profit") is not None and t.get("open_time")]


def analyze_by_hour(trades: list[dict]) -> dict:
    groups: dict[str, list[dict]] = defaultdict(list)
    for t in _closed_with_open_time(trades):
        hour = datetime.fromisoformat(t["open_time"]).strftime("%H")
        groups[hour].append(t)

    return {hour: compute_metrics_from_trades(group) for hour, group in sorted(groups.items())}


def analyze_by_weekday(trades: list[dict]) -> dict:
    groups: dict[str, list[dict]] = defaultdict(list)
    for t in _closed_with_open_time(trades):
        wd = datetime.fromisoformat(t["open_time"]).weekday()
        groups[WEEKDAY_JP[wd]].append(t)

    ordered = {day: groups[day] for day in WEEKDAY_JP if day in groups}
    return {day: compute_metrics_from_trades(group) for day, group in ordered.items()}


def analyze_by_time(trades: list[dict]) -> dict:
    return {
        "by_hour": analyze_by_hour(trades),
        "by_weekday": analyze_by_weekday(trades),
    }


def main():
    import argparse
    import json

    from common import load_json, save_json

    parser = argparse.ArgumentParser(description="トレード履歴を時間帯別/曜日別に集計する")
    parser.add_argument("trades_json", help="parse_mt4_trades.pyが出力したトレードJSON")
    parser.add_argument("-o", "--output", help="出力先JSONパス（省略時は標準出力）")
    args = parser.parse_args()

    trades = load_json(args.trades_json)
    result = analyze_by_time(trades)

    if args.output:
        save_json(args.output, result)
        print(f"保存しました: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

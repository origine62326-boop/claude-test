"""
買い(buy)と売り(sell)を分けて成績を比較する。

EAの買い条件・売り条件は対称に実装されているが(設計上は)、実際の相場では
USD/JPYの方向性のクセにより成績差が出ることが多い。この差が大きい場合、
EnableLong/EnableShortの個別無効化や、方向別のパラメータ調整を検討する材料になる。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from performance_metrics import compute_metrics_from_trades  # noqa: E402


def analyze_by_direction(trades: list[dict]) -> dict:
    buys = [t for t in trades if t.get("type") == "buy" and t.get("profit") is not None]
    sells = [t for t in trades if t.get("type") == "sell" and t.get("profit") is not None]

    return {
        "buy": compute_metrics_from_trades(buys),
        "sell": compute_metrics_from_trades(sells),
    }


def main():
    import argparse
    import json

    from common import load_json, save_json

    parser = argparse.ArgumentParser(description="トレード履歴を買い/売り別に集計する")
    parser.add_argument("trades_json", help="parse_mt4_trades.pyが出力したトレードJSON")
    parser.add_argument("-o", "--output", help="出力先JSONパス（省略時は標準出力）")
    args = parser.parse_args()

    trades = load_json(args.trades_json)
    result = analyze_by_direction(trades)

    if args.output:
        save_json(args.output, result)
        print(f"保存しました: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

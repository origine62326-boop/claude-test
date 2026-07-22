"""
相場環境（レジーム）別の成績分析。

【重要な制約】
MT4の操作履歴HTMLには、エントリー時点のATR/ADX/EMAの値が含まれていない。
そのため「トレンド相場かレンジ相場か」を正確に判定することはできず、
本モジュールは以下の代替（近似）アプローチのみを提供する:

  1. 時系列を均等なN個のブロックに分割し、ブロックごとの成績を比較する
     (「相場環境を複数期間に分ける」の簡易版。regime_analysis.pyというより
     period_analysis.pyに近いが、固定の年/月境界ではなく取引数ベースで
     均等分割する点が異なる)
  2. 移動勝率(直近Mトレードの勝率)を計算し、成績が時間とともに変化しているかを見る

より正確なレジーム分析(ATR/ADXの水準別など)を行うには、EA側で
エントリー時のインジケーター値をCSVログに出力する機能を追加する必要がある。
これは将来の拡張候補としてTODO.mdに記載している。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from performance_metrics import compute_metrics_from_trades  # noqa: E402


def _closed_trades_sorted(trades: list[dict]) -> list[dict]:
    closed = [t for t in trades if t.get("profit") is not None and t.get("open_time")]
    return sorted(closed, key=lambda t: t["open_time"])


def split_into_blocks(trades: list[dict], n_blocks: int = 4) -> dict:
    """取引数が均等になるようN個のブロックに分割し、ブロックごとの指標を返す。
    時系列の前半/後半で傾向が変わっていないか(過剰最適化・レジーム依存の疑い)を見る用途。"""
    closed = _closed_trades_sorted(trades)
    if not closed:
        return {}

    n_blocks = max(1, min(n_blocks, len(closed)))
    block_size = len(closed) / n_blocks

    blocks = {}
    for i in range(n_blocks):
        start = int(i * block_size)
        end = int((i + 1) * block_size) if i < n_blocks - 1 else len(closed)
        block_trades = closed[start:end]
        if not block_trades:
            continue
        label = f"block_{i + 1}_of_{n_blocks}"
        metrics = compute_metrics_from_trades(block_trades)
        metrics["period_start"] = block_trades[0]["open_time"]
        metrics["period_end"] = block_trades[-1]["open_time"]
        blocks[label] = metrics

    return blocks


def rolling_win_rate(trades: list[dict], window: int = 30) -> list[dict]:
    """直近window件の移動勝率を計算し、時系列での推移を返す。"""
    closed = _closed_trades_sorted(trades)
    result = []
    for i in range(window, len(closed) + 1):
        chunk = closed[i - window:i]
        wins = sum(1 for t in chunk if t["profit"] > 0)
        result.append({
            "as_of_open_time": chunk[-1]["open_time"],
            "trade_index": i,
            "rolling_win_rate_pct": round((wins / window) * 100, 2),
        })
    return result


def analyze_regime(trades: list[dict], n_blocks: int = 4, rolling_window: int = 30) -> dict:
    return {
        "note": "ATR/ADXに基づく正確なレジーム分類はEA側のログ拡張が必要(TODO.md参照)。"
                "本結果は時系列ブロック分割と移動勝率による近似分析。",
        "blocks": split_into_blocks(trades, n_blocks),
        "rolling_win_rate": rolling_win_rate(trades, rolling_window),
    }


def main():
    import argparse
    import json

    from common import load_json, save_json

    parser = argparse.ArgumentParser(description="トレード履歴の時系列ブロック分析(レジーム近似分析)")
    parser.add_argument("trades_json", help="parse_mt4_trades.pyが出力したトレードJSON")
    parser.add_argument("--blocks", type=int, default=4, help="ブロック分割数(default: 4)")
    parser.add_argument("--window", type=int, default=30, help="移動勝率のウィンドウ幅(default: 30)")
    parser.add_argument("-o", "--output", help="出力先JSONパス（省略時は標準出力）")
    args = parser.parse_args()

    trades = load_json(args.trades_json)
    result = analyze_regime(trades, n_blocks=args.blocks, rolling_window=args.window)

    if args.output:
        save_json(args.output, result)
        print(f"保存しました: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

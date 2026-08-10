"""
トレード明細(parse_mt4_trades.pyの出力)と、別途取得したH1 OHLC価格履歴(MT4ヒストリー
センターからのCSVエクスポート)を突き合わせ、各トレードのMFE(Maximum Favorable Excursion)・
MAE(Maximum Adverse Excursion)をH1バー粒度で近似再構成する。

【重要な制約】DIAG-001_DATA_REQUIREMENTS.md参照。
- H1バーの高値/安値までしか分からず、ティック単位の真の値動き経路は再現できない
  (ストラテジーテスターのモデリング品質57.79%が示す通り、テスター自体もH1足からティックを
  合成しているため、ティック単位の"正解"はそもそも存在しない)
- 決済が行われたバー(exit_bar)自体も、そのバーの高値/安値までを含めて集計する。
  SL/TP到達前後どちらでその極値が付いたかはバー内では判別できない
- エントリー価格・決済価格はトレード明細側の値を正とし、CSV側のバーOpen価格とは
  数pips程度ずれうる(Bid/Ask・ブローカー気配の違い、Slippage設定等による)

出力される値は「参考値」であり、EA実装のSL/TP判定そのものを再現するものではない。
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json, save_json  # noqa: E402

PIP_SIZE = 0.01  # USDJPY


def load_h1_csv(path) -> list[dict]:
    """MT4ヒストリーセンターのCSVエクスポート(ヘッダー無し、date,time,open,high,low,close,volume)を読む。"""
    bars = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) < 6:
                continue
            date_s, time_s, o, h, l, c = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
            ts = datetime.strptime(f"{date_s} {time_s}", "%Y.%m.%d %H:%M")
            bars.append({"time": ts, "open": float(o), "high": float(h), "low": float(l), "close": float(c)})
    bars.sort(key=lambda b: b["time"])
    return bars


def _bars_in_range(bars: list[dict], start: datetime, end: datetime) -> list[dict]:
    # entry_time <= bar.time <= exit_time のバーを対象とする(entryバー・exitバーを含む)
    return [b for b in bars if start <= b["time"] <= end]


def reconstruct_trade(trade: dict, bars_index: list[dict]) -> dict:
    entry_time = datetime.fromisoformat(trade["open_time"])
    exit_time = datetime.fromisoformat(trade["close_time"])
    entry_price = trade["open_price"]
    sl = trade.get("sl")
    direction = trade.get("type")

    window = _bars_in_range(bars_index, entry_time, exit_time)
    if not window or sl is None or direction not in ("buy", "sell"):
        return {"ticket": trade.get("ticket"), "mfe_pips": None, "mae_pips": None,
                "mfe_R": None, "mae_R": None, "time_to_mfe": None, "time_to_mae": None,
                "note": "NOT_AVAILABLE (バー欠損 or sl/typeなし)"}

    stop_distance_pips = abs(entry_price - sl) / PIP_SIZE
    if stop_distance_pips <= 0:
        return {"ticket": trade.get("ticket"), "mfe_pips": None, "mae_pips": None,
                "mfe_R": None, "mae_R": None, "time_to_mfe": None, "time_to_mae": None,
                "note": "NOT_AVAILABLE (stop_distance<=0)"}

    if direction == "buy":
        best_bar = max(window, key=lambda b: b["high"])
        worst_bar = min(window, key=lambda b: b["low"])
        mfe_pips = (best_bar["high"] - entry_price) / PIP_SIZE
        mae_pips = (entry_price - worst_bar["low"]) / PIP_SIZE
    else:
        best_bar = min(window, key=lambda b: b["low"])
        worst_bar = max(window, key=lambda b: b["high"])
        mfe_pips = (entry_price - best_bar["low"]) / PIP_SIZE
        mae_pips = (worst_bar["high"] - entry_price) / PIP_SIZE

    mfe_pips = max(mfe_pips, 0.0)
    mae_pips = max(mae_pips, 0.0)

    return {
        "ticket": trade.get("ticket"),
        "mfe_pips": round(mfe_pips, 2),
        "mae_pips": round(mae_pips, 2),
        "mfe_R": round(mfe_pips / stop_distance_pips, 4),
        "mae_R": round(mae_pips / stop_distance_pips, 4),
        "time_to_mfe": best_bar["time"].isoformat(),
        "time_to_mae": worst_bar["time"].isoformat(),
        "bars_in_window": len(window),
    }


def reconstruct_all(trades: list[dict], bars: list[dict]) -> list[dict]:
    closed = [t for t in trades if t.get("close_time") and t.get("open_time")]
    results = []
    for t in closed:
        rec = reconstruct_trade(t, bars)
        rec["type"] = t.get("type")
        rec["profit"] = t.get("profit")
        results.append(rec)
    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="H1 OHLC価格履歴からMFE/MAEを近似再構成する(DIAG-001 Stage2)")
    parser.add_argument("trades_json", help="parse_mt4_trades.pyが出力したトレードJSON")
    parser.add_argument("h1_csv", help="MT4ヒストリーセンターのH1 OHLC CSVエクスポート")
    parser.add_argument("-o", "--output", help="出力先JSONパス(省略時は標準出力)")
    args = parser.parse_args()

    trades = load_json(args.trades_json)
    bars = load_h1_csv(args.h1_csv)
    result = reconstruct_all(trades, bars)

    if args.output:
        save_json(args.output, result)
        print(f"保存しました: {args.output} ({len(result)}件)")
    else:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

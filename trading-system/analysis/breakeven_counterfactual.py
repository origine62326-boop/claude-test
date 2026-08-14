"""
既存のトレード明細(EAに建値移動ロジックが実装されていない実行、例: EXP-002/DS004)に対して、
「もし建値移動ルール(H005/EXP-007と同一のBreakEvenAtR/BreakEvenOffsetPips)が有効だったら
このトレードはどう変わっていたか」を、エントリーを一切追加・削除せずに1件ずつ再計算する。

目的: EXP-007は建値移動を実装したEAを再実行した結果であり、取引数がEXP-002の195件から239件に
増えている(経路依存効果)。この反実仮想分析は、エントリーを195件のまま固定し、決済ルールだけを
差し替えることで、建値移動そのものの「純粋な効果」を経路依存の影響から分離することを目的とする。

【重要な制約】mfe_mae_reconstruction.pyと同じくH1バー粒度の近似。
- +1.0R到達と建値retreat(逆戻り)が同一バー内で両方起きた場合、どちらが先だったかは判別できない
  (AMBIGUOUSとして分離し、断定しない)
- スプレッド・スリッページ・手数料・スワップは反実仮想の決済価格計算には反映しない
  (元のトレード明細のprofitとは厳密には比較不能な近似値であることに注意)

出力される値は「参考値」であり、EA実装のExecuteEntry/ManageOpenPositionを再現するものではない。
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mfe_mae_reconstruction import load_h1_csv  # noqa: E402

PIP_SIZE = 0.01  # USDJPY


def _bars_in_range(bars: list[dict], start: datetime, end: datetime) -> list[dict]:
    return [b for b in bars if start <= b["time"] <= end]


def apply_breakeven_counterfactual(trade: dict, bars: list[dict],
                                    break_even_at_r: float = 1.0,
                                    offset_pips: float = 2.0) -> dict:
    """1トレードに対して反実仮想の建値移動を適用する。

    戻り値のoutcome:
      - "UNCHANGED": +1R未到達、または到達したが建値まで戻らず実際の結果(TP等)に到達
      - "MODIFIED": +1R到達後に建値付近まで戻ったため、建値+オフセットでの決済に差し替え
      - "AMBIGUOUS": +1R到達と建値retreatが同一バー内で発生し、順序を判別できない
      - "NOT_AVAILABLE": バー欠損・sl/type欠損等で判定不能
    """
    entry_time = datetime.fromisoformat(trade["open_time"])
    exit_time = datetime.fromisoformat(trade["close_time"]) if trade.get("close_time") else None
    entry_price = trade.get("open_price")
    sl = trade.get("sl")
    direction = trade.get("type")
    lots = trade.get("lots")
    actual_profit = trade.get("profit")

    base = {"ticket": trade.get("ticket"), "type": direction, "actual_profit": actual_profit}

    if exit_time is None or entry_price is None or sl is None or direction not in ("buy", "sell") or lots is None:
        return {**base, "outcome": "NOT_AVAILABLE", "counterfactual_profit": None}

    stop_distance_pips = abs(entry_price - sl) / PIP_SIZE
    if stop_distance_pips <= 0:
        return {**base, "outcome": "NOT_AVAILABLE", "counterfactual_profit": None}

    window = _bars_in_range(bars, entry_time, exit_time)
    if not window:
        return {**base, "outcome": "NOT_AVAILABLE", "counterfactual_profit": None}

    offset_price = offset_pips * PIP_SIZE
    if direction == "buy":
        breakeven_price = entry_price + offset_price
    else:
        breakeven_price = entry_price - offset_price

    pip_value_per_lot = (0.01 * 100000) / entry_price
    counterfactual_profit_if_modified = offset_pips * pip_value_per_lot * lots

    triggered = False
    for bar in window:
        if direction == "buy":
            favorable_pips = (bar["high"] - entry_price) / PIP_SIZE
        else:
            favorable_pips = (entry_price - bar["low"]) / PIP_SIZE
        favorable_R = favorable_pips / stop_distance_pips

        if not triggered:
            if favorable_R >= break_even_at_r:
                triggered = True
                # 同一バー内での建値retreat有無をチェック(順序判別不能ならAMBIGUOUS)
                if direction == "buy":
                    same_bar_retreat = bar["low"] <= breakeven_price
                else:
                    same_bar_retreat = bar["high"] >= breakeven_price
                if same_bar_retreat:
                    return {**base, "outcome": "AMBIGUOUS", "counterfactual_profit": None,
                            "trigger_time": bar["time"].isoformat()}
            continue

        # トリガー後: 建値retreatを探す
        if direction == "buy":
            retreated = bar["low"] <= breakeven_price
        else:
            retreated = bar["high"] >= breakeven_price
        if retreated:
            return {**base, "outcome": "MODIFIED",
                    "counterfactual_profit": round(counterfactual_profit_if_modified, 2),
                    "counterfactual_exit_time": bar["time"].isoformat()}

    return {**base, "outcome": "UNCHANGED", "counterfactual_profit": actual_profit}


def summarize(results: list[dict]) -> dict:
    modified = [r for r in results if r["outcome"] == "MODIFIED"]
    unchanged = [r for r in results if r["outcome"] == "UNCHANGED"]
    ambiguous = [r for r in results if r["outcome"] == "AMBIGUOUS"]
    not_available = [r for r in results if r["outcome"] == "NOT_AVAILABLE"]

    def _pf(rows, profit_key):
        gp = sum(r[profit_key] for r in rows if r[profit_key] and r[profit_key] > 0)
        gl = sum(r[profit_key] for r in rows if r[profit_key] and r[profit_key] < 0)
        return (gp / abs(gl)) if gl else None

    counted = modified + unchanged
    actual_net = sum(r["actual_profit"] for r in counted if r["actual_profit"] is not None)
    cf_net = sum(r["counterfactual_profit"] for r in counted if r["counterfactual_profit"] is not None)

    return {
        "n_total": len(results),
        "n_modified": len(modified),
        "n_unchanged": len(unchanged),
        "n_ambiguous": len(ambiguous),
        "n_not_available": len(not_available),
        "actual_net_profit": round(actual_net, 2),
        "counterfactual_net_profit": round(cf_net, 2),
        "actual_pf": _pf(counted, "actual_profit"),
        "counterfactual_pf": _pf(counted, "counterfactual_profit"),
    }


def main():
    import argparse
    import json

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from parse_mt4_trades import parse_trades_html  # noqa: E402

    parser = argparse.ArgumentParser(description="建値移動ルールの反実仮想適用(エントリー固定、経路依存を排除)")
    parser.add_argument("report_htm", help="トレード明細を含むMT4レポートhtm(例: EXP-002)")
    parser.add_argument("h1_csv", help="MT4ヒストリーセンターのH1 OHLC CSVエクスポート")
    parser.add_argument("--break-even-at-r", type=float, default=1.0)
    parser.add_argument("--offset-pips", type=float, default=2.0)
    parser.add_argument("-o", "--output", help="トレード単位の結果を出力するJSONパス(省略可)")
    args = parser.parse_args()

    trades = parse_trades_html(args.report_htm)
    bars = load_h1_csv(args.h1_csv)
    closed = [t for t in trades if t.get("close_time")]

    results = [apply_breakeven_counterfactual(t, bars, args.break_even_at_r, args.offset_pips) for t in closed]

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"トレード単位の結果を保存しました: {args.output}")

    print(json.dumps(summarize(results), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

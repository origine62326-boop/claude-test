"""
各トレードのエントリー時点における特徴量（ADX/ATR/EMA傾き/EMA間距離/曜日/時間帯/セッション等）を、
H1 OHLC価格履歴(DS006)から再計算してCSV化する。

【重要な前提】
- EA(`USDJPY_LowRisk_Trend_EA.mq4`)はエントリー判定時のインジケーター値をログ出力していない
  （Expertsログにはentry price/lot/ticketのみ）。よってこれらの値は「EAが実際に見た値」の
  直接記録ではなく、DS006(H1 OHLC)から本スクリプトが独立に再計算した値である
- EMA/ADX/ATRの算出方法はEA側の`iMA(..., MODE_EMA, ...)` / `iADX(...)` / `iATR(...)`
  （いずれもMQL4標準関数、Wilder方式のADX/ATR）に合わせているが、完全なbit-for-bit一致は
  保証しない（MT4内部の丸め・初期化区間の扱いの違いにより、特に系列の先頭付近で誤差がありうる）
- エントリー判定は直近の確定足(shift=1)を使う設計（EAコードコメント「未確定(shift=0)は判定に
  一切使用しない」）。よって各トレードのentry_timeの1本前(entry_time - 1H)の確定足時点の
  インジケーター値を使用する
- EMA傾き・EMA間距離は、EAの売買ロジック自体には使われていない本スクリプト独自の派生特徴量。
  定義は下記関数のdocstring参照（後から恣意的に変えない）
- スプレッドはバックテスト全体で固定値（現在値5、実測ではなく設定値）のため、トレードごとの
  変動がない。分析対象としての分散が存在しない旨を明記する
- 重要経済指標までの時間は、`research/governance/DATA_SOURCE_REGISTRY.md`の調査時点で
  無料かつ予想値付きの経済指標カレンダーを取得できるソースが確認できていないため、
  全行`NOT_AVAILABLE`とする（推測・捏造しない）
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json  # noqa: E402
from mfe_mae_reconstruction import load_h1_csv, reconstruct_trade  # noqa: E402

PIP_SIZE = 0.01


def compute_ema_series(closes: list[float], period: int) -> list[float | None]:
    alpha = 2.0 / (period + 1)
    out: list[float | None] = [None] * len(closes)
    if len(closes) < period:
        return out
    seed = sum(closes[:period]) / period
    out[period - 1] = seed
    prev = seed
    for i in range(period, len(closes)):
        prev = closes[i] * alpha + prev * (1 - alpha)
        out[i] = prev
    return out


def compute_atr_series(bars: list[dict], period: int) -> list[float | None]:
    trs: list[float] = []
    for i, b in enumerate(bars):
        if i == 0:
            trs.append(b["high"] - b["low"])
            continue
        prev_close = bars[i - 1]["close"]
        tr = max(b["high"] - b["low"], abs(b["high"] - prev_close), abs(b["low"] - prev_close))
        trs.append(tr)

    out: list[float | None] = [None] * len(bars)
    if len(trs) < period:
        return out
    seed = sum(trs[:period]) / period
    out[period - 1] = seed
    prev = seed
    for i in range(period, len(trs)):
        prev = (prev * (period - 1) + trs[i]) / period
        out[i] = prev
    return out


def compute_adx_series(bars: list[dict], period: int) -> list[float | None]:
    n = len(bars)
    plus_dm = [0.0] * n
    minus_dm = [0.0] * n
    tr = [0.0] * n
    for i in range(1, n):
        up_move = bars[i]["high"] - bars[i - 1]["high"]
        down_move = bars[i - 1]["low"] - bars[i]["low"]
        plus_dm[i] = up_move if (up_move > down_move and up_move > 0) else 0.0
        minus_dm[i] = down_move if (down_move > up_move and down_move > 0) else 0.0
        prev_close = bars[i - 1]["close"]
        tr[i] = max(bars[i]["high"] - bars[i]["low"],
                    abs(bars[i]["high"] - prev_close), abs(bars[i]["low"] - prev_close))

    def wilder_smooth(values: list[float], period: int) -> list[float | None]:
        out: list[float | None] = [None] * len(values)
        if len(values) <= period:
            return out
        seed = sum(values[1:period + 1])
        out[period] = seed
        prev = seed
        for i in range(period + 1, len(values)):
            prev = prev - (prev / period) + values[i]
            out[i] = prev
        return out

    sm_tr = wilder_smooth(tr, period)
    sm_plus_dm = wilder_smooth(plus_dm, period)
    sm_minus_dm = wilder_smooth(minus_dm, period)

    dx: list[float | None] = [None] * n
    for i in range(n):
        if sm_tr[i] is None or sm_tr[i] == 0:
            continue
        plus_di = 100.0 * sm_plus_dm[i] / sm_tr[i]
        minus_di = 100.0 * sm_minus_dm[i] / sm_tr[i]
        denom = plus_di + minus_di
        if denom == 0:
            dx[i] = 0.0
        else:
            dx[i] = 100.0 * abs(plus_di - minus_di) / denom

    adx: list[float | None] = [None] * n
    first_valid = next((i for i, v in enumerate(dx) if v is not None), None)
    if first_valid is None or first_valid + period > n:
        return adx
    seed = sum(v for v in dx[first_valid:first_valid + period] if v is not None) / period
    adx_idx = first_valid + period - 1
    adx[adx_idx] = seed
    prev = seed
    for i in range(adx_idx + 1, n):
        if dx[i] is None:
            continue
        prev = (prev * (period - 1) + dx[i]) / period
        adx[i] = prev
    return adx


def session_for_hour(hour: int) -> str:
    if 0 <= hour < 8:
        return "Asia"
    if 8 <= hour < 15:
        return "London"
    if 15 <= hour < 22:
        return "NY"
    return "LateNY_AsiaOpen"


def build_feature_rows(trades: list[dict], bars: list[dict], dataset_id: str) -> list[dict]:
    bar_index = {b["time"]: i for i, b in enumerate(bars)}
    closes = [b["close"] for b in bars]
    ema20 = compute_ema_series(closes, 20)
    ema75 = compute_ema_series(closes, 75)
    ema200 = compute_ema_series(closes, 200)
    atr14 = compute_atr_series(bars, 14)
    adx14 = compute_adx_series(bars, 14)

    rows = []
    for t in trades:
        if not t.get("close_time") or not t.get("open_time"):
            continue
        entry_time = datetime.fromisoformat(t["open_time"])
        entry_bar_time = entry_time.replace(minute=0, second=0, microsecond=0)
        # shift=1: 直近の確定足 = entry_time足そのものの1本前のバー
        entry_idx = bar_index.get(entry_bar_time)
        decision_idx = entry_idx - 1 if (entry_idx is not None and entry_idx > 0) else None

        row = {
            "dataset_id": dataset_id,
            "ticket": t.get("ticket"),
            "direction": t.get("type"),
            "entry_time": t["open_time"],
            "adx14": None,
            "atr14_pips": None,
            "ema20": None,
            "ema75": None,
            "ema200": None,
            "ema20_slope_5bar_pct": None,
            "ema75_slope_5bar_pct": None,
            "ema200_slope_5bar_pct": None,
            "ema20_75_distance_pips": None,
            "ema75_200_distance_pips": None,
            "weekday": entry_time.strftime("%a"),
            "hour": entry_time.hour,
            "session": session_for_hour(entry_time.hour),
            "minutes_to_next_high_impact_event": "NOT_AVAILABLE",
            "spread_points": 5,  # 固定設定値(現在値5)。全トレード共通、分散なし
            "profit": t.get("profit"),
        }

        if decision_idx is not None and decision_idx >= 200:
            row["adx14"] = adx14[decision_idx]
            row["atr14_pips"] = (atr14[decision_idx] / PIP_SIZE) if atr14[decision_idx] is not None else None
            row["ema20"] = ema20[decision_idx]
            row["ema75"] = ema75[decision_idx]
            row["ema200"] = ema200[decision_idx]
            if decision_idx - 5 >= 0 and ema20[decision_idx - 5]:
                row["ema20_slope_5bar_pct"] = 100.0 * (ema20[decision_idx] - ema20[decision_idx - 5]) / ema20[decision_idx - 5]
            if decision_idx - 5 >= 0 and ema75[decision_idx - 5]:
                row["ema75_slope_5bar_pct"] = 100.0 * (ema75[decision_idx] - ema75[decision_idx - 5]) / ema75[decision_idx - 5]
            if decision_idx - 5 >= 0 and ema200[decision_idx - 5]:
                row["ema200_slope_5bar_pct"] = 100.0 * (ema200[decision_idx] - ema200[decision_idx - 5]) / ema200[decision_idx - 5]
            if ema20[decision_idx] is not None and ema75[decision_idx] is not None:
                row["ema20_75_distance_pips"] = (ema20[decision_idx] - ema75[decision_idx]) / PIP_SIZE
            if ema75[decision_idx] is not None and ema200[decision_idx] is not None:
                row["ema75_200_distance_pips"] = (ema75[decision_idx] - ema200[decision_idx]) / PIP_SIZE

        mfe_mae = reconstruct_trade(t, bars)
        row["mfe_pips"] = mfe_mae.get("mfe_pips")
        row["mae_pips"] = mfe_mae.get("mae_pips")
        row["mfe_R"] = mfe_mae.get("mfe_R")
        row["mae_R"] = mfe_mae.get("mae_R")

        stop_dist = abs(t["open_price"] - t["sl"]) / PIP_SIZE if t.get("sl") else None
        pip_val = (0.01 * 100000) / t["open_price"]
        risk = stop_dist * pip_val * t["lots"] if stop_dist else None
        row["realized_R"] = (t["profit"] / risk) if risk else None
        row["result"] = "win" if t["profit"] > 0 else "loss"

        rows.append(row)
    return rows


def main():
    import argparse

    parser = argparse.ArgumentParser(description="トレードごとの特徴量CSVを生成する(統計分析用、EA非変更)")
    parser.add_argument("h1_csv", help="DS006相当のH1 OHLC CSV")
    parser.add_argument("trade_sources", nargs="+", help="dataset_id:trades_json のペアを複数指定 (例: DS001:reports/normalized/EXP-001_run01_trades.json)")
    parser.add_argument("-o", "--output", required=True, help="出力CSVパス")
    args = parser.parse_args()

    bars = load_h1_csv(args.h1_csv)
    all_rows = []
    for src in args.trade_sources:
        dataset_id, path = src.split(":", 1)
        trades = load_json(path)
        all_rows.extend(build_feature_rows(trades, bars, dataset_id))

    fieldnames = list(all_rows[0].keys()) if all_rows else []
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"保存しました: {args.output} ({len(all_rows)}行)")


if __name__ == "__main__":
    main()

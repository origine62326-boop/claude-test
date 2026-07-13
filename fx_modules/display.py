"""
予測結果のCLI表示（テーブル・テキストグラフ）
"""

from . import ui


def show_history_summary(history: list[dict]):
    ui.section("取得データ")
    print(f"  期間: {history[0]['date']} 〜 {history[-1]['date']} ({len(history)}日分)")
    print(f"  直近終値: {history[-1]['close']:.3f} 円")


def show_forecast_table(last_actual: float, predictions: list[dict]):
    ui.section("予測結果 (USD/JPY)")
    prev = last_actual
    for p in predictions:
        diff = p["close"] - prev
        arrow = f"{ui.Color.GREEN}▲{ui.Color.RESET}" if diff > 0 else (
            f"{ui.Color.RED}▼{ui.Color.RESET}" if diff < 0 else "―")
        print(f"  {p['date']}   {p['close']:>8.3f} 円   {arrow} {diff:+.3f}")
        prev = p["close"]

    total_diff = predictions[-1]["close"] - last_actual
    trend = "円安(USD高)方向" if total_diff > 0 else ("円高(USD安)方向" if total_diff < 0 else "横ばい")
    color = ui.Color.RED if total_diff > 0 else (ui.Color.GREEN if total_diff < 0 else ui.Color.WHITE)
    print(f"\n  {ui.Color.BOLD}トレンド予測: {color}{trend} ({total_diff:+.3f}円){ui.Color.RESET}")


def show_text_graph(history: list[dict], predictions: list[dict], tail: int = 30):
    ui.section("推移グラフ（実績:█ / 予測:░）")

    actual = history[-tail:]
    actual_vals = [h["close"] for h in actual]
    pred_vals = [p["close"] for p in predictions]
    all_vals = actual_vals + pred_vals

    min_v, max_v = min(all_vals), max(all_vals)
    span = max_v - min_v if max_v != min_v else 1.0

    height = 10
    print()
    for row in range(height, -1, -1):
        threshold = min_v + (span * row / height)
        line = ""
        for v in actual_vals:
            line += "█ " if v >= threshold else "  "
        for v in pred_vals:
            line += "░ " if v >= threshold else "  "
        label = f"{threshold:.2f}" if row % 2 == 0 else ""
        print(f"  {label:>8} | {line}")

    print(f"  {'':>8} +-" + "--" * len(all_vals))
    print(f"  {'':>8}   {'実績':<{len(actual_vals) * 2}}{'予測'}")

"""
FX (USD/JPY) 為替変動予測ツール
Yahoo Financeから取得した為替レート履歴をLSTMモデルで学習し、将来のレートを予測する

使い方:
    python fx_predict.py                       # 学習済みモデルがあれば再利用して予測
    python fx_predict.py --retrain             # モデルを再学習してから予測
    python fx_predict.py --forecast-days 10     # 10営業日先まで予測
"""

import argparse

from fx_modules import display, fetcher, forecast, model as model_mod, ui

DEFAULT_WINDOW = 20


def parse_args():
    parser = argparse.ArgumentParser(description="USD/JPY 為替変動予測ツール")
    parser.add_argument("--forecast-days", type=int, default=5, help="何営業日先まで予測するか (default: 5)")
    parser.add_argument("--history-range", default="2y", help="取得する履歴の範囲 (例: 1y, 2y, 5y / default: 2y)")
    parser.add_argument("--window", type=int, default=DEFAULT_WINDOW, help="予測に使う直近日数の窓幅 (default: 20)")
    parser.add_argument("--epochs", type=int, default=40, help="学習エポック数 (default: 40)")
    parser.add_argument("--retrain", action="store_true", help="保存済みモデルを使わず再学習する")
    parser.add_argument("--no-cache", action="store_true", help="レート履歴のキャッシュを使わず再取得する")
    return parser.parse_args()


def main():
    args = parse_args()
    ui.header("FX予測ツール - USD/JPY")

    ui.info("為替レート履歴を取得しています...")
    try:
        history = fetcher.fetch_history(range_=args.history_range, use_cache=not args.no_cache)
    except Exception as e:
        ui.error(f"レート履歴の取得に失敗しました: {e}")
        return

    if len(history) <= args.window:
        ui.error(f"データ件数({len(history)})が窓幅({args.window})より少ないため予測できません")
        return

    display.show_history_summary(history)
    closes = [h["close"] for h in history]

    net, scaler = (None, None) if args.retrain else model_mod.load()
    if net is not None and scaler.get("window") != args.window:
        ui.info("保存済みモデルの窓幅が異なるため再学習します")
        net = None

    if net is None:
        ui.section("モデル学習")
        ui.info(f"LSTMモデルを学習しています (epochs={args.epochs}, window={args.window})...")
        scaler = model_mod.make_scaler(closes)
        scaler["window"] = args.window
        scaled = model_mod.scale(closes, scaler)
        X, y = model_mod.make_sequences(scaled, args.window)
        net = model_mod.build_model(args.window)
        history_log = model_mod.train(net, X, y, epochs=args.epochs)
        final_loss = history_log.history["loss"][-1]
        ui.success(f"学習完了 (最終loss: {final_loss:.6f})")
        model_mod.save(net, scaler)
    else:
        ui.info("保存済みモデルを使用します（再学習するには --retrain を指定）")

    ui.section("予測実行")
    predictions = forecast.forecast_future(
        net, scaler, closes, history[-1]["date"], args.forecast_days, args.window,
    )

    display.show_forecast_table(closes[-1], predictions)
    display.show_text_graph(history, predictions)

    print(f"\n{ui.Color.DIM}※ 本ツールの予測は過去データに基づく統計的推定であり、"
          f"投資判断の根拠として利用しないでください。{ui.Color.RESET}")


if __name__ == "__main__":
    main()

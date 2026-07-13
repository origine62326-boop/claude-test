"""
学習済みモデルを使った将来レートの反復予測
"""

from datetime import datetime, timedelta

import numpy as np

from . import model as model_mod


def _next_weekday(d: datetime) -> datetime:
    d += timedelta(days=1)
    while d.weekday() >= 5:  # 5=土, 6=日
        d += timedelta(days=1)
    return d


def forecast_future(model, scaler: dict, recent_closes: list[float],
                     last_date: str, n_days: int, window: int) -> list[dict]:
    """直近window日分の終値から、n_days先までを1日ずつ反復予測する"""
    scaled_window = model_mod.scale(recent_closes[-window:], scaler).tolist()
    cur_date = datetime.strptime(last_date, "%Y-%m-%d")

    predictions = []
    for _ in range(n_days):
        x = np.array(scaled_window[-window:], dtype="float32").reshape(1, window, 1)
        next_scaled = float(model.predict(x, verbose=0)[0, 0])
        next_value = float(model_mod.unscale(np.array([next_scaled]), scaler)[0])

        cur_date = _next_weekday(cur_date)
        predictions.append({"date": cur_date.strftime("%Y-%m-%d"), "close": round(next_value, 4)})

        scaled_window.append(next_scaled)

    return predictions

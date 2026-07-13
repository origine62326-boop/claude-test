"""
LSTM予測モデルの構築・学習・保存/読み込み
"""

import json
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).parent.parent / "data"
MODEL_FILE = DATA_DIR / "usdjpy_lstm.keras"
SCALER_FILE = DATA_DIR / "usdjpy_scaler.json"


def make_scaler(values: list[float]) -> dict:
    return {"min": min(values), "max": max(values)}


def scale(values: list[float], scaler: dict) -> np.ndarray:
    lo, hi = scaler["min"], scaler["max"]
    span = hi - lo if hi != lo else 1.0
    return np.array([(v - lo) / span for v in values], dtype="float32")


def unscale(values: np.ndarray, scaler: dict) -> np.ndarray:
    lo, hi = scaler["min"], scaler["max"]
    span = hi - lo if hi != lo else 1.0
    return values * span + lo


def make_sequences(scaled_values: np.ndarray, window: int) -> tuple[np.ndarray, np.ndarray]:
    """直近window日分の値から翌日の値を予測する教師データを作る"""
    X, y = [], []
    for i in range(len(scaled_values) - window):
        X.append(scaled_values[i:i + window])
        y.append(scaled_values[i + window])
    X = np.array(X, dtype="float32").reshape(-1, window, 1)
    y = np.array(y, dtype="float32")
    return X, y


def build_model(window: int):
    from tensorflow import keras
    from tensorflow.keras import layers

    model = keras.Sequential([
        layers.Input(shape=(window, 1)),
        layers.LSTM(64, return_sequences=True),
        layers.LSTM(32),
        layers.Dense(16, activation="relu"),
        layers.Dense(1),
    ])
    model.compile(optimizer="adam", loss="mse")
    return model


def train(model, X: np.ndarray, y: np.ndarray, epochs: int, batch_size: int = 16):
    split = max(1, int(len(X) * 0.9))
    X_train, y_train = X[:split], y[:split]
    X_val, y_val = X[split:], y[split:]
    validation_data = (X_val, y_val) if len(X_val) > 0 else None
    history = model.fit(
        X_train, y_train,
        validation_data=validation_data,
        epochs=epochs,
        batch_size=batch_size,
        verbose=0,
    )
    return history


def save(model, scaler: dict):
    DATA_DIR.mkdir(exist_ok=True)
    model.save(MODEL_FILE)
    with open(SCALER_FILE, "w", encoding="utf-8") as f:
        json.dump(scaler, f)


def load():
    """保存済みモデルとスケーラーを返す。無ければ (None, None)"""
    if not MODEL_FILE.exists() or not SCALER_FILE.exists():
        return None, None
    from tensorflow import keras
    model = keras.models.load_model(MODEL_FILE)
    with open(SCALER_FILE, encoding="utf-8") as f:
        scaler = json.load(f)
    return model, scaler

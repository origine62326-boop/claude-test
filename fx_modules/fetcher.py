"""
為替レート取得モジュール
Yahoo Financeのchart APIから USD/JPY の日次終値を取得する
"""

import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
CACHE_FILE = DATA_DIR / "usdjpy_history.json"
CACHE_MAX_AGE_SEC = 6 * 3600  # 6時間

SYMBOL = "JPY=X"  # Yahoo Finance上のUSD/JPYティッカー
CHART_URL = f"https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}"


def fetch_history(range_: str = "2y", use_cache: bool = True) -> list[dict]:
    """USD/JPYの日次終値履歴を [{date, close}, ...] の形式で返す"""
    if use_cache and _cache_is_fresh():
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)

    history = _fetch_from_yahoo(range_)
    DATA_DIR.mkdir(exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    return history


def _cache_is_fresh() -> bool:
    if not CACHE_FILE.exists():
        return False
    age = time.time() - CACHE_FILE.stat().st_mtime
    return age < CACHE_MAX_AGE_SEC


def _fetch_from_yahoo(range_: str) -> list[dict]:
    url = f"{CHART_URL}?range={range_}&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.load(resp)

    result = payload["chart"]["result"][0]
    timestamps = result["timestamp"]
    closes = result["indicators"]["quote"][0]["close"]

    history = []
    for ts, close in zip(timestamps, closes):
        if close is None:
            continue
        date = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        history.append({"date": date, "close": round(close, 4)})
    return history

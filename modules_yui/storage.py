"""
結衣専用ストレージ管理
data_yui/ ディレクトリにデータを保存する
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data_yui"


def _ensure():
    DATA_DIR.mkdir(exist_ok=True)


def load(filename: str) -> dict:
    _ensure()
    p = DATA_DIR / filename
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(filename: str, data: dict | list):
    _ensure()
    with open(DATA_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_list(filename: str) -> list:
    _ensure()
    p = DATA_DIR / filename
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_list(filename: str, data: list):
    _ensure()
    with open(DATA_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

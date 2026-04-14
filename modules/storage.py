"""
共通ストレージ管理モジュール
JSONファイルを使ったデータの読み書きを管理する
"""

import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def _ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)


def load(filename: str) -> dict | list:
    _ensure_data_dir()
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return {}
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def save(filename: str, data: dict | list):
    _ensure_data_dir()
    filepath = DATA_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_list(filename: str) -> list:
    _ensure_data_dir()
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return []
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def save_list(filename: str, data: list):
    _ensure_data_dir()
    filepath = DATA_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

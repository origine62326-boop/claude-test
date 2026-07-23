"""
analysis/ 配下の各モジュールで共有する小さなユーティリティ群。
JSON入出力とパス解決のみを扱う（分析ロジックは各モジュールに置く）。
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
REPORTS_RAW_DIR = ROOT_DIR / "reports" / "raw"
REPORTS_NORMALIZED_DIR = ROOT_DIR / "reports" / "normalized"
REPORTS_ANALYZED_DIR = ROOT_DIR / "reports" / "analyzed"
OUTPUTS_SUMMARIES_DIR = ROOT_DIR / "outputs" / "summaries"
OUTPUTS_COMPARISONS_DIR = ROOT_DIR / "outputs" / "comparisons"
CONFIGS_DIR = ROOT_DIR / "configs"


def load_json(path) -> dict | list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def to_float(text: str) -> float | None:
    """'1,234.56%' や '-8.25' のような文字列から数値を取り出す。取れなければNone。"""
    if text is None:
        return None
    cleaned = text.strip().replace(",", "").replace("%", "").replace("円", "")
    if cleaned in ("", "-", "N/A"):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None

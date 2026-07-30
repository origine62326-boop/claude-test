"""
analysis/ 配下の各モジュールで共有する小さなユーティリティ群。
JSON入出力とパス解決のみを扱う（分析ロジックは各モジュールに置く）。
"""

import json
from pathlib import Path

# MT4は言語設定によって出力HTMLの文字コードが変わる(日本語版はcp932/Shift-JIS、
# 英語版はASCII/UTF-8であることが多い)。事前に判別する手段がないため、UTF-8で
# 厳密にデコードを試し、失敗した場合のみcp932にフォールバックする。

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


def read_html_file(path) -> str:
    """MT4が出力したHTMLレポート/操作履歴を、文字コードを判別しつつ読み込む。
    UTF-8で厳密にデコードできればそれを使い、できなければcp932(Shift-JIS)として
    デコードする。どちらも失敗する場合のみ、文字が欠落しうることを許容してUTF-8+
    置換デコードにフォールバックする(例外は投げない、既存の欠損耐性方針に合わせる)。"""
    raw_bytes = Path(path).read_bytes()
    try:
        return raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        pass
    try:
        return raw_bytes.decode("cp932")
    except UnicodeDecodeError:
        return raw_bytes.decode("utf-8", errors="replace")


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

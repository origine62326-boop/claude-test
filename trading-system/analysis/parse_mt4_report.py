"""
MT4ストラテジーテスターの「結果」タブをHTML保存したファイルをパースし、
正規化されたサマリーJSONを生成する。

注意（重要）:
  このパーサーは実際にMT4から出力されたHTMLファイルでの検証がまだ済んでいない。
  ラベル文言は本プロジェクトの会話中でスクリーンショットから確認できた範囲
  （テストバー数・純利益・総利益・総損失・プロフィットファクター等）を元にした
  best-effortの実装であり、正規表現は多少のゆらぎを許容するようにしてある。
  実ファイルで解析結果がおかしい場合は、該当ファイルを共有のうえパターンを調整すること。
  (TODO.md 参照)

パース方針:
  1. HTML内の全<td>セルをテキストとして順序通りに1本のリストへ平坦化する
  2. フィールドを「MT4レポートに出現する順序」で定義しておく
  3. カーソルを前方にしか進めない形で、各フィールドのラベルを順番に探す
     → 同じ語（例:「勝トレード」）が複数箇所に出現しても、出現順を頼りに正しく対応させる
  4. ラベルが見つかったセルの直後のセルを値として数値化する
  5. 見つからないフィールドはNoneとし、例外は投げない（欠損に強くする）
"""

import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import save_json, to_float  # noqa: E402

# (JSONキー, ラベル候補の正規表現リスト) を、レポート上に出現する順序で並べたもの
FIELD_SEQUENCE = [
    ("bars_in_test", [r"テストバー数", r"バー数"]),
    ("ticks_modelled", [r"モデルティック数"]),
    ("modelling_quality_pct", [r"モデリング品質"]),
    ("mismatched_chart_errors", [r"不整合チャートエラー"]),
    ("initial_deposit", [r"初期証拠金"]),
    ("net_profit", [r"純利益"]),
    ("gross_profit", [r"総利益"]),
    ("gross_loss", [r"総損失"]),
    ("profit_factor", [r"プロフィットファクター"]),
    ("expected_payoff", [r"期待利得"]),
    ("absolute_drawdown", [r"絶対ドローダウン"]),
    ("max_drawdown", [r"最大ドローダウン"]),
    ("relative_drawdown_pct", [r"相対ドローダウン"]),
    ("total_trades", [r"総取引数"]),
    ("short_trades", [r"売りポジション"]),
    ("long_trades", [r"買いポジション"]),
    ("win_trades", [r"勝トレード"]),
    ("loss_trades", [r"敗トレード", r"負けトレード"]),
    ("largest_win", [r"最大.{0,4}勝トレード"]),
    ("largest_loss", [r"最大.{0,4}敗トレード"]),
    ("average_win", [r"平均.{0,4}勝トレード"]),
    ("average_loss", [r"平均.{0,4}敗トレード"]),
    ("max_consecutive_wins_amount", [r"連勝.{0,4}金額", r"最大.{0,4}連勝"]),
    ("max_consecutive_losses_amount", [r"連敗.{0,4}金額", r"最大.{0,4}連敗"]),
    ("max_consecutive_wins_count", [r"連勝.{0,4}トレード数"]),
    ("max_consecutive_losses_count", [r"連敗.{0,4}トレード数"]),
    ("average_consecutive_wins", [r"平均連勝", r"平均.{0,4}連勝"]),
    ("average_consecutive_losses", [r"平均連敗", r"平均.{0,4}連敗"]),
]

# 数値の前に付随する「回数(金額)」表記等から、先頭の数値だけを取り出す正規表現
NUMERIC_RE = re.compile(r"-?[\d,]+\.?\d*")


def _flatten_cells(soup: BeautifulSoup) -> list[str]:
    cells = []
    for td in soup.find_all("td"):
        text = td.get_text(strip=True)
        if text:
            cells.append(text)
    return cells


def _extract_first_number(text: str) -> float | None:
    m = NUMERIC_RE.search(text)
    if not m:
        return None
    return to_float(m.group(0))


def _find_value_after(cells: list[str], patterns: list[str], start: int) -> tuple[float | None, int]:
    """start以降でpatternsのいずれかにマッチする最初のセルを探し、直後のセルから数値を取る。
    見つかった場合は (値, 直後セルのインデックス) を返す。見つからなければ (None, start)。"""
    for i in range(start, len(cells)):
        for pat in patterns:
            if re.search(pat, cells[i]):
                if i + 1 < len(cells):
                    value = _extract_first_number(cells[i + 1])
                    return value, i + 2
                return None, i + 1
    return None, start


def _extract_header_metadata(raw_html: str) -> dict:
    """通貨ペア・時間足・テスト期間・EA名など、先頭の説明部分を緩めに抽出する。
    見つからない項目はNoneのままにする(致命的ではないため)。"""
    meta = {"symbol": None, "period": None, "test_start": None, "test_end": None, "ea_name": None}

    ea_match = re.search(r"([A-Za-z0-9_]*LowRisk[A-Za-z0-9_]*)", raw_html)
    if ea_match:
        meta["ea_name"] = ea_match.group(1)

    symbol_match = re.search(r"(USDJPY)", raw_html)
    if symbol_match:
        meta["symbol"] = symbol_match.group(1)

    period_match = re.search(r"\b(H1|M1|M5|M15|M30|H4|D1|W1|MN1)\b", raw_html)
    if period_match:
        meta["period"] = period_match.group(1)

    date_match = re.search(
        r"(\d{4}[.\-]\d{2}[.\-]\d{2})\D{1,10}(\d{4}[.\-]\d{2}[.\-]\d{2})", raw_html
    )
    if date_match:
        meta["test_start"] = date_match.group(1).replace(".", "-")
        meta["test_end"] = date_match.group(2).replace(".", "-")

    return meta


def parse_report_html(path) -> dict:
    path = Path(path)
    raw_html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(raw_html, "html.parser")
    cells = _flatten_cells(soup)

    result: dict = {"source_file": str(path)}
    result.update(_extract_header_metadata(raw_html))

    cursor = 0
    missing_fields = []
    for key, patterns in FIELD_SEQUENCE:
        value, cursor = _find_value_after(cells, patterns, cursor)
        result[key] = value
        if value is None:
            missing_fields.append(key)

    result["_missing_fields"] = missing_fields
    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="MT4レポートHTMLを正規化JSONへ変換する")
    parser.add_argument("input", help="MT4から保存したレポートHTMLファイルのパス")
    parser.add_argument("-o", "--output", help="出力先JSONパス（省略時は標準出力）")
    args = parser.parse_args()

    data = parse_report_html(args.input)

    if data["_missing_fields"]:
        print(f"[WARN] 抽出できなかったフィールド: {data['_missing_fields']}")

    if args.output:
        save_json(args.output, data)
        print(f"保存しました: {args.output}")
    else:
        import json

        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

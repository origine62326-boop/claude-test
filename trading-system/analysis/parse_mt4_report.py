"""
MT4ストラテジーテスターの「結果」タブをHTML保存したファイルをパースし、
正規化されたサマリーJSONを生成する。

日本語版・英語版どちらのMT4のUIで出力されたレポートも読めるよう、
フィールドごとに日本語ラベルと英語ラベルの両方を候補として持たせている。

注意（重要）:
  このパーサーは実際にMT4から出力されたHTMLファイルでの検証がまだ済んでいない。
  ラベル文言はこれまでの会話中でスクリーンショットから確認できた日本語表記と、
  MT4の標準的な英語表記から推測したものであり、best-effortの実装である。
  実ファイルで解析結果がおかしい場合は、該当ファイルを共有のうえパターンを調整すること。
  (TODO.md 参照)

パース方針:
  1. HTML内の全<td>セルをテキストとして順序通りに1本のリストへ平坦化する
  2. フィールドを「MT4レポートに出現する順序」で定義しておく
  3. カーソルを前方にしか進めない形で、各フィールドのラベルを順番に探す
     → 同じ語が複数箇所に出現しても、出現順を頼りに正しく対応させる
  4. ラベルが見つかったセルの直後のセルを値として数値化する
     - 「1684.49 (16.72%)」のように主値と括弧内の副値が同じセルに入っている場合は
       両方を切り出す(例: 最大ドローダウン額/率、勝率、最大連勝/連敗)
  5. 見つからないフィールドはNoneとし、例外は投げない（欠損に強くする）
"""

import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import save_json, to_float  # noqa: E402

# ユーザーが明示的に要求した必須フィールド(このリストの充足状況をvalidate側で重視する)
REQUIRED_FIELDS = [
    "ea_name", "symbol", "period", "test_start", "test_end",
    "initial_deposit", "currency",
    "modelling_quality_pct", "mismatched_chart_errors",
    "total_trades", "net_profit", "gross_profit", "gross_loss",
    "profit_factor", "expected_payoff",
    "max_drawdown_amount", "max_drawdown_pct",
    "win_rate_pct", "max_consecutive_wins", "max_consecutive_losses",
]

# (JSONキー, ラベル候補の正規表現リスト, "single"|"dual") をレポート出現順に並べたもの。
# "dual" は「主値 (副値)」形式のセルから2つの数値を取り出すフィールド。
FIELD_SEQUENCE = [
    ("bars_in_test", [r"テストバー数", r"バー数", r"Bars in test"], "single"),
    ("ticks_modelled", [r"モデルティック数", r"Ticks modelled"], "single"),
    ("modelling_quality_pct", [r"モデリング品質", r"Modelling quality"], "single"),
    ("mismatched_chart_errors", [r"不整合チャートエラー", r"Mismatched chart errors"], "single"),
    ("initial_deposit", [r"初期証拠金", r"Initial deposit"], "single"),
    ("net_profit", [r"純利益", r"Total net profit", r"Net profit"], "single"),
    ("gross_profit", [r"総利益", r"Gross profit"], "single"),
    ("gross_loss", [r"総損失", r"Gross loss"], "single"),
    ("profit_factor", [r"プロフィットファクター", r"Profit factor"], "single"),
    ("expected_payoff", [r"期待値", r"期待利得", r"Expected payoff"], "single"),
    ("_absolute_drawdown", [r"絶対ドローダウン", r"Absolute drawdown"], "single"),
    ("_max_drawdown_cell", [r"最大ドローダウン", r"Maximal drawdown"], "dual"),
    ("_relative_drawdown_cell", [r"相対ドローダウン", r"Relative drawdown"], "dual"),
    ("total_trades", [r"総取引数", r"総取引回数", r"Total trades"], "single"),
    ("_short_positions_cell", [r"売りポジション", r"Short positions"], "dual"),
    ("_long_positions_cell", [r"買いポジション", r"Long positions"], "dual"),
    ("_win_trades_cell", [r"勝トレード", r"Profit trades"], "dual"),
    ("_loss_trades_cell", [r"敗トレード", r"負けトレード", r"Loss trades"], "dual"),
    ("largest_win", [r"最大.{0,4}勝トレード", r"Largest profit trade"], "single"),
    ("largest_loss", [r"最大.{0,4}敗トレード", r"Largest loss trade"], "single"),
    ("average_win", [r"平均.{0,4}勝トレード", r"Average profit trade"], "single"),
    ("average_loss", [r"平均.{0,4}敗トレード", r"Average loss trade"], "single"),
    ("_max_consecutive_wins_amount_cell", [r"最大連勝.{0,4}金額", r"Maxi?mum consecutive wins.{0,6}\$"], "dual"),
    ("_max_consecutive_losses_amount_cell", [r"最大連敗.{0,4}金額", r"Maxi?mum consecutive losses.{0,6}\$"], "dual"),
    ("_max_consecutive_wins_count_cell", [r"最大連勝.{0,4}トレード数", r"consecutive wins.{0,6}count"], "dual"),
    ("_max_consecutive_losses_count_cell", [r"最大連敗.{0,4}トレード数", r"consecutive losses.{0,6}count"], "dual"),
]

NUMERIC_RE = re.compile(r"-?[\d,]+\.?\d*")
DUAL_NUMERIC_RE = re.compile(r"(-?[\d,]+\.?\d*)(?:\s*\((-?[\d,]+\.?\d*)%?\))?")
CURRENCY_RE = re.compile(r"\b(JPY|USD|EUR|GBP|AUD|CHF|CAD|NZD)\b")


def _flatten_cells(soup: BeautifulSoup) -> list[str]:
    cells = []
    for td in soup.find_all("td"):
        text = td.get_text(strip=True)
        if text:
            cells.append(text)
    return cells


def _extract_single(text: str) -> float | None:
    m = NUMERIC_RE.search(text)
    return to_float(m.group(0)) if m else None


def _extract_dual(text: str) -> tuple[float | None, float | None]:
    m = DUAL_NUMERIC_RE.search(text)
    if not m:
        return None, None
    primary = to_float(m.group(1))
    secondary = to_float(m.group(2)) if m.group(2) else None
    return primary, secondary


def _find_value_after(cells: list[str], patterns: list[str], start: int, mode: str):
    """start以降でpatternsのいずれかにマッチする最初のセルを探し、直後のセルから値を取る。
    mode="single"なら数値1つ、mode="dual"なら(主値, 副値)のタプルを返す。
    見つかった場合は (値, 直後セルのインデックス) を返す。見つからなければ (None, start)。"""
    for i in range(start, len(cells)):
        for pat in patterns:
            if re.search(pat, cells[i], re.IGNORECASE):
                if i + 1 < len(cells):
                    value = _extract_dual(cells[i + 1]) if mode == "dual" else _extract_single(cells[i + 1])
                    return value, i + 2
                return (None, None) if mode == "dual" else None, i + 1
    return (None, None) if mode == "dual" else None, start


def _extract_currency(raw_html: str, cells: list[str]) -> str | None:
    """初期証拠金のセル付近、それでも見つからなければ文書全体から通貨コードを探す。
    MT4の標準レポートに必ず単独の通貨フィールドがあるとは限らないため、確度の低い
    best-effort推定であることに注意(見つからなければNoneのまま)。"""
    for i, cell in enumerate(cells):
        if re.search(r"初期証拠金|Initial deposit", cell, re.IGNORECASE):
            window = " ".join(cells[i:i + 3])
            m = CURRENCY_RE.search(window)
            if m:
                return m.group(1)
    m = CURRENCY_RE.search(raw_html)
    return m.group(1) if m else None


def _extract_header_metadata(raw_html: str, cells: list[str]) -> dict:
    """通貨ペア・時間足・テスト期間・EA名・通貨など、先頭の説明部分を緩めに抽出する。
    見つからない項目はNoneのままにする(致命的ではないため)。"""
    meta = {"symbol": None, "period": None, "test_start": None, "test_end": None,
            "ea_name": None, "currency": None}

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

    meta["currency"] = _extract_currency(raw_html, cells)

    return meta


def parse_report_html(path) -> dict:
    path = Path(path)
    raw_html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(raw_html, "html.parser")
    cells = _flatten_cells(soup)

    result: dict = {"source_file": str(path)}
    result.update(_extract_header_metadata(raw_html, cells))

    raw_values = {}
    cursor = 0
    for key, patterns, mode in FIELD_SEQUENCE:
        value, cursor = _find_value_after(cells, patterns, cursor, mode)
        raw_values[key] = value

    # dual値セルを、要求されたフィールド名へ展開する
    result["total_trades"] = raw_values["total_trades"]
    result["net_profit"] = raw_values["net_profit"]
    result["gross_profit"] = raw_values["gross_profit"]
    result["gross_loss"] = raw_values["gross_loss"]
    result["profit_factor"] = raw_values["profit_factor"]
    result["expected_payoff"] = raw_values["expected_payoff"]
    result["initial_deposit"] = raw_values["initial_deposit"]
    result["modelling_quality_pct"] = raw_values["modelling_quality_pct"]
    result["mismatched_chart_errors"] = raw_values["mismatched_chart_errors"]

    result["max_drawdown_amount"], dd_pct = raw_values["_max_drawdown_cell"]
    # 「相対ドローダウン」セルは "16.72% (1684.49)" のように率が先に来る(逆順)ため、
    # フォールバックとして使う場合は主値(=率)の方を採用する
    rel_dd_pct, _ = raw_values["_relative_drawdown_cell"]
    result["max_drawdown_pct"] = dd_pct if dd_pct is not None else rel_dd_pct

    win_count, win_pct = raw_values["_win_trades_cell"]
    result["win_trades"] = win_count
    result["win_rate_pct"] = win_pct

    loss_count, loss_pct = raw_values["_loss_trades_cell"]
    result["loss_trades"] = loss_count
    result["loss_rate_pct"] = loss_pct

    result["short_trades"], result["short_win_rate_pct"] = raw_values["_short_positions_cell"]
    result["long_trades"], result["long_win_rate_pct"] = raw_values["_long_positions_cell"]

    # 連勝/連敗は「トレード数」セルの主値(=回数)を正とし、「金額」セルの主値(=金額)を
    # 補助情報として添える。どちらか一方しか無いレポートでも取れた方を使う。
    wins_count, _ = raw_values["_max_consecutive_wins_count_cell"]
    wins_amount, wins_count_fallback = raw_values["_max_consecutive_wins_amount_cell"]
    result["max_consecutive_wins"] = wins_count if wins_count is not None else wins_count_fallback
    result["max_consecutive_wins_amount"] = wins_amount

    losses_count, _ = raw_values["_max_consecutive_losses_count_cell"]
    losses_amount, losses_count_fallback = raw_values["_max_consecutive_losses_amount_cell"]
    result["max_consecutive_losses"] = losses_count if losses_count is not None else losses_count_fallback
    result["max_consecutive_losses_amount"] = losses_amount

    # おまけ情報(要求リストには無いが、抽出コストがほぼゼロで診断に有用なもの)
    result["bars_in_test"] = raw_values["bars_in_test"]
    result["ticks_modelled"] = raw_values["ticks_modelled"]
    result["absolute_drawdown"] = raw_values["_absolute_drawdown"]
    result["largest_win"] = raw_values["largest_win"]
    result["largest_loss"] = raw_values["largest_loss"]
    result["average_win"] = raw_values["average_win"]
    result["average_loss"] = raw_values["average_loss"]

    _coerce_integer_fields(result)

    result["_missing_required_fields"] = [f for f in REQUIRED_FIELDS if result.get(f) is None]

    return result


# 本来整数であるフィールドは、to_float()がdoubleを返す都合上「192.0」のような表示に
# なってしまうため、ここでintへ丸め直す(表示・JSON出力を見やすくするための後処理)
INTEGER_FIELDS = [
    "total_trades", "mismatched_chart_errors", "win_trades", "loss_trades",
    "short_trades", "long_trades", "max_consecutive_wins", "max_consecutive_losses",
    "bars_in_test", "ticks_modelled",
]


def _coerce_integer_fields(result: dict) -> None:
    for field in INTEGER_FIELDS:
        if result.get(field) is not None:
            result[field] = int(round(result[field]))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="MT4レポートHTMLを正規化JSONへ変換する")
    parser.add_argument("input", help="MT4から保存したレポートHTMLファイルのパス")
    parser.add_argument("-o", "--output", help="出力先JSONパス（省略時は標準出力）")
    args = parser.parse_args()

    data = parse_report_html(args.input)

    if data["_missing_required_fields"]:
        print(f"[WARN] 抽出できなかった必須フィールド: {data['_missing_required_fields']}")

    if args.output:
        save_json(args.output, data)
        print(f"保存しました: {args.output}")
    else:
        import json

        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

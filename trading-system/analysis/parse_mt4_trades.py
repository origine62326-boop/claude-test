"""
MT4ストラテジーテスターの「操作履歴」タブをHTML保存したファイルをパースし、
1ポジション1レコードに正規化したトレードリストJSONを生成する。

MT4の操作履歴は「新規注文の行」と「決済の行」が別々の行として出力され、
同じ注文番号(チケット)が2回登場する。本モジュールはチケット番号で
open行とclose行をペアリングし、1トレード=1レコードにまとめる。

列の並びは標準的なMT4の操作履歴に合わせて固定順とみなす:
  # | 時間 | 種別 | 注文 | 数量 | 価格 | S/L | T/P | 損益 | 残高

注意（重要）: parse_mt4_report.py と同様、実ファイルでの検証はまだ済んでいない。
実際の列数・順序が異なる場合は本モジュールの COLUMN_* 定数を調整すること。
"""

import re
import sys
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import read_html_file, save_json, to_float  # noqa: E402

COL_INDEX = "#"
COL_TIME = "time"
COL_TYPE = "type"
COL_ORDER = "order"
COL_LOTS = "lots"
COL_PRICE = "price"
COL_SL = "sl"
COL_TP = "tp"
COL_PROFIT = "profit"
COL_BALANCE = "balance"
COLUMN_ORDER = [COL_INDEX, COL_TIME, COL_TYPE, COL_ORDER, COL_LOTS, COL_PRICE, COL_SL, COL_TP, COL_PROFIT, COL_BALANCE]

OPEN_TYPES = {"buy", "sell"}
CLOSE_TYPES = {"t/p", "s/l", "close", "close at market", "決済"}

TIME_FORMATS = ["%Y.%m.%d %H:%M", "%Y.%m.%d %H:%M:%S"]


def _parse_time(text: str) -> str | None:
    text = text.strip()
    for fmt in TIME_FORMATS:
        try:
            return datetime.strptime(text, fmt).isoformat()
        except ValueError:
            continue
    return None


def _find_trade_table(soup: BeautifulSoup):
    """「損益」列を含むtableを操作履歴テーブルとみなす。見つからなければNone。"""
    for table in soup.find_all("table"):
        text = table.get_text()
        if "損益" in text or "Profit" in text:
            return table
    return None


def _row_cells(tr) -> list[str]:
    """<td>のcolspanを展開してからテキストを取り出す。実MT4出力では、新規注文行の
    損益・残高列が未確定のため、この2列が1つの<td colspan=2></td>にまとめられて
    出力される場合がある(確認済み: RakutenSecurities-Demo, Build 1475)。colspanを
    無視すると列数がCOLUMN_ORDERより1つ少なくなり、行ごと除外されてしまう。"""
    cells = []
    for td in tr.find_all("td"):
        text = td.get_text(strip=True)
        try:
            colspan = int(td.get("colspan", 1))
        except (TypeError, ValueError):
            colspan = 1
        cells.extend([text] * max(colspan, 1))
    return cells


def _parse_raw_rows(table) -> list[dict]:
    rows = []
    for tr in table.find_all("tr"):
        cells = _row_cells(tr)
        if len(cells) < len(COLUMN_ORDER):
            continue  # ヘッダー行・区切り行等はスキップ
        row_type = cells[2].strip().lower()
        if row_type not in OPEN_TYPES and row_type not in CLOSE_TYPES:
            continue  # データ行以外(ヘッダー等)を除外
        row = dict(zip(COLUMN_ORDER, cells))
        rows.append(row)
    return rows


def _pair_trades(raw_rows: list[dict]) -> list[dict]:
    opens: dict[str, dict] = {}
    trades: list[dict] = []

    for row in raw_rows:
        ticket = row[COL_ORDER]
        row_type = row[COL_TYPE].strip().lower()

        if row_type in OPEN_TYPES:
            opens[ticket] = row
            continue

        if row_type in CLOSE_TYPES:
            open_row = opens.pop(ticket, None)
            trade = {
                "ticket": ticket,
                "type": (open_row or row)[COL_TYPE].strip().lower(),
                "lots": to_float((open_row or row)[COL_LOTS]),
                "open_time": _parse_time(open_row[COL_TIME]) if open_row else None,
                "open_price": to_float(open_row[COL_PRICE]) if open_row else None,
                "sl": to_float((open_row or row)[COL_SL]),
                "tp": to_float((open_row or row)[COL_TP]),
                "close_time": _parse_time(row[COL_TIME]),
                "close_reason": row_type,
                "close_price": to_float(row[COL_PRICE]),
                "profit": to_float(row[COL_PROFIT]),
                "balance_after": to_float(row[COL_BALANCE]),
                "_unmatched_open": open_row is None,
            }
            trades.append(trade)

    # 決済されないまま残った新規行(テスト終了時に建玉が残っていた等)も記録しておく
    for ticket, open_row in opens.items():
        trades.append({
            "ticket": ticket,
            "type": open_row[COL_TYPE].strip().lower(),
            "lots": to_float(open_row[COL_LOTS]),
            "open_time": _parse_time(open_row[COL_TIME]),
            "open_price": to_float(open_row[COL_PRICE]),
            "sl": to_float(open_row[COL_SL]),
            "tp": to_float(open_row[COL_TP]),
            "close_time": None,
            "close_reason": None,
            "close_price": None,
            "profit": None,
            "balance_after": None,
            "_unmatched_open": False,
            "_still_open_at_test_end": True,
        })

    trades.sort(key=lambda t: t["open_time"] or "")
    return trades


def parse_trades_html(path) -> list[dict]:
    path = Path(path)
    raw_html = read_html_file(path)
    soup = BeautifulSoup(raw_html, "html.parser")

    table = _find_trade_table(soup)
    if table is None:
        return []

    raw_rows = _parse_raw_rows(table)
    return _pair_trades(raw_rows)


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="MT4操作履歴HTMLを正規化トレードJSONへ変換する")
    parser.add_argument("input", help="MT4から保存した操作履歴HTMLファイルのパス")
    parser.add_argument("-o", "--output", help="出力先JSONパス（省略時は標準出力）")
    args = parser.parse_args()

    trades = parse_trades_html(args.input)

    unmatched = [t for t in trades if t.get("_unmatched_open")]
    still_open = [t for t in trades if t.get("_still_open_at_test_end")]
    if unmatched:
        print(f"[WARN] open行が見つからなかった決済行: {len(unmatched)}件")
    if still_open:
        print(f"[WARN] テスト終了時に未決済のまま残ったポジション: {len(still_open)}件")

    if args.output:
        save_json(args.output, trades)
        print(f"保存しました: {args.output} ({len(trades)}トレード)")
    else:
        print(json.dumps(trades, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

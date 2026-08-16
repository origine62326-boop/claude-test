"""
HistData ASCII M1 CSV を MT4 ヒストリーセンター取り込み形式へ変換する。

【入力形式（実ファイルから確認、推測ではない）】
    20250801 000000;150.585000;150.585000;150.569000;150.571000;0
    YYYYMMDD HHMMSS;Open;High;Low;Close;Volume    セミコロン区切り、ヘッダー無し
    - 秒フィールドは全行00（M1バーの開始時刻）
    - Volumeは全行0（出来高情報なし）

【出力形式（MT4ヒストリーセンターのインポート想定）】
    2025.08.01,07:00,150.585,150.585,150.569,150.571,0
    YYYY.MM.DD,HH:MM,Open,High,Low,Close,Volume   カンマ区切り

【タイムゾーン変換について（最重要）】

HistDataのタイムスタンプとRakuten MT4サーバー時間の差は **固定ではない**。
2025-08〜10のPOCで実測した結果:

    2025-10-24(金)まで : MT4時刻 = HistData時刻 + 7時間
    2025-10-27(月)から : MT4時刻 = HistData時刻 + 8時間

変化点は2025-10-25/26の週末。同じ週末にHistData側で 2025-10-26 19:00〜19:59 の
重複バー（内容同一）も観測されており、「HistData側の時計が1時間戻った」と整合する。

したがって **単一の固定オフセットで長期データを変換してはならない**。
オフセットは`OFFSET_SCHEDULE`として明示的に与え、期間ごとに検証する。

【未検証事項】
- 春の切替（DST開始側）は本POC期間に含まれないため未検証
- 両者がそれぞれどのDSTカレンダーに従うかは確定していない。観測されたのは
  「この週末に1時間ずれた」という事実のみ
- 10年分へ拡張する場合、各切替の前後で本スクリプトの検証モードを再実行すること
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# (適用開始日時[HistData時刻基準], オフセット時間) を古い順に並べる。
# 実測に基づく値のみを記載する。未検証期間へ無検証で適用しないこと。
OFFSET_SCHEDULE = [
    (datetime(1970, 1, 1), 7),      # POC実測: 2025-10-24まで +7
    (datetime(2025, 10, 25), 8),    # POC実測: 2025-10-27から +8（変化点は10/25-26の週末）
]


def offset_for(ts: datetime, schedule=None) -> int:
    schedule = schedule or OFFSET_SCHEDULE
    off = schedule[0][1]
    for start, val in schedule:
        if ts >= start:
            off = val
    return off


def load_histdata(paths) -> dict:
    """HistData M1 CSVを読み込む。重複timestampは先勝ちで除去し、件数を返す。"""
    bars = {}
    dup = 0
    malformed = 0
    for p in paths:
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(";")
                if len(parts) < 6:
                    malformed += 1
                    continue
                try:
                    ts = datetime.strptime(parts[0], "%Y%m%d %H%M%S")
                    vals = (float(parts[1]), float(parts[2]), float(parts[3]),
                            float(parts[4]), int(parts[5]))
                except ValueError:
                    malformed += 1
                    continue
                if ts in bars:
                    dup += 1
                    continue
                bars[ts] = vals
    return bars, dup, malformed


def convert(bars: dict, schedule=None) -> list[str]:
    out = []
    for ts in sorted(bars):
        o, h, l, c, v = bars[ts]
        shifted = ts + timedelta(hours=offset_for(ts, schedule))
        out.append(f"{shifted:%Y.%m.%d},{shifted:%H:%M},{o:.3f},{h:.3f},{l:.3f},{c:.3f},{v}")
    return out


def main():
    import argparse

    ap = argparse.ArgumentParser(description="HistData ASCII M1 -> MT4取り込み用CSV変換")
    ap.add_argument("inputs", nargs="+", help="DAT_ASCII_USDJPY_M1_YYYYMM.csv")
    ap.add_argument("-o", "--output", required=True, help="出力CSVパス")
    args = ap.parse_args()

    bars, dup, malformed = load_histdata(args.inputs)
    lines = convert(bars)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    ts = sorted(bars)
    print(f"入力ファイル数: {len(args.inputs)}")
    print(f"読み込みバー数: {len(bars)}（重複除去: {dup}件、不正行: {malformed}件）")
    print(f"HistData時刻範囲: {ts[0]} .. {ts[-1]}")
    first = ts[0] + timedelta(hours=offset_for(ts[0]))
    last = ts[-1] + timedelta(hours=offset_for(ts[-1]))
    print(f"変換後(MT4時刻)範囲: {first} .. {last}")
    print(f"適用オフセット: {OFFSET_SCHEDULE}")
    print(f"出力: {args.output}（{len(lines)}行）")


if __name__ == "__main__":
    main()

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


TIMEFRAMES = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60}


def shift_bars(bars: dict, schedule=None) -> dict:
    """HistData時刻のバーを、MT4時刻に変換したdictへ写す。"""
    return {ts + timedelta(hours=offset_for(ts, schedule)): v for ts, v in bars.items()}


def aggregate(shifted: dict, minutes: int) -> dict:
    """MT4時刻のM1バーを、指定分数の上位足へ機械的に再集約する。

    O=バケット内で最も早いM1のOpen, H=最大High, L=最小Low, C=最も遅いM1のClose,
    V=合計。空バケットは生成しない（MT4の実データも無取引時間帯はバーを持たないため）。
    """
    if minutes == 1:
        return dict(shifted)
    out = {}
    for ts in sorted(shifted):
        o, h, l, c, v = shifted[ts]
        key = ts.replace(minute=(ts.minute // minutes) * minutes, second=0, microsecond=0)
        cur = out.get(key)
        if cur is None:
            out[key] = [ts, o, h, l, ts, c, v]
        else:
            if ts < cur[0]:
                cur[0], cur[1] = ts, o
            if h > cur[2]:
                cur[2] = h
            if l < cur[3]:
                cur[3] = l
            if ts > cur[4]:
                cur[4], cur[5] = ts, c
            cur[6] += v
    return {k: (v[1], v[2], v[3], v[5], v[6]) for k, v in out.items()}


def to_lines(bars: dict) -> list[str]:
    return [f"{t:%Y.%m.%d},{t:%H:%M},{o:.3f},{h:.3f},{l:.3f},{c:.3f},{v}"
            for t, (o, h, l, c, v) in sorted(bars.items())]


def main():
    import argparse

    ap = argparse.ArgumentParser(description="HistData ASCII M1 -> MT4取り込み用CSV変換")
    ap.add_argument("inputs", nargs="+", help="DAT_ASCII_USDJPY_M1_YYYYMM.csv")
    ap.add_argument("-d", "--outdir", required=True, help="出力ディレクトリ")
    ap.add_argument("--prefix", default="USDJPY", help="出力ファイル名の接頭辞")
    ap.add_argument("--timeframes", default="M1,M5,M15,M30,H1",
                    help="生成する時間足（カンマ区切り）")
    args = ap.parse_args()

    bars, dup, malformed = load_histdata(args.inputs)
    ts = sorted(bars)
    print(f"入力ファイル数: {len(args.inputs)}")
    print(f"重複除去前: {len(bars) + dup}行 / 除去後: {len(bars)}行"
          f"（完全重複 {dup}件を1件に一意化、不正行 {malformed}件）")
    print(f"HistData時刻範囲: {ts[0]} .. {ts[-1]}")

    shifted = shift_bars(bars)
    st = sorted(shifted)
    print(f"MT4時刻範囲     : {st[0]} .. {st[-1]}")
    print(f"適用オフセット  : {OFFSET_SCHEDULE}\n")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for tf in [t.strip() for t in args.timeframes.split(",") if t.strip()]:
        if tf not in TIMEFRAMES:
            raise SystemExit(f"未知の時間足: {tf}")
        agg = aggregate(shifted, TIMEFRAMES[tf])
        lines = to_lines(agg)
        path = outdir / f"{args.prefix}_{tf}_MT4import.csv"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        k = sorted(agg)
        print(f"{tf:>3}: {len(lines):>6}本  {k[0]} .. {k[-1]}  -> {path.name}")


if __name__ == "__main__":
    main()

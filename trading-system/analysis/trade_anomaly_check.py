"""
EAの禁止事項・安全設計(ナンピン禁止、損切りなし禁止、同時保有1ポジション等)が
バックテスト結果でも実際に守られているかを、トレード履歴から事後検証する。

ここで異常が検出された場合、それは「バックテストの問題」ではなく
「EAのロジックにバグがある」ことを意味するので、最優先で調査すること。
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def check_missing_stop_loss(trades: list[dict]) -> list[dict]:
    """損切り(SL)が0またはNoneのまま新規注文されたトレードを検出する。
    EnableECNFallback経由でSL無し発注→即Modifyというパスがあるため、
    最終的なS/Lが0のままなのは「損切りなし禁止」違反の疑いが強い。"""
    violations = []
    for t in trades:
        sl = t.get("sl")
        if sl is None or sl == 0:
            violations.append({"ticket": t.get("ticket"), "open_time": t.get("open_time"), "sl": sl})
    return violations


def check_overlapping_positions(trades: list[dict]) -> list[dict]:
    """保有期間が重複しているトレードの組を検出する(同時保有1ポジション制限の違反疑い)。"""
    intervals = []
    for t in trades:
        open_t = _parse_dt(t.get("open_time"))
        close_t = _parse_dt(t.get("close_time")) or datetime.max
        if open_t is None:
            continue
        intervals.append((open_t, close_t, t.get("ticket")))

    intervals.sort(key=lambda x: x[0])

    overlaps = []
    for i in range(len(intervals) - 1):
        _, close_i, ticket_i = intervals[i]
        open_next, _, ticket_next = intervals[i + 1]
        if open_next < close_i:
            overlaps.append({"ticket_a": ticket_i, "ticket_b": ticket_next})
    return overlaps


def check_duplicate_entries_same_bar(trades: list[dict]) -> list[dict]:
    """同一時刻(=同一確定足)に複数の新規エントリーがないかを確認する
    (「1本の足につき最大1回判定」の違反疑い)。"""
    seen: dict[str, list[str]] = {}
    for t in trades:
        open_t = t.get("open_time")
        if not open_t:
            continue
        seen.setdefault(open_t, []).append(t.get("ticket"))

    return [{"open_time": k, "tickets": v} for k, v in seen.items() if len(v) > 1]


def check_lot_size_bounds(trades: list[dict], max_lot: float | None = None) -> list[dict]:
    """ロットが0以下、またはMaximumLotを超えていないかを確認する。"""
    violations = []
    for t in trades:
        lots = t.get("lots")
        if lots is None or lots <= 0:
            violations.append({"ticket": t.get("ticket"), "lots": lots, "issue": "invalid_lot"})
        elif max_lot is not None and lots > max_lot:
            violations.append({"ticket": t.get("ticket"), "lots": lots, "issue": "exceeds_max_lot"})
    return violations


def check_weekend_entries(trades: list[dict]) -> list[dict]:
    """土曜・日曜に新規エントリーされた形跡がないかを確認する(通常は市場が閉まっているため
    起こらないはずだが、ブローカーのサーバー時間設定やヒストリーの穴を検出する目的で確認する)。"""
    violations = []
    for t in trades:
        open_t = _parse_dt(t.get("open_time"))
        if open_t is None:
            continue
        if open_t.weekday() >= 5:  # 5=土, 6=日
            violations.append({"ticket": t.get("ticket"), "open_time": t.get("open_time")})
    return violations


def run_all_checks(trades: list[dict], max_lot: float | None = None) -> dict:
    return {
        "missing_stop_loss": check_missing_stop_loss(trades),
        "overlapping_positions": check_overlapping_positions(trades),
        "duplicate_entries_same_bar": check_duplicate_entries_same_bar(trades),
        "lot_size_violations": check_lot_size_bounds(trades, max_lot),
        "weekend_entries": check_weekend_entries(trades),
    }


def summarize(check_results: dict) -> dict:
    total_issues = sum(len(v) for v in check_results.values())
    return {
        "total_issues": total_issues,
        "is_clean": total_issues == 0,
        "issue_counts": {k: len(v) for k, v in check_results.items()},
    }


def main():
    import argparse
    import json

    from common import load_json, save_json

    parser = argparse.ArgumentParser(description="トレード履歴からEA安全設計違反の疑いを検出する")
    parser.add_argument("trades_json", help="parse_mt4_trades.pyが出力したトレードJSON")
    parser.add_argument("--max-lot", type=float, help="MaximumLot入力パラメータの値(任意)")
    parser.add_argument("-o", "--output", help="出力先JSONパス（省略時は標準出力）")
    args = parser.parse_args()

    trades = load_json(args.trades_json)
    results = run_all_checks(trades, max_lot=args.max_lot)
    results["_summary"] = summarize(results)

    if not results["_summary"]["is_clean"]:
        print(f"[WARN] 異常を検出しました: {results['_summary']['issue_counts']}")
    else:
        print("異常は検出されませんでした")

    if args.output:
        save_json(args.output, results)
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

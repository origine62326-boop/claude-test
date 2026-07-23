"""
性能指標にまつわる2つの役割を持つモジュール。

1. validate_report_data(): parse_mt4_report.pyが抽出したレポートデータを検査し、
   欠損値・異常値・整合性の問題を洗い出す（最小構成パイプラインの中心機能）
2. compute_metrics_from_trades(): 正規化済みトレードリスト（parse_mt4_trades.pyの出力）
   から指標を独立に再計算し、レポート値と突き合わせる（トレード明細まで扱う
   フル版パイプライン向け。最小構成パイプラインでは使わない）
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_mt4_report import REQUIRED_FIELDS  # noqa: E402

MIN_TRADES_FOR_CONFIDENCE = 200  # これ未満は統計的信頼性が低いと見なす目安
MIN_MODELLING_QUALITY_PCT = 70.0  # これ未満はバックテスト精度への注意を促す目安


# ====================================================================
# 1. レポートデータの検証（欠損値・異常値チェック）
# ====================================================================

def _check_missing_fields(report: dict) -> list[dict]:
    return [
        {"field": f, "detail": "抽出できませんでした（レポートHTML内に該当ラベルが見つからないか、値が読み取れませんでした）"}
        for f in REQUIRED_FIELDS
        if report.get(f) is None
    ]


def _check_range_violations(report: dict) -> list[dict]:
    errors = []

    def check_range(field, lo, hi):
        v = report.get(field)
        if v is not None and not (lo <= v <= hi):
            errors.append({"field": field, "detail": f"値が想定範囲外です: {v} (期待範囲: {lo}〜{hi})"})

    check_range("win_rate_pct", 0, 100)
    check_range("max_drawdown_pct", 0, 100)
    check_range("modelling_quality_pct", 0, 100)

    if report.get("total_trades") is not None and report["total_trades"] < 0:
        errors.append({"field": "total_trades", "detail": f"負の値です: {report['total_trades']}"})

    if report.get("profit_factor") is not None and report["profit_factor"] < 0:
        errors.append({"field": "profit_factor", "detail": f"負の値です(通常0以上): {report['profit_factor']}"})

    if report.get("initial_deposit") is not None and report["initial_deposit"] <= 0:
        errors.append({"field": "initial_deposit", "detail": f"0以下です: {report['initial_deposit']}"})

    return errors


def _check_consistency(report: dict) -> list[dict]:
    """複数フィールド間の整合性を確認する(純利益=総利益+総損失、等)。"""
    errors = []
    tolerance = 1.0  # 端数処理・パース誤差を許容する絶対誤差(円/pips等の単位に依らずゆるめに設定)

    net, gp, gl = report.get("net_profit"), report.get("gross_profit"), report.get("gross_loss")
    if None not in (net, gp, gl):
        expected = gp + gl
        if abs(expected - net) > tolerance:
            errors.append({
                "field": "net_profit",
                "detail": f"総利益+総損失({expected:.2f})と純利益({net:.2f})が一致しません",
            })

    win_t, loss_t, total_t = report.get("win_trades"), report.get("loss_trades"), report.get("total_trades")
    if None not in (win_t, loss_t, total_t) and (win_t + loss_t) > total_t:
        errors.append({
            "field": "total_trades",
            "detail": f"勝トレード({win_t})+敗トレード({loss_t})が総取引数({total_t})を超えています",
        })

    return errors


def _check_advisory_warnings(report: dict) -> list[dict]:
    """異常ではないが、結果の解釈時に注意すべき点(警告レベル)。"""
    warnings = []

    if report.get("total_trades") is not None and report["total_trades"] < MIN_TRADES_FOR_CONFIDENCE:
        warnings.append({
            "field": "total_trades",
            "detail": f"取引数が{MIN_TRADES_FOR_CONFIDENCE}件未満({report['total_trades']}件)のため、"
                      f"統計的な信頼性が低い可能性があります",
        })

    if report.get("modelling_quality_pct") is not None and report["modelling_quality_pct"] < MIN_MODELLING_QUALITY_PCT:
        warnings.append({
            "field": "modelling_quality_pct",
            "detail": f"モデリング品質が{MIN_MODELLING_QUALITY_PCT}%未満({report['modelling_quality_pct']}%)のため、"
                      f"バックテスト結果の精度に注意してください",
        })

    if report.get("mismatched_chart_errors") is not None and report["mismatched_chart_errors"] > 0:
        warnings.append({
            "field": "mismatched_chart_errors",
            "detail": f"不整合チャートエラーが{report['mismatched_chart_errors']}件検出されています。"
                      f"ヒストリカルデータに欠損がある可能性があります",
        })

    return warnings


def validate_report_data(report: dict) -> dict:
    """parse_mt4_report.pyの出力を検査し、欠損値・異常値・整合性の問題を報告する。"""
    missing = _check_missing_fields(report)
    range_errors = _check_range_violations(report)
    consistency_errors = _check_consistency(report)
    warnings = _check_advisory_warnings(report)

    errors = missing + range_errors + consistency_errors

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "missing_field_count": len(missing),
        "error_count": len(errors),
        "warning_count": len(warnings),
    }


# ====================================================================
# 2. トレード明細からの指標再計算（フル版パイプライン向け）
# ====================================================================


def _closed_trades(trades: list[dict]) -> list[dict]:
    return [t for t in trades if t.get("profit") is not None]


def compute_metrics_from_trades(trades: list[dict]) -> dict:
    closed = _closed_trades(trades)
    n = len(closed)

    if n == 0:
        return {"total_trades": 0, "note": "決済済みトレードがありません"}

    profits = [t["profit"] for t in closed]
    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p < 0]
    breakeven = [p for p in profits if p == 0]

    net_profit = sum(profits)
    gross_profit = sum(wins)
    gross_loss = sum(losses)  # 負の値

    win_count = len(wins)
    loss_count = len(losses)

    average_win = (gross_profit / win_count) if win_count else 0.0
    average_loss = (gross_loss / loss_count) if loss_count else 0.0

    profit_factor = (gross_profit / abs(gross_loss)) if gross_loss != 0 else None
    expected_payoff = net_profit / n
    win_rate_pct = (win_count / n) * 100

    risk_reward_ratio = (average_win / abs(average_loss)) if average_loss != 0 else None

    max_consec_wins, max_consec_losses = _max_consecutive(profits)

    return {
        "total_trades": n,
        "breakeven_trades": len(breakeven),
        "win_trades": win_count,
        "loss_trades": loss_count,
        "win_rate_pct": round(win_rate_pct, 2),
        "net_profit": round(net_profit, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "profit_factor": round(profit_factor, 3) if profit_factor is not None else None,
        "expected_payoff": round(expected_payoff, 3),
        "average_win": round(average_win, 2),
        "average_loss": round(average_loss, 2),
        "risk_reward_ratio": round(risk_reward_ratio, 3) if risk_reward_ratio is not None else None,
        "largest_win": round(max(wins), 2) if wins else None,
        "largest_loss": round(min(losses), 2) if losses else None,
        "max_consecutive_wins": max_consec_wins,
        "max_consecutive_losses": max_consec_losses,
        "sample_size_reliable": n >= MIN_TRADES_FOR_CONFIDENCE,
        "min_trades_for_confidence": MIN_TRADES_FOR_CONFIDENCE,
    }


def _max_consecutive(profits: list[float]) -> tuple[int, int]:
    max_wins = cur_wins = 0
    max_losses = cur_losses = 0
    for p in profits:
        if p > 0:
            cur_wins += 1
            cur_losses = 0
        elif p < 0:
            cur_losses += 1
            cur_wins = 0
        else:
            cur_wins = cur_losses = 0
        max_wins = max(max_wins, cur_wins)
        max_losses = max(max_losses, cur_losses)
    return max_wins, max_losses


# 突き合わせを行う際、四捨五入誤差を許容する相対誤差
CROSS_CHECK_TOLERANCE = 0.01  # 1%


def cross_check_against_report(computed: dict, report: dict) -> list[dict]:
    """トレードから再計算した値と、MT4レポートの値を比較し、乖離が大きい項目を返す。
    パーサーのバグ検出や、レポートの見落とし発見のために使う。"""
    pairs = [
        ("total_trades", "total_trades"),
        ("net_profit", "net_profit"),
        ("gross_profit", "gross_profit"),
        ("gross_loss", "gross_loss"),
        ("profit_factor", "profit_factor"),
        ("expected_payoff", "expected_payoff"),
    ]

    mismatches = []
    for computed_key, report_key in pairs:
        c = computed.get(computed_key)
        r = report.get(report_key)
        if c is None or r is None:
            continue
        if r == 0:
            diff_ok = (c == 0)
        else:
            diff_ok = abs(c - r) / abs(r) <= CROSS_CHECK_TOLERANCE
        if not diff_ok:
            mismatches.append({"field": computed_key, "computed": c, "report": r})

    return mismatches


def main():
    import argparse
    import json

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import load_json, save_json

    parser = argparse.ArgumentParser(description="性能指標の検証・計算を行う")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    validate_parser = subparsers.add_parser("validate", help="レポートJSONの欠損値・異常値を検査する(最小構成パイプライン向け)")
    validate_parser.add_argument("report_json", help="parse_mt4_report.pyが出力したレポートJSON")
    validate_parser.add_argument("-o", "--output", help="出力先JSONパス（省略時は標準出力）")

    trades_parser = subparsers.add_parser("from-trades", help="トレード明細JSONから指標を再計算する(フル版パイプライン向け)")
    trades_parser.add_argument("trades_json", help="parse_mt4_trades.pyが出力したトレードJSON")
    trades_parser.add_argument("--report-json", help="parse_mt4_report.pyが出力したサマリーJSON(突き合わせ用、任意)")
    trades_parser.add_argument("-o", "--output", help="出力先JSONパス（省略時は標準出力）")

    args = parser.parse_args()

    if args.mode == "validate":
        report = load_json(args.report_json)
        result = validate_report_data(report)
        if not result["is_valid"]:
            print(f"[ERROR] 検証NG: {result['error_count']}件のエラー")
        if result["warnings"]:
            print(f"[WARN] {result['warning_count']}件の注意事項")
        output_data = result
    else:
        trades = load_json(args.trades_json)
        metrics = compute_metrics_from_trades(trades)
        if args.report_json:
            report = load_json(args.report_json)
            mismatches = cross_check_against_report(metrics, report)
            metrics["_cross_check_mismatches"] = mismatches
            if mismatches:
                print(f"[WARN] レポートとの乖離を検出: {mismatches}")
        output_data = metrics

    if args.output:
        save_json(args.output, output_data)
        print(f"保存しました: {args.output}")
    else:
        print(json.dumps(output_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

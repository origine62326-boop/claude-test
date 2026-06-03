"""
Report モジュール - 結衣専用
投稿比率・DMM収益・フォロワー推移・Markdownエクスポート
"""

from pathlib import Path

from modules import ui
from . import storage
from .plan import list_cycles, get_cycle_by_id
from .do import get_posts_for_cycle, CATEGORY_LABEL
from .check import get_metrics_for_cycle, get_followers_for_cycle
from .act import get_actions_for_cycle
from .dmm import _load_conversions, _load_products


FOLLOWERS_FILE = "yui_followers.json"


def run():
    ui.header("REPORT - レポート", ui.Color.CYAN)

    while True:
        choice = ui.menu("Reportメニュー", [
            ("1", "サイクルサマリー"),
            ("2", "フォロワー推移グラフ"),
            ("3", "投稿比率レポート"),
            ("4", "DMM収益レポート"),
            ("5", "全サイクル比較"),
            ("6", "Markdownレポートを出力"),
            ("0", "メインメニューに戻る"),
        ])

        if choice == "1":
            _cycle_summary()
        elif choice == "2":
            _follower_trend()
        elif choice == "3":
            _ratio_report()
        elif choice == "4":
            _dmm_report()
        elif choice == "5":
            _compare_cycles()
        elif choice == "6":
            _export_markdown()
        elif choice == "0":
            break


def _select_cycle() -> dict | None:
    cycles = list_cycles()
    if not cycles:
        ui.info("サイクルがありません")
        return None
    for c in cycles:
        print(f"  {ui.Color.CYAN}{c['id']}{ui.Color.RESET} - {c['name']} ({c['start_date']}~{c['end_date']})")
    cid = ui.prompt("サイクルID")
    cycle = get_cycle_by_id(cid)
    if not cycle:
        ui.error("IDが見つかりません")
    return cycle


def _cycle_summary():
    ui.section("サイクルサマリー")
    cycle = _select_cycle()
    if not cycle:
        return
    _print_summary(cycle)


def _print_summary(cycle: dict):
    posts     = get_posts_for_cycle(cycle["id"])
    metrics   = get_metrics_for_cycle(cycle["id"])
    followers = get_followers_for_cycle(cycle["id"])
    actions   = get_actions_for_cycle(cycle["id"])
    goals     = cycle["goals"]

    print(f"\n{ui.Color.BOLD}{'=' * 54}{ui.Color.RESET}")
    print(f"{ui.Color.BOLD}  朝5時の結衣 - PDCAサマリー{ui.Color.RESET}")
    print(f"{ui.Color.BOLD}{'=' * 54}{ui.Color.RESET}")
    print(f"  サイクル  : {cycle['name']}")
    print(f"  期間      : {cycle['start_date']} ~ {cycle['end_date']}")
    print(f"  フェーズ  : {cycle.get('phase', '-')}")

    ui.section("KPI達成状況")
    _bar("投稿数",         len(posts),  goals.get("posts", 1), "件")
    total_imp = sum(m["impressions"] for m in metrics)
    _bar("インプレッション", total_imp,  goals.get("impressions", 1), "")
    if followers:
        _bar("フォロワー数",  followers[-1]["count"], goals.get("followers_total", 1), "人")
    avg_eng = round(sum(m["engagement_rate"] for m in metrics) / len(metrics), 2) if metrics else 0.0
    _bar("平均エンゲジ率",   avg_eng,    goals.get("engagement_rate", 1), "%")

    # 比率
    if posts:
        ui.section("投稿比率")
        total = len(posts)
        for cat, label in [("daily", "日常"), ("love", "恋愛"), ("dmm", "DMM ")]:
            cnt = sum(1 for p in posts if p.get("category") == cat)
            pct = round(cnt / total * 100)
            tgt = goals.get(f"ratio_{cat}", 0)
            diff = pct - tgt
            sign = f"+{diff}" if diff > 0 else str(diff)
            ok = ui.Color.GREEN if abs(diff) <= 5 else ui.Color.YELLOW
            print(f"  {label}  {cnt:3d}件 / {pct:3d}%  (目標{tgt}%  {ok}{sign}%{ui.Color.RESET})")

    # Top3
    if metrics:
        ui.section("Top3投稿 (インプレッション)")
        for i, m in enumerate(sorted(metrics, key=lambda x: x["impressions"], reverse=True)[:3], 1):
            print(f"  {i}. {m['post_content'][:40]}")
            print(f"     imp:{m['impressions']:,}  ❤:{m['likes']}  RT:{m['retweets']}  eng:{m['engagement_rate']}%")

    # 振り返り
    if actions:
        good    = [a for a in actions if a["category"] == "good"]
        problem = [a for a in actions if a["category"] == "problem"]
        tries   = [a for a in actions if a["category"] == "try"]
        ui.section("振り返り")
        if good:
            print(f"  {ui.Color.GREEN}良かった点:{ui.Color.RESET}")
            for a in good:
                print(f"    ✓ {a['description']}")
        if problem:
            print(f"  {ui.Color.RED}課題:{ui.Color.RESET}")
            for a in problem:
                print(f"    ✗ {a['description']}")
        if tries:
            print(f"  {ui.Color.CYAN}次に試すこと:{ui.Color.RESET}")
            for a in tries:
                print(f"    → {a['description']}")


def _follower_trend():
    all_fw = storage.load_list(FOLLOWERS_FILE)
    if not all_fw:
        ui.info("フォロワーデータがありません")
        return

    ui.section("フォロワー推移")
    sorted_fw = sorted(all_fw, key=lambda f: f["date"])
    counts = [f["count"] for f in sorted_fw]
    min_c, max_c = min(counts), max(counts)
    rng = max_c - min_c if max_c != min_c else 1
    height = 8

    print()
    for row in range(height, -1, -1):
        threshold = min_c + (rng * row / height)
        line = ""
        for c in counts:
            line += "█ " if c >= threshold else "  "
        label = f"{int(threshold):,}" if row % 2 == 0 else ""
        print(f"  {label:>8} | {line}")

    print(f"  {'':>8} +-" + "--" * len(counts))
    dates = [f["date"][5:] for f in sorted_fw]
    step = max(1, len(dates) // 8)
    date_line = "".join((d + " ") if i % step == 0 else "  " for i, d in enumerate(dates))
    print(f"           {date_line}")

    if len(counts) >= 2:
        total_gain = counts[-1] - counts[0]
        goal_300   = 300
        goal_1000  = 1000
        print(f"\n  最初: {counts[0]:,}人  →  最新: {counts[-1]:,}人  ({total_gain:+d}人)")
        pct_300  = round(counts[-1] / goal_300 * 100)
        pct_1000 = round(counts[-1] / goal_1000 * 100)
        print(f"  30日目標300人: {pct_300}%  /  90日目標1000人: {pct_1000}%")


def _ratio_report():
    ui.section("投稿比率レポート")
    cycle = _select_cycle()
    if not cycle:
        return

    posts = get_posts_for_cycle(cycle["id"])
    if not posts:
        ui.info("投稿記録がありません")
        return

    total  = len(posts)
    goals  = cycle["goals"]
    metrics = get_metrics_for_cycle(cycle["id"])
    post_map = {p["id"]: p for p in posts}

    ui.section(f"比率分析 ({cycle['name']}) / 総投稿 {total} 件")

    cat_data: dict[str, dict] = {}
    for cat in ["daily", "love", "dmm"]:
        cat_posts   = [p for p in posts if p.get("category") == cat]
        cat_metrics = [m for m in metrics if post_map.get(m["post_id"], {}).get("category") == cat]
        avg_imp = round(sum(m["impressions"] for m in cat_metrics) / len(cat_metrics)) if cat_metrics else 0
        avg_eng = round(sum(m["engagement_rate"] for m in cat_metrics) / len(cat_metrics), 2) if cat_metrics else 0.0
        cat_data[cat] = {
            "count": len(cat_posts),
            "pct":   round(len(cat_posts) / total * 100),
            "target": goals.get(f"ratio_{cat}", 0),
            "avg_imp": avg_imp,
            "avg_eng": avg_eng,
        }

    label_map = {"daily": "日常", "love": "恋愛", "dmm": "DMM "}
    color_map  = {"daily": ui.Color.CYAN, "love": ui.Color.RED, "dmm": ui.Color.YELLOW}

    print()
    for cat in ["daily", "love", "dmm"]:
        d = cat_data[cat]
        diff = d["pct"] - d["target"]
        sign = f"+{diff}" if diff > 0 else str(diff)
        ok = ui.Color.GREEN if abs(diff) <= 5 else ui.Color.YELLOW if abs(diff) <= 15 else ui.Color.RED
        c = color_map[cat]
        print(f"  {c}{label_map[cat]}{ui.Color.RESET}  {d['count']:3d}件 / {d['pct']:3d}%  (目標{d['target']}%  {ok}{sign}%{ui.Color.RESET})")
        if d["avg_imp"]:
            print(f"         平均imp:{d['avg_imp']:,}  平均eng:{d['avg_eng']}%")


def _dmm_report():
    ui.section("DMM収益レポート")

    convs    = _load_conversions()
    products = _load_products()

    if not convs:
        ui.info("DMM成約記録がありません")
        return

    total_conv    = sum(c["count"] for c in convs)
    total_revenue = sum(c["revenue"] for c in convs)
    total_clicks  = sum(c.get("clicks", 0) for c in convs)

    print(f"\n  {ui.Color.BOLD}総成約数  : {total_conv} 件{ui.Color.RESET}")
    print(f"  {ui.Color.BOLD}総収益    : {total_revenue:,} 円{ui.Color.RESET}")
    if total_clicks:
        ctr = round(total_conv / total_clicks * 100, 2)
        print(f"  総クリック: {total_clicks:,} 回  成約率: {ctr}%")

    # 月別
    monthly: dict[str, dict] = {}
    for c in convs:
        m = c["date"][:7]
        if m not in monthly:
            monthly[m] = {"conv": 0, "revenue": 0}
        monthly[m]["conv"]    += c["count"]
        monthly[m]["revenue"] += c["revenue"]

    if monthly:
        ui.section("月別収益")
        for month in sorted(monthly.keys()):
            d = monthly[month]
            bar = "█" * min(d["conv"], 15)
            print(f"  {month}  {bar:<15}  {d['conv']}件  {d['revenue']:,}円")

    # 案件別
    if products:
        ui.section("案件別成約")
        for p in products:
            p_convs = [c for c in convs if c["product_id"] == p["id"]]
            if p_convs:
                cnt = sum(c["count"] for c in p_convs)
                rev = sum(c["revenue"] for c in p_convs)
                print(f"  {p['name'][:28]}  {cnt}件  {rev:,}円")


def _compare_cycles():
    cycles = list_cycles()
    if not cycles:
        ui.info("サイクルがありません")
        return

    ui.section("全サイクル比較")
    rows = []
    for c in cycles:
        posts   = get_posts_for_cycle(c["id"])
        metrics = get_metrics_for_cycle(c["id"])
        fw      = get_followers_for_cycle(c["id"])
        total_imp = sum(m["impressions"] for m in metrics)
        avg_eng   = round(sum(m["engagement_rate"] for m in metrics) / len(metrics), 1) if metrics else 0.0
        fw_latest = fw[-1]["count"] if fw else "-"
        rows.append([c["id"], c["name"][:18], len(posts), f"{total_imp:,}", f"{avg_eng}%", fw_latest, c["status"]])

    ui.table(
        ["ID", "サイクル名", "投稿", "imp合計", "eng%", "FW数", "状態"],
        rows,
        [10, 20, 6, 10, 7, 7, 8],
    )


def _export_markdown():
    ui.section("Markdownレポートを出力")
    cycle = _select_cycle()
    if not cycle:
        return

    posts     = get_posts_for_cycle(cycle["id"])
    metrics   = get_metrics_for_cycle(cycle["id"])
    followers = get_followers_for_cycle(cycle["id"])
    actions   = get_actions_for_cycle(cycle["id"])
    convs     = _load_conversions()
    goals     = cycle["goals"]

    total_imp  = sum(m["impressions"] for m in metrics)
    avg_eng    = round(sum(m["engagement_rate"] for m in metrics) / len(metrics), 2) if metrics else 0.0
    fw_latest  = followers[-1]["count"] if followers else "N/A"
    total_conv = sum(c["count"] for c in convs)
    total_rev  = sum(c["revenue"] for c in convs)

    def pct(a, g):
        try:
            return f"{round(float(str(a).replace(',','')) / float(str(g).replace(',','')) * 100)}%"
        except Exception:
            return "N/A"

    lines = [
        f"# 朝5時の結衣 - PDCAレポート: {cycle['name']}",
        "",
        f"> 期間: {cycle['start_date']} ~ {cycle['end_date']}  ",
        f"> フェーズ: {cycle.get('phase', '-')}  ",
        f"> 作成日: {ui.today_str()}",
        "",
        "## Plan - 目標",
        "",
        "| KPI | 目標値 |",
        "|-----|--------|",
        f"| 投稿数 | {goals.get('posts', '-')} 件 |",
        f"| フォロワー数 | {goals.get('followers_total', '-')} 人 |",
        f"| インプレッション合計 | {goals.get('impressions', 0):,} |",
        f"| エンゲージメント率 | {goals.get('engagement_rate', '-')} % |",
        f"| DMM CTR | {goals.get('dmm_ctr', '-')} % |",
        f"| 投稿比率 | 日常{goals.get('ratio_daily',70)}% / 恋愛{goals.get('ratio_love',20)}% / DMM{goals.get('ratio_dmm',10)}% |",
        "",
        "## Do & Check - 実績",
        "",
        "| KPI | 実績値 | 目標値 | 達成率 |",
        "|-----|--------|--------|--------|",
        f"| 投稿数 | {len(posts)} 件 | {goals.get('posts','-')} 件 | {pct(len(posts), goals.get('posts',1))} |",
        f"| インプレッション合計 | {total_imp:,} | {goals.get('impressions',0):,} | {pct(total_imp, goals.get('impressions',1))} |",
        f"| 平均エンゲージメント率 | {avg_eng}% | {goals.get('engagement_rate','-')}% | {pct(avg_eng, goals.get('engagement_rate',1))} |",
        f"| フォロワー数 | {fw_latest} 人 | {goals.get('followers_total','-')} 人 | {pct(fw_latest, goals.get('followers_total',1)) if fw_latest != 'N/A' else 'N/A'} |",
        "",
    ]

    # 投稿比率
    if posts:
        total = len(posts)
        lines += ["### 投稿比率", "", "| カテゴリ | 件数 | 比率 | 目標 |", "|---------|------|------|------|"]
        for cat, label in [("daily","日常"), ("love","恋愛"), ("dmm","DMM")]:
            cnt = sum(1 for p in posts if p.get("category") == cat)
            p_pct = round(cnt / total * 100)
            tgt   = goals.get(f"ratio_{cat}", 0)
            lines.append(f"| {label} | {cnt} 件 | {p_pct}% | {tgt}% |")
        lines.append("")

    # Top3投稿
    if metrics:
        top3 = sorted(metrics, key=lambda m: m["impressions"], reverse=True)[:3]
        lines += ["### パフォーマンス上位投稿", "", "| 内容 | imp | ❤ | RT | eng% |", "|-----|-----|---|-----|------|"]
        for m in top3:
            lines.append(f"| {m.get('post_content','')[:38]} | {m['impressions']:,} | {m['likes']} | {m['retweets']} | {m['engagement_rate']}% |")
        lines.append("")

    # DMM
    if total_conv:
        lines += [
            "## DMM収益",
            "",
            f"- 総成約数: {total_conv} 件",
            f"- 総収益: {total_rev:,} 円",
            "",
        ]

    # 振り返り
    lines += ["## Act - 振り返り", ""]
    cat_map = {"good": "### Keep (良かった点)", "problem": "### Problem (課題)", "try": "### Try (次に試すこと)", "worldbreak": "### 世界観崩れ対策"}
    for cat_key, cat_title in cat_map.items():
        cat_actions = [a for a in actions if a["category"] == cat_key]
        if cat_actions:
            lines.append(cat_title)
            for a in cat_actions:
                lines.append(f"- {a['description']}")
            lines.append("")

    lines += ["---", f"*Generated by 朝5時の結衣 PDCAツール on {ui.today_str()}*"]

    filename = f"yui_report_{cycle['id']}_{ui.today_str()}.md"
    filepath = Path(__file__).parent.parent / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    ui.success(f"レポートを保存しました: {filename}")


def _bar(label: str, actual, goal, unit: str):
    try:
        pct = round(float(actual) / float(goal) * 100) if goal else 0
    except Exception:
        pct = 0
    bar_len = min(pct // 5, 20)
    bar     = "█" * bar_len + "░" * (20 - bar_len)
    color   = ui.Color.GREEN if pct >= 100 else (ui.Color.YELLOW if pct >= 60 else ui.Color.RED)
    print(f"  {ui.Color.BOLD}{label:14}{ui.Color.RESET} {actual}{unit} / {goal}{unit}  ({pct}%)")
    print(f"  {' ' * 14} {color}{bar}{ui.Color.RESET}")

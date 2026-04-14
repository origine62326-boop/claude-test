"""
Report モジュール
PDCAサイクル全体のレポートを生成する
- サイクル横断の推移レポート
- Markdownファイルへのエクスポート
- フォロワー推移グラフ（テキストグラフ）
"""

from datetime import datetime
from pathlib import Path

from . import storage, ui
from .plan import list_cycles, get_cycle_by_id
from .do import get_posts_for_cycle
from .check import get_metrics_for_cycle
from .act import get_actions_for_cycle


FOLLOWERS_FILE = "followers.json"


def run():
    ui.header("REPORT - レポート", ui.Color.CYAN)

    while True:
        choice = ui.menu("Report メニュー", [
            ("1", "サイクルサマリーを表示"),
            ("2", "フォロワー推移を表示"),
            ("3", "全サイクル比較"),
            ("4", "MarkdownレポートをExport"),
            ("0", "メインメニューに戻る"),
        ])

        if choice == "1":
            _cycle_summary()
        elif choice == "2":
            _follower_trend()
        elif choice == "3":
            _compare_cycles()
        elif choice == "4":
            _export_markdown()
        elif choice == "0":
            break


def _cycle_summary():
    cycles = list_cycles()
    if not cycles:
        ui.info("サイクルがありません")
        return

    ui.section("サイクル選択")
    for c in cycles:
        print(f"  {ui.Color.CYAN}{c['id']}{ui.Color.RESET} - {c['name']} ({c['start_date']}~{c['end_date']})")

    cycle_id = ui.prompt("サイクルID")
    cycle = get_cycle_by_id(cycle_id)
    if not cycle:
        ui.error("IDが見つかりません")
        return

    _print_full_summary(cycle)


def _print_full_summary(cycle: dict):
    posts   = get_posts_for_cycle(cycle["id"])
    metrics = get_metrics_for_cycle(cycle["id"])
    actions = get_actions_for_cycle(cycle["id"])
    followers = [f for f in storage.load_list(FOLLOWERS_FILE) if f.get("cycle_id") == cycle["id"]]
    goals   = cycle["goals"]

    print(f"\n{ui.Color.BOLD}{'=' * 54}{ui.Color.RESET}")
    print(f"{ui.Color.BOLD}  PDCA サイクル サマリー{ui.Color.RESET}")
    print(f"{ui.Color.BOLD}{'=' * 54}{ui.Color.RESET}")
    print(f"  サイクル  : {cycle['name']}")
    print(f"  期間      : {cycle['start_date']} ~ {cycle['end_date']}")
    print(f"  ステータス: {cycle['status']}")

    # KPI達成状況
    ui.section("KPI達成状況")
    post_pct = round(len(posts) / goals.get("posts", 1) * 100)
    _bar_line("投稿数", len(posts), goals.get("posts", 0), "件", post_pct)

    total_imp = sum(m["impressions"] for m in metrics)
    imp_pct = round(total_imp / goals.get("impressions", 1) * 100) if goals.get("impressions") else 0
    _bar_line("インプレッション", f"{total_imp:,}", f"{goals.get('impressions', 0):,}", "", imp_pct)

    avg_eng = round(sum(m["engagement_rate"] for m in metrics) / len(metrics), 2) if metrics else 0.0
    eng_goal = goals.get("engagement_rate", 0)
    eng_pct = round(avg_eng / eng_goal * 100) if eng_goal else 0
    _bar_line("平均エンゲージ率", avg_eng, eng_goal, "%", eng_pct)

    if followers:
        gain = followers[-1]["count"] - followers[0]["count"]
        fw_goal = goals.get("followers_gain", 0)
        fw_pct = round(gain / fw_goal * 100) if fw_goal else 0
        _bar_line("フォロワー増加", f"{gain:+d}", fw_goal, "人", fw_pct)

    # 投稿集計
    if posts:
        ui.section("投稿集計")
        print(f"  総投稿数  : {len(posts)} 件")
        type_counts: dict[str, int] = {}
        for p in posts:
            type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1
        for t, cnt in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"    {t:8}: {cnt} 件")

    # Top投稿
    if metrics:
        ui.section("パフォーマンス上位投稿")
        top = sorted(metrics, key=lambda m: m["impressions"], reverse=True)[:3]
        for i, m in enumerate(top, 1):
            print(f"  {i}. {m.get('post_content', '')[:40]}")
            print(f"     imp:{m['impressions']:,}  ❤:{m['likes']}  RT:{m['retweets']}  eng:{m['engagement_rate']}%")

    # 改善アクション
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
            print(f"  {ui.Color.CYAN}次回試すこと:{ui.Color.RESET}")
            for a in tries:
                print(f"    → {a['description']}")


def _follower_trend():
    all_followers = storage.load_list(FOLLOWERS_FILE)
    if not all_followers:
        ui.info("フォロワーデータがありません")
        return

    ui.section("フォロワー推移")

    # 日付でソート
    sorted_fw = sorted(all_followers, key=lambda f: f["date"])
    counts = [f["count"] for f in sorted_fw]
    min_c, max_c = min(counts), max(counts)
    range_c = max_c - min_c if max_c != min_c else 1

    height = 8
    print()
    for row in range(height, -1, -1):
        threshold = min_c + (range_c * row / height)
        line = ""
        for c in counts:
            line += "█ " if c >= threshold else "  "
        label = f"{int(threshold):,}" if row % 2 == 0 else ""
        print(f"  {label:>8} | {line}")

    print(f"  {'':>8} +-" + "--" * len(counts))
    dates = [f["date"][5:] for f in sorted_fw]  # MM-DD
    step = max(1, len(dates) // 8)
    date_line = ""
    for i, d in enumerate(dates):
        date_line += (d + " ") if i % step == 0 else "  "
    print(f"           {date_line}")

    if len(counts) >= 2:
        total_gain = counts[-1] - counts[0]
        print(f"\n  最初: {counts[0]:,}人  →  最新: {counts[-1]:,}人  ({total_gain:+d}人)")


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
        total_imp = sum(m["impressions"] for m in metrics)
        avg_eng = round(sum(m["engagement_rate"] for m in metrics) / len(metrics), 1) if metrics else 0.0
        rows.append([
            c["id"],
            c["name"][:18],
            len(posts),
            f"{total_imp:,}",
            f"{avg_eng}%",
            c["status"],
        ])

    ui.table(
        ["ID", "サイクル名", "投稿", "imp合計", "eng%", "状態"],
        rows,
        [10, 20, 6, 10, 7, 8],
    )


def _export_markdown():
    cycles = list_cycles()
    if not cycles:
        ui.info("サイクルがありません")
        return

    for c in cycles:
        print(f"  {ui.Color.CYAN}{c['id']}{ui.Color.RESET} - {c['name']}")

    cycle_id = ui.prompt("ExportするサイクルID")
    cycle = get_cycle_by_id(cycle_id)
    if not cycle:
        ui.error("IDが見つかりません")
        return

    posts   = get_posts_for_cycle(cycle["id"])
    metrics = get_metrics_for_cycle(cycle["id"])
    actions = get_actions_for_cycle(cycle["id"])
    followers = [f for f in storage.load_list(FOLLOWERS_FILE) if f.get("cycle_id") == cycle["id"]]
    goals   = cycle["goals"]

    total_imp = sum(m["impressions"] for m in metrics)
    avg_eng = round(sum(m["engagement_rate"] for m in metrics) / len(metrics), 2) if metrics else 0.0
    fw_gain = (followers[-1]["count"] - followers[0]["count"]) if len(followers) >= 2 else "N/A"
    cp = cycle["content_plan"]

    lines = [
        f"# X運用PDCAレポート: {cycle['name']}",
        "",
        f"> 期間: {cycle['start_date']} ~ {cycle['end_date']}  ",
        f"> 作成日: {ui.today_str()}",
        "",
        "## 目標 (Plan)",
        "",
        "| KPI | 目標値 |",
        "|-----|--------|",
        f"| 投稿数 | {goals.get('posts', '-')} 件 |",
        f"| フォロワー増加 | {goals.get('followers_gain', '-')} 人 |",
        f"| インプレッション合計 | {goals.get('impressions', 0):,} |",
        f"| エンゲージメント率 | {goals.get('engagement_rate', '-')} % |",
        "",
    ]

    if cp.get("themes"):
        lines += [f"**コンテンツテーマ**: {', '.join(cp['themes'])}", ""]
    if cp.get("hashtags"):
        lines += [f"**ハッシュタグ**: {', '.join(cp['hashtags'])}", ""]

    lines += [
        "## 実績 (Do & Check)",
        "",
        "| KPI | 実績値 | 目標値 | 達成率 |",
        "|-----|--------|--------|--------|",
    ]

    def pct(a, g):
        try:
            return f"{round(float(str(a).replace(',','')) / float(str(g).replace(',','')) * 100)}%"
        except Exception:
            return "N/A"

    lines += [
        f"| 投稿数 | {len(posts)} 件 | {goals.get('posts', '-')} 件 | {pct(len(posts), goals.get('posts',1))} |",
        f"| インプレッション合計 | {total_imp:,} | {goals.get('impressions', 0):,} | {pct(total_imp, goals.get('impressions',1))} |",
        f"| 平均エンゲージメント率 | {avg_eng}% | {goals.get('engagement_rate', '-')}% | {pct(avg_eng, goals.get('engagement_rate',1))} |",
        f"| フォロワー増加 | {fw_gain if isinstance(fw_gain, str) else f'{fw_gain:+d}'} 人 | {goals.get('followers_gain', '-')} 人 | {pct(fw_gain, goals.get('followers_gain',1)) if fw_gain != 'N/A' else 'N/A'} |",
        "",
    ]

    if posts:
        lines += ["### 投稿一覧", "", "| 日付 | タイプ | 内容 |", "|------|--------|------|"]
        for p in posts:
            lines.append(f"| {p['date'][:10]} | {p['type']} | {p['content'][:40]} |")
        lines.append("")

    if metrics:
        top3 = sorted(metrics, key=lambda m: m["impressions"], reverse=True)[:3]
        lines += [
            "### パフォーマンス上位投稿",
            "",
            "| 投稿内容 | imp | ❤ | RT | 返信 | eng% |",
            "|---------|-----|---|-----|------|------|",
        ]
        for m in top3:
            lines.append(f"| {m.get('post_content','')[:35]} | {m['impressions']:,} | {m['likes']} | {m['retweets']} | {m['replies']} | {m['engagement_rate']}% |")
        lines.append("")

    # 振り返り
    lines += ["## 振り返り (Act)", ""]
    cat_map = {"good": "### 良かった点 (Keep)", "problem": "### 課題 (Problem)", "try": "### 次に試すこと (Try)", "idea": "### アイデア"}
    for cat_key, cat_title in cat_map.items():
        cat_actions = [a for a in actions if a["category"] == cat_key]
        if cat_actions:
            lines.append(cat_title)
            for a in cat_actions:
                next_act = f" → {a['next_action']}" if a.get("next_action") else ""
                lines.append(f"- {a['description']}{next_act}")
            lines.append("")

    lines += ["---", f"*Generated by X PDCA Tool on {ui.today_str()}*"]

    # ファイル書き込み
    filename = f"pdca_report_{cycle['id']}_{ui.today_str()}.md"
    filepath = Path(__file__).parent.parent / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    ui.success(f"レポートを保存しました: {filename}")


def _bar_line(label: str, actual, goal, unit: str, pct: int):
    bar_len = min(pct // 5, 20)
    bar     = "█" * bar_len + "░" * (20 - bar_len)
    color   = ui.Color.GREEN if pct >= 100 else (ui.Color.YELLOW if pct >= 60 else ui.Color.RED)
    print(f"  {ui.Color.BOLD}{label:14}{ui.Color.RESET} {actual}{unit} / {goal}{unit}  ({pct}%)")
    print(f"  {' ' * 14} {color}{bar}{ui.Color.RESET}")

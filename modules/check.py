"""
Check (確認) モジュール
PDCAサイクルの確認フェーズを管理する
- 投稿ごとの指標入力（インプレッション、いいね、RT、返信）
- フォロワー数の記録
- 目標対比の確認・分析
- エンゲージメント率の計算
"""

import uuid

from . import storage, ui
from .plan import get_active_cycle, list_cycles, get_cycle_by_id
from .do import get_posts_for_cycle, CONTENT_CATEGORIES, HOOK_TYPES, CATEGORY_LABEL, HOOK_LABEL


METRICS_FILE  = "metrics.json"
FOLLOWERS_FILE = "followers.json"


def _load_metrics() -> list:
    return storage.load_list(METRICS_FILE)


def _save_metrics(metrics: list):
    storage.save_list(METRICS_FILE, metrics)


def _load_followers() -> list:
    return storage.load_list(FOLLOWERS_FILE)


def _save_followers(followers: list):
    storage.save_list(FOLLOWERS_FILE, followers)


def get_metrics_for_cycle(cycle_id: str) -> list:
    return [m for m in _load_metrics() if m.get("cycle_id") == cycle_id]


def run():
    ui.header("CHECK - 確認", ui.Color.YELLOW)

    while True:
        choice = ui.menu("Check メニュー", [
            ("1", "投稿の指標を入力"),
            ("2", "フォロワー数を記録"),
            ("3", "サイクルの達成状況を確認"),
            ("4", "指標一覧を表示"),
            ("0", "メインメニューに戻る"),
        ])

        if choice == "1":
            _input_post_metrics()
        elif choice == "2":
            _record_followers()
        elif choice == "3":
            _show_achievement()
        elif choice == "4":
            _show_metrics()
        elif choice == "0":
            break


def _select_cycle() -> dict | None:
    active = get_active_cycle()
    if active:
        use = ui.prompt(f"アクティブサイクル '{active['name']}' を使用しますか？ (y/n)", "y")
        if use.lower() == "y":
            return active

    cycles = list_cycles()
    if not cycles:
        ui.error("サイクルがありません")
        return None

    for c in cycles:
        print(f"  {ui.Color.CYAN}{c['id']}{ui.Color.RESET} - {c['name']}")
    cycle_id = ui.prompt("サイクルID")
    return get_cycle_by_id(cycle_id)


def _input_post_metrics():
    ui.section("投稿指標を入力")

    cycle = _select_cycle()
    if not cycle:
        return

    posts = get_posts_for_cycle(cycle["id"])
    if not posts:
        ui.error("このサイクルに投稿記録がありません。先にDoで投稿を記録してください。")
        return

    # 既存の指標がある投稿IDセット
    existing = {m["post_id"] for m in _load_metrics() if m.get("cycle_id") == cycle["id"]}

    ui.section(f"投稿一覧 ({cycle['name']})")
    for p in posts:
        status = f"{ui.Color.DIM}[記録済]{ui.Color.RESET}" if p["id"] in existing else ""
        print(f"  {ui.Color.CYAN}{p['id']}{ui.Color.RESET} {p['date'][:10]} {status}")
        print(f"    {p['content'][:40]}")

    post_id = ui.prompt("\n指標を入力する投稿ID")
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        ui.error("IDが見つかりません")
        return

    print(f"\n  対象投稿: {post['content'][:50]}")
    ui.section("指標を入力 (Enterでスキップ)")

    impressions = ui.prompt_int("インプレッション数", 0)
    likes       = ui.prompt_int("いいね数", 0)
    retweets    = ui.prompt_int("リポスト(RT)数", 0)
    replies     = ui.prompt_int("返信数", 0)
    bookmarks   = ui.prompt_int("ブックマーク数", 0)
    link_clicks = ui.prompt_int("リンククリック数 (任意)", 0)
    profile_visits = ui.prompt_int("プロフィールアクセス数 (任意)", 0)

    # エンゲージメント率計算 (いいね+RT+返信) / インプレッション * 100
    eng_actions = (likes or 0) + (retweets or 0) + (replies or 0)
    eng_rate = round(eng_actions / impressions * 100, 2) if impressions else 0.0

    metric = {
        "id": str(uuid.uuid4())[:8],
        "cycle_id": cycle["id"],
        "post_id": post_id,
        "post_content": post["content"][:50],
        "recorded_at": ui.now_str(),
        "impressions":     impressions or 0,
        "likes":           likes or 0,
        "retweets":        retweets or 0,
        "replies":         replies or 0,
        "bookmarks":       bookmarks or 0,
        "link_clicks":     link_clicks or 0,
        "profile_visits":  profile_visits or 0,
        "engagement_rate": eng_rate,
    }

    metrics = _load_metrics()
    # 同じ投稿の既存記録を更新
    updated = False
    for i, m in enumerate(metrics):
        if m.get("post_id") == post_id and m.get("cycle_id") == cycle["id"]:
            metrics[i] = metric
            updated = True
            break
    if not updated:
        metrics.append(metric)

    _save_metrics(metrics)
    ui.success(f"指標を記録しました (エンゲージメント率: {eng_rate}%)")


def _record_followers():
    ui.section("フォロワー数を記録")

    cycle = _select_cycle()
    if not cycle:
        return

    current_count = ui.prompt_int("現在のフォロワー数")
    if current_count is None:
        ui.error("フォロワー数を入力してください")
        return

    memo = ui.prompt("メモ (任意)")

    record = {
        "id": str(uuid.uuid4())[:8],
        "cycle_id": cycle["id"],
        "date": ui.today_str(),
        "count": current_count,
        "memo": memo,
        "recorded_at": ui.now_str(),
    }

    followers = _load_followers()
    followers.append(record)
    _save_followers(followers)

    # フォロワー増加数の計算
    cycle_records = [f for f in followers if f.get("cycle_id") == cycle["id"]]
    if len(cycle_records) >= 2:
        first = cycle_records[0]["count"]
        gain = current_count - first
        goal = cycle["goals"].get("followers_gain", 0)
        pct = round(gain / goal * 100) if goal else 0
        ui.success(f"フォロワー数を記録しました")
        ui.info(f"増加数: {gain:+d} 人 / 目標 {goal} 人 ({pct}%達成)")
    else:
        ui.success(f"フォロワー数を記録しました ({current_count:,} 人)")


def _show_achievement():
    ui.section("達成状況確認")

    cycle = _select_cycle()
    if not cycle:
        return

    goals     = cycle["goals"]
    posts     = get_posts_for_cycle(cycle["id"])
    metrics   = get_metrics_for_cycle(cycle["id"])
    followers = [f for f in _load_followers() if f.get("cycle_id") == cycle["id"]]

    ui.section(f"サイクル: {cycle['name']} ({cycle['start_date']} ~ {cycle['end_date']})")

    # --- 投稿数 ---
    post_count  = len(posts)
    post_goal   = goals.get("posts", 0)
    post_pct    = round(post_count / post_goal * 100) if post_goal else 0
    _print_kpi("投稿数", post_count, post_goal, "件", post_pct)

    # --- インプレッション合計 ---
    total_imp   = sum(m["impressions"] for m in metrics)
    imp_goal    = goals.get("impressions", 0)
    imp_pct     = round(total_imp / imp_goal * 100) if imp_goal else 0
    _print_kpi("インプレッション合計", f"{total_imp:,}", f"{imp_goal:,}", "", imp_pct)

    # --- エンゲージメント率（平均）---
    avg_eng = round(sum(m["engagement_rate"] for m in metrics) / len(metrics), 2) if metrics else 0.0
    eng_goal = goals.get("engagement_rate", 0)
    eng_pct  = round(avg_eng / eng_goal * 100) if eng_goal else 0
    _print_kpi("平均エンゲージメント率", avg_eng, eng_goal, "%", eng_pct)

    # --- フォロワー増加 ---
    if followers:
        first_count = followers[0]["count"]
        last_count  = followers[-1]["count"]
        gain        = last_count - first_count
        fw_goal     = goals.get("followers_gain", 0)
        fw_pct      = round(gain / fw_goal * 100) if fw_goal else 0
        _print_kpi("フォロワー増加", f"{gain:+d}", fw_goal, "人", fw_pct)
    else:
        ui.info("フォロワー: 記録なし")

    # --- コンテンツカテゴリ内訳 ---
    if posts:
        ui.section("コンテンツカテゴリ内訳")
        cat_counts: dict[str, int] = {}
        for p in posts:
            cat = p.get("content_category", "未分類")
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
        for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
            label = CATEGORY_LABEL.get(cat, cat)
            bar   = "█" * cnt
            print(f"  {label[:18]:18} : {bar} ({cnt}件)")

    # --- フックタイプ内訳 ---
    if posts:
        hook_counts: dict[str, int] = {}
        for p in posts:
            h = p.get("hook_type", "")
            if h and h != "none":
                hook_counts[h] = hook_counts.get(h, 0) + 1
        if hook_counts:
            ui.section("フックタイプ内訳")
            for h, cnt in sorted(hook_counts.items(), key=lambda x: -x[1]):
                label = HOOK_LABEL.get(h, h)
                bar   = "█" * cnt
                print(f"  {label[:18]:18} : {bar} ({cnt}件)")

    # --- カテゴリ別エンゲージメント分析 ---
    if metrics and posts:
        post_map = {p["id"]: p for p in posts}
        cat_metrics: dict[str, list] = {}
        for m in metrics:
            post  = post_map.get(m["post_id"])
            cat   = post.get("content_category", "未分類") if post else "未分類"
            cat_metrics.setdefault(cat, []).append(m["engagement_rate"])
        if cat_metrics:
            ui.section("カテゴリ別 平均エンゲージメント率")
            ranked = sorted(
                cat_metrics.items(),
                key=lambda x: sum(x[1]) / len(x[1]),
                reverse=True,
            )
            for cat, rates in ranked:
                avg  = round(sum(rates) / len(rates), 2)
                label = CATEGORY_LABEL.get(cat, cat)
                color = ui.Color.GREEN if avg >= 3.0 else (ui.Color.YELLOW if avg >= 1.5 else ui.Color.RED)
                print(f"  {label[:20]:20} : {color}{avg}%{ui.Color.RESET}  ({len(rates)}件)")

    # --- Top3 投稿 ---
    if metrics:
        ui.section("インプレッション Top3 投稿")
        top3 = sorted(metrics, key=lambda m: m["impressions"], reverse=True)[:3]
        for i, m in enumerate(top3, 1):
            print(f"  {i}. {m['post_content'][:35]}")
            print(f"     imp:{m['impressions']:,}  ❤:{m['likes']}  RT:{m['retweets']}  eng:{m['engagement_rate']}%")


def _show_metrics():
    metrics = _load_metrics()
    if not metrics:
        ui.info("指標データがありません")
        return

    cycle = _select_cycle()
    if not cycle:
        return

    cycle_metrics = [m for m in metrics if m.get("cycle_id") == cycle["id"]]
    if not cycle_metrics:
        ui.info("このサイクルに指標データがありません")
        return

    rows = [
        [
            m["post_id"],
            m.get("post_content", "")[:20],
            f"{m['impressions']:,}",
            m["likes"],
            m["retweets"],
            m["replies"],
            f"{m['engagement_rate']}%",
        ]
        for m in cycle_metrics
    ]
    ui.table(
        ["投稿ID", "内容", "imp", "❤", "RT", "返信", "eng%"],
        rows,
        [10, 22, 10, 6, 6, 6, 7],
    )


def _print_kpi(label: str, actual, goal, unit: str, pct: int):
    bar_len = min(pct // 5, 20)
    bar     = "█" * bar_len + "░" * (20 - bar_len)
    color   = ui.Color.GREEN if pct >= 100 else (ui.Color.YELLOW if pct >= 60 else ui.Color.RED)
    print(f"\n  {ui.Color.BOLD}{label}{ui.Color.RESET}")
    print(f"  実績: {actual}{unit}  /  目標: {goal}{unit}  ({pct}%)")
    print(f"  {color}{bar}{ui.Color.RESET}")

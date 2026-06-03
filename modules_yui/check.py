"""
Check (確認) モジュール - 結衣専用
投稿ごとの指標入力 + フォロワー記録 + 達成状況確認
"""

import uuid

from modules import ui
from . import storage
from .plan import get_active_cycle, list_cycles, get_cycle_by_id
from .do import get_posts_for_cycle, CATEGORY_LABEL, HOOK_LABEL


METRICS_FILE   = "yui_metrics.json"
FOLLOWERS_FILE = "yui_followers.json"


def _load_metrics() -> list:
    return storage.load_list(METRICS_FILE)


def _save_metrics(data: list):
    storage.save_list(METRICS_FILE, data)


def _load_followers() -> list:
    return storage.load_list(FOLLOWERS_FILE)


def _save_followers(data: list):
    storage.save_list(FOLLOWERS_FILE, data)


def get_metrics_for_cycle(cycle_id: str) -> list:
    return [m for m in _load_metrics() if m.get("cycle_id") == cycle_id]


def get_followers_for_cycle(cycle_id: str) -> list:
    return [f for f in _load_followers() if f.get("cycle_id") == cycle_id]


def run():
    ui.header("CHECK - 確認", ui.Color.YELLOW)

    while True:
        choice = ui.menu("Check メニュー", [
            ("1", "投稿の指標を入力"),
            ("2", "フォロワー数を記録"),
            ("3", "達成状況サマリー"),
            ("4", "指標一覧を表示"),
            ("0", "メインメニューに戻る"),
        ])

        if choice == "1":
            _input_metrics()
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
        if ui.prompt(f"アクティブサイクル '{active['name']}' を使用しますか？ (y/n)", "y").lower() == "y":
            return active

    cycles = list_cycles()
    if not cycles:
        ui.error("サイクルがありません")
        return None
    for c in cycles:
        print(f"  {ui.Color.CYAN}{c['id']}{ui.Color.RESET} - {c['name']}")
    return get_cycle_by_id(ui.prompt("サイクルID"))


def _input_metrics():
    ui.section("投稿指標を入力")

    cycle = _select_cycle()
    if not cycle:
        return

    posts = get_posts_for_cycle(cycle["id"])
    if not posts:
        ui.error("投稿記録がありません。先にDoで記録してください。")
        return

    existing = {m["post_id"] for m in _load_metrics() if m.get("cycle_id") == cycle["id"]}

    ui.section(f"投稿一覧 ({cycle['name']})")
    for p in posts:
        status = f"{ui.Color.DIM}[記録済]{ui.Color.RESET}" if p["id"] in existing else ""
        cat = CATEGORY_LABEL.get(p.get("category", ""), "")
        print(f"  {ui.Color.CYAN}{p['id']}{ui.Color.RESET} [{cat:4}] {p['date'][:10]} {status}")
        print(f"    {p['content'][:45]}")

    pid = ui.prompt("\n指標を入力する投稿ID")
    post = next((p for p in posts if p["id"] == pid), None)
    if not post:
        ui.error("IDが見つかりません")
        return

    print(f"\n  対象: {post['content'][:55]}")
    ui.section("指標を入力 (Enterで0)")

    impressions  = ui.prompt_int("インプレッション数", 0)
    likes        = ui.prompt_int("いいね数", 0)
    retweets     = ui.prompt_int("リポスト数", 0)
    replies      = ui.prompt_int("返信数", 0)
    bookmarks    = ui.prompt_int("ブックマーク数", 0)
    profile_vis  = ui.prompt_int("プロフィールアクセス数", 0)
    new_follows  = ui.prompt_int("この投稿経由のフォロー数 (任意)", 0)

    dmm_clicks = 0
    dmm_conv   = 0
    if post.get("category") == "dmm":
        ui.section("DMM指標")
        dmm_clicks = ui.prompt_int("DMMリンククリック数", 0)
        dmm_conv   = ui.prompt_int("DMM成約数", 0)

    eng_actions = (likes or 0) + (retweets or 0) + (replies or 0) + (bookmarks or 0)
    eng_rate = round(eng_actions / impressions * 100, 2) if impressions else 0.0
    dmm_ctr  = round(dmm_clicks / impressions * 100, 2) if impressions and post.get("category") == "dmm" else 0.0

    metric = {
        "id":           str(uuid.uuid4())[:8],
        "cycle_id":     cycle["id"],
        "post_id":      pid,
        "post_content": post["content"][:50],
        "post_cat":     post.get("category", "daily"),
        "recorded_at":  ui.now_str(),
        "impressions":  impressions or 0,
        "likes":        likes or 0,
        "retweets":     retweets or 0,
        "replies":      replies or 0,
        "bookmarks":    bookmarks or 0,
        "profile_vis":  profile_vis or 0,
        "new_follows":  new_follows or 0,
        "dmm_clicks":   dmm_clicks,
        "dmm_conv":     dmm_conv,
        "engagement_rate": eng_rate,
        "dmm_ctr":      dmm_ctr,
    }

    metrics = _load_metrics()
    updated = False
    for i, m in enumerate(metrics):
        if m.get("post_id") == pid and m.get("cycle_id") == cycle["id"]:
            metrics[i] = metric
            updated = True
            break
    if not updated:
        metrics.append(metric)

    _save_metrics(metrics)
    ui.success(f"指標を記録しました (エンゲージ率: {eng_rate}%)")
    if dmm_ctr:
        ui.info(f"DMM CTR: {dmm_ctr}%  成約数: {dmm_conv}")


def _record_followers():
    ui.section("フォロワー数を記録")

    cycle = _select_cycle()
    if not cycle:
        return

    count = ui.prompt_int("現在のフォロワー数")
    if count is None:
        ui.error("フォロワー数を入力してください")
        return

    memo = ui.prompt("メモ (任意)")

    record = {
        "id":          str(uuid.uuid4())[:8],
        "cycle_id":    cycle["id"],
        "date":        ui.today_str(),
        "count":       count,
        "memo":        memo,
        "recorded_at": ui.now_str(),
    }

    followers = _load_followers()
    followers.append(record)
    _save_followers(followers)

    cycle_fw = get_followers_for_cycle(cycle["id"])
    goal = cycle["goals"].get("followers_total", 0)
    pct  = round(count / goal * 100) if goal else 0
    ui.success(f"フォロワー数を記録しました ({count:,} 人 / 目標 {goal:,} 人 = {pct}%)")

    if len(cycle_fw) >= 2:
        gain = count - cycle_fw[0]["count"]
        ui.info(f"このサイクル内増加: {gain:+d} 人")


def _show_achievement():
    ui.section("達成状況確認")

    cycle = _select_cycle()
    if not cycle:
        return

    goals     = cycle["goals"]
    posts     = get_posts_for_cycle(cycle["id"])
    metrics   = get_metrics_for_cycle(cycle["id"])
    followers = get_followers_for_cycle(cycle["id"])

    ui.section(f"{cycle['name']} ({cycle['start_date']} ~ {cycle['end_date']})")

    # 投稿数
    _kpi_bar("投稿数", len(posts), goals.get("posts", 0), "件")

    # フォロワー
    if followers:
        latest_fw = followers[-1]["count"]
        _kpi_bar("フォロワー数", latest_fw, goals.get("followers_total", 0), "人")
    else:
        ui.info("フォロワー: 未記録")

    # インプレッション
    total_imp = sum(m["impressions"] for m in metrics)
    _kpi_bar("インプレッション", total_imp, goals.get("impressions", 0), "")

    # エンゲージメント率
    avg_eng = round(sum(m["engagement_rate"] for m in metrics) / len(metrics), 2) if metrics else 0.0
    _kpi_bar("平均エンゲージ率", avg_eng, goals.get("engagement_rate", 0), "%")

    # DMM CTR
    dmm_metrics = [m for m in metrics if m.get("post_cat") == "dmm" and m.get("impressions", 0) > 0]
    if dmm_metrics:
        avg_dmm_ctr = round(sum(m["dmm_ctr"] for m in dmm_metrics) / len(dmm_metrics), 2)
        _kpi_bar("DMM平均CTR", avg_dmm_ctr, goals.get("dmm_ctr", 3.0), "%")
        total_conv = sum(m.get("dmm_conv", 0) for m in dmm_metrics)
        ui.info(f"DMM総成約数: {total_conv} 件")

    # 投稿比率
    if posts:
        ui.section("投稿比率 (目標: 日常70% / 恋愛20% / DMM10%)")
        total = len(posts)
        for cat, label in [("daily", "日常"), ("love", "恋愛"), ("dmm", "DMM ")]:
            cnt = sum(1 for p in posts if p.get("category") == cat)
            pct = round(cnt / total * 100)
            tgt = goals.get(f"ratio_{cat}", 0)
            diff = pct - tgt
            sign = f"+{diff}" if diff > 0 else str(diff)
            color = ui.Color.GREEN if abs(diff) <= 5 else ui.Color.YELLOW
            print(f"  {label}  {cnt:3d}件 / {pct:3d}% (目標{tgt}%  {color}{sign}%{ui.Color.RESET})")

    # Top3投稿
    if metrics:
        ui.section("インプレッション Top3")
        for i, m in enumerate(sorted(metrics, key=lambda x: x["impressions"], reverse=True)[:3], 1):
            print(f"  {i}. {m['post_content'][:38]}")
            print(f"     imp:{m['impressions']:,}  ❤:{m['likes']}  RT:{m['retweets']}  eng:{m['engagement_rate']}%")


def _show_metrics():
    cycle = _select_cycle()
    if not cycle:
        return

    metrics = get_metrics_for_cycle(cycle["id"])
    if not metrics:
        ui.info("指標データがありません")
        return

    rows = [
        [
            m["post_id"],
            CATEGORY_LABEL.get(m.get("post_cat",""), "-"),
            f"{m['impressions']:,}",
            m["likes"],
            m["retweets"],
            f"{m['engagement_rate']}%",
            m.get("dmm_clicks", 0) or "-",
        ]
        for m in metrics
    ]
    ui.table(
        ["投稿ID", "カテゴリ", "imp", "❤", "RT", "eng%", "DMM"],
        rows,
        [10, 8, 10, 6, 6, 7, 6],
    )


def _kpi_bar(label: str, actual, goal, unit: str):
    try:
        pct = round(float(actual) / float(goal) * 100) if goal else 0
    except Exception:
        pct = 0
    bar_len = min(pct // 5, 20)
    bar     = "█" * bar_len + "░" * (20 - bar_len)
    color   = ui.Color.GREEN if pct >= 100 else (ui.Color.YELLOW if pct >= 60 else ui.Color.RED)
    print(f"\n  {ui.Color.BOLD}{label}{ui.Color.RESET}")
    print(f"  実績: {actual}{unit}  /  目標: {goal}{unit}  ({pct}%)")
    print(f"  {color}{bar}{ui.Color.RESET}")

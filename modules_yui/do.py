"""
Do (実行) モジュール - 結衣専用
投稿記録。カテゴリ: 日常(70%) / 恋愛(20%) / DMM(10%)
"""

import uuid

from modules import ui
from . import storage
from .plan import get_active_cycle, list_cycles, get_cycle_by_id


POSTS_FILE = "yui_posts.json"

CONTENT_CATEGORIES = [
    ("daily", "日常  (夜勤帰り・コンビニ・朝の空気) [目標70%]"),
    ("love",  "恋愛  (淡い恋愛・片思い・温かさへの憧れ) [目標20%]"),
    ("dmm",   "DMM   (夜勤→動画→FANZA誘導) [目標10%]"),
]

POST_TYPES = [
    ("text",   "テキストのみ"),
    ("image",  "画像付き (AI画像 or 自撮り)"),
    ("thread", "スレッド"),
    ("reply",  "リプライ"),
    ("quote",  "引用リポスト"),
]

HOOK_TYPES = [
    ("scene",   "情景描写 (朝5時・コンビニ・鳥の声)"),
    ("emotion", "感情吐露 (寂しい・温かい・眠れない)"),
    ("relate",  "共感誘発 (同じ人いる? 夜勤あるある)"),
    ("love",    "恋愛フック (手繋ぐだけで幸せ系)"),
    ("story",   "物語導線 (夜勤→動画→おすすめ)"),
    ("none",    "なし"),
]

TIME_SLOTS = [
    ("dawn",    "朝5〜9時 (夜勤帰り・帰宅直後)"),
    ("morning", "9〜12時 (帰宅後まったり)"),
    ("noon",    "12〜17時 (昼・寝起き後)"),
    ("night",   "17〜24時 (出勤前・夜勤前)"),
    ("late",    "0〜5時 (夜勤中・休憩)"),
]

CATEGORY_LABEL = {k: v.split("(")[0].strip() for k, v in CONTENT_CATEGORIES}
HOOK_LABEL     = {k: v.split("(")[0].strip() for k, v in HOOK_TYPES}
TIME_LABEL     = {k: v.split("(")[0].strip() for k, v in TIME_SLOTS}


def _load_posts() -> list:
    return storage.load_list(POSTS_FILE)


def _save_posts(data: list):
    storage.save_list(POSTS_FILE, data)


def get_posts_for_cycle(cycle_id: str) -> list:
    return [p for p in _load_posts() if p.get("cycle_id") == cycle_id]


def run():
    ui.header("DO - 実行", ui.Color.GREEN)

    while True:
        choice = ui.menu("Do メニュー", [
            ("1", "投稿を記録する"),
            ("2", "投稿比率を確認 (70/20/10)"),
            ("3", "投稿一覧を表示"),
            ("4", "投稿を削除"),
            ("0", "メインメニューに戻る"),
        ])

        if choice == "1":
            _log_post()
        elif choice == "2":
            _show_ratio()
        elif choice == "3":
            _show_posts()
        elif choice == "4":
            _delete_post()
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
        ui.error("サイクルがありません。先にPlanでサイクルを作成してください。")
        return None
    for c in cycles:
        print(f"  {ui.Color.CYAN}{c['id']}{ui.Color.RESET} - {c['name']}")
    return get_cycle_by_id(ui.prompt("サイクルID"))


def _log_post():
    ui.section("投稿を記録")

    cycle = _select_cycle()
    if not cycle:
        return

    post_date    = ui.prompt("投稿日時 (YYYY-MM-DD HH:MM)", ui.now_str())
    content      = ui.prompt("投稿内容 (冒頭〜概要)")
    if not content:
        ui.error("投稿内容は必須です")
        return

    post_type    = ui.menu("投稿フォーマット", POST_TYPES)
    cat          = ui.menu("コンテンツカテゴリ", CONTENT_CATEGORIES)
    hook         = ui.menu("フックタイプ", HOOK_TYPES)
    time_slot    = ui.menu("投稿時間帯", TIME_SLOTS)

    ai_image = "no"
    if post_type == "image":
        ai_image = ui.prompt("AI画像を使用しましたか？ (yes/no)", "no")

    dmm_product_id = ""
    if cat == "dmm":
        dmm_product_id = ui.prompt("DMM案件ID (任意、dmmメニューで登録済みの場合)")

    hashtags_raw = ui.prompt("使用ハッシュタグ (カンマ区切り, 任意)")
    hashtags = [h.strip() for h in hashtags_raw.split(",") if h.strip()] if hashtags_raw else []

    url  = ui.prompt("投稿URL (任意)")
    memo = ui.prompt("メモ (任意)")

    post = {
        "id":             str(uuid.uuid4())[:8],
        "cycle_id":       cycle["id"],
        "cycle_name":     cycle["name"],
        "date":           post_date,
        "content":        content,
        "type":           post_type,
        "category":       cat,
        "hook":           hook,
        "time_slot":      time_slot,
        "ai_image":       ai_image,
        "dmm_product_id": dmm_product_id,
        "hashtags":       hashtags,
        "url":            url,
        "memo":           memo,
        "created_at":     ui.now_str(),
    }

    posts = _load_posts()
    posts.append(post)
    _save_posts(posts)

    ui.success(f"投稿を記録しました (ID: {post['id']})")

    # 即時比率フィードバック
    cycle_posts = get_posts_for_cycle(cycle["id"])
    total = len(cycle_posts)
    goals = cycle["goals"]
    goal_posts = goals.get("posts", 0)
    ui.info(f"累計投稿数: {total} / 目標 {goal_posts} 件")

    if total >= 5:
        _print_ratio_bar(cycle_posts, goals)


def _show_ratio():
    cycle = _select_cycle()
    if not cycle:
        return

    posts = get_posts_for_cycle(cycle["id"])
    if not posts:
        ui.info("投稿記録がありません")
        return

    ui.section(f"投稿比率 ({cycle['name']})")
    _print_ratio_bar(posts, cycle["goals"])


def _print_ratio_bar(posts: list, goals: dict):
    total = len(posts)
    if total == 0:
        return

    counts = {"daily": 0, "love": 0, "dmm": 0}
    for p in posts:
        cat = p.get("category", "daily")
        if cat in counts:
            counts[cat] += 1

    targets = {
        "daily": goals.get("ratio_daily", 70),
        "love":  goals.get("ratio_love", 20),
        "dmm":   goals.get("ratio_dmm", 10),
    }
    labels = {"daily": "日常", "love": "恋愛", "dmm": "DMM "}
    colors = {"daily": ui.Color.CYAN, "love": ui.Color.RED, "dmm": ui.Color.YELLOW}

    print(f"\n  総投稿数: {total} 件\n")
    for cat in ["daily", "love", "dmm"]:
        cnt  = counts[cat]
        pct  = round(cnt / total * 100)
        tgt  = targets[cat]
        diff = pct - tgt
        bar  = "█" * (cnt // max(total // 20, 1) + 1) if cnt > 0 else ""
        sign = f"+{diff}" if diff > 0 else str(diff)
        ok   = ui.Color.GREEN if abs(diff) <= 5 else ui.Color.YELLOW if abs(diff) <= 15 else ui.Color.RED
        color = colors[cat]
        print(f"  {color}{labels[cat]}{ui.Color.RESET}  {bar:<20} {pct:3d}% (目標{tgt}%  {ok}{sign}%{ui.Color.RESET})")


def _show_posts():
    posts = _load_posts()
    if not posts:
        ui.info("投稿記録がありません")
        return

    f_choice = ui.menu("表示対象", [
        ("1", "アクティブサイクルの投稿"),
        ("2", "サイクル指定"),
        ("3", "全投稿"),
    ])

    if f_choice == "1":
        cycle = get_active_cycle()
        if not cycle:
            ui.info("アクティブなサイクルがありません")
            return
        filtered = get_posts_for_cycle(cycle["id"])
    elif f_choice == "2":
        cycles = list_cycles()
        for c in cycles:
            print(f"  {ui.Color.CYAN}{c['id']}{ui.Color.RESET} - {c['name']}")
        filtered = [p for p in posts if p.get("cycle_id") == ui.prompt("サイクルID")]
    else:
        filtered = posts

    if not filtered:
        ui.info("該当する投稿がありません")
        return

    rows = [
        [p["id"], p["date"][:10], CATEGORY_LABEL.get(p.get("category",""), "-"), p["content"][:28]]
        for p in filtered
    ]
    ui.table(["ID", "日付", "カテゴリ", "内容"], rows, [10, 12, 8, 30])

    pid = ui.prompt("\n詳細表示するID (Enterでスキップ)")
    if pid:
        post = next((p for p in filtered if p["id"] == pid), None)
        if post:
            _print_post(post)
        else:
            ui.error("IDが見つかりません")


def _delete_post():
    posts = _load_posts()
    if not posts:
        ui.info("投稿記録がありません")
        return

    pid = ui.prompt("削除する投稿ID")
    post = next((p for p in posts if p["id"] == pid), None)
    if not post:
        ui.error("IDが見つかりません")
        return

    _print_post(post)
    if ui.prompt("本当に削除しますか？ (yes/no)", "no").lower() == "yes":
        _save_posts([p for p in posts if p["id"] != pid])
        ui.success("削除しました")
    else:
        ui.info("キャンセルしました")


def _print_post(post: dict):
    ui.section(f"投稿詳細: {post['id']}")
    print(f"  サイクル  : {post.get('cycle_name', '-')}")
    print(f"  日時      : {post['date']}")
    print(f"  カテゴリ  : {CATEGORY_LABEL.get(post.get('category',''), '-')}")
    print(f"  フック    : {HOOK_LABEL.get(post.get('hook',''), '-')}")
    print(f"  時間帯    : {TIME_LABEL.get(post.get('time_slot',''), '-')}")
    print(f"  AI画像    : {post.get('ai_image', 'no')}")
    print(f"  内容      : {post['content']}")
    if post.get("hashtags"):
        print(f"  タグ      : {' '.join(post['hashtags'])}")
    if post.get("dmm_product_id"):
        print(f"  DMM案件   : {post['dmm_product_id']}")
    if post.get("url"):
        print(f"  URL       : {post['url']}")
    if post.get("memo"):
        print(f"  メモ      : {post['memo']}")

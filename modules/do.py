"""
Do (実行) モジュール
PDCAサイクルの実行フェーズを管理する
- 投稿ログの記録
- 投稿カテゴリ・メディアタイプ管理
- サイクルごとの活動追跡
"""

import uuid

from . import storage, ui
from .plan import get_active_cycle, list_cycles, get_cycle_by_id


POSTS_FILE = "posts.json"

POST_TYPES = [
    ("text",    "テキストのみ"),
    ("image",   "画像付き"),
    ("video",   "動画付き"),
    ("thread",  "スレッド"),
    ("quote",   "引用リポスト"),
    ("reply",   "リプライ"),
]

# ノクト専用コンテンツカテゴリ
CONTENT_CATEGORIES = [
    ("reality",  "リアル体験（工場・夜勤の現実）"),
    ("numbers",  "数字公開（インプレ・売上・フォロワー）"),
    ("failure",  "失敗→改善ストーリー"),
    ("ai",       "AI活用レポート"),
    ("learning", "学び・気づき"),
    ("journey",  "0→1ジャーニー"),
    ("empathy",  "共感・応援"),
]

# フックタイプ
HOOK_TYPES = [
    ("number",   "数字フック（「〇〇日目」「〇〇円」）"),
    ("empathy",  "共感フック（「わかる」「あるある」）"),
    ("shock",    "衝撃フック（「正直に言う」「驚いた」）"),
    ("question", "疑問フック（「なぜ〇〇なのか」）"),
    ("declare",  "宣言フック（「やる」「変える」）"),
    ("none",     "なし"),
]

CATEGORY_LABEL = {k: v for k, v in CONTENT_CATEGORIES}
HOOK_LABEL     = {k: v for k, v in HOOK_TYPES}


def _load_posts() -> list:
    return storage.load_list(POSTS_FILE)


def _save_posts(posts: list):
    storage.save_list(POSTS_FILE, posts)


def get_posts_for_cycle(cycle_id: str) -> list:
    return [p for p in _load_posts() if p.get("cycle_id") == cycle_id]


def run():
    ui.header("DO - 実行", ui.Color.GREEN)

    while True:
        choice = ui.menu("Do メニュー", [
            ("1", "投稿を記録する"),
            ("2", "投稿一覧を表示"),
            ("3", "投稿を削除"),
            ("0", "メインメニューに戻る"),
        ])

        if choice == "1":
            _log_post()
        elif choice == "2":
            _show_posts()
        elif choice == "3":
            _delete_post()
        elif choice == "0":
            break


def _select_cycle() -> dict | None:
    """アクティブなサイクルを自動選択 or 手動選択"""
    active = get_active_cycle()
    if active:
        use_active = ui.prompt(f"アクティブサイクル '{active['name']}' を使用しますか？ (y/n)", "y")
        if use_active.lower() == "y":
            return active

    cycles = list_cycles()
    if not cycles:
        ui.error("サイクルがありません。先にPlanでサイクルを作成してください。")
        return None

    ui.section("サイクル選択")
    for c in cycles:
        print(f"  {ui.Color.CYAN}{c['id']}{ui.Color.RESET} - {c['name']} ({c['start_date']}~{c['end_date']})")

    cycle_id = ui.prompt("サイクルID")
    return get_cycle_by_id(cycle_id)


def _log_post():
    ui.section("投稿を記録")

    cycle = _select_cycle()
    if not cycle:
        return

    post_date = ui.prompt("投稿日時 (YYYY-MM-DD HH:MM)", ui.now_str())
    content = ui.prompt("投稿内容 (概要・冒頭文)")
    if not content:
        ui.error("投稿内容は必須です")
        return

    post_type = ui.menu("投稿フォーマット", POST_TYPES)

    ui.section("ノクト専用分類")
    content_category = ui.menu("コンテンツカテゴリ", CONTENT_CATEGORIES)
    hook_type        = ui.menu("フックタイプ", HOOK_TYPES)

    themes = cycle["content_plan"].get("themes", [])
    if themes:
        print(f"  計画テーマ: {', '.join(themes)}")
    theme = ui.prompt("使用したテーマ (任意)")

    hashtags_raw = ui.prompt("使用したハッシュタグ (カンマ区切り, 任意)")
    hashtags = [h.strip() for h in hashtags_raw.split(",") if h.strip()] if hashtags_raw else []

    url = ui.prompt("投稿URL (任意)")
    memo = ui.prompt("メモ (任意)")

    post = {
        "id": str(uuid.uuid4())[:8],
        "cycle_id": cycle["id"],
        "cycle_name": cycle["name"],
        "date": post_date,
        "content": content,
        "type": post_type,
        "content_category": content_category,
        "hook_type": hook_type,
        "theme": theme,
        "hashtags": hashtags,
        "url": url,
        "memo": memo,
        "created_at": ui.now_str(),
    }

    posts = _load_posts()
    posts.append(post)
    _save_posts(posts)

    ui.success(f"投稿を記録しました (ID: {post['id']})")

    # サイクル内の投稿数を表示
    cycle_posts = get_posts_for_cycle(cycle["id"])
    goal = cycle["goals"].get("posts", 0)
    ui.info(f"このサイクルの投稿数: {len(cycle_posts)} / 目標 {goal} 件")


def _show_posts():
    posts = _load_posts()
    if not posts:
        ui.info("投稿記録がありません")
        return

    ui.section("投稿フィルター")
    filter_choice = ui.menu("表示対象", [
        ("1", "アクティブサイクルの投稿"),
        ("2", "サイクルを指定して表示"),
        ("3", "全投稿を表示"),
    ])

    if filter_choice == "1":
        cycle = get_active_cycle()
        if not cycle:
            ui.info("アクティブなサイクルがありません")
            return
        filtered = get_posts_for_cycle(cycle["id"])
        title = f"投稿一覧 ({cycle['name']})"
    elif filter_choice == "2":
        cycle_id = ui.prompt("サイクルID")
        filtered = [p for p in posts if p.get("cycle_id") == cycle_id]
        cycle = get_cycle_by_id(cycle_id)
        title = f"投稿一覧 ({cycle['name'] if cycle else cycle_id})"
    else:
        filtered = posts
        title = "全投稿一覧"

    if not filtered:
        ui.info("該当する投稿がありません")
        return

    ui.section(title)
    rows = [
        [p["id"], p["date"][:10], p.get("content_category", p["type"]), p["content"][:25]]
        for p in filtered
    ]
    ui.table(
        ["ID", "日付", "カテゴリ", "内容"],
        rows,
        [10, 12, 10, 27],
    )

    show_id = ui.prompt("\n詳細表示するID (Enterでスキップ)")
    if show_id:
        post = next((p for p in filtered if p["id"] == show_id), None)
        if post:
            _print_post(post)
        else:
            ui.error("IDが見つかりません")


def _delete_post():
    posts = _load_posts()
    if not posts:
        ui.info("投稿記録がありません")
        return

    post_id = ui.prompt("削除する投稿ID")
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        ui.error("IDが見つかりません")
        return

    _print_post(post)
    confirm = ui.prompt("本当に削除しますか？ (yes/no)", "no")
    if confirm.lower() == "yes":
        updated = [p for p in posts if p["id"] != post_id]
        _save_posts(updated)
        ui.success("投稿を削除しました")
    else:
        ui.info("削除をキャンセルしました")


def _print_post(post: dict):
    ui.section(f"投稿詳細: {post['id']}")
    print(f"  サイクル  : {post.get('cycle_name', post.get('cycle_id', '-'))}")
    print(f"  日時      : {post['date']}")
    print(f"  フォーマット: {post['type']}")
    cat = post.get("content_category", "")
    if cat:
        print(f"  カテゴリ  : {CATEGORY_LABEL.get(cat, cat)}")
    hook = post.get("hook_type", "")
    if hook and hook != "none":
        print(f"  フック    : {HOOK_LABEL.get(hook, hook)}")
    print(f"  内容      : {post['content']}")
    if post.get("theme"):
        print(f"  テーマ    : {post['theme']}")
    if post.get("hashtags"):
        print(f"  タグ      : {', '.join(post['hashtags'])}")
    if post.get("url"):
        print(f"  URL       : {post['url']}")
    if post.get("memo"):
        print(f"  メモ      : {post['memo']}")

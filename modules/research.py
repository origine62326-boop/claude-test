"""
リサーチ・分析モジュール (ハーマイオニー)
テーマ・ネタを収集・管理し、今日のブリーフィングを生成する
- ネタ帳: URL/メモ/キーワードの保存
- テーマ設定: 今日の投稿テーマとターゲット
- ブリーフィング生成: テーマ × ハッシュタグ × 参考情報のまとめ
"""

import uuid

from . import storage, ui
from .plan import get_active_cycle


BRIEFS_FILE = "briefs.json"
NETA_FILE   = "neta.json"


def _load_briefs() -> list:
    return storage.load_list(BRIEFS_FILE)


def _save_briefs(data: list):
    storage.save_list(BRIEFS_FILE, data)


def _load_neta() -> list:
    return storage.load_list(NETA_FILE)


def _save_neta(data: list):
    storage.save_list(NETA_FILE, data)


def get_latest_brief() -> dict | None:
    briefs = _load_briefs()
    return briefs[-1] if briefs else None


def get_brief_by_id(brief_id: str) -> dict | None:
    for b in _load_briefs():
        if b["id"] == brief_id:
            return b
    return None


def run():
    ui.header("RESEARCH - リサーチ・分析 [ハーマイオニー]", ui.Color.BLUE)
    print(f"  {ui.Color.DIM}YouTube・ニュースを収集し、今日のテーマとブリーフィングを生成{ui.Color.RESET}")

    while True:
        choice = ui.menu("Researchメニュー", [
            ("1", "今日のブリーフィングを作成"),
            ("2", "ネタ帳に追加"),
            ("3", "ネタ帳を表示"),
            ("4", "ブリーフィング履歴"),
            ("0", "戻る"),
        ])

        if choice == "1":
            _create_briefing()
        elif choice == "2":
            _add_neta()
        elif choice == "3":
            _show_neta()
        elif choice == "4":
            _show_briefs()
        elif choice == "0":
            break


def _create_briefing():
    ui.section("今日のブリーフィング作成")

    cycle = get_active_cycle()
    cycle_themes = cycle["content_plan"].get("themes", []) if cycle else []
    if cycle_themes:
        print(f"  計画テーマ: {', '.join(cycle_themes)}")

    # テーマ設定
    main_theme = ui.prompt("今日のメインテーマ")
    if not main_theme:
        ui.error("テーマは必須です")
        return

    sub_theme = ui.prompt("サブテーマ (任意)")

    # ターゲット
    target = ui.prompt("ターゲット読者 (例: エンジニア初心者, マーケター)", "フォロワー全体")

    # 参考情報
    ui.section("参考情報を入力 (Enterで終了)")
    refs = []
    while True:
        ref_url = ui.prompt(f"  参考URL #{len(refs)+1} (Enterでスキップ)")
        if not ref_url:
            break
        ref_memo = ui.prompt(f"  メモ")
        refs.append({"url": ref_url, "memo": ref_memo})

    # ネタ帳からピックアップ
    neta_list = _load_neta()
    unused = [n for n in neta_list if not n.get("used")]
    if unused:
        ui.section(f"ネタ帳から参考にする ({len(unused)}件 未使用)")
        for n in unused[:5]:
            print(f"  [{n['id']}] {n['keyword']} - {n['memo'][:30]}")
        neta_ids_raw = ui.prompt("使用するネタIDをカンマ区切りで (Enterでスキップ)")
        neta_ids = [s.strip() for s in neta_ids_raw.split(",") if s.strip()] if neta_ids_raw else []
    else:
        neta_ids = []

    # トーン・スタイル
    tone = ui.menu("今日のトーン", [
        ("casual",    "カジュアル・親しみやすい"),
        ("expert",    "専門的・信頼感"),
        ("inspiring", "インスピレーション・前向き"),
        ("question",  "問いかけ・共感"),
        ("story",     "ストーリー・体験談"),
    ])

    # ハッシュタグ
    cycle_tags = cycle["content_plan"].get("hashtags", []) if cycle else []
    tags_default = ",".join(cycle_tags)
    tags_raw = ui.prompt("使用ハッシュタグ (カンマ区切り)", tags_default)
    hashtags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []

    # 投稿数目標
    slot_count = ui.prompt_int("今日の投稿スロット数", 3)
    tree_count = ui.prompt_int("1スロットのツリー数 (1=単発投稿)", 1)

    brief = {
        "id": str(uuid.uuid4())[:8],
        "date": ui.today_str(),
        "cycle_id": cycle["id"] if cycle else None,
        "main_theme": main_theme,
        "sub_theme": sub_theme,
        "target": target,
        "tone": tone,
        "hashtags": hashtags,
        "references": refs,
        "neta_ids": neta_ids,
        "slot_count": slot_count or 3,
        "tree_count": tree_count or 1,
        "created_at": ui.now_str(),
        "status": "active",
    }

    # 参照したネタを使用済みにマーク
    if neta_ids:
        updated_neta = []
        for n in neta_list:
            if n["id"] in neta_ids:
                n["used"] = True
            updated_neta.append(n)
        _save_neta(updated_neta)

    briefs = _load_briefs()
    briefs.append(brief)
    _save_briefs(briefs)

    ui.success(f"ブリーフィングを作成しました (ID: {brief['id']})")
    _print_brief(brief)

    return brief


def _add_neta():
    ui.section("ネタ帳に追加")

    category = ui.menu("カテゴリ", [
        ("news",    "ニュース・トレンド"),
        ("youtube", "YouTube・動画"),
        ("idea",    "アイデア・ひらめき"),
        ("quote",   "名言・引用"),
        ("own",     "自分の体験・気づき"),
        ("other",   "その他"),
    ])

    keyword = ui.prompt("キーワード・タイトル")
    if not keyword:
        ui.error("キーワードは必須です")
        return

    memo = ui.prompt("メモ・要点")
    url  = ui.prompt("URL (任意)")
    tags_raw = ui.prompt("タグ (カンマ区切り, 任意)")
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []

    neta = {
        "id": str(uuid.uuid4())[:8],
        "category": category,
        "keyword": keyword,
        "memo": memo,
        "url": url,
        "tags": tags,
        "used": False,
        "created_at": ui.now_str(),
    }

    neta_list = _load_neta()
    neta_list.append(neta)
    _save_neta(neta_list)

    ui.success(f"ネタを追加しました (ID: {neta['id']})")


def _show_neta():
    neta_list = _load_neta()
    if not neta_list:
        ui.info("ネタ帳が空です")
        return

    filter_used = ui.menu("表示フィルター", [
        ("1", "未使用のみ"),
        ("2", "すべて表示"),
    ])

    filtered = [n for n in neta_list if not n.get("used")] if filter_used == "1" else neta_list

    if not filtered:
        ui.info("該当するネタがありません")
        return

    rows = [
        [n["id"], n["category"], n["keyword"][:25], n["memo"][:25],
         "済" if n.get("used") else "-"]
        for n in filtered
    ]
    ui.table(
        ["ID", "カテゴリ", "キーワード", "メモ", "使用"],
        rows,
        [10, 10, 27, 27, 5],
    )


def _show_briefs():
    briefs = _load_briefs()
    if not briefs:
        ui.info("ブリーフィング履歴がありません")
        return

    rows = [
        [b["id"], b["date"], b["main_theme"][:25], b.get("tone", "-"),
         f"{b['slot_count']}スロット"]
        for b in briefs
    ]
    ui.table(
        ["ID", "日付", "テーマ", "トーン", "スロット"],
        rows,
        [10, 12, 27, 14, 9],
    )

    show_id = ui.prompt("\n詳細表示ID (Enterでスキップ)")
    if show_id:
        brief = get_brief_by_id(show_id)
        if brief:
            _print_brief(brief)
        else:
            ui.error("IDが見つかりません")


def _print_brief(brief: dict):
    ui.section(f"ブリーフィング: {brief['date']}")
    print(f"  ID          : {brief['id']}")
    print(f"  メインテーマ: {brief['main_theme']}")
    if brief.get("sub_theme"):
        print(f"  サブテーマ  : {brief['sub_theme']}")
    print(f"  ターゲット  : {brief.get('target', '-')}")
    print(f"  トーン      : {brief.get('tone', '-')}")
    print(f"  スロット数  : {brief.get('slot_count', 3)}")
    print(f"  ツリー数    : {brief.get('tree_count', 1)}")
    if brief.get("hashtags"):
        print(f"  ハッシュタグ: {' '.join(brief['hashtags'])}")
    if brief.get("references"):
        print(f"  参考情報    :")
        for r in brief["references"]:
            print(f"    - {r['url']}")
            if r.get("memo"):
                print(f"      {r['memo']}")

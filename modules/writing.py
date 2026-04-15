"""
ライティングモジュール (ルーナ)
投稿文案を3スロット × 3〜5ツリーで管理する
- スロット: 朝(7時)・夕(18時)・夜(21時)
- ツリー: 1つのスロットに複数候補案
- ステータス: draft → review → approved / rejected
"""

import uuid

from . import storage, ui
from .research import get_latest_brief, get_brief_by_id, _load_briefs


DRAFTS_FILE = "drafts.json"

SLOTS = {
    "morning": "朝 (7:00)",
    "evening": "夕 (18:00)",
    "night":   "夜 (21:00)",
}


def _load_drafts() -> list:
    return storage.load_list(DRAFTS_FILE)


def _save_drafts(data: list):
    storage.save_list(DRAFTS_FILE, data)


def get_drafts_for_brief(brief_id: str) -> list:
    return [d for d in _load_drafts() if d.get("brief_id") == brief_id]


def get_approved_drafts() -> list:
    return [d for d in _load_drafts() if d.get("status") == "approved"]


def get_draft_by_id(draft_id: str) -> dict | None:
    for d in _load_drafts():
        if d["id"] == draft_id:
            return d
    return None


def run():
    ui.header("WRITING - ライティング [ルーナ]", ui.Color.GREEN)
    print(f"  {ui.Color.DIM}投稿案を3スロット分自動生成（1日3投稿 × 3〜5ツリー）{ui.Color.RESET}")

    while True:
        choice = ui.menu("Writingメニュー", [
            ("1", "投稿文案を新規作成"),
            ("2", "ブリーフィングから文案を展開"),
            ("3", "文案一覧を表示"),
            ("4", "文案を編集"),
            ("0", "戻る"),
        ])

        if choice == "1":
            _create_draft()
        elif choice == "2":
            _expand_from_brief()
        elif choice == "3":
            _show_drafts()
        elif choice == "4":
            _edit_draft()
        elif choice == "0":
            break


def _select_brief() -> dict | None:
    latest = get_latest_brief()
    if latest:
        use = ui.prompt(f"最新ブリーフィング '{latest['main_theme']}' ({latest['date']}) を使用しますか？ (y/n)", "y")
        if use.lower() == "y":
            return latest

    briefs = _load_briefs()
    if not briefs:
        ui.info("ブリーフィングがありません。先にResearchでブリーフィングを作成してください。")
        return None

    for b in briefs[-5:]:
        print(f"  {ui.Color.CYAN}{b['id']}{ui.Color.RESET} - {b['date']} {b['main_theme']}")
    brief_id = ui.prompt("ブリーフィングID (EnterでブリーフィングなしでOK)")
    return get_brief_by_id(brief_id) if brief_id else None


def _create_draft(brief: dict | None = None, slot: str = "", tree_no: int = 1):
    ui.section("投稿文案を作成")

    if brief is None:
        brief = _select_brief()

    if brief:
        print(f"  テーマ: {brief['main_theme']}  トーン: {brief.get('tone', '-')}")
        if brief.get("hashtags"):
            print(f"  タグ  : {' '.join(brief['hashtags'])}")

    # スロット選択
    if not slot:
        slot = ui.menu("投稿スロット", [
            ("morning", "朝 (7:00)"),
            ("evening", "夕 (18:00)"),
            ("night",   "夜 (21:00)"),
            ("unset",   "未設定"),
        ])

    # ツリー番号
    if tree_no == 1:
        tree_no = ui.prompt_int("ツリー番号 (同一スロット内の候補番号)", 1) or 1

    # 投稿内容
    ui.section("投稿内容を入力")
    print(f"  {ui.Color.DIM}改行: \\n と入力してください (後でそのまま保存されます){ui.Color.RESET}")

    body_lines = []
    print(f"  1行ずつ入力 → 空行で終了:")
    while True:
        line = input(f"  {ui.Color.WHITE}> {ui.Color.RESET}")
        if line == "":
            break
        body_lines.append(line)

    body = "\n".join(body_lines)
    if not body.strip():
        ui.error("本文は必須です")
        return None

    # ハッシュタグ
    default_tags = " ".join(brief.get("hashtags", [])) if brief else ""
    tags_raw = ui.prompt("ハッシュタグ", default_tags)
    hashtags = tags_raw.split() if tags_raw else []

    # 文字数チェック
    char_count = len(body)
    color = ui.Color.GREEN if char_count <= 140 else (ui.Color.YELLOW if char_count <= 280 else ui.Color.RED)
    print(f"  文字数: {color}{char_count}{ui.Color.RESET} 文字")

    memo = ui.prompt("ライターメモ (任意)")

    draft = {
        "id": str(uuid.uuid4())[:8],
        "brief_id": brief["id"] if brief else None,
        "brief_theme": brief["main_theme"] if brief else "",
        "slot": slot,
        "tree_no": tree_no,
        "body": body,
        "hashtags": hashtags,
        "char_count": char_count,
        "memo": memo,
        "status": "draft",       # draft / review / approved / rejected
        "quality_score": None,
        "created_at": ui.now_str(),
        "updated_at": ui.now_str(),
    }

    drafts = _load_drafts()
    drafts.append(draft)
    _save_drafts(drafts)

    ui.success(f"文案を保存しました (ID: {draft['id']}  スロット: {SLOTS.get(slot, slot)}  ツリー#{tree_no})")
    return draft


def _expand_from_brief():
    """ブリーフィングからスロット × ツリー数分の文案を展開入力"""
    ui.section("ブリーフィングから文案を展開")

    brief = _select_brief()
    if not brief:
        return

    slot_count  = brief.get("slot_count", 3)
    tree_count  = brief.get("tree_count", 1)
    slot_keys   = list(SLOTS.keys())[:slot_count]

    ui.info(f"スロット {slot_count} 個 × ツリー {tree_count} 個 = 計 {slot_count * tree_count} 文案を入力します")

    for slot in slot_keys:
        ui.section(f"スロット: {SLOTS[slot]}")
        for t in range(1, tree_count + 1):
            print(f"\n  ツリー #{t}/{tree_count}")
            skip = ui.prompt("  スキップしますか？ (y/n)", "n")
            if skip.lower() == "y":
                continue
            _create_draft(brief=brief, slot=slot, tree_no=t)

    ui.success("文案展開が完了しました")
    _show_drafts(brief_id=brief["id"])


def _show_drafts(brief_id: str | None = None):
    drafts = _load_drafts()
    if not drafts:
        ui.info("文案がありません")
        return

    if brief_id:
        filtered = [d for d in drafts if d.get("brief_id") == brief_id]
    else:
        latest = get_latest_brief()
        if latest:
            use = ui.prompt(f"最新ブリーフィング '{latest['main_theme']}' の文案を表示しますか？ (y/n)", "y")
            filtered = [d for d in drafts if d.get("brief_id") == latest["id"]] if use.lower() == "y" else drafts
        else:
            filtered = drafts

    if not filtered:
        ui.info("該当する文案がありません")
        return

    status_colors = {
        "draft":    ui.Color.DIM,
        "review":   ui.Color.YELLOW,
        "approved": ui.Color.GREEN,
        "rejected": ui.Color.RED,
    }

    rows = []
    for d in filtered:
        sc = status_colors.get(d["status"], "")
        rows.append([
            d["id"],
            SLOTS.get(d["slot"], d["slot"])[:6],
            f"#{d.get('tree_no',1)}",
            f"{sc}{d['status']}{ui.Color.RESET}",
            f"{d['char_count']}字",
            d["body"][:30].replace("\n", " "),
        ])

    ui.table(
        ["ID", "スロット", "ツリー", "状態", "文字数", "本文"],
        rows,
        [10, 10, 7, 10, 7, 32],
    )

    show_id = ui.prompt("\n詳細表示ID (Enterでスキップ)")
    if show_id:
        d = get_draft_by_id(show_id)
        if d:
            _print_draft(d)
        else:
            ui.error("IDが見つかりません")


def _edit_draft():
    draft_id = ui.prompt("編集する文案ID")
    draft = get_draft_by_id(draft_id)
    if not draft:
        ui.error("IDが見つかりません")
        return

    _print_draft(draft)

    choice = ui.menu("編集内容", [
        ("1", "本文を書き直す"),
        ("2", "ハッシュタグを変更"),
        ("3", "スロットを変更"),
        ("4", "ステータスを変更"),
        ("0", "キャンセル"),
    ])

    drafts = _load_drafts()

    if choice == "1":
        ui.info("新しい本文を入力 (空行で終了):")
        lines = []
        while True:
            line = input(f"  {ui.Color.WHITE}> {ui.Color.RESET}")
            if line == "":
                break
            lines.append(line)
        if lines:
            draft["body"] = "\n".join(lines)
            draft["char_count"] = len(draft["body"])
            draft["updated_at"] = ui.now_str()
            draft["status"] = "draft"  # 書き直したらdraftに戻す

    elif choice == "2":
        tags_raw = ui.prompt("ハッシュタグ", " ".join(draft.get("hashtags", [])))
        draft["hashtags"] = tags_raw.split() if tags_raw else []
        draft["updated_at"] = ui.now_str()

    elif choice == "3":
        slot = ui.menu("新しいスロット", [
            ("morning", "朝 (7:00)"),
            ("evening", "夕 (18:00)"),
            ("night",   "夜 (21:00)"),
            ("unset",   "未設定"),
        ])
        draft["slot"] = slot
        draft["updated_at"] = ui.now_str()

    elif choice == "4":
        new_status = ui.menu("新しいステータス", [
            ("draft",    "下書き"),
            ("review",   "校閲待ち"),
            ("approved", "承認済み"),
            ("rejected", "却下"),
        ])
        draft["status"] = new_status
        draft["updated_at"] = ui.now_str()

    if choice != "0":
        updated = [draft if d["id"] == draft_id else d for d in drafts]
        _save_drafts(updated)
        ui.success("文案を更新しました")


def _print_draft(draft: dict):
    ui.section(f"文案詳細: {draft['id']}")
    status_color = {"draft": ui.Color.DIM, "review": ui.Color.YELLOW,
                    "approved": ui.Color.GREEN, "rejected": ui.Color.RED}.get(draft["status"], "")
    print(f"  スロット: {SLOTS.get(draft['slot'], draft['slot'])}  ツリー#{draft.get('tree_no', 1)}")
    print(f"  テーマ  : {draft.get('brief_theme', '-')}")
    print(f"  状態    : {status_color}{draft['status']}{ui.Color.RESET}")
    print(f"  文字数  : {draft['char_count']} 字")
    if draft.get("quality_score") is not None:
        print(f"  品質スコア: {draft['quality_score']} / 100")
    print(f"\n  {ui.Color.BOLD}--- 本文 ---{ui.Color.RESET}")
    for line in draft["body"].split("\n"):
        print(f"  {line}")
    if draft.get("hashtags"):
        print(f"\n  {' '.join(draft['hashtags'])}")
    if draft.get("memo"):
        print(f"\n  メモ: {draft['memo']}")

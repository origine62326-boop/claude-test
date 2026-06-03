"""
Act (改善) モジュール - 結衣専用
課題・改善アクション管理。次サイクルへの引き継ぎ。
"""

import uuid

from modules import ui
from . import storage
from .plan import get_active_cycle, list_cycles, get_cycle_by_id


ACTIONS_FILE = "yui_actions.json"


def _load() -> list:
    return storage.load_list(ACTIONS_FILE)


def _save(data: list):
    storage.save_list(ACTIONS_FILE, data)


def get_actions_for_cycle(cycle_id: str) -> list:
    return [a for a in _load() if a.get("cycle_id") == cycle_id]


def run():
    ui.header("ACT - 改善", ui.Color.RED)

    while True:
        choice = ui.menu("Act メニュー", [
            ("1", "改善アクションを記録"),
            ("2", "サイクル振り返り"),
            ("3", "アクション一覧"),
            ("4", "次サイクルへ引き継ぎ"),
            ("0", "メインメニューに戻る"),
        ])

        if choice == "1":
            _record_action()
        elif choice == "2":
            _retrospective()
        elif choice == "3":
            _show_actions()
        elif choice == "4":
            _carry_over()
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


def _record_action():
    ui.section("改善アクションを記録")

    cycle = _select_cycle()
    if not cycle:
        return

    category = ui.menu("カテゴリ", [
        ("good",        "良かった点 (Keep)"),
        ("problem",     "課題・問題点 (Problem)"),
        ("try",         "次に試すこと (Try)"),
        ("worldbreak",  "世界観崩れの指摘"),
        ("idea",        "アイデア・気づき"),
    ])

    description = ui.prompt("内容")
    if not description:
        ui.error("内容は必須です")
        return

    priority = ui.menu("優先度", [
        ("high", "高"), ("medium", "中"), ("low", "低"),
    ])

    next_action = ui.prompt("具体的なアクション (任意)")
    due_date    = ui.prompt("期限 (YYYY-MM-DD, 任意)")

    action = {
        "id":          str(uuid.uuid4())[:8],
        "cycle_id":    cycle["id"],
        "cycle_name":  cycle["name"],
        "category":    category,
        "description": description,
        "priority":    priority,
        "next_action": next_action,
        "due_date":    due_date,
        "status":      "open",
        "created_at":  ui.now_str(),
    }

    actions = _load()
    actions.append(action)
    _save(actions)

    ui.success(f"アクションを記録しました (ID: {action['id']})")


def _retrospective():
    ui.section("サイクル振り返り")

    cycle = _select_cycle()
    if not cycle:
        return

    actions = get_actions_for_cycle(cycle["id"])

    categories = {
        "good":       ("良かった点 (Keep)",     ui.Color.GREEN),
        "problem":    ("課題・問題点 (Problem)", ui.Color.RED),
        "try":        ("次に試すこと (Try)",     ui.Color.CYAN),
        "worldbreak": ("世界観崩れ",            ui.Color.YELLOW),
        "idea":       ("アイデア・気づき",       ui.Color.BLUE),
    }

    print(f"\n{ui.Color.BOLD}=== 振り返り: {cycle['name']} ==={ui.Color.RESET}")

    for cat_key, (label, color) in categories.items():
        cat_actions = [a for a in actions if a["category"] == cat_key]
        print(f"\n{color}{ui.Color.BOLD}{label}{ui.Color.RESET}")
        if cat_actions:
            for a in cat_actions:
                mark = {"high": "!!!", "medium": "!!", "low": "!"}.get(a["priority"], "")
                print(f"  {mark} {a['description']}")
                if a.get("next_action"):
                    print(f"    → {a['next_action']}")
        else:
            print(f"  {ui.Color.DIM}(未記録){ui.Color.RESET}")

    add = ui.prompt("\n総括メモを追加しますか？ (y/n)", "n")
    if add.lower() == "y":
        memo = ui.prompt("総括メモ")
        if memo:
            action = {
                "id":          str(uuid.uuid4())[:8],
                "cycle_id":    cycle["id"],
                "cycle_name":  cycle["name"],
                "category":    "summary",
                "description": memo,
                "priority":    "medium",
                "next_action": "",
                "due_date":    "",
                "status":      "closed",
                "created_at":  ui.now_str(),
            }
            actions_all = _load()
            actions_all.append(action)
            _save(actions_all)
            ui.success("振り返りメモを保存しました")


def _show_actions():
    cycle = _select_cycle()
    if not cycle:
        return

    actions = get_actions_for_cycle(cycle["id"])
    if not actions:
        ui.info("改善アクションがありません")
        return

    icons = {"good": "✓", "problem": "✗", "try": "→", "worldbreak": "⚠", "idea": "★", "summary": "≡"}

    ui.section(f"改善アクション一覧: {cycle['name']}")
    rows = [
        [a["id"], icons.get(a["category"], "·"), a["description"][:32], a["priority"], a.get("status", "open")]
        for a in actions
    ]
    ui.table(["ID", "", "内容", "優先度", "状態"], rows, [10, 3, 34, 8, 8])

    uid = ui.prompt("\nステータスを更新するID (Enterでスキップ)")
    if uid:
        new_status = ui.menu("新しいステータス", [
            ("open", "未対応"), ("done", "完了"), ("wip", "対応中"), ("cancelled", "キャンセル"),
        ])
        all_actions = _load()
        for i, a in enumerate(all_actions):
            if a["id"] == uid:
                all_actions[i]["status"] = new_status
                break
        _save(all_actions)
        ui.success(f"ステータスを '{new_status}' に更新しました")


def _carry_over():
    ui.section("次サイクルへ引き継ぎ")

    current = _select_cycle()
    if not current:
        return

    open_actions = [a for a in get_actions_for_cycle(current["id"]) if a.get("status") in ("open", "wip")]
    if not open_actions:
        ui.info("未対応のアクションはありません")
        return

    print(f"\n  未対応アクション ({len(open_actions)}件):")
    for a in open_actions:
        print(f"  [{a['id']}] {a['description']}")

    cycles = list_cycles()
    for c in cycles:
        if c["id"] != current["id"]:
            print(f"  {ui.Color.CYAN}{c['id']}{ui.Color.RESET} - {c['name']}")

    next_cycle = get_cycle_by_id(ui.prompt("引き継ぎ先サイクルID"))
    if not next_cycle:
        ui.error("IDが見つかりません")
        return

    carried = 0
    all_actions = _load()
    for a in open_actions:
        carry = ui.prompt(f"  '{a['description'][:40]}' を引き継ぎますか？ (y/n)", "y")
        if carry.lower() == "y":
            all_actions.append({
                **a,
                "id":          str(uuid.uuid4())[:8],
                "cycle_id":    next_cycle["id"],
                "cycle_name":  next_cycle["name"],
                "description": f"[引継] {a['description']}",
                "status":      "open",
                "created_at":  ui.now_str(),
            })
            carried += 1

    _save(all_actions)
    ui.success(f"{carried} 件を '{next_cycle['name']}' に引き継ぎました")

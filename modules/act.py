"""
Act (改善) モジュール
PDCAサイクルの改善フェーズを管理する
- 課題・気づきの記録
- 改善アクションの設定
- 次サイクルへの引き継ぎ
- サイクルの振り返りまとめ
"""

import uuid

from . import storage, ui
from .plan import get_active_cycle, list_cycles, get_cycle_by_id


ACTIONS_FILE = "actions.json"


def _load_actions() -> list:
    return storage.load_list(ACTIONS_FILE)


def _save_actions(actions: list):
    storage.save_list(ACTIONS_FILE, actions)


def get_actions_for_cycle(cycle_id: str) -> list:
    return [a for a in _load_actions() if a.get("cycle_id") == cycle_id]


def run():
    ui.header("ACT - 改善", ui.Color.RED)

    while True:
        choice = ui.menu("Act メニュー", [
            ("1", "課題・改善アクションを記録"),
            ("2", "サイクルの振り返りをまとめる"),
            ("3", "改善アクション一覧"),
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


def _record_action():
    ui.section("課題・改善アクションを記録")

    cycle = _select_cycle()
    if not cycle:
        return

    category = ui.menu("カテゴリ", [
        ("good",    "良かった点 (Keep)"),
        ("problem", "課題・問題点 (Problem)"),
        ("try",     "次に試すこと (Try)"),
        ("idea",    "アイデア・気づき"),
    ])

    description = ui.prompt("内容")
    if not description:
        ui.error("内容は必須です")
        return

    priority = ui.menu("優先度", [
        ("high",   "高"),
        ("medium", "中"),
        ("low",    "低"),
    ])

    next_action = ui.prompt("具体的なアクション (任意)")
    due_date    = ui.prompt("期限 (YYYY-MM-DD, 任意)")

    action = {
        "id": str(uuid.uuid4())[:8],
        "cycle_id": cycle["id"],
        "cycle_name": cycle["name"],
        "category": category,
        "description": description,
        "priority": priority,
        "next_action": next_action,
        "due_date": due_date,
        "status": "open",
        "created_at": ui.now_str(),
    }

    actions = _load_actions()
    actions.append(action)
    _save_actions(actions)

    ui.success(f"アクションを記録しました (ID: {action['id']})")


def _retrospective():
    ui.section("サイクル振り返り")

    cycle = _select_cycle()
    if not cycle:
        return

    actions = get_actions_for_cycle(cycle["id"])

    # カテゴリ別に表示
    categories = {
        "good":    ("良かった点 (Keep)", ui.Color.GREEN),
        "problem": ("課題・問題点 (Problem)", ui.Color.RED),
        "try":     ("次に試すこと (Try)", ui.Color.CYAN),
        "idea":    ("アイデア・気づき", ui.Color.YELLOW),
    }

    print(f"\n{ui.Color.BOLD}=== 振り返り: {cycle['name']} ==={ui.Color.RESET}")

    for cat_key, (cat_label, color) in categories.items():
        cat_actions = [a for a in actions if a["category"] == cat_key]
        print(f"\n{color}{ui.Color.BOLD}{cat_label}{ui.Color.RESET}")
        if cat_actions:
            for a in cat_actions:
                priority_mark = {"high": "!!!", "medium": "!!", "low": "!"}.get(a["priority"], "")
                print(f"  {priority_mark} {a['description']}")
                if a.get("next_action"):
                    print(f"    → {a['next_action']}")
        else:
            print(f"  {ui.Color.DIM}(未記録){ui.Color.RESET}")

    # 振り返りメモ追加
    add_memo = ui.prompt("\n振り返りの総括メモを追加しますか？ (y/n)", "n")
    if add_memo.lower() == "y":
        memo = ui.prompt("総括メモ")
        if memo:
            action = {
                "id": str(uuid.uuid4())[:8],
                "cycle_id": cycle["id"],
                "cycle_name": cycle["name"],
                "category": "summary",
                "description": memo,
                "priority": "medium",
                "next_action": "",
                "due_date": "",
                "status": "closed",
                "created_at": ui.now_str(),
            }
            actions_all = _load_actions()
            actions_all.append(action)
            _save_actions(actions_all)
            ui.success("振り返りメモを保存しました")


def _show_actions():
    cycle = _select_cycle()
    if not cycle:
        return

    actions = get_actions_for_cycle(cycle["id"])
    if not actions:
        ui.info("改善アクションがありません")
        return

    cat_icons = {"good": "✓", "problem": "✗", "try": "→", "idea": "★", "summary": "≡"}
    priority_colors = {
        "high":   ui.Color.RED,
        "medium": ui.Color.YELLOW,
        "low":    ui.Color.DIM,
    }

    ui.section(f"改善アクション一覧: {cycle['name']}")
    rows = []
    for a in actions:
        icon  = cat_icons.get(a["category"], "·")
        pcolor = priority_colors.get(a["priority"], "")
        rows.append([
            a["id"],
            icon,
            a["description"][:30],
            a["priority"],
            a.get("status", "open"),
        ])

    ui.table(
        ["ID", "", "内容", "優先度", "状態"],
        rows,
        [10, 3, 32, 8, 8],
    )

    # ステータス更新
    update_id = ui.prompt("\nステータスを更新するID (Enterでスキップ)")
    if update_id:
        new_status = ui.menu("新しいステータス", [
            ("open",    "未対応"),
            ("done",    "完了"),
            ("wip",     "対応中"),
            ("cancelled", "キャンセル"),
        ])
        all_actions = _load_actions()
        for i, a in enumerate(all_actions):
            if a["id"] == update_id:
                all_actions[i]["status"] = new_status
                break
        _save_actions(all_actions)
        ui.success(f"ステータスを '{new_status}' に更新しました")


def _carry_over():
    ui.section("次サイクルへ引き継ぎ")

    ui.info("現在のサイクルの未完了アクションを確認します")
    current_cycle = _select_cycle()
    if not current_cycle:
        return

    open_actions = [a for a in get_actions_for_cycle(current_cycle["id"])
                    if a.get("status") in ("open", "wip")]

    if not open_actions:
        ui.info("未対応のアクションはありません")
        return

    print(f"\n  未対応アクション ({len(open_actions)}件):")
    for a in open_actions:
        print(f"  [{a['id']}] {a['description']}")

    ui.info("\n引き継ぎ先のサイクルを選択してください")
    cycles = list_cycles()
    for c in cycles:
        if c["id"] != current_cycle["id"]:
            print(f"  {ui.Color.CYAN}{c['id']}{ui.Color.RESET} - {c['name']}")

    next_id = ui.prompt("引き継ぎ先サイクルID")
    next_cycle = get_cycle_by_id(next_id)
    if not next_cycle:
        ui.error("IDが見つかりません")
        return

    carried = 0
    all_actions = _load_actions()
    for a in open_actions:
        carry = ui.prompt(f"  '{a['description'][:40]}' を引き継ぎますか？ (y/n)", "y")
        if carry.lower() == "y":
            new_action = {
                **a,
                "id": str(uuid.uuid4())[:8],
                "cycle_id": next_cycle["id"],
                "cycle_name": next_cycle["name"],
                "description": f"[引継] {a['description']}",
                "status": "open",
                "created_at": ui.now_str(),
            }
            all_actions.append(new_action)
            carried += 1

    _save_actions(all_actions)
    ui.success(f"{carried} 件のアクションを '{next_cycle['name']}' に引き継ぎました")

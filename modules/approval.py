"""
承認モジュール (あなたの承認)
品質チェック合格文案をレビューし承認/却下する
- 承認待ちリストの表示 (2〜3分で確認)
- 承認 / 却下 / 修正依頼
- 承認済みをスケジュールキューへ
"""

from . import storage, ui
from .writing import _load_drafts, _save_drafts, _print_draft, get_draft_by_id, SLOTS


def run():
    ui.header("APPROVAL - あなたの承認", ui.Color.YELLOW)
    print(f"  {ui.Color.DIM}通知が届いたら「承認」するだけ (目安 2〜3分){ui.Color.RESET}")

    while True:
        choice = ui.menu("Approvalメニュー", [
            ("1", "承認待ち一覧を確認"),
            ("2", "承認済み一覧"),
            ("0", "戻る"),
        ])

        if choice == "1":
            _review_pending()
        elif choice == "2":
            _show_approved()
        elif choice == "0":
            break


def _review_pending():
    drafts = _load_drafts()
    pending = [d for d in drafts if d["status"] == "review"]

    if not pending:
        ui.info("承認待ちの文案がありません")
        ui.info("先にQualityで品質チェックを通過させてください")
        return

    ui.section(f"承認待ち: {len(pending)} 件")

    for draft in pending:
        print(f"\n{'─' * 52}")
        print(f"  {ui.Color.BOLD}[{draft['id']}] スロット: {SLOTS.get(draft['slot'], draft['slot'])}  ツリー#{draft.get('tree_no',1)}{ui.Color.RESET}")
        print(f"  テーマ: {draft.get('brief_theme', '-')}  品質スコア: {draft.get('quality_score', '-')}/100")
        print()
        for line in draft["body"].split("\n"):
            print(f"  {line}")
        if draft.get("hashtags"):
            print(f"\n  {' '.join(draft['hashtags'])}")
        print(f"  文字数: {draft['char_count']} 字")

        action = ui.menu("判定", [
            ("a", "承認 (approve)"),
            ("r", "却下 (reject)"),
            ("s", "スキップ"),
            ("q", "ここで終了"),
        ])

        if action == "a":
            _update_status(draft["id"], "approved", drafts)
            ui.success(f"承認しました → スケジュールに追加されます")
        elif action == "r":
            reason = ui.prompt("却下理由 (任意)")
            _update_status(draft["id"], "rejected", drafts, reason)
            ui.error(f"却下しました")
        elif action == "s":
            continue
        elif action == "q":
            break

    _save_drafts(drafts)

    # 承認件数をサマリー表示
    approved_count = sum(1 for d in drafts if d["status"] == "approved")
    ui.section(f"承認済み合計: {approved_count} 件")


def _update_status(draft_id: str, new_status: str, drafts: list, note: str = ""):
    for d in drafts:
        if d["id"] == draft_id:
            d["status"] = new_status
            d["approved_at"] = ui.now_str() if new_status == "approved" else None
            if note:
                d["reject_reason"] = note
            break


def _show_approved():
    drafts = _load_drafts()
    approved = [d for d in drafts if d["status"] == "approved"]

    if not approved:
        ui.info("承認済みの文案がありません")
        return

    rows = [
        [
            d["id"],
            SLOTS.get(d["slot"], d["slot"])[:6],
            f"#{d.get('tree_no',1)}",
            d.get("brief_theme", "-")[:20],
            d.get("approved_at", "-")[:16] if d.get("approved_at") else "-",
        ]
        for d in approved
    ]
    ui.table(
        ["ID", "スロット", "ツリー", "テーマ", "承認日時"],
        rows,
        [10, 10, 7, 22, 18],
    )

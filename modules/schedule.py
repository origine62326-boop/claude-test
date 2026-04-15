"""
投稿スケジュール管理モジュール (ロン)
承認済み文案をThreads/X投稿スケジュールに登録・管理する
- 投稿時刻: 7:00 / 18:00 / 21:00
- ステータス: scheduled → posted → measured
- 24時間後に指標を計測するリマインダー表示
"""

import uuid
from datetime import datetime, timedelta

from . import storage, ui
from .writing import _load_drafts, _save_drafts, SLOTS


SCHEDULE_FILE = "schedule.json"

SLOT_TIMES = {
    "morning": "07:00",
    "evening": "18:00",
    "night":   "21:00",
    "unset":   "--:--",
}


def _load_schedule() -> list:
    return storage.load_list(SCHEDULE_FILE)


def _save_schedule(data: list):
    storage.save_list(SCHEDULE_FILE, data)


def run():
    ui.header("SCHEDULE - 投稿スケジュール [ロン]", ui.Color.CYAN)
    print(f"  {ui.Color.DIM}Threadsへ自動投稿 (7時・18時・21時) / 24時間後に指標を計測{ui.Color.RESET}")

    while True:
        choice = ui.menu("Scheduleメニュー", [
            ("1", "本日のスケジュールを確認"),
            ("2", "承認済み文案をスケジュールに登録"),
            ("3", "投稿完了をマークする"),
            ("4", "計測リマインダーを確認"),
            ("5", "スケジュール履歴"),
            ("0", "戻る"),
        ])

        if choice == "1":
            _show_today()
        elif choice == "2":
            _register_approved()
        elif choice == "3":
            _mark_posted()
        elif choice == "4":
            _check_reminders()
        elif choice == "5":
            _show_history()
        elif choice == "0":
            break


def _show_today():
    schedule = _load_schedule()
    today = ui.today_str()
    today_items = [s for s in schedule if s["post_date"] == today]

    ui.section(f"本日の投稿スケジュール ({today})")

    if not today_items:
        ui.info("本日のスケジュールがありません")
        return

    slot_order = {"morning": 0, "evening": 1, "night": 2, "unset": 3}
    sorted_items = sorted(today_items, key=lambda s: slot_order.get(s.get("slot", "unset"), 9))

    for item in sorted_items:
        time_str = SLOT_TIMES.get(item["slot"], "--:--")
        status = item["status"]
        status_color = {
            "scheduled": ui.Color.YELLOW,
            "posted":    ui.Color.GREEN,
            "measured":  ui.Color.DIM,
        }.get(status, "")

        print(f"\n  {ui.Color.BOLD}{time_str}{ui.Color.RESET}  [{item['id']}]  {status_color}{status}{ui.Color.RESET}")
        preview = item["body"][:60].replace("\n", " ")
        print(f"  {preview}...")
        if item.get("hashtags"):
            print(f"  {' '.join(item['hashtags'][:3])}")


def _register_approved():
    drafts = _load_drafts()
    approved = [d for d in drafts if d["status"] == "approved"]

    if not approved:
        ui.info("承認済みの文案がありません。Approvalで承認してください。")
        return

    # 既にスケジュール登録済みの文案IDセット
    schedule = _load_schedule()
    scheduled_draft_ids = {s["draft_id"] for s in schedule}
    unregistered = [d for d in approved if d["id"] not in scheduled_draft_ids]

    if not unregistered:
        ui.info("未登録の承認済み文案はありません")
        return

    ui.section(f"スケジュール登録 ({len(unregistered)} 件)")

    post_date = ui.prompt("投稿日 (YYYY-MM-DD)", ui.today_str())

    new_entries = []
    for draft in unregistered:
        time_str = SLOT_TIMES.get(draft["slot"], "--:--")
        print(f"\n  [{draft['id']}] {SLOTS.get(draft['slot'], draft['slot'])} {time_str}")
        print(f"  {draft['body'][:50].replace(chr(10),' ')}...")

        register = ui.prompt("スケジュールに登録しますか？ (y/n)", "y")
        if register.lower() != "y":
            continue

        # カスタム日時
        custom_date = ui.prompt(f"投稿日 (YYYY-MM-DD)", post_date)
        custom_time = ui.prompt(f"投稿時刻 (HH:MM)", time_str)

        entry = {
            "id": str(uuid.uuid4())[:8],
            "draft_id": draft["id"],
            "slot": draft["slot"],
            "post_date": custom_date,
            "post_time": custom_time,
            "body": draft["body"],
            "hashtags": draft.get("hashtags", []),
            "char_count": draft["char_count"],
            "brief_theme": draft.get("brief_theme", ""),
            "status": "scheduled",
            "posted_at": None,
            "measure_remind": False,
            "created_at": ui.now_str(),
        }
        new_entries.append(entry)
        ui.success(f"  登録: {custom_date} {custom_time}")

    if new_entries:
        schedule.extend(new_entries)
        _save_schedule(schedule)
        ui.success(f"\n{len(new_entries)} 件をスケジュールに登録しました")


def _mark_posted():
    schedule = _load_schedule()
    pending = [s for s in schedule if s["status"] == "scheduled"]

    if not pending:
        ui.info("投稿待ちのスケジュールがありません")
        return

    rows = [
        [s["id"], s["post_date"], s["post_time"],
         s["body"][:25].replace("\n", " ")]
        for s in pending
    ]
    ui.table(["ID", "日付", "時刻", "本文"], rows, [10, 12, 7, 27])

    entry_id = ui.prompt("投稿完了にするスケジュールID")
    entry = next((s for s in schedule if s["id"] == entry_id), None)
    if not entry:
        ui.error("IDが見つかりません")
        return

    actual_time = ui.prompt("実際の投稿日時 (YYYY-MM-DD HH:MM)", ui.now_str())
    url = ui.prompt("投稿URL (任意)")

    for s in schedule:
        if s["id"] == entry_id:
            s["status"] = "posted"
            s["posted_at"] = actual_time
            s["post_url"] = url
            # 24時間後の計測リマインダー
            try:
                dt = datetime.strptime(actual_time, "%Y-%m-%d %H:%M")
                s["measure_at"] = (dt + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
            except ValueError:
                s["measure_at"] = None
            break

    _save_schedule(schedule)
    ui.success(f"投稿完了をマークしました")
    ui.info(f"24時間後に指標計測リマインダーが表示されます")


def _check_reminders():
    schedule = _load_schedule()
    now = ui.now_str()
    remind_items = [
        s for s in schedule
        if s["status"] == "posted"
        and s.get("measure_at")
        and s["measure_at"] <= now
    ]

    if not remind_items:
        ui.info("計測リマインダーはありません")
        return

    ui.section(f"計測リマインダー: {len(remind_items)} 件")
    print(f"  {ui.Color.YELLOW}以下の投稿の指標をCheckモジュールで入力してください:{ui.Color.RESET}")

    for s in remind_items:
        print(f"\n  [{s['id']}] {s['posted_at']} に投稿")
        print(f"  {s['body'][:50].replace(chr(10),' ')}...")
        if s.get("post_url"):
            print(f"  URL: {s['post_url']}")

        done = ui.prompt("計測済みにしますか？ (y/n)", "n")
        if done.lower() == "y":
            for item in schedule:
                if item["id"] == s["id"]:
                    item["status"] = "measured"
                    break

    _save_schedule(schedule)


def _show_history():
    schedule = _load_schedule()
    if not schedule:
        ui.info("スケジュール履歴がありません")
        return

    rows = [
        [
            s["id"],
            s["post_date"],
            s["post_time"],
            s["status"],
            s["body"][:25].replace("\n", " "),
        ]
        for s in sorted(schedule, key=lambda x: x["post_date"], reverse=True)[:20]
    ]
    ui.table(
        ["ID", "日付", "時刻", "状態", "本文"],
        rows,
        [10, 12, 7, 10, 27],
    )

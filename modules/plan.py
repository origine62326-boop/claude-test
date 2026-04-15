"""
Plan (計画) モジュール
PDCAサイクルの計画フェーズを管理する
- サイクルの作成（週次/月次）
- KPI目標設定（フォロワー数、投稿数、エンゲージメント率）
- コンテンツテーマとハッシュタグ計画
"""

import uuid
from datetime import datetime

from . import storage, ui


CYCLES_FILE = "cycles.json"


def _load_cycles() -> list:
    return storage.load_list(CYCLES_FILE)


def _save_cycles(cycles: list):
    storage.save_list(CYCLES_FILE, cycles)


def get_active_cycle() -> dict | None:
    cycles = _load_cycles()
    today = ui.today_str()
    for c in cycles:
        if c["start_date"] <= today <= c["end_date"] and c["status"] == "active":
            return c
    return None


def get_cycle_by_id(cycle_id: str) -> dict | None:
    for c in _load_cycles():
        if c["id"] == cycle_id:
            return c
    return None


def list_cycles() -> list:
    return _load_cycles()


def run():
    ui.header("PLAN - 計画", ui.Color.BLUE)

    while True:
        choice = ui.menu("Plan メニュー", [
            ("1", "新しいPDCAサイクルを作成"),
            ("2", "ノクト設定で週次サイクルを素早く作成"),
            ("3", "サイクル一覧を表示"),
            ("4", "サイクルの目標を編集"),
            ("0", "メインメニューに戻る"),
        ])

        if choice == "1":
            _create_cycle()
        elif choice == "2":
            _create_noct_cycle()
        elif choice == "3":
            _show_cycles()
        elif choice == "4":
            _edit_cycle()
        elif choice == "0":
            break


def _create_noct_cycle():
    """ノクト (@noct_zero) のデフォルト設定で週次サイクルを素早く作成"""
    ui.section("ノクト週次サイクル - クイック作成")
    ui.info("@noct_zero のデフォルト設定で今週のサイクルを作成します")

    from datetime import timedelta
    today = ui.today_str()
    end   = (datetime.strptime(today, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")

    # 週番号を自動でサイクル名に
    dt   = datetime.strptime(today, "%Y-%m-%d")
    week = dt.isocalendar()[1]
    name = ui.prompt(f"サイクル名", f"{dt.year}年 第{week}週 週次運用")

    ui.section("KPI目標 (Enterで推奨値を使用)")
    target_posts       = ui.prompt_int("目標投稿数 (件/週)", 7)
    target_followers   = ui.prompt_int("目標フォロワー増加数", 10)
    target_impressions = ui.prompt_int("目標インプレッション合計", 5000)
    target_eng_rate    = ui.prompt_float("目標エンゲージメント率 (%)", 3.0)

    memo = ui.prompt("今週の戦略メモ (任意)")

    cycle = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "start_date": today,
        "end_date": end,
        "status": "active",
        "created_at": ui.now_str(),
        "goals": {
            "posts": target_posts,
            "followers_gain": target_followers,
            "impressions": target_impressions,
            "engagement_rate": target_eng_rate,
        },
        "content_plan": {
            "themes": ["リアル体験", "数字公開", "失敗→改善", "AI活用", "共感・応援"],
            "hashtags": ["#副業", "#工場勤務", "#AI活用", "#0から1", "#夜勤副業"],
        },
        "memo": memo,
    }

    cycles = _load_cycles()
    cycles.append(cycle)
    _save_cycles(cycles)

    ui.success(f"サイクル '{name}' を作成しました (ID: {cycle['id']})")
    _print_cycle(cycle)


def _create_cycle():
    ui.section("新しいPDCAサイクル作成")

    name = ui.prompt("サイクル名 (例: 2026年4月 週次運用)")
    if not name:
        ui.error("サイクル名は必須です")
        return

    period = ui.menu("期間タイプ", [
        ("1", "週次 (7日間)"),
        ("2", "月次 (30日間)"),
        ("3", "カスタム"),
    ])

    today = ui.today_str()
    if period == "1":
        from datetime import timedelta
        end = (datetime.strptime(today, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
        start_date, end_date = today, end
    elif period == "2":
        from datetime import timedelta
        end = (datetime.strptime(today, "%Y-%m-%d") + timedelta(days=29)).strftime("%Y-%m-%d")
        start_date, end_date = today, end
    else:
        start_date = ui.prompt("開始日 (YYYY-MM-DD)", today)
        end_date = ui.prompt("終了日 (YYYY-MM-DD)")

    ui.section("KPI目標を設定")
    target_posts       = ui.prompt_int("目標投稿数 (件/期間)", 7)
    target_followers   = ui.prompt_int("目標フォロワー増加数", 50)
    target_impressions = ui.prompt_int("目標インプレッション合計", 10000)
    target_eng_rate    = ui.prompt_float("目標エンゲージメント率 (%)", 3.0)

    ui.section("コンテンツ計画")
    themes_raw = ui.prompt("コンテンツテーマ (カンマ区切り, 例: 技術,日常,業界ニュース)")
    themes = [t.strip() for t in themes_raw.split(",") if t.strip()] if themes_raw else []

    hashtags_raw = ui.prompt("定番ハッシュタグ (カンマ区切り, 例: #AI,#エンジニア)")
    hashtags = [h.strip() for h in hashtags_raw.split(",") if h.strip()] if hashtags_raw else []

    memo = ui.prompt("メモ・戦略メモ (任意)")

    cycle = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "start_date": start_date,
        "end_date": end_date,
        "status": "active",
        "created_at": ui.now_str(),
        "goals": {
            "posts": target_posts,
            "followers_gain": target_followers,
            "impressions": target_impressions,
            "engagement_rate": target_eng_rate,
        },
        "content_plan": {
            "themes": themes,
            "hashtags": hashtags,
        },
        "memo": memo,
    }

    cycles = _load_cycles()
    cycles.append(cycle)
    _save_cycles(cycles)

    ui.success(f"サイクル '{name}' を作成しました (ID: {cycle['id']})")
    _print_cycle(cycle)


def _show_cycles():
    cycles = _load_cycles()
    if not cycles:
        ui.info("サイクルがありません。まず新しいサイクルを作成してください。")
        return

    ui.section("PDCAサイクル一覧")
    rows = []
    for c in cycles:
        status_label = {"active": "進行中", "completed": "完了", "cancelled": "中止"}.get(c["status"], c["status"])
        rows.append([
            c["id"],
            c["name"][:20],
            c["start_date"],
            c["end_date"],
            status_label,
        ])

    ui.table(
        ["ID", "サイクル名", "開始日", "終了日", "状態"],
        rows,
        [10, 22, 12, 12, 8],
    )

    show_detail = ui.prompt("\n詳細表示するID (Enterでスキップ)")
    if show_detail:
        cycle = get_cycle_by_id(show_detail)
        if cycle:
            _print_cycle(cycle)
        else:
            ui.error("IDが見つかりません")


def _edit_cycle():
    cycles = _load_cycles()
    if not cycles:
        ui.info("サイクルがありません")
        return

    cycle_id = ui.prompt("編集するサイクルID")
    cycle = get_cycle_by_id(cycle_id)
    if not cycle:
        ui.error("IDが見つかりません")
        return

    ui.section(f"サイクル '{cycle['name']}' を編集")
    choice = ui.menu("編集項目", [
        ("1", "KPI目標を更新"),
        ("2", "コンテンツ計画を更新"),
        ("3", "ステータスを変更"),
        ("0", "キャンセル"),
    ])

    if choice == "1":
        g = cycle["goals"]
        cycle["goals"]["posts"]           = ui.prompt_int("目標投稿数", g["posts"])
        cycle["goals"]["followers_gain"]  = ui.prompt_int("目標フォロワー増加数", g["followers_gain"])
        cycle["goals"]["impressions"]     = ui.prompt_int("目標インプレッション合計", g["impressions"])
        cycle["goals"]["engagement_rate"] = ui.prompt_float("目標エンゲージメント率 (%)", g["engagement_rate"])
        ui.success("KPI目標を更新しました")

    elif choice == "2":
        themes_raw = ui.prompt("コンテンツテーマ (カンマ区切り)", ",".join(cycle["content_plan"].get("themes", [])))
        hashtags_raw = ui.prompt("定番ハッシュタグ (カンマ区切り)", ",".join(cycle["content_plan"].get("hashtags", [])))
        cycle["content_plan"]["themes"]   = [t.strip() for t in themes_raw.split(",") if t.strip()]
        cycle["content_plan"]["hashtags"] = [h.strip() for h in hashtags_raw.split(",") if h.strip()]
        ui.success("コンテンツ計画を更新しました")

    elif choice == "3":
        new_status = ui.menu("新しいステータス", [
            ("active", "進行中"),
            ("completed", "完了"),
            ("cancelled", "中止"),
        ])
        cycle["status"] = new_status
        ui.success(f"ステータスを '{new_status}' に変更しました")

    if choice != "0":
        updated = [cycle if c["id"] == cycle_id else c for c in cycles]
        _save_cycles(updated)


def _print_cycle(cycle: dict):
    ui.section(f"サイクル詳細: {cycle['name']}")
    g = cycle["goals"]
    cp = cycle["content_plan"]
    print(f"  ID          : {cycle['id']}")
    print(f"  期間        : {cycle['start_date']} ~ {cycle['end_date']}")
    print(f"  ステータス  : {cycle['status']}")
    print(f"  目標投稿数  : {g.get('posts', '-')} 件")
    print(f"  フォロワー増: {g.get('followers_gain', '-')} 人")
    print(f"  インプレッション: {g.get('impressions', '-'):,}")
    print(f"  エンゲージ率: {g.get('engagement_rate', '-')} %")
    if cp.get("themes"):
        print(f"  テーマ      : {', '.join(cp['themes'])}")
    if cp.get("hashtags"):
        print(f"  ハッシュタグ: {', '.join(cp['hashtags'])}")
    if cycle.get("memo"):
        print(f"  メモ        : {cycle['memo']}")

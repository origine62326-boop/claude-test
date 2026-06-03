"""
Plan (計画) モジュール - 結衣専用
PDCAサイクルと KPI を管理する。
KPI 設計:
  30日テスト: 投稿100本・フォロワー300
  90日フェーズ2: フォロワー1000
  180日フェーズ3: フォロワー5000
"""

import uuid
from datetime import datetime, timedelta

from modules import ui
from . import storage


CYCLES_FILE = "yui_cycles.json"


def _load() -> list:
    return storage.load_list(CYCLES_FILE)


def _save(data: list):
    storage.save_list(CYCLES_FILE, data)


def get_active_cycle() -> dict | None:
    today = ui.today_str()
    for c in _load():
        if c["start_date"] <= today <= c["end_date"] and c["status"] == "active":
            return c
    return None


def get_cycle_by_id(cid: str) -> dict | None:
    return next((c for c in _load() if c["id"] == cid), None)


def list_cycles() -> list:
    return _load()


def run():
    ui.header("PLAN - 計画", ui.Color.BLUE)

    while True:
        choice = ui.menu("Plan メニュー", [
            ("1", "30日テストサイクルをクイック作成"),
            ("2", "カスタムサイクルを作成"),
            ("3", "サイクル一覧"),
            ("4", "目標KPIを編集"),
            ("0", "メインメニューに戻る"),
        ])

        if choice == "1":
            _create_30day_test()
        elif choice == "2":
            _create_custom()
        elif choice == "3":
            _show_cycles()
        elif choice == "4":
            _edit_cycle()
        elif choice == "0":
            break


def _create_30day_test():
    ui.section("30日テストサイクル - クイック作成")
    ui.info("「夜勤帰りの孤独女子」世界観の仮説検証サイクルです")
    ui.info("目標: 投稿100本 / フォロワー300 / 世界観の確立")

    today = ui.today_str()
    end = (datetime.strptime(today, "%Y-%m-%d") + timedelta(days=29)).strftime("%Y-%m-%d")

    name = ui.prompt("サイクル名", f"30日テスト_{today[:7]}")

    ui.section("KPI目標 (Enterで推奨値)")
    target_posts     = ui.prompt_int("目標投稿数 (件/30日)", 100)
    target_followers = ui.prompt_int("目標フォロワー数 (到達目標)", 300)
    target_imp       = ui.prompt_int("目標インプレッション合計", 50000)
    target_eng       = ui.prompt_float("目標エンゲージメント率 (%)", 2.0)
    target_dmm_ctr   = ui.prompt_float("目標DMM CTR (%, DMMポスト対比)", 3.0)

    memo = ui.prompt("テスト仮説・戦略メモ (任意)",
                     "夜勤帰り孤独女子×物語×淡い恋愛で差別化85点を実証する")

    cycle = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "phase": "test30",
        "start_date": today,
        "end_date": end,
        "status": "active",
        "created_at": ui.now_str(),
        "goals": {
            "posts":           target_posts,
            "followers_total": target_followers,
            "impressions":     target_imp,
            "engagement_rate": target_eng,
            "dmm_ctr":         target_dmm_ctr,
            "ratio_daily":     70,
            "ratio_love":      20,
            "ratio_dmm":       10,
        },
        "content_plan": {
            "themes":    ["夜勤帰り", "コンビニ朝帰り", "孤独と温かさ", "淡い恋愛", "DMM導線"],
            "hashtags":  ["#夜勤", "#夜勤あるある", "#工場勤務", "#一人暮らし", "#深夜"],
            "fixed_post": "朝5時。みんなが出勤する頃に私は帰宅。コンビニのカフェラテ飲みながら寝る準備してます。同じような人いたら仲良くしてください☕",
        },
        "memo": memo,
    }

    cycles = _load()
    cycles.append(cycle)
    _save(cycles)

    ui.success(f"サイクル '{name}' を作成しました (ID: {cycle['id']})")
    _print_cycle(cycle)


def _create_custom():
    ui.section("カスタムサイクル作成")

    name = ui.prompt("サイクル名")
    if not name:
        ui.error("サイクル名は必須です")
        return

    phase = ui.menu("フェーズ", [
        ("test30",  "30日テスト (仮説検証)"),
        ("phase2",  "Phase2 (フォロワー1000目標)"),
        ("phase3",  "Phase3 (フォロワー5000目標)"),
        ("weekly",  "週次サイクル"),
    ])

    today = ui.today_str()
    period = ui.menu("期間", [
        ("1", "7日間"),
        ("2", "30日間"),
        ("3", "90日間"),
        ("4", "カスタム"),
    ])

    days_map = {"1": 6, "2": 29, "3": 89}
    if period in days_map:
        end = (datetime.strptime(today, "%Y-%m-%d") + timedelta(days=days_map[period])).strftime("%Y-%m-%d")
        start_date, end_date = today, end
    else:
        start_date = ui.prompt("開始日 (YYYY-MM-DD)", today)
        end_date   = ui.prompt("終了日 (YYYY-MM-DD)")

    ui.section("KPI目標")
    target_posts     = ui.prompt_int("目標投稿数", 30)
    target_followers = ui.prompt_int("目標フォロワー数 (到達目標)", 300)
    target_imp       = ui.prompt_int("目標インプレッション合計", 30000)
    target_eng       = ui.prompt_float("目標エンゲージメント率 (%)", 2.0)
    target_dmm_ctr   = ui.prompt_float("目標DMM CTR (%)", 3.0)

    memo = ui.prompt("メモ (任意)")

    cycle = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "phase": phase,
        "start_date": start_date,
        "end_date": end_date,
        "status": "active",
        "created_at": ui.now_str(),
        "goals": {
            "posts":           target_posts,
            "followers_total": target_followers,
            "impressions":     target_imp,
            "engagement_rate": target_eng,
            "dmm_ctr":         target_dmm_ctr,
            "ratio_daily":     70,
            "ratio_love":      20,
            "ratio_dmm":       10,
        },
        "content_plan": {
            "themes":   ["夜勤帰り", "孤独と温かさ", "淡い恋愛", "DMM導線"],
            "hashtags": ["#夜勤", "#夜勤あるある", "#工場勤務", "#一人暮らし"],
        },
        "memo": memo,
    }

    cycles = _load()
    cycles.append(cycle)
    _save(cycles)

    ui.success(f"サイクル '{name}' を作成しました (ID: {cycle['id']})")
    _print_cycle(cycle)


def _show_cycles():
    cycles = _load()
    if not cycles:
        ui.info("サイクルがありません。30日テストサイクルを作成してください。")
        return

    ui.section("サイクル一覧")
    rows = []
    for c in cycles:
        status_label = {"active": "進行中", "completed": "完了", "cancelled": "中止"}.get(c["status"], c["status"])
        rows.append([c["id"], c["name"][:22], c["start_date"], c["end_date"], status_label])
    ui.table(["ID", "サイクル名", "開始日", "終了日", "状態"], rows, [10, 24, 12, 12, 8])

    cid = ui.prompt("\n詳細表示するID (Enterでスキップ)")
    if cid:
        c = get_cycle_by_id(cid)
        if c:
            _print_cycle(c)
        else:
            ui.error("IDが見つかりません")


def _edit_cycle():
    cycles = _load()
    if not cycles:
        ui.info("サイクルがありません")
        return

    cid = ui.prompt("編集するサイクルID")
    cycle = get_cycle_by_id(cid)
    if not cycle:
        ui.error("IDが見つかりません")
        return

    choice = ui.menu(f"'{cycle['name']}' の編集", [
        ("1", "KPI目標を更新"),
        ("2", "ステータスを変更"),
        ("0", "キャンセル"),
    ])

    if choice == "1":
        g = cycle["goals"]
        cycle["goals"]["posts"]           = ui.prompt_int("目標投稿数", g["posts"])
        cycle["goals"]["followers_total"] = ui.prompt_int("目標フォロワー数", g["followers_total"])
        cycle["goals"]["impressions"]     = ui.prompt_int("目標インプレッション", g["impressions"])
        cycle["goals"]["engagement_rate"] = ui.prompt_float("目標エンゲージ率 (%)", g["engagement_rate"])
        cycle["goals"]["dmm_ctr"]         = ui.prompt_float("目標DMM CTR (%)", g.get("dmm_ctr", 3.0))
        ui.success("KPI目標を更新しました")

    elif choice == "2":
        new_status = ui.menu("新しいステータス", [
            ("active", "進行中"), ("completed", "完了"), ("cancelled", "中止"),
        ])
        cycle["status"] = new_status
        ui.success(f"ステータスを '{new_status}' に変更しました")

    if choice != "0":
        updated = [cycle if c["id"] == cid else c for c in cycles]
        _save(updated)


def _print_cycle(cycle: dict):
    g  = cycle["goals"]
    cp = cycle.get("content_plan", {})
    ui.section(f"サイクル詳細: {cycle['name']}")
    print(f"  ID          : {cycle['id']}")
    print(f"  フェーズ    : {cycle.get('phase', '-')}")
    print(f"  期間        : {cycle['start_date']} ~ {cycle['end_date']}")
    print(f"  ステータス  : {cycle['status']}")
    print(f"  目標投稿数  : {g.get('posts', '-')} 件")
    print(f"  目標フォロワー: {g.get('followers_total', '-')} 人")
    print(f"  目標インプレ: {g.get('impressions', 0):,}")
    print(f"  目標エンゲジ: {g.get('engagement_rate', '-')} %")
    print(f"  目標DMMCTR  : {g.get('dmm_ctr', '-')} %")
    print(f"  投稿比率目標: 日常{g.get('ratio_daily',70)}% / 恋愛{g.get('ratio_love',20)}% / DMM{g.get('ratio_dmm',10)}%")
    if cp.get("themes"):
        print(f"  テーマ      : {', '.join(cp['themes'])}")
    if cp.get("hashtags"):
        print(f"  ハッシュタグ: {', '.join(cp['hashtags'])}")
    if cycle.get("memo"):
        print(f"  仮説メモ    : {cycle['memo']}")

"""
エージェントパイプライン（ホグワーツ）
========================================
コンテンツ制作フローを管理するモジュール。

各エージェントの役割:
  ハーマイオニー  リサーチ・分析（テーマ・ブリーフィング生成）
  ルーナ          ライティング（投稿案作成）
  マルフォイ      校閲・品質チェック
  あなたの承認    承認ステップ（2〜3分）
  ロン            投稿・計測管理
  スネイプ        全体監視・改善提案
"""

import uuid
from . import storage, ui
from .plan import get_active_cycle
from .do import CONTENT_CATEGORIES, HOOK_TYPES, CATEGORY_LABEL, HOOK_LABEL

PIPELINE_FILE = "pipeline.json"

# 品質チェック項目（マルフォイ）
QUALITY_CHECKS = [
    ("voice",    "ノクトらしい声・語尾になっている"),
    ("hook",     "冒頭にフックがある（数字・共感・衝撃など）"),
    ("concrete", "具体的な数字や体験が入っている"),
    ("empathy",  "読者が「自分も」と共感できる内容"),
    ("length",   "投稿として適切な長さ（長すぎない）"),
    ("readable", "空白・改行が読みやすい"),
]

STATUS_LABEL = {
    "draft":     "草稿",
    "checked":   "チェック済",
    "approved":  "承認済",
    "published": "投稿済",
    "rejected":  "要修正",
}

STATUS_COLOR = {
    "draft":     ui.Color.DIM,
    "checked":   ui.Color.CYAN,
    "approved":  ui.Color.GREEN,
    "published": ui.Color.BLUE,
    "rejected":  ui.Color.RED,
}

POST_TIMES = ["07:00", "12:00", "18:00", "21:00", "23:00"]


def _load() -> list:
    return storage.load_list(PIPELINE_FILE)


def _save(data: list):
    storage.save_list(PIPELINE_FILE, data)


def _today_session() -> dict | None:
    today = ui.today_str()
    for s in _load():
        if s.get("date") == today:
            return s
    return None


def _get_all_drafts() -> list:
    drafts = []
    for s in _load():
        for d in s.get("drafts", []):
            d["_date"] = s.get("date", "")
            d["_theme"] = s.get("theme", "")
            drafts.append(d)
    return drafts


def run():
    ui.header("FLOW - エージェントパイプライン", ui.Color.YELLOW)
    print(f"  {ui.Color.DIM}ハーマイオニー → ルーナ → マルフォイ → 承認 → ロン{ui.Color.RESET}\n")

    # 今日のステータスを簡易表示
    session = _today_session()
    if session:
        drafts = session.get("drafts", [])
        counts = {}
        for d in drafts:
            s = d.get("status", "draft")
            counts[s] = counts.get(s, 0) + 1
        parts = [f"{STATUS_LABEL.get(s,'?')}:{n}" for s, n in counts.items()]
        print(f"  今日の進捗: {' / '.join(parts) if parts else 'まだ投稿案なし'}")
        print(f"  テーマ: {session.get('theme', '未設定')}\n")
    else:
        print(f"  {ui.Color.YELLOW}今日のブリーフィングがまだありません{ui.Color.RESET}\n")

    while True:
        choice = ui.menu("Pipeline メニュー", [
            ("1", "ハーマイオニー  リサーチ・ブリーフィング作成"),
            ("2", "ルーナ          投稿案を作成"),
            ("3", "マルフォイ      品質チェック"),
            ("4", "あなたの承認    承認キューを確認"),
            ("5", "ロン            投稿スケジュール管理"),
            ("6", "スネイプ        パイプライン全体監視"),
            ("0", "メインメニューに戻る"),
        ])

        if choice == "1":
            _hermione()
        elif choice == "2":
            _luna()
        elif choice == "3":
            _malfoy()
        elif choice == "4":
            _approval()
        elif choice == "5":
            _ron()
        elif choice == "6":
            _snape()
        elif choice == "0":
            break


# ─────────────────────────────────────────
# ハーマイオニー: リサーチ・ブリーフィング
# ─────────────────────────────────────────
def _hermione():
    ui.header("ハーマイオニー - リサーチ・分析", ui.Color.CYAN)
    print(f"  {ui.Color.DIM}今日のテーマとブリーフィングを作成します{ui.Color.RESET}\n")

    today = ui.today_str()
    sessions = _load()

    # 既存セッションチェック
    existing = next((s for s in sessions if s.get("date") == today), None)
    if existing:
        ui.info(f"今日のブリーフィングは既に作成済みです")
        ui.info(f"テーマ: {existing.get('theme', '未設定')}")
        overwrite = ui.prompt("上書きしますか？ (y/n)", "n")
        if overwrite.lower() != "y":
            return
        sessions = [s for s in sessions if s.get("date") != today]

    ui.section("今日のテーマを設定")
    theme = ui.prompt("今日の発信テーマ（例: 夜勤明けのAI活用記録）")
    if not theme:
        ui.error("テーマは必須です")
        return

    ui.section("リサーチインプット（自分の体験・気づきを入力）")
    print(f"  {ui.Color.DIM}箇条書きでOK。AIへの指示のように書く必要はありません。{ui.Color.RESET}")
    experience = ui.prompt("今日の体験・出来事（任意）")
    numbers    = ui.prompt("出せる数字があれば（インプレ・時間・金額など）（任意）")
    emotion    = ui.prompt("今の気持ち・感情（任意）")
    news       = ui.prompt("関連するニュース・トレンド（任意）")

    active = get_active_cycle()
    cycle_id = active["id"] if active else ""

    session = {
        "id":         str(uuid.uuid4())[:8],
        "date":       today,
        "cycle_id":   cycle_id,
        "theme":      theme,
        "research": {
            "experience": experience,
            "numbers":    numbers,
            "emotion":    emotion,
            "news":       news,
        },
        "drafts": [],
        "created_at": ui.now_str(),
    }

    sessions.append(session)
    _save(sessions)
    ui.success(f"ブリーフィングを作成しました")
    ui.info(f"テーマ: {theme}")
    ui.info("次: ルーナで投稿案を作成してください")


# ─────────────────────────────────────────
# ルーナ: ライティング
# ─────────────────────────────────────────
def _luna():
    ui.header("ルーナ - ライティング", ui.Color.GREEN)
    print(f"  {ui.Color.DIM}投稿案を作成します（1日3スロット）{ui.Color.RESET}\n")

    session = _today_session()
    if not session:
        ui.error("先にハーマイオニーでブリーフィングを作成してください")
        return

    ui.info(f"テーマ: {session['theme']}")
    r = session.get("research", {})
    if r.get("experience"):
        ui.info(f"体験: {r['experience'][:50]}")
    if r.get("numbers"):
        ui.info(f"数字: {r['numbers']}")

    existing_drafts = session.get("drafts", [])
    if existing_drafts:
        ui.info(f"既存の投稿案: {len(existing_drafts)}件")

    ui.section("新しい投稿案を作成")

    content = ui.prompt("投稿内容（本文）")
    if not content:
        ui.error("投稿内容は必須です")
        return

    content_category = ui.menu("コンテンツカテゴリ", CONTENT_CATEGORIES)
    hook_type        = ui.menu("フックタイプ", HOOK_TYPES)

    post_time = ui.menu("投稿予定時刻", [(t, t) for t in POST_TIMES])
    memo      = ui.prompt("メモ（任意）")

    draft = {
        "id":               str(uuid.uuid4())[:8],
        "content":          content,
        "content_category": content_category,
        "hook_type":        hook_type,
        "post_time":        post_time,
        "status":           "draft",
        "memo":             memo,
        "check_results":    {},
        "check_notes":      "",
        "approved_at":      "",
        "published_at":     "",
        "created_at":       ui.now_str(),
    }

    sessions = _load()
    for s in sessions:
        if s["id"] == session["id"]:
            s.setdefault("drafts", []).append(draft)
            break
    _save(sessions)

    ui.success(f"投稿案を作成しました (ID: {draft['id']})")
    ui.info(f"スロット {post_time} / {CATEGORY_LABEL.get(content_category, content_category)}")
    ui.info("次: マルフォイで品質チェックをしてください")


# ─────────────────────────────────────────
# マルフォイ: 校閲・品質チェック
# ─────────────────────────────────────────
def _malfoy():
    ui.header("マルフォイ - 校閲・品質チェック", ui.Color.RED)
    print(f"  {ui.Color.DIM}語尾・構成・声の定義を基準に審査します{ui.Color.RESET}\n")

    drafts = [d for d in _get_all_drafts() if d.get("status") == "draft"]
    if not drafts:
        ui.info("チェック待ちの投稿案がありません")
        return

    ui.section("チェック待ちの投稿案")
    for d in drafts:
        print(f"  {ui.Color.CYAN}{d['id']}{ui.Color.RESET}  [{d.get('_date','')}]  {d['content'][:35]}")

    draft_id = ui.prompt("\nチェックする投稿案ID")
    target   = next((d for d in drafts if d["id"] == draft_id), None)
    if not target:
        ui.error("IDが見つかりません")
        return

    ui.section("投稿内容")
    print(f"\n{ui.Color.WHITE}{target['content']}{ui.Color.RESET}\n")
    print(f"  カテゴリ: {CATEGORY_LABEL.get(target.get('content_category',''), '-')}")
    print(f"  フック  : {HOOK_LABEL.get(target.get('hook_type',''), '-')}\n")

    ui.section("品質チェック（y=合格 / n=不合格）")
    results = {}
    passed  = 0
    for key, label in QUALITY_CHECKS:
        ans = ui.prompt(f"  {label}", "y")
        results[key] = ans.lower() == "y"
        if results[key]:
            passed += 1

    total  = len(QUALITY_CHECKS)
    score  = round(passed / total * 100)
    color  = ui.Color.GREEN if score >= 80 else (ui.Color.YELLOW if score >= 60 else ui.Color.RED)
    print(f"\n  品質スコア: {color}{score}% ({passed}/{total}){ui.Color.RESET}")

    notes = ui.prompt("マルフォイのコメント（改善点など）")

    if score >= 80:
        new_status = "checked"
        ui.success("合格！承認キューに進みます")
    else:
        retry = ui.prompt("再修正に戻しますか？ (y=要修正 / n=強制合格)", "y")
        new_status = "rejected" if retry.lower() == "y" else "checked"
        if new_status == "rejected":
            ui.info("要修正としてルーナに差し戻しました")
        else:
            ui.info("強制合格にしました")

    # データ更新
    sessions = _load()
    for s in sessions:
        for d in s.get("drafts", []):
            if d["id"] == draft_id:
                d["status"]        = new_status
                d["check_results"] = results
                d["check_notes"]   = notes
                break
    _save(sessions)


# ─────────────────────────────────────────
# 承認: あなたの承認
# ─────────────────────────────────────────
def _approval():
    ui.header("あなたの承認", ui.Color.YELLOW)
    print(f"  {ui.Color.DIM}2〜3分で確認 → 「承認」コメントするだけ{ui.Color.RESET}\n")

    drafts = [d for d in _get_all_drafts() if d.get("status") == "checked"]
    if not drafts:
        ui.info("承認待ちの投稿案がありません")
        ui.info("先にマルフォイで品質チェックを完了させてください")
        return

    ui.section(f"承認待ち {len(drafts)}件")
    for d in drafts:
        cat_label  = CATEGORY_LABEL.get(d.get("content_category", ""), "-")
        hook_label = HOOK_LABEL.get(d.get("hook_type", ""), "-")
        print(f"\n  {ui.Color.CYAN}ID: {d['id']}{ui.Color.RESET}  {d.get('_date','')} {d.get('post_time','')}")
        print(f"  {ui.Color.WHITE}{d['content']}{ui.Color.RESET}")
        print(f"  {ui.Color.DIM}カテゴリ: {cat_label} / フック: {hook_label}{ui.Color.RESET}")
        if d.get("check_notes"):
            print(f"  {ui.Color.DIM}マルフォイ: {d['check_notes']}{ui.Color.RESET}")

        ans = ui.menu(f"  ID:{d['id']} の判断", [
            ("approve", "承認する"),
            ("reject",  "差し戻す"),
            ("skip",    "あとで決める"),
        ])

        if ans in ("approve", "reject"):
            new_status = "approved" if ans == "approve" else "rejected"
            sessions   = _load()
            for s in sessions:
                for dr in s.get("drafts", []):
                    if dr["id"] == d["id"]:
                        dr["status"]      = new_status
                        dr["approved_at"] = ui.now_str() if new_status == "approved" else ""
                        break
            _save(sessions)
            label = ui.Color.GREEN + "承認しました" if new_status == "approved" else ui.Color.RED + "差し戻しました"
            print(f"  {label}{ui.Color.RESET}")


# ─────────────────────────────────────────
# ロン: 投稿・計測管理
# ─────────────────────────────────────────
def _ron():
    ui.header("ロン - 投稿・計測管理", ui.Color.BLUE)
    print(f"  {ui.Color.DIM}承認済み投稿のスケジュール確認と投稿完了マーク{ui.Color.RESET}\n")

    approved = [d for d in _get_all_drafts() if d.get("status") == "approved"]
    published = [d for d in _get_all_drafts() if d.get("status") == "published"]

    ui.section("投稿スケジュール（承認済み）")
    if not approved:
        ui.info("承認済みの投稿案がありません")
    else:
        sorted_approved = sorted(approved, key=lambda d: (d.get("_date", ""), d.get("post_time", "")))
        for d in sorted_approved:
            cat = CATEGORY_LABEL.get(d.get("content_category", ""), "-")
            print(f"  {ui.Color.GREEN}[{d.get('_date','')} {d.get('post_time','')}]{ui.Color.RESET}  {d['id']}")
            print(f"    {d['content'][:50]}")
            print(f"    {ui.Color.DIM}{cat}{ui.Color.RESET}")

    if approved:
        ui.section("投稿完了マーク")
        done_id = ui.prompt("投稿済みにするID（Enterでスキップ）")
        if done_id:
            sessions = _load()
            found    = False
            for s in sessions:
                for d in s.get("drafts", []):
                    if d["id"] == done_id and d["status"] == "approved":
                        d["status"]       = "published"
                        d["published_at"] = ui.now_str()
                        found = True
                        break
            if found:
                _save(sessions)
                ui.success("投稿済みにしました")
                ui.info("Doモジュールでも投稿ログを記録してください")
            else:
                ui.error("IDが見つからないか承認済みでありません")

    ui.section(f"投稿済み {len(published)}件（直近5件）")
    for d in published[-5:]:
        print(f"  {ui.Color.DIM}[{d.get('published_at', d.get('_date',''))}]{ui.Color.RESET}  {d['content'][:45]}")


# ─────────────────────────────────────────
# スネイプ: 全体監視
# ─────────────────────────────────────────
def _snape():
    ui.header("スネイプ - パイプライン全体監視", ui.Color.RED)
    print(f"  {ui.Color.DIM}全体を定期監視・品質チェック・改善提案を生成{ui.Color.RESET}\n")

    all_drafts = _get_all_drafts()
    total      = len(all_drafts)

    if total == 0:
        ui.info("データがありません。まずハーマイオニーからスタートしてください。")
        return

    # ステータス別集計
    ui.section("パイプライン全体ステータス")
    status_counts: dict[str, int] = {}
    for d in all_drafts:
        s = d.get("status", "draft")
        status_counts[s] = status_counts.get(s, 0) + 1

    for status, count in status_counts.items():
        color = STATUS_COLOR.get(status, "")
        label = STATUS_LABEL.get(status, status)
        bar   = "█" * count
        print(f"  {color}{label:8}{ui.Color.RESET} : {bar} ({count}件)")

    # 品質スコア分析
    checked = [d for d in all_drafts if d.get("check_results")]
    if checked:
        ui.section("品質チェック分析")
        key_pass: dict[str, int] = {}
        for d in checked:
            for k, v in d.get("check_results", {}).items():
                if v:
                    key_pass[k] = key_pass.get(k, 0) + 1

        total_checked = len(checked)
        print(f"  チェック済み投稿数: {total_checked}件\n")
        weak_points = []
        for key, label in QUALITY_CHECKS:
            passed = key_pass.get(key, 0)
            pct    = round(passed / total_checked * 100)
            color  = ui.Color.GREEN if pct >= 80 else (ui.Color.YELLOW if pct >= 60 else ui.Color.RED)
            bar    = "█" * (pct // 10) + "░" * (10 - pct // 10)
            print(f"  {label[:22]:22} {color}{bar}{ui.Color.RESET} {pct}%")
            if pct < 70:
                weak_points.append(label)

        # 改善提案
        if weak_points:
            ui.section("スネイプの改善提案")
            suggestions = {
                "ノクトらしい声・語尾になっている": "→ 投稿前に「俺ならこう言う？」と自分に問いかけてみてください",
                "冒頭にフックがある（数字・共感・衝撃など）": "→ 1行目だけ書き直す練習を毎日1投稿でやってみてください",
                "具体的な数字や体験が入っている": "→ 「なんとなく」を「○時間」「○円」「○日目」に変えてください",
                "読者が「自分も」と共感できる内容": "→ 「自分の話」ではなく「読者も経験する話」になってるか確認",
                "投稿として適切な長さ（長すぎない）": "→ スマホ1画面に収まるか目視確認してください",
                "空白・改行が読みやすい": "→ 3行以上続いたら改行を入れるルールを徹底してください",
            }
            for wp in weak_points:
                print(f"  {ui.Color.RED}弱点:{ui.Color.RESET} {wp}")
                print(f"         {suggestions.get(wp, '')}\n")

    # 今日の進捗チェック
    today   = ui.today_str()
    session = _today_session()
    ui.section("今日のチェック")
    if not session:
        print(f"  {ui.Color.RED}NG{ui.Color.RESET} 今日のブリーフィングがありません → ハーマイオニーへ")
    else:
        today_drafts = session.get("drafts", [])
        approved_today = [d for d in today_drafts if d["status"] in ("approved", "published")]
        print(f"  テーマ設定    : {ui.Color.GREEN}OK{ui.Color.RESET}  {session['theme']}")
        print(f"  投稿案作成数  : {len(today_drafts)} 件")
        print(f"  承認済み      : {len(approved_today)} 件")
        if len(today_drafts) < 3:
            print(f"  {ui.Color.YELLOW}→ 目標3投稿まであと{3 - len(today_drafts)}件{ui.Color.RESET}")

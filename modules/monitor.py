"""
監視モジュール (スネイプ)
全体を定期監視し、品質・重複・異常を検出して改善提案を生成する
- 重複チェック: 類似投稿の検出 (キーワード一致)
- 品質統計監視: スコア推移・合格率アラート
- 改善提案の自動生成
- パイプライン全体の状態サマリー
"""

from collections import Counter

from . import storage, ui
from .writing  import _load_drafts
from .quality  import _load_quality_logs, _load_voice_def
from .schedule import _load_schedule
from .check    import get_metrics_for_cycle, _load_followers
from .plan     import get_active_cycle, list_cycles
from .research import _load_briefs, _load_neta
from .act      import get_actions_for_cycle


SUGGESTIONS_FILE = "suggestions.json"


def _load_suggestions() -> list:
    return storage.load_list(SUGGESTIONS_FILE)


def _save_suggestions(data: list):
    storage.save_list(SUGGESTIONS_FILE, data)


def run():
    ui.header("MONITOR - 監視 [スネイプ]", ui.Color.RED)
    print(f"  {ui.Color.DIM}全体を定期監視し、品質チェック・重複確認・改善提案を自動生成{ui.Color.RESET}")

    while True:
        choice = ui.menu("Monitorメニュー", [
            ("1", "パイプライン全体サマリー"),
            ("2", "重複チェック"),
            ("3", "品質統計アラート"),
            ("4", "改善提案を生成"),
            ("5", "改善提案一覧"),
            ("0", "戻る"),
        ])

        if choice == "1":
            _pipeline_summary()
        elif choice == "2":
            _duplicate_check()
        elif choice == "3":
            _quality_alert()
        elif choice == "4":
            _generate_suggestions()
        elif choice == "5":
            _show_suggestions()
        elif choice == "0":
            break


def _pipeline_summary():
    ui.section("パイプライン全体サマリー")

    drafts   = _load_drafts()
    schedule = _load_schedule()
    briefs   = _load_briefs()
    neta     = _load_neta()
    logs     = _load_quality_logs()

    # ステータス別集計
    draft_counts = Counter(d["status"] for d in drafts)
    sched_counts = Counter(s["status"] for s in schedule)

    stages = [
        ("ネタ帳",      f"{len([n for n in neta if not n.get('used')])} 件 (未使用)"),
        ("ブリーフィング", f"{len(briefs)} 件"),
        ("文案 draft",  f"{draft_counts.get('draft', 0)} 件"),
        ("文案 review", f"{draft_counts.get('review', 0)} 件"),
        ("文案 approved", f"{draft_counts.get('approved', 0)} 件"),
        ("文案 rejected", f"{draft_counts.get('rejected', 0)} 件"),
        ("スケジュール済", f"{sched_counts.get('scheduled', 0)} 件"),
        ("投稿済み",    f"{sched_counts.get('posted', 0)} 件"),
        ("計測済み",    f"{sched_counts.get('measured', 0)} 件"),
    ]

    print(f"\n  {'ステージ':20} {'件数':>15}")
    print(f"  {'─' * 36}")
    for stage, count in stages:
        bar = "▶" if "draft" in stage or "review" in stage or "approved" in stage else "·"
        print(f"  {bar} {stage:20} {count:>15}")

    # 品質統計
    if logs:
        avg_score = sum(l["score"] for l in logs) / len(logs)
        pass_rate = sum(1 for l in logs if l["passed"]) / len(logs) * 100
        color = ui.Color.GREEN if pass_rate >= 70 else (ui.Color.YELLOW if pass_rate >= 50 else ui.Color.RED)
        print(f"\n  品質平均スコア: {avg_score:.1f}点  合格率: {color}{pass_rate:.0f}%{ui.Color.RESET}")

    # 本日のスケジュール状況
    today = ui.today_str()
    today_sched = [s for s in schedule if s["post_date"] == today]
    if today_sched:
        posted_today = sum(1 for s in today_sched if s["status"] in ("posted", "measured"))
        print(f"\n  本日の投稿: {posted_today}/{len(today_sched)} 件完了")


def _duplicate_check():
    ui.section("重複チェック")

    drafts = _load_drafts()
    if len(drafts) < 2:
        ui.info("チェック対象が不足しています (2件以上必要)")
        return

    # キーワード重複チェック (シンプルな実装)
    def extract_keywords(text: str) -> set:
        # 簡易キーワード抽出: 5文字以上の単語・フレーズ
        import re
        words = re.findall(r'[^\s、。！？\n]{5,}', text)
        return set(words)

    duplicates = []
    checked = []

    for i, d1 in enumerate(drafts):
        kw1 = extract_keywords(d1["body"])
        for d2 in drafts[i+1:]:
            kw2 = extract_keywords(d2["body"])
            common = kw1 & kw2
            if len(common) >= 3:
                similarity = len(common) / max(len(kw1), len(kw2)) * 100
                if similarity >= 30:
                    duplicates.append({
                        "id1": d1["id"],
                        "id2": d2["id"],
                        "common": list(common)[:5],
                        "similarity": round(similarity, 1),
                    })

    if not duplicates:
        ui.success("重複の疑いがある文案は見つかりませんでした")
        return

    ui.error(f"{len(duplicates)} 件の重複疑いを検出しました")
    for dup in duplicates:
        print(f"\n  {ui.Color.YELLOW}[{dup['id1']}] と [{dup['id2']}]{ui.Color.RESET}")
        print(f"  類似度: {dup['similarity']}%")
        print(f"  共通キーワード: {', '.join(dup['common'])}")


def _quality_alert():
    ui.section("品質統計アラート")

    logs = _load_quality_logs()
    if not logs:
        ui.info("品質ログがありません")
        return

    # 直近10件の統計
    recent = logs[-10:]
    avg = sum(l["score"] for l in recent) / len(recent)
    pass_rate = sum(1 for l in recent if l["passed"]) / len(recent) * 100

    # アラート判定
    alerts = []
    if pass_rate < 50:
        alerts.append(f"合格率が低下しています ({pass_rate:.0f}%) - 声の定義を見直してください")
    if avg < 60:
        alerts.append(f"平均スコアが低下しています ({avg:.1f}点)")

    # NGワード頻出チェック
    all_notes = []
    for l in recent:
        all_notes.extend(l.get("notes", []))
    ng_notes = [n for n in all_notes if "NGワード" in n]
    if len(ng_notes) >= 3:
        alerts.append(f"NGワードが頻繁に検出されています ({len(ng_notes)}件/直近10件)")

    if alerts:
        for alert in alerts:
            ui.error(f"ALERT: {alert}")
    else:
        ui.success(f"品質統計は正常です (合格率: {pass_rate:.0f}%  平均: {avg:.1f}点)")

    # 失敗パターン分析
    if len(logs) >= 5:
        all_notes_flat = []
        for l in logs:
            all_notes_flat.extend(l.get("notes", []))

        from collections import Counter
        note_counter = Counter()
        for note in all_notes_flat:
            if "語尾" in note:
                note_counter["語尾の問題"] += 1
            elif "NGワード" in note:
                note_counter["NGワード"] += 1
            elif "文字数" in note:
                note_counter["文字数"] += 1
            elif "構成" in note:
                note_counter["構成"] += 1

        if note_counter:
            ui.section("よくある指摘事項 (TOP3)")
            for issue, cnt in note_counter.most_common(3):
                print(f"  {issue}: {cnt} 件")


def _generate_suggestions():
    ui.section("改善提案を生成中...")

    suggestions = []

    # 1. 品質スコアの傾向分析
    logs = _load_quality_logs()
    if logs:
        recent = logs[-10:]
        pass_rate = sum(1 for l in recent if l["passed"]) / len(recent) * 100
        if pass_rate < 60:
            suggestions.append({
                "category": "quality",
                "priority": "high",
                "suggestion": f"品質合格率が{pass_rate:.0f}%と低下しています。声の定義(NGワード・語尾ルール)を見直し、ライティングのテンプレートを整備してください。",
            })

    # 2. 投稿頻度の分析
    cycle = get_active_cycle()
    if cycle:
        from .do import get_posts_for_cycle
        posts = get_posts_for_cycle(cycle["id"])
        goal = cycle["goals"].get("posts", 7)
        days_elapsed_str = ui.today_str()
        from datetime import datetime
        try:
            start = datetime.strptime(cycle["start_date"], "%Y-%m-%d")
            today = datetime.strptime(ui.today_str(), "%Y-%m-%d")
            days_elapsed = max(1, (today - start).days + 1)
            expected = round(goal * days_elapsed / 7)
            if len(posts) < expected * 0.7:
                suggestions.append({
                    "category": "frequency",
                    "priority": "medium",
                    "suggestion": f"投稿ペースが遅れています (実績{len(posts)}件 / 期待値{expected}件)。毎日のブリーフィング作成と文案展開を習慣化してください。",
                })
        except Exception:
            pass

    # 3. エンゲージメント低下アラート
    if cycle:
        metrics = get_metrics_for_cycle(cycle["id"])
        if len(metrics) >= 3:
            eng_rates = [m["engagement_rate"] for m in metrics[-3:]]
            if all(eng_rates[i] >= eng_rates[i+1] for i in range(len(eng_rates)-1)):
                suggestions.append({
                    "category": "engagement",
                    "priority": "medium",
                    "suggestion": f"エンゲージメント率が3投稿連続で低下しています。投稿の書き出しを「問いかけ型」や「共感型」に変えてみてください。",
                })

    # 4. ネタ帳の枯渇
    neta = _load_neta()
    unused = [n for n in neta if not n.get("used")]
    if len(unused) < 3:
        suggestions.append({
            "category": "content",
            "priority": "low",
            "suggestion": f"ネタ帳の未使用ネタが{len(unused)}件と少なくなっています。今週中にネタを10件以上補充してください。",
        })

    # 5. 重複リスク
    drafts = _load_drafts()
    recent_topics = [d.get("brief_theme", "") for d in drafts[-10:] if d.get("brief_theme")]
    topic_counter = Counter(recent_topics)
    for topic, cnt in topic_counter.items():
        if cnt >= 3 and topic:
            suggestions.append({
                "category": "diversity",
                "priority": "low",
                "suggestion": f"テーマ '{topic}' の投稿が{cnt}件と集中しています。コンテンツの多様性を高めてください。",
            })

    if not suggestions:
        ui.success("現時点では特筆すべき改善提案はありません。このまま継続してください。")
        return

    # 保存
    import uuid as uuid_mod
    for s in suggestions:
        s["id"] = str(uuid_mod.uuid4())[:8]
        s["generated_at"] = ui.now_str()
        s["status"] = "open"

    all_suggestions = _load_suggestions()
    all_suggestions.extend(suggestions)
    _save_suggestions(all_suggestions)

    ui.success(f"{len(suggestions)} 件の改善提案を生成しました")

    priority_colors = {"high": ui.Color.RED, "medium": ui.Color.YELLOW, "low": ui.Color.DIM}
    for s in suggestions:
        color = priority_colors.get(s["priority"], "")
        print(f"\n  {color}[{s['priority'].upper()}] {s['category']}{ui.Color.RESET}")
        print(f"  {s['suggestion']}")


def _show_suggestions():
    suggestions = _load_suggestions()
    if not suggestions:
        ui.info("改善提案がありません。'改善提案を生成' を実行してください。")
        return

    open_suggestions = [s for s in suggestions if s.get("status") == "open"]
    if not open_suggestions:
        ui.info("未対応の改善提案はありません")
        return

    priority_colors = {"high": ui.Color.RED, "medium": ui.Color.YELLOW, "low": ui.Color.DIM}

    ui.section(f"未対応の改善提案 ({len(open_suggestions)} 件)")
    for s in sorted(open_suggestions, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x["priority"], 9)):
        color = priority_colors.get(s["priority"], "")
        print(f"\n  [{s['id']}] {color}{s['priority'].upper():6}{ui.Color.RESET} [{s['category']}]")
        print(f"  {s['suggestion']}")

    close_id = ui.prompt("\n対応済みにするID (Enterでスキップ)")
    if close_id:
        updated = []
        for s in suggestions:
            if s["id"] == close_id:
                s["status"] = "done"
                s["closed_at"] = ui.now_str()
            updated.append(s)
        _save_suggestions(updated)
        ui.success("対応済みにしました")

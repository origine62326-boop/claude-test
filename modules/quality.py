"""
校閲・品質チェックモジュール (マルフォイ)
語尾・構成・声のトーンを基準に文案を評価する
- チェック項目: 語尾統一 / 構成 / トーン / 文字数 / NG表現
- スコアリング: 100点満点、60点未満は自動的にNG
- 修正ノートの記録
"""

import re

from . import storage, ui
from .writing import get_draft_by_id, _load_drafts, _save_drafts


QUALITY_FILE    = "quality_logs.json"
VOICE_DEF_FILE  = "voice_definition.json"

# デフォルト声の定義
DEFAULT_VOICE = {
    "ending_rules": ["です", "ます", "だ", "である"],      # 許可する語尾
    "ng_words": ["最強", "絶対", "必ず", "バズる", "稼げる"],  # NGワード
    "min_chars": 20,
    "max_chars": 280,
    "preferred_tone": "casual",
}

SCORE_WEIGHTS = {
    "length":      20,  # 文字数適正
    "tone":        20,  # トーン一致
    "structure":   20,  # 構成 (書き出し/本文/CTA)
    "ending":      20,  # 語尾統一
    "no_ng_words": 20,  # NGワード不使用
}


def _load_quality_logs() -> list:
    return storage.load_list(QUALITY_FILE)


def _save_quality_logs(data: list):
    storage.save_list(QUALITY_FILE, data)


def _load_voice_def() -> dict:
    saved = storage.load(VOICE_DEF_FILE)
    if not saved:
        return DEFAULT_VOICE.copy()
    return {**DEFAULT_VOICE, **saved}


def _save_voice_def(data: dict):
    storage.save(VOICE_DEF_FILE, data)


def run():
    ui.header("QUALITY - 校閲・品質チェック [マルフォイ]", ui.Color.YELLOW)
    print(f"  {ui.Color.DIM}語尾・構成・声の定義を基軸に査定、不合格なら書き直しを促す{ui.Color.RESET}")

    while True:
        choice = ui.menu("Qualityメニュー", [
            ("1", "文案を品質チェックする"),
            ("2", "一括チェック (校閲待ち全件)"),
            ("3", "声の定義 (ルール) を設定"),
            ("4", "品質ログを表示"),
            ("0", "戻る"),
        ])

        if choice == "1":
            _check_single()
        elif choice == "2":
            _check_batch()
        elif choice == "3":
            _edit_voice_def()
        elif choice == "4":
            _show_quality_logs()
        elif choice == "0":
            break


def _check_single():
    draft_id = ui.prompt("チェックする文案ID")
    draft = get_draft_by_id(draft_id)
    if not draft:
        ui.error("IDが見つかりません")
        return
    _run_check(draft)


def _check_batch():
    drafts = _load_drafts()
    targets = [d for d in drafts if d["status"] in ("draft", "review")]
    if not targets:
        ui.info("校閲待ちの文案がありません")
        return

    ui.info(f"{len(targets)} 件の文案をチェックします")
    for draft in targets:
        ui.section(f"文案 {draft['id']}: {draft['body'][:30].replace(chr(10),' ')}...")
        _run_check(draft, auto=True)


def _run_check(draft: dict, auto: bool = False) -> dict:
    voice = _load_voice_def()

    scores = {}
    notes  = []

    # 1. 文字数チェック
    n = draft["char_count"]
    if voice["min_chars"] <= n <= voice["max_chars"]:
        scores["length"] = SCORE_WEIGHTS["length"]
    elif n < voice["min_chars"]:
        scores["length"] = SCORE_WEIGHTS["length"] // 2
        notes.append(f"文字数が短すぎます ({n}字 / 最小{voice['min_chars']}字)")
    else:
        deduct = min(SCORE_WEIGHTS["length"], (n - voice["max_chars"]) // 10)
        scores["length"] = max(0, SCORE_WEIGHTS["length"] - deduct)
        notes.append(f"文字数が長すぎます ({n}字 / 上限{voice['max_chars']}字)")

    # 2. NGワードチェック
    body_lower = draft["body"].lower()
    found_ng = [w for w in voice.get("ng_words", []) if w in body_lower]
    if found_ng:
        scores["no_ng_words"] = 0
        notes.append(f"NGワードが含まれています: {', '.join(found_ng)}")
    else:
        scores["no_ng_words"] = SCORE_WEIGHTS["no_ng_words"]

    # 3. 語尾チェック (最後の文の語尾)
    last_line = [l for l in draft["body"].split("\n") if l.strip()][-1] if draft["body"].strip() else ""
    ending_ok = any(last_line.endswith(e) for e in voice.get("ending_rules", []))
    # 語尾に句読点や記号が付いている場合も考慮
    last_stripped = last_line.rstrip("。！!？?…")
    ending_ok = ending_ok or any(last_stripped.endswith(e) for e in voice.get("ending_rules", []))
    if ending_ok:
        scores["ending"] = SCORE_WEIGHTS["ending"]
    else:
        scores["ending"] = SCORE_WEIGHTS["ending"] // 2
        notes.append(f"語尾が定義外の可能性があります: 「{last_line[-10:]}」")

    # 4. 構成チェック (書き出し行があるか)
    lines = [l for l in draft["body"].split("\n") if l.strip()]
    if len(lines) >= 2:
        scores["structure"] = SCORE_WEIGHTS["structure"]
    elif len(lines) == 1 and len(lines[0]) >= 40:
        scores["structure"] = SCORE_WEIGHTS["structure"]
    else:
        scores["structure"] = SCORE_WEIGHTS["structure"] // 2
        notes.append("構成が短すぎます。書き出し + 本文の形を推奨します")

    # 5. トーンチェック (手動評価)
    if auto:
        scores["tone"] = SCORE_WEIGHTS["tone"]  # 自動モードはデフォルト満点
    else:
        ui.section("本文を表示します")
        for line in draft["body"].split("\n"):
            print(f"  {line}")
        tone_score = ui.prompt_int(f"トーンスコア (0〜{SCORE_WEIGHTS['tone']}点, 声の定義: {voice.get('preferred_tone','-')})", SCORE_WEIGHTS["tone"])
        scores["tone"] = min(tone_score or 0, SCORE_WEIGHTS["tone"])
        if scores["tone"] < SCORE_WEIGHTS["tone"] // 2:
            tone_note = ui.prompt("トーン改善メモ")
            if tone_note:
                notes.append(f"トーン: {tone_note}")

    total_score = sum(scores.values())
    passed = total_score >= 60

    # 結果表示
    color = ui.Color.GREEN if passed else ui.Color.RED
    result_label = "合格" if passed else "不合格"
    print(f"\n  {color}{ui.Color.BOLD}品質スコア: {total_score}/100  [{result_label}]{ui.Color.RESET}")

    for cat, s in scores.items():
        max_s = SCORE_WEIGHTS[cat]
        bar = "█" * (s * 10 // max_s) + "░" * (10 - s * 10 // max_s)
        c = ui.Color.GREEN if s >= max_s * 0.7 else (ui.Color.YELLOW if s >= max_s * 0.4 else ui.Color.RED)
        print(f"  {cat:14}: {c}{bar}{ui.Color.RESET} {s}/{max_s}")

    if notes:
        print(f"\n  {ui.Color.YELLOW}指摘事項:{ui.Color.RESET}")
        for note in notes:
            print(f"    ・{note}")

    # ログ記録 & 文案ステータス更新
    import uuid
    log = {
        "id": str(uuid.uuid4())[:8],
        "draft_id": draft["id"],
        "score": total_score,
        "passed": passed,
        "scores": scores,
        "notes": notes,
        "checked_at": ui.now_str(),
    }
    logs = _load_quality_logs()
    logs.append(log)
    _save_quality_logs(logs)

    # 文案のスコアとステータスを更新
    all_drafts = _load_drafts()
    new_status = "review" if passed else "rejected"
    updated = []
    for d in all_drafts:
        if d["id"] == draft["id"]:
            d["quality_score"] = total_score
            d["status"] = new_status
            d["quality_notes"] = notes
        updated.append(d)
    _save_drafts(updated)

    if passed:
        ui.success(f"合格: ステータスを 'review' に更新しました")
    else:
        ui.error(f"不合格: ステータスを 'rejected' に更新しました")
        if not auto:
            rewrite = ui.prompt("書き直しますか？ (y/n)", "n")
            if rewrite.lower() == "y":
                from .writing import _edit_draft as edit
                # 文案編集画面へ
                draft_obj = get_draft_by_id(draft["id"])
                if draft_obj:
                    ui.info("本文を書き直してください:")
                    lines = []
                    while True:
                        line = input(f"  {ui.Color.WHITE}> {ui.Color.RESET}")
                        if line == "":
                            break
                        lines.append(line)
                    if lines:
                        new_body = "\n".join(lines)
                        for i, d in enumerate(updated):
                            if d["id"] == draft["id"]:
                                updated[i]["body"] = new_body
                                updated[i]["char_count"] = len(new_body)
                                updated[i]["status"] = "draft"
                                updated[i]["updated_at"] = ui.now_str()
                        _save_drafts(updated)
                        ui.success("書き直しを保存しました。再度チェックしてください。")

    return log


def _edit_voice_def():
    voice = _load_voice_def()
    ui.section("声の定義 (ルール) 設定")
    print(f"  現在の設定: {voice}")

    choice = ui.menu("編集項目", [
        ("1", "NGワードを設定"),
        ("2", "語尾ルールを設定"),
        ("3", "文字数制限を設定"),
        ("4", "推奨トーンを設定"),
        ("0", "戻る"),
    ])

    if choice == "1":
        raw = ui.prompt("NGワード (カンマ区切り)", ",".join(voice.get("ng_words", [])))
        voice["ng_words"] = [w.strip() for w in raw.split(",") if w.strip()]
        ui.success("NGワードを更新しました")

    elif choice == "2":
        raw = ui.prompt("許可する語尾 (カンマ区切り)", ",".join(voice.get("ending_rules", [])))
        voice["ending_rules"] = [w.strip() for w in raw.split(",") if w.strip()]
        ui.success("語尾ルールを更新しました")

    elif choice == "3":
        voice["min_chars"] = ui.prompt_int("最小文字数", voice.get("min_chars", 20)) or 20
        voice["max_chars"] = ui.prompt_int("最大文字数", voice.get("max_chars", 280)) or 280
        ui.success("文字数制限を更新しました")

    elif choice == "4":
        voice["preferred_tone"] = ui.menu("推奨トーン", [
            ("casual",    "カジュアル"),
            ("expert",    "専門的"),
            ("inspiring", "インスピレーション"),
            ("question",  "問いかけ"),
            ("story",     "ストーリー"),
        ])
        ui.success("推奨トーンを更新しました")

    if choice != "0":
        _save_voice_def(voice)


def _show_quality_logs():
    logs = _load_quality_logs()
    if not logs:
        ui.info("品質ログがありません")
        return

    rows = [
        [
            l["draft_id"],
            l["score"],
            ui.Color.GREEN + "合格" + ui.Color.RESET if l["passed"] else ui.Color.RED + "不合格" + ui.Color.RESET,
            l["checked_at"][:16],
        ]
        for l in logs[-20:]
    ]
    ui.table(
        ["文案ID", "スコア", "判定", "チェック日時"],
        rows,
        [10, 7, 10, 18],
    )

    avg = sum(l["score"] for l in logs) / len(logs)
    pass_rate = sum(1 for l in logs if l["passed"]) / len(logs) * 100
    print(f"\n  平均スコア: {avg:.1f}点  合格率: {pass_rate:.0f}%")

"""
世界観チェッカー - 結衣専用
投稿テキストが「朝5時の夜勤帰り孤独女子」の世界観と
一致しているかをチェックする。
"""

import re

from modules import ui
from . import storage


WORLDCHECK_LOG = "yui_worldcheck.json"

# 世界観を強化するキーワード (あると◎)
OK_KEYWORDS = [
    "夜勤", "工場", "朝5時", "朝4時", "朝6時", "帰宅", "帰り道",
    "コンビニ", "カフェラテ", "鳥の声", "朝日", "眠れない", "寝れない",
    "深夜", "孤独", "一人", "誰もいない", "静かな", "夜明け",
    "眠い", "疲れた", "お疲れ", "休憩", "夜勤明け",
]

# 恋愛世界観キーワード (淡い・受け身)
LOVE_KEYWORDS = [
    "手繋ぐ", "手繋いで", "返信待", "好きな人", "特別な", "温かい",
    "幸せになれる", "ドキドキ", "照れる", "仲良く", "寄り添い",
]

# NG キーワード (世界観を壊す)
NG_KEYWORDS_WORLDBREAK = [
    "OL", "就活", "大学", "JD", "女子大", "ギャル", "地雷系", "量産型",
    "メンヘラ", "病み", "死にたい", "消えたい",
]

# NG キーワード (エロ・過激表現)
NG_KEYWORDS_EROTIC = [
    "エロ", "えっち", "セックス", "ヤリたい", "ムラムラ",
    "パンツ", "おっぱい", "巨乳", "ヌード",
]

# NG キーワード (競合ポジション)
NG_KEYWORDS_COMPETITOR = [
    "会社員", "事務職", "ホワイト", "残業", "会議", "上司",
    "バイト", "スタバ", "スターバックス", "推し活", "フェス",
]


def run():
    ui.header("WORLDCHECK - 世界観チェッカー", ui.Color.CYAN)

    while True:
        choice = ui.menu("WorldCheckメニュー", [
            ("1", "投稿テキストをチェック"),
            ("2", "世界観ルール一覧を確認"),
            ("3", "チェック履歴を表示"),
            ("0", "メインメニューに戻る"),
        ])

        if choice == "1":
            _check_text()
        elif choice == "2":
            _show_rules()
        elif choice == "3":
            _show_history()
        elif choice == "0":
            break


def _check_text():
    ui.section("投稿テキストをチェック")
    ui.info("投稿予定のテキストを貼り付けてください (空行2回で終了)")

    lines = []
    empty_count = 0
    while True:
        line = input()
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
            lines.append(line)
        else:
            empty_count = 0
            lines.append(line)

    text = "\n".join(lines).strip()
    if not text:
        ui.error("テキストが入力されていません")
        return

    print(f"\n{ui.Color.DIM}--- 入力テキスト ---{ui.Color.RESET}")
    print(text)

    score, issues, strengths = _analyze(text)

    print(f"\n{ui.Color.BOLD}=== チェック結果 ==={ui.Color.RESET}")
    print(f"\n  世界観スコア: {_score_color(score)}{score}/100{ui.Color.RESET}")

    if strengths:
        print(f"\n  {ui.Color.GREEN}◎ 世界観強化ワード:{ui.Color.RESET}")
        for s in strengths:
            print(f"    ✓ {s}")

    if issues:
        print(f"\n  {ui.Color.RED}⚠ 問題点:{ui.Color.RESET}")
        for level, msg in issues:
            mark  = "!!" if level == "error" else "!"
            color = ui.Color.RED if level == "error" else ui.Color.YELLOW
            print(f"    {color}{mark} {msg}{ui.Color.RESET}")
    else:
        print(f"\n  {ui.Color.GREEN}問題なし ✓{ui.Color.RESET}")

    # 投稿時間帯チェック (入力があれば)
    post_hour = ui.prompt_int("投稿時刻の時 (0〜23, スキップはEnter)", None)
    if post_hour is not None:
        _check_time(post_hour)

    # ログ保存
    log = {
        "date":     ui.today_str(),
        "text":     text[:100],
        "score":    score,
        "issues":   [m for _, m in issues],
        "created":  ui.now_str(),
    }
    logs = storage.load_list(WORLDCHECK_LOG)
    logs.append(log)
    storage.save_list(WORLDCHECK_LOG, logs)

    # 判定
    print()
    if score >= 80:
        ui.success("この投稿は世界観に合っています。投稿OK!")
    elif score >= 60:
        ui.info("世界観はほぼOK。細かい修正を検討してください。")
    else:
        ui.error("世界観から外れています。投稿前に修正を検討してください。")


def _analyze(text: str) -> tuple[int, list, list]:
    """テキストを分析してスコア・課題・強みを返す"""
    score = 50
    issues  = []
    strengths = []

    # OK: 世界観ワード (+5 each, max +30)
    ok_found = [kw for kw in OK_KEYWORDS if kw in text]
    score += min(len(ok_found) * 5, 30)
    strengths.extend([f"夜勤キーワード: {kw}" for kw in ok_found[:3]])

    # OK: 恋愛ワード (+3 each, max +10)
    love_found = [kw for kw in LOVE_KEYWORDS if kw in text]
    score += min(len(love_found) * 3, 10)
    if love_found:
        strengths.append(f"淡い恋愛表現: {love_found[0]}")

    # NG: 世界観崩れ (-15 each)
    for kw in NG_KEYWORDS_WORLDBREAK:
        if kw in text:
            score -= 15
            issues.append(("error", f"世界観崩れワード: '{kw}' → 結衣は夜勤工場女子です"))

    # NG: エロ表現 (-30 each)
    for kw in NG_KEYWORDS_EROTIC:
        if kw.lower() in text.lower():
            score -= 30
            issues.append(("error", f"NG表現: '{kw}' → エロ方向はポジション外です"))

    # NG: 競合ポジション (-10 each)
    for kw in NG_KEYWORDS_COMPETITOR:
        if kw in text:
            score -= 10
            issues.append(("warn", f"競合ポジション: '{kw}' → OL/会社員キャラになってしまいます"))

    # 文字数チェック
    if len(text) > 280:
        issues.append(("warn", f"文字数 {len(text)} 字 → X の上限に近いです (140字程度が読まれやすい)"))
    elif len(text) < 20:
        issues.append(("warn", "テキストが短すぎます (20字以上推奨)"))

    # 改行チェック (詩的な改行は世界観 UP)
    line_count = len([l for l in text.split("\n") if l.strip()])
    if line_count >= 3:
        score += 5
        strengths.append("詩的な改行スタイル ◎")

    score = max(0, min(100, score))
    return score, issues, strengths


def _check_time(hour: int):
    if 5 <= hour <= 9:
        ui.success(f"投稿時刻 {hour}時 → 夜勤帰り時間帯 ◎ (フォロワーと同じ時間帯)")
    elif 10 <= hour <= 14:
        ui.info(f"投稿時刻 {hour}時 → 帰宅後まったり時間帯 (やや遅め)")
    elif 22 <= hour or hour <= 4:
        ui.info(f"投稿時刻 {hour}時 → 夜勤中・深夜 (夜勤勢には刺さります)")
    else:
        print(f"  {ui.Color.YELLOW}投稿時刻 {hour}時 → 昼間帯 (夜勤キャラとしては少し外れます){ui.Color.RESET}")


def _score_color(score: int) -> str:
    if score >= 80:
        return ui.Color.GREEN
    elif score >= 60:
        return ui.Color.YELLOW
    return ui.Color.RED


def _show_rules():
    ui.section("世界観ルール一覧")

    print(f"\n{ui.Color.GREEN}{ui.Color.BOLD}◎ 世界観強化ワード (使うとスコアUP){ui.Color.RESET}")
    print(f"  {', '.join(OK_KEYWORDS[:10])}")
    print(f"  {', '.join(OK_KEYWORDS[10:])}")

    print(f"\n{ui.Color.RED}{ui.Color.BOLD}✗ NG: 世界観崩れワード{ui.Color.RESET}")
    print(f"  {', '.join(NG_KEYWORDS_WORLDBREAK)}")

    print(f"\n{ui.Color.RED}{ui.Color.BOLD}✗ NG: エロ表現 (ポジション外){ui.Color.RESET}")
    print(f"  {', '.join(NG_KEYWORDS_EROTIC[:6])}")

    print(f"\n{ui.Color.YELLOW}{ui.Color.BOLD}! 競合ポジション (OL/JD要素){ui.Color.RESET}")
    print(f"  {', '.join(NG_KEYWORDS_COMPETITOR)}")

    print(f"\n{ui.Color.CYAN}{ui.Color.BOLD}◎ 投稿スタイルガイド{ui.Color.RESET}")
    rules = [
        "詩的な改行スタイル (3行以上が望ましい)",
        "朝5〜9時 or 深夜帯に投稿すると世界観が強まる",
        "恋愛は淡く・受け身で (手繋ぐだけで幸せ系)",
        "エロ方向NG・物語で差別化",
        "AI画像は「自然光・雰囲気重視」でAI感を消す",
    ]
    for r in rules:
        print(f"  ・{r}")


def _show_history():
    logs = storage.load_list(WORLDCHECK_LOG)
    if not logs:
        ui.info("チェック履歴がありません")
        return

    ui.section("世界観チェック履歴")
    rows = [
        [l["date"], f"{l['score']}/100", l["text"][:30], len(l.get("issues", []))]
        for l in sorted(logs, key=lambda x: x["date"], reverse=True)[:20]
    ]
    ui.table(["日付", "スコア", "テキスト抜粋", "問題数"], rows, [12, 8, 32, 7])

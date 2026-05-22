"""
Content (コンテンツ) モジュール
コンテンツアイデア生成とGrok AI美女画像生成を管理する
"""

from . import ui
from . import grok_beauty

# ノクト向けコンテンツネタテンプレート
IDEA_TEMPLATES = {
    "reality": [
        "夜勤{n}日目のリアルな疲労感と乗り越え方",
        "工場勤務で気づいた「時間の使い方」の盲点",
        "夜勤明けに勉強を続けるための朝ルーティン",
        "工場×AI副業 - 本業に影響させないスケジュール管理術",
    ],
    "numbers": [
        "フォロワー{n}人達成までに投稿した回数と振り返り",
        "AI副業で最初の{n}円を稼ぐまでにかかった時間",
        "インプレ{n}回超えた投稿の共通パターン分析",
        "0→1達成ロードマップ：{n}日間の行動ログ公開",
    ],
    "ai": [
        "工場勤務者が副業でAIを使うべき3つの理由",
        "ChatGPT/Grok活用でX投稿作成時間を1/3に短縮した方法",
        "AI画像生成でXアカウントのエンゲージメントが上がった話",
        "AIツール比較：副業初心者に本当に使えるのはどれか",
    ],
    "failure": [
        "フォロワーが全然増えなかった最初の1ヶ月の反省",
        "副業詐欺に引っかかりかけた経験とその見分け方",
        "投稿を30日続けたのに結果ゼロだった原因分析",
        "やり続けた先に見えてきたもの：失敗からの学び",
    ],
}


def _show_idea_by_category():
    ui.section("カテゴリ選択")
    options = [
        ("1", "リアル体験系"),
        ("2", "数字公開系"),
        ("3", "AI活用系"),
        ("4", "失敗→改善系"),
    ]
    cat_map = {"1": "reality", "2": "numbers", "3": "ai", "4": "failure"}
    choice = ui.menu("カテゴリ", options)
    key = cat_map[choice]

    ideas = IDEA_TEMPLATES[key]
    ui.section("コンテンツアイデア")
    for i, idea in enumerate(ideas, 1):
        print(f"  {ui.Color.CYAN}{i}.{ui.Color.RESET} {idea}")


def run():
    ui.header("Content - コンテンツ", ui.Color.YELLOW)

    while True:
        choice = ui.menu("コンテンツメニュー", [
            ("1", "コンテンツアイデア一覧"),
            ("2", "Grok AI美女画像生成"),
            ("0", "メインメニューに戻る"),
        ])

        if choice == "1":
            _show_idea_by_category()
        elif choice == "2":
            grok_beauty.run()
        elif choice == "0":
            break

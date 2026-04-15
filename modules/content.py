"""
コンテンツアイデアジェネレーター
==================================
ノクト (@noct_zero) のコンセプトに合った投稿アイデアを生成する。
カテゴリ・フック別のテンプレートとランダム提案機能を提供。
"""

import random
from . import ui


# カテゴリ別アイデアテンプレート
IDEA_BANK = {
    "reality": {
        "label": "リアル体験（工場・夜勤の現実）",
        "ideas": [
            "夜勤明けの頭で副業を進めたリアル記録",
            "工場の休憩室でスマホ1本で作業した話",
            "シフト表が出た瞬間に副業スケジュールを組む方法",
            "体が限界のとき、それでも5分だけやった話",
            "夜勤中に頭の中で考えた今日のポスト内容",
            "工場仲間に副業の話をしたときの反応",
            "夜勤明け→そのまま副業作業→何時間寝たか報告",
            "ライン作業中に浮かんだビジネスアイデア",
        ],
    },
    "numbers": {
        "label": "数字公開（インプレ・売上・フォロワー）",
        "ideas": [
            "今週のインプレッション数を全公開する",
            "フォロワー○○人達成までにかかった日数報告",
            "売上0円のまま○○日が経過した正直報告",
            "note記事のビュー数を包み隠さず出す",
            "1投稿あたりのインプレッション平均を計算した",
            "今月の副業にかけた時間と収益の比較",
            "エンゲージメント率が高かった投稿ベスト3",
            "フォロワー増減の推移グラフを公開",
        ],
    },
    "failure": {
        "label": "失敗→改善ストーリー",
        "ideas": [
            "投稿が全然伸びなかった原因を分析した",
            "やってみたら全然ダメだった施策の話",
            "3日間継続できなかった言い訳と再スタート",
            "バズると思った投稿が0いいねだった話",
            "同じミスを2回やってしまった反省と対策",
            "note記事を書いたのに誰にも読まれなかった話",
            "AI使ったのに逆に時間がかかった失敗談",
            "フォロワーが減った日にやっていたこと",
        ],
    },
    "ai": {
        "label": "AI活用レポート",
        "ideas": [
            "Claude(AI)でX投稿を作る実際の手順を公開",
            "AIに頼んで失敗したこと・成功したこと",
            "夜勤明けでも30分でnote記事が書けたAI活用術",
            "AIを使った1週間のコンテンツ制作フロー",
            "無料AIツールだけで副業を進める方法",
            "AIに壁打ちしてもらって気づいたこと",
            "ChatGPTとClaudeを使い分けている理由",
            "AI×工場勤務でできる副業の組み合わせ案",
        ],
    },
    "learning": {
        "label": "学び・気づき",
        "ideas": [
            "X運用を○○日やって気づいた一番大事なこと",
            "フォロワーが増えている人と自分の違いを分析",
            "副業を始めて変わった「時間の使い方」",
            "発信を続けてわかった「伸びる投稿の共通点」",
            "失敗から学んだ「継続のための仕組み化」",
            "工場勤務だからこそ気づけた副業の本質",
            "0→1を突破するのに本当に必要だったもの",
            "最初の1ヶ月でやってよかったこと・やらなくていいこと",
        ],
    },
    "journey": {
        "label": "0→1ジャーニー",
        "ideas": [
            "副業を始めた日から今日までの正直な記録",
            "○○日目の現在地報告（フォロワー・収益・学び）",
            "今週できたこと・できなかったこと全部出す",
            "1ヶ月前の自分に教えてあげたいこと",
            "0→1突破のために今週挑戦することを宣言",
            "副業をやめたくなった瞬間と続けた理由",
            "最初の売上が立つまでにかかる時間の予測",
            "0円から始まる攻略ログ○○日目",
        ],
    },
    "empathy": {
        "label": "共感・応援",
        "ideas": [
            "「時間がない」を言い訳にしてた自分への手紙",
            "動けない人に伝えたい「5分だけルール」",
            "工場勤務でも副業できる証拠を積み上げてる",
            "しんどいけどやめない理由を正直に書く",
            "同じ状況の人へ：一緒にやろうという話",
            "「どうせ無理」と思ってた自分が変わった話",
            "副業で稼ぐより先に変わったこと",
            "眠くてもスマホを開く習慣の作り方",
        ],
    },
}

# フック×カテゴリの組み合わせ提案
HOOK_COMBOS = [
    ("number",   "numbers",  "「○○日目、売上0円。それでも続ける理由を話す。」"),
    ("empathy",  "empathy",  "「忙しいのはわかる。でも5分だけ見てほしい。」"),
    ("shock",    "failure",  "「正直に言う。今週は全部失敗した。」"),
    ("question", "learning", "「なぜ工場勤務の自分が副業できてるのか、ようやくわかった。」"),
    ("declare",  "journey",  "「今週こそ0→1を突破する。全部見せる。」"),
    ("number",   "reality",  "「夜勤明け4時間睡眠で副業2時間やった記録。」"),
    ("shock",    "ai",       "「AIを使ったら、30分でnote記事が完成した話。」"),
    ("empathy",  "journey",  "「止まってる人へ。俺も2ヶ月止まってた。」"),
]


def run():
    ui.header("IDEA - コンテンツアイデア生成", ui.Color.CYAN)
    print(f"  {ui.Color.DIM}ノクトのコンセプトに合ったアイデアを提案{ui.Color.RESET}")

    while True:
        choice = ui.menu("Idea メニュー", [
            ("1", "ランダムアイデアを提案"),
            ("2", "カテゴリ別アイデアを見る"),
            ("3", "フック×カテゴリの組み合わせ提案"),
            ("4", "今週の投稿プランを作る"),
            ("0", "メインメニューに戻る"),
        ])

        if choice == "1":
            _random_ideas()
        elif choice == "2":
            _category_ideas()
        elif choice == "3":
            _hook_combos()
        elif choice == "4":
            _weekly_plan()
        elif choice == "0":
            break


def _random_ideas():
    ui.section("ランダムアイデア提案（5件）")
    print(f"  {ui.Color.DIM}ノクトのカテゴリからランダムに抽出します{ui.Color.RESET}\n")

    all_ideas = []
    for cat_key, cat_data in IDEA_BANK.items():
        for idea in cat_data["ideas"]:
            all_ideas.append((cat_key, cat_data["label"], idea))

    picked = random.sample(all_ideas, min(5, len(all_ideas)))
    for i, (cat_key, cat_label, idea) in enumerate(picked, 1):
        print(f"  {ui.Color.CYAN}{i}.{ui.Color.RESET} {idea}")
        print(f"     {ui.Color.DIM}[{cat_label}]{ui.Color.RESET}")

    print()
    again = ui.prompt("もう5件見る？ (y/n)", "n")
    if again.lower() == "y":
        _random_ideas()


def _category_ideas():
    ui.section("カテゴリ選択")
    options = [(k, v["label"]) for k, v in IDEA_BANK.items()] + [("0", "戻る")]
    choice = ui.menu("カテゴリ", options)

    if choice == "0":
        return

    cat = IDEA_BANK[choice]
    ui.section(cat["label"])
    for i, idea in enumerate(cat["ideas"], 1):
        print(f"  {ui.Color.CYAN}{i}.{ui.Color.RESET} {idea}")


def _hook_combos():
    ui.section("フック×カテゴリ 組み合わせ提案")
    print(f"  {ui.Color.DIM}刺さるフックとカテゴリの黄金パターン{ui.Color.RESET}\n")

    hook_names = {
        "number":   "数字フック",
        "empathy":  "共感フック",
        "shock":    "衝撃フック",
        "question": "疑問フック",
        "declare":  "宣言フック",
    }

    for hook, cat, example in HOOK_COMBOS:
        h_label = hook_names.get(hook, hook)
        c_label = IDEA_BANK[cat]["label"]
        print(f"  {ui.Color.YELLOW}{h_label}{ui.Color.RESET} × {ui.Color.CYAN}{c_label}{ui.Color.RESET}")
        print(f"    例: {example}\n")


def _weekly_plan():
    ui.section("今週の投稿プラン作成（7投稿）")
    print(f"  {ui.Color.DIM}カテゴリをバランスよく割り振ります{ui.Color.RESET}\n")

    # ノクト推奨の週間バランス
    weekly_template = [
        ("月", "reality",  "数字フック",  "週の始まりにリアルを出す"),
        ("火", "ai",       "衝撃フック",  "AI活用で差別化"),
        ("水", "numbers",  "数字フック",  "中間数字公開で信頼を積む"),
        ("木", "failure",  "共感フック",  "失敗を正直に出して共感を取る"),
        ("金", "learning", "疑問フック",  "学びで価値提供"),
        ("土", "empathy",  "共感フック",  "週末に共感投稿で繋がる"),
        ("日", "journey",  "宣言フック",  "週の締めに進捗・宣言"),
    ]

    print(f"  {'曜':4} {'カテゴリ':20} {'フック':12} {'狙い'}")
    print(f"  {ui.Color.DIM}{'─' * 60}{ui.Color.RESET}")

    for day, cat, hook, aim in weekly_template:
        cat_label  = IDEA_BANK[cat]["label"][:16]
        idea       = random.choice(IDEA_BANK[cat]["ideas"])
        print(f"  {ui.Color.CYAN}{day}曜{ui.Color.RESET}  {cat_label:18} {hook:10} {aim}")
        print(f"       → {idea}")
        print()

    print(f"  {ui.Color.DIM}※ アイデアはランダム提案です。実際の内容はあなたの体験に合わせて調整してください。{ui.Color.RESET}")

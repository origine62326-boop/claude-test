"""
コンテンツテンプレート - 結衣専用
投稿テンプレ・フック文・ハッシュタグ集
"""

import random

from modules import ui


# ────────────────────────────────────────────────
# 日常テンプレ集 (目標70%)
# ────────────────────────────────────────────────
DAILY_TEMPLATES = [
    # 朝帰り・コンビニ
    ("朝5時。\n今日もコンビニのカフェラテ買った。\n店員さんに顔覚えられてそう。",
     "コンビニカフェラテ日常"),
    ("帰宅したら鳥の鳴き声。\nこれ聞くと\n夜勤終わったなって思う。",
     "鳥の声・帰宅"),
    ("朝5時の空って\n誰にも見せたくない感じがする。\nひとり占めしてる感覚。",
     "朝の空・孤独感"),
    ("夜勤明け、\nコンビニで温かいもの買って\nそのまま道端でひとり飲む。\n最高のひとときです。",
     "コンビニ・夜勤明け"),
    ("みんなが出勤する時間に\n私は帰宅する。\n逆向きの人生。",
     "逆向きの人生"),
    ("工場の匂いが制服についたまま\n朝のコンビニに入るの\nちょっと恥ずかしい。",
     "工場の匂い・コンビニ"),
    ("夜勤が終わると\nすごく静かな朝がくる。\nその静けさがなんか好き。",
     "夜勤終わり・静けさ"),
    ("朝5時の自販機って\n誰かいる気がする。\nいつも私ひとりだけど。",
     "深夜の自販機"),
    ("眠いのに眠れない日。\nSNS見てたら朝になってた。",
     "眠れない夜"),
    ("帰り道、月がきれいだった。\n夜勤の数少ない特権。",
     "帰り道・月"),
    ("朝の空気って\n夜勤終わりにしか嗅げない気がする。\nちょっと得した気分。",
     "朝の空気"),
    ("休憩室で食べるカップ麺が\nなぜかすごく美味しい。\n夜中の2時の話。",
     "休憩室・夜中のカップ麺"),
]

# ────────────────────────────────────────────────
# 恋愛テンプレ集 (目標20%)
# ────────────────────────────────────────────────
LOVE_TEMPLATES = [
    ("手繋いで帰るだけで\n幸せになれるタイプです。",
     "手繋ぎ・シンプルな幸せ"),
    ("好きな人ができると\n返信待っちゃう。",
     "返信待ち"),
    ("夜勤明け、\n「お疲れ」って言ってくれる人が\nいたらいいなって思う。",
     "お疲れと言ってくれる人"),
    ("寝る前に\nおやすみって言える人が\nほしいな。",
     "おやすみの人"),
    ("恋愛が苦手なんじゃなくて\n人が怖いのかもしれない。",
     "人が怖い・恋愛苦手"),
    ("好きな人と\n朝5時のコンビニ行きたい。\nそれだけでいい。",
     "好きな人とコンビニ"),
    ("LINEの既読って\nなんで何時についたかわかるんだろう。\nドキドキしすぎる。",
     "LINE既読・ドキドキ"),
    ("夜勤終わりに\n迎えに来てくれる人がいる人生\n想像したことある。",
     "迎えに来てくれる人"),
    ("ぼーっとしてると\n好きな人のこと考えちゃう。\n夜勤中に考えてどうするんだって話。",
     "夜勤中・好きな人"),
]

# ────────────────────────────────────────────────
# DMM導線テンプレ集 (目標10%)
# ────────────────────────────────────────────────
DMM_TEMPLATES = [
    ("夜勤明け、眠れない時ってありません?\n私はよく動画見て過ごしてます。\n最近ハマってるの→ [URL]",
     "夜勤明け眠れない→動画"),
    ("帰宅してからの1〜2時間が\n一番好きな時間。\nひとりでまったり動画見てる。\nおすすめあったら教えてください☕\n→ [URL]",
     "帰宅後まったり→おすすめ"),
    ("休憩中に見てる動画\nこれが好きすぎて時間溶ける→ [URL]\n夜勤の楽しみになってます。",
     "休憩中に見る動画"),
    ("夜中に見る動画って\nなぜか昼より刺さる。\n今日見てよかったやつ→ [URL]",
     "夜中に見る動画"),
    ("同じ夜勤の方に聞きたいんですが\n起きてる時間に何してますか?\n私はこれ見てます→ [URL]",
     "夜勤の方へ・共感誘発"),
]

# ────────────────────────────────────────────────
# フック文集 (冒頭に使う)
# ────────────────────────────────────────────────
HOOKS = [
    ("朝5時。", "情景・時間"),
    ("夜勤明けの話をしてもいい?", "問いかけ"),
    ("帰宅したら鳥の声。", "情景"),
    ("みんなが起きる頃に私は寝る。", "逆転生活"),
    ("夜勤あるあるなんだけど、", "あるある共感"),
    ("眠れない夜ってありますよね。", "共感"),
    ("コンビニが好き。特に深夜の。", "深夜コンビニ"),
    ("工場女子の日常を聞いてほしい。", "日常開示"),
    ("同じような人いたら教えてほしい。", "共感募集"),
    ("今日も朝日見ながら帰宅。", "帰宅情景"),
]

# ────────────────────────────────────────────────
# ハッシュタグ集
# ────────────────────────────────────────────────
HASHTAG_SETS = {
    "日常": ["#夜勤", "#夜勤あるある", "#工場勤務", "#一人暮らし", "#深夜"],
    "恋愛": ["#恋愛", "#恋愛あるある", "#片思い", "#夜勤女子"],
    "DMM":  ["#夜勤", "#眠れない夜", "#動画配信", "#夜勤あるある"],
    "広め": ["#夜勤あるある", "#工場あるある", "#一人暮らし女子", "#深夜テンション"],
}

# 固定ポスト
FIXED_POST = """朝5時。
みんなが出勤する頃に私は帰宅。
コンビニのカフェラテ飲みながら寝る準備してます。
同じような人いたら仲良くしてください☕"""


def run():
    ui.header("CONTENT - コンテンツ生成", ui.Color.CYAN)

    while True:
        choice = ui.menu("Contentメニュー", [
            ("1", "日常テンプレを表示 (70%枠)"),
            ("2", "恋愛テンプレを表示 (20%枠)"),
            ("3", "DMM導線テンプレを表示 (10%枠)"),
            ("4", "ランダムに投稿案を生成"),
            ("5", "フック文集を表示"),
            ("6", "ハッシュタグ集を表示"),
            ("7", "固定ポスト文を表示"),
            ("0", "メインメニューに戻る"),
        ])

        if choice == "1":
            _show_templates(DAILY_TEMPLATES, "日常テンプレ集 (70%枠)", ui.Color.CYAN)
        elif choice == "2":
            _show_templates(LOVE_TEMPLATES, "恋愛テンプレ集 (20%枠)", ui.Color.RED)
        elif choice == "3":
            _show_dmm_templates()
        elif choice == "4":
            _random_suggestion()
        elif choice == "5":
            _show_hooks()
        elif choice == "6":
            _show_hashtags()
        elif choice == "7":
            _show_fixed_post()
        elif choice == "0":
            break


def _show_templates(templates: list, title: str, color: str):
    ui.section(title)
    for i, (text, label) in enumerate(templates, 1):
        print(f"\n  {color}{ui.Color.BOLD}[{i}] {label}{ui.Color.RESET}")
        for line in text.split("\n"):
            print(f"    {line}")

    pick = ui.prompt_int("\n番号を選んでコピー用に表示 (Enterでスキップ)", None)
    if pick and 1 <= pick <= len(templates):
        text, label = templates[pick - 1]
        print(f"\n{ui.Color.BOLD}--- コピー用 ---{ui.Color.RESET}")
        print(text)
        print(f"{ui.Color.BOLD}----------------{ui.Color.RESET}")


def _show_dmm_templates():
    ui.section("DMM導線テンプレ集 (10%枠)")
    ui.info("[URL] の部分をアフィリエイトURLに置き換えてください")

    for i, (text, label) in enumerate(DMM_TEMPLATES, 1):
        print(f"\n  {ui.Color.YELLOW}{ui.Color.BOLD}[{i}] {label}{ui.Color.RESET}")
        for line in text.split("\n"):
            print(f"    {line}")

    pick = ui.prompt_int("\n番号を選んでコピー用に表示 (Enterでスキップ)", None)
    if pick and 1 <= pick <= len(DMM_TEMPLATES):
        text, label = DMM_TEMPLATES[pick - 1]
        print(f"\n{ui.Color.BOLD}--- コピー用 ---{ui.Color.RESET}")
        print(text)
        print(f"{ui.Color.BOLD}----------------{ui.Color.RESET}")


def _random_suggestion():
    ui.section("ランダム投稿案を生成")

    cat = ui.menu("カテゴリ", [
        ("daily", "日常 (70%)"),
        ("love",  "恋愛 (20%)"),
        ("dmm",   "DMM  (10%)"),
        ("mix",   "ミックス (比率に合わせてランダム)"),
    ])

    if cat == "mix":
        r = random.random()
        cat = "daily" if r < 0.70 else "love" if r < 0.90 else "dmm"

    template_map = {"daily": DAILY_TEMPLATES, "love": LOVE_TEMPLATES, "dmm": DMM_TEMPLATES}
    hook = random.choice(HOOKS)
    template = random.choice(template_map[cat])
    hashtags = HASHTAG_SETS.get("日常" if cat == "daily" else "恋愛" if cat == "love" else "DMM", [])

    cat_color = {"daily": ui.Color.CYAN, "love": ui.Color.RED, "dmm": ui.Color.YELLOW}[cat]
    cat_label = {"daily": "日常", "love": "恋愛", "dmm": "DMM"}[cat]

    print(f"\n  {cat_color}{ui.Color.BOLD}カテゴリ: {cat_label}{ui.Color.RESET}")
    print(f"\n  {ui.Color.BOLD}フック候補:{ui.Color.RESET}")
    print(f"    {hook[0]}  ({hook[1]})")
    print(f"\n  {ui.Color.BOLD}本文候補:{ui.Color.RESET}")
    for line in template[0].split("\n"):
        print(f"    {line}")
    print(f"\n  {ui.Color.BOLD}ハッシュタグ:{ui.Color.RESET}")
    print(f"    {' '.join(hashtags)}")


def _show_hooks():
    ui.section("フック文集 (投稿冒頭に使う)")
    for i, (text, label) in enumerate(HOOKS, 1):
        print(f"  {ui.Color.CYAN}{i:2d}.{ui.Color.RESET} {text:<22}  {ui.Color.DIM}({label}){ui.Color.RESET}")


def _show_hashtags():
    ui.section("ハッシュタグ集")
    for scene, tags in HASHTAG_SETS.items():
        print(f"\n  {ui.Color.YELLOW}{scene}:{ui.Color.RESET}")
        print(f"    {' '.join(tags)}")


def _show_fixed_post():
    ui.section("固定ポスト (プロフィールに固定する文)")
    print()
    for line in FIXED_POST.split("\n"):
        print(f"  {line}")
    print()
    ui.info("プロフィールの固定ポストとして使用することを推奨します")

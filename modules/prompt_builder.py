"""
AI美女プロンプトビルダー
要素を選択式で組み合わせて高品質なGrok用プロンプトを構築する
"""

from . import storage, ui

SAVED_PROMPTS_FILE = "saved_prompts.json"

# ─────────────────────────────────────────────
# Xバズ狙いプリセットプロンプト
# ─────────────────────────────────────────────
BUZZ_PRESETS = [
    {
        "id": "B01",
        "name": "【桜×清楚】春の透明感ガール",
        "tags": ["桜", "清楚", "春", "透明感"],
        "buzz_point": "桜×逆光×清楚の最強トリオ。春季は特に拡散されやすい",
        "prompt": (
            "a beautiful 20-year-old Japanese woman, innocent expression, rosy cheeks, soft features, "
            "long straight black hair, elegant floral dress, "
            "under cherry blossom trees, petals falling, "
            "backlit, sun halo, silhouette glow, "
            "portrait shot, face and upper body, dreamy expression, slightly unfocused gaze, "
            "photorealistic, 8K resolution, ultra-detailed, sharp focus"
        ),
    },
    {
        "id": "B02",
        "name": "【浴衣×夏祭り】縁日の彼女感",
        "tags": ["浴衣", "夏祭り", "彼女感", "夜"],
        "buzz_point": "浴衣×夜縁日×はにかみ笑顔。夏に最高拡散。「好きになるやつ」コメントを誘発",
        "prompt": (
            "a beautiful 20-year-old Japanese woman, natural face, minimal makeup, clear skin, "
            "high ponytail hairstyle, colorful summer yukata, "
            "nighttime city street, neon lights background, warm candlelight, intimate atmosphere, "
            "half-body shot, waist up, shy smile, blushing cheeks, "
            "photorealistic, 8K resolution, ultra-detailed, sharp focus"
        ),
    },
    {
        "id": "B03",
        "name": "【ネオン×クール】深夜の渋谷系",
        "tags": ["ネオン", "クール", "夜", "都市"],
        "buzz_point": "映画のワンシーン風。「ドラマの主人公感」でRTを稼ぐ",
        "prompt": (
            "a beautiful 20-year-old Japanese woman, sharp facial features, strong brows, cool expression, "
            "long wavy brown hair, smart casual office attire, blazer, "
            "nighttime city street, neon lights background, colorful neon lighting, dramatic shadows, "
            "full body shot, head to toe, confident posture, direct gaze, "
            "cinematic photography, film grain, bokeh background"
        ),
    },
    {
        "id": "B04",
        "name": "【ビーチ×夏】青春の眩しさ",
        "tags": ["ビーチ", "夏", "水着", "健康的"],
        "buzz_point": "夏の健康美×明るい笑顔。保存数が特に伸びる構成",
        "prompt": (
            "a beautiful 20-year-old Japanese woman, Korean-style makeup, gradient lips, dewy skin, "
            "long wavy brown hair, stylish bikini at the beach, "
            "tropical beach, blue ocean background, natural daylight, soft shadows, "
            "full body shot, head to toe, bright cheerful smile, energetic vibe, "
            "photorealistic, 8K resolution, ultra-detailed, sharp focus"
        ),
    },
    {
        "id": "B05",
        "name": "【着物×幻想】和の美人図",
        "tags": ["着物", "和風", "幻想的", "雑誌風"],
        "buzz_point": "伝統美×幻想光で「芸術作品」として保存される。海外勢への訴求も高い",
        "prompt": (
            "a beautiful 20-year-old Japanese woman, glamorous makeup, defined eyes, glossy lips, "
            "long straight black hair, traditional Japanese kimono, "
            "fantasy flower field, magical soft light, blue hour dusk lighting, cool tones, "
            "full body shot, head to toe, dreamy expression, slightly unfocused gaze, "
            "professional magazine photography, editorial style"
        ),
    },
    {
        "id": "B06",
        "name": "【カフェ×ナチュラル】日常のかわいさ",
        "tags": ["カフェ", "ナチュラル", "日常", "親近感"],
        "buzz_point": "「隣にいそうな可愛い子」感。親近感が高くコメントを誘発しやすい",
        "prompt": (
            "a beautiful 20-year-old Japanese woman, natural face, minimal makeup, clear skin, "
            "short black bob haircut, casual outfit, jeans and white t-shirt, "
            "outdoor café terrace, warm afternoon light, soft studio lighting, even illumination, "
            "portrait shot, face and upper body, bright cheerful smile, energetic vibe, "
            "photorealistic, high quality"
        ),
    },
    {
        "id": "B07",
        "name": "【逆光×花畑×後ろ姿】エモ最強構図",
        "tags": ["逆光", "後ろ姿", "エモ", "花畑"],
        "buzz_point": "「顔が見たい」コメントでエンゲージが爆増する想像力を掻き立てる最強構図",
        "prompt": (
            "a beautiful 20-year-old Japanese woman, innocent expression, rosy cheeks, soft features, "
            "long straight black hair, elegant floral dress, "
            "fantasy flower field, magical soft light, backlit, sun halo, silhouette glow, "
            "shot from behind, looking back over shoulder, dreamy expression, slightly unfocused gaze, "
            "photorealistic, 8K resolution, ultra-detailed, sharp focus"
        ),
    },
    {
        "id": "B08",
        "name": "【メイド×アニメ風】萌え×アート",
        "tags": ["メイド", "アニメ風", "ツインテール", "萌え"],
        "buzz_point": "イラスト風×メイド×ツインテールはオタク層への訴求力が圧倒的",
        "prompt": (
            "a beautiful 20-year-old Japanese woman, Korean-style makeup, gradient lips, dewy skin, "
            "twin tails hairstyle, classic maid outfit, "
            "minimalist white room, clean background, soft studio lighting, even illumination, "
            "portrait shot, face and upper body, seductive expression, slightly open mouth, "
            "detailed digital illustration, anime art style"
        ),
    },
]

# ─────────────────────────────────────────────
# プロンプト要素ライブラリ
# ─────────────────────────────────────────────

SUBJECT = [
    ("japanese_20s", "日本人・20代",   "a beautiful 20-year-old Japanese woman"),
    ("japanese_30s", "日本人・30代",   "a beautiful 30-year-old Japanese woman"),
    ("asian_young",  "アジア系・若い", "a beautiful young Asian woman"),
    ("mixed",        "ハーフ系",       "a beautiful woman of mixed Japanese and European descent"),
]

FACE = [
    ("natural",    "自然・無加工風",  "natural face, minimal makeup, clear skin"),
    ("glamour",    "グラマラスメイク","glamorous makeup, defined eyes, glossy lips"),
    ("korean",     "韓国メイク風",    "Korean-style makeup, gradient lips, dewy skin"),
    ("cool",       "クールビューティー", "sharp facial features, strong brows, cool expression"),
    ("innocent",   "清純・透明感",    "innocent expression, rosy cheeks, soft features"),
]

HAIR = [
    ("long_black",  "ロング・黒髪",    "long straight black hair"),
    ("long_brown",  "ロング・ブラウン","long wavy brown hair"),
    ("short_black", "ショート・黒髪",  "short black bob haircut"),
    ("ponytail",    "ポニーテール",    "high ponytail hairstyle"),
    ("blonde",      "ブロンド",        "long blonde hair"),
    ("twintail",    "ツインテール",    "twin tails hairstyle"),
]

OUTFIT = [
    ("casual",    "カジュアル",        "casual outfit, jeans and white t-shirt"),
    ("office",    "オフィスカジュアル","smart casual office attire, blazer"),
    ("dress",     "ワンピース",        "elegant floral dress"),
    ("kimono",    "着物",              "traditional Japanese kimono"),
    ("yukata",    "浴衣",              "colorful summer yukata"),
    ("bikini",    "水着",              "stylish bikini at the beach"),
    ("school",    "制服風",            "Japanese-style school uniform"),
    ("lingerie",  "ランジェリー",      "delicate lace lingerie"),
    ("sportswear","スポーツウェア",    "athletic sportswear, leggings"),
    ("maid",      "メイド服",          "classic maid outfit"),
]

SETTING = [
    ("outdoor_park",   "公園・昼",         "sunny park, green trees background"),
    ("outdoor_cherry", "桜の下",           "under cherry blossom trees, petals falling"),
    ("outdoor_beach",  "ビーチ",           "tropical beach, blue ocean background"),
    ("outdoor_city",   "都市・夜",         "nighttime city street, neon lights background"),
    ("outdoor_cafe",   "カフェテラス",     "outdoor café terrace, warm afternoon light"),
    ("indoor_room",    "白い部屋",         "minimalist white room, clean background"),
    ("indoor_bedroom", "寝室",             "cozy bedroom, soft pillows"),
    ("indoor_onsen",   "温泉・露天風呂",   "outdoor hot spring onsen, steam and nature"),
    ("studio",         "スタジオ・無地",   "plain studio background, neutral gray"),
    ("fantasy",        "幻想的・花畑",     "fantasy flower field, magical soft light"),
]

LIGHTING = [
    ("golden_hour", "ゴールデンアワー", "golden hour sunlight, warm tones"),
    ("soft_studio", "スタジオ・柔らか", "soft studio lighting, even illumination"),
    ("neon",        "ネオン・夜",        "colorful neon lighting, dramatic shadows"),
    ("backlight",   "逆光・ハロー",      "backlit, sun halo, silhouette glow"),
    ("natural_day", "自然光・昼",        "natural daylight, soft shadows"),
    ("candle",      "キャンドル・暖色",  "warm candlelight, intimate atmosphere"),
    ("blue_hour",   "ブルーアワー",      "blue hour dusk lighting, cool tones"),
]

COMPOSITION = [
    ("portrait",    "ポートレート (顔〜胸)", "portrait shot, face and upper body"),
    ("half_body",   "半身 (腰まで)",         "half-body shot, waist up"),
    ("full_body",   "全身",                  "full body shot, head to toe"),
    ("close_up",    "クローズアップ (顔)",   "close-up face shot"),
    ("from_behind", "後ろ姿",               "shot from behind, looking back over shoulder"),
    ("lying_down",  "横たわり",              "lying down pose, relaxed"),
]

QUALITY = [
    ("standard",     "標準",      "photorealistic, high quality"),
    ("ultra",        "超高品質",  "photorealistic, 8K resolution, ultra-detailed, sharp focus"),
    ("cinematic",    "映画風",    "cinematic photography, film grain, bokeh background"),
    ("illustration", "イラスト風","detailed digital illustration, anime art style"),
    ("magazine",     "雑誌風",    "professional magazine photography, editorial style"),
]

MOOD_EXTRA = [
    ("none",      "なし",         ""),
    ("sexy",      "セクシー",     "seductive expression, slightly open mouth"),
    ("cheerful",  "明るい・元気", "bright cheerful smile, energetic vibe"),
    ("dreamy",    "夢見がち",     "dreamy expression, slightly unfocused gaze"),
    ("confident", "自信満々",     "confident posture, direct gaze"),
    ("shy",       "照れ・はにかみ","shy smile, blushing cheeks"),
]

# ─────────────────────────────────────────────
# 選択ヘルパー
# ─────────────────────────────────────────────

def _pick(title: str, options: list[tuple]) -> tuple:
    """(key, label, value) のリストからメニュー選択して (key, value) を返す"""
    menu_opts = [(k, label) for k, label, _ in options]
    choice_key = ui.menu(title, menu_opts)
    for k, label, val in options:
        if k == choice_key:
            return k, val
    return options[0][0], options[0][2]


def _multi_pick(title: str, options: list[tuple], default_keys: list[str] | None = None) -> list[str]:
    """複数選択: カンマ区切りで入力 → values のリスト"""
    ui.section(title)
    for i, (k, label, _) in enumerate(options, 1):
        mark = "*" if (default_keys and k in default_keys) else " "
        print(f"  {ui.Color.CYAN}{i}{ui.Color.RESET}. [{mark}] {label}")
    raw = ui.prompt("番号をカンマ区切りで入力 (例: 1,3)", "")
    selected = []
    if raw:
        try:
            indices = [int(x.strip()) - 1 for x in raw.split(",")]
            for idx in indices:
                if 0 <= idx < len(options):
                    selected.append(options[idx][2])
        except ValueError:
            pass
    if not selected and default_keys:
        selected = [v for k, _, v in options if k in default_keys]
    return selected


# ─────────────────────────────────────────────
# プロンプト組み立て
# ─────────────────────────────────────────────

def assemble(parts: list[str]) -> str:
    return ", ".join(p for p in parts if p)


def build_interactive() -> str | None:
    """対話式でプロンプトを組み立てて完成プロンプトを返す"""
    ui.header("プロンプトビルダー", ui.Color.CYAN)
    print(f"  {ui.Color.DIM}各カテゴリから要素を選んでプロンプトを組み立てます{ui.Color.RESET}\n")

    # 1. 被写体
    _, subject_val = _pick("① 被写体", SUBJECT)

    # 2. 顔・メイク
    _, face_val = _pick("② 顔・メイク", FACE)

    # 3. 髪型
    _, hair_val = _pick("③ 髪型", HAIR)

    # 4. 衣装
    _, outfit_val = _pick("④ 衣装", OUTFIT)

    # 5. 背景・ロケーション
    _, setting_val = _pick("⑤ 背景・ロケーション", SETTING)

    # 6. 照明
    _, lighting_val = _pick("⑥ 照明", LIGHTING)

    # 7. 構図
    _, comp_val = _pick("⑦ 構図", COMPOSITION)

    # 8. ムード (任意)
    _, mood_val = _pick("⑧ ムード・表情", MOOD_EXTRA)

    # 9. クオリティ
    _, quality_val = _pick("⑨ クオリティ", QUALITY)

    # 10. 追加キーワード (自由入力)
    ui.section("⑩ 追加キーワード (任意)")
    ui.info("例: red ribbon, holding umbrella, wet hair, smiling")
    extra = ui.prompt("追加キーワード (英語推奨)", "")

    # 組み立て
    parts = [subject_val, face_val, hair_val, outfit_val, setting_val,
             lighting_val, comp_val]
    if mood_val:
        parts.append(mood_val)
    parts.append(quality_val)
    if extra:
        parts.append(extra)

    prompt = assemble(parts)

    # 確認表示
    ui.section("完成プロンプト")
    print(f"\n  {ui.Color.GREEN}{ui.Color.BOLD}{prompt}{ui.Color.RESET}\n")

    action = ui.menu("次のアクション", [
        ("1", "このプロンプトで生成する"),
        ("2", "プロンプトを保存する"),
        ("3", "プロンプトをコピー表示して戻る"),
        ("0", "キャンセル"),
    ])

    if action == "0":
        return None
    if action == "3":
        print(f"\n{prompt}\n")
        input("Enterで戻る...")
        return None
    if action == "2":
        _save_prompt(prompt)
        return None
    # action == "1"
    return prompt


# ─────────────────────────────────────────────
# 保存済みプロンプト管理
# ─────────────────────────────────────────────

def _load_saved() -> list:
    return storage.load_list(SAVED_PROMPTS_FILE)


def _save_prompt(prompt: str):
    name = ui.prompt("保存名 (例: 黒髪清楚ビーチ)")
    if not name:
        name = f"prompt_{ui.now_str()}"
    saved = _load_saved()
    entry = {
        "id": str(len(saved) + 1).zfill(3),
        "name": name,
        "prompt": prompt,
        "created_at": ui.now_str(),
    }
    saved.append(entry)
    storage.save_list(SAVED_PROMPTS_FILE, saved)
    ui.success(f"「{name}」として保存しました (ID: {entry['id']})")


def list_saved() -> list:
    return _load_saved()


def select_saved() -> str | None:
    """保存済みプロンプト一覧から選択して文字列を返す"""
    saved = _load_saved()
    if not saved:
        ui.info("保存済みプロンプトがありません")
        return None

    ui.section(f"保存済みプロンプト ({len(saved)} 件)")
    rows = [[s["id"], s["name"][:20], s["created_at"][:10], s.get("buzz_point", s["prompt"])[:28]] for s in saved]
    ui.table(["ID", "名前", "日付", "バズ狙い/プロンプト"], rows, [5, 22, 12, 30])

    sid = ui.prompt("\n使用するID (Enterでキャンセル)", "")
    if not sid:
        return None
    entry = next((s for s in saved if s["id"] == sid), None)
    if not entry:
        ui.error("IDが見つかりません")
        return None

    ui.info(f"選択: {entry['name']}")
    if entry.get("tags"):
        print(f"  タグ  : {' '.join('#'+t for t in entry['tags'])}")
    if entry.get("buzz_point"):
        print(f"  狙い  : {entry['buzz_point']}")
    print(f"  Prompt: {ui.Color.GREEN}{entry['prompt']}{ui.Color.RESET}")
    return entry["prompt"]


def delete_saved():
    saved = _load_saved()
    if not saved:
        ui.info("保存済みプロンプトがありません")
        return

    rows = [[s["id"], s["name"], s["prompt"][:30]] for s in saved]
    ui.table(["ID", "名前", "プロンプト"], rows, [5, 16, 32])

    sid = ui.prompt("削除するID", "")
    entry = next((s for s in saved if s["id"] == sid), None)
    if not entry:
        ui.error("IDが見つかりません")
        return

    confirm = ui.prompt(f"「{entry['name']}」を削除しますか？ (yes/no)", "no")
    if confirm.lower() == "yes":
        updated = [s for s in saved if s["id"] != sid]
        storage.save_list(SAVED_PROMPTS_FILE, updated)
        ui.success("削除しました")


def select_buzz_preset() -> str | None:
    """Xバズプリセット一覧から選択してプロンプトを返す"""
    ui.section(f"Xバズプリセット ({len(BUZZ_PRESETS)} 件)")
    rows = [
        [p["id"], p["name"][:22], " ".join("#"+t for t in p["tags"][:3])]
        for p in BUZZ_PRESETS
    ]
    ui.table(["ID", "名前", "タグ"], rows, [5, 24, 24])

    bid = ui.prompt("\n使用するID (例: B01)", "")
    if not bid:
        return None
    entry = next((p for p in BUZZ_PRESETS if p["id"] == bid.upper()), None)
    if not entry:
        ui.error("IDが見つかりません")
        return None

    ui.section(f"{entry['name']}")
    print(f"  タグ  : {' '.join('#'+t for t in entry['tags'])}")
    print(f"  狙い  : {ui.Color.YELLOW}{entry['buzz_point']}{ui.Color.RESET}")
    print(f"  Prompt: {ui.Color.GREEN}{entry['prompt']}{ui.Color.RESET}\n")
    return entry["prompt"]


def run() -> str | None:
    """
    プロンプトビルダーのメインエントリーポイント。
    生成に使うプロンプト文字列を返す (キャンセル時は None)。
    """
    while True:
        choice = ui.menu("プロンプトメニュー", [
            ("1", "Xバズプリセット (おすすめ)"),
            ("2", "新規作成 (ビルダー)"),
            ("3", "保存済みから選択"),
            ("4", "保存済みを削除"),
            ("0", "戻る"),
        ])

        if choice == "1":
            result = select_buzz_preset()
            if result:
                return result
        elif choice == "2":
            result = build_interactive()
            if result:
                return result
        elif choice == "3":
            result = select_saved()
            if result:
                return result
        elif choice == "4":
            delete_saved()
        elif choice == "0":
            return None

#!/usr/bin/env python3
"""
Grok Aurora 最適化プロンプト集
キャラクター「凪 (Nagi)」用

Grok Auroraの特性：
- 自然言語で詳細に書くほど精度UP
- カメラ・レンズ指定が効果的
- 「しないこと」を書くとブレ防止
- 2026年1月アップデートで肌テクスチャが大幅改善
"""

# ══════════════════════════════════════════════════════════════════════════════
# キャラクター固定設定（全シーン共通）
# ══════════════════════════════════════════════════════════════════════════════

CHARACTER_BASE = """
A photorealistic portrait of a 23-year-old Japanese woman named Nagi.
She has medium-length brown hair with a natural slight wave,
single eyelids with deep, melancholic dark brown eyes,
porcelain-smooth fair skin with a natural glow,
minimal makeup — just a hint of lip tint and soft eyebrows.
She has a delicate, quietly beautiful face with a subtle,
contemplative expression — not quite smiling, not quite sad.
She looks like she has a secret she's keeping to herself.
"""

CAMERA_BASE = "Shot on Sony A7R V with 85mm f/1.4 lens, shallow depth of field."
STYLE_BASE  = "Film grain texture, muted pastel color palette, cinematic color grading."
NEGATIVE    = "Do not make her look anime, cartoon, or illustrated. No heavy makeup, no explicit content, no watermarks."


# ══════════════════════════════════════════════════════════════════════════════
# シーン別プロンプト
# ══════════════════════════════════════════════════════════════════════════════

GROK_PROMPTS = {

    "桜_昼": f"""{CHARACTER_BASE}
She is sitting alone under a cherry blossom tree in a quiet Tokyo park.
Soft pink petals are gently falling around her.
She is wearing a white ribbed cotton blouse and cream-colored wide-leg pants.
Her gaze is slightly downward, watching a petal fall.
The lighting is soft golden afternoon sunlight filtering through the blossoms,
creating a dreamy, slightly overexposed glow on her hair and shoulders.
The background is a soft bokeh of pink and white blossoms.
{CAMERA_BASE}
{STYLE_BASE}
Vertical 9:16 portrait composition. {NEGATIVE}
""",

    "桜_夕暮れ": f"""{CHARACTER_BASE}
She is standing under cherry blossom trees at dusk in a Japanese park.
She is wearing a simple white dress, hair slightly disheveled by the breeze.
A few petals rest on her hair and shoulders.
Her eyes are looking directly at the camera with a quiet, searching gaze — like she's asking a question.
Lighting: warm orange-pink sunset backlighting creating a soft halo effect around her silhouette.
{CAMERA_BASE}
{STYLE_BASE}
Vertical 9:16 portrait composition. {NEGATIVE}
""",

    "深夜カフェ": f"""{CHARACTER_BASE}
She is sitting alone at a window seat in a dimly lit, retro Japanese coffee shop at midnight.
It is raining outside — you can see rain streaks on the dark window glass behind her.
She is cradling a white ceramic coffee cup with both hands.
She is wearing an oversized caramel-colored knit sweater.
Her eyes are looking out the window, slightly unfocused, lost in thought.
Lighting: warm tungsten lamp from above casting soft shadows, moody interior ambiance.
The reflection of the rain and street lights is visible on the window.
{CAMERA_BASE}
{STYLE_BASE}
Vertical 9:16 portrait composition. {NEGATIVE}
""",

    "夜の窓辺": f"""{CHARACTER_BASE}
She is standing at an apartment window at night, looking out at the city lights below.
She is wearing an oversized white t-shirt as if she just woke up or is about to sleep.
Her hair is slightly messy. One hand rests on the cold glass.
Her face is in semi-profile, partially lit by the blue-white glow of the city below.
Outside the window: blurred Tokyo city lights and a dark rainy sky.
Lighting: only the cool city light illuminating half her face — dramatic chiaroscuro effect.
{CAMERA_BASE}
{STYLE_BASE}
Vertical 9:16 portrait composition. {NEGATIVE}
""",

    "朝の光": f"""{CHARACTER_BASE}
She is lying in bed in soft morning light, just waking up.
White linen sheets, a minimalist bedroom with sheer curtains.
Golden morning sunlight streams through the curtains, creating lens flare and god rays.
Her hair is spread on the pillow, slightly tangled.
She is wearing a simple white pajama top.
Her eyes are half-open, expression dreamy and slightly melancholic.
She seems to be savoring the last moment before the day begins.
{CAMERA_BASE}
{STYLE_BASE}
Vertical 9:16 portrait composition. {NEGATIVE}
""",

    "夏の夜_浴衣": f"""{CHARACTER_BASE}
She is at a summer night festival (夏祭り) in Japan, slightly apart from the crowd.
She is wearing a light pink yukata with a delicate floral pattern and matching obi.
Her hair is loosely pinned up with a simple kanzashi.
She is holding a small paper fan, looking slightly away from the camera.
Background: warm orange lantern lights, blurred festival crowd, and fireflies.
Lighting: soft warm glow from multiple paper lanterns creating a romantic, nostalgic atmosphere.
{CAMERA_BASE}
{STYLE_BASE}
Vertical 9:16 portrait composition. {NEGATIVE}
""",

    "雨の日": f"""{CHARACTER_BASE}
She is standing in a quiet Tokyo alley on a rainy evening.
She holds a clear umbrella. The rain is visible.
She is wearing a light beige trench coat over a simple black turtleneck.
Puddles reflect the neon signs and streetlights around her.
Her expression is calm but distant — like she prefers the rain to company.
Lighting: wet reflective streets, neon bokeh in background, soft fill light on her face.
{CAMERA_BASE}
{STYLE_BASE}
Vertical 9:16 portrait composition. {NEGATIVE}
""",

    "TikTok_ダンス": f"""{CHARACTER_BASE}
She is caught mid-movement, dancing slowly and gracefully outdoors at night.
Her eyes are closed, lost in the music.
She is wearing a simple white slip dress. Her brown hair flows with the movement.
The background is blurred city lights and cherry blossoms.
Motion blur on her hair and dress suggests gentle movement, like a slow dance.
Lighting: soft blue moonlight with warm bokeh from city lights.
{CAMERA_BASE}
{STYLE_BASE}
Vertical 9:16 portrait composition. {NEGATIVE}
""",
}


# ══════════════════════════════════════════════════════════════════════════════
# 一貫性を保つためのコツ
# ══════════════════════════════════════════════════════════════════════════════

CONSISTENCY_TIPS = """
【Grokでキャラクターを一貫させるコツ】

1. 毎回 CHARACTER_BASE の説明を冒頭に入れる
   → 顔の特徴を毎回指定することが重要

2. 気に入った画像が出たら「シード固定」のメモを残す
   → Grokでは同じプロンプトでも少し変わるため、
     気に入ったものはスクショを必ず保存

3. 気に入らない場合の修正指示例：
   - 「もっと自然な表情に」
   - 「目をもう少し細く、憂いのある感じに」
   - 「肌をもう少し白く透明感を出して」
   - 「背景のボケをもっと強く」

4. LoRA的な一貫性を出す方法：
   → 最初に1枚気に入った画像を生成
   → その画像を添付して「この人物のまま〇〇シーンで」と指示
   （Grokはマルチモーダル対応）

5. アスペクト比：
   → 「縦長 9:16 の縦向き」と必ず指定
"""

WORKFLOW = """
【Grok → TikTok動画 ワークフロー】

Step 1: Grokで画像生成
  → 上記プロンプトをGrok.comまたはX(Twitter)のGrokで使用
  → 各シーンで3〜5枚生成して最良を選ぶ

Step 2: 画像を保存
  → /home/user/claude-test/photos/ に保存

Step 3: 動画生成
  → python dance_video_editor.py --photos ./photos --bpm 115 --output nagi_dance.mp4

Step 4: X / TikTokに投稿
  → ai_character_system.py のカレンダー通りに投稿
"""


# ══════════════════════════════════════════════════════════════════════════════
# 出力
# ══════════════════════════════════════════════════════════════════════════════

def print_all():
    print("=" * 60)
    print("  Grok Aurora プロンプト集 — キャラ「凪 (Nagi)」")
    print("=" * 60)

    for scene, prompt in GROK_PROMPTS.items():
        print(f"\n{'─'*60}")
        print(f"【シーン: {scene}】")
        print(f"{'─'*60}")
        print(prompt.strip())

    print("\n" + "=" * 60)
    print(CONSISTENCY_TIPS)
    print(WORKFLOW)

    # テキストファイルにも保存
    with open("nagi_grok_prompts.txt", "w", encoding="utf-8") as f:
        f.write("Grok Aurora プロンプト集 — 凪 (Nagi)\n\n")
        for scene, prompt in GROK_PROMPTS.items():
            f.write(f"【{scene}】\n{prompt.strip()}\n\n{'─'*60}\n\n")
        f.write(CONSISTENCY_TIPS)
        f.write(WORKFLOW)

    print("✅ nagi_grok_prompts.txt に保存しました")


if __name__ == "__main__":
    print_all()

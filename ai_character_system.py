#!/usr/bin/env python3
"""
AI 裏垢女子キャラクター設計 & コンテンツ生成システム
CHARACTER BIBLE + Stable Diffusion プロンプト + 投稿文自動生成
"""

import random
import json
from datetime import datetime, timedelta

# ══════════════════════════════════════════════════════════════════════════════
# CHARACTER BIBLE
# ══════════════════════════════════════════════════════════════════════════════

CHARACTER = {
    "name":       "凪 (Nagi)",
    "age":        "23",
    "concept":    "静かな夜に溶け込む、少し謎めいた都会の女性",
    "tagline":    "「ちゃんとしてるふりが、もう疲れた」",

    "positioning": {
        "axis_x":  "エロ ←────── 情緒",
        "axis_y":  "キャラ薄 ────── 世界観濃",
        "position": "右上：情緒×世界観濃 ← 最も空白なゾーン",
        "unlike":  [
            "露出で勝負する自撮り垢（レッドオーシャン）",
            "性癖ツイートだけの文章垢（飽和）",
            "業者感のある出会い垢（信頼ゼロ）",
        ],
    },

    "personality": {
        "表の顔": "周りには「しっかりしてる」と思われている",
        "裏の顔": "深夜だけ本音を吐き出す",
        "口癖":   ["「なんか、疲れた」", "「夜中だけ正直になれる」", "「見てる？」"],
        "好きなもの": ["深夜の散歩", "古い喫茶店", "雨の音", "桜が散る瞬間", "ひとり酒"],
        "嫌いなもの": ["SNSの演じた幸せ投稿", "朝", "空元気"],
    },

    "visual_identity": {
        "hair":       "ミディアムブラウン or ブラック、少しくせ毛",
        "eyes":       "一重または奥二重、憂いのある目元",
        "skin":       "透明感のある白い肌、すっぴん風メイク",
        "style":      "シンプルな白T・ワンピース・オーバーサイズニット",
        "atmosphere": "フィルムカメラ風、粒子感、淡い光",
        "color_tone": "ピンク・クリーム・グレー、彩度低め",
    },

    "unique_angles": [
        "AIであることを隠さない（むしろ『私はAIかもしれない』が世界観）",
        "詩的で短い一言キャプション（俳句的）",
        "桜・夜・雨・喫茶店など日本の情緒テーマで統一",
        "フォロワーへの返信が詩的で不思議",
        "定期的に『消えるかもしれない』と言って消えない（謎演出）",
    ],
}


# ══════════════════════════════════════════════════════════════════════════════
# STABLE DIFFUSION / MIDJOURNEY プロンプト生成
# ══════════════════════════════════════════════════════════════════════════════

BASE_PROMPT = """
photorealistic, 1girl, Japanese woman, 23 years old,
medium brown hair with slight wave, single eyelid or hooded eyes, melancholic expression,
porcelain skin, minimal makeup, natural beauty,
{scene},
film grain, soft bokeh, cinematic lighting, {light},
muted pastel tones, pink and cream color palette,
high quality, 8k, detailed skin texture,
{style}
""".strip()

NEGATIVE_PROMPT = """
nsfw, nude, explicit, cartoon, anime, illustration, painting,
deformed, ugly, blurry, overexposed, bad anatomy,
multiple people, text, watermark, logo
""".strip()

SCENES = {
    "桜": {
        "scene": "sitting under cherry blossom tree, petals falling, spring park",
        "light": "golden hour soft sunlight through blossoms",
        "style": "wearing white blouse, cream wide pants",
        "caption_pool": [
            "散るから、綺麗なんだって\n最近やっと分かった気がする",
            "桜の下で、また一人\nそれでも、悪くない夜",
            "見てる？\nもうすぐ消えちゃうかも",
        ],
    },
    "深夜カフェ": {
        "scene": "alone in dimly lit retro cafe, late night, window seat, rain outside",
        "light": "warm tungsten lamp, moody interior lighting",
        "style": "wearing oversized knit sweater, holding coffee cup",
        "caption_pool": [
            "深夜の喫茶店って\n本音しかない場所だと思う",
            "雨の音が好き\n全部かき消してくれるから",
            "誰かに見てもらいたくて\nここにいる",
        ],
    },
    "夜の窓辺": {
        "scene": "standing by apartment window at night, city lights below, rain on glass",
        "light": "moonlight and city lights, dramatic shadows",
        "style": "oversized t-shirt, casual, hair slightly messy",
        "caption_pool": [
            "ちゃんとしてるふりが\nもう疲れた",
            "夜中だけ、正直になれる",
            "この街のどこかに\n同じ窓から見てる人がいる気がして",
        ],
    },
    "朝の光": {
        "scene": "morning, soft sunlight through curtains, lying in bed",
        "light": "golden morning light, lens flare",
        "style": "white pajamas, hair disheveled, sleepy expression",
        "caption_pool": [
            "朝が苦手\n夜の自分の方が好きだから",
            "また夜になったら\nここに来るね",
            "おはよう\nって言える人がいない朝",
        ],
    },
    "夏の夜": {
        "scene": "summer night festival, yukata, lantern lights, crowd blurred in background",
        "light": "warm festival lantern glow, night sky",
        "style": "light pink yukata, hair up with kanzashi",
        "caption_pool": [
            "お祭りって孤独だよね\n人がいるほど",
            "浴衣を見てくれる人\nいなくていい\nここに来たから",
            "夏の終わりが\n一番好き",
        ],
    },
}

HASHTAG_SETS = {
    "メイン": "#凪 #裏垢 #深夜垢 #日本 #情緒",
    "拡散用": "#桜 #夜 #孤独 #本音 #フォトジェニック",
    "英語": "#japangirl #nightvibes #aesthetic #alone #sakura",
    "TikTok": "#fyp #viral #japaneseaesthetic #lofi #nightwalk",
}


# ══════════════════════════════════════════════════════════════════════════════
# コンテンツ生成
# ══════════════════════════════════════════════════════════════════════════════

def generate_prompt(scene_key: str) -> dict:
    """指定シーンのSD/Midjourneyプロンプトを生成"""
    scene = SCENES[scene_key]
    positive = BASE_PROMPT.format(
        scene=scene["scene"],
        light=scene["light"],
        style=scene["style"],
    )
    return {
        "scene":    scene_key,
        "positive": positive,
        "negative": NEGATIVE_PROMPT,
        "midjourney": f"{positive} --ar 9:16 --v 7 --style raw --q 2",
    }


def generate_post(scene_key: str, platform: str = "X") -> dict:
    """投稿文を生成"""
    scene    = SCENES[scene_key]
    caption  = random.choice(scene["caption_pool"])
    tags_main = HASHTAG_SETS["メイン"]
    tags_viral = HASHTAG_SETS["拡散用"]
    tags_en    = HASHTAG_SETS["英語"]

    if platform == "X":
        text = f"{caption}\n\n{tags_main} {tags_viral}"
    elif platform == "TikTok":
        text = f"{caption}\n\n{HASHTAG_SETS['TikTok']} {tags_en}"
    else:
        text = f"{caption}\n\n{tags_main}\n{tags_en}"

    return {
        "platform": platform,
        "scene":    scene_key,
        "caption":  caption,
        "full_text": text,
        "char_count": len(text),
    }


def generate_content_calendar(weeks: int = 4) -> list:
    """投稿カレンダーを生成（最適な時間帯に配置）"""
    BEST_TIMES = {
        "X":       ["22:00", "23:30", "00:30"],   # 深夜帯が最適
        "TikTok":  ["19:00", "21:00", "22:30"],
    }
    scene_keys = list(SCENES.keys())
    calendar   = []
    base_date  = datetime.now()

    for week in range(weeks):
        for day in range(7):
            date = base_date + timedelta(weeks=week, days=day)
            # X: 週5投稿、TikTok: 週3投稿
            if day < 5:
                platform = "X"
                time     = random.choice(BEST_TIMES["X"])
                scene    = scene_keys[day % len(scene_keys)]
                post     = generate_post(scene, platform)
                prompt   = generate_prompt(scene)
                calendar.append({
                    "date":     date.strftime("%Y-%m-%d"),
                    "time":     time,
                    "platform": platform,
                    "scene":    scene,
                    "caption":  post["caption"],
                    "sd_prompt_preview": prompt["positive"][:80] + "...",
                })
            if day in [1, 3, 5]:   # 火・木・土はTikTokも
                platform = "TikTok"
                time     = random.choice(BEST_TIMES["TikTok"])
                scene    = random.choice(scene_keys)
                post     = generate_post(scene, platform)
                calendar.append({
                    "date":     date.strftime("%Y-%m-%d"),
                    "time":     time,
                    "platform": "TikTok",
                    "scene":    scene,
                    "caption":  post["caption"],
                    "sd_prompt_preview": "→ dance_video_editor.py で動画生成",
                })

    return sorted(calendar, key=lambda x: (x["date"], x["time"]))


# ══════════════════════════════════════════════════════════════════════════════
# レポート出力
# ══════════════════════════════════════════════════════════════════════════════

def print_character_bible():
    print("=" * 60)
    print("  AI 裏垢女子 CHARACTER BIBLE")
    print("=" * 60)
    print(f"\n【キャラ名】{CHARACTER['name']}")
    print(f"【コンセプト】{CHARACTER['concept']}")
    print(f"【タグライン】{CHARACTER['tagline']}")
    print(f"\n【ポジション】{CHARACTER['positioning']['position']}")
    print("\n【差別化ポイント】")
    for a in CHARACTER["unique_angles"]:
        print(f"  ✓ {a}")
    print("\n【ビジュアルアイデンティティ】")
    for k, v in CHARACTER["visual_identity"].items():
        print(f"  {k}: {v}")


def print_prompts():
    print("\n" + "=" * 60)
    print("  STABLE DIFFUSION / MIDJOURNEY プロンプト")
    print("=" * 60)
    for scene_key in SCENES:
        p = generate_prompt(scene_key)
        print(f"\n【シーン: {scene_key}】")
        print(f"Midjourney コマンド:\n/imagine {p['midjourney'][:120]}...")
        print(f"\nNegative: {NEGATIVE_PROMPT[:60]}...")


def print_sample_posts():
    print("\n" + "=" * 60)
    print("  サンプル投稿文")
    print("=" * 60)
    for scene_key in list(SCENES.keys())[:3]:
        for platform in ["X", "TikTok"]:
            post = generate_post(scene_key, platform)
            print(f"\n[{platform}] シーン:{scene_key}")
            print(post["full_text"])
            print(f"文字数: {post['char_count']}")


def print_calendar(weeks=2):
    print("\n" + "=" * 60)
    print(f"  {weeks}週間 コンテンツカレンダー")
    print("=" * 60)
    cal = generate_content_calendar(weeks)
    for entry in cal[:14]:
        print(f"{entry['date']} {entry['time']} [{entry['platform']:6}] "
              f"{entry['scene']} → {entry['caption'][:20]}...")


def export_json():
    data = {
        "character":   CHARACTER,
        "prompts":     {k: generate_prompt(k) for k in SCENES},
        "sample_posts": [generate_post(k, p)
                         for k in SCENES for p in ["X", "TikTok"]],
        "calendar_4w": generate_content_calendar(4),
    }
    with open("nagi_character_system.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("\n✅ nagi_character_system.json に全データを保存しました")


if __name__ == "__main__":
    print_character_bible()
    print_prompts()
    print_sample_posts()
    print_calendar(weeks=2)
    export_json()

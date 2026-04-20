#!/usr/bin/env python3
"""
TikTok Viral Dance Video Editor
写真からバズるダンス動画を自動生成するツール

使い方:
    python dance_video_editor.py --photos ./photos --bpm 128 --output my_dance.mp4
"""

import os
import sys
import math
import random
import argparse
import glob
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageOps
import imageio

TIKTOK_W = 1080
TIKTOK_H = 1920
FPS = 30


# ─── Image helpers ────────────────────────────────────────────────────────────

def fit_to_tiktok(img: Image.Image) -> Image.Image:
    """写真をTikTokサイズ(9:16)にクロップ・リサイズ"""
    img = img.convert("RGB")
    src_w, src_h = img.size
    src_ratio = src_w / src_h
    tgt_ratio = TIKTOK_W / TIKTOK_H

    if src_ratio > tgt_ratio:
        # 横長 → 高さ基準でリサイズして横をクロップ
        new_h = TIKTOK_H
        new_w = int(src_w * TIKTOK_H / src_h)
    else:
        # 縦長 → 幅基準でリサイズして縦をクロップ
        new_w = TIKTOK_W
        new_h = int(src_h * TIKTOK_W / src_w)

    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - TIKTOK_W) // 2
    top = (new_h - TIKTOK_H) // 2
    return img.crop((left, top, left + TIKTOK_W, top + TIKTOK_H))


def img_to_array(img: Image.Image) -> np.ndarray:
    return np.array(img, dtype=np.uint8)


def array_to_img(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ─── Effects ──────────────────────────────────────────────────────────────────

def zoom_frame(img: Image.Image, scale: float) -> Image.Image:
    """中心を基点にズームイン/アウト"""
    w, h = img.size
    new_w = int(w / scale)
    new_h = int(h / scale)
    left = (w - new_w) // 2
    top = (h - new_h) // 2
    cropped = img.crop((left, top, left + new_w, top + new_h))
    return cropped.resize((w, h), Image.LANCZOS)


def shake_frame(img: Image.Image, strength: int) -> Image.Image:
    """カメラシェイクエフェクト"""
    dx = random.randint(-strength, strength)
    dy = random.randint(-strength, strength)
    arr = np.array(img)
    shifted = np.roll(np.roll(arr, dx, axis=1), dy, axis=0)
    return Image.fromarray(shifted.astype(np.uint8))


def glitch_frame(img: Image.Image, strength: int = 12) -> Image.Image:
    """RGBチャンネルをずらすグリッチエフェクト"""
    arr = np.array(img, dtype=np.int32)
    r, g, b = arr[:, :, 0].copy(), arr[:, :, 1].copy(), arr[:, :, 2].copy()
    dx = random.randint(-strength, strength)
    dy = random.randint(-strength, strength)
    r = np.roll(r, dx, axis=1)
    b = np.roll(b, dy, axis=0)
    out = np.stack([r, g, b], axis=2)
    return array_to_img(out)


def color_pop(img: Image.Image, t: float = 1.4) -> Image.Image:
    """彩度を上げてバズりやすい鮮やかな色に"""
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(t)
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(1.15)


def add_vignette(img: Image.Image, strength: float = 0.6) -> Image.Image:
    """周辺光量落ちでドラマティックな雰囲気に"""
    arr = np.array(img, dtype=np.float32)
    rows, cols = arr.shape[:2]
    cx, cy = cols / 2, rows / 2
    x = np.linspace(0, cols, cols)
    y = np.linspace(0, rows, rows)
    X, Y = np.meshgrid(x, y)
    dist = np.sqrt(((X - cx) / cx) ** 2 + ((Y - cy) / cy) ** 2)
    mask = 1 - np.clip(dist * strength, 0, 1)
    mask = mask[:, :, np.newaxis]
    arr = arr * mask
    return array_to_img(arr)


def flash_overlay(img: Image.Image, alpha: float, color=(255, 255, 255)) -> Image.Image:
    """フラッシュオーバーレイ"""
    overlay = Image.new("RGB", img.size, color)
    return Image.blend(img, overlay, alpha)


def ken_burns(img: Image.Image, t: float, direction: str = "in") -> Image.Image:
    """ケンバーンズ効果（ゆっくりズーム＋パン）"""
    if direction == "in":
        scale = 1.0 + 0.15 * t
    else:
        scale = 1.15 - 0.15 * t
    return zoom_frame(img, scale)


def beat_pulse(img: Image.Image, beat_t: float) -> Image.Image:
    """ビートに合わせてドンと拡大するパルス効果"""
    # beat_t: 0=ビート直後, 1=次のビート直前
    # 最初に強くズームして徐々に戻る
    scale = 1.0 + 0.08 * math.exp(-beat_t * 4)
    return zoom_frame(img, scale)


def strobe(img: Image.Image, beat_t: float, n: int = 3) -> Image.Image:
    """ビート後半にストロボ効果"""
    if beat_t < 0.3:
        cycle = (beat_t * n * FPS) % 1.0
        if cycle < 0.5:
            alpha = 0.6 * (1 - beat_t / 0.3)
            return flash_overlay(img, alpha)
    return img


# ─── Transition builders ───────────────────────────────────────────────────────

def build_transition_frames(img_a: Image.Image, img_b: Image.Image,
                             n_frames: int, style: str) -> list:
    """2枚の写真間のトランジションフレームを生成"""
    frames = []
    for i in range(n_frames):
        t = i / max(n_frames - 1, 1)  # 0.0 → 1.0

        if style == "flash":
            alpha = math.sin(t * math.pi)
            frame = flash_overlay(img_a if t < 0.5 else img_b, alpha * 0.95)

        elif style == "zoom_flash":
            if t < 0.5:
                scale = 1.0 + t * 0.4
                frame = zoom_frame(img_a, scale)
                frame = flash_overlay(frame, t * 1.8)
            else:
                scale = 1.2 - (t - 0.5) * 0.4
                frame = zoom_frame(img_b, max(scale, 1.0))
                frame = flash_overlay(frame, (1 - t) * 1.8)

        elif style == "glitch":
            if t < 0.5:
                frame = glitch_frame(img_a, strength=int(20 * t * 2))
                frame = flash_overlay(frame, t * 0.7, color=(0, 255, 255))
            else:
                frame = glitch_frame(img_b, strength=int(20 * (1 - t) * 2))
                frame = flash_overlay(frame, (1 - t) * 0.7, color=(255, 0, 255))

        elif style == "slide_left":
            offset = int(TIKTOK_W * t)
            canvas = Image.new("RGB", (TIKTOK_W, TIKTOK_H))
            canvas.paste(img_a, (-offset, 0))
            canvas.paste(img_b, (TIKTOK_W - offset, 0))
            frame = canvas

        elif style == "whip":
            # 高速スワイプ＋モーションブラー風
            if t < 0.4:
                offset = int(TIKTOK_W * (t / 0.4) ** 2)
                canvas = Image.new("RGB", (TIKTOK_W, TIKTOK_H), (0, 0, 0))
                canvas.paste(img_a, (-offset, 0))
                frame = canvas
            else:
                offset = int(TIKTOK_W * (1 - (t - 0.4) / 0.6))
                canvas = Image.new("RGB", (TIKTOK_W, TIKTOK_H), (0, 0, 0))
                canvas.paste(img_b, (TIKTOK_W - offset, 0))
                frame = canvas

        else:  # crossfade
            frame = Image.blend(img_a, img_b, t)

        frames.append(img_to_array(frame))
    return frames


# ─── Main render ──────────────────────────────────────────────────────────────

TRANSITIONS = ["flash", "zoom_flash", "glitch", "whip", "slide_left"]

EFFECT_STYLES = [
    "beat_pulse",
    "ken_burns_in",
    "ken_burns_out",
    "shake_light",
    "strobe",
]


def render_photo_segment(img: Image.Image, n_frames: int,
                          effect: str, transition_start: int) -> list:
    """1枚の写真に対してビート同期エフェクトを適用したフレーム列を生成"""
    frames = []
    for i in range(n_frames):
        t = i / n_frames          # 写真全体での進行度
        beat_t = (i % transition_start) / transition_start  # ビート内進行度

        frame = img.copy()
        frame = color_pop(frame, 1.35)

        if effect == "beat_pulse":
            frame = beat_pulse(frame, beat_t)

        elif effect == "ken_burns_in":
            frame = ken_burns(frame, t, direction="in")

        elif effect == "ken_burns_out":
            frame = ken_burns(frame, t, direction="out")

        elif effect == "shake_light":
            frame = beat_pulse(frame, beat_t)
            if beat_t < 0.15:
                frame = shake_frame(frame, strength=8)

        elif effect == "strobe":
            frame = beat_pulse(frame, beat_t)
            frame = strobe(frame, beat_t)

        frame = add_vignette(frame, strength=0.5)
        frames.append(img_to_array(frame))

    return frames


def build_video(photo_paths: list, bpm: int, beats_per_photo: int,
                transition_beats: int, output_path: str, seed: int = 42):
    random.seed(seed)

    beat_frames = int(FPS * 60 / bpm)
    segment_frames = beat_frames * beats_per_photo
    transition_frames = beat_frames * transition_beats

    print(f"\n📱 TikTok Viral Dance Video Editor")
    print(f"   BPM: {bpm}  |  フレームレート: {FPS}fps")
    print(f"   写真1枚あたり: {beats_per_photo}拍 ({segment_frames}フレーム)")
    print(f"   トランジション: {transition_beats}拍 ({transition_frames}フレーム)")
    print(f"   写真枚数: {len(photo_paths)}枚")

    # 写真を読み込んでTikTokサイズに変換
    print("\n🖼  写真を読み込み中...")
    images = []
    for p in photo_paths:
        img = Image.open(p)
        img = fit_to_tiktok(img)
        images.append(img)
        print(f"   ✓ {Path(p).name}")

    all_frames = []
    n = len(images)
    effects = random.choices(EFFECT_STYLES, k=n)
    transitions = random.choices(TRANSITIONS, k=n - 1)

    print("\n🎬 レンダリング中...")
    for i, img in enumerate(images):
        effect = effects[i]
        seg_frames = segment_frames - (transition_frames // 2 if i > 0 else 0) \
                                    - (transition_frames // 2 if i < n - 1 else 0)
        seg_frames = max(seg_frames, beat_frames)

        seg = render_photo_segment(img, seg_frames, effect, beat_frames)
        all_frames.extend(seg)

        print(f"   [{i+1}/{n}] {Path(photo_paths[i]).name} → {effect} ({len(seg)}f)")

        if i < n - 1:
            t_style = transitions[i]
            trans = build_transition_frames(images[i], images[i + 1],
                                            transition_frames, t_style)
            all_frames.extend(trans)
            print(f"        └─ transition: {t_style} ({len(trans)}f)")

    total_sec = len(all_frames) / FPS
    print(f"\n💾 書き出し中... ({len(all_frames)}フレーム / {total_sec:.1f}秒)")

    writer = imageio.get_writer(
        output_path,
        fps=FPS,
        codec="libx264",
        macro_block_size=1,
        output_params=["-crf", "18", "-preset", "fast"],
        pixelformat="yuv420p",
    )
    for frame in all_frames:
        writer.append_data(frame)
    writer.close()

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅ 完成！ → {output_path}")
    print(f"   サイズ: {size_mb:.1f} MB  |  長さ: {total_sec:.1f}秒")
    print(f"   解像度: {TIKTOK_W}×{TIKTOK_H} (TikTok 9:16)")


# ─── Demo photo generator (サンプル写真がない場合) ───────────────────────────

def generate_demo_photos(out_dir: str, n: int = 6) -> list:
    """デモ用のカラフルなサンプル写真を生成"""
    os.makedirs(out_dir, exist_ok=True)
    colors = [
        ("#FF6B6B", "#FFE66D", "🔥 DANCE"),
        ("#4ECDC4", "#44A08D", "💃 VIBE"),
        ("#A770EF", "#CF8BF3", "✨ VIRAL"),
        ("#F7971E", "#FFD200", "🎵 BEAT"),
        ("#56CCF2", "#2F80ED", "💫 FLOW"),
        ("#EB5757", "#000000", "🔥 FIRE"),
    ]
    paths = []
    for i in range(n):
        color1, color2, text = colors[i % len(colors)]

        img = Image.new("RGB", (1080, 1920))
        draw = ImageDraw.Draw(img)

        # グラデーション背景
        c1 = tuple(int(color1[j:j+2], 16) for j in (1, 3, 5))
        c2 = tuple(int(color2[j:j+2], 16) for j in (1, 3, 5))
        for y in range(1920):
            t = y / 1920
            r = int(c1[0] * (1 - t) + c2[0] * t)
            g = int(c1[1] * (1 - t) + c2[1] * t)
            b = int(c1[2] * (1 - t) + c2[2] * t)
            draw.line([(0, y), (1080, y)], fill=(r, g, b))

        # テキスト（大きめ）
        draw.text((540, 900), text, fill="white", anchor="mm",
                  font=None)
        draw.text((540, 1000), f"Photo {i+1}", fill="white", anchor="mm",
                  font=None)

        # デコレーション
        for _ in range(20):
            x, y = random.randint(0, 1080), random.randint(0, 1920)
            r2 = random.randint(10, 60)
            alpha_color = (255, 255, 255)
            draw.ellipse([x-r2, y-r2, x+r2, y+r2],
                         outline=alpha_color, width=3)

        path = os.path.join(out_dir, f"demo_{i+1:02d}.jpg")
        img.save(path, quality=95)
        paths.append(path)

    return paths


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="TikTok Viral Dance Video Editor — 写真からバズる動画を自動生成"
    )
    parser.add_argument(
        "--photos", "-p",
        help="写真フォルダのパス（例: ./my_photos）",
        default=None,
    )
    parser.add_argument(
        "--bpm", "-b",
        type=int,
        default=128,
        help="音楽のBPM（デフォルト: 128）",
    )
    parser.add_argument(
        "--beats-per-photo", "-n",
        type=int,
        default=4,
        help="1枚の写真を表示する拍数（デフォルト: 4）",
    )
    parser.add_argument(
        "--transition-beats", "-t",
        type=int,
        default=1,
        help="トランジションの拍数（デフォルト: 1）",
    )
    parser.add_argument(
        "--output", "-o",
        default="dance_video.mp4",
        help="出力ファイル名（デフォルト: dance_video.mp4）",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="デモ写真を自動生成してテスト",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="ランダムシード（エフェクトの再現性）",
    )

    args = parser.parse_args()

    if args.demo or args.photos is None:
        print("🎨 デモ写真を生成中...")
        photo_dir = "./demo_photos"
        photo_paths = generate_demo_photos(photo_dir, n=6)
        print(f"   {len(photo_paths)}枚のデモ写真を生成しました")
    else:
        exts = ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG")
        photo_paths = []
        for ext in exts:
            photo_paths.extend(glob.glob(os.path.join(args.photos, ext)))
        photo_paths.sort()

        if not photo_paths:
            print(f"❌ エラー: {args.photos} に写真が見つかりません")
            sys.exit(1)

    build_video(
        photo_paths=photo_paths,
        bpm=args.bpm,
        beats_per_photo=args.beats_per_photo,
        transition_beats=args.transition_beats,
        output_path=args.output,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()

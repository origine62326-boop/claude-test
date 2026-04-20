#!/usr/bin/env python3
"""
桜ダンス動画生成スクリプト
Maps Dance スタイル (115 BPM) × 桜エフェクト × TikTok最適化
"""

import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import imageio

# ── 設定 ──────────────────────────────────────────────────────────────────────
FPS       = 30
BPM       = 115          # Maps / 桜系の曲に合うテンポ
W, H      = 1080, 1920
BEAT_F    = int(FPS * 60 / BPM)   # 1拍 = フレーム数
PHOTO     = "photos/sakura.jpg"
OUTPUT    = "sakura_dance_v2.mp4"

random.seed(7)

# ── 花びら管理 ────────────────────────────────────────────────────────────────
class Petal:
    COLORS = [
        (255, 182, 193, 180),   # ライトピンク
        (255, 192, 203, 160),   # ピンク
        (255, 218, 224, 140),   # 薄ピンク
        (255, 240, 245, 120),   # ラベンダーブラッシュ
    ]
    def __init__(self):
        self.reset(init=True)

    def reset(self, init=False):
        self.x  = random.uniform(0, W)
        self.y  = random.uniform(-200, 0) if not init else random.uniform(-H, H)
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(1.5, 4.0)
        self.rot   = random.uniform(0, 360)
        self.vrot  = random.uniform(-3, 3)
        self.w  = random.randint(14, 28)
        self.h  = int(self.w * random.uniform(0.5, 0.8))
        self.color = random.choice(self.COLORS)
        self.wave  = random.uniform(0, 2 * math.pi)

    def update(self, frame):
        self.wave += 0.05
        self.x  += self.vx + math.sin(self.wave) * 0.8
        self.y  += self.vy
        self.rot += self.vrot
        if self.y > H + 50:
            self.reset()

    def draw(self, draw: ImageDraw.ImageDraw):
        cx, cy = int(self.x), int(self.y)
        # 回転した楕円（簡易：軸に沿った楕円）
        r = math.radians(self.rot)
        pts = []
        for a in range(0, 360, 30):
            ar = math.radians(a)
            px = cx + self.w * math.cos(ar) * math.cos(r) - self.h * math.sin(ar) * math.sin(r)
            py = cy + self.w * math.cos(ar) * math.sin(r) + self.h * math.sin(ar) * math.cos(r)
            pts.append((px, py))
        draw.polygon(pts, fill=self.color[:3])


PETALS = [Petal() for _ in range(60)]


def draw_petals(base: Image.Image, frame: int) -> Image.Image:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)
    for p in PETALS:
        p.update(frame)
        p.draw(draw)
    base_rgba = base.convert("RGBA")
    merged    = Image.alpha_composite(base_rgba, overlay)
    return merged.convert("RGB")


# ── エフェクト関数 ────────────────────────────────────────────────────────────

def fit(img: Image.Image) -> Image.Image:
    img  = img.convert("RGB")
    sw, sh = img.size
    if sw / sh > W / H:
        nw, nh = int(sw * H / sh), H
    else:
        nw, nh = W, int(sh * W / sw)
    img = img.resize((nw, nh), Image.LANCZOS)
    l, t = (nw - W) // 2, (nh - H) // 2
    return img.crop((l, t, l + W, t + H))


def color_grade_sakura(img: Image.Image) -> Image.Image:
    """桜テーマのカラーグレーディング：暖色・高彩度"""
    img = ImageEnhance.Color(img).enhance(1.5)
    img = ImageEnhance.Brightness(img).enhance(1.05)
    img = ImageEnhance.Contrast(img).enhance(1.1)
    arr = np.array(img, dtype=np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.08, 0, 255)   # R up
    arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.92, 0, 255)   # B down
    return Image.fromarray(arr.astype(np.uint8))


def add_vignette(img: Image.Image, s: float = 0.55) -> Image.Image:
    arr = np.array(img, dtype=np.float32)
    cx, cy = W / 2, H / 2
    X, Y   = np.meshgrid(np.linspace(0, W, W), np.linspace(0, H, H))
    dist   = np.sqrt(((X - cx) / cx) ** 2 + ((Y - cy) / cy) ** 2)
    mask   = (1 - np.clip(dist * s, 0, 1))[:, :, np.newaxis]
    return Image.fromarray(np.clip(arr * mask, 0, 255).astype(np.uint8))


def zoom_center(img: Image.Image, scale: float) -> Image.Image:
    nw, nh = int(W / scale), int(H / scale)
    l, t   = (W - nw) // 2, (H - nh) // 2
    return img.crop((l, t, l + nw, t + nh)).resize((W, H), Image.LANCZOS)


def shake(img: Image.Image, strength: int) -> Image.Image:
    dx, dy = random.randint(-strength, strength), random.randint(-strength, strength)
    arr    = np.array(img)
    return Image.fromarray(np.roll(np.roll(arr, dx, 1), dy, 0).astype(np.uint8))


def flash(img: Image.Image, alpha: float) -> Image.Image:
    white = Image.new("RGB", (W, H), (255, 255, 255))
    return Image.blend(img, white, min(alpha, 1.0))


def glitch(img: Image.Image, strength: int = 18) -> Image.Image:
    arr = np.array(img, dtype=np.int32)
    dx, dy = random.randint(-strength, strength), random.randint(-strength, strength)
    arr[:, :, 0] = np.roll(arr[:, :, 0], dx, axis=1)
    arr[:, :, 2] = np.roll(arr[:, :, 2], dy, axis=0)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ── テキストオーバーレイ ──────────────────────────────────────────────────────

def add_text_overlay(img: Image.Image, frame: int, total: int) -> Image.Image:
    overlay = img.copy().convert("RGBA")
    draw    = ImageDraw.Draw(overlay)

    # 下部グラデーションバー
    bar_h = 320
    for y in range(H - bar_h, H):
        alpha = int(180 * (y - (H - bar_h)) / bar_h)
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    # メインテキスト
    texts = [
        (540, H - 230, "🌸 桜ダンス 🌸",         "white", 72),
        (540, H - 145, "#MapsChallenge",           "#FFB6C1", 48),
        (540, H - 85,  "#桜ダンス #TikTok #バズり", "#FFD0D8", 38),
    ]
    for x, y, text, color, size in texts:
        # シャドウ
        for sdx, sdy in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            draw.text((x + sdx, y + sdy), text, fill=(0, 0, 0, 160),
                      anchor="mm", font=None)
        draw.text((x, y), text, fill=color, anchor="mm", font=None)

    # ビートに合わせたパルスインジケーター（下部中央）
    beat_t = (frame % BEAT_F) / BEAT_F
    pulse_r = int(18 + 10 * math.exp(-beat_t * 5))
    draw.ellipse(
        [W // 2 - pulse_r, H - 40 - pulse_r, W // 2 + pulse_r, H - 40 + pulse_r],
        fill=(255, 182, 193, 200)
    )

    return overlay.convert("RGB")


# ── シーン定義 ────────────────────────────────────────────────────────────────

def make_scene(img: Image.Image, scene: str, n: int, frame_offset: int) -> list:
    """指定シーンのフレーム列を生成"""
    frames = []
    for i in range(n):
        t      = i / max(n - 1, 1)
        beat_t = (i % BEAT_F) / BEAT_F
        f      = img.copy()

        if scene == "ken_in":
            f = zoom_center(f, 1.0 + 0.18 * t)

        elif scene == "ken_out":
            f = zoom_center(f, 1.18 - 0.18 * t)

        elif scene == "beat_pulse":
            scale = 1.0 + 0.07 * math.exp(-beat_t * 4)
            f = zoom_center(f, scale)

        elif scene == "shake_beat":
            scale = 1.0 + 0.07 * math.exp(-beat_t * 4)
            f = zoom_center(f, scale)
            if beat_t < 0.12:
                f = shake(f, 12)

        elif scene == "flash_beat":
            scale = 1.0 + 0.06 * math.exp(-beat_t * 5)
            f = zoom_center(f, scale)
            if beat_t < 0.1:
                f = flash(f, 0.55 * (1 - beat_t / 0.1))

        elif scene == "glitch_beat":
            scale = 1.0 + 0.05 * math.exp(-beat_t * 4)
            f = zoom_center(f, scale)
            if beat_t < 0.15:
                f = glitch(f, strength=int(20 * (1 - beat_t / 0.15)))

        elif scene == "zoom_out_fade":
            f = zoom_center(f, 1.18 - 0.18 * t)
            if t > 0.7:
                f = flash(f, (t - 0.7) / 0.3 * 0.8)

        f = add_vignette(f, 0.5)
        f = draw_petals(f, frame_offset + i)
        f = add_text_overlay(f, frame_offset + i, n)
        frames.append(np.array(f, dtype=np.uint8))

    return frames


# ── メイン ────────────────────────────────────────────────────────────────────

def main():
    print("🌸 桜ダンス動画生成開始")
    print(f"   BPM: {BPM}  |  {FPS}fps  |  {BEAT_F}フレーム/拍\n")

    img = fit(Image.open(PHOTO))
    img = color_grade_sakura(img)

    # シーン構成（拍数 × BEAT_F = フレーム数）
    scenes = [
        ("ken_in",       8),   # ゆっくりズームイン
        ("beat_pulse",   8),   # ビートパルス
        ("flash_beat",   8),   # フラッシュビート
        ("shake_beat",   8),   # シェイク
        ("glitch_beat",  4),   # グリッチ
        ("ken_out",      8),   # ズームアウト
        ("beat_pulse",   8),   # ビートパルス × 2周
        ("zoom_out_fade",4),   # フェードアウト
    ]

    all_frames = []
    frame_off  = 0
    for name, beats in scenes:
        n = BEAT_F * beats
        print(f"   {name:20s} {beats}拍 ({n}フレーム)")
        all_frames.extend(make_scene(img, name, n, frame_off))
        frame_off += n

    total_sec = len(all_frames) / FPS
    print(f"\n💾 書き出し中... {len(all_frames)}フレーム / {total_sec:.1f}秒")

    writer = imageio.get_writer(
        OUTPUT, fps=FPS, codec="libx264",
        macro_block_size=1,
        pixelformat="yuv420p",
        output_params=["-crf", "18", "-preset", "fast"],
    )
    for f in all_frames:
        writer.append_data(f)
    writer.close()

    size_mb = os.path.getsize(OUTPUT) / 1024 / 1024
    print(f"\n✅ 完成！ → {OUTPUT}")
    print(f"   サイズ: {size_mb:.1f} MB  |  長さ: {total_sec:.1f}秒")
    print(f"   解像度: {W}×{H}  |  BPM: {BPM} (Maps スタイル)")


if __name__ == "__main__":
    main()

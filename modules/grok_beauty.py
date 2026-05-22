"""
Grok AI美女画像生成モジュール
xAI Grok の画像生成APIを使ってAI美女画像を生成・管理する
"""

import os
import uuid
import requests
from pathlib import Path
from datetime import datetime

from . import storage, ui, prompt_builder

HISTORY_FILE = "grok_beauty_history.json"
IMAGES_DIR   = Path(__file__).parent.parent / "demo_photos" / "grok_generated"

XAI_API_URL  = "https://api.x.ai/v1/images/generations"
XAI_MODEL    = "grok-2-image-1212"

# プリセットスタイル (X投稿映え重視)
PRESETS = [
    ("natural",  "ナチュラル系",  "A beautiful Japanese woman with natural makeup, soft smile, casual outdoor setting, golden hour lighting, photorealistic"),
    ("cool",     "クール系",      "A stylish Japanese woman, cool expression, urban city background at night, elegant fashion, cinematic lighting, photorealistic"),
    ("elegant",  "清楚系",        "An elegant Japanese woman in simple white dress, clean background, soft diffused light, graceful pose, photorealistic"),
    ("casual",   "カジュアル系",  "A cute Japanese woman in casual street fashion, café background, natural warm lighting, cheerful expression, photorealistic"),
    ("office",   "オフィス系",    "A professional Japanese woman in business attire, modern office setting, confident smile, clean corporate aesthetic, photorealistic"),
    ("custom",   "カスタム",      None),
]

PRESET_MAP = {k: (label, prompt) for k, label, prompt in PRESETS}


def _get_api_key() -> str | None:
    key = os.environ.get("XAI_API_KEY", "").strip()
    return key if key else None


def _ensure_images_dir():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def _load_history() -> list:
    return storage.load_list(HISTORY_FILE)


def _save_history(history: list):
    storage.save_list(HISTORY_FILE, history)


def generate_image(prompt: str, n: int = 1) -> list[dict]:
    """
    Grok APIで画像を生成してURLリストを返す
    Returns list of {"url": str, "revised_prompt": str}
    """
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("XAI_API_KEY が設定されていません。環境変数に設定してください。")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": XAI_MODEL,
        "prompt": prompt,
        "n": n,
        "response_format": "url",
    }

    resp = requests.post(XAI_API_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])


def download_image(url: str, filename: str) -> Path:
    """画像URLをローカルに保存してパスを返す"""
    _ensure_images_dir()
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    path = IMAGES_DIR / filename
    with open(path, "wb") as f:
        f.write(resp.content)
    return path


def run():
    ui.header("Grok AI美女生成", ui.Color.CYAN)

    api_key = _get_api_key()
    if not api_key:
        ui.error("XAI_API_KEY が未設定です")
        ui.info("設定方法: export XAI_API_KEY='xai-xxxxxxxxxx'")
        ui.info("xAI Developer Portal: https://console.x.ai/")
        input("\nEnterで戻る...")
        return

    ui.success(f"API Key: {api_key[:8]}...{api_key[-4:]}")

    while True:
        choice = ui.menu("美女生成メニュー", [
            ("1", "プロンプトビルダーで生成 (推奨)"),
            ("2", "プリセットから生成"),
            ("3", "フリープロンプトで生成"),
            ("4", "生成履歴を表示"),
            ("0", "戻る"),
        ])

        if choice == "1":
            _generate_with_builder()
        elif choice == "2":
            _generate_with_preset()
        elif choice == "3":
            _generate_custom()
        elif choice == "4":
            _show_history()
        elif choice == "0":
            break


def _generate_with_builder():
    prompt = prompt_builder.run()
    if prompt:
        n_raw = ui.prompt("生成枚数 (1-4)", "1")
        try:
            n = max(1, min(4, int(n_raw)))
        except ValueError:
            n = 1
        _run_generation(prompt=prompt, style="ビルダー", n=n)


def _generate_with_preset():
    ui.section("スタイル選択")
    options = [(k, label) for k, label, _ in PRESETS if k != "custom"]
    style_key = ui.menu("スタイル", options)

    label, base_prompt = PRESET_MAP[style_key]
    ui.info(f"ベースプロンプト: {base_prompt[:60]}...")

    extra = ui.prompt("追加指定 (任意。例: 赤いドレス, 桜の背景)")
    prompt = base_prompt
    if extra:
        prompt = f"{base_prompt}, {extra}"

    n_raw = ui.prompt("生成枚数 (1-4)", "1")
    try:
        n = max(1, min(4, int(n_raw)))
    except ValueError:
        n = 1

    _run_generation(prompt=prompt, style=label, n=n)


def _generate_custom():
    ui.section("カスタムプロンプト")
    ui.info("英語推奨。例: A beautiful woman in kimono, cherry blossoms background, photorealistic")
    prompt = ui.prompt("プロンプト")
    if not prompt:
        ui.error("プロンプトを入力してください")
        return

    n_raw = ui.prompt("生成枚数 (1-4)", "1")
    try:
        n = max(1, min(4, int(n_raw)))
    except ValueError:
        n = 1

    _run_generation(prompt=prompt, style="カスタム", n=n)


def _run_generation(prompt: str, style: str, n: int):
    ui.section("生成中...")
    print(f"  プロンプト : {prompt[:70]}")
    print(f"  スタイル   : {style}")
    print(f"  枚数       : {n}")
    print(f"\n  {ui.Color.DIM}Grok APIにリクエスト送信中...{ui.Color.RESET}")

    try:
        results = generate_image(prompt=prompt, n=n)
    except ValueError as e:
        ui.error(str(e))
        return
    except requests.HTTPError as e:
        ui.error(f"API エラー: {e.response.status_code} - {e.response.text[:200]}")
        return
    except requests.RequestException as e:
        ui.error(f"ネットワークエラー: {e}")
        return

    if not results:
        ui.error("画像が生成されませんでした")
        return

    ui.success(f"{len(results)}枚の画像が生成されました")

    history = _load_history()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for i, item in enumerate(results, 1):
        url = item.get("url", "")
        entry_id = str(uuid.uuid4())[:8]
        print(f"\n  [{i}] URL: {url[:80]}...")

        save = ui.prompt(f"  画像 {i} をローカルに保存しますか？ (y/n)", "y")
        local_path = None
        if save.lower() == "y":
            filename = f"{timestamp}_{i}_{entry_id}.jpg"
            try:
                path = download_image(url, filename)
                local_path = str(path)
                ui.success(f"保存完了: {path}")
            except requests.RequestException as e:
                ui.error(f"ダウンロード失敗: {e}")

        history.append({
            "id": entry_id,
            "created_at": ui.now_str(),
            "style": style,
            "prompt": prompt,
            "url": url,
            "local_path": local_path,
        })

    _save_history(history)
    ui.info(f"履歴に {len(results)} 件追加しました")


def _show_history():
    history = _load_history()
    if not history:
        ui.info("生成履歴がありません")
        return

    ui.section(f"生成履歴 (計 {len(history)} 件)")
    rows = [
        [
            h["id"],
            h["created_at"][:16],
            h["style"][:8],
            "✓" if h.get("local_path") else "-",
            h["prompt"][:20],
        ]
        for h in reversed(history[-20:])
    ]
    ui.table(
        ["ID", "生成日時", "スタイル", "保存", "プロンプト"],
        rows,
        [10, 17, 10, 4, 22],
    )

    show_id = ui.prompt("\n詳細表示するID (Enterでスキップ)")
    if show_id:
        entry = next((h for h in history if h["id"] == show_id), None)
        if entry:
            _print_entry(entry)
        else:
            ui.error("IDが見つかりません")


def _print_entry(entry: dict):
    ui.section(f"生成詳細: {entry['id']}")
    print(f"  生成日時   : {entry['created_at']}")
    print(f"  スタイル   : {entry['style']}")
    print(f"  プロンプト : {entry['prompt']}")
    print(f"  URL        : {entry['url']}")
    if entry.get("local_path"):
        print(f"  保存先     : {entry['local_path']}")
    else:
        print(f"  保存先     : (未保存)")

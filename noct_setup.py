#!/usr/bin/env python3
"""
ノクト専用 初期セットアップスクリプト
======================================
X @noct_zero のアカウント設計に基づき、
PDCAツールをフル初期設定する。

実行:
    python noct_setup.py

設定内容:
    - PDCAサイクル (2026年4月 週次)
    - 声の定義 (ノクトのトーン・NGワード)
    - コンテンツテーマ × ハッシュタグ
    - ネタ帳初期エントリ (5大柱)
    - 今日のブリーフィング (サンプル)
"""

import json
import uuid
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def w(filename: str, data):
    path = DATA_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ {filename}")


# ─────────────────────────────────────────
# 1. PDCAサイクル (週次 #1 + 月次全体)
# ─────────────────────────────────────────
CYCLES = [
    {
        "id": "noct-w01",
        "name": "ノクト 2026年4月 週次#1 (4/15〜4/21)",
        "start_date": "2026-04-15",
        "end_date":   "2026-04-21",
        "status": "active",
        "created_at": "2026-04-15 00:00",
        "goals": {
            "posts":           21,    # 3投稿/日 × 7日
            "followers_gain":  50,
            "impressions":   5000,
            "engagement_rate": 3.0,
        },
        "content_plan": {
            "themes": [
                "AI×X実践記録",
                "失敗→改善ログ",
                "夜勤リアル",
                "数字・指標公開",
                "note戦略",
            ],
            "hashtags": [
                "#副業",
                "#工場勤務",
                "#AI副業",
                "#note",
                "#0から1",
                "#夜勤",
                "#副業初心者",
            ],
        },
        "memo": (
            "コンセプト:「工場勤務・夜勤でも、AI×X×noteで0→1突破までの"
            "全手順を公開するリアル実況アカウント」\n"
            "差別化:成功じゃなく途中を売る。感情を乗せる。再現性を示す。"
        ),
    },
    {
        "id": "noct-m04",
        "name": "ノクト 2026年4月 月次目標",
        "start_date": "2026-04-01",
        "end_date":   "2026-04-30",
        "status": "active",
        "created_at": "2026-04-15 00:00",
        "goals": {
            "posts":           90,    # 3/日 × 30日
            "followers_gain": 200,
            "impressions":  20000,
            "engagement_rate": 3.5,
        },
        "content_plan": {
            "themes": [
                "AI×X実践記録",
                "失敗→改善ログ",
                "夜勤リアル",
                "数字・指標公開",
                "note戦略",
            ],
            "hashtags": [
                "#副業",
                "#工場勤務",
                "#AI副業",
                "#note",
                "#0から1",
            ],
        },
        "memo": "月次目標: フォロワー+200人、note初売上達成、インプレッション2万突破",
    },
]

# ─────────────────────────────────────────
# 2. 声の定義 (ノクトのトーン)
# ─────────────────────────────────────────
VOICE_DEFINITION = {
    # 感情が乗った口語体。AI発信者との差別化
    "ending_rules": [
        "た", "だ", "る", "ない", "ぞ", "よ", "ね", "わ",
        "た。", "だ。", "る。", "ない。", "ぞ。", "よ。",
        "た!", "だ!", "る!", "ない!", "！", "…", "笑",
    ],
    # NG: 綺麗すぎる表現・マーケ臭・他人事感
    "ng_words": [
        "おすすめです", "ぜひ", "お役に立てれば",
        "最強", "絶対", "バズる", "稼げる", "簡単に",
        "〜になります", "〜でしょう", "〜かと思います",
        "弊社", "御社", "皆様",
    ],
    "min_chars": 30,
    "max_chars": 280,
    "preferred_tone": "casual",

    # ノクト固有の声ルール (チェック時の参考)
    "noct_voice_rules": [
        "一人称は「俺」または「おれ」",
        "体験・感情を先に書く。ハウツーは後",
        "失敗・しんどさ・葛藤を隠さない",
        "数字は具体的に (フォロワー○人、インプ○回 など)",
        "夜勤・工場という文脈を意識する",
        "「でもやる」という意思表示で締める",
    ],
}

# ─────────────────────────────────────────
# 3. ネタ帳 (5大コンテンツ柱の初期ネタ)
# ─────────────────────────────────────────
NETA = [
    # 柱①: AI×X実践記録
    {
        "id": str(uuid.uuid4())[:8],
        "category": "own",
        "keyword": "Claude Codeで投稿文案を生成してみた",
        "memo": "具体的なプロンプト → 出力 → 俺が修正した部分を正直に見せる",
        "url": "",
        "tags": ["AI", "実践", "Claude"],
        "used": False,
        "created_at": "2026-04-15 00:00",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "category": "own",
        "keyword": "X運用ツールをClaudeで作った話",
        "memo": "このPDCAツール自体を発信ネタにする。0から作った過程を見せる",
        "url": "",
        "tags": ["AI", "ツール", "実践"],
        "used": False,
        "created_at": "2026-04-15 00:00",
    },
    # 柱②: 失敗→改善ログ
    {
        "id": str(uuid.uuid4())[:8],
        "category": "own",
        "keyword": "初投稿のインプレッションが0だった話",
        "memo": "数字公開。何が悪かったか考えた → 書き出しを変えた → どう変わったか",
        "url": "",
        "tags": ["失敗", "改善", "数字"],
        "used": False,
        "created_at": "2026-04-15 00:00",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "category": "own",
        "keyword": "3日坊主になりかけた夜のこと",
        "memo": "夜勤明け疲れてて何もできなかった → めんどくさい → でもやった理由",
        "url": "",
        "tags": ["失敗", "感情", "継続"],
        "used": False,
        "created_at": "2026-04-15 00:00",
    },
    # 柱③: 夜勤リアル
    {
        "id": str(uuid.uuid4())[:8],
        "category": "own",
        "keyword": "夜勤明け6時に副業した話",
        "memo": "体が重い、眠い、でも30分だけやった。何をやったか具体的に",
        "url": "",
        "tags": ["夜勤", "リアル", "継続"],
        "used": False,
        "created_at": "2026-04-15 00:00",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "category": "own",
        "keyword": "工場の休憩室でnoteを書いた",
        "memo": "スマホ1台で書けることの証明。環境じゃなくてやるかどうか",
        "url": "",
        "tags": ["夜勤", "note", "環境"],
        "used": False,
        "created_at": "2026-04-15 00:00",
    },
    # 柱④: 数字・指標公開
    {
        "id": str(uuid.uuid4())[:8],
        "category": "own",
        "keyword": "4/15時点のリアルな数字全公開",
        "memo": "フォロワー数・インプレッション・売上。0であることを恥じずに出す",
        "url": "",
        "tags": ["数字", "公開", "透明性"],
        "used": False,
        "created_at": "2026-04-15 00:00",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "category": "own",
        "keyword": "週次レポートをXに出す",
        "memo": "毎週月曜に先週の数字をそのまま投稿。良くても悪くても",
        "url": "",
        "tags": ["数字", "週次", "継続"],
        "used": False,
        "created_at": "2026-04-15 00:00",
    },
    # 柱⑤: note戦略
    {
        "id": str(uuid.uuid4())[:8],
        "category": "own",
        "keyword": "note初記事を書くまでの葛藤",
        "memo": "何を書けばいいかわからなかった → 調べた → 決めた理由",
        "url": "",
        "tags": ["note", "初心者", "0から1"],
        "used": False,
        "created_at": "2026-04-15 00:00",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "category": "idea",
        "keyword": "有料note 0→1突破マニュアル (工場勤務版)",
        "memo": "いつか作る目標コンテンツ。まず無料記事で信頼を積む",
        "url": "",
        "tags": ["note", "有料", "目標"],
        "used": False,
        "created_at": "2026-04-15 00:00",
    },
    # ボーナス: 競合分析・参考
    {
        "id": str(uuid.uuid4())[:8],
        "category": "idea",
        "keyword": "「途中を売る」系アカウントの研究",
        "memo": "成功者の発信より過程発信の方がエンゲージ高い仮説を検証したい",
        "url": "",
        "tags": ["分析", "戦略"],
        "used": False,
        "created_at": "2026-04-15 00:00",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "category": "idea",
        "keyword": "プロフィール文「止まってた人間が、動き始めた過程を全部出してる。」",
        "memo": "ベースのプロフ文。投稿のトーンとの一貫性を常に確認",
        "url": "https://x.com/noct_zero",
        "tags": ["プロフィール", "コンセプト"],
        "used": False,
        "created_at": "2026-04-15 00:00",
    },
]

# ─────────────────────────────────────────
# 4. 今日のブリーフィング (スターターサンプル)
# ─────────────────────────────────────────
BRIEFS = [
    {
        "id": "noct-br01",
        "date": "2026-04-15",
        "cycle_id": "noct-w01",
        "main_theme": "スタート宣言 × 現状の数字を全公開",
        "sub_theme": "0円・0フォロワーからの出発を正直に見せる",
        "target": "副業やりたいけど動けてない工場・シフト勤務の人",
        "tone": "casual",
        "hashtags": ["#副業", "#工場勤務", "#AI副業", "#0から1"],
        "references": [
            {
                "url": "https://x.com/noct_zero",
                "memo": "自分のアカウント。今日時点のフォロワー・インプレッションを確認して数字を投稿に入れる",
            }
        ],
        "neta_ids": [],
        "slot_count": 3,
        "tree_count": 1,
        "created_at": "2026-04-15 00:00",
        "status": "active",
    },
]

# ─────────────────────────────────────────
# 5. 改善アクション初期 (コンセプト弱点対策)
# ─────────────────────────────────────────
ACTIONS = [
    {
        "id": str(uuid.uuid4())[:8],
        "cycle_id": "noct-w01",
        "cycle_name": "ノクト 2026年4月 週次#1",
        "category": "try",
        "description": "「何が得られるか」を明示する: 各投稿末尾に読者へのベネフィットを1行添える",
        "priority": "high",
        "next_action": "「俺と一緒に0→1突破できる」と伝わる文末パターンを3種類用意する",
        "due_date": "2026-04-17",
        "status": "open",
        "created_at": "2026-04-15 00:00",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "cycle_id": "noct-w01",
        "cycle_name": "ノクト 2026年4月 週次#1",
        "category": "try",
        "description": "感情ワードを必ず1投稿1個入れる: めんどくさい / 眠い / やめたい / でもやる",
        "priority": "high",
        "next_action": "Quality チェックで「感情ワードあるか」の確認を習慣化",
        "due_date": "2026-04-15",
        "status": "open",
        "created_at": "2026-04-15 00:00",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "cycle_id": "noct-w01",
        "cycle_name": "ノクト 2026年4月 週次#1",
        "category": "try",
        "description": "毎週月曜に数字公開ポスト: フォロワー数・インプレッション・売上を正直に出す",
        "priority": "medium",
        "next_action": "月曜朝スロットに「週次数字」を固定テンプレ化",
        "due_date": "2026-04-21",
        "status": "open",
        "created_at": "2026-04-15 00:00",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "cycle_id": "noct-w01",
        "cycle_name": "ノクト 2026年4月 週次#1",
        "category": "good",
        "description": "「成功じゃなく途中を売る」: これが最大の差別化。絶対にブレるな",
        "priority": "high",
        "next_action": "",
        "due_date": "",
        "status": "open",
        "created_at": "2026-04-15 00:00",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "cycle_id": "noct-w01",
        "cycle_name": "ノクト 2026年4月 週次#1",
        "category": "problem",
        "description": "「何が得られるか」が弱い: 読者は「で、俺はどう変われるの？」と思っている",
        "priority": "high",
        "next_action": "ベネフィット明示の型: 「これを見れば〇〇な人が△△できる」を毎投稿に入れる",
        "due_date": "2026-04-16",
        "status": "open",
        "created_at": "2026-04-15 00:00",
    },
]


# ─────────────────────────────────────────
# 実行
# ─────────────────────────────────────────
def main():
    print()
    print("=" * 52)
    print("  ノクト (@noct_zero) 専用セットアップ")
    print("=" * 52)
    print()
    print("  コンセプト:")
    print("  「工場勤務・夜勤でも、AI×X×noteで")
    print("   '0→1突破'までの全手順を公開する")
    print("   リアル実況アカウント」")
    print()

    # 既存データの確認
    existing = list(DATA_DIR.glob("*.json"))
    if existing:
        print(f"  ⚠️  既存データ {len(existing)} ファイルを上書きします")
        ans = input("  続けますか？ (yes/no): ").strip()
        if ans.lower() != "yes":
            print("  キャンセルしました")
            return
        print()

    print("  データを書き込み中...")
    w("cycles.json",          CYCLES)
    w("voice_definition.json", VOICE_DEFINITION)
    w("neta.json",            NETA)
    w("briefs.json",          BRIEFS)
    w("actions.json",         ACTIONS)

    # 空ファイルを初期化
    for fname in ["posts.json", "metrics.json", "followers.json",
                  "drafts.json", "quality_logs.json", "schedule.json",
                  "suggestions.json"]:
        w(fname, [])

    print()
    print("  セットアップ完了！")
    print()
    print("─" * 52)
    print("  ▶ 毎日の推奨フロー")
    print("─" * 52)
    print()
    print("  【朝 (起床 or 夜勤明け)】")
    print("  1. python x_pdca.py")
    print("  2. → 1 Research : ブリーフィング確認 or 作成")
    print("  3. → 2 Writing  : 朝スロット (7:00) の文案作成")
    print("  4. → 3 Quality  : 品質チェック")
    print("  5. → 4 Approval : 承認 → スケジュール登録")
    print()
    print("  【夕方・夜 (帰宅後 or 出勤前)】")
    print("  6. → 2 Writing  : 夕(18:00) / 夜(21:00) 文案作成")
    print("  7. → 3 Quality  : チェック")
    print("  8. → 4 Approval : 承認")
    print("  9. → 5 Schedule : 投稿完了マーク → 24h後に指標計測")
    print()
    print("  【週次 (月曜)】")
    print("  10. → C Check   : 指標入力・達成確認")
    print("  11. → A Act     : KPT振り返り")
    print("  12. → R Report  : Markdownレポート出力")
    print("  13. → 6 Monitor : 改善提案生成")
    print()
    print("─" * 52)
    print("  プロフィール文案 (候補):")
    print("  「止まってた人間が、動き始めた過程を全部出してる。」")
    print("  「0円のまま終わりたくない人へ。」")
    print("─" * 52)
    print()
    print("  → python x_pdca.py で起動")
    print()


if __name__ == "__main__":
    main()

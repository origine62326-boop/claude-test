"""
AIエージェント - Claude API統合
================================
各エージェントのAI自動化機能を提供する。
ANTHROPIC_API_KEY が設定されている場合のみ動作する。
"""

import os

try:
    import anthropic as _anthropic
    AI_AVAILABLE = bool(os.environ.get("ANTHROPIC_API_KEY"))
except ImportError:
    AI_AVAILABLE = False

# ノクトのシステムプロンプト
_NOCT_SYSTEM = """
あなたはノクト(@noct_zero)のX(Twitter)投稿を書くアシスタントです。

【アカウントコンセプト】
工場勤務・夜勤でも、AI×X×noteで0→1突破までの全手順を公開するリアル実況アカウント

【ターゲット】
工場勤務・シフト制で副業したいが動けていない人。0→1で止まっている人。

【声のトーン】
- 一人称は「俺」もしくは「僕」
- 正直・リアル・感情あり（めんどくさい、眠い、でもやる）
- 成功者ではなく「一緒に進む人」として書く
- 難しい言葉を使わない・体言止めも活用
- AIっぽい綺麗すぎる文章にしない

【フォーマット】
- X投稿用（140字目安、スレッドは各ツイートを---で区切る）
- 読みやすい改行・空行
- 必ずフックから始める（数字・共感・衝撃・疑問・宣言のいずれか）
- 具体的な数字や体験を入れる
"""


def _client():
    return _anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


def _call(prompt: str, max_tokens: int = 1024) -> str:
    """Claude APIを呼び出してテキストを返す"""
    resp = _client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=max_tokens,
        system=_NOCT_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def generate_briefing(theme: str, experience: str, numbers: str, emotion: str, news: str) -> str:
    """ハーマイオニー: テーマ・体験からブリーフィングを生成"""
    prompt = f"""
以下の情報をもとに、今日のX投稿用ブリーフィングを作成してください。

テーマ: {theme}
今日の体験・出来事: {experience or 'なし'}
使える数字: {numbers or 'なし'}
今の気持ち: {emotion or 'なし'}
関連ニュース: {news or 'なし'}

出力形式:
【今日のブリーフィング】
- 核心メッセージ（1行）
- 使うべき具体的な数字や事実
- 読者への価値提供
- おすすめ投稿パターン（3つ）
"""
    return _call(prompt, 600)


def generate_drafts(theme: str, briefing: str, category: str, hook_type: str) -> list[str]:
    """ルーナ: 投稿案を3つ自動生成"""
    hook_guide = {
        "number":   "数字から始める（「○○日目」「○○円」「○時間」など）",
        "empathy":  "共感フックから始める（「わかる」「あるある」の体験から）",
        "shock":    "衝撃フックから始める（「正直に言う」「驚いた」から）",
        "question": "疑問フックから始める（「なぜ○○なのか」の問いから）",
        "declare":  "宣言フックから始める（「やる」「変える」の宣言から）",
        "none":     "自然な書き出しで始める",
    }

    prompt = f"""
以下の情報をもとに、X投稿案を3パターン作成してください。

テーマ: {theme}
カテゴリ: {category}
フックタイプ: {hook_guide.get(hook_type, hook_type)}
ブリーフィング:
{briefing}

各投稿案の形式:
- 140字程度（スレッドの場合は各ツイートを---で区切る）
- 必ず指定のフックタイプで始める
- ノクトの声（工場勤務・夜勤・副業0→1）で書く
- 数字や具体的な体験を入れる

[パターン1]
（投稿文）

[パターン2]
（投稿文）

[パターン3]
（投稿文）
"""
    raw = _call(prompt, 1200)

    # パターンごとに分割
    drafts = []
    for marker in ["[パターン1]", "[パターン2]", "[パターン3]"]:
        if marker in raw:
            start = raw.index(marker) + len(marker)
            next_markers = [m for m in ["[パターン2]", "[パターン3]"] if m in raw and raw.index(m) > start]
            end = raw.index(next_markers[0]) if next_markers else len(raw)
            drafts.append(raw[start:end].strip())
    return drafts if drafts else [raw]


def check_quality(content: str) -> dict:
    """マルフォイ: 品質チェックと改善案を自動生成"""
    prompt = f"""
以下のX投稿をノクト(@noct_zero)のブランド基準でチェックしてください。

【投稿内容】
{content}

以下の6項目それぞれについて pass/fail と理由を1行で答え、
最後に改善案（改善が必要な場合のみ）を提示してください。

チェック項目:
1. voice: ノクトらしい声・語尾になっているか
2. hook: 冒頭にフックがあるか（数字・共感・衝撃など）
3. concrete: 具体的な数字や体験が入っているか
4. empathy: 読者が「自分も」と共感できる内容か
5. length: 投稿として適切な長さか
6. readable: 空白・改行が読みやすいか

出力形式（厳守）:
voice: pass/fail - 理由
hook: pass/fail - 理由
concrete: pass/fail - 理由
empathy: pass/fail - 理由
length: pass/fail - 理由
readable: pass/fail - 理由
score: XX/100

改善案:
（改善が必要な場合のみ書く。不要なら「なし」）
"""
    raw = _call(prompt, 800)

    # パース
    results = {}
    score   = 0
    improvement = ""

    for line in raw.split("\n"):
        line = line.strip()
        for key in ["voice", "hook", "concrete", "empathy", "length", "readable"]:
            if line.startswith(f"{key}:"):
                results[key] = "fail" not in line.lower()
        if line.startswith("score:"):
            try:
                score = int(line.split(":")[1].strip().split("/")[0])
            except Exception:
                pass
        if line.startswith("改善案:"):
            improvement = line.replace("改善案:", "").strip()

    # 改善案が複数行の場合
    if "改善案:" in raw:
        improvement = raw.split("改善案:")[1].strip()

    return {
        "results":     results,
        "score":       score,
        "improvement": improvement,
        "raw":         raw,
    }


def rewrite_post(content: str, weak_points: list[str]) -> str:
    """マルフォイ: 不合格項目を修正して書き直し"""
    weak_str = "\n".join(f"- {w}" for w in weak_points)
    prompt = f"""
以下のX投稿を、指摘された弱点を修正して書き直してください。

【元の投稿】
{content}

【修正すべき点】
{weak_str}

ノクト(@noct_zero)の声（工場勤務・夜勤・副業0→1）を維持したまま改善してください。
修正後の投稿文のみ出力してください。
"""
    return _call(prompt, 600)


def generate_snape_report(status_summary: str, weak_points: list[str]) -> str:
    """スネイプ: パイプライン全体の改善提案を生成"""
    prompt = f"""
ノクト(@noct_zero)のX運用パイプラインの状況を分析して改善提案をしてください。

【現在の状況】
{status_summary}

【品質チェックで弱い項目】
{chr(10).join(f'- {w}' for w in weak_points) if weak_points else 'なし'}

以下の観点で具体的な改善提案を3〜5個出してください:
- コンテンツの質向上
- 投稿頻度・タイミング
- ノクトのブランドの強化
- 0→1突破に向けた戦略

簡潔に、箇条書きで出力してください。
"""
    return _call(prompt, 600)

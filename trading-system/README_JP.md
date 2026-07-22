# trading-system

`USDJPY_LowRisk_Trend_EA`（楽天MT4向け、USD/JPY H1専用の低リスク順張りEA）を、
バックテスト→分析→改善提案→人間承認→次バージョン実装、というサイクルで
安全に育てていくための検証パイプラインです。

## 目的

- 「一晩で大きく稼ぐAI」を作ることではなく、**損失を限定しながら長期的に検証できる**
  自動売買開発基盤を作ること
- 改善内容を**数値で比較**し、過剰最適化を避けること
- 実口座への誤発注・人間の承認なしのリスク増加を防ぐこと

## 全体の流れ

```
MT4でバックテスト実行
   ↓ (手動: レポート/操作履歴をHTML保存)
reports/raw/ に .htm を配置
   ↓ scripts/run_analysis.py
reports/normalized/ (正規化JSON)
reports/analyzed/   (指標・異常検知・期間/方向/時間/レジーム分析)
outputs/summaries/  (人間が読むMarkdownサマリー)
   ↓ (任意) scripts/compare_backtests.py で前バージョンと比較
   ↓ (任意) scripts/validate_release.py で機械的な合格基準と照合
   ↓ prompts/*.md を使ってClaude Codeに解釈・改善提案を依頼
   ↓ 人間が承認
次バージョンのEA実装 (mt4/USDJPY_LowRisk_Trend_EA.mq4 を変更)
```

**重要な制約**: このパイプラインを動かすClaude(Claude Code)は、あなたのPC上のMT4に
直接アクセスできません。「MT4でバックテスト実行」から「reports/raw/に配置」までは
必ず人間が手動で行う必要があります。手順は `mt4/README_MT4_JP.md` を参照してください。

## セットアップ

```bash
cd trading-system
pip install -r requirements.txt
```

## 使い方

### 1. バックテスト結果を1回分析する

```bash
python scripts/run_analysis.py \
  --report reports/raw/report_v0.1_1y.htm \
  --trades reports/raw/trades_v0.1_1y.htm \
  --run-id v0.1_1y \
  --max-lot 1.0
```

`outputs/summaries/v0.1_1y_summary.md` に結果がまとまります。

### 2. 2つの結果を比較する

```bash
python scripts/compare_backtests.py \
  --baseline reports/analyzed/v0.1_2y_metrics.json \
  --candidate reports/analyzed/v0.1_1y_metrics.json \
  --baseline-label "v0.1 2年間" --candidate-label "v0.1 直近1年" \
  --run-id v0.1_2y_vs_1y
```

### 3. 機械的な合格基準と照合する

```bash
python scripts/validate_release.py \
  --metrics reports/analyzed/v0.1_1y_metrics.json \
  --anomalies reports/analyzed/v0.1_1y_anomalies.json
```

基準は `configs/acceptance_criteria.yaml`。**PASSは実口座投入の推奨ではありません**。
明らかに水準未満のものを機械的に弾くためのフィルタです。

### 4. テストを実行する

```bash
pytest tests/ -v
```

## ディレクトリ構成

| ディレクトリ | 内容 |
|---|---|
| `mt4/` | EA本体とMT4側の手順書 |
| `reports/raw/` | MT4から出力した生のHTMLファイル(gitignore対象) |
| `reports/normalized/` | パース後の正規化JSON(gitignore対象) |
| `reports/analyzed/` | 指標・異常検知等の分析結果JSON(gitignore対象) |
| `analysis/` | 分析ロジック本体(Pythonモジュール、単体でもCLIとして実行可能) |
| `tests/` | analysis/ のユニットテスト |
| `prompts/` | Claude Codeへレビューを依頼する際のプロンプトテンプレート |
| `configs/` | 分析設定・合格基準・EAリスク値のミラー |
| `outputs/` | 人間向けの成果物(サマリー・比較・チャート、gitignore対象) |
| `scripts/` | 上記を組み合わせて実行するCLIエントリーポイント |

## 現在の既知の制約

- MT4レポートのパーサーは実ファイルでまだ検証していません（`TODO.md` 参照）
- `regime_analysis.py` はATR/ADXの実値を使った正確なレジーム分類ではなく、
  時系列ブロック分割による近似分析です
- `configs/*.yaml` の一部はまだPythonコード側にハードコードされた値と二重管理の状態です

詳細は `TODO.md` を参照してください。

## 免責

このパイプラインおよびEAは、利益を保証するものではありません。実口座への投入前には
十分なバックテスト・デモ運用による検証と、人間による最終承認が必要です。

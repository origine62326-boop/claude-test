# trading-system

**現在のバージョン: v0.2.0**（詳細は `CHANGELOG.md`、正式記録は `releases/v0.2.0/`）

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

### 1. バックテスト結果を1回分析する（最小構成: レポートHTMLのみ）

```bash
python scripts/run_analysis.py reports/raw/report_v0.1_1y.htm
```

`--run-id` を省略した場合、ファイル名(拡張子抜き)がそのままrun-idになります。
`outputs/summaries/report_v0.1_1y_summary.md` に、初心者向けの日本語サマリー
（バックテスト条件・純利益・PF・最大DD・勝率・取引回数・最大連敗・モデリング品質・
注意点・次に確認すべきこと）がまとまります。

### 1b. 操作履歴HTMLも渡す（フル版: トレード明細まで分析）

```bash
python scripts/run_analysis.py \
  reports/raw/report_v0.1_1y.htm \
  --trades reports/raw/trades_v0.1_1y.htm \
  --run-id v0.1_1y \
  --max-lot 1.0
```

上記の最小構成の結果に加え、トレード明細からの指標再計算・安全設計違反の異常検知・
年別/月別・買売別・時間帯別・レジーム近似分析も実行し、詳細版サマリー
(`outputs/summaries/v0.1_1y_summary_full.md`)を生成します。

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
| `releases/` | **バージョンごとの正式な記録**(NOTES.md・確定版サマリー・比較レポート。git管理対象) |

## バージョン管理ルール

`mt4/`(EA本体)と `analysis/`〜`scripts/`(分析パイプライン)をセットにして、
以下のバージョン番号で管理します。

| バージョン | 意味 |
|---|---|
| v0.1.0 | 初回EA |
| v0.2.0 | 新機能追加 |
| v0.2.1 | バグ修正 |
| v0.3.0 | 売買ロジック改善 |
| v1.0.0 | 十分なバックテスト・デモ運用を経て安定版と判断した時点 |

**変更を行う際の手順**:

1. 既存ファイルを上書きする前に、その時点の状態をGitでコミットしておく
2. 変更を実施する
3. 重要な変更であればバージョンを1つ進める（上表の基準に従う）
4. `CHANGELOG.md` に変更内容を追記する
5. この `README_JP.md` にも変更内容を追記する（該当セクションを更新）
6. そのバージョンでバックテストを実行し、`scripts/run_analysis.py` の出力を
   `releases/vX.Y.Z/` にコピーして記録する
7. 前バージョンがあれば `scripts/compare_backtests.py` で比較レポートを作成し、
   同様に `releases/vX.Y.Z/` へ記録する
8. `git tag -a vX.Y.Z -m "..."` でタグを作成し、GitHubへpushする
9. GitHub Releaseを作成する（現状Claude側にRelease作成用のツールがないため、
   タグをpushした後、人間がGitHub上の「Draft a release」から作成する。
   本文は `releases/vX.Y.Z/NOTES.md` の内容をベースにする）

詳細な `releases/` の運用は `releases/README.md` を参照してください。

## 現在の既知の制約

- MT4レポートのパーサーは実ファイルでまだ検証していません（`TODO.md` 参照）
- `regime_analysis.py` はATR/ADXの実値を使った正確なレジーム分類ではなく、
  時系列ブロック分割による近似分析です
- `configs/*.yaml` の一部はまだPythonコード側にハードコードされた値と二重管理の状態です

詳細は `TODO.md` を参照してください。

## 免責

このパイプラインおよびEAは、利益を保証するものではありません。実口座への投入前には
十分なバックテスト・デモ運用による検証と、人間による最終承認が必要です。

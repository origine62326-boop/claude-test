# CHANGELOG

このファイルは `mt4/`(EA本体)と `analysis/`〜`scripts/`(バックテスト分析パイプライン)を
セットにした、このプロジェクト全体の変更履歴。バージョンは以下の方針で付与する
(詳細な運用ルールは `README_JP.md` の「バージョン管理ルール」を参照)。

| バージョン | 意味 |
|---|---|
| v0.1.0 | 初回EA(Phase1-4実装 + 分析パイプライン初版) |
| v0.2.0 | 新機能追加(このバージョン。最小構成の解析パイプライン完成) |
| v0.2.1 | バグ修正 |
| v0.3.0 | 売買ロジック改善 |
| v1.0.0 | 十分なバックテスト・デモ運用を経て安定版と判断した時点 |

各バージョンの正式な記録(バックテスト結果・比較レポート)は `releases/vX.Y.Z/` に保存する。

## インフラ (バージョン番号なし。リリース作業の自動化)

`.github/workflows/release.yml` を追加。`vX.Y.Z` 形式のタグをpushすると、GitHub
Releaseが自動作成されるようになった。`releases/<tag>/NOTES.md` があればそれを
本文に、無ければGitHub自動生成ノートを使う。EA・分析パイプラインの動作には
影響しないため、製品バージョン番号は進めていない。

## v0.2.0 (最小構成の解析パイプライン完成)

EA (`mt4/USDJPY_LowRisk_Trend_EA.mq4`) には変更なし。分析パイプラインのみを対象とした
バージョン。目的は売買ロジックの変更ではなく、バックテスト結果を保存・解析できる
最小構成のパイプラインを完成させること。

### 変更点

- `analysis/parse_mt4_report.py` を全面改訂
  - 抽出フィールドを要求仕様の20項目(EA名・通貨ペア・時間足・テスト開始/終了日・
    初期証拠金・通貨・モデリング品質・不整合チャートエラー・総取引回数・純利益・
    総利益・総損失・プロフィットファクター・期待値・最大ドローダウン額/率・勝率・
    最大連勝・最大連敗)に整理。加えてbars_in_test等の補助フィールドも保持
  - **日本語版・英語版どちらのMT4レポートも読めるよう、ラベルごとに日英両方の
    パターンを追加**
  - 「主値(副値%)」形式の複合セル(最大ドローダウン、勝率、最大連勝/連敗)を
    正しく分解して抽出するよう修正(旧実装のバグを2件修正: 連勝/連敗セルの
    金額と回数の取り違え、相対ドローダウンの主値/副値の取り違え)
  - 取引回数等の整数フィールドが `192.0` のような小数表示にならないよう後処理を追加
- `analysis/performance_metrics.py` に `validate_report_data()` を追加
  - レポートデータの欠損値・異常値・整合性(純利益=総利益+総損失 等)を検査
  - 取引数200件未満・モデリング品質70%未満は警告(エラーではない)として報告
  - 既存のトレード明細ベースの指標再計算機能(`compute_metrics_from_trades`等)は
    フル版パイプライン向けとして維持
- `analysis/generate_summary.py` に `render_minimal_summary()` を追加
  - バックテスト条件・純利益・PF・最大DD・勝率・取引回数・最大連敗・
    モデリング品質・注意点・次に確認すべきこと、を含む初心者向け日本語サマリー
- `scripts/run_analysis.py` のCLIを再設計
  - `python scripts/run_analysis.py reports/raw/xxx.htm` の1コマンドで
    最小構成パイプライン(パース→検証→サマリー生成)が実行できるように変更
  - `--trades` を追加指定すると、既存のフル版パイプライン(トレード明細分析)も実行
  - 入力ファイル(`reports/raw/`配下)を書き換えるコードパスが無いことを確認
- テスト: 日本語版・英語版両方のfixture(`sample_report.htm` / `sample_report_en.htm`)で
  pytest 36件全て通過を確認

### 既知の制約(変更なし)

- パーサーは実際のMT4出力ファイルでまだ検証していない（`TODO.md` 最優先項目）

## v0.1.0 (初回EA + パイプライン初版)

`mt4/CHANGELOG_EA.md` に記録していたEA単体の変更履歴(旧v0.1.0 Phase1-4実装、
旧v0.1.1 コンパイル警告修正)は、このバージョンからここに統合する。

### EA (`mt4/USDJPY_LowRisk_Trend_EA.mq4`)

- Phase1〜4実装（入力検証・トレンド/ADX/押し目判定・ATRベースSL/TP・ロット自動計算・
  SafeOrderSend/Modify/Close・ECNフォールバック・実口座誤稼働防止）
- ユーザー環境のMetaEditorでコンパイル確認: 0 errors, 0 warnings
- Phase5〜9(建値移動・日次損失上限・取引時間フィルター・ドキュメント整備)は未実装

### 分析パイプライン (`analysis/` / `scripts/` / `tests/` / `prompts/` / `configs/`)

- `mt4/`: 既存の `USDJPY_LowRisk_Trend_EA.mq4`(v1.00、Phase1-4)を配置。
  MT4→Python連携のためのレポートエクスポート手順書(`README_MT4_JP.md`)を追加
- `analysis/`:
  - `parse_mt4_report.py`: レポートHTML→正規化JSON
  - `parse_mt4_trades.py`: 操作履歴HTML→正規化トレードJSON(open/close行のペアリング込み)
  - `performance_metrics.py`: トレードからの指標再計算＋レポート値とのクロスチェック
  - `trade_anomaly_check.py`: 損切りなし・同時保有・重複エントリー等の安全設計違反検知
  - `period_analysis.py` / `direction_analysis.py` / `time_analysis.py`: 年別月別・買売別・時間帯/曜日別集計
  - `regime_analysis.py`: 時系列ブロック分割による近似レジーム分析(ATR/ADX実値は未使用、TODO参照)
  - `compare_versions.py`: 2つの分析結果の指標差分計算
  - `generate_summary.py`: 上記すべてを統合したMarkdownサマリー生成
- `scripts/`: `run_analysis.py`(一括実行) / `compare_backtests.py` / `validate_release.py`
  (合格基準との機械的照合)。いずれも動作確認済み(fixtureデータでのスモークテスト実施)
- `tests/`: pytest 19件、全て通過を確認
- `prompts/`: EAレビュー・バックテスト分析・バージョン比較・過剰最適化チェックの
  4種のプロンプトテンプレート
- `configs/`: `analysis_config.yaml` / `acceptance_criteria.yaml` / `risk_limits.yaml`

### 既知の制約

- MT4レポート/操作履歴パーサーは実データでの検証が未実施（`TODO.md` 最優先項目）
- `regime_analysis.py` はATR/ADXの実値を使わない近似分析
- `configs/analysis_config.yaml` の一部設定値はPythonコード側とまだ二重管理

### 検証

```
pytest tests/ -v          → 19 passed
python scripts/run_analysis.py (fixtureデータ) → 正常終了、サマリー生成を確認
python scripts/validate_release.py (fixtureデータ) → FAIL判定(取引数不足)を正しく検出
python scripts/compare_backtests.py (fixtureデータ) → 正常終了
```

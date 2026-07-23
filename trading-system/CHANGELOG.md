# CHANGELOG

このファイルは `mt4/`(EA本体)と `analysis/`〜`scripts/`(バックテスト分析パイプライン)を
セットにした、このプロジェクト全体の変更履歴。バージョンは以下の方針で付与する
(詳細な運用ルールは `README_JP.md` の「バージョン管理ルール」を参照)。

| バージョン | 意味 |
|---|---|
| v0.1.0 | 初回EA(このバージョン。Phase1-4実装 + 分析パイプライン初版) |
| v0.2.0 | 新機能追加(例: Phase5以降の実装) |
| v0.2.1 | バグ修正 |
| v0.3.0 | 売買ロジック改善 |
| v1.0.0 | 十分なバックテスト・デモ運用を経て安定版と判断した時点 |

各バージョンの正式な記録(バックテスト結果・比較レポート)は `releases/vX.Y.Z/` に保存する。

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

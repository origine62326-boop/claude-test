# CHANGELOG

## v0.1.0 (パイプライン初版)

### 実装済み

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

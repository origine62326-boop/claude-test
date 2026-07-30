# TODO / 既知の課題

優先度の高いものから並べています。

## [2026-07-28 完了] 実データでのパーサー検証(楽天MT4 Build 1475, 日本語UI)

- [x] `analysis/parse_mt4_report.py` を、実際に楽天MT4(RakutenSecurities-Demo, Build 1475)から
      出力したレポートHTMLで検証した。ラベル文言・行構造の想定違いが6件見つかり、修正した
      （文字コード固定、「純益」表記、長音符欠落、勝敗内訳セルのラベル誤り、行修飾語の分離、
      連勝/連敗セルの主値副値逆転。詳細は`research/versions/BACKTEST_REPRODUCIBILITY.md`参照）
- [x] `analysis/parse_mt4_trades.py` を同ファイルで検証した。操作履歴の新規注文行が
      `colspan`省略により列数不足で除外されるバグを修正した
- [x] `FIELD_SEQUENCE` / `_merge_row_qualifiers` / `_row_cells`のcolspan展開を実データに合わせて調整済み
- [x] `tests/fixtures/sample_report.htm` / `sample_report_en.htm`の連勝/連敗セルの値を、実データで
      確認した仕様（主値/副値の並び）に合わせて修正した

- [ ] **残タスク**: 上記はRakutenSecurities-Demo(Build 1475, 日本語UI)の1ファイルのみでの検証。
      他のブローカー・MT4ビルド・英語UIでの実ファイル検証はまだ行っていない（英語ラベルは
      引き続き推測ベース）。実際の英語版レポートが手に入った時点で改めて検証すること
- [ ] レポート公式値とトレード明細再計算値の間に小さな乖離が残っている（原因未特定、
      `research/data/DATASET_REGISTRY.md` DS001の`known_issues`参照）。調査は未着手

## 次に対応したいこと

- [ ] `configs/analysis_config.yaml` の値を実際にPythonコードから読み込むようにする
      （現状は `performance_metrics.py` 等にハードコードされた値と二重管理）
- [ ] `regime_analysis.py` をATR/ADXベースの本来のレジーム分類に近づける。
      そのためにはEA側 (`mt4/USDJPY_LowRisk_Trend_EA.mq4`) にエントリー時点の
      インジケーター値をCSVログ出力する機能を追加する必要がある（新規Phaseとして提案）
- [ ] `parse_mt4_report.py` の日本語ラベル正規表現が、楽天MT4以外のブローカーや
      MT4のバージョン差で変わらないか確認する
- [ ] スプレッド変動耐性のテスト（カスタムスプレッドでの再バックテスト）を
      このパイプラインに組み込む（現状は手動でMT4側の設定を変えて再実行する運用）

## EA側(mt4/)の未実装機能との対応

以下はEA側(`mt4/CHANGELOG_EA.md`参照)がまだPhase5〜9を実装していないための制約です。
分析パイプライン側ではなく、EA側の実装が進み次第、以下も合わせて更新する:

- [ ] Phase6(日次損失上限・連敗制限)実装後、`trade_anomaly_check.py` に
      「日次損失上限を超えて新規発注していないか」のチェックを追加する
- [ ] Phase7(取引時間フィルター)実装後、`time_analysis.py` の結果を使って
      フィルターの妥当性を事後検証できるようにする
- [ ] Phase5(建値移動・トレーリング)実装後、`parse_mt4_trades.py` がSL変更履歴を
      追えるようにする(現状は新規注文時点のSLしか見ていない)

## 直近の実データ分析（このパイプライン構築のきっかけになった結果）

[2026-07-28] 上記2件とは別の期間（2025.07.21〜2026.07.27、USDJPY H1, 100000初期証拠金）の
実バックテスト結果を1件、このパイプラインで正式に処理した（`research/data/DATASET_REGISTRY.md`
DS001、`research/experiments/EXP-001_ema_adx_trend_baseline.md`参照。結果はHOLD、
最低取引数200件に対し184件で不足）。下記2件はまだ実ファイルが手に入っておらず未処理のまま。

会話内で確認済みの2回のバックテスト結果を、実ファイルが揃い次第このパイプラインで
再現・比較すると良い:

- v0.1、2025.07.21〜2026.07.21(直近1年)、初期証拠金10万円: PF 0.76、純利益 -1,583.42、
  モデリング品質57.30%
- v0.1、約2年間、初期証拠金1万円: PF 1.06、純利益 +1,395.26、モデリング品質49.59%

このパイプラインの `compare_backtests.py` で両者を比較し、`regime_analysis.py` の
時系列ブロック分析で「どの期間から傾向が変わったか」を確認するのが次の一手になる。

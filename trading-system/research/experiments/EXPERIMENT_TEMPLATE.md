# Experiment Template

`trading-system/RESEARCH_CHARTER.md` 第6節に基づく実験記録テンプレート。新しい実験を登録する際は
このファイルをコピーし、`research/experiments/EXP-<連番>_<短い説明>.md` のようなファイル名で保存する
（例: `EXP-001_ema_adx_trend_baseline.md`）。このテンプレート自体は編集せず、雛形として保持する。

実験結果を見た後にパラメータや評価対象期間を変更する場合、このファイルを上書きせず、
新しい`experiment_id`を発行して別ファイルとして保存すること（憲章第18節、テストデータを見た後の
条件変更禁止）。

## 必須フィールド

| フィールド | 記入内容 |
|---|---|
| experiment_id | 一意のID（例: EXP-001） |
| hypothesis_id | 対応する`HYPOTHESIS_REGISTRY.md`のID（例: H001） |
| title | 実験名 |
| evidence_level | この実験が根拠とするEvidence/Hypothesisのレベル（E1-E3/H/U） |
| objective | この実験で何を確認したいか |
| rationale | なぜこの実験が必要か |
| evidence_ids | 参照するEvidence ID（あれば） |
| features | 使用する特徴量（`FEATURE_REGISTRY.md`のfeature_id） |
| target | 予測・評価対象（例: 方向, 期待値R） |
| baseline | 比較対象のベースライン（憲章第9節: Random Walk / Always WAIT / Buy and Hold相当 / 単純Momentum / 単純Mean Reversion / Logistic Regression / LightGBM のいずれか、または複数） |
| comparison_method | ベースラインとの比較方法 |
| train_period | 学習期間 |
| validation_period | 検証期間 |
| test_period | テスト期間（事前登録し、結果を見るまで変更しない） |
| walk_forward_definition | ウォークフォワードの分割方法・ウィンドウ幅・再学習頻度 |
| transaction_cost_assumption | 手数料の仮定 |
| spread_assumption | スプレッドの仮定 |
| slippage_assumption | スリッページの仮定 |
| parameters | 使用パラメータ一覧（値を固定して記録） |
| random_seed | 乱数シード |
| code_version | 実装のGitコミットSHA |
| data_version | 使用データセットの`DATASET_REGISTRY.md`上のdata_version |
| execution_date | 実行日時 |
| metrics | 得られた評価指標一覧（`RESEARCH_CHARTER.md`第12節の予測評価・取引評価を含む） |
| result | 数値結果の要約 |
| decision | ADOPTED / HOLD / REJECTED / INVALIDATED のいずれか |
| status | DRAFT / READY / RUNNING / COMPLETED / ADOPTED / HOLD / REJECTED / INVALIDATED |
| acceptance_reason | 採用する場合、憲章第13節のどの条件を満たしたか |
| rejection_reason | 棄却する場合、憲章第14節のどの条件に該当したか |
| limitations | この実験の限界・注意点 |
| reviewer | レビューした人（人間の承認者） |
| created_at | 作成日時 |
| updated_at | 最終更新日時 |

## 最小記録セット（検証回数を増やすための簡易トラック、2026-07-31追加）

`BACKTEST_COVERAGE_EXPANSION_PLAN.md`のような、既存仮説（H001/H002等）の検証範囲を広げるための
比較的小さな実験（期間・方向・コスト条件の違いを見るだけの実験等）では、上記フルセットの全項目を
毎回埋めるのではなく、以下の**最小記録セット**で登録してよい。ただし事前登録の原則（実行前に
比較対象・変更点・判定基準を確定し、結果を見た後に変更しない）は最小トラックでも省略しない。

- experiment_id
- 検証目的
- 比較対象
- 変更点（1実験1変更点に限定する。複数の検証軸を同時に変えない）
- EA Commit SHA
- 使用パラメータ
- MT4設定（期間・スプレッド・モデル・初期証拠金等）
- データ期間
- レポート`.htm`（`DATASET_REGISTRY.md`にchecksum登録）
- Expertsログ（比較対象がリスク管理機能の発動有無等、レポートだけでは判定できない場合のみ必須。
  不要な場合は「対象外」と明記する）
- 主要指標（PF・純損益・最大DD・取引数等、この実験の目的に関係するもののみでよい）
- 判定（ADOPTED / HOLD / REJECTED / INVALIDATEDのいずれか。新しいstatus値は追加しない）
- 既知の制約

H001（EMA/ADXトレンドフォロー）・H002（リスク管理）本体の判定に直接使う主要な実験（`EXP-001`,
`EXP-002`, `EXP-003`等）は、引き続き上記フルセットで記録する。

## required_data_sources（憲章第8節）

この実験で必須とするデータソースを列挙する。ここに列挙したデータが欠けている場合、
Decision EngineはWAITを返す、または本実験は「実験無効(INVALIDATED)」として扱う。

- (例) USDJPY H1 OHLC
- (例) スプレッド履歴
- (例) 経済指標カレンダー（該当する場合のみ）

## 事前登録チェックリスト（実行前に埋めること）

- [ ] test_periodを実行前に確定し、結果を見た後に変更していない
- [ ] acceptance_criteria / rejection_criteriaを実行前に確定している（`HYPOTHESIS_REGISTRY.md`または本テンプレート内に記載）
- [ ] train/validation/testの期間が重複していない
- [ ] 未来データを参照する特徴量が含まれていない（`FEATURE_REGISTRY.md`のleakage_riskを確認）
- [ ] transaction_cost / spread / slippageの仮定を明記している
- [ ] code_version（コミットSHA）とdata_versionを記録する準備ができている

## 記入例（プレースホルダー、実データではない）

```
experiment_id: EXP-000 (記入例)
hypothesis_id: H001
title: (例) EMA/ADXベースラインの再現バックテスト
evidence_level: H
status: DRAFT
```

この記入例は実際の実験結果ではない。実データを登録する際は、上記フィールドを実験ごとに
新規ファイルへ記入すること。

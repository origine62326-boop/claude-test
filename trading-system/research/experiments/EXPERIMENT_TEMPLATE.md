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

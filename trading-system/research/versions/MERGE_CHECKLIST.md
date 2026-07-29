# Merge Checklist — Phase 5-1 (`claude/ea-v0.3.0-risk-management`)

`RESEARCH_PLATFORM_ROADMAP.md` Phase R1 ステップ3向けのチェックリスト。**チェック状態は
2026-07-28時点で確認できた事実のみに基づく。マージすべきか否かの判断はこのチェックリストではなく
人間が行う。** 詳細な根拠は`PHASE5_1_DECISION_REPORT.md`を参照。

## チェック項目

- [ ] **コンパイル成功**
  現状: 未達。当該ブランチの`trading-system/CHANGELOG.md`が「コンパイル確認・バックテスト検証待ち」
  と自己申告しており、`configs/risk_limits.yaml`の`implementation_status.compile_status`は
  `PENDING_USER_METAEDITOR_CONFIRMATION`。ユーザー環境のMetaEditorで0 errors/0 warningsを
  確認できた時点でチェックすること。

- [ ] **Backtest Run A**
  現状: 未達。定義未確定（本チェックリスト作成時点でRun A/Run Bの区別がユーザー指示に
  明記されていないため、下記「A/B の定義（提案）」を参照。定義自体も人間の確認・修正を要する）。

- [ ] **Backtest Run B**
  現状: 未達。Run Aと同様。

- [ ] **HTMLレポート保存**
  現状: 未達。`trading-system/reports/raw/`は`.gitkeep`のみで、Phase 5-1適用後の実際の
  `.htm`ストラテジーテスターレポートは未保存（`DATASET_REGISTRY.md` DS001が未確定状態のまま）。

- [ ] **Parameter保存**
  現状: 未達。上記HTMLレポートと対になる、実行時のEA入力パラメータ一式（`RiskPercent`,
  `MaxDailyLossPercent`, `MaxConsecutiveLosses`, `MinimumADX`等）のスナップショットが、
  レポートファイルと紐づく形では保存されていない。

- [x] **Commit SHA保存**
  現状: 達成。`PHASE5_1_DECISION_REPORT.md`第2節、`CODE_COMPONENT_REGISTRY.md`(CC002)、
  `VERSION_REGISTRY.md`(VR003)に、ブランチ先端`1cea16ad8916e59dcb26a31c06a6f60546074ebe`および
  本ブランチ固有の4コミットのSHAを記録済み（`git log`で実在確認済み）。
  ※この項目は「SHAが記録されていること」という文書化作業であり、Phase 5-1の品質評価とは無関係。

- [ ] **実験登録済み**
  現状: 未達。H002（`HYPOTHESIS_REGISTRY.md`、日次損失上限・連敗制限によるテールリスク・
  稼働継続性改善仮説）に対応する`experiment_id`は、`research/experiments/`配下にまだ
  発行されていない。

- [ ] **リスク確認**
  現状: 部分的。`PHASE5_1_DECISION_REPORT.md`第9節に、確認できる範囲の事実（未検証ロジックである
  こと、Signal/Riskが密結合していること、AllowLiveTrading=falseが維持されていること等）を
  文書化済み。ただし、これを踏まえた**人間によるリスク確認・承認**自体は未実施のため未チェック。

## A/B の定義（提案、要確認）

ユーザー指示の「Backtest Run A」「Backtest Run B」が具体的に何を指すか本チェックリスト作成時点では
未確定だったため、`TEST_PLAN_PHASE5-1.md`の「実施後の報告項目」（v0.2.0との比較を含むバックテスト
結果を`releases/v0.3.0/`へ記録する）と整合する形で、以下を暫定的な定義として提案する。
**この定義自体、人間の確認・修正を前提とする。**

- **Run A（案）**: Phase 5-1適用前（main, v0.1.0, Phase1-4）のEAでの基準バックテスト
- **Run B（案）**: Phase 5-1適用後（本ブランチ）のEAでの、Run Aと同一期間・同一パラメータでの
  比較バックテスト

いずれも、実行後は`.htm`レポート・使用パラメータ・コミットSHA・データ条件・ファイルハッシュを
`trading-system/reports/raw/`および`research/data/DATASET_REGISTRY.md`に記録し、
`UNVERIFIED_OBSERVATION`ではなく正式なResearch Resultとして扱えるようにすること
（`RESEARCH_RULES.md`第0節参照）。

## 全体状況

| 項目 | 状態 |
|---|---|
| コンパイル成功 | 未達 |
| Backtest Run A | 未達（定義要確認） |
| Backtest Run B | 未達（定義要確認） |
| HTMLレポート保存 | 未達 |
| Parameter保存 | 未達 |
| Commit SHA保存 | **達成** |
| 実験登録済み | 未達 |
| リスク確認 | 部分的（事実整理は完了、人間の承認は未実施） |

8項目中1項目のみ達成（文書化作業）。残り7項目は、実機での検証作業またはユーザーによる
定義確認・承認を要するため、本セッション内では完了できない。

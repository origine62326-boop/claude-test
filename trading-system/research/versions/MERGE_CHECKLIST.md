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

- [x] **Backtest Run A**（2026-07-29更新）
  現状: **達成**。`EXP-001_ema_adx_trend_baseline.md`を「旧版Baseline」として固定し、Run Aに
  対応させた（`DATASET_REGISTRY.md` DS001, checksum記録済み）。ただし使用EAビルドが未確認のため、
  「Phase5-1適用前(CC001)のバックテスト」であることは**確定していない**（`EXP-001`の
  `limitations`参照）。この不確実性を許容した上でBaselineとして採用する、というのが
  2026-07-29時点のユーザー判断。

- [x] **Backtest Run B**（2026-07-29更新）
  現状: **実行完了**（`EXP-002_phase5_1_risk_management.md`, DS004）。ただしExpertsログが
  提供されていないため、H002が本来検証したい「制限が実際に発動したか」は未確認のまま。
  数値指標（純損益・PF・最大DD）はRun A(EXP-001)と同等〜わずかに改善、最大連敗は変化なし、
  取引数は+12件増加という結果。EXP-002自体の判定は`HOLD`（Expertsログ待ち）。
  なお初回の試行はMT4のスプレッド設定がRun Aと異なっており（4.1pips、`MaxSpreadPips=3`を
  常時超過）取引数0件になったため不採用とし、設定修正後の再実行分を正式なRun Bとして採用した。

- [x] **HTMLレポート保存**（2026-07-29更新）
  現状: **達成**。Run A分（DS001）・Run B分（DS004）とも保存・checksum記録済み
  （`trading-system/reports/raw/`はgitignore対象のため、ファイル本体はリポジトリには
  含まれず、checksumのみ`DATASET_REGISTRY.md`に記録する運用）。

- [x] **Parameter保存**（2026-07-29更新）
  現状: **達成**。Run B分は`EXP-002`にレポート埋め込みの実測パラメータ一覧を記録済み
  （`MaxDailyLossPercent=2, MaxConsecutiveLosses=3`等、既定値通りであることを確認）。
  Run A分は`EXP-001`にCC001の既定値を記録済みだが、実際に使われた値かどうかは引き続き未確認
  （EXP-001固有の限界として残る）。

- [x] **Commit SHA保存**
  現状: 達成。`PHASE5_1_DECISION_REPORT.md`第2節、`CODE_COMPONENT_REGISTRY.md`(CC002)、
  `VERSION_REGISTRY.md`(VR003)に、ブランチ先端`1cea16ad8916e59dcb26a31c06a6f60546074ebe`および
  本ブランチ固有の4コミットのSHAを記録済み（`git log`で実在確認済み）。
  ※この項目は「SHAが記録されていること」という文書化作業であり、Phase 5-1の品質評価とは無関係。

- [x] **実験登録済み**（2026-07-29更新）
  現状: **達成**。H002に対応する`EXP-002_phase5_1_risk_management.md`を事前登録済み
  （status=`READY`）。ただし実行・結果記録はまだ（下記Backtest Run B参照）。

- [ ] **リスク確認**
  現状: 部分的。`PHASE5_1_DECISION_REPORT.md`第9節に、確認できる範囲の事実（未検証ロジックである
  こと、Signal/Riskが密結合していること、AllowLiveTrading=falseが維持されていること等）を
  文書化済み。ただし、これを踏まえた**人間によるリスク確認・承認**自体は未実施のため未チェック。

## A/B の定義（2026-07-29確定）

2026-07-29のユーザー指示により、Run A/Run Bの定義が確定した。

- **Run A = EXP-001**（`EXP-001_ema_adx_trend_baseline.md`、旧版Baseline）。ただし使用EAビルドが
  CC001(Phase5-1適用前)であることは確定していない、という限界を保持したまま採用する
- **Run B = EXP-002**（`EXP-002_phase5_1_risk_management.md`、CC002/Phase5-1版）。**実行完了**
  （2026-07-29、DS004）

いずれも、`.htm`レポート・使用パラメータ・コミットSHA・データ条件・ファイルハッシュを
`research/data/DATASET_REGISTRY.md`に記録し、`UNVERIFIED_OBSERVATION`ではなく正式なResearch Result
として扱った（`RESEARCH_RULES.md`第0節参照）。Run A・Run Bともにこの基準を満たしている。

## 全体状況（2026-07-29更新）

| 項目 | 状態 |
|---|---|
| コンパイル成功 | 未達 |
| Backtest Run A | **達成**（EXP-001をBaselineとして固定） |
| Backtest Run B | **達成**（EXP-002実行完了、DS004。ただしEXP-002自体の判定はHOLD） |
| HTMLレポート保存 | **達成**（Run A・Run Bとも） |
| Parameter保存 | **達成**（Run B分は実測値、Run A分は既定値想定のまま） |
| Commit SHA保存 | **達成** |
| 実験登録済み | **達成**（EXP-001, EXP-002とも登録済み） |
| リスク確認 | 部分的（事実整理は完了、人間の承認は未実施） |

8項目中6項目が達成。残りはコンパイル確認（ユーザー環境のMetaEditor）と、リスク確認の人間による
承認のみ。**ただしEXP-002自体はExpertsログ未提供のためHOLD判定であり、「Backtest Run B達成」は
あくまで「実行してデータを取得した」という意味であって、「Phase5-1の効果が実証された」という
意味ではない点に注意。** マージ判断における未解決点は`PHASE5_1_DECISION_REPORT.md`の更新版を参照。

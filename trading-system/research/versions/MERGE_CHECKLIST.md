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

- [ ] **Backtest Run B**（2026-07-29更新）
  現状: 未達。`EXP-002_phase5_1_risk_management.md`をCC002(Phase5-1)向けに事前登録済み
  （status=`READY`）。実際のバックテスト実行とレポート提供はユーザー側の作業として残っている。

- [ ] **HTMLレポート保存**（2026-07-29更新、部分達成）
  現状: Run A分（DS001）は保存・checksum記録済み。Run B分（Phase5-1版）は未保存
  （`trading-system/reports/raw/`はgitignore対象のため、提供されたファイルはリポジトリには
  含まれず、checksumのみ`DATASET_REGISTRY.md`に記録する運用）。

- [ ] **Parameter保存**（2026-07-29更新、部分達成）
  現状: Run A分は`EXP-001`にCC001の既定値を記録済み（ただし実際に使われた値かは未確認、上記参照）。
  Run B分は`EXP-002`に使用予定パラメータ（CC002既定値 + `MaxDailyLossPercent=2.0`,
  `MaxConsecutiveLosses=3`）を事前登録済みだが、実行時に変更があれば要更新。

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
- **Run B = EXP-002**（`EXP-002_phase5_1_risk_management.md`、CC002/Phase5-1版）。実行はこれから

いずれも、実行後は`.htm`レポート・使用パラメータ・コミットSHA・データ条件・ファイルハッシュを
`research/data/DATASET_REGISTRY.md`に記録し、`UNVERIFIED_OBSERVATION`ではなく正式なResearch Result
として扱う（`RESEARCH_RULES.md`第0節参照）。Run Aはこの基準を満たし済み。Run Bは未実施。

## 全体状況（2026-07-29更新）

| 項目 | 状態 |
|---|---|
| コンパイル成功 | 未達 |
| Backtest Run A | **達成**（EXP-001をBaselineとして固定） |
| Backtest Run B | 未達（EXP-002は事前登録済み、実行待ち） |
| HTMLレポート保存 | 部分達成（Run A分のみ） |
| Parameter保存 | 部分達成（Run A・Run Bとも事前登録上は記録済みだが、Run Aは実値未確認、Run Bは実行後に確定） |
| Commit SHA保存 | **達成** |
| 実験登録済み | **達成**（EXP-001, EXP-002とも登録済み） |
| リスク確認 | 部分的（事実整理は完了、人間の承認は未実施） |

8項目中3項目が達成、2項目が部分達成、3項目が未達。残りはユーザーによるPhase5-1版バックテストの
実行（MT4上、CC002ビルドで）と、コンパイル確認・リスク確認の人間による承認待ち。

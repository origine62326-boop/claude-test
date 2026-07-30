# Phase 5-1 Decision Report

`RESEARCH_PLATFORM_ROADMAP.md` Phase R1 ステップ3（未マージPhase 5-1の扱い決定）向けの判断材料。
**本文書は事実の整理のみを目的とし、マージすべきか否かの判断は行わない。** 判断は人間が行う。

対応する台帳: `CODE_COMPONENT_REGISTRY.md`のCC002、`VERSION_REGISTRY.md`のVR003、
`BACKTEST_REPRODUCIBILITY.md`のBR002。

作成日: 2026-07-28。全てのGit情報は`git log` / `git diff` / `git merge-tree`の実行結果に基づく
（推測なし）。

---

## 1. 現在のブランチ

- ブランチ名: `claude/ea-v0.3.0-risk-management`
- 派生元(merge-base): `origin/main`との共通祖先は `bb29b92b221697fbae57ba2e978a046796c1a462`
  （"Automate GitHub Release creation on tag push"）
- 現在の`origin/main`はこの共通祖先からさらに進んでおり（PR #8マージ等）、本ブランチはその後の
  main側の変更（研究基盤ドキュメント一式）を含んでいない

## 2. Commit SHA

- ブランチ先端: `1cea16ad8916e59dcb26a31c06a6f60546074ebe`
  （"Mark Phase5-1 code-review-only test items as verified"、2026-07-28 03:50:31 +0000）
- 本ブランチ固有のコミット（merge-base以降、4件、`git log origin/main..origin/claude/ea-v0.3.0-risk-management`で確認）:

| SHA | 日時 | メッセージ |
|---|---|---|
| `0c1510eddb92d4dfacd5b66630fc6eeea601b59c` | 2026-07-27 07:35:01 +0000 | Add workflow_dispatch to release.yml for manual verification |
| `a058abd4281ab063cc142ba21bb2b6a82f4bf107` | 2026-07-27 12:27:14 +0000 | Bump actions/checkout to v5 in release workflow |
| `13fc725a6a6e96fe2dd13af3970e88eeee821d73` | 2026-07-28 01:26:04 +0000 | Implement Phase 5-1: daily loss limit + consecutive loss limit |
| `1cea16ad8916e59dcb26a31c06a6f60546074ebe` | 2026-07-28 03:50:31 +0000 | Mark Phase5-1 code-review-only test items as verified |

## 3. mainとの差分

2種類の比較を分けて記録する（混同すると誤解を招くため）。

### 3.1 本ブランチが「実際に持ち込む変更」（三点diff: `origin/main...origin/claude/ea-v0.3.0-risk-management`）

merge-base(`bb29b92`)からブランチが独自に加えた変更。**これが実質的な差分。**

```
7 files changed, 516 insertions(+), 20 deletions(-)
.github/workflows/release.yml                  |  13 +-
trading-system/CHANGELOG.md                    |  36 +++
trading-system/README_JP.md                    |   4 +
trading-system/TODO.md                         |  12 +-
trading-system/mt4/README_MT4_JP.md            |  16 +
trading-system/mt4/TEST_PLAN_PHASE5-1.md       |  42 +++
trading-system/mt4/USDJPY_LowRisk_Trend_EA.mq4 | 413 ++++++++++++++++++++++++-
```

- `.github/workflows/release.yml`の変更（`workflow_dispatch`追加、`actions/checkout@v4→v5`）は、
  **現在のmainには別コミット経由（"Sync release.yml to main: ..."）で独立に同じ内容が既に反映済み**。
  二点diff（`origin/main..origin/claude/ea-v0.3.0-risk-management`、現時点の実差分）ではこのファイルに
  差分がないことを確認済み。実質的な新規変更ではない。

### 3.2 マージシミュレーション結果（`git merge-tree --write-tree`、読み取り専用、作業ツリー変更なし）

- 実行コマンド: `git merge-tree --write-tree origin/main origin/claude/ea-v0.3.0-risk-management`
- 結果: 終了コード0、結果ツリー`51e1e31957eee42ce380431c9b49c8e4d0d886c8`を単独出力
  （**コンフリクトなしでクリーンにマージ可能**。ファイル単位で実際にコンフリクトマーカー
  `<<<<<<<`/`>>>>>>>`が含まれていないことも全ファイル走査で確認済み）
- マージ結果ツリーには、mainの研究基盤ドキュメント一式（`RESEARCH_CHARTER.md`,
  `research/roadmap/RESEARCH_PLATFORM_ROADMAP.md`等）と、ブランチのPhase 5-1変更
  （`TEST_PLAN_PHASE5-1.md`, `USDJPY_LowRisk_Trend_EA.mq4`内の`MaxDailyLossPercent`関連ロジック等）が
  両方含まれることを確認済み。**現時点でマージした場合、技術的なコンフリクトは発生しない見込み。**

## 4. 変更ファイル一覧

上記3.1の7ファイル（実質的な差分）。うち新規ファイルは`trading-system/mt4/TEST_PLAN_PHASE5-1.md`の1件、
残り6件は既存ファイルの変更。

## 5. コンパイル状態

`PENDING_USER_METAEDITOR_CONFIRMATION`

- 当該ブランチの`trading-system/CHANGELOG.md`には「ブランチ`claude/ea-v0.3.0-risk-management`。
  **コンパイル確認・バックテスト検証待ちのため未タグ・未リリース。**」と明記
- 同CHANGELOG.mdの「既知の制約」節: 「コンパイル確認はユーザー環境のMetaEditorで実施が必要
  (このセッションではMQL4コンパイラを実行できないため、手動コードレビューのみ実施)」
- 比較対象として、main側のv0.1.0(Phase1-4)は`releases/v0.1.0/NOTES.md`に
  「ユーザー環境のMetaEditorでコンパイル確認済み: 0 errors, 0 warnings」と明記されており、
  こちらは確認済み。Phase 5-1はこれと同水準の確認が**まだ行われていない**

## 6. テスト状態

`trading-system/mt4/TEST_PLAN_PHASE5-1.md`（全20項目のチェックリスト）:

| 区分 | 件数 | 内訳 |
|---|---:|---|
| コードレビューで確認済み(✅) | 5件 | #11(手動取引・別Magic非集計), #13(注文履歴取得失敗時), #14(複数ポジション含み損), #15(履歴が決済時刻順でない), #16(同一秒複数決済) |
| 未実施(☐) | 15件 | #1〜#10, #12, #17〜#20 |

- pytest等の自動テストは対象外（MQL4には自動ユニットテストの仕組みがないため、当該TEST_PLAN自体が
  「ストラテジーテスターでの手動再現＋Expertsログ確認」を前提とした設計）
- 分析パイプライン側(Python, CC005/CC006)のpytestは本ブランチの変更範囲外（このブランチはPythonコードを
  変更していない）。参考として、mainの現状ではpytest 36件が実行時点で全通過済み
  （`research/versions/CODE_COMPONENT_REGISTRY.md` CC005参照、Phase 5-1固有の状態ではない）

## 7. バックテスト実施状況

**[2026-07-29更新]** 本節作成時点（2026-07-28）ではスクリーンショットのみの`UNVERIFIED_OBSERVATION`
だったが、その後ユーザーから実際の`.htm`レポートの提供を受け、`EXP-001_ema_adx_trend_baseline.md`
として正式に処理・記録した（`REPRODUCIBLE`、`BACKTEST_REPRODUCIBILITY.md` BR002参照）。
2026-07-29のユーザー指示により、この結果は**Phase5-1の効果検証としてではなく「旧版Baseline」
（Run A）**として位置づけ直された。Phase5-1版（CC002）自体のバックテストは`EXP-002_phase5_1_risk_management.md`
として事前登録済み（Run B、status=`READY`）だが、**まだ実行されていない**。以下、原文（2026-07-28時点）は
そのまま残す。

- 本セッション内の会話で、ユーザー提供のMT4 Strategy Testerスクリーンショット1件が共有された
  （USDJPY H1、PF 0.74、勝率29.89%、最大DD 7.45%等）
- この観察値がPhase 5-1適用後の結果かPhase 5-1適用前(Phase1-4のみ)の結果かは、画像からは特定できない
  （使用EA版・パラメータ設定が未確認のため）→ **[2026-07-29追記] 実ファイルを処理した後もこの点は
  未解消のまま。`EXP-001`の`limitations`参照**
- 実際の`.htm`レポートファイルは未取得。`trading-system`パイプライン(`parse_mt4_report.py`等)を
  通した正式な検証は未実施 → **[2026-07-29追記] 完了済み（EXP-001）**
- 日次損失上限・連敗制限が実際に機能した（狙った通りに新規エントリーを止めた）ことを示すExpertsログの
  確認は、TEST_PLAN_PHASE5-1.mdの該当項目(#2, #5等)が未実施のため、現時点で存在しない →
  **[2026-07-29追記] 引き続き未解消。`EXP-002`の比較項目7・8として、Phase5-1版バックテスト実行時に
  Expertsログの提供を要請中**

## 8. 未解決事項

TEST_PLAN_PHASE5-1.mdの未実施15項目のうち、特に判断材料として重要と考えられるもの:

- **#2, #3(日次損失上限の到達・超過時の挙動)、#5(連敗数到達時の挙動)**: 制限機能そのものが
  意図通り新規エントリーを止めるかどうかの中核的な確認が未実施
- **#8, #9(日次損失ラッチの日付変更後の解除、回復しても当日中は解除されないことの確認)**:
  ラッチ方式の要である「当日中は解除しない」という安全設計が未確認
- **#17, #18(GlobalVariableの残存・キー衝突)**: 複数回のテスト実行や複数口座・複数Symbol運用時に
  意図しない状態干渉が起きないかが未確認
- **#20(不正パラメータ時にOnInitが失敗しEAが起動しないこと)**: 誤設定時の安全側動作が未確認
- 上記に加え、そもそも「MetaEditorでのコンパイル確認(0 errors/0 warnings)」自体が未実施
  （本レポート第5節）

## 9. リスク

事実として確認できる範囲のみ記録する（推測による重大性評価は行わない）。

- **未検証の資金管理ロジックである**: 日次損失上限・連敗制限は、実際に損失を止められなかった場合
  「資金管理機能があるという誤った安心感」を生むリスクがある。この機能が正しく動作することは
  第6-8節の通り現時点で実機確認されていない
- **既存ロジックとの結合度**: `RISK_ENGINE_SPEC.md`に記載の通り、Signal（エントリー判定）とRisk
  （損失制限）が同一`TryEnter()`関数内で密結合しており、Phase 5-1の変更はEAの新規エントリー経路
  全体に影響する（既存ポジションの管理には影響しないと設計上は記載されている）
- **AllowLiveTrading**: `false`のまま維持されている（`configs/risk_limits.yaml`
  `implementation_status.live_approval_status: NOT_APPROVED`）。本ブランチ自体に実口座発注を
  有効化する変更は含まれていない
- **mainとの継続的な乖離**: マージを先送りするほど、mainと本ブランチの差分（現状は7ファイル、
  実質的にはEA本体1ファイルが中心）を人間がレビューするコストは大きくは増えない見込み
  （本ブランチはPython側の変更を含まないため）が、mainが今後EA側に別の変更を加えた場合は
  コンフリクトの可能性が生じる

## 10. 推奨事項（事実ベースのみ）

以下は「マージすべき/すべきでない」という判断ではなく、**本プロジェクト自身が既に定めている
基準（TEST_PLAN_PHASE5-1.md、CHANGELOG.mdの記載）に対して、現状どこが未達かの整理**である。

- `trading-system/CHANGELOG.md`(当該ブランチ)は、Phase 5-1を「未タグ・未リリース」と自己申告して
  おり、その理由として「コンパイル確認・バックテスト検証待ち」を挙げている。この2条件は
  本レポート作成時点でも未充足のままである（第5-7節）
- `TEST_PLAN_PHASE5-1.md`は「実施後の報告項目」として、コンパイル結果・チェックリスト結果・
  v0.2.0との比較バックテスト結果を`releases/v0.3.0/`へ記録することを求めているが、
  `trading-system/releases/`配下にv0.3.0のディレクトリはまだ存在しない
- 技術的なマージ可否（コンフリクトの有無）と、機能としての検証状況は別軸である。第3.2節の通り
  技術的にはクリーンにマージ可能だが、それは「検証が完了している」ことを意味しない
- `MERGE_CHECKLIST.md`（本作業で別途作成）の各項目が、現時点でどこまで満たされているかは
  そちらを参照

## 参照

- `research/versions/CODE_COMPONENT_REGISTRY.md`（CC001, CC002）
- `research/versions/VERSION_REGISTRY.md`（VR003）
- `research/versions/BACKTEST_REPRODUCIBILITY.md`（BR002）
- `research/risk/RISK_ENGINE_SPEC.md`
- `trading-system/configs/risk_limits.yaml`（`implementation_status`）
- `trading-system/mt4/TEST_PLAN_PHASE5-1.md`

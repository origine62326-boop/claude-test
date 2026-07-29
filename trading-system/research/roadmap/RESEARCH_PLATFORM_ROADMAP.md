# Research Platform Roadmap

段階的移行計画。各Phaseは前Phaseの成果物を前提とする。実口座接続は本ロードマップの範囲外とし、
別途承認を要する（`RESEARCH_CHARTER.md`第19節、本文書末尾参照）。

## Phase R0: 研究憲章・台帳・テンプレート（本作業で着手）

- `RESEARCH_CHARTER.md`の作成
- `research/evidence/`, `research/hypotheses/`, `research/experiments/`, `research/features/`,
  `research/data/`, `research/models/`, `research/decisions/`, `research/risk/`, `research/reports/`,
  `research/governance/`, `research/roadmap/`, `research/audits/` の各テンプレート・初期登録
- 完了条件: 本文書一式がレビュー可能な状態でブランチにpushされていること（コード変更なし）

## Phase R1: 既存EA・LSTM・レガシーコードの状態固定と棚卸し（2026-07-28、5ステップの順序を確定）

R2（データ品質基盤）へ進む前に、まず現状を固定点として確定させることを優先する。以下の5ステップは
この順序で実施する（後段のステップは前段の成果物を前提とする）。

```
既存システムの状態固定
  ↓
EA・LSTM・解析コードのバージョン整理
  ↓
未マージPhase 5-1の扱い決定
  ↓
MT4バックテストの正式再現
  ↓
Dataset / Experiment登録
```

### ステップ1: 既存システムの状態固定（完了済み、本PRで着手）

- `main`(EA v0.1.0, Phase1-4)、`claude/ea-v0.3.0-risk-management`(Phase 5-1, 未マージ)、
  レガシーフォルダ`USDJPY_LowRisk_Trend_EA/`(v0.1.0バックアップ)の各コミットSHAを固定点として記録
- `research/audits/CURRENT_SYSTEM_AUDIT.md`の作成（EA, Phase5-1, EMA/ADX/ATRロジック, LSTM予測,
  解析パイプライン等をA-Eに分類、Evidenceレベルを推測なしに付与）
- `research/audits/GAP_ANALYSIS.md`の作成
- 完了条件: 主要コンポーネントのコミットSHAが特定され、監査・ギャップ分析が完了していること

### ステップ2: EA・LSTM・解析コードのバージョン整理（着手済み、台帳作成完了）

- `research/versions/CODE_COMPONENT_REGISTRY.md`を作成。EA(main/Phase1-4)・EA(Phase5-1/未マージ)・
  レガシーEAバックアップ・LSTM・Python解析コード全般・MT4レポート解析・Risk Engine(仕様のみ)・
  Decision Engine(仕様のみ)の8コンポーネントを、Component ID/Version/Git Commit SHA/Branch/Status/
  Dependencies/Owner/Last Verified/Related Dataset/Related Experimentの10項目で固定点として記録
- `research/versions/VERSION_REGISTRY.md`を作成。`trading-system/CHANGELOG.md`のプロジェクトバージョン
  (v0.1.0, v0.2.0, v0.3.0開発中, インフラ, 本研究基盤)と、上記コンポーネントの対応を整理
- `research/versions/BACKTEST_REPRODUCIBILITY.md`を作成。fixtureベースのパーサー再現性(pytest 36件、
  実測確認済み)と、実際のバックテスト観察値(DS002等)の再現性を区別して記録。この過程で
  `releases/v0.1.0/NOTES.md`の写真ベース参考値2件が`DATASET_REGISTRY.md`未登録であるという
  新たなギャップを発見（`BACKTEST_REPRODUCIBILITY.md` BR003参照）
- 全てのGit Commit SHAは`git log`/`git cat-file -e`で実在確認済み（推測・パディングによる
  捏造SHAがないことを機械的に検証済み）
- 残タスク: `MODEL_REGISTRY.md`のcode_commit列へステップ1・2で固定したSHAを反映する作業は未実施
- 完了条件: EA/LSTM/解析パイプラインそれぞれの現在バージョンと、機能ごとの実装状態
  （mainか未マージブランチか）が1箇所から追跡できること（3台帳の作成により概ね達成。
  `MODEL_REGISTRY.md`への反映が残タスク）

### ステップ3: 未マージPhase 5-1の扱い決定（残タスク、人間の意思決定が必要）

- `claude/ea-v0.3.0-risk-management`(Phase 5-1)を今後どう扱うか、次の選択肢等を人間が決定する
  （例: (a) `full_test_plan_status`が完了し次第mainへマージする、(b) 研究基盤側でH002の実験結果が
  出るまでmainへはマージせず現状維持する、(c) その他の方針）
- 決定した方針と理由を、`RISK_ENGINE_SPEC.md`の「未確定・要検討事項」および
  `configs/risk_limits.yaml`の`implementation_status.merge_status`に反映する
  （決定するまでは`NOT_MERGED_TO_MAIN`のまま維持し、先回りしてマージ作業やmain実装済み扱いの
  記述を行わない）
- 完了条件: mainへのマージ方針（する/しない/条件付き）が人間により明示的に決定され、
  文書化されていること。本ロードマップ自体は、この決定が下るまでEA側のコード変更を伴わない

### ステップ4: MT4バックテストの正式再現（残タスク、ユーザーからの実データ提供待ち）

- これまで会話内でスクリーンショット(DS002)のみで確認していた観察値
  (`UNVERIFIED_OBSERVATION`、`MODEL_REGISTRY.md` M001参照)を、実際の`.htm`レポートを用いて
  `trading-system`パイプライン(`parse_mt4_report.py`等)で正式に再現する
- 完了条件: 少なくとも1件の既存バックテストがパイプラインを通して再現され、数値が
  `UNVERIFIED_OBSERVATION`から検証可能な状態になっていること（まだ正式なResearch Result化は
  次のステップで行う）

### ステップ5: Dataset / Experiment登録（残タスク）

- ステップ4で再現したデータを`DATASET_REGISTRY.md`のDS001として正式登録する（`status = ACTIVE`）
- H001（EMA/ADX/ATRトレンドフォロー仮説）について、`EXPERIMENT_TEMPLATE.md`形式で最初の
  experiment_id（例: EXP-001）を発行し、DS001を用いた実験として事前登録する
- 完了条件: DS001が`status = ACTIVE`になり、少なくとも1件のexperiment_idが発行され、
  UNVERIFIED_OBSERVATIONから正式なResearch Result（`RESEARCH_REPORT_TEMPLATE.md`形式）へ
  昇格する準備が整っていること

### Phase R1全体の完了条件

上記5ステップすべてが完了していること。

## Phase R2: データ品質基盤

DS001自体の登録はPhase R1ステップ5で完了させるため、R2では個別データセットの登録ではなく、
**今後追加される全てのデータセットに適用する共通の品質チェック基盤**を対象とする。

- 欠損・重複・異常値・タイムゾーン・時刻順序・未来データ混入チェックを、`DATASET_REGISTRY.md`の
  `known_issues`列への手動記載だけでなく、再利用可能な仕組み（チェックスクリプトまたは手順書）として
  整備する方針を確定する
- 完了条件: 少なくとも1つの新規データセットが、上記チェックを経て`status = ACTIVE`になり、
  既知の品質問題が`known_issues`に記録されていること

## Phase R3: 再現可能なバックテスト基盤

- 既存の`trading-system/analysis/`, `scripts/run_analysis.py`等を、研究基盤の
  `EXPERIMENT_TEMPLATE.md`形式から呼び出せる形に整理する方針を検討
- コード・データのバージョン固定、乱数シード記録の仕組みを整理
- 完了条件: 1件のバックテストが、`experiment_id`付きで再現可能な形で記録できること

## Phase R4: ベースラインモデル

- Random Walk / Always WAIT / Buy and Hold相当 / 単純Momentum / 単純Mean Reversion /
  Logistic Regression / LightGBM の各ベースラインを定義・固定
- 完了条件: 各ベースラインの定義が`MODEL_REGISTRY.md`に登録され、以降変更しない運用が
  合意されていること

## Phase R5: 仮説実験フレームワーク

- H001-H003（および追加される仮説）を`EXPERIMENT_TEMPLATE.md`形式で実験化
- 完了条件: 少なくとも1件の仮説が事前登録済み実験として`RUNNING`または`COMPLETED`になること

## Phase R6: ウォークフォワード検証

- train/validation/testの時系列分割とウォークフォワードの実装方針を確定
- 完了条件: 少なくとも1件の実験がウォークフォワードで検証され、結果が
  `RESEARCH_REPORT_TEMPLATE.md`形式でまとめられること

## Phase R7: Decision Engine

- `DECISION_SCHEMA.md`に基づくBUY/SELL/WAIT出力の実装
- 完了条件: Signal Engineの出力とデータ品質状態を入力として、Decision Engineが
  仕様通りの出力を返すこと（発注は行わない）

## Phase R8: Risk Engineとの統合

- `RISK_ENGINE_SPEC.md`で整理したRisk Engine機能（現状はEA内に密結合）を、Decision Engineから
  分離した形で統合する方針を確定・実装
- 完了条件: Signal EngineがBUY/SELLを出しても、Risk EngineがBLOCK/EMERGENCY_STOPを返した場合に
  最終出力がWAITになることをテストで確認できること

## Phase R9: デモフォワードテスト

- デモ口座でのフォワードテスト運用
- 完了条件: 憲章第13節の採用条件（時系列外データでの正の期待値、コスト込み、ウォークフォワード
  再現、ベースライン超過、複数期間再現等）を満たしたモデル・仮説について、デモ運用での
  再現性を確認する

## 実口座について

実口座での自動発注・実運用は、本ロードマップの範囲外とする。Phase R9のデモフォワードテストが
一定期間・一定件数（具体的な数値基準は証拠なく決め打ちせず、実施時に別途事前登録する）を
満たし、人間による明示的な承認を得た場合にのみ、別途「実運用移行計画」として改めて仕様化する。
`RESEARCH_CHARTER.md`の禁止事項（実口座発注の自動許可なし、`AllowLiveTrading`の既定false等）は
本ロードマップ全体を通じて維持する。

## 既存のEA開発（Phase1-9, `USDJPY_LowRisk_Trend_EA.mq4`）との関係

既存EAのPhase番号（Phase1-9、`trading-system/mt4/`側の開発）と、本ロードマップのPhase R0-R9は
**別の採番体系**である。名称の混同を避けるため、既存EA側は今後も「Phase N」、本研究基盤側は
「Phase RN」と表記を分ける。既存EAの開発自体は本作業の対象外であり、変更していない
（`RESEARCH_CHARTER.md`冒頭の作業範囲、`research/audits/CURRENT_SYSTEM_AUDIT.md`参照）。

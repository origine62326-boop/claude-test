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

### ステップ4: MT4バックテストの正式再現（完了、2026-07-28）

- ユーザーから実際の`.htm`レポート（RakutenSecurities-Demo, Build 1475）の提供を受け、
  `trading-system`パイプライン(`parse_mt4_report.py`等)で正式に処理した
- この過程でパイプライン側の実装バグ6件（文字コード、ラベル表記ゆれ、行修飾語の分離、
  連勝/連敗の主値副値逆転、操作履歴のcolspan省略）を発見・修正した
  （`research/versions/BACKTEST_REPRODUCIBILITY.md`, `trading-system/CHANGELOG.md` v0.2.1参照）
- 完了条件: 達成。DS002由来の`UNVERIFIED_OBSERVATION`が、DS001としてパイプラインを通した
  検証可能な数値になった（`currency`を除く全必須フィールド抽出成功、操作履歴184件中183件を
  正しくペアリング）

### ステップ5: Dataset / Experiment登録（完了、2026-07-28）

- `research/experiments/EXP-001_ema_adx_trend_baseline.md`を実データを見る前に事前登録
  （baseline, データ分割方法, コスト前提の取得方針, `configs/acceptance_criteria.yaml`を
  流用した採用/棄却条件）
- `DATASET_REGISTRY.md`のDS001を`status = ACTIVE`として正式登録（checksum記録済み）
- EXP-001を実データで実行し、`status = COMPLETED`, `decision = HOLD`（最低取引数200件に対し
  184件で未達のため参考外。PF・期待値も未達）として記録
- `HYPOTHESIS_REGISTRY.md` H001のstatusをHOLDへ更新、`MODEL_REGISTRY.md` M001の`metrics`を
  UNVERIFIED_OBSERVATIONから実測値へ更新
- 完了条件: 達成。ただしH001自体はサンプル不足のため未確定のまま（ADOPTED/REJECTEDではなくHOLD）。
  さらなるデータでの追加検証はPhase R5以降の課題として残る

### Phase R1全体の完了条件

上記5ステップすべてが完了していること。2026-07-28時点の進捗: ステップ1・4・5は完了。
ステップ2は台帳作成が完了し、`MODEL_REGISTRY.md`のcode_commit列への反映のみ残タスク。
ステップ3（未マージPhase 5-1の扱い決定）は人間の意思決定待ちのまま未着手。
Phase R1全体としては、ステップ3の決定が下るまで未完了とする。

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

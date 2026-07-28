# Research Platform Roadmap

段階的移行計画。各Phaseは前Phaseの成果物を前提とする。実口座接続は本ロードマップの範囲外とし、
別途承認を要する（`RESEARCH_CHARTER.md`第19節、本文書末尾参照）。

## Phase R0: 研究憲章・台帳・テンプレート（本作業で着手）

- `RESEARCH_CHARTER.md`の作成
- `research/evidence/`, `research/hypotheses/`, `research/experiments/`, `research/features/`,
  `research/data/`, `research/models/`, `research/decisions/`, `research/risk/`, `research/reports/`,
  `research/governance/`, `research/roadmap/`, `research/audits/` の各テンプレート・初期登録
- 完了条件: 本文書一式がレビュー可能な状態でブランチにpushされていること（コード変更なし）

## Phase R1: 既存EAとLSTMコードの棚卸し（本作業で着手）

- `research/audits/CURRENT_SYSTEM_AUDIT.md`の作成
- `research/audits/GAP_ANALYSIS.md`の作成
- 完了条件: 既存コンポーネント（EA, Phase5-1, EMA/ADX/ATRロジック, LSTM予測, 解析パイプライン等）が
  A-Eに分類され、Evidenceレベルが推測なしに付与されていること

## Phase R2: データ品質基盤

- `DATASET_REGISTRY.md`のDS001（MT4バックテストレポート）を実データで正式登録（現状はディレクトリのみ）
- 欠損・重複・異常値・タイムゾーン・時刻順序・未来データ混入チェックの実装方針を確定
- 完了条件: 少なくとも1つのデータセットが`status = ACTIVE`になり、既知の品質問題が
  `known_issues`に記録されていること

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

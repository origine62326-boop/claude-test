# Observation Schema

**ステータス: 骨格のみ（2026-07-31作成）。Hypothesisの本格登録・検証開始はPhase 2/3（データ取得経路・
分足データ基盤の確定）まで凍結する。本文書はスキーマと運用ルールのみを定義し、この時点でObservation IDの
実登録は行わない。**

## 位置づけ

`FACT_SCHEMA.md`で定義したFact（生データ）と、`trading-system/research/hypotheses/HYPOTHESIS_REGISTRY.md`
のHypothesis（検証対象の仮説）の間に位置する層。ユーザーが採用した3層構造（Fact→Observation→
Hypothesis）における中間層である。

## Observationとは何か

**Observation = 1件以上のFactから、決まった計算方法（決定的な計算のみ）によって導出された、
解釈を含まない事実の集計・変換。**

- Observationは「解釈」ではなく「計算」でなければならない。例:
  - OK: 「米雇用統計発表（Fact F-012）の前後30分におけるUSDJPY H1終値の変化率は+0.42%だった
    （Fact F-034, F-035から算出）」
  - NG: 「米雇用統計が強かったのでドル買いが優勢だった」（因果の解釈、方向性の断定を含むためObservationではない）
- Observationは必ず、使用した全Fact IDと計算方法（式・パラメータ・使用したコード/スクリプト名）を
  明記し、他者が同じFactから同じObservationを再現できなければならない（`RESEARCH_RULES.md`第7節
  「再現性」と同じ基準）。
- Observationは「効きそう」「有意そう」といった評価・スコア・確信度を含まない。それらは
  Hypothesisの検証結果（Experiment）側で扱う。
- Observationは複数のFactにまたがってよいが、使用したFactの`revision_status`（速報値/改定値）が
  混在する場合、どちらを使ったかを明記する（未来の改定値を過去時点の判定に使わない、という憲章の
  原則をObservation生成時点でも守るため）。

## Observation ID体系

`O-###`。

## 必須フィールド

| フィールド | 説明 |
|---|---|
| observation_id | 一意のID（`O-001`形式） |
| title | 何を計算したかの短い説明 |
| input_fact_ids | 使用した`fact_id`のリスト（すべて`FACT_REGISTRY.md`に存在すること） |
| computation_method | 計算方法（式・アルゴリズム・使用スクリプト/関数名とバージョン） |
| computed_value | 算出結果の値（または値へのファイル参照 + checksum） |
| computed_at | 計算実行日時 |
| code_version | 計算に使用したコードのGit commit SHA（`RESEARCH_RULES.md`第8節と同基準） |
| timezone | 時刻を含む場合の基準タイムゾーン |
| leakage_check | 使用したFactの`event_time`/`retrieved_at`が、想定する判定時刻より後になっていないかの確認結果（`FEATURE_REGISTRY.md`の`availability_time`概念と同様の考え方） |
| known_limitations | 既知の制約（サンプル数不足、欠損補完の有無等） |
| status | `DRAFT` / `VERIFIED` / `QUARANTINED` |
| created_at | 登録日時 |

## Observationからの禁止事項

- Observationの時点で「買い」「売り」「効果あり」等の方向性・評価判断を含めない。
- Observation生成後に、都合の良い結果が出るまで`computation_method`を調整して再計算し、
  古いObservationを上書きしない（新しい`observation_id`を発行する。`RESEARCH_RULES.md`第4節と同じ扱い）。
- Fact不足・欠損によりObservationが計算不能な場合は、Observationを作らず`status`を`QUARANTINED`のまま
  残すか、`computed_value`を`UNKNOWN`とし理由を明記する（無理な補完をしない）。

## Hypothesisへの接続

- `HYPOTHESIS_REGISTRY.md`の各行は、根拠として使うObservationがあれば`observation_ids`（新設予定の列。
  Phase 4でHypothesis登録を再開する際に、既存の`evidence_ids`列と並べて追加を検討する）を明記すること。
- Observationの存在は、それだけでHypothesisをEvidenceへ昇格させる理由にはならない
  （`RESEARCH_RULES.md`第5節と同じ原則）。

## 今後の実装（Phase 3以降、現時点では未着手）

- `research/observations/OBSERVATION_REGISTRY.md`（実データ台帳）は、Phase 3のデータ基盤設計確定後に
  作成する。
- 本ファイルはPhase 1時点ではスキーマ定義のみであり、実Observation登録は行わない。

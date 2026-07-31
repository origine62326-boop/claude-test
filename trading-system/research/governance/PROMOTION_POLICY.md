# Promotion Policy

**ステータス: 骨格のみ（2026-07-31作成）。Fact/Observation層に基づく実際の昇格判定は、Phase 4
（Hypothesis検証再開）以降に発生する。本文書は昇格経路のルールのみを先に定義する。**

## 位置づけ

Fact→Observation→Hypothesis→Evidenceという昇格経路について、各層の間で「何が揃えば次の層に進めるか」
を明文化する。`RESEARCH_CHARTER.md`第2節「根拠がないものは仮説として扱う」「実装前にEvidenceレベルを
付与する」、および`RESEARCH_RULES.md`第5節「EvidenceとHypothesisの分離」を運用レベルで補強する。

## 昇格の基本原則

- 昇格は常に一方向（Fact→Observation→Hypothesis→Evidenceのうち上位方向）へのみ行い、下位層の記録を
  昇格に伴って書き換えない（元のFact/Observationはそのまま残す）。
- どの昇格も、**それ単独の結果が良かった/悪かったという理由だけでは行わない**。以下の各段階の要件を
  満たすことが必要条件であり、要件を満たしても自動昇格はしない（人間による確認・承認を要する場面が
  ある場合は明記する）。

## 段階1: Fact → Observation

要件（`FACT_SCHEMA.md`, `OBSERVATION_SCHEMA.md`参照）:

- Observationが参照する全Fact IDが`FACT_REGISTRY.md`（Phase 3以降に新設）に存在し、`status=VERIFIED`
  であること。
- 計算方法（`computation_method`）が決定的（同じ入力から常に同じ出力）であり、再現可能であること。
- Observation自体に方向性の解釈・スコア・確信度を含まないこと（含む場合はObservationではなく
  Hypothesisとして扱う）。

## 段階2: Observation → Hypothesis

要件:

- `HYPOTHESIS_POLICY.md`の登録条件（登録上限、事前登録原則、多重検定ファミリーの記録）を満たすこと。
- 現時点で新規Hypothesis登録自体が凍結中のため、本段階の昇格はPhase 2/3完了まで発生しない。
- Hypothesisの`evidence_level`は登録時点では原則`H`（検証前の仮説）とする。Observationの存在だけで
  `evidence_level`を`H`より上に設定しない。

## 段階3: Hypothesis → Evidence

要件（`RESEARCH_CHARTER.md`第3〜4節、`RESEARCH_RULES.md`第5節の再確認）:

- Evidenceは信頼できる情報源（BIS/FRB/ECB/日銀/CFTC/査読論文/公式仕様等、`DATA_SOURCE_REGISTRY.md`
  Phase 2で確認された一次情報源）そのものに基づくものに限る。
- **Hypothesisの検証実験（Experiment）が良好な結果を出したことは、それ単独ではEvidenceへの昇格理由に
  ならない**。実験結果は「この仮説を支持する実験結果が得られた」という事実として
  `HYPOTHESIS_REGISTRY.md`・`EXPERIMENT_TEMPLATE.md`側に記録するに留める。
- Evidence化するのは、あくまで仮説の背景にある一次情報源（例: 「BISのワーキングペーパーがこの現象を
  報告している」）であり、自社の実験結果そのものをEvidenceとして登録しない。実験結果は
  Hypothesisの`status`（ADOPTED等）と`EXPERIMENT_TEMPLATE.md`の記録によって管理する。

## 段階4: Hypothesis → ADOPTED（実運用判断への使用可否）

要件（`RESEARCH_CHARTER.md`第13節の再確認。新規追加ではない）:

- 採用条件（時系列外データでの正の期待値、コスト込み、ウォークフォワード再現、複数期間再現、
  最低取引件数、リスク制約内、事前登録済みの採用条件、等）を満たすこと。
- `MULTIPLE_TESTING_POLICY.md`確定後は、検定した仮説母数に対する多重検定補正を経ていること。
- ADOPTED判定であっても、それはSignal Engineとしての採用に限られ、Risk Engineの制約
  （`RESEARCH_CHARTER.md`第15節）を上書きしない。

## 降格・無効化

- 一度昇格した記録でも、後から品質問題（データ破損、未来データ混入発覚等）が判明した場合は、
  `DATASET_REGISTRY.md`の`QUARANTINED`と同様の考え方で、該当するFact/Observation/Hypothesisの
  `status`を`QUARANTINED`または`INVALIDATED`に変更する。ただし記録自体は削除・書き換えず、
  取り消し線+追記の形で残す（`RESEARCH_RULES.md`第10節）。

## 今後の実装

- 各段階の昇格記録（誰が・いつ・どの要件を確認して昇格させたか）をどこに記録するかは、Phase 4で
  `HYPOTHESIS_REGISTRY.md`の運用と合わせて確定する。

# Hypothesis Policy

**ステータス: 骨格のみ（2026-07-31作成）。本文書自体はHypothesisの追加・修正ルールを定義するが、
Fact/Observation層に基づく新規Hypothesisの本格登録・検証開始は、Phase 2（データソース調査）・Phase 3
（分足+経済指標データ基盤設計）が完了しデータ品質が確認されるまで凍結する。**

## 位置づけ

`trading-system/RESEARCH_CHARTER.md` 第5節（Hypothesis）・`RESEARCH_RULES.md` 第4節（新experiment_id
発行の原則）を、Fact/Observation層の導入に伴い補強するもの。矛盾がある場合は`RESEARCH_CHARTER.md`を
優先する。

## 背景

過去20年の経済ニュースとFX変動の網羅的分析という目標は、性質上「大量の切り口・条件の組み合わせ」を
生みやすい（例: 通貨ペア×指標種類×時間帯×窓幅の組み合わせだけで容易に数百〜数千パターン）。
この種の探索は、検証を経ずに大量の仮説を登録・試行すると、偶然良く見えるパターンを実力と誤認する
多重検定問題（data dredging / multiple comparisons problem）を引き起こす。本ポリシーはこれに対する
歯止めを定める（詳細な統計的取り扱いは`MULTIPLE_TESTING_POLICY.md`）。

## 凍結条件（現在の状態）

- **現在、Fact/Observation層に基づく新規Hypothesisの登録・検証は凍結中**。
- 凍結解除の条件: `DATA_SOURCE_REGISTRY.md`（Phase 2）でデータソースの取得可否・品質・時間精度が
  確認され、かつPhase 3のデータ基盤（分足価格データ + 経済指標イベントの時刻付き結合）が設計・
  最低限のデータ品質確認を経ていること。
- 凍結解除は本文書またはロードマップ文書（`research/roadmap/RESEARCH_PLATFORM_ROADMAP.md`）への
  追記という形で明示的に記録し、暗黙のうちに再開しない。
- 既存の`H001`〜`H003`（`HYPOTHESIS_REGISTRY.md`）は本凍結の対象外（Fact/Observation層導入前に
  既に登録済みのため）。ただし、これらの仮説について新しいバリエーション（新しい条件・閾値等）を
  追加登録する場合は、下記「登録上限」「事前登録の原則」に従う。

## 登録上限（多重検定対策の基本方針）

- Fact/Observation層に基づく新規Hypothesisは、**一度の調査サイクルで登録できる件数に上限を設ける**。
  具体的な上限値は、`MULTIPLE_TESTING_POLICY.md`で採用する多重検定補正方法（Bonferroni、
  Benjamini-Hochberg等）と整合させて確定する（Phase 4着手時に確定。現時点では決め打ちしない）。
- 上限に達した場合、新しいHypothesisを追加するには、既存の未検証Hypothesisをまず`REJECTED`/`HOLD`/
  `INVALIDATED`のいずれかに確定させるか、上限自体の引き上げについて変更理由とともに承認を得る。

## 事後的なバリエーション登録の禁止

- あるHypothesisの検証（Experiment）を実行し結果を見た後に、条件・閾値・時間窓等を変えた
  「類似だが微妙に異なる」新しいHypothesisを、あたかも独立した仮説であるかのように登録することを
  禁止する（`RESEARCH_RULES.md`第3節「テストデータを見た後の最適化禁止」の拡張）。
- 結果を見た後に条件を変えたい場合は、次のいずれかを満たすこと。
  1. 新しい`hypothesis_id`を発行し、**旧hypothesis_idへの参照と変更理由を明記**した上で、
     新しい未使用のtest_periodで再検証する。
  2. 変更後のHypothesisを、多重検定の母数（上記「登録上限」でカウントする件数）に加算する
     （既存Hypothesisの「言い換え」として無料で追加しない）。
- 1つの根本アイデアから生成された複数のバリエーション（パラメータ違い等）は、`HYPOTHESIS_REGISTRY.md`
  上で「ファミリー」として相互参照できるようにし（例: 備考欄に関連hypothesis_idを列挙）、
  `MULTIPLE_TESTING_POLICY.md`の補正計算時にファミリー単位で扱えるようにする。

## Hypothesis登録の必須条件（既存ルールの再確認）

- 登録には`RESEARCH_CHARTER.md`第6節の必須フィールドを満たすこと。
- Fact/Observation層に基づくHypothesisは、根拠として使用したObservation ID（`observation_ids`）を
  明記すること（`OBSERVATION_SCHEMA.md`参照）。
- 「なんとなく効きそう」「一般的に言われている」等、Fact/Observationの裏付けのない理由だけでの登録を
  禁止する（`RESEARCH_CHARTER.md`第19節と同じ原則）。

## 今後の実装

- 具体的な登録上限値・多重検定補正方法は`MULTIPLE_TESTING_POLICY.md`で確定する（Phase 4着手時）。
- `HYPOTHESIS_REGISTRY.md`に`observation_ids`・`hypothesis_family_id`列を追加するかどうかは、
  Phase 4でHypothesis登録を再開する際にあわせて検討する（現時点では未実施）。

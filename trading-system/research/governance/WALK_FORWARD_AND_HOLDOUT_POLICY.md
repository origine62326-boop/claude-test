# Walk-Forward and Holdout Policy

`research/DATA_EXPANSION_PHASE.md`に基づく、期間分割と Holdout 保護の方針。
2026-08-15、ユーザー指示により新設。

**本方針はデータ取得の前に確定させる。** 取得後に都合よく期間を切ることを防ぐためである
（`RESEARCH_RULES.md`第3節「テストデータを見た後の最適化禁止」の期間版）。

## 分割原則（年月ではなく長さで固定）

利用可能なデータ期間が確定していないため、**具体的な年月ではなく長さのルールを先に固定する**。

| 項目 | 値 | 備考 |
|---|---|---|
| Discovery / Research 長 | **24ヶ月** | 仮説生成・特徴量探索用 |
| Validation 長 | **24ヶ月** | 事前登録仮説の評価用 |
| Step 幅 | **12ヶ月** | Rolling Walk-Forward の前進幅 |
| Final Historical Holdout 最低長 | **12ヶ月** | 取得データの最新側に予約 |
| Fold最低取引数（全体） | **150件以上** | 下回るfoldは判定に使わない |
| Fold最低取引数（方向別） | **50件以上** | `EXP-009`/`EXP-010`のGuardrailと整合 |

### Validation を 24ヶ月とする根拠（実測ベース）

`LEGACY_DATA_EPOCH`での取引密度は年間175〜200件、うち買い90〜140件だった。
方向限定の仮説にフィルターを適用すると削減率は37〜71%（`EXP-008`〜`EXP-010`実績）であり、
**12ヶ月foldでは買いが26〜88件にしかならない**。実際に`EXP-009`（42件）と`EXP-010`（24件）で
最低取引数Guardrailを2回連続で下回っている。12ヶ月foldを採用すると同じ失敗を構造的に繰り返す。

## Fold の3分類

| 分類 | 用途 | 参照可否 |
|---|---|---|
| **A. Discovery / Research** | 仮説生成、特徴量探索、レジーム分析 | 自由に参照可 |
| **B. Validation / Development OOS** | 事前登録した仮説の反復評価 | Budget管理下で参照可（`HYPOTHESIS_FOLD_BUDGET.md`） |
| **C. Final Historical Holdout** | 最終候補のみの評価 | **開発中は参照しない** |

## Overlap Fold の扱い（重要）

Validation 24ヶ月 / Step 12ヶ月という設計では、**隣接する Validation Fold が12ヶ月重複する**。

> **overlapした複数Foldを、完全に独立した複数のEvidenceとして数えてはならない。**

- Rolling Validation は**開発用**として使用可能（傾向の確認、頑健性の感触を得る目的）
- しかし「5 foldで4回改善した」という記述は、overlapがある限り**5回の独立試行ではない**
- Evidence の独立性を主張できるのは以下に限る:
  - **non-overlapping period** で得られた結果
  - **Final Historical Holdout**
  - **Live Forward**（将来）

記録時は必ず「overlapの有無」を併記する。

## Final Holdout

### Historical Final Holdout

- 取得データの**最新12ヶ月**を予約する
- 開発中は参照しない
- Validation を通過した**最終候補のみ**が使用できる
- **1 Hypothesis につき原則1回**

**消費ルール**: Holdout の結果を見た後に、ロジック・閾値・条件・特徴量のいずれかを変更した場合、
その Holdout は**消費済み**として記録し、以後その Hypothesis の証拠には使わない。

### Live Forward Holdout（将来）

Historical Final Holdout と **Live Forward Holdout を分離する**。

- Historical: 過去データ上の最終確認
- Live Forward: デモ口座等での前向き検証

**最終的なProduction判断では Live Forward Evidence を重視する設計とする。**
Historical Holdout の通過は必要条件であって十分条件ではない。

## Sign Consistency の記録

今後のOOS評価では、平均改善幅だけでなく **何Fold中何Foldで改善方向が再現したか**を記録する。

例: `Positive effect in 4 / 5 folds`

ただし上記「Overlap Fold の扱い」の通り、overlapping folds を完全独立試行として扱わない。
記載時は `Positive effect in 4 / 5 folds (overlapping, not independent trials)` のように明記する。

## Effect Size の評価（固定基準は作らない）

今後の実験では、可能な範囲で以下を記録できる設計とする。

- Effect size
- Standard error
- Bootstrap CI
- Fold-to-fold variability（`DIAG-DATA-002`で測定）
- Data-source variability（`DIAG-DATA-001`で測定）
- Effect sign consistency

目的は、H006の +0.02R〜+0.06R のような改善が、Baseline Variability や Data Source Variability に
対して十分大きいかを**後から判断できるようにする**ことである。

**禁止事項**:

- 現段階で「+0.05R以下は無意味」のような固定基準を作らない
- `DIAG-DATA-001` / `DIAG-DATA-002` の結果を見てから、既存 Hypothesis の判定条件を遡及的に
  変更しない（`RESEARCH_RULES.md`第3節）

## created_at / updated_at

- created_at: 2026-08-15
- updated_at: 2026-08-15（初版。データ取得前に確定）

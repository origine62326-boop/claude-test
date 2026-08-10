# Diagnostic Study Registry

`research/hypotheses/HYPOTHESIS_REGISTRY.md`とは別に管理する、**Diagnostic Study**（既存戦略・
既存データのボトルネック診断、「勝てるルールの仮説」の新規提案ではないもの）の一覧管理表。
2026-08-02、ユーザー指示により新設（DIAG-001の依頼を機に、無理にHypothesisとして登録しない
管理方法として導入）。

## Diagnostic StudyとHypothesisの違い

- **Hypothesis**（`HYPOTHESIS_REGISTRY.md`）: 「この条件を追加/変更すると期待値やリスク指標が
  改善するのではないか」という、検証対象の主張。ADOPTED/REJECTED等の採否判定に進みうる
- **Diagnostic Study**（本レジストリ）: 「なぜ今の数値がこうなっているのか」を、既存の確定済み
  実験データ（`EXP-###`）を対象に事実ベースで分析するもの。新しい売買ルールを主張しない。
  採否判定の対象ではなく、`Primary Bottleneck`等の**診断結果**を出力する

`RESEARCH_RULES.md`第11節「追加してよいものの範囲」に、本レジストリ新設に伴い
「Diagnostic Study（既存データの原因分析、新しい売買ルールを主張しないもの）」を追加した。

## ID体系

`DIAG-###`。Hypothesis(`H###`)・Experiment(`EXP-###`)とは独立した採番。

## status候補

`DRAFT` / `RUNNING` / `BLOCKED` / `COMPLETED`。既存の実験status語彙（`DRAFT / READY / RUNNING /
COMPLETED / ADOPTED / HOLD / REJECTED / INVALIDATED`）とは意図的に異なる、Diagnostic Study専用の
軽量な語彙とする（ADOPTED/HOLD/REJECTED/INVALIDATEDは「採否判定」を前提とした語であり、診断には
そぐわないため転用しない）。新規に追加したのは`BLOCKED`のみ（「外部データ待ちで一時停止」を表す
既存語がなかったため）。

- `DRAFT`: 診断計画のみ、未着手
- `RUNNING`: 一部の診断項目を実行中
- `BLOCKED`: 追加データ取得待ちで停止中（理由を明記すること）
- `COMPLETED`: 全診断項目（Stage分割している場合は全Stage）が完了

## 一覧

| diagnostic_id | title | 対象 | 関連Hypothesis | 対象データ | status | Primary Bottleneck判定 | Confidence | 関連ファイル |
|---|---|---|---|---|---|---|---|---|
| DIAG-001 | 現行USDJPY H1トレンドフォローEAのEntry/Exitボトルネック診断 | `USDJPY_LowRisk_Trend_EA`(H1, 現行基準戦略) | H001, H002 | DS001(EXP-001), DS004(EXP-002), DS006(H1価格履歴, Stage2)。DS005(EXP-003)は個別トレード情報なしのため対象外 | **COMPLETED**（Stage1・Stage2とも完了、2026-08-10） | MIXED（ENTRY=MEDIUM-HIGH confidenceで確認、EXIT[利益保護の不在]=MEDIUM-HIGH confidenceで確認、DIRECTION_ASYMMETRY=HIGH confidenceで確認、POSITION_SIZING=MEDIUM confidenceで副次的要因と確認） | 論点ごとに異なる（本文参照、総合MEDIUM-HIGH） | `DIAG-001_ENTRY_EXIT_ANALYSIS.md`, `DIAG-001_TRADE_LEVEL_SCHEMA.md`, `DIAG-001_DATA_REQUIREMENTS.md`, `DIAG-001_NEXT_EXPERIMENT_CANDIDATES.md` |

## 運用ルール

- Diagnostic Studyの結果は、それ単独ではHypothesisをADOPTED/REJECTEDへ進める根拠にしない
  （`RESEARCH_RULES.md`第5節と同じ精神。診断結果は「次にどのHypothesis/Experimentを検証すべきか」
  の優先順位付けに使う）
- 診断結果を見た後に、診断の途中で対象データや集計軸を都合よく変更しない。変更が必要な場合は
  新しい`diagnostic_id`を発行する（`RESEARCH_RULES.md`第3-4節と同じ原則）
- Diagnostic StudyからEntry/Exitフィルターやパラメータ変更の実装を直接行わない。診断結果に基づいて
  新しいHypothesis（`H###`）または実験候補（`EXP-###`の候補、`BACKTEST_COVERAGE_EXPANSION_PLAN.md`
  経由）を提案するに留める

## created_at / updated_at

- created_at: 2026-08-02
- updated_at: 2026-08-10（DIAG-001 Stage2完了、statusをBLOCKED→COMPLETEDへ更新）

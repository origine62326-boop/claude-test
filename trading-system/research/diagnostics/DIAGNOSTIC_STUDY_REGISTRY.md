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
| DIAG-DATA-001 | Data Source Noise Floor（データソース差だけで生じる結果変動の測定） | `USDJPY_LowRisk_Trend_EA`（無改造Baseline） | なし（特定仮説の検証ではない） | 同一期間・同一EA・同一パラメータ・**異なるデータソース**（Rakuten MT4 vs 外部取得M1等） | `DRAFT`（データ取得待ち） | 対象外（ボトルネック診断ではなくデータ感度測定） | 対象外 | 本レジストリ内「DIAG-DATA-001 設計」節 |
| DIAG-DATA-002 | Baseline Temporal / Regime Variability（期間差による結果変動の測定） | `USDJPY_LowRisk_Trend_EA`（無改造Baseline） | なし（特定仮説の検証ではない） | **同一データソース**・同一EA・同一パラメータで、Foldごとに期間のみを変えた結果 | `DRAFT`（データ取得待ち） | 対象外 | 対象外 | 本レジストリ内「DIAG-DATA-002 設計」節 |

## DIAG-DATA-001 設計（Data Source Noise Floor）

### 目的

同一期間・同一EA・同一パラメータで**データソースだけを変えた**場合に、結果がどれだけ変化するかを
測定する。これは純粋な **Data Source Sensitivity** であり、市場の性質ではなくデータ提供側の差
（ティック生成方式・Bid/Ask仕様・欠損・タイムゾーン等）に起因する変動である。

### 比較する指標

**集計レベル**: Trade count / Entry一致率 / Exit一致率 / PF / Expectancy R / Net Profit /
Max DD / Win rate / Long・Short別結果 / SL・TP分類の内訳 / MFE・MAE

**トレード単位マッチング**（entry時刻が同一H1バーに入るものを対応付ける）:

| 分類 | 定義 |
|---|---|
| Full match | entry・exitとも同一バーに収まる |
| Entry-only match | entryは一致するがexitが異なる（SL/TP到達順序の差） |
| Exit difference | 一致トレード内での決済価格・決済理由の差 |
| Source-exclusive trade | 片方のソースにしか存在しないトレード |

### 記録形式

Noise Floorを**単一の±Xという数字にまとめない**。各指標の差分を**分布**として記録する
（中央値・四分位・最大乖離）。

### 事前の確約（結果を見た後の基準変更禁止）

- 本Studyの結果を見てから、既存Hypothesis（H004〜H007）の判定基準を変更しない
- 本Studyの結果は「今後の効果量を評価する際の参照値」として使い、過去の判定には遡及適用しない
- H006の +0.02R〜+0.06R がこの変動幅の範囲内かどうかを**後から比較可能にする**ことが目的であり、
  「範囲内だったから無効」と自動的に結論づけるための装置ではない

## DIAG-DATA-002 設計（Baseline Temporal / Regime Variability）

### 目的

**同一データソース**・同一EA・同一パラメータで、**期間だけ**を変えた場合に、Baseline戦略の結果が
どれだけ変動するかを測定する。

### 「ノイズ」と断定しない

期間差には**本物のMarket Regime差が含まれる**。したがって本Studyの測定値を「ノイズ」と呼ばず、
`Temporal / Regime Variability` として扱う。低ボラ期と高ボラ期でPFが違うのは、測定誤差ではなく
市場の実態である可能性が高い。

### Foldごとに記録する指標

- PF
- Expectancy R
- Trade count
- Max DD
- Win rate
- Long PF / Short PF
- Long Expectancy R / Short Expectancy R

### 本Studyの動機（実測済みの予備的事実）

`LEGACY_DATA_EPOCH`の3期間で、無改造EAの全体PFは既に大きく変動している。

| 期間 | dataset | 全体PF |
|---|---|---|
| 2025-07〜2026-07 | DS004 | 0.76 |
| 2024-07〜2025-07 | DS013 | 1.16 |
| 2024-01〜2024-07 | DS015 | 1.17 |

一方、これまでに見つかった最良の効果量は買い期待値R +0.02〜+0.06である。
**期間変動が処理効果を大きく上回っている可能性**があり、これを定量化しないまま仮説検証を続けると、
検出不可能な効果を追い続けることになる。

ただし上記3期間はfold設計前の非統制な比較であり、`DIAG-DATA-002`では
`WALK_FORWARD_AND_HOLDOUT_POLICY.md`の分割規則に従って統制した上で再測定する。

## DIAG-DATA-001 と DIAG-DATA-002 を分離する理由

両者を「Noise Floor」として一括りにしない。

- `DIAG-DATA-001`: **データ提供側**に起因する変動。減らせる可能性がある（より良いデータを使う）
- `DIAG-DATA-002`: **市場側**に起因する変動。減らせない。むしろレジーム判定で「いつ動かすか」を
  決めるための情報になる

対処法が正反対であるため、混ぜて測定してはならない。


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
- updated_at: 2026-08-15（Data Expansion Phase開始に伴い`DIAG-DATA-001`（データソース感度）と
  `DIAG-DATA-002`（期間/レジーム変動）を登録。両者を意図的に分離した理由も記載）

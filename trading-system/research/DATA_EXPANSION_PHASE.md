# Data Expansion / Validation Phase

2026-08-15、ユーザー指示により正式開始。本フェーズは`RESEARCH_PLATFORM_ROADMAP.md`のPhase R0-R9
とは別枠の、**横断的な基盤整備フェーズ**として位置づける（既存Phase番号を振り直さない）。

## このフェーズの目的（PF改善ではない）

**本フェーズの目的は「PFを改善すること」ではない。** 以下9点の達成をもって完了とする。

1. 長期データを利用可能にする
2. Layer A / Layer B を分離する（`governance/DATA_LAYER_SPEC.md`）
3. 新Data Epochでのベースラインを確立する
4. Data Source Variability を測定する（`DIAG-DATA-001`）
5. Temporal / Regime Variability を測定する（`DIAG-DATA-002`）
6. Walk-Forward を実行可能にする（`governance/WALK_FORWARD_AND_HOLDOUT_POLICY.md`）
7. Final Holdout を保護する
8. Hypothesis Adaptation History を追跡可能にする（`HYPOTHESIS_FOLD_BUDGET.md`）
9. Effect Size が検出可能な水準かを評価可能にする

## 開始の経緯（なぜロジック探索を止めるのか）

`EXP-008`〜`EXP-010`（H006、トレンド成熟度フィルター）の検証を通じて、以下が判明した。

- 固定閾値`MaxBuyTrendDurationBars=50`の買いシグナル削減率が、期間ごとに-36.9% / -53.8% / -71.1%と
  大きく変動した（`EXP-010`）
- その対処として自然に思いつく「相対指標への変換」を3定義試したが、いずれも削減率を安定させなかった
  （`O-007`、変動幅27〜29pt vs 固定閾値33.8pt）
- **より根本的な問題**: 同一の無改造EAの全体PFが、期間だけで0.76（DS004）/ 1.16（DS013）/
  1.17（DS015）と変動している。一方で我々が見つけた最良の効果量は買い期待値R +0.02〜+0.06であり、
  **期間変動が処理効果より遥かに大きい**

この状態で新しいEntry/Exitロジックを探索しても、効果とノイズを区別できない。したがって
ロジック探索を一旦停止し、検証可能性そのものを整備する。

## Data Epoch（世代管理）

高品質データ（M1/Tick）導入の前後で、データ世代を分離する。**旧データは削除しない。**

| epoch | 対象 | 扱い |
|---|---|---|
| `LEGACY_DATA_EPOCH` | `DS001`〜`DS016`（モデリング品質50.0% / 57.79%） | Historical Evidenceとして保持。過去の判定記録は書き換えない |
| `HIGHER_FIDELITY_DATA_EPOCH` | M1/Tick導入後に取得する全データセット | 新規実験のベースラインはこちらで再構築する |

### Epoch切替ルール

- **新Epoch開始後、`EXP-002`等の旧数値を新実験の直接Baselineとして使用しない。**
  モデリング品質が変われば同一EA・同一期間でもSL/TP到達順序が変わり、数値が変わるため
- 旧Epochで得られたEvidenceは「その品質条件下での事実」として保持する。無効化・削除はしない
- 新Epochでの実験は**新しいexperiment_idを採番**する（旧IDを上書きしない、`RESEARCH_RULES.md`第4節）
- 各`DATASET_REGISTRY.md`エントリに`data_epoch`を記録する（本フェーズでの改訂事項）

## Baseline Rebuild Plan

### 必須（最優先）

| 対象 | 新Epochでの扱い | 理由 |
|---|---|---|
| **`EXP-002`相当のBaseline** | **各Validation Foldごとに1本**、新experiment_idで実行 | 全実験の比較基準。これなしでは新Epochで何も判定できない |

### Hypothesis再検証時に必要（優先順位順）

| 順位 | 対象 | 旧experiment_id | 新Epochでの扱い |
|---|---|---|---|
| 1 | H007（Short停止） | なし（未着手） | 最もクリーン。`adaptation_debt=LOW` |
| 2 | H004（NYセッション） | EXP-006 | 新IDで再検証 |
| 3 | H005（建値移動） | EXP-007 | 新IDで再検証。Layer B必須（経路依存のため） |
| 4 | H006（トレンド成熟度） | EXP-008〜010 | 新IDで再検証。`adaptation_debt=HIGH`のためBudget減額 |

### 再実行が不要なもの

| 対象 | 理由 |
|---|---|
| `EXP-001` | CC001旧版。歴史的記録として保持 |
| `EXP-003` | 機能動作確認であり収益性評価ではない |
| `EXP-004` | 旧Epochで未完了のまま凍結。新Epochでは`EXP-002`相当のBaselineで代替 |
| `EXP-005` | 診断目的。ただし方向非対称性は期間依存の可能性が高いため、新Epochでの再確認を**推奨**（必須ではない） |

## 必要なデータ期間

| Layer | 形式 | 目標期間 | 必須/努力目標 |
|---|---|---|---|
| A | USDJPY H1 | 2016〜2026（10年） | 必須（最低5年） |
| B | USDJPY M1 | 可能なら同期間 | 最低でもValidation + Final Holdout期間 |
| B | USDJPY Tick | 10年一括は**必須としない** | Final Holdout・最重要候補・データソース頑健性確認に限定して使用可 |

Tickを全期間必須としない理由: 10年分で概算5〜15GBとなり、容量・実行時間ともに非現実的。
**容量・実行コストとEvidence qualityのトレードオフとして記録する**（本フェーズの判断事項）。

レジーム被覆の想定: 低ボラ(2016-2019) / コロナショック(2020) / 別環境(2021) / 歴史的円安(2022) /
高金利(2023) / 現在に近い環境(2024-2026)。

## 本フェーズ中の凍結事項

Data Expansion Phase完了まで、以下を**停止**する。既存Evidenceは保持する。

- H004の追加実装
- H005のパラメータ探索
- H006の閾値探索（45/60/75等）
- H006の相対化定義の追加探索
- H007の実装
- Market Structure特徴量の追加
- FVG / Order Block / Liquidity
- 新規Entry Filter全般
- Exit最適化

新Data Epoch構築後に、Hypothesis Priorityを再決定する。

## 関連文書

| 文書 | 役割 |
|---|---|
| `governance/DATA_LAYER_SPEC.md` | Layer A/Bの用途と禁止事項 |
| `governance/WALK_FORWARD_AND_HOLDOUT_POLICY.md` | Fold分割原則、overlap扱い、Holdout保護 |
| `HYPOTHESIS_FOLD_BUDGET.md` | Fold消費とadaptation debtの台帳 |
| `governance/DATA_SOURCE_REGISTRY.md` | データソースの必須記録項目（本フェーズで拡張） |
| `diagnostics/DIAGNOSTIC_STUDY_REGISTRY.md` | `DIAG-DATA-001`/`DIAG-DATA-002`の登録先 |

## created_at / updated_at

- created_at: 2026-08-15
- updated_at: 2026-08-15（初版。設計のみ、データ取得・コード変更は未着手）

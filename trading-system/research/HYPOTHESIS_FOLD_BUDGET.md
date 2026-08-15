# Hypothesis Fold Budget

`governance/WALK_FORWARD_AND_HOLDOUT_POLICY.md`に基づく、**Foldの消費と研究者側の適応履歴**を
追跡する台帳。2026-08-15、ユーザー指示により新設。

## 目的（検証回数をゼロにすることではない）

> **目的は「検証回数を減らすこと」ではなく、どれだけデータに適応したかを追跡可能にすることである。**

同じOOS結果を見て仮説・閾値・ロジックを変更すると、そのFoldに対する **adaptive overfitting** が
進行する。これは「1 foldは1回使ったら消滅する」という単純な消費モデルではなく、
**見た回数と、見た後に変更したかどうかの累積**として捉える。

## adaptation_debt（適応債務）

各Hypothesisが「既にどれだけデータに適応してしまっているか」の定性評価。

| 値 | 意味 |
|---|---|
| `LOW` | 実データを見た後のロジック変更がほぼない |
| `MEDIUM` | 1〜2回、結果を見た後に条件や解釈を調整した |
| `HIGH` | 複数回の結果閲覧と、それに基づく仮説・閾値・定義の変更を経ている |

**重要**: `adaptation_debt`は**Data Epochが変わってもリセットされない**。
研究者側が既に結果を見て考えを変えた履歴は、データを入れ替えても消えないためである。

## Budget台帳

| hypothesis_id | Validation Budget | Final Holdout | adaptation_debt | 旧Epochでの消費実績 | 備考 |
|---|---:|---:|---|---|---|
| H004 | 2 | Validation通過時のみ1 | `MEDIUM` | `EXP-006`（1回、decision=HOLD） | `O-002`で7特徴量ファミリー探索の中から選抜された経緯あり |
| H005 | 2 | Validation通過時のみ1 | `MEDIUM` | `EXP-007`（1回、HOLD）、`O-004`（反実仮想分析1回） | Layer B必須（経路依存のため） |
| H006 | **1**（減額） | Validation通過時のみ1 | **`HIGH`** | `EXP-008`(in-sample), `EXP-009`(OOS), `EXP-010`(OOS)、`O-007`（相対化3定義探索） | 下記参照 |
| H007 | 2 | Validation通過時のみ1 | **`LOW`** | なし（未着手） | 最もクリーンな検証が可能 |

### H006のBudget減額理由（正式記録）

H006は`LEGACY_DATA_EPOCH`で既に以下を消費している。

1. `EXP-008`: in-sampleでADOPTED判定
2. `EXP-009`: 第1OOS期間。Primary達成もGuardrail未達でHOLD
3. `EXP-010`: 第2OOS期間。Primary未達でHOLD
4. `O-007`: 相対化指標を3定義探索（結果を見て定義を変えた）

そして**これらの結果を見たことで「50バーという固定閾値の頑健性に疑義がある」という認識が
生まれている**。この認識自体が、データへの適応の産物である。

Data Epochを新しくしても、この適応履歴はリセットされない。したがって:

- Validation Budget を **2 → 1 に減額**
- `adaptation_debt = HIGH` を初期値とする
- 新Epochでの再検証は、**閾値を再探索せず**、既存の`MaxBuyTrendDurationBars=50`のまま
  1回だけ確認する形が望ましい（閾値を動かした時点で適応がさらに進むため）

## 記録項目（実験実施ごとに更新）

各Hypothesisについて、Fold使用のたびに以下を記録する。

| 項目 | 内容 |
|---|---|
| hypothesis_id | 対象仮説 |
| 使用したDiscovery期間 | 仮説生成に使った期間 |
| 使用したValidation Fold | fold識別子と期間 |
| overlap有無 | 他foldと期間が重複しているか（独立試行として数えられるか） |
| 結果を見た後のロジック変更 | **有/無**（有の場合は変更内容も記載） |
| 再利用回数 | 同一foldを何回参照したか |
| 多重検定カウント | そのfoldに対して評価した仮説・条件の総数 |
| Final Holdout使用 | 未使用 / 使用済み / 消費済み（見た後に変更した） |

## 運用ルール

- Budgetを超える検証が必要になった場合、**Budgetを黙って増やさない**。
  超過が必要な理由を記録し、`adaptation_debt`を1段階引き上げた上で実施するか、
  その仮説を保留する
- Final Holdoutは**極力温存する**。Validationを通過していない仮説には使わない
- 複数のHypothesisが同一foldを使う場合、そのfoldに対する多重検定カウントを加算する
  （`MULTIPLE_TESTING_POLICY.md`の母数管理と同じ精神）

## created_at / updated_at

- created_at: 2026-08-15
- updated_at: 2026-08-15（初版。Budget初期値を設定、旧Epochの消費実績を記録）

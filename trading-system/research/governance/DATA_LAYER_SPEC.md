# Data Layer Spec (Layer A / Layer B)

`research/DATA_EXPANSION_PHASE.md`に基づき、価格データを**用途別の2階層**に分離する仕様。
2026-08-15、ユーザー指示により新設。

## なぜ分離するのか（実測に基づく根拠）

現行EAは SL・TP・建値移動など**バー内の価格経路**に結果が左右される。H1 OHLCだけでは
「同一バー内で高値と安値のどちらに先に到達したか」が判別できない。

これは理論上の懸念ではなく、**本プロジェクトで実測済みの事実**である。

> `O-004`（`observations/OBSERVATION_REGISTRY.md`）で`EXP-002`の195トレードに建値移動ルールを
> 反実仮想適用したところ、**28件（14.4%）が`AMBIGUOUS`**となった。これらは同一H1バー内で
> 「+1.0R到達」と「建値への逆戻り」の両方が観測され、H1粒度では順序を決定できなかったケースである。

14.4%が判定不能というのは、PF・期待値の推定に無視できない誤差を与える水準である。

## Layer A: Research / Regime Data

### 用途

- 特徴量計算（EMA、ATR、トレンド継続長、EMA間距離等）
- Regime分析（トレンド/レンジ、高ボラ/低ボラ等の分類）
- Market Structure分析（高値安値更新、スイング構造等）
- 仮説生成
- 年別・相場環境別の記述統計

### 最低要件

| 項目 | 必須 |
|---|---|
| Timestamp | 必須 |
| Open / High / Low / Close | 必須 |
| Volume | 利用可能な場合（ソースにより定義が異なる点に注意） |
| データソース | 必須（`DATA_SOURCE_REGISTRY.md`のsource_id） |
| タイムゾーン | 必須 |
| 欠損情報 | 必須（欠損バー・重複バー・週末バーの有無） |

H1データを使用してよい。

### Layer Aだけから確定してはいけないもの（禁止事項）

以下を Layer A のみを根拠に**正式な数値として確定しない**。

- Profit Factor
- Expectancy R
- Max Drawdown
- SL/TP の到達順序
- BreakEven（建値移動）の効果
- 経路依存の MFE / MAE

Layer Aでこれらを算出すること自体は「参考値」「近似値」として許容するが、
**その旨を必ず明記し、Hypothesis の採否判定の根拠に使わない**
（`DIAG-001` Stage2 のMFE/MAE再構成が、この「参考値」扱いの先例）。

## Layer B: Execution / Backtest Data

### 用途

- 正式な Profit Factor
- 正式な Expectancy R
- Max Drawdown
- SL / TP の判定
- BreakEven の効果測定
- MFE / MAE の経路依存評価
- Execution Path（約定順序）の評価

### 原則

| 優先度 | 形式 | 位置づけ |
|---|---|---|
| 第一候補 | **Tick** | 最も忠実。ただし容量・実行時間のコストが大きい |
| 最低基準候補 | **M1** | Tickが不可能な場合の最低ライン。バー内順序の解像度はTickに劣る |
| 使用不可 | H1のみ | **正式なExecution評価には使用しない** |

### モデリング品質の記録

Layer Bのデータセットには、MT4レポートの**モデリング品質(%)を必ず記録する**。
`LEGACY_DATA_EPOCH`の実績値は50.0%（DS013〜DS016）および57.79%（DS001〜DS012）であり、
これはMT4が上位足から合成ティックを生成している状態を示す。M1導入後にこの値がどう変化するかは
実測するまで不明であり、**推定値を記載しない**。

## 混用の禁止

- Layer A のデータで Layer B の用途を代替しない
- 1つのデータセットが両方の要件を満たす場合（例: M1データは Layer B 要件を満たしつつ
  Layer A 用途にも使える）、`DATASET_REGISTRY.md`の`permitted_uses`に両方を明記する
- 逆に、H1データを Layer B 用途に流用しようとする場合は、
  **`prohibited_uses`に該当するため実施しない**

## created_at / updated_at

- created_at: 2026-08-15
- updated_at: 2026-08-15（初版）

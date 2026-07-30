# Model Registry

`trading-system/RESEARCH_CHARTER.md` 第7節(Layer 4)・第11節に基づくモデル管理表。

## 運用ルール

- 憲章第11節に従い、Price Model / News Model / Interest Rate Model / Liquidity Model /
  Event Model / Regime Model / Ensemble Model は分離して比較できる構成とし、単独の寄与を
  比較可能にする。複数モデルを最初から混在させて登録しない。
- 各モデルの`status`が`ADOPTED`になるまで、実運用の売買判断に使用しない。

## 列定義

| 列 | 説明 |
|---|---|
| model_id | 一意のID |
| model_type | Price / News / Interest Rate / Liquidity / Event / Regime / Ensemble のいずれか |
| model_version | バージョン |
| purpose | 何を予測・判定するモデルか |
| feature_set | 使用する`FEATURE_REGISTRY.md`のfeature_id一覧 |
| target | 予測対象 |
| training_period / validation_period / test_period | データ分割期間 |
| parameters | ハイパーパラメータ等 |
| random_seed | 乱数シード |
| data_version | 使用データの`DATASET_REGISTRY.md`上のバージョン |
| code_commit | 実装のGitコミットSHA |
| metrics | 評価指標の結果 |
| status | DRAFT / READY / RUNNING / COMPLETED / ADOPTED / HOLD / REJECTED / INVALIDATED |
| limitations | このモデルの既知の限界 |

## 初期登録（棚卸し結果、いずれも研究基盤としては未評価）

| model_id | model_type | model_version | purpose | feature_set | target | training_period | validation_period | test_period | parameters | random_seed | data_version | code_commit | metrics | status | limitations |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M001 | Regime + Price (ルールベース) | main, Phase1-4（使用ビルド未確認、Phase5-1の可能性も残る。`EXP-001`の`limitations`参照） | `USDJPY_LowRisk_Trend_EA.mq4`のEMA/ADX/押し目判定によるBUY/SELL/見送り判定 | F001, F002, F004 | 方向 (BUY/SELL/no-signal) | 対象外(パラメータ学習なし) | 2025-07-21〜2026-07-27の70% | 2025-07-21〜2026-07-27の30% | `FastEMAPeriod=20, MiddleEMAPeriod=75, LongEMAPeriod=200, ADXPeriod=14, MinimumADX=20, ATRStopMultiplier=1.5, RewardRiskRatio=2.0`等（`USDJPY_LowRisk_Trend_EA.mq4`入力パラメータ） | 適用外(MQL4ルールベース、乱数なし) | DS001 v1 | main branch時点(想定), `72ac293f71131d53cd027a2786fbfaa2b3bed19d`(CC001) | **[EXP-001実行結果、2026-07-28]** レポート公式値: 総取引数184, 純利益-6128.31, PF 0.74, 期待利得-33.31, 勝率29.89%, 最大DD 7.45%。トレード明細再計算値: PF 0.742, 期待利得-33.808, 勝率29.51%(公式値との乖離あり、`DATASET_REGISTRY.md` DS001参照)。買い134件PF1.02(ほぼ損益分岐) vs 売り49件PF0.305(大幅マイナス)という非対称性を実データで確認 | HOLD（`EXP-001`参照。最低取引数200件未達のため参考外、ADOPTED/REJECTEDの正式判定には至らず） | ウォークフォワード・ベースライン比較（Random Walk/Always WAIT）との定量比較は未実施。使用EAビルドが未確認。単一run・単一期間の結果であり複数期間での再現は未検証 |
| M002 | Price (LSTM) | (バージョン管理なし、`data/`にモデルファイルをgitignoreで保持) | `fx_predict.py`によるUSD/JPY日次終値の将来予測 | (未登録。窓幅`--window`日分の終値系列) | 将来N営業日の終値 | 可変(`--history-range`, 既定2y) | (パイプライン内で明示分割されているか未確認) | (未確認) | `--window`(既定20), `--epochs`(既定40) | (未確認。TensorFlow/Keras既定动作に依存する可能性) | DS003 | (未確認。モデルファイル自体はgitignore対象で追跡されていない) | (未評価。本研究基盤のPF/DD/Direction Accuracy等の指標では未計測) | DRAFT | MT4バックテスト系(M001)とはデータ系統・コスト前提が異なる(スプレッド・スワップ・取引コストを含まない日次終値ベース)。売買判断への接続は現時点でなく、予測結果表示のみ |

## 備考

- 上記いずれも`status = DRAFT`であり、本研究基盤の採用条件（憲章第13節: ウォークフォワード再現、
  ベースライン超過、コスト込み評価等）を満たした実績はまだない。
- M001とM002は目的・データ系統が異なる別モデルであり、統合(Ensemble)は現時点で行っていない
  （行う場合も憲章第11節により単独寄与を比較可能な形で進める）。

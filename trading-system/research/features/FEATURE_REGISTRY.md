# Feature Registry

`trading-system/RESEARCH_CHARTER.md` 第10節に基づく特徴量管理表。

## 運用ルール

- 特徴量は「効くもの」ではなく「検証対象」として管理する。ある特徴量が過去の会話や経験則で
  「効きそう」と言われていたとしても、それだけでは採用理由にならない。
- `leakage_risk`（未来情報混入リスク）は必須記入項目とする。`availability_time`（その特徴量が
  実際に観測可能になる時刻）を明記し、判定時刻より後に確定する情報を使っていないか確認する。
- 特徴量ごとにEvidence/Hypothesisとの対応を記録し、根拠のない特徴量を無断で追加しない
  （憲章第19節: 追加できるのはEvidence/Hypothesis/Experiment/Data Quality Rule/Reproducibility Rule/
  Risk Constraint/実装上必要な技術要件のみ）。

## 列定義

| 列 | 説明 |
|---|---|
| feature_id | 一意のID（例: F001） |
| name | 特徴量名 |
| definition | 何を表す特徴量か |
| formula | 計算式（可能な限り具体的に） |
| source | 元データの出所 |
| availability_time | この特徴量が実際に観測・計算可能になる時刻（例: 当該H1足の確定時刻） |
| timezone | 基準タイムゾーン |
| lookback | 計算に必要な遡り本数・期間 |
| missing_value_rule | 欠損時の扱い（例: WAITを返す、直近値で補完しない 等） |
| leakage_risk | 未来情報混入リスクの有無と理由 |
| evidence_ids | 対応するEvidence ID（あれば） |
| evidence_level | E1-E3 / H / U |
| implementation_version | 実装バージョン・コミットSHA |

## 初期登録候補（検証対象としての登録。採用を意味しない）

登録済みの実装（`trading-system/mt4/USDJPY_LowRisk_Trend_EA.mq4`）で既に計算式が存在する特徴量のみ、
`CURRENT_SYSTEM_AUDIT.md`の棚卸し結果に基づいて「検証対象」として仮登録する。いずれも
`evidence_level = H`（既存実装からの抽出であり、外部Evidenceでの裏付けはまだない）。

| feature_id | name | definition | formula | source | availability_time | timezone | lookback | missing_value_rule | leakage_risk | evidence_ids | evidence_level | implementation_version |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F001 | EMA_FAST/MID/SLOW | 20/75/200期間の指数移動平均によるトレンド方向判定 | `close>slow && fast>mid && mid>slow`で上昇、逆で下降（`USDJPY_LowRisk_Trend_EA.mq4` `GetTrendDirection()`） | USDJPY H1 終値 | 確定足(shift=1)時点 | サーバー時間 | 200本 | 本数不足なら判定スキップ(`HasSufficientHistory()`) | 未確定足(shift=0)を使わない設計のため低い | (未登録) | H | v0.1.0時点の実装(main) |
| F002 | ADX14 | トレンド強度フィルター、MinimumADX(既定20)以上を要求 | `iADX(...,14,...,MODE_MAIN,shift)` | USDJPY H1 | 確定足(shift=1)時点 | サーバー時間 | 14本+ | 本数不足なら判定スキップ | 低い | (未登録) | H | v0.1.0時点の実装(main) |
| F003 | ATR14 (SL/TP用) | ATRベースの損切り・利確幅計算。エントリー可否フィルターとしては未使用 | `iATR(...,14,...,shift) * ATRStopMultiplier` | USDJPY H1 | 確定足(shift=1)時点 | サーバー時間 | 14本+ | 本数不足なら判定スキップ | 低い | (未登録) | H | v0.1.0時点の実装(main) |
| F004 | EMA20押し目/戻り接触判定 | 直近PullbackLookbackBars本以内でEMA20帯への接触・回復を判定 | `BarTouchesEMABand`, `IsRecoveryConfirmed`（`USDJPY_LowRisk_Trend_EA.mq4`） | USDJPY H1 高値/安値/終値 | 確定足(shift=1)時点 | サーバー時間 | 5本(既定) | 接触足なしなら不成立 | 低い | (未登録) | H | v0.1.0時点の実装(main) |

## 未実装・検証段階の特徴量候補（会話内で提案されたのみ、コード未実装）

| feature_id | name | definition | 備考 |
|---|---|---|---|
| F101 | EMA200乖離度(ATR正規化) | 終値とEMA200の距離をATRで正規化した値 | 提案のみ。H001の派生仮説として検証可能。未実装 |
| F102 | ATR比率(現在/N本平均) | ボラティリティが自身の平均に対し高いか低いか | 提案のみ。低ボラ局面の除外仮説。未実装 |
| F103 | セッション/時間帯フラグ | ロンドン/NY/東京等のセッション区分 | EA側に`TradingStartHour`等の入力は存在するが未接続（`CURRENT_SYSTEM_AUDIT.md`参照） |
| F104 | 重要指標までの残り時間 | 次の高インパクト指標までの分数 | H003の実験に必要。経済指標カレンダーデータソース未整備 |

上記F101-F104は特徴量としてまだ実装されておらず、Evidence/Hypothesisとしての裏付けもない
（`evidence_level = U`）。実装前に対応する仮説・実験を`HYPOTHESIS_REGISTRY.md` /
`EXPERIMENT_TEMPLATE.md`側で登録すること。

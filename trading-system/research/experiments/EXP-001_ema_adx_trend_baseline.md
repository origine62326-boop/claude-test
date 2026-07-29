# EXP-001: EMA/ADXベースラインの正式バックテスト検証

`EXPERIMENT_TEMPLATE.md`に基づく実験記録。**本ファイルは実データを見る前に事前登録するものであり、
作成時点(2026-07-28)でtest_period・acceptance_criteria・rejection_criteriaを確定する。**
結果を見た後にこれらを変更する場合は、本ファイルを書き換えず新しいexperiment_id(EXP-002以降)を
発行すること（憲章第18節）。

## 基本情報

| フィールド | 内容 |
|---|---|
| experiment_id | EXP-001 |
| hypothesis_id | H001（EMA20/75/200 + ADXによるUSDJPY H1トレンドフォローの正の期待値仮説） |
| title | EMA/ADXベースラインの正式バックテスト検証 |
| evidence_level | H（検証前の仮説。本実験の結果が良くてもEvidenceへは自動昇格しない、憲章第19節） |
| objective | 現行EA(`trading-system/mt4/USDJPY_LowRisk_Trend_EA.mq4`, main, Phase1-4, CC001)のエントリーロジックが、コスト控除後に正の期待値を持つかどうかを、実際のMT4バックテストデータ（`UNVERIFIED_OBSERVATION`ではない、パイプラインを通した正式なデータ）で検証する |
| rationale | 本セッション内の会話でDS002（スクリーンショット）から確認した参考値はPF 0.74・勝率29.89%と損益分岐点近傍だが、`UNVERIFIED_OBSERVATION`のため正式な判断根拠にできない。`HYPOTHESIS_REGISTRY.md` H001参照 |
| evidence_ids | なし |
| features | F001(EMA_FAST/MID/SLOW), F002(ADX14), F004(EMA20押し目/戻り接触判定) |
| target | 方向判定の結果として生成される個別トレードのR倍数、および集計指標（期待値R, PF, 勝率, 最大DD） |

## ベースライン・比較方法

| フィールド | 内容 |
|---|---|
| baseline | (1) Always WAIT（無取引、損失ゼロ・機会ゼロの基準） (2) Random Walk（EMA/ADX/押し目条件を無視し、トレンド方向判定が満たされた時点でランダムにBUY/SELL/WAITを1/3ずつ割り当てた場合の期待値） |
| comparison_method | 同一データ・同一コスト前提のもとで、CC001のロジックによる集計指標と、上記2ベースラインの集計指標を並べて比較する。ベースライン自体もコード実装が必要な場合はPhase R3〜R4で用意し、それまでは(1)Always WAITとの比較（=単純にPF>1.0かどうか）を最小要件とする |

## データ分割（メソッドを事前登録。具体的な日付はデータ受領後に機械的に適用する）

| フィールド | 内容 |
|---|---|
| train_period | 対象外（本実験はルールベースEAのバックテストであり、パラメータの学習は行わない。EA入力パラメータは`CODE_COMPONENT_REGISTRY.md` CC001記載の既定値を固定して使用する） |
| validation_period | 入手した全期間データのうち、時系列で先頭70% |
| test_period | 入手した全期間データのうち、時系列で末尾30%（**このデータには実験完了までEAの結果を見ない。validation側の分析結果を見てtest_period側の割合・境界を後から動かさない**） |
| walk_forward_definition | 最小構成としてvalidation/testの単純な時系列分割から開始する。データ量が十分であれば、Phase R6でウォークフォワード（例: 6ヶ月学習相当の期間→1ヶ月検証、をローリング）に拡張する。拡張する場合は新experiment_id(EXP-002等)を発行する |

## コスト前提

| フィールド | 内容 |
|---|---|
| transaction_cost_assumption | Rakuten Securities MT4のコミッションは現時点で未確認。バックテストレポートの「総利益・総損失」等がコミッション込みかどうかをレポート受領時に確認し、記載する |
| spread_assumption | バックテストレポートの実測スプレッド値を採用する。DS002スクリーンショットでは「スプレッド(現在値5)」という表示があったが、テスト全期間を通じた実測値ではなく末尾時点の参考値の可能性があるため、正式な値はレポート受領後に確定する。EA自体の`MaxSpreadPips=3.0`はエントリー可否フィルターであり、コストモデルそのものではない点に注意 |
| slippage_assumption | EA入力`Slippage=30`（points）を許容スリッページとして使用しているが、ストラテジーテスターのモデリング品質（`DS002`参考値では57.79%）が低いほど、実際の約定シミュレーション精度は下がる。モデリング品質が明らかに低い場合は`limitations`に明記し、結果の解釈を割り引く |

## パラメータ・再現性情報

| フィールド | 内容 |
|---|---|
| parameters | `CODE_COMPONENT_REGISTRY.md` CC001の既定値を使用: `FastEMAPeriod=20, MiddleEMAPeriod=75, LongEMAPeriod=200, ADXPeriod=14, MinimumADX=20, ATRStopMultiplier=1.5, RewardRiskRatio=2.0, MinStopLossPips=5.0, MaxStopLossPips=100.0, RiskPercent=0.5, MaxSpreadPips=3.0`。実行時に変更した場合はここではなく新experiment_idで記録する |
| random_seed | 対象外（MQL4ルールベース、乱数要素なし） |
| code_version | `72ac293f71131d53cd027a2786fbfaa2b3bed19d`（CC001, main, Phase1-4。`CODE_COMPONENT_REGISTRY.md`参照） |
| data_version | 未確定（`DATASET_REGISTRY.md` DS001。実データ受領後に確定・登録する） |
| execution_date | 未実施（本ファイル作成時点では事前登録のみ） |

## 事前登録した採用条件・棄却条件（結果を見る前に確定）

既存の`trading-system/configs/acceptance_criteria.yaml`（本実験より前から存在し、本実験の結果を見て
決めた数値ではない）をそのまま採用条件の下限として使う。**この数値を本実験の結果を見た後に緩めない。**

| 項目 | 基準（`acceptance_criteria.yaml`より） |
|---|---|
| 最低取引数 | 200件以上 |
| 最低プロフィットファクター | 1.2以上 |
| 最大ドローダウン率 | 15.0%以下 |
| 最低期待値 | 0.0超（マイナス不可） |
| 連敗数の異常上限 | 15連敗以下（これを超える場合は設計上の異常を疑う） |
| 異常検知 | `trade_anomaly_check.py`の結果がクリーンであること |
| 最低リスクリワード比 | 平均勝ち ÷ 平均負けの絶対値が1.5以上 |

上記に加え、憲章第13節の一般原則（コスト込み、ベースライン超過、複数期間での再現、未来データ
リークなし、実装再現性あり）も満たすことを条件とする。**具体的な「複数期間」の下限本数（例: 何年分・
何レジーム分）は、入手できるデータの期間が確定した時点で追記する（現時点でデータ範囲が不明なため
数値を決め打ちできない）。**

`rejection_criteria`: 上記いずれか1つでも不足する場合はADOPTEDにしない。特に最低取引数(200件)を
満たさない場合は「参考外」（憲章第9.3節の分類）として、REJECTEDではなくHOLD扱いとする。

## required_data_sources（憲章第8節）

- USDJPY H1のMT4 Strategy Testerレポート（`.htm`形式、日本語版または英語版）
- 可能であれば操作履歴（トレード明細）の`.htm`もあわせて取得する（フル版パイプライン用、`--trades`オプション）
- 上記が揃わない場合、本実験は`INVALIDATED`のまま`DRAFT`に留め、`UNVERIFIED_OBSERVATION`（DS002等）を
  代用データとして正式な結果には使用しない

## 事前登録チェックリスト

- [x] test_periodを実行前に確定し、結果を見た後に変更していない（分割方法を確定。具体的日付は未確定=未実施のため該当なし）
- [x] acceptance_criteria / rejection_criteriaを実行前に確定している（上表、`acceptance_criteria.yaml`を流用し本実験用に決め打ちしていない）
- [x] train/validation/testの期間が重複しない設計にしている（時系列の70/30分割、trainは対象外）
- [x] 未来データを参照する特徴量が含まれていない（F001/F002/F004はいずれも確定足shift=1基準、`FEATURE_REGISTRY.md`参照）
- [x] transaction_cost / spread / slippageの仮定を（値は未確定だが）取得方法・採用方針として明記している
- [ ] code_version（コミットSHA）とdata_versionを記録する準備ができている（code_versionは記録済み、data_versionは実データ受領後）

## ステータス

- status: `DRAFT`（実データ未受領のため`READY`にはしていない。`.htm`レポートを受領し次第`READY`→`RUNNING`に更新する）
- decision: 未定
- metrics / result: 未定
- limitations: モデリング品質・不整合チャートエラーの水準次第で結果の信頼性が変わる（DS002参考値ではモデリング品質57.79%、不整合チャートエラー2件）。この点は正式レポート受領後に再評価する
- reviewer: 未定（人間の承認者を今後指定）
- created_at: 2026-07-28
- updated_at: 2026-07-28

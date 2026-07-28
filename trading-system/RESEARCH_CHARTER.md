# FX Research Platform 憲章 (RESEARCH_CHARTER)

## この文書の位置づけ

- 本文書は `trading-system/` 配下におけるFX市場研究基盤の**最上位仕様**である。
- `trading-system/` 配下の下位仕様・実装（EA、分析パイプライン、設定ファイル、READMEなど）は、
  本文書の原則と矛盾してはならない。矛盾が見つかった場合は、下位仕様側を修正するか、
  本文書の改訂を提案すること。
- 本文書の変更には、**変更理由・差分・承認**が必要である。理由なく内容を書き換えてはならない。
- 本文書は2026-07-28、ユーザーの指示に基づき初版として作成された（`claude/fx-research-platform-foundation-v0.1.0`ブランチ）。

以下は、ユーザーから提示された最上位仕様の全文である。

---

# FX Research Platform 最上位仕様

## 1. プロジェクトの目的

本プロジェクトの目的は、
「勝てる売買AI」を作ることではない。

FX市場に存在する可能性のある優位性を、
再現可能な方法で検証し、
継続的に改善できる研究基盤を構築する。

利益を保証するシステムではなく、

- 事実
- 仮説
- 検証結果

を明確に分離したシステムを構築する。

## 2. 最重要原則

Claude Codeおよび本プロジェクトは、以下を守る。

1. 推測して仕様を作らない
2. 根拠がないものは仮説として扱う
3. 未来情報を使用しない
4. テストデータを見て最適化しない
5. すべて再現可能であること
6. データ不足ならWAITを返す
7. 根拠を必ず保存する
8. 実装前にEvidenceレベルを付与する

## 3. Evidenceの定義

Evidenceとは、信頼できる情報源によって支持される内容。

例:

- BIS
- FRB
- ECB
- 日本銀行
- CFTC
- 査読論文
- 市場仕様
- 公式API仕様
- 公式ブローカー仕様
- MQL4公式ドキュメント

Evidenceには必ず一意のIDを付ける。

例:

E001
BIS FX Market Structure

E002
FRB Exchange Rate Forecasting

E003
ECB Market Microstructure

## 4. Evidenceレベル

E1:
複数の査読研究、公的機関、公式仕様等で支持される

E2:
一定の研究または一次資料で支持される

E3:
実務・市場で使われるが、条件依存または根拠が限定的

H:
検証前の仮説

U:
根拠不足または分類不能

Evidenceレベルは、
「正しいことの保証」ではなく、
現時点における根拠の強さを表す。

## 5. Hypothesis

仮説は自由に追加してよい。

ただし、採用判定されるまで
実運用の売買判断へ使用してはいけない。

例:

H001:
ロンドン時間のモメンタム

H002:
重要指標発表後の押し目

H003:
ATRが一定以上の局面でEMA戦略の期待値が改善する

H004:
経済指標前後の新規エントリー停止で損失分布が改善する

現在検討中の経済指標フィルターは、
最初から有効な機能として扱わず、
H004の検証対象として登録すること。

## 6. 仮説・実験管理

各仮説または実験について、最低限以下を保存する。

- experiment_id
- hypothesis_id
- title
- evidence_level
- objective
- rationale
- evidence_ids
- features
- target
- baseline
- comparison_method
- train_period
- validation_period
- test_period
- walk_forward_definition
- transaction_cost_assumption
- spread_assumption
- slippage_assumption
- parameters
- random_seed
- code_version
- data_version
- execution_date
- metrics
- result
- decision
- status
- acceptance_reason
- rejection_reason
- limitations
- reviewer
- created_at
- updated_at

status候補:

- DRAFT
- READY
- RUNNING
- COMPLETED
- ADOPTED
- HOLD
- REJECTED
- INVALIDATED

## 7. システム構成

Layer 1: Data Acquisition

- 価格
- 経済指標
- ニュース
- 金利
- 出来高またはTick Volume
- スプレッド
- 取引コスト
- 市場カレンダー
- 祝日

Layer 2: Data Quality

- 欠損
- 重複
- 異常値
- タイムゾーン
- 時刻順序
- 未来データ混入
- API停止
- データ鮮度
- シンボル差異
- ブローカー差異

Layer 3: Feature Engineering

- 価格
- リターン
- ボラティリティ
- モメンタム
- トレンド
- 流動性
- スプレッド
- マクロ
- 時間帯
- 曜日
- 祝日
- イベント

Layer 4: Research Models

- ベースライン
- ルールベース仮説
- 統計モデル
- 機械学習モデル
- 統合モデル

Layer 5: Validation

- バックテスト
- 時系列分割
- ウォークフォワード
- アウト・オブ・サンプル
- コスト込み評価
- 統計検定
- 頑健性検証
- 感度分析
- モンテカルロ
- データスヌーピング対策

Layer 6: Reporting / Decision

- BUY
- SELL
- WAIT
- 期待値
- 信頼区間
- 予測確率
- 根拠
- 使用モデル
- 使用仮説
- データ品質状態
- リスク制約状態

## 8. データ品質ルール

以下の場合は、原則としてDecision EngineはWAITを返す。

- 必須価格データ欠損
- 必須ニュースデータ欠損
- 必須経済指標データ欠損
- API停止
- タイムスタンプ異常
- 未来データ混入
- スプレッド取得失敗
- 重要指標時間不明
- 必要期間のデータ不足
- データ期限切れ
- データバージョン不明
- モデルバージョン不明
- 特徴量計算失敗
- リスク判定不能

ただし、
すべての研究でニュースデータが必須とは限らない。

各実験ごとに
required_data_sources
を定義し、その実験で必須とされたデータが欠けた場合にWAITまたは実験無効とすること。

## 9. ベースライン

最低限、以下と比較する。

- Random Walk
- Always WAIT
- Buy and Hold相当の参考値
- 単純Momentum
- 単純Mean Reversion
- Logistic Regression
- LightGBM

注意:

Always WAITは収益ベースラインというより、
「無理に取引しない場合の損失ゼロ・機会ゼロ」
を示す運用上の基準として扱う。

各ベースラインの定義は固定し、
実験ごとに都合よく変更しない。

## 10. 特徴量

候補:

- 価格リターン
- ATR
- ADX
- EMA
- RSI
- MACD
- 実現ボラティリティ
- Tick数
- Spread
- 金利
- 金利差
- ニュース
- 経済指標
- 時間帯
- 曜日
- Holiday
- イベント
- 過去のギャップ
- セッション
- ロールオーバー時間帯

特徴量は「効くもの」ではなく
「検証対象」として管理する。

各特徴量には以下を記録する。

- feature_id
- name
- definition
- formula
- source
- availability_time
- timezone
- lookback
- missing_value_rule
- leakage_risk
- evidence_ids
- evidence_level
- implementation_version

## 11. モデル

以下を分離して比較できる構成にする。

- Price Model
- News Model
- Interest Rate Model
- Liquidity Model
- Event Model
- Regime Model
- Ensemble / Integrated Model

モデル同士を直接混在させず、
各モデル単独の寄与を比較可能にする。

## 12. 評価指標

最低限:

予測評価:
- Direction Accuracy
- Balanced Accuracy
- Brier Score
- Log Loss
- Calibration
- Precision
- Recall
- Coverage
- WAIT率

取引評価:
- Expectancy
- Net Profit
- Profit Factor
- Sharpe Ratio
- Sortino Ratio
- Maximum Drawdown
- Calmar Ratio
- Win Rate
- Average Win
- Average Loss
- Payoff Ratio
- Trade Count
- Turnover
- Cost Impact
- Slippage Impact

評価指標は1つだけで採用判断しない。

## 13. 採用条件

バックテストだけでは採用しない。

最低限、以下を満たすこと。

- 時系列外データでも期待値がプラス
- 手数料・スプレッド・スリッページ込み
- ウォークフォワードで再現
- ベースラインを上回る
- 複数期間で再現
- 特定の1期間に依存しない
- 過学習の兆候が許容範囲
- 未来データリークなし
- 実装再現性あり
- データとコードのバージョン固定
- 最低取引件数を満たす
- リスク制約内
- テスト前に採用条件が定義済み

具体的な数値基準は、
証拠なく決め打ちせず、
研究目的・運用条件ごとに事前登録する。

## 14. 棄却条件

- コスト込みで期待値が負
- 特定期間だけ勝つ
- 未来データを使用
- データリークあり
- 過学習
- 再現不能
- 統計的・経済的に意味がない
- ベースラインを安定して上回らない
- 感度が高すぎる
- 少数取引の偶然に依存
- データ品質が不十分
- 検証手順が事前登録されていない
- テストデータを見た後に条件変更された

「統計的有意性がない」だけで即棄却せず、
検出力不足・取引数不足・効果量も併せて確認する。

## 15. Risk Engine

Signal Engineと完全分離する。

Risk Engineが管理するもの:

- 最大日次損失
- 1取引リスク
- ロット
- 同時保有数
- 緊急停止
- 連続損失
- 最大ドローダウン
- スプレッド上限
- 発注制約
- 口座制約
- 稼働時間制約
- データ品質エラー時停止

Risk Engineは
Signalの方向予測を変更してはいけない。

Risk Engineの出力例:

- ALLOW
- REDUCE
- BLOCK
- EMERGENCY_STOP

SignalがBUYでも、
Risk EngineがBLOCKなら最終判断はWAITとする。

## 16. Decision Engine

出力:

- BUY
- SELL
- WAIT

補助出力:

- confidence
- expected_value
- lower_confidence_bound
- upper_confidence_bound
- signal_model_id
- hypothesis_ids
- evidence_ids
- data_quality_status
- risk_status
- reason_codes
- generated_at

WAITは正常な判断である。

無理にエントリーしない。

BUYまたはSELLを出す場合も、
必ず根拠・データ品質・リスク状態を添付する。

## 17. Logging

最低限以下を保存する。

- 入力データ
- 入力データバージョン
- 特徴量
- 特徴量バージョン
- 予測
- モデル
- モデルバージョン
- Evidence
- Hypothesis
- 期待値
- 不確実性
- Decision
- Risk Decision
- 注文結果
- 決済結果
- 実現損益
- スプレッド
- スリッページ
- エラー
- WAIT理由
- 実行時刻
- コードコミットSHA

ログは追記型とし、
後から都合よく改変しない。

個人情報・口座情報・認証情報は保存しない。

## 18. Research Loop

新しい仮説追加
↓
事前登録
↓
データ品質確認
↓
バックテスト
↓
ウォークフォワード
↓
統計評価
↓
頑健性評価
↓
採用・保留・棄却
↓
Evidence更新
↓
フォワードテスト

テスト結果を見た後に仮説を変更する場合は、
既存実験を書き換えず、
新しいexperiment_idを発行する。

## 19. Claude Codeへのルール

Claude Codeは、

「勝てそうだから」
「一般的によく使われるから」
「精度が上がりそうだから」

という理由だけで機能・ルール・特徴量を追加してはいけない。

追加できるのは以下のみ。

- Evidence
- Hypothesis
- Experiment
- Data Quality Rule
- Reproducibility Rule
- Risk Constraint
- 実装上必要な技術要件

Evidenceには必ず出典を付ける。

Hypothesisには必ず検証計画を付ける。

根拠が見つからない場合はUまたはHとして登録する。

EvidenceとHypothesisを混同しない。

実験結果が良かったことを、
Evidenceレベルの自動昇格理由にしない。

## 20. 最終目的

このシステムは、
FX市場を研究するための研究プラットフォームである。

目的:

- 市場を理解する
- 仮説を検証する
- 期待値を測定する
- 再現性を確認する
- 不確実性を保存する
- 採用しない判断を可能にする

利益は、その結果として得られる可能性があるものであり、
設計段階で保証するものではない。

---

## 既知の内部矛盾（初版作成時点でのメモ）

本憲章の第5節は「例」としてH001〜H004（ロンドン時間モメンタム／指標後押し目／ATR局面でのEMA戦略／
経済指標前後の停止）を挙げ、経済指標前後停止を「H004」として登録するよう指示している。一方、
`research/hypotheses/HYPOTHESIS_REGISTRY.md` の初期登録指示ではEMA/ADXトレンドフォロー・日次損失/連敗制限・
経済指標前後停止の3件をH001〜H003として登録するよう明示されており、経済指標前後停止のIDが両者で
一致しない（憲章側=H004、レジストリ側=H003）。

本文書は「全文をそのまま保存する」という指示に基づき、内容を書き換えずに保存している。実際の登録は
`HYPOTHESIS_REGISTRY.md` の明示的な初期登録指示（H001〜H003）を優先して行った。ID体系の整合は
今後の改訂（変更理由・差分・承認を伴う）で解消することを推奨する。詳細は
`research/audits/GAP_ANALYSIS.md` を参照。

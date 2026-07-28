# Hypothesis Registry

`trading-system/RESEARCH_CHARTER.md` 第5節に基づく、仮説（Hypothesis）の一覧管理表。

## 運用ルール

- 仮説は自由に追加してよい。ただし**採用判定（ADOPTED）されるまで実運用の売買判断へ使用してはいけない**。
- EvidenceとHypothesisを混同しない。実データ・実験なしに「効きそう」という理由だけでHypothesisを
  Evidenceへ昇格させない。
- 各Hypothesisは、対応する`EXPERIMENT_TEMPLATE.md`ベースの実験（experiment_id）で検証する。
- テスト結果を見た後に仮説内容を書き換える場合、既存行は書き換えず、新しいhypothesis_idまたは
  新しいexperiment_idを発行する（憲章第18節）。

## ID体系に関する既知の注意事項

`RESEARCH_CHARTER.md`第5節の「例」ではH001〜H004として別内容（ロンドン時間モメンタム等）が例示され、
経済指標前後停止は「H004」として言及されている。一方、本レジストリの初期登録指示ではH001〜H003として
下記3件を登録するよう明示されているため、経済指標前後停止のIDが両者で一致しない
（憲章の例=H004、本レジストリ=H003）。本レジストリは実際の初期登録指示を優先して採番した。
詳細は`research/audits/GAP_ANALYSIS.md`を参照。今後ID体系を統一する場合は、既存行のIDを書き換えず、
統一版として新しいIDを発行すること。

## 初期登録（DRAFT）

| hypothesis_id | title | description | rationale | evidence_ids | evidence_level | required_data | proposed_features | target | baseline | validation_method | acceptance_criteria | rejection_criteria | status | related_experiments |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H001 | EMA20/75/200 + ADXによるUSDJPY H1トレンドフォローの正の期待値仮説 | EMA20>EMA75>EMA200（またはその逆）でトレンド方向を判定し、ADXでトレンド強度を確認したうえでの押し目買い・戻り売りエントリーに、コスト控除後の正の期待値が存在する可能性を検証する | 現行`USDJPY_LowRisk_Trend_EA.mq4`（v0.1.0, Phase1-4）が採用しているエントリーロジックそのもの。過去のバックテスト（本セッション内の会話で確認: PF 0.74、勝率29.89%、R:R理論値2.0に対し実現1.75）では損益分岐点近傍〜やや下回る結果であり、正の期待値の有無は未確定 | (未登録。会話内での経験的観測のみで、E1-E3のEvidenceには未到達) | H | USDJPY H1 OHLC, スプレッド, スワップ | EMA20/75/200, ADX14, 押し目/戻り接触判定 | 方向 (BUY/SELL/WAIT) と期待値R | Random Walk, Always WAIT | ウォークフォワード + アウトオブサンプル、コスト込み | (未確定。事前登録が必要。憲章第13節により数値基準を証拠なく決め打ちしない) | (未確定。事前登録が必要) | DRAFT | (なし) |
| H002 | 日次損失上限・連敗制限による損失分布・最大DD改善仮説 | 最大日次損失上限とMaxConsecutiveLossesによる当日エントリー停止が、リターン(期待値)そのものを改善しなくても、損失分布の裾（テールリスク）や最大ドローダウンを改善する可能性を検証する | Phase 5-1として`claude/ea-v0.3.0-risk-management`ブランチ（本ブランチの基点であるmainには未マージ）に実装済み。資金管理側の変更であり、エントリー精度（勝率・PF）そのものの改善は意図していない | (未登録) | H | 日次決済履歴, 連敗カウント, 口座残高推移 | daily_pnl, consecutive_loss_count | 最大DD, 損失分布(テール), PF | 制限なしの同一シグナルロジック | 同一シグナルでの制限あり/なし比較 | (未確定。事前登録が必要) | (未確定。事前登録が必要) | DRAFT | (なし) |
| H003 | 重要経済指標前後の新規エントリー停止によるPF/最大DD改善仮説 | 重要指標（米雇用統計・CPI・FOMC・政策金利・GDP・中央銀行総裁会見等）の前後一定時間、新規エントリーを停止することで、コスト控除後PFまたは最大DDが改善する可能性を検証する。現時点では未実装のアイデア段階であり、最初から有効な機能として扱わない | 会話内で「経済指標前後は取引停止」として改善案の一つに挙がったが、MQL4に標準経済指標カレンダーAPIがなく、バックテスト用の指標時刻データの整備が別途必要という制約が判明している | (未登録) | H | 経済指標カレンダー(過去分, ポイントインタイム), 重要度分類 | minutes_to_next_high_impact_event | PF, 最大DD | 指標フィルターなしの同一シグナルロジック | 同一シグナルでのフィルターあり/なし比較 | (未確定。事前登録が必要) | (未確定。事前登録が必要) | DRAFT | (なし) |

## status候補（憲章第6節）

DRAFT / READY / RUNNING / COMPLETED / ADOPTED / HOLD / REJECTED / INVALIDATED

## 備考

- 上記3件はいずれも`evidence_level = H`（検証前の仮説）であり、Evidence（E1-E3）ではない。
- `acceptance_criteria` / `rejection_criteria`列を「未確定」としているのは、根拠なく数値基準を
  決め打ちしないという憲章第13節の原則による。各仮説を実験化する際に、`EXPERIMENT_TEMPLATE.md`側で
  実験ごとに事前登録すること。
- H003（本レジストリの採番）は、これまでの会話で提案された「ADXが弱い相場で見送る」「EMA200乖離で見送る」
  「ATRが低すぎるレンジで見送る」「利確・損切り倍率の最適化」等、他の改善案と同様に、現時点では
  検証されていない仮説であり、Evidenceではない。今後追加する場合はH004以降として登録すること。

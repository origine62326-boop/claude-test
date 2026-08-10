# Hypothesis Registry

`trading-system/RESEARCH_CHARTER.md` 第5節に基づく、仮説（Hypothesis）の一覧管理表。

## 運用ルール

- 仮説は自由に追加してよい。ただし**採用判定（ADOPTED）されるまで実運用の売買判断へ使用してはいけない**。
- EvidenceとHypothesisを混同しない。実データ・実験なしに「効きそう」という理由だけでHypothesisを
  Evidenceへ昇格させない。
- 各Hypothesisは、対応する`EXPERIMENT_TEMPLATE.md`ベースの実験（experiment_id）で検証する。
- テスト結果を見た後に仮説内容を書き換える場合、既存行は書き換えず、新しいhypothesis_idまたは
  新しいexperiment_idを発行する（憲章第18節）。

## ID体系に関する注意事項（2026-07-28 解消済み）

初版では`RESEARCH_CHARTER.md`第5節の例がH001〜H004という具体的IDで示され、経済指標前後停止を
「H004」として言及していたため、本レジストリのH003（経済指標前後停止）と参照先が一致しない状態
だった。PR #8のレビュー指摘を受け、`RESEARCH_CHARTER.md`第5節を改訂し、経済指標前後停止の参照を
H003に統一した（詳細は`RESEARCH_CHARTER.md`の改訂履歴、`research/audits/GAP_ANALYSIS.md`参照）。
本レジストリのH001〜H003のID自体は変更していない。

## 初期登録（DRAFT）

| hypothesis_id | title | description | rationale | evidence_ids | evidence_level | required_data | proposed_features | target | baseline | validation_method | acceptance_criteria | rejection_criteria | status | related_experiments |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H001 | EMA20/75/200 + ADXによるUSDJPY H1トレンドフォローの正の期待値仮説 | EMA20>EMA75>EMA200（またはその逆）でトレンド方向を判定し、ADXでトレンド強度を確認したうえでの押し目買い・戻り売りエントリーに、コスト控除後の正の期待値が存在する可能性を検証する | 現行`USDJPY_LowRisk_Trend_EA.mq4`（v0.1.0, Phase1-4）が採用しているエントリーロジックそのもの。**[2026-07-28更新] EXP-001でDS001(実MT4データ、184件)を用いて検証した結果、PF0.74・期待利得-33.31（レポート公式値）で、`acceptance_criteria.yaml`の最低取引数200件・最低PF1.2・最低期待値0超のいずれも未達。買い側(134件, PF1.02)はほぼ損益分岐だが、売り側(49件, PF0.305)が純損失の大半を占めるという非対称性を確認** | (未登録。E1-E3のEvidenceには未到達) | H | USDJPY H1 OHLC, スプレッド, スワップ | EMA20/75/200, ADX14, 押し目/戻り接触判定 | 方向 (BUY/SELL/WAIT) と期待値R | Random Walk, Always WAIT | ウォークフォワード + アウトオブサンプル、コスト込み | `EXP-001`にて事前登録済み（`configs/acceptance_criteria.yaml`を流用、本実験用の決め打ちなし） | `EXP-001`にて事前登録済み | HOLD（EXP-001の結果、サンプル数不足のため参考外） | EXP-001 (COMPLETED, decision=HOLD), EXP-005 (COMPLETED, decision=ADOPTED〔実験単体の診断結論〕。方向別分離診断の結果、Run B〔売りのみ〕がEXP-002売りサブセットとトレード単位まで完全一致、Run A〔買いのみ〕も+1トレードのみの差にとどまり、方向非対称性はポジション枠競合ではなく方向固有の信号品質差であると判定) |
| H002 | 日次損失上限・連敗制限によるテールリスク・稼働継続性改善仮説 | 最大日次損失上限とMaxConsecutiveLossesによる当日エントリー停止が、**純利益や期待値そのものの改善を前提とせず**、最大ドローダウン・損失分布の裾（Tail Loss）・最悪連敗の悪化抑制・異常時の稼働停止率・機会損失とのトレードオフを改善する可能性を検証する。**評価は必ず「純利益/PFが上がるか」ではなく、下記targetの各指標で行うこと** | [IMPLEMENTED_ON_UNMERGED_BRANCH] Phase 5-1として`claude/ea-v0.3.0-risk-management`ブランチ（本ブランチの基点であるmainには未マージ。merge_status等の詳細は`RISK_ENGINE_SPEC.md`, `trading-system/configs/risk_limits.yaml`参照）に実装済み。資金管理側の変更であり、エントリー精度（勝率・PF・純利益）そのものの改善は意図していない。**[2026-07-29更新] EXP-002で実バックテスト実行済み(DS004)。最大DD・PF・純損益はEXP-001(Baseline)と同等〜わずかに改善、最大連敗は変化なし(8のまま)。[2026-07-31更新] Expertsログ解析により、連敗制限機能はVERIFIED（2回発動: 2026-05-14 17:00, 2026-06-17 19:00。いずれも翌日正常再開）。日次損失上限機能は本バックテスト期間中0回発動でNOT_TRIGGERED。[2026-07-31更新] `EXP-003`（非標準パラメータMaxDailyLossPercent=0.3/MaxConsecutiveLosses=20による専用機能試験、DS005）を実行し、日次損失上限機能もVERIFIED（14回発動、全て正常な停止・翌日再開・連敗制限との非干渉を確認）。Phase5-1の2機能（連敗制限・日次損失上限）はいずれも機能としてはVERIFIED済みだが、これは「コードが意図通り動く」ことの確認であり、H002本来の主要評価対象（既定値パラメータでの最大DD・Tail Loss・最悪連敗の悪化抑制効果）はEXP-002（既定値実行）の結果に基づく。H002全体のADOPTED/HOLD/REJECTED最終判定はPrimary/Secondary/Guardrail Metricsの総合判断が必要で未実施** | (未登録) | H | 日次決済履歴, 連敗カウント, 口座残高推移 | daily_pnl, consecutive_loss_count | **主要評価対象（純利益改善は前提としない）**: 最大ドローダウン(Max DD), 損失分布(左裾/Tail Loss), 最悪連敗(Worst Consecutive Losses), 稼働停止率(制限発動によりエントリー機会が失われた日数の割合), 機会損失(制限がなければ得られたはずの利益の逸失、参考指標として併記) | EXP-001（旧版Baseline、制限なしのシグナルロジック） | 同一シグナルでの制限あり/なし比較 | `EXP-002`にてPrimary/Secondary/Guardrail区分を事前登録済み（具体的閾値は実データ受領後に確定。「純利益改善」を採用基準にしないことは確定事項） | `EXP-002`にて事前登録済み | HOLD（連敗制限機能・日次損失上限機能とも機能としてはVERIFIED（`EXP-002`, `EXP-003`）。ただしH002本来の評価対象であるPrimary/Secondary/Guardrail Metricsに基づく最終判定はまだ実施していない。既存status語彙にPARTIALLY_VERIFIED相当の値がないため、最も近い`HOLD`を使用し本注記で内実を補足） | EXP-002 (COMPLETED, decision=HOLD), EXP-003 (COMPLETED, decision=ADOPTED〔実験単体の合格判定、H002全体の採用可否とは別〕), EXP-004 (READY、CC001確定ビルドによるEXP-002比較用Baseline取得、事前登録済み・MT4実行待ち) |
| H003 | 重要経済指標前後の新規エントリー停止によるPF/最大DD改善仮説 | 重要指標（米雇用統計・CPI・FOMC・政策金利・GDP・中央銀行総裁会見等）の前後一定時間、新規エントリーを停止することで、コスト控除後PFまたは最大DDが改善する可能性を検証する。現時点では未実装のアイデア段階であり、最初から有効な機能として扱わない。**実験化する際は、実験開始前にPrimary Metric・Secondary Metrics・Guardrail Metricsを定義し`EXPERIMENT_TEMPLATE.md`側に事前登録すること**（例: Primary=PFまたは期待値R、Secondary=最大DD・取引回数・稼働停止率、Guardrail=最低取引件数・最大DD悪化なし等。具体的な値は証拠なく決め打ちせず実験ごとに確定する） | 会話内で「経済指標前後は取引停止」として改善案の一つに挙がったが、MQL4に標準経済指標カレンダーAPIがなく、バックテスト用の指標時刻データの整備が別途必要という制約が判明している | (未登録) | H | 経済指標カレンダー(過去分, ポイントインタイム), 重要度分類 | minutes_to_next_high_impact_event | PF, 最大DD (Primary/Secondary/Guardrailの区別は実験登録時に確定) | 指標フィルターなしの同一シグナルロジック | 同一シグナルでのフィルターあり/なし比較 | (未確定。事前登録が必要。Primary/Secondary/Guardrail Metricsの定義を含む) | (未確定。事前登録が必要) | DRAFT | (なし) |
| H004 | NY時間帯(セッション)新規エントリー除外による買い方向期待値改善仮説 | H1の買いエントリーのうち、サーバー時間15:00-22:00（本レジストリでの暫定区分「NYセッション」）に発生したものを新規エントリーから除外することで、コスト控除後PFまたは期待値Rが改善する可能性を検証する。**`O-002`のObservationに基づく提案であり、まだ実験化されていない。EAコード・パラメータは変更していない** | `O-002`（`research/observations/OBSERVATION_REGISTRY.md`）で、DS001+DS004(378トレード)を方向別に条件付けたセッション分析を実施した結果、買いのみで見てもNYセッション(n=85)がPF0.695・期待値R -0.227と唯一マイナス期待値のセッションであり、Asia(n=89, PF1.290)・London(n=81, PF1.369)は明確にプラスだった。この差は方向（Long/Short）で条件付けても残存し、DS001・DS004（近い構成の2データセット）双方で同方向・近い数値を示した。一方、同様に検討したATR四分位・EMA傾き符号は方向との強い交絡が判明し独立効果と言えず、不採用とした。曜日効果（月曜が最良、水曜が最悪）も方向調整後に残るが、FX研究における曜日効果は多重検定・過学習の典型的な罠として知られるため、本レジストリでは優先度をセッションより下げた。**本仮説は、探索的に7つの特徴量ファミリーを検証した中から選ばれた1件であり、多重検定リスクがある点を明記する（`MULTIPLE_TESTING_POLICY.md`参照、母数=7）** | O-002 | H | USDJPY H1 OHLC, entry_time（セッション区分算出用） | session_at_entry（Asia/London/NY/LateNY_AsiaOpenの4区分、サーバー時間ベース） | PF, 期待値R（買い方向のみを対象。売り方向はH004の対象に含めない、非対称性は別仮説の領域） | H001の現行シグナルロジック（セッションフィルターなし、買いのみ） | 同一シグナル・同一期間で、NYセッションのエントリーを除外した場合と除外しない場合を比較 | (未確定。証拠なく決め打ちせず、実験登録時にPrimary=期待値R、Secondary=PF・取引回数、Guardrail=最低取引件数等を事前登録する) | (未確定。事前登録が必要) | DRAFT（**まだ実験化されていない。実験化にはPrimary/Secondary/Guardrail Metricsの事前登録と、既存H001データの事後的な条件選択にならないよう、可能であればOOS〔別期間データ〕での検証が望ましい**） | (なし。実験化する場合は新規experiment_idを発行する) |

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

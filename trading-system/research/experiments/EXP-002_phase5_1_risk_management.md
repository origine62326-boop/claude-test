# EXP-002: Phase5-1(日次損失上限・連敗制限)リスク管理効果の検証

`EXPERIMENT_TEMPLATE.md`に基づく実験記録。**本ファイルは実際のPhase5-1版バックテストデータを見る前に
事前登録するものであり、作成時点(2026-07-29)でtest_period・比較項目・acceptance_criteria・
rejection_criteriaを確定する。** 結果を見た後にこれらを変更する場合は、本ファイルを書き換えず
新しいexperiment_id(EXP-003以降)を発行すること（憲章第18節）。

**現時点では実バックテストデータは存在しない。バックテストの実行はユーザーがMT4上で行い、
結果の`.htm`レポート（レポート・操作履歴・可能であればExpertsログ）を受領した後に、
本ファイルの`metrics`以降を追記する。それまでは`status = READY`のまま実行を待つ。**

## 基本情報

| フィールド | 内容 |
|---|---|
| experiment_id | EXP-002 |
| hypothesis_id | H002（日次損失上限・連敗制限によるテールリスク・稼働継続性改善仮説） |
| title | Phase5-1(日次損失上限・連敗制限)リスク管理効果の検証 |
| evidence_level | H（検証前の仮説。本実験の結果が良くてもEvidenceへは自動昇格しない、憲章第19節） |
| objective | Phase5-1（`claude/ea-v0.3.0-risk-management`ブランチ, CC002）を適用したEAで、EXP-001（旧版Baseline）と同一条件のバックテストを実行し、日次損失上限・連敗制限が損益・リスク指標に与える影響を測定する。**純利益・PFの改善を目的とした実験ではない**（`HYPOTHESIS_REGISTRY.md` H002の前提を踏襲） |
| rationale | Phase5-1は現状mainに未マージ（`IMPLEMENTED_ON_UNMERGED_BRANCH`、`RISK_ENGINE_SPEC.md`参照）。マージ判断（`RESEARCH_PLATFORM_ROADMAP.md` Phase R1ステップ3）の材料として、実際のバックテストによる効果測定が必要（`MERGE_CHECKLIST.md`のBacktest Run A/Run B項目に対応）。EXP-001はサンプル数不足でHOLDだが、Phase5-1が損益そのものを変える設計ではないため、EXP-001の集計値を参照点として使うことができる |
| evidence_ids | なし |
| features | F001(EMA_FAST/MID/SLOW), F002(ADX14), F004(EMA20押し目/戻り接触判定) ＋ Phase5-1固有: daily_pnl, consecutive_loss_count（`HYPOTHESIS_REGISTRY.md` H002のproposed_features） |
| target | 下記「比較項目」参照 |

## 比較項目（ユーザー指定、事前登録）

EXP-001（旧版Baseline）とEXP-002（Phase5-1版）を、以下9項目で比較する。**「純利益が改善したか」を
主要な採用基準にはしない**（H002の前提、`HYPOTHESIS_REGISTRY.md`参照）。

| # | 比較項目 | EXP-001(Baseline)の値 | データ取得元 | 備考 |
|---|---|---|---|---|
| 1 | 純損益 | -6128.31（公式）/ -6186.90（再計算） | レポート/トレード明細（既存パイプラインで取得可能） | Phase5-1は理論上これを変えない設計（エントリー条件不変）。大きく変化していれば要調査 |
| 2 | プロフィットファクター(PF) | 0.74 / 0.742 | 同上 | 同上 |
| 3 | 最大ドローダウン | 7.45%(7495.84) | レポート | H002のPrimary Metric。Baseline以下(悪化しない)であることを期待 |
| 4 | 最大連敗 | 8 | レポート/トレード明細 | H002のSecondary Metric |
| 5 | 日次最大損失 | **未算出**（既存パイプラインに日次損益集計機能がない） | トレード明細のclose_time+profitから日次集計が必要 | **要対応**: `analysis/period_analysis.py`等に日次集計を追加するか、簡易スクリプトで別途算出するかは実データ受領後に判断する。本実験の登録時点では未実装のまま、必要性のみ記録する |
| 6 | 取引数 | 184（うち183決済、1未決済） | レポート | 日次損失上限・連敗制限が発動していれば、Baselineより取引数が減るはず |
| 7 | 停止発動回数 | 対象外(Phase1-4にはこの機能がない) | **Expertsログが必要**（レポート/トレード明細には含まれない） | `IsDailyLossLimitReached()`/`IsMaxConsecutiveLossesReached()`のログ出力回数をカウント。要ログ提供 |
| 8 | 停止後の再開挙動 | 対象外 | **Expertsログが必要** | 日付変更後に正しくエントリー再開しているか（`TEST_PLAN_PHASE5-1.md` #7, #8参照）。ログでの確認が前提、レポート集計だけでは判定不能 |
| 9 | 買い/売り別結果 | 買い134件PF1.02・売り49件PF0.305（`direction_analysis.py`） | レポート/トレード明細 | Baselineの非対称性がPhase5-1後も残るか、変化するかを確認 |

## ベースライン・比較方法

| フィールド | 内容 |
|---|---|
| baseline | EXP-001（旧版Baseline。上表参照） |
| comparison_method | 同一データ・同一期間・同一エントリーパラメータのもとでPhase5-1版のバックテストを実行し、上記9項目をEXP-001の値と並べて比較する。差分の解釈は、Phase5-1が「エントリー条件を変えず、新規エントリーの停止条件のみ追加する」設計であることを前提に行う（`RISK_ENGINE_SPEC.md`参照）。日次損失上限・連敗制限が一度も発動しなければ、理論上は項目1・2・3・4・6・9はEXP-001と同一になるはずであり、そうならない場合は実装差異かデータ条件の不一致を疑う |

## データ分割

| フィールド | 内容 |
|---|---|
| train_period | 対象外（EXP-001と同様、ルールベースEAのバックテストでありパラメータ学習は行わない） |
| validation_period | EXP-001と同一の期間・分割方法を踏襲する（後述「旧版と同じバックテスト条件の再構成」参照） |
| test_period | EXP-001と同一（末尾30%相当）。**EXP-001同様、結果を見た後に境界を動かさない** |
| walk_forward_definition | EXP-001と同一方針（最小構成の時系列分割。ウォークフォワード拡張はPhase R6で別experiment_idにて） |

## コスト前提

EXP-001と同一の前提を踏襲する（`transaction_cost_assumption` / `spread_assumption` /
`slippage_assumption`いずれもEXP-001の記載を参照）。EXP-001自体がこれらを正確な数値として
確定できていないため、EXP-002でも同水準の不確実性を引き継ぐ。**新たに推測で数値を埋めない。**

## 旧版と同じバックテスト条件の再構成（不明な条件はUNKNOWN/要ユーザー確認とする）

`DATASET_REGISTRY.md` DS001（EXP-001で使用した実データ）から判明している条件を転記し、
不明な条件はUNKNOWNまたは「要ユーザー確認」と明記する。**推測で埋めない。**

| 条件 | EXP-001(Baseline)での値 | EXP-002で使うべき値 |
|---|---|---|
| 通貨ペア | USDJPY | 同一（USDJPY） |
| 時間足 | H1 | 同一（H1） |
| テスト期間(開始) | 2025-07-21（実際の初回エントリーは2025-07-23 11:00） | 同一。**要ユーザー確認**: MT4ストラテジーテスターの「期間」欄をEXP-001と同じ日付に設定すること |
| テスト期間(終了) | 2026-07-27（実際の最終エントリーは2026-07-24 11:00、1件未決済） | 同一。上記と同様に設定を確認 |
| 初期証拠金 | 100,000 | 同一（100,000） |
| モデル(ティックモデリング) | 全ティック | 同一（全ティック）。**UNKNOWN**: モデリング品質が57.79%からどの程度変わるかは、テスターのヒストリーデータ状態に依存するため予測不可 |
| スプレッド設定 | 「現在値(5)」と表示。テスト全期間で固定だったか、代表値表示に過ぎないかは**UNKNOWN**（`DATASET_REGISTRY.md` DS001参照） | **要ユーザー確認**: EXP-001実行時と同じスプレッド設定（固定値か、カレントスプレッドモードか）を使うこと。設定を変更した場合は必ず記録する |
| ブローカー/口座 | RakutenSecurities-Demo, Build 1475 | 同一口座での実行を推奨（ブローカーが変わるとスプレッド・約定モデルが変わり、比較の前提が崩れる） |
| 使用EAビルド | **UNKNOWN**（CC001かCC002か未確認、EXP-001の`limitations`参照） | **CC002固定**（`claude/ea-v0.3.0-risk-management`ブランチのEA、`MaxDailyLossPercent`/`MaxConsecutiveLosses`を含む版）。EXP-001と違い、ここは確定させる |
| EAパラメータ(共通部分) | `CODE_COMPONENT_REGISTRY.md` CC001の既定値を想定（`FastEMAPeriod=20, MiddleEMAPeriod=75, LongEMAPeriod=200, ADXPeriod=14, MinimumADX=20, ATRStopMultiplier=1.5, RewardRiskRatio=2.0, MinStopLossPips=5.0, MaxStopLossPips=100.0, RiskPercent=0.5, MaxSpreadPips=3.0`）ただし実際にこの値が使われたかは未確認 | 上記と同一の値を使用することを推奨（EXP-001が本当にこの値を使っていたかは不明なため、ここでの「同一」は「CC002の既定値をそのまま使う」という意味に留まる） |
| EAパラメータ(Phase5-1固有) | 対象外 | `configs/risk_limits.yaml`記載の既定値を使用: `MaxDailyLossPercent=2.0`, `MaxConsecutiveLosses=3`。変更した場合は必ず記録する |
| ログ出力設定 | (対象外、レポートのみ使用) | **重要**: 比較項目7・8（停止発動回数・再開挙動）にはExpertsログが必須。バックテスト実行時にExpertsタブのログを保存し、`.htm`レポートと一緒に提供すること |

## パラメータ・再現性情報

| フィールド | 内容 |
|---|---|
| parameters | 上表「旧版と同じバックテスト条件の再構成」を参照。CC002の既定値 + `MaxDailyLossPercent=2.0, MaxConsecutiveLosses=3` |
| random_seed | 対象外（MQL4ルールベース、乱数要素なし） |
| code_version | `13fc725a6a6e96fe2dd13af3970e88eeee821d73`（CC002, `claude/ea-v0.3.0-risk-management`ブランチ, Phase5-1。`CODE_COMPONENT_REGISTRY.md`参照）。**EXP-001と異なりここは確定情報**（本実験はPhase5-1版で実行することが目的そのものであるため） |
| data_version | 未確定（新規バックテスト実施後に`DATASET_REGISTRY.md`へDS004等として登録する） |
| execution_date | 未実施（本ファイル作成時点では事前登録のみ） |

## 事前登録した採用条件・棄却条件（Primary / Secondary / Guardrail Metrics）

H002は「純利益・PFの改善」を採用基準にしないことが確定事項（`HYPOTHESIS_REGISTRY.md`参照）。
そのため、具体的な数値基準はPhase5-1の実バックテストデータが無い現時点では決め打ちできない
（憲章第13節「証拠なく決め打ちしない」）。以下はPrimary/Secondary/Guardrailの**区分と方向性**を
事前登録するものであり、具体的な閾値は実データ受領後、結果を見る前に別途確定する。

| 区分 | 指標 | 期待する方向性 |
|---|---|---|
| Primary Metric | 最大ドローダウン | EXP-001(Baseline)以下（悪化しない） |
| Secondary Metrics | 最大連敗、日次最大損失、停止発動回数 | 連敗・日次損失がBaselineより抑制されていること。停止発動回数は0でも「発動しなかった」という結果として意味を持つ |
| Guardrail Metrics | 純損益、PF、取引数 | Baselineから大きく悪化していないこと（大きな悪化は資金管理ロジックのバグを疑うシグナルとして扱う。「純利益が改善したか」はGuardrailであって採用基準ではない） |

`rejection_criteria`: 停止後の再開挙動（比較項目8）がExpertsログで確認できず、`TEST_PLAN_PHASE5-1.md`
の該当項目（#7, #8等）を満たせない場合、本実験は`HOLD`とし、ログ再取得まで正式な判定を保留する。
最大DDがBaselineより悪化した場合、Primary Metric未達として`REJECTED`ではなく`HOLD`とし、原因調査を
優先する（棄却ではなく、まず実装の問題かデータの問題かを切り分ける）。

## required_data_sources（憲章第8節）

- USDJPY H1のMT4 Strategy Testerレポート（`.htm`形式）— CC002(Phase5-1)を適用した状態で実行
- 操作履歴（トレード明細）の`.htm`（フル版パイプライン用）
- **Expertsログ（ジャーナル/エキスパートタブの出力）** — 比較項目7(停止発動回数)・8(停止後の再開挙動)に必須。
  これが無い場合、この2項目は`UNKNOWN`のまま`HOLD`とする
- 上記が揃わない場合、本実験は`READY`のまま`RUNNING`に進めない

## 事前登録チェックリスト

- [x] test_periodを実行前に確定し、EXP-001と同一の期間・分割方法を踏襲することを明記している
- [x] acceptance_criteria / rejection_criteriaの区分(Primary/Secondary/Guardrail)を事前登録している（具体的閾値はデータ受領後、結果を見る前に確定）
- [x] train/validation/testの期間が重複しない設計を踏襲している
- [x] 未来データを参照する特徴量が含まれていない（EXP-001と同一のF001/F002/F004、追加のdaily_pnl/consecutive_loss_countも当日確定分のみ使用しEA側の設計に準拠）
- [x] transaction_cost / spread / slippageの仮定を（値は未確定だが）EXP-001と同一方針で引き継ぐことを明記している
- [x] code_version（コミットSHA）を記録済み（CC002のSHAを確定。data_versionは実データ受領後）
- [ ] Expertsログの取得方法・保存方法をユーザーと合意している（未実施、次のやり取りで確認）

## [2026-07-29] 実行前の試行に関する記録

ユーザーによる初回実行(`EXP-002_run001`のファイル名で最初に共有されたレポート)は、MT4の
スプレッド設定がEXP-001実行時と異なっていたため（現在値41ポイント=4.1pips、`MaxSpreadPips=3`を
常時超過）、総取引数0件という結果になった。このデータは正式なDatasetとして登録せず、比較にも
使用していない。ユーザーがスプレッド設定を修正して再実行した結果（本節以下）を正式なEXP-002の
結果として採用する。

## データ（DS004として登録）

| フィールド | 内容 |
|---|---|
| データソース | `trading-system/reports/raw/EXP-002_run001_report.htm`（gitignore対象） |
| checksum | sha256:`db6bd5f27e378696a8a994ca1fcb6fe5789d44c9d2f42bcd64407586f03d592f` |
| 実際に使用されたパラメータ（レポートに埋め込み記載、実測） | `MagicNumber=20260714; RiskPercent=0.5; MaximumLot=1; MaxDailyLossPercent=2; MaxConsecutiveLosses=3; FastEMAPeriod=20; MiddleEMAPeriod=75; LongEMAPeriod=200; ATRPeriod=14; ATRStopMultiplier=1.5; RewardRiskRatio=2; MinStopLossPips=5; MaxStopLossPips=100; ADXPeriod=14; MinimumADX=20; PullbackLookbackBars=5; PullbackTolerancePips=3; MaxPullbackPenetrationPips=10; RequireSignalCandleDirection=false; MaxSpreadPips=3; Slippage=30` 等。**この実行はレポート自体にパラメータが埋め込まれており、EXP-001と違って実際の使用値が確定情報である**（EXP-001の`limitations`にあった「使用パラメータ未確認」という限界は本実行には該当しない） |
| スプレッド | 現在値(5) — EXP-001と一致（0.5pips相当） |
| テスト期間 | 2025.07.21 01:00 - 2026.07.24 23:00（2025-07-21〜2026-07-27設定）— EXP-001と一致 |
| モデリング品質 / 不整合チャートエラー | 57.79% / 2件 — EXP-001と一致（同一ヒストリーデータであることの傍証） |

## EXP-001とEXP-002の比較結果

| # | 比較項目 | EXP-001(Baseline) | EXP-002(Phase5-1) | 差分・所見 |
|---|---|---|---|---|
| 1 | 純損益 | -6128.31(公式)/-6186.90(再計算) | -6126.05(公式)/-6184.64(再計算) | ほぼ同一（公式値差+2.26） |
| 2 | PF | 0.74(公式)/0.742(再計算) | 0.76(公式)/0.762(再計算) | わずかに改善（+0.02） |
| 3 | 最大ドローダウン | 7.45%(7495.84) | 7.45%(7493.58) | ほぼ同一（-2.26、悪化なし。Primary Metric: 達成） |
| 4 | 最大連敗 | 8 | 8 | 変化なし（下記「解釈」参照） |
| 5 | 日次最大損失 | 未算出 | 未算出 | 比較不可（既存パイプラインに算出機能がなく未実装のまま。今回も算出していない） |
| 6 | 取引数 | 184（183決済+1未決済） | 196（195決済+1未決済） | **+12件増加**（下記「解釈」参照） |
| 7 | 停止発動回数 | 対象外 | **UNKNOWN** | Expertsログが今回提供されていないため判定不能 |
| 8 | 停止後の再開挙動 | 対象外 | **UNKNOWN** | 同上 |
| 9 | 買い/売り別 | 買い134件 +286.75 PF1.02 34.33% / 売り49件 -6473.65 PF0.305 16.33% | 買い141件 +923.73 PF1.059 34.04% / 売り54件 -7108.37 PF0.313 16.67% | 非対称構造（売りが弱い）は維持。買い側はやや改善 |

### 解釈（事実に基づく考察、断定はしない）

- **最大連敗が8のまま変わらなかった点**: `MaxConsecutiveLosses=3`が有効なはずだが、EA実装は
  「当日限定でカウント、日付が変わるとリセット」という設計（`RISK_ENGINE_SPEC.md`参照）。8連敗が
  複数の営業日にまたがって発生していた場合、1日のうちに3連敗に到達しないまま日をまたいでカウントが
  リセットされ続け、制限が一度も発動しない、という可能性がある。Expertsログがあれば検証できるが、
  今回は確認できていない
- **取引数が184→196に増加した点**: Phase5-1はエントリー条件自体を変更しない設計だが、日次損失上限や
  連敗制限が発動して新規エントリーを一時的に止めた場合、その間ポジションを持たない状態が続くため、
  Baselineでは発生しなかった別のシグナルを新たに拾える可能性がある（逆に、Baselineで取ったトレードが
  Phase5-1では制限中で取れず、値動きの経路が変わってその後のシグナル自体が変化する可能性もある）。
  どちらの機序が働いたかは、Expertsログでの発動履歴確認が必要
- **PF・純損益・最大DDはほぼ同一〜わずかに改善**: 大きな悪化は見られず、Guardrail Metricsは通過している

## 事前登録した採用条件との照合

| 区分 | 指標 | 判定 |
|---|---|---|
| Primary Metric | 最大DD | 達成（Baseline同等、悪化なし） |
| Secondary Metrics | 最大連敗、日次最大損失、停止発動回数 | 最大連敗=変化なし。日次最大損失=未算出。停止発動回数=UNKNOWN |
| Guardrail Metrics | 純損益、PF、取引数 | 純損益・PFは悪化なし。取引数は+12件（悪化ではないが未説明の変化） |

`rejection_criteria`に定めた通り、比較項目8（停止後の再開挙動）がExpertsログで確認できないため、
**本実験はHOLDとし、ログ再取得まで正式な判定を保留する。**

## decision

**HOLD**（Expertsログ未提供のため、事前登録した`rejection_criteria`に従い正式なADOPTED/REJECTED
判定に進めない。数値指標自体はBaselineから大きな悪化なし〜わずかに改善だが、H002が本来検証したい
「制限が実際に機能したか」を示す発動回数・再開挙動の確認ができていないため、Phase5-1の効果を
実証したとは言えない）

## status

`COMPLETED`（バックテスト実行・数値比較は完了。Expertsログ待ちのためHOLDのまま）

## limitations

- **Expertsログ未提供**: 比較項目7・8が確認できず、H002の本質的な検証（制限が実際に機能したか）が
  未完了のまま
- **取引数の増加(184→196)の機序が未解明**: 上記「解釈」参照。Expertsログがあれば発動タイミングと
  突き合わせて説明できる可能性がある
- **EXP-001（Baseline）自体が使用EAビルド未確認**: 本比較が厳密な「同一ビルド+リスク管理追加のみ」の
  比較になっているかは、EXP-001側の限界を引き継いだまま
- **レポート公式値とトレード明細再計算値の小さな乖離が今回も再現**: 期待利得で公式-31.26 vs
  再計算-31.716。EXP-001と同様の未解明の乖離（`DATASET_REGISTRY.md` DS001の既知の問題と同種）
- **日次最大損失（比較項目5）は引き続き未算出**: パイプラインへの追加実装が必要（未着手）
- サンプル数（195〜196件）はEXP-001同様200件を下回っており、H002についても単独では
  「参考外」（憲章第9.3節）の水準にとどまる

## reviewer

未定（人間の承認者を今後指定）

## created_at / updated_at

- created_at: 2026-07-29
- updated_at: 2026-07-29（実データでの実行・比較結果を反映）

# EXP-004: Phase1-4(CC001)確定ビルドによる、EXP-002と完全同一条件でのBaseline再取得

`EXPERIMENT_TEMPLATE.md`に基づく実験記録。**本ファイルは実際のバックテストデータを見る前の事前登録
である。ユーザーが`BACKTEST_COVERAGE_EXPANSION_PLAN.md`の優先2として承認したことを受けて発行する
（2026-07-31）。結果を見た後にtest_period・比較項目・acceptance_criteriaを変更する場合は、本ファイルを
書き換えず新しい`experiment_id`(EXP-005以降)を発行する。**

## 位置づけ・目的（1実験1目的）

**唯一の変更点はEAビルド（CC001 ↔ CC002）のみ**。それ以外の条件（期間・パラメータ・スプレッド・
初期証拠金・モデル）は`EXP-002`と完全に同一にする。

- `EXP-001`（H001向けのBaseline）は使用EAビルド（CC001かCC002か）が未確認という限界を持つため
  （`EXP-001`の`limitations`参照）、`EXP-002`との比較が厳密な「同一データ・同一パラメータでビルドの
  みが異なる」A/B比較になっていなかった（`BACKTEST_COVERAGE_EXPANSION_PLAN.md`優先2参照）
- 本実験は、**ビルドをCC001（main, Phase1-4, リスク管理ロジック未実装）に確定**した上で、`EXP-002`
  （CC002, Phase5-1）と完全同一条件で再実行し、Phase5-1のリスク管理ロジック追加による純粋な差分を
  測定可能にする
- 副次的に、本実験は`EXP-001`の「使用EAビルド未確認」という限界を解消する新しいCC001確定データにも
  なる（H001側の参考データとしても扱えるが、H001自体の採用可否判定は`EXP-001`のacceptance_criteriaを
  流用せず本実験では行わない。目的が異なるため、H001の判定は引き続き`EXP-001`のHOLDのまま据え置く）

## 基本情報

| フィールド | 内容 |
|---|---|
| experiment_id | EXP-004 |
| hypothesis_id | H002（日次損失上限・連敗制限によるテールリスク・稼働継続性改善仮説。`EXP-002`のBaseline側データを確定させるための実験） |
| title | Phase1-4(CC001)確定ビルドによる、EXP-002と完全同一条件でのBaseline再取得 |
| evidence_level | H（検証前） |
| objective | CC001（`main`, Phase1-4, リスク管理ロジック未実装）を、`EXP-002`と完全同一の期間・パラメータ・スプレッド・初期証拠金・モデルで実行し、`EXP-002`(CC002)との厳密なA/B比較を可能にするBaselineデータを得る |
| rationale | `EXP-001`は使用ビルド未確認のため、`EXP-002`との比較には「ビルド差か、それとも他の条件差か」を切り分けられないという限界があった。本実験でビルドをCC001に確定することでこの限界を解消する |
| evidence_ids | なし |
| features | F001(EMA_FAST/MID/SLOW), F002(ADX14), F004(EMA20押し目/戻り接触判定)。CC001は`MaxDailyLossPercent`/`MaxConsecutiveLosses`を入力パラメータとして持つが、**エントリー可否判定には未接続**（後述「CC001固有の注意点」参照） |
| target | `EXP-002`との比較（下記「比較項目」参照） |

## CC001固有の注意点（実行前に必ず確認）

`trading-system/mt4/USDJPY_LowRisk_Trend_EA.mq4`（現在の`main`, CC001, commit
`72ac293f71131d53cd027a2786fbfaa2b3bed19d`）を確認したところ、**CC001にも`MaxDailyLossPercent`・
`MaxConsecutiveLosses`という入力パラメータ自体は存在する**（`OnInit`での値検証のみ実施）。ただし
`IsDailyLossLimitReached()`・`IsMaxConsecutiveLossesReached()`に相当する関数はCC001のコードに
存在せず、`TryEnter()`相当のエントリー判定からも一切参照されていない。**つまりCC001ではこの2つの
入力値は妥当性チェックのみ行われる「宣言されているが機能に接続されていない」パラメータであり、
値を何に設定してもエントリー挙動には影響しない。** これは`RISK_ENGINE_SPEC.md`が既に記録している
「main時点ではリスク管理ロジック未実装」という事実と一致する（今回、実際のコードを再確認して
裏付けを取った）。

よって、本実験でも`MaxDailyLossPercent=2.0`・`MaxConsecutiveLosses=3`（`EXP-002`実測値と同じ既定値）
に設定することを推奨するが、これらの値自体はCC001の挙動に影響しないため、仮に異なる値を設定して
しまっても本実験の結果には影響しない（ただし記録の一貫性のため、指定通りに設定すること）。

## 比較項目（`EXP-002`と同一の9項目を踏襲）

`EXP-002`が`EXP-001`に対して用いた9項目の比較を、今度は**厳密な同一条件下**で再実施する。

| # | 比較項目 | 備考 |
|---|---|---|
| 1 | 純損益 | `EXP-002`(CC002)の値と比較 |
| 2 | プロフィットファクター(PF) | 同上 |
| 3 | 最大ドローダウン | 同上。H002のPrimary Metric |
| 4 | 最大連敗 | 同上。H002のSecondary Metric |
| 5 | 日次最大損失 | 既存パイプラインに日次損益集計機能がないため今回も未算出（`EXP-002`と同じ既知の制約） |
| 6 | 取引数 | 同上 |
| 7 | 停止発動回数 | CC001は該当なし（機能未接続のため常に0回・対象外） |
| 8 | 停止後の再開挙動 | CC001は該当なし（同上） |
| 9 | 買い/売り別成績 | 同上。`EXP-001`/`EXP-002`で確認された非対称性が、ビルド確定後も再現するかを確認 |

## ベースライン・比較方法

| フィールド | 内容 |
|---|---|
| baseline | `EXP-002`（Phase5-1版, CC002, DS004）。比較の基準を`EXP-001`からEXP-002本体へ切り替える点が`EXP-002`とは異なる（`EXP-002`は`EXP-001`をBaselineとしたが、本実験は逆にCC001側を新規取得しCC002=`EXP-002`と比較する） |
| comparison_method | 同一データ期間・同一EAパラメータ・同一スプレッドのもとでCC001を実行し、上記9項目を`EXP-002`の値と並べて比較する。変更点はEAビルド（CC001↔CC002）のみに限定する |

## データ分割

| フィールド | 内容 |
|---|---|
| train_period | 対象外（ルールベースEA、パラメータ学習なし） |
| validation_period | `EXP-002`と同一の期間・分割方法を踏襲する |
| test_period | `EXP-002`と同一（末尾30%相当）。結果を見た後に境界を動かさない |
| walk_forward_definition | `EXP-002`と同一方針（最小構成の時系列分割） |

## コスト前提

`EXP-002`と完全に同一の前提を踏襲する（`transaction_cost_assumption` / `spread_assumption` /
`slippage_assumption`いずれも`EXP-002`の記載を参照）。

## 検証用設定（確定、`EXP-002`と同一条件）

| 設定 | 値 |
|---|---|
| 使用EAビルド | **CC001**（`main`ブランチ、commit `72ac293f71131d53cd027a2786fbfaa2b3bed19d`）。`EXP-002`/`EXP-003`で使用したCC002（`claude/ea-v0.3.0-risk-management`）とは別ブランチのファイルに切り替える必要がある |
| `MaxDailyLossPercent` | 2.0（`EXP-002`実測値と同じ既定値。CC001では機能に未接続のため実質無効、上記「CC001固有の注意点」参照） |
| `MaxConsecutiveLosses` | 3（同上） |
| その他EAパラメータ | `EXP-002`と同一（`FastEMAPeriod=20, MiddleEMAPeriod=75, LongEMAPeriod=200, ADXPeriod=14, MinimumADX=20, ATRStopMultiplier=1.5, RewardRiskRatio=2.0, MinStopLossPips=5.0, MaxStopLossPips=100.0, RiskPercent=0.5, MaxSpreadPips=3.0, Slippage=30`等） |
| 通貨ペア | USDJPY |
| 時間足 | H1 |
| モデル | 全ティック |
| 初期証拠金 | 100,000 |
| ブローカー環境 | RakutenSecurities-Demo |
| スプレッド | 現在値(5) |
| 期間 | `EXP-002`と同一期間（2025-07-21〜2026-07-27） |

## acceptance_criteria / rejection_criteria

本実験自体は「ADOPTED/REJECTEDされる仮説検証」ではなく、**H002のBaseline側データを確定させるための
基礎データ収集**である。そのため`decision`欄には憲章第13-14節の採用/棄却条件を機械的に適用せず、
以下の基準で評価する。

- 期間・パラメータ・スプレッド等がすべて`EXP-002`と一致していることをレポート埋め込みパラメータで
  確認できれば、本実験は`COMPLETED`とする（`REPRODUCIBLE`の考え方を流用）
- 一致しない項目があれば、その差異を明記した上で`HOLD`とし、再実行が必要かどうかを判断する
- 本実験の数値自体は、`HYPOTHESIS_REGISTRY.md` H002のPrimary/Secondary/Guardrail Metricsに、
  `EXP-002`との比較値として供給する（H002全体のADOPTED/HOLD/REJECTED最終判定は本ファイルでは行わない）

## required_data_sources（憲章第8節）

- USDJPY H1のMT4 Strategy Testerレポート（`.htm`形式） — 必須
- Expertsログ — **任意**（CC001はリスク管理ロジック未接続のため、停止発動回数・再開挙動の確認は
  そもそも不要。ただしエラー・異常終了の有無を確認する目的で提供されれば参考にする）
- 実際に使用したパラメータ一覧（レポート埋め込み） — 必須
- EA Commit SHA（CC001固定、`72ac293f71131d53cd027a2786fbfaa2b3bed19d`） — 必須
- コンパイル確認（0 errors / 0 warningsかどうか） — 必須
- 操作履歴`.htm` — 任意（本MT4環境では保存不可と確認済み、`EXP-003`と同じ制約）

## パラメータ・再現性情報

| フィールド | 内容 |
|---|---|
| parameters | 上表「検証用設定」参照 |
| random_seed | 対象外 |
| code_version | `72ac293f71131d53cd027a2786fbfaa2b3bed19d`（CC001, `main`, Phase1-4） |
| data_version | 未確定（新規バックテスト実施後に`DATASET_REGISTRY.md`へDS006等として登録する） |
| execution_date | 未実施 |

## 事前登録チェックリスト

- [x] test_periodを実行前に確定している（`EXP-002`と同一期間）
- [x] acceptance_criteria / rejection_criteriaを事前登録している（基礎データ収集としての基準）
- [x] 未来データを参照する特徴量が含まれていない（`EXP-001`/`EXP-002`と同一のエントリーロジック）
- [x] transaction_cost / spread / slippageの仮定を`EXP-002`と同一方針で引き継ぐことを明記している
- [x] code_version（コミットSHA）を記録済み。data_versionは実データ受領後
- [x] 使用するEAビルド（CC001）と、その入力パラメータの実際の機能的意味（`MaxDailyLossPercent`等が
  未接続であること）を事前に確認している

## status

`READY`（事前登録完了。ユーザーによるMT4実行・データ提供待ち）

## limitations（事前に予期される限界）

- CC001の`MaxDailyLossPercent`/`MaxConsecutiveLosses`入力は機能に未接続のため、比較項目7・8は
  そもそも「対象外」であり、`EXP-003`のような機能試験の対象にはならない
- 本実験は`EXP-002`との比較のみを目的とし、H001自体の採用可否判定（`EXP-001`の役割）を代替しない
- レポート公式値とトレード明細再計算値の乖離（`EXP-001`/`EXP-002`で確認済みの既知の問題）が
  本実験でも再現する可能性がある。操作履歴`.htm`が取得できない場合はクロスチェック自体ができない

## ユーザーが次にMT4で行う操作

1. **EAビルドの切り替え**: MetaEditorで開いている`USDJPY_LowRisk_Trend_EA.mq4`を、`main`ブランチの
   版（commit `72ac293f71131d53cd027a2786fbfaa2b3bed19d`。`EXP-003`まで使用していた
   `claude/ea-v0.3.0-risk-management`版とは別のファイル）に差し替える
2. コンパイルし、**0 errors / 0 warnings**を確認する
3. **ストラテジーテスターの設定**（`EXP-002`と同一）:
   - 通貨ペア: USDJPY / 時間足: H1 / モデル: 全ティック
   - 期間: 2025.07.21 〜 2026.07.27
   - 初期証拠金: 100,000 / スプレッド: 現在値(5)
4. **入力パラメータ**（`EXP-002`と同一の既定値。CC001では`MaxDailyLossPercent`/`MaxConsecutiveLosses`
   は機能に影響しないが、記録の一貫性のため指定通りに設定）:
   - `MaxDailyLossPercent = 2.0`
   - `MaxConsecutiveLosses = 3`
   - その他は`EXP-002`実行時と同じ値（`FastEMAPeriod=20`等、上表「検証用設定」参照）
5. バックテストを実行
6. 「結果」タブをレポート`.htm`として保存
7. 上記レポート`.htm`をこのチャットにアップロードする（Expertsログ・操作履歴は任意）

## reviewer

未定（人間の承認者を今後指定）

## created_at / updated_at

- created_at: 2026-07-31
- updated_at: 2026-07-31（事前登録。ユーザーが`BACKTEST_COVERAGE_EXPANSION_PLAN.md`優先2を承認したことを受けて発行）

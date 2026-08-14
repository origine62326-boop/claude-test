# EXP-006: NYセッション(15:00-22:00)除外による買い方向期待値改善検証

`EXPERIMENT_TEMPLATE.md`に基づく実験記録。**H004（`HYPOTHESIS_REGISTRY.md`）の事前登録実験。
ユーザーが2026-08-11、H004の実験登録を承認したことを受けて発行する。本ファイル作成時点では
EAコードは一切変更していない（後述「実装の要否」参照、実行には別途承認が必要）。**

**[2026-08-14追記（訂正ではなく追記。上記は登録時点の事実として残す）]** ユーザーが
「実行する」と明示的に承認（`RESEARCH_RULES.md`第13節の半自動PDCAループに基づく）。
これを受けて`IsWithinTradingHours()`の実装を完了した。詳細は下記「実装ログ」参照。
**MT4でのコンパイル・バックテスト実行はまだユーザー側で未実施**（本サンドボックスに
MQL4コンパイラがないため、コンパイル確認・実行結果の受領を待って本ファイルをさらに更新する）。

## 基本情報

| フィールド | 内容 |
|---|---|
| experiment_id | EXP-006 |
| hypothesis_id | H004（NY時間帯新規エントリー除外による買い方向期待値改善仮説） |
| title | NYセッション(15:00-22:00)除外による買い方向期待値改善検証 |
| evidence_level | H（検証前） |
| objective | サーバー時間15:00-22:00（NYセッション）の新規エントリーを除外した場合、買い方向の期待値R・PFが改善するかを、実バックテストで検証する |
| rationale | `O-002`（`OBSERVATION_REGISTRY.md`）で、DS001+DS004(378トレード)を方向別に条件付けたセッション分析を行い、買いのみでもNYセッション(n=85)がPF0.695・期待値R -0.227と唯一マイナス期待値のセッションであることを確認した。ただしこれは**既存トレードを事後的に絞り込んだ観察**であり、実際にNYセッションで新規エントリーを止めた場合に、それ以降の値動きへの追従経路が変わる可能性がある（`EXP-002`/`EXP-003`で確認済みの経路依存効果と同じ論点）。実際にフィルターを実装したバックテストでの検証が必要 |
| evidence_ids | なし |
| features | F001(EMA_FAST/MID/SLOW), F002(ADX14), F004(EMA20押し目/戻り接触判定)。エントリー条件自体は変更しない。新規: `trading_hours_filter`（下記「実装の要否」参照） |
| target | 下記「acceptance_criteria」参照 |

## 重要な注意（H004との違い）

`O-002`のObservationは**買いのみ**を対象にしていたが、EAの`TradingStartHour`/`TradingEndHour`
入力パラメータ（下記「実装の要否」参照）は方向を区別しない設計になっている。買い方向のみに
時間帯フィルターを適用する実装は、既存パラメータの意味を超える追加変更になり「最小変更」の
原則から外れるため、**本実験では買い・売り両方にフィルターを適用する**（フィルター自体は
方向非依存、売り方向への影響は副次的な観察として記録するに留め、H004の主結論はあくまで
買い方向のデータで判断する）。

## 実装の要否（重要、実行前に承認が必要）

EA (`trading-system/mt4/USDJPY_LowRisk_Trend_EA.mq4`) には`TradingStartHour`/`TradingStartMinute`/
`TradingEndHour`/`TradingEndMinute`という入力パラメータが**既に存在する**が、CC001・CC002いずれも
コード内コメント「取引時間フィルター (Phase 7で機能実装予定。現状は入力値検証のみ)」の通り、
**`OnInit`での値検証のみで、`TryEnter()`には一切接続されていない**（実在確認済み、
`RISK_ENGINE_SPEC.md`の既存記載と一致）。

したがって、**本実験を実行するには、この既存パラメータを`TryEnter()`の新規エントリー判定に
接続する、EAコードの変更が必要**。想定する最小限の変更:

- `IsWithinTradingHours()`という新規関数を追加し、現在サーバー時刻が
  `TradingStartHour:TradingStartMinute`〜`TradingEndHour:TradingEndMinute`の範囲内かを判定する
  （開始>終了の場合は日をまたぐ範囲として扱う。例: 開始22:00・終了15:00なら「22:00〜翌15:00」が
  許可範囲）
- `TryEnter()`の先頭付近（既存の`IsSpreadAcceptable()`チェックと同様の位置）に
  `if(!IsWithinTradingHours()) { ログ出力; return; }`を追加
- `MaxDailyLossPercent`/`MaxConsecutiveLosses`と同様、既存の未接続パラメータを接続するのみで、
  新しい入力パラメータは追加しない
- H004検証用の設定値: `TradingStartHour=22, TradingStartMinute=0, TradingEndHour=15,
  TradingEndMinute=0`（22:00〜翌15:00を許可=NY(15:00-22:00)を除外）

**本ファイルの事前登録時点では、このコード変更は実施していない。実装するにはユーザーの
別途明示的な承認が必要（`RESEARCH_RULES.md`第11節、EAコード変更を伴うため）。実装する場合、
既存のブランチ運用（main=CC001, `claude/ea-v0.3.0-risk-management`=CC002）を踏まえ、
新規ブランチ（例: `claude/ea-trading-hours-filter`）を作成して実装することを推奨する
（このドキュメント作業ブランチ自体はEAコード変更を含めない方針を維持してきたため）。**

## 比較方法

| フィールド | 内容 |
|---|---|
| baseline | `EXP-002`(CC002, DS004)。買いサブセット(141件, PF1.059, 期待値R算出可能)を比較の基準とする |
| comparison_method | `TradingStartHour=22, TradingEndHour=15`（NY除外）を実装したビルドで、`EXP-002`と同一期間・同一パラメータ（`MaxDailyLossPercent=2, MaxConsecutiveLosses=3`含む）でバックテストを実行し、買いサブセットの期待値R・PF・取引数を比較する。売り方向の変化は参考記録として併記するが、H004の主結論には使わない |
| 変更点 | 時間帯フィルターの導入(`TradingStartHour/EndHour`の接続)のみ。EMA/ADX/ATR/TP/SL等の他ロジックは一切変更しない |

## 事前登録した評価指標（Primary/Secondary/Guardrail、結果を見た後に変更しない）

| 区分 | 指標 | 期待する方向性 |
|---|---|---|
| Primary Metric | 買いサブセットの期待値R | `EXP-002`買いサブセット(+0.022〜+0.13程度、`O-002`のNY除外時試算+0.197参照)を上回ること |
| Secondary Metrics | 買いサブセットのPF、取引回数 | PFは`EXP-002`買いサブセット(1.059)を上回ることが望ましい。取引回数はNYセッション分(約85/275=31%相当)減少する見込みで、これ自体は許容する（機会減少とのトレードオフとして記録） |
| Guardrail Metrics | 最低取引件数、最大DD | 取引数が極端に減りすぎないこと（目安: 買いのみで100件以上）。最大DDが`EXP-002`から悪化しないこと |

`rejection_criteria`: Primary Metric（買い期待値R）が`EXP-002`買いサブセット以下の場合、
`REJECTED`ではなく`HOLD`とする（`O-002`の観察が経路依存の影響で実際には再現しなかった可能性を
優先して疑うため。ただし何度も`HOLD`が続く場合はH004自体をREJECTEDとする判断も今後検討する）。

## required_data_sources（憲章第8節）

- USDJPY H1のMT4 Strategy Testerレポート（`.htm`形式） — 必須
- 可能であれば操作履歴`.htm`（取得できれば買い/売り別の詳細分析が可能。本MT4環境で保存できない
  場合はレポート集計値のみで判定する） — 任意
- 使用パラメータ一覧（`TradingStartHour/EndHour`の設定値を含む） — 必須
- EA Commit SHA（新規実装後に確定） — 必須
- コンパイル確認（0 errors / 0 warnings） — 必須

## パラメータ・再現性情報

| フィールド | 内容 |
|---|---|
| parameters | `TradingStartHour=22, TradingStartMinute=0, TradingEndHour=15, TradingEndMinute=0`。他は`EXP-002`と同一 |
| random_seed | 対象外 |
| code_version | `2c014aa`（ブランチ`claude/ea-trading-hours-filter`、基点`claude/ea-v0.3.0-risk-management`の`1cea16a`） |
| data_version | 未確定（MT4実行後に`DATASET_REGISTRY.md`へ登録） |
| execution_date | 未実施（コード実装は完了。MT4でのコンパイル・バックテスト実行待ち） |

## 事前登録チェックリスト

- [x] test_periodを実行前に確定している（`EXP-002`と同一期間）
- [x] acceptance_criteria（Primary/Secondary/Guardrail）を事前登録している
- [x] 未来データを参照する特徴量が含まれていない（時間帯フィルターはentry_time時点で判定可能な情報のみ使用）
- [x] H004が同一データからの探索的発見であることを明記し、本実験の結果だけでは確証的な検証にならない可能性を記録している（下記limitations参照）
- [x] EAコード変更の実施についてユーザーの承認を得ている（2026-08-14「実行する」により承認）
- [x] 実装ブランチについてユーザーと合意している（`claude/ea-trading-hours-filter`を提案し、ユーザー承認後に作成・実装・push済み）

## 実装ログ（2026-08-14）

- 実装ブランチ: `claude/ea-trading-hours-filter`（基点: `claude/ea-v0.3.0-risk-management`＝CC002/Phase5-1。
  `EXP-002`ベースラインとの単一変更点比較を成立させるため、`main`ではなくCC002から分岐した）
- 実装コミット: `2c014aa`（"feat: implement Phase7 trading-hours filter (EXP-006 / H004)"）
- 変更内容: `IsWithinTradingHours()`を新規追加し、`TryEnter()`内の`IsSpreadAcceptable()`チェックと
  同様の位置に`if(!IsWithinTradingHours()) { ログ出力; return; }`を追加。開始>終了の日またぎ判定を実装。
  新規入力パラメータの追加なし、既存デフォルト値(8:00-22:00)も変更なし
- diff範囲: `trading-system/mt4/USDJPY_LowRisk_Trend_EA.mq4`の1ファイルのみ（`git diff --stat`で確認、
  31 insertions, 3 deletions）。エントリー条件・決済条件・ロット計算・Phase5-1ロジックへの変更なし
- コンパイル確認: **未実施**（ユーザー側MetaEditorでの確認待ち）
- テスト: `pytest tests/ -q` 36 passed（Pythonパイプライン側、EA本体はMQL4のためpytest対象外）
- H004検証用の入力値`TradingStartHour=22, TradingStartMinute=0, TradingEndHour=15,
  TradingEndMinute=0`は、ストラテジーテスターの入力パラメータとして実行時に指定する
  （`EXP-003`での`MaxDailyLossPercent`/`MaxConsecutiveLosses`と同じ運用、コンパイル済み
  デフォルト値としては変更していない）

## status

**[2026-08-14更新]** `READY`（EAコード変更の承認・実装・push完了。コンパイル確認・
バックテスト実行はユーザー側で今後実施し、結果受領後に本ファイルを追記更新する）

~~`DRAFT`（Primary/Secondary/Guardrail Metricsの事前登録は完了。EAコード変更の承認待ちのため`READY`にはまだ進めない）~~
（2026-08-11時点の記録として残す）

## limitations（事前に予期される限界）

- **同一データからの探索的発見**: H004は`O-002`でDS001+DS004（378トレード）を対象に7特徴量ファミリーを
  探索した結果選ばれた仮説であり、本実験がその**同一期間**のデータで実行される場合、真のアウト・
  オブ・サンプル検証にはならない（`RESEARCH_RULES.md`第3節の精神に照らし、この点を明記する）。
  可能であれば別期間データでの検証が望ましいが、現状は`EXP-002`と同一期間で実施することを想定する
- 売り方向にも同じフィルターが適用されるため、売り方向の結果変化はH004の主張（買い方向の改善）とは
  別の混在要因になりうる。売り方向の変化は参考記録に留め、主結論には使わない
- 取引数減少（見込み約31%）により、サンプル数がさらに小さくなる可能性がある

## reviewer

未定（人間の承認者を今後指定）

## created_at / updated_at

- created_at: 2026-08-11
- updated_at: 2026-08-11（事前登録。H004実験登録の承認を受けて発行。EAコード変更は未実施、別途承認が必要）
- updated_at: 2026-08-14（ユーザー承認を受けてEAコード変更を実装・push。status DRAFT→READY。
  MT4でのコンパイル・実行はユーザー側で今後実施）

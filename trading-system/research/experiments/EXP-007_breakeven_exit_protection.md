# EXP-007: 含み益+1R到達後の建値移動によるExit保護検証

`EXPERIMENT_TEMPLATE.md`に基づく実験記録。**H005（`HYPOTHESIS_REGISTRY.md`）の事前登録実験。
ユーザーが2026-08-15、「そのまま改善して」とH005の提案を承認したことを受けて発行する。
**本ファイル作成時点ではEAコードは一切変更していない**（後述「実装の要否」参照、実行には
別途明示的な承認が必要）。

## 基本情報

| フィールド | 内容 |
|---|---|
| experiment_id | EXP-007 |
| hypothesis_id | H005（含み益+1R到達後の建値移動によるExit保護仮説） |
| title | 含み益+1R到達後の建値移動によるExit保護検証 |
| evidence_level | H（検証前） |
| objective | ポジションが含み益+1.0R以上に到達した時点で損切りを建値+オフセットへ移動する処理を実装し、PF・純利益・期待値Rが改善するかを実バックテストで検証する |
| rationale | `DIAG-001_ENTRY_EXIT_ANALYSIS.md`のStage2（MFE/MAE実測）で、損切り決済トレードの約24%（DS004: 33/138件23.9%、DS001: 31/129件24.0%）が、一度+1.0R以上の含み益に到達してから最終的に-1.0Rの全損まで反転していたことを確認した。現行EAには利益保護機構（建値移動・トレーリング・部分利確）が一切実装されていない。勝ちトレードのMFE capture ratioは87〜91%と高く、TP幅自体の設計は妥当と判断されているため、「TP/SL幅の変更」ではなく「保護機構の追加」が示唆されている |
| evidence_ids | なし |
| features | 既存入力`EnableBreakEven`/`BreakEvenAtR`/`BreakEvenOffsetPips`の機能実装。エントリー条件(EMA/ADX/押し目判定)・TP/SL初期値・ロット計算は一切変更しない |
| target | 下記「acceptance_criteria」参照 |

## 実装の要否（重要、実行前に承認が必要）

EA (`trading-system/mt4/USDJPY_LowRisk_Trend_EA.mq4`) には`EnableBreakEven`/`BreakEvenAtR`/
`BreakEvenOffsetPips`という入力パラメータが**既に存在する**（デフォルト: `EnableBreakEven=true`,
`BreakEvenAtR=1.0`, `BreakEvenOffsetPips=2.0`）が、`TradingStartHour`等と同様、宣言のみで
`OnTick()`のポジション管理には一切接続されていない（`OnTick()`末尾のコメント
「Phase5-2でここにポジション管理(建値移動/トレーリング/金曜決済)を追加予定」の通り）。

したがって、**本実験を実行するには、この既存パラメータをポジション管理ロジックへ接続する、
EAコードの変更が必要**。想定する最小限の変更:

- `ManageOpenPosition()`という新規関数を追加し、`OnTick()`から毎tick呼び出す（新規バーの確定を
  待たず、含み益到達を早期に検知するため。エントリー判定`TryEnter()`とは独立した経路とする）
- 保有中のポジション(Symbol+MagicNumber一致)について、現在の含み益をR単位で計算する。
  計算式はDIAG-001のMFE/MAE再構成・`feature_extraction.py`と同一の`realized_R`計算式を踏襲する
  （`risk = stop_distance_pips × pip_value_per_lot × lot`、`floating_profit_R = floating_profit / risk`）
- `EnableBreakEven=true`かつ`floating_profit_R >= BreakEvenAtR`の場合、現在のSLが建値
  （エントリー価格±`BreakEvenOffsetPips`、方向に応じて有利側にオフセット）より不利な位置にあれば
  `SafeOrderModify()`でSLのみを建値+オフセットへ移動する。TPは変更しない
- 既に建値以上までSLが移動済みの場合は再度の`OrderModify`を発行しない（現在のSLと目標建値価格を
  比較し、目標に到達済みならスキップする。冪等性を保つため、フラグではなく毎回SL位置を比較する
  設計とする）
- `EnableTrailingStop`（トレーリングストップ）・`EnableFridayClose`（金曜決済）は本実験の対象外。
  引き続き未接続のまま残す（それぞれ別のHypothesisとして検討する）
- 新しい入力パラメータは追加しない。既存デフォルト値を変更しない（`BreakEvenAtR=1.0`,
  `BreakEvenOffsetPips=2.0`のまま使用する。これは`EXP-006`のように非標準の試験値を使う実験ではなく、
  **既存デフォルト値そのものでの機能検証**という位置づけ）

**本ファイルの事前登録時点では、このコード変更は実施していない。実装するにはユーザーの
別途明示的な承認が必要（`RESEARCH_RULES.md`第11節、EAコード変更を伴うため）。実装する場合、
`EXP-006`と同様、新規ブランチ（例: `claude/ea-breakeven-exit-protection`、基点は
`claude/ea-v0.3.0-risk-management`＝CC002/Phase5-1）を作成して実装することを推奨する。**

## 比較方法

| フィールド | 内容 |
|---|---|
| baseline | `EXP-002`(CC002, DS004)。全体(195件, PF0.76公式値)を比較の基準とする。時間帯フィルター(`EXP-006`/H004)は`HOLD`のため適用しない、独立した変更点として扱う |
| comparison_method | 建値移動ロジックを実装したビルドで、`EXP-002`と同一期間・同一パラメータ（`MaxDailyLossPercent=2, MaxConsecutiveLosses=3`含む、`TradingStartHour/EndHour`は未接続時のデフォルトのまま）でバックテストを実行し、全体・買いサブセット・売りサブセット別のPF・純利益・期待値Rを比較する |
| 変更点 | 建値移動ロジックの導入(`EnableBreakEven`/`BreakEvenAtR`/`BreakEvenOffsetPips`の接続)のみ。エントリー条件・TP/SL初期値・ロット計算・Phase5-1ロジック・時間帯フィルターは一切変更しない |

## 事前登録した評価指標（Primary/Secondary/Guardrail、結果を見た後に変更しない）

| 区分 | 指標 | 期待する方向性 |
|---|---|---|
| Primary Metric | 全体の期待値R（`EXP-002`と同一の実現R計算式で算出） | `EXP-002`のBaseline値を上回ること（`EXP-002`の実トレード明細データがこのセッションでは未取得のため、正確な基準値は実装完了後・実行直前に`EXP-002`の生データを再取得して確定する） |
| Secondary Metrics | 買いサブセット・売りサブセット別のPF・期待値R、取引回数 | 取引回数は`EXP-002`とほぼ同数のはず（エントリー条件を変更していないため）。大きく異なる場合はロジック実装の誤りを疑う |
| Guardrail Metrics | 最大DD、最大連敗（金額ベース） | `EXP-002`から悪化しないこと。特に「建値に移動したことで、その後さらに不利な方向へ動いて建値未満で決済され、かつ本来のSLよりは損失が小さい」ケースが正しく機能しているかを個別トレードで抽出的に確認する |

`rejection_criteria`: Primary Metric（期待値R）が`EXP-002`のBaseline以下の場合、`REJECTED`ではなく
`HOLD`とする（`EXP-006`と同じ理由づけ: 一度の結果だけで機構自体を否定しない。ただし本仮説は
既存データの事後的な絞り込みではなく実測ベース〔DIAG-001 Stage2〕の直接的な構造的欠陥に基づく
提案であるため、H004より再現可能性への確信度は高いと位置づける）。

## required_data_sources（憲章第8節）

- USDJPY H1のMT4 Strategy Testerレポート（`.htm`形式、操作履歴込み） — 必須
- 使用パラメータ一覧（`EnableBreakEven`/`BreakEvenAtR`/`BreakEvenOffsetPips`の設定値を含む） — 必須
- EA Commit SHA（新規実装後に確定） — 必須
- コンパイル確認（0 errors / 0 warnings。今回は特に「0 warnings」の明示的な確認をお願いしたい） — 必須
- Expertsログ（建値移動の発動有無・回数を確認するため。レポート集計だけでは判定できない） — 必須（`EXP-003`/`EXP-006`と同様の理由）

## パラメータ・再現性情報

| フィールド | 内容 |
|---|---|
| parameters | `EnableBreakEven=true, BreakEvenAtR=1.0, BreakEvenOffsetPips=2.0`（すべて既存デフォルト値）。他は`EXP-002`と同一 |
| random_seed | 対象外 |
| code_version | 未確定（コード実装後に確定。新規ブランチを想定） |
| data_version | 未確定（実行後に`DATASET_REGISTRY.md`へ登録） |
| execution_date | 未実施（コード実装の承認待ち） |

## 事前登録チェックリスト

- [x] test_periodを実行前に確定している（`EXP-002`と同一期間）
- [x] acceptance_criteria（Primary/Secondary/Guardrail）を事前登録している
- [x] 未来データを参照する特徴量が含まれていない（建値移動判定は現在の含み益のみを使用）
- [x] H005がMFE/MAE実測（DIAG-001 Stage2）という直接的な構造分析に基づくことを明記している（H004のような事後的な特徴量相関ではない点が異なる）
- [ ] EAコード変更の実施についてユーザーの承認を得ている（**未実施、本実験の実行条件**）
- [ ] 実装ブランチについてユーザーと合意している（未実施）

## limitations（事前に予期される限界）

- **同一データからの構造分析**: H005はDIAG-001でDS001/DS004（本実験のBaselineと同一期間・近い構成）
  を対象に実測した結果に基づく提案であり、本実験がその同一期間のデータで実行される場合、真の
  アウト・オブ・サンプル検証にはならない
- **経路依存効果**: `EXP-006`で確認された通り、Exit条件を変更するとそれ以降の値動きへの追従経路
  そのものが変わる可能性がある。DIAG-001の「参考試算$5,719/$5,410」はこの効果を考慮しない
  単純計算であり、実際の改善幅がこれと一致するとは限らない（診断書内に明記済み）
- **建値移動特有のトレードオフ**: SLを建値へ動かすことで、一時的に含み益+1R到達後に建値付近まで
  戻ってから再度TPへ向かうような値動きのトレードが、本来はTPまで到達していたはずが建値決済に
  なってしまうケースが生じうる。これは実測結果を見るまで方向・規模とも不明
- **DIAG-001の$試算はDS001/DS004ベース**であり、`EXP-002`(DS004)をBaselineとする本実験と一部重複
  する期間・データを参照している。Primary Metricの正確な基準値は実装完了後に`EXP-002`の生データを
  再取得して確定する（本ファイルの現時点では概算のみ）

## reviewer

未定（人間の承認者を今後指定）

## status

`DRAFT`（Primary/Secondary/Guardrail Metricsの事前登録は完了。EAコード変更の承認待ちのため`READY`にはまだ進めない）

## created_at / updated_at

- created_at: 2026-08-15
- updated_at: 2026-08-15（事前登録。H005実験登録の承認を受けて発行。EAコード変更は未実施、別途承認が必要）

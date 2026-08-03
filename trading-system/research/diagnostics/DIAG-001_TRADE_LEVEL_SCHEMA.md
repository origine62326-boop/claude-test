# DIAG-001: トレードレベル・スキーマ定義

`DIAG-001_ENTRY_EXIT_ANALYSIS.md`が使用するトレードレベルのフィールド定義。各フィールドの
算出可否と根拠を明記する（推測で埋めない、`RESEARCH_CHARTER.md`第2節）。

## 可否の凡例

- `AVAILABLE`: 既存データ（操作履歴`.htm`）から直接または単純計算で算出可能
- `AVAILABLE_APPROX`: 追加データ（H1 OHLC価格履歴）取得後、近似値として算出可能
- `NOT_AVAILABLE`: 現状のデータ・コードでは算出不能（理由を付す）
- `KNOWN_CONSTANT`: 推測ではなくコード確認により値が確定している（EAソース参照済み）

## フィールド一覧

| フィールド | 可否 | 算出方法・根拠 |
|---|---|---|
| trade_id | AVAILABLE | `dataset_id` + `ticket`で一意化（例: `DS004-196`） |
| ticket | AVAILABLE | 操作履歴`.htm`の`ticket`列 |
| direction | AVAILABLE | 操作履歴`.htm`の`type`列（buy/sell）。**Expertsログ単独では取得不可**（`ExecuteEntry()`のログ出力に方向文字列が含まれないことをコード確認済み、`OrderSend`の`comment`引数`LRT_BUY`/`LRT_SELL`はMT4の仕様上、操作履歴のコメント欄に残る場合とログにのみ残る場合がありブローカー依存、本セッションでは操作履歴`type`列を正とする） |
| entry_time | AVAILABLE | 操作履歴`.htm`の`open_time` |
| exit_time | AVAILABLE | 操作履歴`.htm`の`close_time` |
| entry_price | AVAILABLE | 操作履歴`.htm`の`open_price` |
| exit_price | AVAILABLE | 操作履歴`.htm`の`close_price` |
| initial_sl | AVAILABLE | 操作履歴`.htm`の`sl`列。**注記**: `KNOWN_CONSTANT`によりSL/TPはエントリー後に一切変更されない（`OnTick()`にポジション管理ロジックが存在しないことをCC001/CC002双方でコード確認済み）ため、この値は「初期」であると同時に「最終」でもある |
| initial_tp | AVAILABLE | 操作履歴`.htm`の`tp`列。同上の理由で不変 |
| stop_distance_pips | AVAILABLE | `abs(entry_price - initial_sl) / 0.01`（USDJPYの1pip=0.01） |
| target_distance_pips | AVAILABLE | `abs(initial_tp - entry_price) / 0.01` |
| planned_RR | AVAILABLE | `target_distance_pips / stop_distance_pips`。EA入力`RewardRiskRatio`と一致するはず（実測値との整合確認に使う） |
| realized_pnl | AVAILABLE | 操作履歴`.htm`の`profit`列 |
| realized_R | AVAILABLE | `realized_pnl / actual_initial_risk_amount`（下記参照） |
| MFE_pips | AVAILABLE_APPROX | H1 OHLC取得後、entry_timeからexit_timeまでの各H1バーについて、買いなら`high`、売りなら`low`側の最大有利変動をentry_priceからの差分で算出。**H1バー粒度の近似値であり、ティック単位の真のMFEより過小評価されうる** |
| MAE_pips | AVAILABLE_APPROX | 同上、逆方向（買いなら`low`、売りなら`high`側の最大不利変動） |
| MFE_R | AVAILABLE_APPROX | `MFE_pips / stop_distance_pips` |
| MAE_R | AVAILABLE_APPROX | `MAE_pips / stop_distance_pips` |
| time_to_MFE | AVAILABLE_APPROX | MFEを記録したH1バーのバー番号・時刻（H1粒度） |
| time_to_MAE | AVAILABLE_APPROX | 同上、MAE版 |
| holding_time | AVAILABLE | `exit_time - entry_time` |
| exit_type | AVAILABLE | 操作履歴`.htm`の`close_reason`列（`s/l`または`t/p`のみ。実データで確認した限り他の値は出現しない） |
| break_even_applied | KNOWN_CONSTANT | **常にFALSE**（`OnTick()`にポジション管理ロジックが存在しないことをCC001・CC002双方のソースで確認済み。推測ではなくコード事実） |
| maximum_lot_capped | AVAILABLE | `theoretical_lot_before_cap > MaximumLot(=1.0)`で判定 |
| theoretical_lot_before_cap | AVAILABLE | `(balance_at_entry × RiskPercent/100) / (stop_distance_pips × pip_value_per_lot)`。`pip_value_per_lot = (0.01 × 100000) / entry_price`（USDJPY、簡易近似。ブローカーのTickValue仕様の完全な再現ではない点に注意） |
| actual_lot | AVAILABLE | 操作履歴`.htm`の`lots`列 |
| theoretical_risk_amount | AVAILABLE | `balance_at_entry × RiskPercent/100` |
| actual_initial_risk_amount | AVAILABLE | `stop_distance_pips × pip_value_per_lot × actual_lot` |
| long_or_short | AVAILABLE | `direction`と同一（別名として維持、ユーザー指定スキーマに合わせる） |

## balance_at_entry の算出方法

操作履歴`.htm`は`balance_after`（決済後残高）のみを持つため、`balance_at_entry`は
**エントリー時刻の直前に決済されたトレードの`balance_after`**（初回トレードのみ初期証拠金100,000）
を時系列順に追跡して算出する。ポジションは同時に最大1つ（`HasOpenPosition()`により保証済み、
`RISK_ENGINE_SPEC.md`参照）のため、この追跡は曖昧性なく行える。

## pip_value_per_lot の近似精度について

`(0.01 × 100000) / entry_price`は、USDJPYの1標準ロット(100,000通貨)あたりの1pip価値をUSD建てで
近似する式であり、ブローカーの実際のTickValue/TickSize仕様（コミッション・スワップ・約定通貨等の
細部）を完全には再現しない。理論ロットの算出はあくまで**近似**であり、`CalculateLotSize()`の
実装（`trading-system/mt4/USDJPY_LowRisk_Trend_EA.mq4`）と完全一致する保証はない。ただし
`DIAG-001_ENTRY_EXIT_ANALYSIS.md`で示す通り、この近似でも「理論ロットが183/183・195/195件で
`MaximumLot`を超過している」という結論は、近似誤差を考慮しても覆らない規模の差（中央値で
理論値が実際の約2.6〜2.7倍）である。

## データソース別の利用可否まとめ

| データセット | 対応実験 | 操作履歴`.htm` | 本スキーマでの利用可否 |
|---|---|---|---|
| DS001 | EXP-001 | あり | Stage1(AVAILABLE項目)は利用可能。Stage2はH1 OHLC取得後に可能 |
| DS004 | EXP-002 | あり | 同上 |
| DS005 | EXP-003 | **なし**（本MT4環境で保存不可と確認済み） | Stage1・Stage2とも**利用不可**（entry_price/sl/tp/close_reason等の個別トレード情報が存在しない） |
| （EXP-004データ） | EXP-004 | 未取得（実行自体が未完了） | 同上、取得できても操作履歴なしなら同じ制約 |

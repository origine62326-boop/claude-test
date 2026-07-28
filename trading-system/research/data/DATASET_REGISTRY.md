# Dataset Registry

`trading-system/RESEARCH_CHARTER.md` 第7節(Layer 1/2)・第17節に基づくデータセット管理表。

## 運用ルール

- 実験(`EXPERIMENT_TEMPLATE.md`)で使用するデータセットは、必ず`dataset_id`と`data_version`を
  記録し、後から同じデータで再現できるようにする。
- `checksum`はデータファイルの同一性確認に用いる。同じ`dataset_id`でも内容が変わった場合は
  `data_version`を上げ、旧バージョンの行は書き換えずに残す。
- `known_issues`には、モデリング品質・不整合チャートエラー・欠損・タイムゾーンの疑義など、
  既知の問題点を必ず記載する。

## 列定義

| 列 | 説明 |
|---|---|
| dataset_id | 一意のID |
| source | 取得元（例: MT4 Strategy Tester Export, Yahoo Finance chart API） |
| symbol | 通貨ペア等 |
| timeframe | 時間足 |
| start_time / end_time | データ期間 |
| timezone | 基準タイムゾーン |
| broker | ブローカー（該当する場合） |
| spread_model | 固定/変動、参照したスプレッド値 |
| data_version | バージョン番号 |
| checksum | ファイルのハッシュ値等 |
| missing_rate | 欠損率 |
| quality_status | 品質評価（例: モデリング品質%、不整合チャートエラー件数） |
| known_issues | 既知の問題点 |
| permitted_uses | 使ってよい用途 |
| prohibited_uses | 使ってはいけない用途 |

## 初期登録（棚卸し結果）

現時点で本リポジトリに存在する、または会話内でユーザーから共有されたデータソースを事実として記録する。
いずれも`quality_status`・`checksum`等は未確定のものが多く、正式なデータセットとして`ACTIVE`扱いには
していない。

| dataset_id | source | symbol | timeframe | start_time | end_time | timezone | broker | spread_model | data_version | checksum | missing_rate | quality_status | known_issues | permitted_uses | prohibited_uses | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DS001 | MT4 Strategy Tester export (`trading-system/reports/raw/`予定) | USDJPY | H1 | (未確定) | (未確定) | サーバー時間(未確認) | Rakuten Securities (Rakuten MT4, Demo) | ブローカー実測スプレッド(未記録) | v0(未取り込み) | (未計算) | (未計測) | (未計測) | `reports/raw/`はディレクトリのみ存在し実データは`.gitkeep`のみ(2026-07-28時点)。実際の`.htm`レポートはまだリポジトリに取り込まれていない | 未定(取り込み後に決定) | 実データ取り込み前の実験には使用不可 | DRAFT |
| DS002 | ユーザー提供スクリーンショット(MT4 Strategy Tester レポートタブ, 2026-07-28会話内で共有) | USDJPY | H1 | (画面上のチャート範囲は2026-07-16〜2026-07-24だが、テストバー数7285はこれよりはるかに長い全体テスト期間を示唆。正確な開始/終了日は未確認) | (未確認) | サーバー時間(未確認) | Rakuten Securities (Rakuten MT4, Demo) | (未記録) | (画像のみ、ファイル化されていない) | (算出不可、画像のため) | (算出不可) | モデリング品質57.79%、不整合チャートエラー2件（スクリーンショット記載値） | 画像ベースであり`parse_mt4_report.py`等のパイプラインには未投入。集計値の会話内分析のみに使用済み | 定性的な会話内考察の参考情報としてのみ | 正式な実験(EXPERIMENT_TEMPLATE.md)の`metrics`欄への直接転記、Evidence登録 | DRAFT |
| DS003 | Yahoo Finance chart API (`query1.finance.yahoo.com/v8/finance/chart/JPY=X`) | USD/JPY | 日次終値 | 可変(`--history-range`引数, 既定2y) | 実行時点まで | 未確認(API仕様の要確認事項) | (取引所ではなく参考レート集約元) | 適用外(レートのみ、スプレッドなし) | 実行毎に再取得(`data/`配下にキャッシュ、gitignore対象) | (未計算) | (未計測) | 未計測（日次終値のみで、モデリング品質等のMT4指標は適用外） | `fx_predict.py`/`fx_modules/fetcher.py`が使用。取引コスト・スプレッドを含まない参考レートであり、EAのバックテストとは別データ系統 | LSTM予測(`fx_predict.py`)の学習・推論入力 | MT4ベースのバックテスト実験への直接流用（データ系統・コスト前提が異なるため） | DRAFT |

## status候補

DRAFT / VALIDATING / ACTIVE / DEPRECATED / QUARANTINED

- `QUARANTINED`: 品質問題（未来データ混入疑い、破損等）が判明し、解消するまで使用禁止としたデータ

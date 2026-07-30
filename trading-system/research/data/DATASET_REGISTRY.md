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
| DS001 | MT4 Strategy Tester export (`trading-system/reports/raw/EXP-001_run01_report.htm`, gitignore対象のためリポジトリには含まれない。checksumで同一性確認) | USDJPY | H1 | 2025-07-21 (テスト開始、実際の初回エントリーは2025-07-23 11:00) | 2026-07-27 (テスト終了設定。実際の最終エントリーは2026-07-24 11:00、テスト終了時点で1件未決済) | サーバー時間(RakutenSecurities-Demo、UTC/JSTとの対応は未確認) | Rakuten Securities (RakutenSecurities-Demo, Build 1475) | 現在値(5)固定モードと表示（レポート「スプレッド」欄）。モデルは「全ティック」だが、テスト全期間で本当に5固定だったか、それとも表示上の代表値かは未確認 | v1(2026-07-28に初取り込み) | sha256:92cf4bf55ad997eafb646f4a8d973864193016602c8a83bcb4100f8354f2776c | 24必須項目中1件欠損(`currency`。MT4レポートに明示的な通貨コード欄がないための既知の限界) | モデリング品質57.79%、不整合チャートエラー2件。総取引数184件（うち183件決済・1件テスト終了時未決済）で、`acceptance_criteria.yaml`の最低取引数200件を下回る | **[既知の未解決事項]** トレード明細からの再計算値とレポート公式値に小さな乖離あり（期待利得: 再計算-33.808 vs 報告-33.31、純利益: 再計算-6186.90 vs 報告-6128.31、勝率: 再計算29.51%(54勝) vs 報告29.89%(55勝)）。原因未特定（テスト終了時未決済ポジションの含み損益が公式値に反映されている可能性等、仮説段階）。`trading-system/scripts/run_analysis.py`の`_cross_check_mismatches`が自動検出済み | EXP-001(H001)での使用。PF/勝率等の記述統計としての参照 | 最低取引数未達のため単独でのADOPTED判定には使用不可（HOLD止まり、`EXP-001`参照）。使用EAビルド(main/Phase1-4かPhase5-1未マージブランチか)が未確認のため、H002(Phase5-1固有の効果)の直接的な検証には現時点で使用しない | ACTIVE |
| DS002 | ユーザー提供スクリーンショット(MT4 Strategy Tester レポートタブ, 2026-07-28会話内で共有) | USDJPY | H1 | (画面上のチャート範囲は2026-07-16〜2026-07-24だが、テストバー数7285はこれよりはるかに長い全体テスト期間を示唆。正確な開始/終了日は未確認) | (未確認) | サーバー時間(未確認) | Rakuten Securities (Rakuten MT4, Demo) | (未記録) | (画像のみ、ファイル化されていない) | (算出不可、画像のため) | (算出不可) | モデリング品質57.79%、不整合チャートエラー2件（スクリーンショット記載値） | **[UNVERIFIED_OBSERVATION]** 画像ベースであり`parse_mt4_report.py`等のパイプラインには未投入。集計値の会話内分析のみに使用済み。MT4 HTMLレポート・使用パラメータ・コードSHA・データ条件・ファイルハッシュのいずれも未取得のため、正式なResearch ResultやEvidenceには昇格できない | 定性的な会話内考察の参考情報としてのみ | 正式な実験(EXPERIMENT_TEMPLATE.md)の`metrics`欄への直接転記、Evidence登録、`MODEL_REGISTRY.md`等での確定値としての扱い（いずれも`[UNVERIFIED_OBSERVATION]`の明記なしでの引用は禁止） | DRAFT |
| DS003 | Yahoo Finance chart API (`query1.finance.yahoo.com/v8/finance/chart/JPY=X`) | USD/JPY | 日次終値 | 可変(`--history-range`引数, 既定2y) | 実行時点まで | 未確認(API仕様の要確認事項) | (取引所ではなく参考レート集約元) | 適用外(レートのみ、スプレッドなし) | 実行毎に再取得(`data/`配下にキャッシュ、gitignore対象) | (未計算) | (未計測) | 未計測（日次終値のみで、モデリング品質等のMT4指標は適用外） | `fx_predict.py`/`fx_modules/fetcher.py`が使用。取引コスト・スプレッドを含まない参考レートであり、EAのバックテストとは別データ系統 | LSTM予測(`fx_predict.py`)の学習・推論入力 | MT4ベースのバックテスト実験への直接流用（データ系統・コスト前提が異なるため） | DRAFT |

## status候補

DRAFT / VALIDATING / ACTIVE / DEPRECATED / QUARANTINED

- `QUARANTINED`: 品質問題（未来データ混入疑い、破損等）が判明し、解消するまで使用禁止としたデータ

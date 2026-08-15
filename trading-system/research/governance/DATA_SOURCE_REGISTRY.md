# Data Source Registry

`FACT_SCHEMA.md`の「Factは`DATA_SOURCE_REGISTRY.md`に登録済みのソースからのみ取得する」規定に基づく
データソース台帳。Phase 2（`RESEARCH_PLATFORM_ROADMAP.md`参照）として、2026-07-31にこの実行環境から
実際に到達性を確認した結果を記録する。**「網羅的」とは、ユーザーの再定義に従い「取得可能で、出典・
時刻・価格データを検証できる範囲を最大限網羅する」ことを意味し、有料・認証必須・スクレイピング
規約違反等で取得できないソースは無理に含めない。**

## 検証方法（この文書の値の根拠）

各ソースについて、本セッション内で`curl`により実際にHTTPリクエストを送り、到達性（HTTPステータス）と
可能な範囲で実データの中身を確認した。推測や一般的な知識だけに基づく記載はしていない。認証が必要な
ソースは、実際にAPIキーを取得・登録するところまでは行っていない（本セッションからのユーザー承認済み
アカウント・APIキーがないため）。この場合は「エンドポイントの到達性は確認したが、実データ取得は
未確認」として区別する。表の各セルは長い説明を1行に収めている（Markdownテーブルの制約上、セル内で
改行するとテーブル構造が崩れるため、詳細な注記は表下の「補足」に分離した行がある）。

## 列定義

| 列 | 説明 |
|---|---|
| source_id | 一意のID（`SRC-###`） |
| 提供元 | データの一次発行者 |
| 取得方法 | 具体的なエンドポイント・アクセス方法 |
| 対象期間 | 遡及可能な期間（確認できた範囲） |
| 更新頻度 | 公表・更新の頻度 |
| 時間精度 | タイムスタンプの粒度（日次/分次/イベント発生時刻等） |
| 利用条件 | 認証要否・利用規約上の制約 |
| 費用 | 無料/有料/条件付き無料 |
| 到達性確認結果 | 本セッションでの実際の確認結果（HTTPステータス等） |
| status | `CONFIRMED_ACCESSIBLE` / `REQUIRES_REGISTRATION` / `NOT_ACCESSIBLE` / `NOT_PERMITTED` |

商用利用可否・再配布可否・欠損の詳細は、列を分けると行が過度に長くなるため、各ソースの後に続く
「補足」段落にまとめて記載する（`DATASET_REGISTRY.md`の列構成とは異なる簡略構成であることに注意）。

## 価格データソースの必須記録項目（2026-08-15、Data Expansion Phaseで追加）

別ソースから価格データを取得する場合、`DATASET_REGISTRY.md`へ登録する際に以下を**必須項目**とする。
ソースごとに仕様が異なり、これらを記録しないと結果差の原因を切り分けられないためである。

| 項目 | 記録内容 |
|---|---|
| timezone | サーバー時間の基準（UTC+N、またはブローカー固有） |
| DST | 夏時間の適用有無・切替タイミング |
| daily rollover | 日足の区切り時刻 |
| Bid/Ask仕様 | Bidのみか、Ask/スプレッドを含むか |
| spread | 固定/変動、実測値の有無 |
| missing bars | 欠損バーの件数・分布 |
| duplicate bars | 重複バーの有無 |
| weekend bars | 週末バーの有無・扱い |
| volume定義 | ティック数か実出来高か（ソースにより異なる） |
| data_epoch | `LEGACY_DATA_EPOCH` / `HIGHER_FIDELITY_DATA_EPOCH` |
| layer | `A`(Research) / `B`(Execution) / `A+B` |

### 別ソースの結果の扱い（重要）

- 別ソースで良い結果が出ても、**Rakuten MT4で同一結果になるとは扱わない**
- 逆に、**複数ソースで同じ効果方向が出れば `Robustness Evidence` として扱える**
- 単一ソースでの結果は、そのソース条件下での事実に留まる


## 価格データ

| source_id | 提供元 | 取得方法 | 対象期間 | 更新頻度 | 時間精度 | 利用条件 | 費用 | 到達性確認結果 | status |
|---|---|---|---|---|---|---|---|---|---|
| SRC-001 | Yahoo Finance（`query1.finance.yahoo.com`、非公式chart API） | `fx_modules/fetcher.py`が使用中の`GET /v8/finance/chart/JPY=X` | 可変（`--history-range`引数、既定2年、日次終値） | 日次 | 日足のみ | 非公式API、公式ToS上の商用可否は未確認 | 無料（レート制限あり） | 2026-07-31時点でHTTP 429（レート制限）を受信 | REQUIRES_REGISTRATION |
| SRC-002 | Rakuten Securities (Rakuten MT4, Demo) | MT4 Strategy Testerのエクスポート（`.htm`レポート、`Experts.log`）をユーザーが手動で共有 | ユーザー設定期間（DS001/DS004実績で2025-07-21〜2026-07-27） | 手動実行の都度 | H1バー単位 | デモ口座利用規約に従う（未読了）。本セッションはMT4に直接接続していない | デモ口座は無料 | トップページ`fx.rakuten-sec.co.jp`はHTTP 200だが、これはデータ提供とは無関係 | NOT_ACCESSIBLE |

**補足（SRC-001）**: 欠損はスプレッド・出来高情報なし、週末休場日欠損（想定通り）。商用利用可否・
再配布可否ともに未確認（非公式APIのためYahoo公式の許諾は確認できていない。既存コード
`fx_predict.py`は研究・個人利用目的での使用）。

**補足（SRC-002）**: 通貨コード欄なし等、既存の`DATASET_REGISTRY.md`記載の欠損あり。商用利用可否・
再配布可否は未確認。本セッションから直接アクセスは不可で、ユーザー環境のMT4経由の手動連携のみ。

## 金利・中央銀行・公的統計

| source_id | 提供元 | 取得方法 | 対象期間 | 更新頻度 | 時間精度 | 利用条件 | 費用 | 到達性確認結果 | status |
|---|---|---|---|---|---|---|---|---|---|
| SRC-010 | ECB (欧州中央銀行) Data Portal | `GET https://data-api.ecb.europa.eu/service/data/EXR/...`（SDMX形式） | 日次為替参照レート等の長期時系列（最新1件のみ確認、遡及範囲は別途要確認） | 営業日ごと | 日次 | 認証不要、公開データ | 無料 | HTTP 200、実データ（JPY/EUR参照レート、CSV形式）を取得成功 | CONFIRMED_ACCESSIBLE |
| SRC-011 | 米国St. Louis連銀 FRED | `GET https://api.stlouisfed.org/fred/series/observations`（要APIキー）、または`https://fred.stlouisfed.org/graph/fredgraph.csv?id=<series>`（キー不要） | シリーズによるが数十年規模が多い（例: `DEXJPUS`） | シリーズによる | シリーズによる | フルAPIは無料登録必要、CSVエンドポイントは不要 | 無料 | APIはHTTP 400（`api_key`未設定エラー、生存確認）。CSVエンドポイントはHTTP 200で取得成功 | REQUIRES_REGISTRATION |
| SRC-012 | BIS (国際決済銀行) Data Portal | `https://data.bis.org/bulkdownload`（旧URLからリダイレクト） | データセットによる（金利・為替・信用統計等） | データセットによる | データセットによる | 認証不要、公開データ | 無料 | HTTP 302でリダイレクト後`data.bis.org/bulkdownload`にHTTP 200到達。個別CSVのDLは未実施 | CONFIRMED_ACCESSIBLE |
| SRC-013 | 日本銀行 時系列統計データ検索サイト | `https://www.stat-search.boj.or.jp/`（検索UI経由のCSV/Excel DL） | 系列による（長期系列あり） | 系列による | 系列による | 認証不要、公開データ | 無料 | トップページはHTTP 200。個別系列ページの直接URLはHTTP 404で要追加調査 | REQUIRES_REGISTRATION |
| SRC-014 | 米国労働統計局 (BLS) Public API v2 | `GET https://api.bls.gov/publicAPI/v2/timeseries/data/<series_id>` | シリーズによる（雇用統計等、数十年規模） | 月次 | 月次（速報値/改定値フラグあり） | APIキーなしで利用可（登録で上限緩和） | 無料 | APIキーなしでHTTP 200、実データ（雇用統計、速報値フラグ付き）を取得成功 | CONFIRMED_ACCESSIBLE |
| SRC-015 | 日本 e-Stat（政府統計の総合窓口） | `GET https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList`（要`appId`） | 統計による | 統計による | 統計による | 無料のアプリケーションID登録が必要 | 無料 | `appId=test`でHTTP 200だがAPI側は認証エラーを返却（エンドポイント自体は生存） | REQUIRES_REGISTRATION |
| SRC-016 | 財務省 (MOF) 為替介入実績 | `https://www.mof.go.jp/policy/international_policy/reference/feio/index.html`（Excel/PDF） | 公表開始以降（月次公表） | 月次（実施時のみ） | 実施日単位（時刻精度は資料により異なる、要個別確認） | 認証不要、公開資料 | 無料 | HTTP 200でページ到達確認。個別ファイルのDL・解析は未実施 | CONFIRMED_ACCESSIBLE |

**補足**: いずれも商用利用可否・再配布可否は本セッションで規約全文を読了していないため未確認として
扱う（一般に公的機関統計は出典明記の上での再利用を許容することが多いが、断定はしない）。

## 先物ポジション・センチメント

| source_id | 提供元 | 取得方法 | 対象期間 | 更新頻度 | 時間精度 | 利用条件 | 費用 | 到達性確認結果 | status |
|---|---|---|---|---|---|---|---|---|---|
| SRC-020 | CFTC Commitments of Traders (COT)、Socrata公開API経由 | `GET https://publicreporting.cftc.gov/resource/6dca-aqww.json` | 長期（レガシーレポートは1980年代〜） | 週次（毎週金曜公表、火曜時点） | 週次スナップショット（日中精度なし） | 認証不要（アプリトークンなしで利用可、レート制限あり） | 無料 | HTTP 200、実データ（先物ポジションレポート）を取得成功 | CONFIRMED_ACCESSIBLE |
| SRC-021 | OANDA Order Book / Position Ratios | 旧`developer.oanda.com` legacy APIおよび`oanda.com/forex-trading/analysis/open-position-ratios` | — | — | — | 取引口座+APIトークン必須（現行v20 API） | — | 旧ページはHTTP 301で無関係ページへ、旧APIはHTTP 404（廃止済み）、現行v20 APIはHTTP 401（認証必須） | NOT_ACCESSIBLE |

**補足（SRC-020）**: 通貨先物（CME上場JPY先物等）が対象で現物FXの直接データではなく、プロキシとして
扱う必要がある。米国商品先物取引委員会の公表データでパブリックドメイン相当と考えられるが規約全文は
未読了。

**補足（SRC-021、重要な訂正）**: 以前の会話内で「OANDA Order Book/Position Bookは公開されている実在の
FXポジショニングデータソース」と述べたが、本セッションでの実確認の結果これは不正確だった。旧ページ
(`oanda.com/forex-trading/analysis/open-position-ratios`)はHTTP 301で一般的な取引案内ページへ
リダイレクトされ該当コンテンツは見当たらない。旧開発者API
(`developer.oanda.com/rates/api/max/instruments/.../orderbook/`)はHTTP 404（廃止済み）。現行のOANDA
v20 REST API (`api-fxtrade.oanda.com`)はHTTP 401（IPブロックではなく認証エラー、取引口座+APIトークンが
必須）。よって本セッションからは取得不可であり、ユーザーがOANDA口座を開設しAPIトークンを取得しない
限り利用できない。`FACT_SCHEMA.md`の「未検証ソースからFactを作らない」原則、および憲章の「推測して
仕様を作らない」原則に照らし、ここで明示的に訂正する。

## ニュース・経済指標カレンダー

| source_id | 提供元 | 取得方法 | 対象期間 | 更新頻度 | 時間精度 | 利用条件 | 費用 | 到達性確認結果 | status |
|---|---|---|---|---|---|---|---|---|---|
| SRC-030 | ForexFactory 経済指標カレンダー | スクレイピングを想定していたが直接アクセス不可 | — | — | — | `robots.txt`にクロール禁止の明記はないが自動化アクセスをブロック | 無料（閲覧としては） | HTTP 403（アクセス拒否） | NOT_ACCESSIBLE |
| SRC-031 | Investing.com 経済指標カレンダー | 同上 | — | — | — | 利用規約でスクレイピング禁止が一般に知られている（本セッションでは条文未読了） | 無料（閲覧としては） | HTTP 403（アクセス拒否） | NOT_PERMITTED |
| SRC-032 | 一般ニュース（Bloomberg/Reuters/日経等の個別記事） | 未調査。著作権・利用規約上の制約が大きく本セッションでは調査対象外とした | — | — | — | 未確認（著作権法・各社規約の制約を受ける） | 有料契約が前提のことが多い | 到達性確認は未実施 | NOT_ACCESSIBLE |

**補足**: SRC-030/031は商用利用・再配布いずれも不可と想定（規約全文は未読了だが、スクレイピングを
前提とした業界的な既知の制約として扱う）。SRC-032は未調査。Phase 3設計時に、個別記事全文の保存では
なく「発表事実の時刻・内容の要約のみをFact化する」等の代替アプローチを検討する必要がある。

## まとめ（2026-07-31時点の到達性）

| status | 該当ソース |
|---|---|
| CONFIRMED_ACCESSIBLE（認証不要で実データ取得を確認済み） | SRC-010 (ECB), SRC-014 (BLS), SRC-016 (MOF、ページのみ), SRC-020 (CFTC), SRC-012 (BIS、ページのみ) |
| REQUIRES_REGISTRATION（無料登録・追加調査で取得可能な見込み） | SRC-001 (Yahoo Finance, 非公式), SRC-011 (FRED), SRC-013 (BOJ, URL要調査), SRC-015 (e-Stat) |
| NOT_ACCESSIBLE（本セッションからは取得不可） | SRC-002 (Rakuten, 手動連携のみ), SRC-021 (OANDA, 口座+トークン必須), SRC-032 (未調査) |
| NOT_PERMITTED（技術的ブロックまたは規約上不適切） | SRC-030 (ForexFactory), SRC-031 (Investing.com) |

## 今後の課題（Phase 3設計に持ち越す事項）

- 価格データはSRC-001（Yahoo Finance日次）とSRC-002（MT4手動連携、H1）のみで、いずれも分足レベルの
  連続的な自動取得ではない。ユーザーが挙げた「分足データ基盤」の要件を満たすには、追加の価格データ
  ソース調査（例: 証券会社API、有料ティックデータベンダー等）が必要。
- 経済指標の「予想値・結果値・改定値」を発表時刻付きで機械的に取得できる無料ソースは、本調査では
  確認できていない（BLS/e-Stat/FRED等は個別系列の実績値は取れるが、市場コンセンサス予想値までは
  含まない）。ForexFactory/Investing.com型のカレンダーはアクセス不可のため、代替ソースの追加調査が
  Phase 3着手前に必要。
- BOJ統計検索サイトは検索UI経由のため、機械的取得には別途URL/パラメータ調査（またはユーザーへの
  確認）が必要。

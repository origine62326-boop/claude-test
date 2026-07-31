# Fact Schema

**ステータス: 骨格のみ（2026-07-31作成）。Hypothesisの本格登録・検証開始はPhase 2/3（データ取得経路・
分足データ基盤の確定）まで凍結する。本文書はスキーマと運用ルールのみを定義し、この時点でFact IDの
実登録は行わない。**

## 位置づけ

`trading-system/RESEARCH_CHARTER.md` 第7節 Layer 1 (Data Acquisition) / Layer 2 (Data Quality) を、
「過去20年の経済ニュースと為替変動をFact/Observation/Hypothesisの3層で検証可能な範囲で網羅する」
という目標に向けて運用レベルへ落とし込んだものである。矛盾がある場合は`RESEARCH_CHARTER.md`を優先する。

## Factとは何か

**Fact = 特定のデータソースから、特定の時刻に、そのままの形で取得した生データ。解釈・加工・方向性の
判断を一切加えない。**

- Factは「何が起きたか」の記録であり、「それがどう為替に影響したか」は含まない（それはObservation/
  Hypothesisの役割）。
- Factは検証可能でなければならない。出典・取得方法・取得時刻・元データへの参照（URL、ファイル、
  APIレスポンス等）を必ず記録する。
- 取得できなかった項目は空欄にせず、`UNKNOWN` / `NOT_CONNECTED` / `NOT_AVAILABLE`のいずれかを明記する
  （憲章第6節・第8節の「データ不足ならWAIT」原則、および本レジストリ既存の`UNVERIFIED_OBSERVATION`
  タグ運用と整合させる）。
- Factソース自体は`research/governance/DATA_SOURCE_REGISTRY.md`（Phase 2）に登録されたソースからのみ
  取得する。未登録・未検証のソースからFactを起票しない。

## Fact ID体系

`F-###`（`FEATURE_REGISTRY.md`の`feature_id`である`F001`等とは名前空間を分ける。Factは特徴量ではなく
生データそのものであるため、混同を避けるためハイフン付きの`F-001`形式とする）。

## 必須フィールド

| フィールド | 説明 |
|---|---|
| fact_id | 一意のID（`F-001`形式） |
| category | 分類（例: price, economic_indicator, central_bank_statement, news, order_flow, intervention） |
| source_id | `DATA_SOURCE_REGISTRY.md`に登録済みの`source_id`への参照（必須。未登録ソースは使用不可） |
| retrieval_method | 取得方法（API名・エンドポイント・スクレイピング可否・手動取得等を具体的に） |
| retrieved_at | 実際に取得した時刻（タイムゾーン明記） |
| event_time | 事実そのものが発生・発表された時刻（タイムゾーン明記。取得時刻とは別概念） |
| raw_value | 取得した生の値・データへの参照（大きいデータは`trading-system/reports/raw/`等gitignore対象の実体を指し、checksumのみここに記録する運用を`DATASET_REGISTRY.md`と揃える） |
| revision_status | 経済指標等、後日改定される可能性があるデータについて、これが速報値/改定値/確定値のどれかを明記（`RESEARCH_CHARTER.md`第2節「未来情報を使用しない」原則に直結。改定値を発表前の時刻の判定に使ってはならない） |
| checksum | データ実体のハッシュ値（該当する場合） |
| missing_fields | 取得できなかった項目のリスト（`UNKNOWN`/`NOT_CONNECTED`/`NOT_AVAILABLE`のいずれかを付す） |
| license_terms | `DATA_SOURCE_REGISTRY.md`の利用条件への参照（再配布可否・商用利用可否を継承） |
| status | `DRAFT` / `VERIFIED` / `QUARANTINED`（`DATASET_REGISTRY.md`の`status`候補と概念を揃える） |
| created_at | 本レジストリへの登録日時 |

## 禁止事項

- Factに解釈・方向性判断・スコアを含めない（それらはObservation/Hypothesisの役割）。
- `DATA_SOURCE_REGISTRY.md`未登録のソースからFactを作らない。
- 未検証のニュース・噂・SNS投稿を、出典・時刻を検証しないままFactとして登録しない
  （検証できない場合は`category=news`かつ`status=QUARANTINED`、または登録自体を見送る）。
- Factの値を後から書き換えない（`RESEARCH_RULES.md`第10節「結果の改ざん禁止」と同じ扱い。訂正は
  取り消し線+追記）。

## 今後の実装（Phase 3以降、現時点では未着手）

- `research/facts/FACT_REGISTRY.md`（実データ台帳）は、Phase 3のデータ基盤設計確定後に作成する。
- 本ファイルはPhase 1時点ではスキーマ定義のみであり、実Fact登録は行わない。

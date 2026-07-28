# Evidence Registry

`trading-system/RESEARCH_CHARTER.md` 第3-4節に基づく、Evidence（信頼できる情報源によって支持される内容）の一覧管理表。

## 運用ルール

- Evidenceは、BIS・FRB・ECB・日本銀行・CFTC・査読論文・市場仕様・公式API仕様・公式ブローカー仕様・
  MQL4公式ドキュメントなど、確認可能な一次情報源に基づく場合のみ登録する。
- 既存のコード内コメントや開発中の会話での経験則を、根拠なくEvidenceへ昇格させない。
- 実験結果が良好だったことをEvidenceレベルの自動昇格理由にしない（憲章第19節）。
- 根拠が見つからない場合、またはEvidenceとHypothesisの判別がつかない場合は`U`または`H`として
  `HYPOTHESIS_REGISTRY.md`側で扱う。EvidenceとHypothesisを混同しない。
- 登録・更新はこの表への追記で行い、既存行を無断で書き換えない（変更履歴が追える形にする）。

## Evidenceレベル定義（憲章第4節）

| レベル | 定義 |
|---|---|
| E1 | 複数の査読研究、公的機関、公式仕様等で支持される |
| E2 | 一定の研究または一次資料で支持される |
| E3 | 実務・市場で使われるが、条件依存または根拠が限定的 |
| H | 検証前の仮説（Evidenceではない。`HYPOTHESIS_REGISTRY.md`で管理） |
| U | 根拠不足または分類不能 |

## 登録一覧

初版時点では、確認済みの一次情報源をまだ調査・登録していないため、テンプレート行のみとする。
既存EAのコメントや会話内の経験則をここへ推測で登録することはしない
（`research/audits/CURRENT_SYSTEM_AUDIT.md`参照。既存ロジックの根拠は現時点でH/Uに分類済み）。

| evidence_id | title | organization_or_author | source_type | publication_date | accessed_date | url_or_reference | summary | supported_claims | limitations | evidence_level | related_hypotheses | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (例) E001 | (例) BIS FX Market Structure | (例) Bank for International Settlements | (例) 公的機関レポート | | | | | | | | | DRAFT |

- 上記1行は記入例のプレースホルダーであり、実際のEvidenceとして採用されたものではない。
  実データを登録する際は新しい行を追加し、この例の行は削除せず残す（表の使い方の参照用）。

## status候補

- DRAFT: 出典確認中、未確定
- ACTIVE: 出典確認済み、参照可能
- SUPERSEDED: より新しい情報源に置き換えられた
- RETRACTED: 出典自体が撤回・無効化された

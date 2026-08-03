# Research Rules（研究基盤ガバナンスルール）

`trading-system/RESEARCH_CHARTER.md`を運用レベルに落とし込んだルール集。矛盾がある場合は
`RESEARCH_CHARTER.md`を優先する。

## 0. 共通ステータスタグ（2026-07-28, PR #8レビューで導入）

台帳・レジストリ・仕様書全体で、次の2つのタグを共通の目印として使う。新しい文書を追加する際も
同じ表記を使うこと（表記ゆれを作らない）。

- **`UNVERIFIED_OBSERVATION`**: 会話・スクリーンショット・手動確認等に基づく、パイプラインを
  通していない観察値。MT4 HTMLレポート・使用パラメータ・コードSHA・データ条件・ファイルハッシュが
  揃い、パイプラインを通して再現されるまで、正式なResearch ResultやEvidenceとして登録しない。
- **`IMPLEMENTED_ON_UNMERGED_BRANCH`**: 未マージブランチ上にのみ実装が存在する機能。mainに
  実装済みであるかのような表現（「実装済み」とだけ書く等）を禁止し、必ずsource_branchと
  merge_statusを併記する。

## 1. 事前登録 (Pre-registration)

- 実験を実行する前に、`EXPERIMENT_TEMPLATE.md`のtrain/validation/test期間、baseline、
  acceptance_criteria、rejection_criteriaを確定させる。
- 事前登録済みの内容は、結果を見た後に書き換えない。

## 2. データリーク禁止

- 特徴量の`availability_time`が判定時刻より後になっていないか、`FEATURE_REGISTRY.md`登録時に確認する。
- train/validation/testの期間は重複させない。
- 未来のニュース・経済指標・確定値（改定後の指標値等）を、発表前の時点の判定に使わない。

## 3. テストデータを見た後の最適化禁止

- テスト期間の結果を確認した後に、パラメータ・特徴量・期間を変更して再実行する行為（いわゆる
  "test set leakage" / "見てから調整") を禁止する。
- 調整したい場合は、新しい`experiment_id`を発行し、新しい（未使用の）test_periodを設定するか、
  既存test_periodを「もう使用済み」として記録した上で、validation側で再検討する。

## 4. 新experiment_id発行の原則

- 条件変更・パラメータ変更・期間変更を行う場合、既存の実験記録ファイルを上書きしない。
- 新しいexperiment_idで新規ファイルを作成し、変更理由と旧experiment_idへの参照を記載する。

## 5. EvidenceとHypothesisの分離

- Evidenceは信頼できる情報源（BIS/FRB/ECB/日銀/CFTC/査読論文/公式仕様等）に基づくものに限る。
- 社内・個人の経験則、会話内の推測、実装コード内のコメントは、それ単独ではEvidenceにならない。
- 実験結果が良好だったことをもってEvidenceレベルを自動的に引き上げない。あくまで
  「この仮説を支持する実験結果が得られた」という事実として`HYPOTHESIS_REGISTRY.md`や
  `EXPERIMENT_TEMPLATE.md`側に記録する。

## 6. WAIT許容

- データ不足・品質不良・判定不能な場合、Decision Engineは必ずWAITを返す。
- WAITは失敗ではなく正常な判断として扱い、「機会損失だからWAITを減らす」という理由だけで
  WAIT条件を緩めない。

## 7. 再現性

- 同一の入力（データバージョン・コードバージョン・パラメータ・乱数シード）に対しては、
  常に同一の結果が得られること。
- 非決定的な処理（並列処理の順序依存等）がある場合は、その旨を`limitations`に明記する。

## 8. Gitコミットハッシュ保存

- 各実験・モデル・意思決定ログには、実行時点のGitコミットSHA(`code_version` / `code_commit`)を
  記録する。

## 9. データバージョン保存

- 各実験・モデルには、使用したデータセットの`data_version`（`DATASET_REGISTRY.md`参照）を記録する。

## 10. 結果の改ざん禁止

- ログ・実験記録・レポートは追記型とし、都合の悪い結果を後から書き換えたり削除したりしない。
- 記録を訂正する必要がある場合は、取り消し線や「訂正: 」を付した追記の形で行い、元の記載を残す。

## 11. 追加してよいものの範囲（憲章第19節の運用ルール化）

Claude Codeおよび開発者は、次のもの以外を「勝てそうだから」「一般的だから」という理由だけで
追加してはならない。

- Evidence（出典付き）
- Hypothesis（検証計画付き）
- Experiment
- Data Quality Rule
- Reproducibility Rule
- Risk Constraint
- Fact（`governance/FACT_SCHEMA.md`準拠。出典・取得時刻・計算方法を伴わないものは不可）
- Observation（`governance/OBSERVATION_SCHEMA.md`準拠。決定的な計算のみ、方向性の解釈を含まないもの）
- Diagnostic Study（`diagnostics/DIAGNOSTIC_STUDY_REGISTRY.md`準拠。既存の確定済み実験データに対する
  原因分析であり、新しい売買ルール・Hypothesisを主張しないもの）
- 実装上必要な技術要件（バグ修正、依存関係更新等）

新しい特徴量・売買ルール・スコアリング重みを追加する場合は、必ず対応するHypothesis
（またはEvidence）を先に登録し、実装はその後に行う。

**[2026-07-31追加]** Fact/Observationは、それ自体が新しい売買ルールやスコアリング重みではないため
本ルールの対象に追加したが、`governance/HYPOTHESIS_POLICY.md`の凍結規定により、これらから新規
Hypothesisを登録・検証すること自体は現在凍結中（Phase 2/3のデータ基盤確定まで）。

## 12. 台帳ファイルの形式チェック（提案、未実装）

`EVIDENCE_REGISTRY.md` / `HYPOTHESIS_REGISTRY.md` / `research/experiments/*.md`等の台帳ファイルについて、
以下を機械的にチェックする軽量スクリプトを将来的に用意することを提案する。**このスクリプトは
今回のタスクでは実装しない（承認待ち）。**

想定するチェック内容（案）:

- ID形式（`E\d{3}`, `H\d{3}`, `EXP-\d{3}`等の正規表現一致）
- 同一ファイル内でのID重複
- 必須列の欠落（Markdownテーブルのヘッダーと各行の列数一致）
- Markdown内部リンク切れ（`research/`配下の相対リンクが実在ファイルを指しているか）
- `status`列の値が定義済みの候補（DRAFT/READY/RUNNING/...）に含まれるか

実装する場合は`trading-system/scripts/`配下に追加し、既存の`run_analysis.py`等と同様、
単体でも呼び出せるCLIとする案が既存の設計慣習（プロジェクトルートのCLAUDE.md）と整合的。
実装の要否・優先度は`GAP_ANALYSIS.md`のP2項目として記録し、承認後に着手する。

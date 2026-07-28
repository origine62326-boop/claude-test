# Research Report Template

実験や仮説検証のまとまりごとに、人間のレビュー向けにまとめる報告書のテンプレート。
`research/reports/REPORT-<連番>_<短い説明>.md` として保存する。このテンプレート自体は編集しない。

## 1. 概要

- report_id:
- 対象hypothesis_id:
- 対象experiment_id（複数可）:
- 作成日:
- 作成者/レビュー担当:

## 2. 目的

（この報告で何を明らかにしたいか）

## 3. 使用したEvidence / Hypothesis

| ID | 種別(Evidence/Hypothesis) | レベル | 概要 |
|---|---|---|---|

## 4. データ

| dataset_id | data_version | 期間 | quality_status | known_issues |
|---|---|---|---|---|

## 5. 手法

- ベースライン:
- 比較モデル/ルール:
- train/validation/test期間:
- ウォークフォワード定義:
- コスト前提(手数料/スプレッド/スリッページ):

## 6. 結果

### 6.1 予測評価

| 指標 | 値 |
|---|---|
| Direction Accuracy | |
| Balanced Accuracy | |
| Brier Score | |
| Log Loss | |
| Calibration | |
| Precision | |
| Recall | |
| Coverage | |
| WAIT率 | |

### 6.2 取引評価

| 指標 | 値 |
|---|---|
| Expectancy | |
| Net Profit | |
| Profit Factor | |
| Sharpe Ratio | |
| Sortino Ratio | |
| Maximum Drawdown | |
| Calmar Ratio | |
| Win Rate | |
| Average Win | |
| Average Loss | |
| Payoff Ratio | |
| Trade Count | |
| Turnover | |
| Cost Impact | |
| Slippage Impact | |

### 6.3 ベースラインとの比較

| ベースライン | 指標 | ベースライン値 | 本モデル値 | 差分 |
|---|---|---|---|---|

## 7. 頑健性・過学習チェック

- 複数期間での再現性:
- 感度分析結果:
- モンテカルロ結果（該当する場合）:
- データスヌーピング対策の確認:

## 8. 採用条件との照合（憲章第13節）

| 採用条件 | 満たすか | 根拠 |
|---|---|---|
| 時系列外データでも期待値がプラス | | |
| コスト込み | | |
| ウォークフォワードで再現 | | |
| ベースラインを上回る | | |
| 複数期間で再現 | | |
| 過学習の兆候が許容範囲 | | |
| 未来データリークなし | | |
| 実装再現性あり | | |
| データ・コードのバージョン固定 | | |
| 最低取引件数を満たす | | |
| リスク制約内 | | |
| 採用条件が事前登録済み | | |

## 9. 判定

- decision: ADOPTED / HOLD / REJECTED / INVALIDATED
- 理由:
- 限界・注意点:

## 10. 次のアクション

- 次に検証すべき仮説・実験:
- Evidence登録が必要な項目:
- 承認が必要な事項:

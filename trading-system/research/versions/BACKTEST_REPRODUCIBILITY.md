# Backtest Reproducibility Tracker

`RESEARCH_PLATFORM_ROADMAP.md` Phase R1 ステップ2〜4の橋渡しとなる台帳。「このコード版・このデータ版で、
この結果を再現できるか」を明示的に記録する。`RESEARCH_RULES.md`第8-9節（コード・データのバージョン保存）を
バックテスト単位で具体化したもの。

**本作業は台帳作成のみ。コード変更は一切行っていない。**

## 運用ルール

- `Status`は次のいずれかを使う: `REPRODUCIBLE`（コード・データを固定して再現できることを確認済み） /
  `NOT_REPRODUCIBLE_BLOCKED`（生データが画像等でしか存在せず、現状のコードでは再現不可能） /
  `NOT_ATTEMPTED`（未着手）。
- 「観察された数値が正しそうに見える」ことと「再現可能である」ことは別軸として扱う。前者は
  `UNVERIFIED_OBSERVATION`（`RESEARCH_RULES.md`第0節参照）、後者が本ファイルの対象。

## 一覧

| Component ID | 対象 | Version | Git Commit SHA | Branch | Status | Dependencies | Owner | Last Verified | Related Dataset | Related Experiment |
|---|---|---|---|---|---|---|---|---|---|---|
| BR001 | MT4レポートパーサーのfixtureベース再現性 — `pytest tests/ -q` | v0.2.0 (CC005/CC006) | `d1705dbbc3fd0295b11894b67e18a612ede39f1e` | `main` | REPRODUCIBLE | `tests/fixtures/`配下のサンプルレポート(日本語版・英語版) | 未割当 | **2026-07-28、本registry作成時に実行し36 passed(0.53s)を実測確認**（Python 3.11.15, pytest 9.1.1）。同一コード・同一fixtureで再実行すれば同一結果になることを確認済み | なし（`tests/fixtures/`は`DATASET_REGISTRY.md`未登録、下記備考参照） | なし |
| BR002 | DS002由来の観察値（本セッション会話内、2026-07-28共有スクリーンショット） — PF0.74・勝率29.89%・最大DD7.45%等 | 対象コード不明（CC001かCC002か、EA設定パラメータも未確認） | 不明（画像のみで特定不可） | 不明 | NOT_REPRODUCIBLE_BLOCKED | 実際の`.htm`レポート・使用パラメータ・コードSHA・データ条件・ファイルハッシュのいずれも未取得 | 未割当 | 2026-07-28（`DATASET_REGISTRY.md` DS002, `MODEL_REGISTRY.md` M001参照。再現の試みは未着手） | DS002 | なし |
| BR003 | v0.1.0リリースノート記載の参考値（写真ベース、2件） — `releases/v0.1.0/NOTES.md`「参考値」節 | v0.1.0 (CC001)？（`NOTES.md`に対象コード版の明記なし） | 不明 | 不明 | NOT_REPRODUCIBLE_BLOCKED | 同上。当時のスクリーンショット自体もリポジトリに保存されていない | 未割当 | 2026-07-28（`releases/v0.1.0/NOTES.md`に「本パイプラインを通していない参考値であり、正式な記録ではない」と当時から明記されていることを確認） | 未登録（`DATASET_REGISTRY.md`にDSとして未登録。本registry作成で新たに発見したギャップ、下記備考参照） | なし |

## 備考・発見事項

- **BR003は本台帳作成中に新たに見つけたギャップである。** `releases/v0.1.0/NOTES.md`には
  「開発中の会話でユーザーの手元のMT4スクリーンショットから確認した2回のバックテスト結果」
  （約2年間/初期証拠金1万円: 527取引・純利益+1,395.26・PF1.06・モデリング品質49.59%、および
  直近1年間/初期証拠金10万円: 192取引・純利益-1,583.42・PF0.76・モデリング品質57.30%）が
  参考値として記載されているが、これは`DATASET_REGISTRY.md`にDS-IDとして登録されていない。
  DS002（本セッションで共有された別のスクリーンショット）と同様に扱うべきだが、当時の画像自体が
  保存されていないため、DS002以上に再現性がない。DS-ID発行は本作業のスコープ外（今回はVERSION/
  CODE_COMPONENT/BACKTEST_REPRODUCIBILITYの3ファイル作成のみが依頼範囲）のため、次の承認事項として
  ここに記録するに留める。
- BR001（fixtureベースの再現性）と、BR002/BR003（実際のMT4バックテスト結果の再現性）は
  **別物である**。BR001が「REPRODUCIBLE」であることは、パーサーのコードが決定的に動作することを
  示すのみで、CC001/CC002のEAロジック自体に優位性があるかどうかとは無関係。
- `RESEARCH_PLATFORM_ROADMAP.md` Phase R1ステップ4「MT4バックテストの正式再現」は、BR002を
  `NOT_REPRODUCIBLE_BLOCKED`から`REPRODUCIBLE`（またはそれに準ずる正式なResearch Result化）へ
  移行させることが目標になる。ユーザーから実際の`.htm`レポートが提供され次第、この表を更新する。

# Backtest Reproducibility Tracker

`RESEARCH_PLATFORM_ROADMAP.md` Phase R1 ステップ2〜4の橋渡しとなる台帳。「このコード版・このデータ版で、
この結果を再現できるか」を明示的に記録する。`RESEARCH_RULES.md`第8-9節（コード・データのバージョン保存）を
バックテスト単位で具体化したもの。

**初版（2026-07-28、Phase R1ステップ2）作成時点では台帳作成のみでコード変更は行っていなかった。
同日のPhase R1ステップ4（本追記）で、実際に`.htm`レポートをパイプラインに通した結果、
`analysis/parse_mt4_report.py` / `analysis/parse_mt4_trades.py` / `analysis/common.py`の
複数のバグが判明したため、これらは修正した（詳細は下記BR002・備考参照）。EA(MQL4)・LSTM・
売買ロジックは変更していない。**

## 運用ルール

- `Status`は次のいずれかを使う: `REPRODUCIBLE`（コード・データを固定して再現できることを確認済み） /
  `NOT_REPRODUCIBLE_BLOCKED`（生データが画像等でしか存在せず、現状のコードでは再現不可能） /
  `NOT_ATTEMPTED`（未着手）。
- 「観察された数値が正しそうに見える」ことと「再現可能である」ことは別軸として扱う。前者は
  `UNVERIFIED_OBSERVATION`（`RESEARCH_RULES.md`第0節参照）、後者が本ファイルの対象。

## 一覧

| Component ID | 対象 | Version | Git Commit SHA | Branch | Status | Dependencies | Owner | Last Verified | Related Dataset | Related Experiment |
|---|---|---|---|---|---|---|---|---|---|---|
| BR001 | MT4レポートパーサーのfixtureベース再現性 — `pytest tests/ -q` | v0.2.1(本追記でのバグ修正後、未タグ) | `<PENDING_COMMIT_SHA>`（本追記をコミットした時点のSHA。コミット後に確定） | `claude/fx-research-platform-foundation-v0.1.0` | REPRODUCIBLE | `tests/fixtures/`配下のサンプルレポート(日本語版・英語版、本追記でmax_consecutive_wins/lossesの主値/副値順序を実データに合わせて修正) | 未割当 | **2026-07-28、コード修正後に再実行し36 passed(0.14秒)を実測確認**（Python 3.11.15, pytest 9.1.1）。修正前後で件数・結果に変化なし（fixtureの一部データ値は実データに合わせて修正済み） | なし（`tests/fixtures/`は`DATASET_REGISTRY.md`未登録、下記備考参照） | なし |
| BR002 | DS001由来の正式バックテスト結果（EXP-001, 実MT4レポート） — PF0.74・勝率29.89%・最大DD7.45%等 | 対象コード: main想定(CC001)だが未確認(`EXP-001`の`limitations`参照) | `72ac293f71131d53cd027a2786fbfaa2b3bed19d`(想定、未確認) | main(想定) | **REPRODUCIBLE**（2026-07-28、DS002からDS001へ格上げ） | `trading-system/reports/raw/EXP-001_run01_report.htm`(DS001, checksum記録済み)、修正後の`analysis/parse_mt4_report.py`・`analysis/parse_mt4_trades.py`・`analysis/common.py` | 未割当 | 2026-07-28、`python scripts/run_analysis.py reports/raw/EXP-001_run01_report.htm --trades reports/raw/EXP-001_run01_report.htm --run-id EXP-001_run01`を実行し、`reports/analyzed/EXP-001_run01_*.json`・`outputs/summaries/EXP-001_run01_summary_full.md`を生成・確認済み（生成物自体は`reports/`, `outputs/`の既存gitignore方針によりリポジトリには含まれない。再現するには同一checksumの`.htm`ファイルと同一コードが必要） | DS001 | EXP-001 (COMPLETED, HOLD) |
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
- `RESEARCH_PLATFORM_ROADMAP.md` Phase R1ステップ4「MT4バックテストの正式再現」は、2026-07-28に
  ユーザーから実際の`.htm`レポートの提供を受け、達成した。BR002は`NOT_REPRODUCIBLE_BLOCKED`から
  `REPRODUCIBLE`へ移行済み。

## 2026-07-28追記: 実データ投入で判明したパーサーのバグと修正内容

実際の`.htm`ファイル（RakutenSecurities-Demo, Build 1475, 日本語UI）を初めて`parse_mt4_report.py`に
通したところ、必須フィールドがほぼ全て`null`になった。原因調査の結果、以下のバグが判明し、
いずれも修正した（コミットSHAは本追記のコミット後に確定）。

1. **文字コード**: `parse_mt4_report.py`/`parse_mt4_trades.py`が`encoding="utf-8", errors="ignore"`で
   固定されており、日本語UIのMT4が出力するcp932(Shift-JIS)ファイルの日本語ラベルが読めず、
   数値フィールドが軒並み欠損していた。`common.py`に`read_html_file()`を新設し、UTF-8で失敗した
   場合にcp932へフォールバックする方式に変更
2. **ラベル表記ゆれ**: 実ファイルでは「純利益」ではなく「純益」、「プロフィットファクター」では
   なく末尾の長音符を欠く「プロフィットファクタ」が使われていた。パターンに追加・調整
3. **勝敗内訳セルのラベル誤り**: コードは「勝トレード」「敗トレード」を勝敗内訳セルのラベルと
   想定していたが、これは実際には「最大の勝トレード/平均の勝トレード」(largest/average win)の
   ラベルであり、勝敗内訳セルの実際のラベルは「勝率(%)」「負率(%)」だった。両対応する形に修正
4. **行修飾語の分離**: 一部のMT4ビルドでは「最大」「平均」が独立した`<td>`セル(colspan)として
   行全体にかかる形式で出現し、単一セル内一致を前提にした正規表現と噛み合わなかった。
   `_merge_row_qualifiers()`を新設し、直後2組のラベルセルへ結合してから照合する方式に変更
5. **連勝/連敗の主値・副値の逆転**: 「(金額)」セルは主値=回数・副値=金額、「(トレード数)」セルは
   主値=金額・副値=回数、という直感に反する並びが実際のMT4仕様だった（コード側は逆に想定していた）。
   構成ロジックを修正し、`tests/fixtures/`のサンプルデータも実仕様に合わせて修正
6. **操作履歴のcolspan省略**: 新規注文行(open)は損益・残高の2列が値未確定のため
   `<td colspan=2></td>`と1セルにまとめられて出力され、`_row_cells()`がcolspanを展開していなかった
   ため列数不足でopen行ごと除外されていた(open/close行のペアリングが全滅していた)。colspanを
   展開してから読む方式に修正

修正後、DS001に対して`total_trades`以下ほぼ全フィールドが正しく抽出され（欠損は`currency`のみ、
これはMT4レポート側に明示的な通貨コード欄が無いための既知の限界）、操作履歴側も184件中183件を
正しくopen/closeペアリングできることを確認した（残り1件はテスト終了時点で未決済のポジション、
正しく「未決済」として記録される）。

一方で、レポート公式値とトレード明細からの再計算値の間に小さな乖離が残っている
（`DATASET_REGISTRY.md` DS001の「known_issues」参照）。これは`scripts/run_analysis.py`が
自動検出する`_cross_check_mismatches`機能により可視化されており、原因は未特定のまま次の
未解決事項として記録する。

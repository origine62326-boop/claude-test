# Code Component Registry

`RESEARCH_PLATFORM_ROADMAP.md` Phase R1 ステップ2（EA・LSTM・解析コードのバージョン整理）の一次成果物。
既存EA・LSTM・解析パイプラインの各コンポーネントを、Gitコミット単位で固定点として記録する。

**本作業は台帳作成のみ。コード変更は一切行っていない。**

## 運用ルール

- `Git Commit SHA`は、そのコンポーネントの実体ファイルを**最後に変更した**コミットを記録する
  （ブランチの最新コミットではなく、当該パスに実際に差分があった最後のコミット）。
- `Status`は次のいずれかを使う: `ACTIVE`（mainで稼働中） / `IMPLEMENTED_ON_UNMERGED_BRANCH`
  （未マージブランチにのみ存在） / `FROZEN_BACKUP`（凍結済みバックアップ） /
  `SPEC_ONLY_NOT_IMPLEMENTED`（仕様のみでコード実装なし）。
- `Related Dataset` / `Related Experiment`は、`research/data/DATASET_REGISTRY.md` /
  `research/experiments/`のIDを参照する。まだ発行されていない場合は「なし」と明記する
  （存在しないIDを先回りして書かない）。
- この表の値は2026-07-28時点のGit履歴・ファイル内容の確認に基づく。以降の変更は
  この表を上書きするのではなく、`Last Verified`列を更新しつつ変更履歴が追える形で反映すること。

## コンポーネント一覧

| Component ID | コンポーネント名 | Version | Git Commit SHA | Branch | Status | Dependencies | Owner | Last Verified | Related Dataset | Related Experiment |
|---|---|---|---|---|---|---|---|---|---|---|
| CC001 | EA本体 (main, Phase1-4) — `trading-system/mt4/USDJPY_LowRisk_Trend_EA.mq4` | v0.1.0 | `72ac293f71131d53cd027a2786fbfaa2b3bed19d` | `main` | ACTIVE | MT4プラットフォームAPI(MQL4)のみ。外部ライブラリなし | 未割当（人間のレビュー担当者を今後指定） | 2026-07-28（本研究基盤の監査でコード全文を読み取り確認。ユーザー環境のMetaEditorでのコンパイル確認は`trading-system/CHANGELOG.md` v0.1.0時点の記載により0 errors/0 warnings済みと確認） | DS001(ACTIVE。ただしこのバックテストがCC001由来かCC002由来かは未確認、`EXP-001`参照), DS002(UNVERIFIED_OBSERVATION、参考のみ) | EXP-001 (COMPLETED, HOLD) |
| CC002 | EA本体 (Phase5-1, 未マージ) — 同ファイルの`claude/ea-v0.3.0-risk-management`版 | v0.3.0(開発中) | `13fc725a6a6e96fe2dd13af3970e88eeee821d73`（同ファイルへの最終変更。ブランチ先端は`1cea16ad8916e59dcb26a31c06a6f60546074ebe`） | `claude/ea-v0.3.0-risk-management`（**mainには未マージ**） | IMPLEMENTED_ON_UNMERGED_BRANCH | CC001をベースに日次損失上限・連敗制限ロジックを追加。CC001と機能的に分岐した状態 | 未割当 | 2026-07-28（本セッション内でコード全文を読み取り確認。コンパイル確認は`PENDING_USER_METAEDITOR_CONFIRMATION`、詳細は`configs/risk_limits.yaml`参照） | DS001(ACTIVE。可能性として使用された側、未確認), DS002(UNVERIFIED_OBSERVATION、パイプライン未検証) | なし（H002対象、未発行） |
| CC003 | レガシーEAバックアップ — `USDJPY_LowRisk_Trend_EA/`（リポジトリルート） | v0.1.0（凍結） | `0654a1ff5bde2fbd47b34fcaa6e080e1090559af` | `main` | FROZEN_BACKUP | なし（CC001のv0.1.0時点と同一内容と`LEGACY_BACKUP_NOTICE.md`に記載。本registry作成時点でバイト単位の再比較は実施していない） | 未割当 | 2026-07-28（`LEGACY_BACKUP_NOTICE.md`の記載内容を確認。ファイル内容自体の再比較は未実施） | なし | なし |
| CC004 | LSTM予測 — `fx_predict.py` + `fx_modules/` | バージョン番号なし（`trading-system`のvX.Y.Z体系の対象外） | `62aaf2dac71bac614a54942a0d68945afe38d30a` | `main` | ACTIVE | TensorFlow/Keras, Yahoo Finance chart API（外部、`query1.finance.yahoo.com`） | 未割当 | 2026-07-28（コード構成を確認。train/validation/test分割方法の精査は未実施、`GAP_ANALYSIS.md` P1-5参照） | DS003 | なし（M002登録のみ、experiment未発行） |
| CC005 | Python解析コード全般 — `trading-system/analysis/`, `trading-system/scripts/` | v0.2.1相当（未タグ。本追記で`parse_mt4_report.py`/`parse_mt4_trades.py`/`common.py`にバグ修正を実施） | `<PENDING_COMMIT_SHA>`（本追記のコミット後に確定） | `claude/fx-research-platform-foundation-v0.1.0` | ACTIVE | `beautifulsoup4>=4.12.0`, `lxml>=5.0.0`, `PyYAML>=6.0`, `pytest>=8.0.0`（`trading-system/requirements.txt`） | 未割当 | **2026-07-28、DS001(実MT4出力)で初めて検証。6件のバグを発見・修正し、修正後`pytest tests/ -q`で36 passed（0.14s）を再確認**（詳細は`BACKTEST_REPRODUCIBILITY.md`の追記参照） | DS001(ACTIVE) | EXP-001 |
| CC006 | MT4レポート解析（CC005のサブセット） — `analysis/parse_mt4_report.py`, `analysis/parse_mt4_trades.py` | v0.2.1相当（未タグ、本追記でバグ修正） | `<PENDING_COMMIT_SHA>`（本追記のコミット後に確定） | `claude/fx-research-platform-foundation-v0.1.0` | ACTIVE | CC005に同じ（beautifulsoup4, lxml） | 未割当 | **2026-07-28、DS001で実データ検証済み**。文字コード(cp932)対応、ラベル表記ゆれ対応、行修飾語分離対応、連勝/連敗主値副値の逆転修正、操作履歴colspan展開対応の6件を修正（`BACKTEST_REPRODUCIBILITY.md`参照）。旧バージョン(v0.2.0)は実MT4出力で機能しなかった点に注意 | DS001(ACTIVE) | EXP-001 |
| CC007 | Risk Engine | spec v1（`research/risk/RISK_ENGINE_SPEC.md`のみ、Python実装なし） | `7ffe91ae143fc3fd1d6b1424e5cc197a68c302c9`（仕様初版。直近改訂は本ブランチの`RISK_ENGINE_SPEC.md`更新コミット） | `claude/fx-research-platform-foundation-v0.1.0`（PR #8経由でmainへ反映済み。以降の改訂は本ブランチ側） | SPEC_ONLY_NOT_IMPLEMENTED | 仕様上CC001/CC002のロジックを参照。実装時は`DECISION_SCHEMA.md`(CC008)と連携する設計 | 未割当 | 該当なし（コード実装が存在しないため） | なし | なし |
| CC008 | Decision Engine | spec v1（`research/decisions/DECISION_SCHEMA.md`のみ、Python実装なし） | `7ffe91ae143fc3fd1d6b1424e5cc197a68c302c9` | `claude/fx-research-platform-foundation-v0.1.0`（PR #8経由でmainへ反映済み） | SPEC_ONLY_NOT_IMPLEMENTED | CC007（Risk Engineの出力を受け取る設計） | 未割当 | 該当なし | なし | なし |

## 備考

- CC001とCC002は同一ファイル（`USDJPY_LowRisk_Trend_EA.mq4`）の異なるブランチ上の版であり、
  「どちらが正か」を本registryが決めるものではない。両方の状態を記録することが目的であり、
  disposition（mainへのマージ可否等）は`RESEARCH_PLATFORM_ROADMAP.md` Phase R1ステップ3で
  人間が決定する。
- CC003（レガシーバックアップ）は`LEGACY_BACKUP_NOTICE.md`の記載を根拠にCC001のv0.1.0時点と
  同一内容としているが、本registry作成時点でバイト単位の`diff`による再確認は行っていない。
  厳密な同一性確認はPhase R1の追加タスク候補とする。
- CC007/CC008は「コンポーネント」として登録しているが、実体はドキュメント（仕様書）のみで
  実行可能なコードは存在しない。`Git Commit SHA`は仕様書ファイルが追加されたコミットを指す。

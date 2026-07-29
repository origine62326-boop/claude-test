# Version Registry

`trading-system`全体のプロジェクトバージョン（`vX.Y.Z`、`trading-system/CHANGELOG.md`の体系）と、
`CODE_COMPONENT_REGISTRY.md`の各コンポーネント(CC-ID)がどのバージョンでどう変化したかを紐づける台帳。
`CODE_COMPONENT_REGISTRY.md`が「コンポーネント単位」の固定点だとすれば、本ファイルは
「プロジェクトのリリース単位」の固定点にあたる。

**本作業は台帳作成のみ。コード変更は一切行っていない。**

## 運用ルール

- 行は`trading-system/CHANGELOG.md`に記載されたバージョンに1対1で対応させる。
- `Dependencies`列には、そのバージョンに含まれる`CODE_COMPONENT_REGISTRY.md`のComponent IDを列挙する。
- `fx_predict.py`/`fx_modules/`（LSTM, CC004）は`trading-system`のvX.Y.Zバージョン体系の対象外
  （リポジトリ直下の独立ツールであり、`trading-system/CHANGELOG.md`が管理する範囲ではない）。
  このため下表には現れず、`CODE_COMPONENT_REGISTRY.md`側でのみ管理する。この非対称性自体を
  ギャップとして`GAP_ANALYSIS.md`に追記候補とする（本作業では追記していない）。

## バージョン一覧

| Version ID | Version | Git Commit SHA | Branch | Status | Dependencies (含まれるComponent ID) | Owner | Last Verified | Related Dataset | Related Experiment |
|---|---|---|---|---|---|---|---|---|---|
| VR001 | v0.1.0 — 初回EA(Phase1-4) + 分析パイプライン初版 | `9564c22a0524bf4b2941a5c7d01a5d2d87d65dee`（"Establish version-controlled workflow, finalize v0.1.0"、`trading-system/releases/v0.1.0/NOTES.md`確定コミット。`git log`で実SHAを確認済み） | `main` | ACTIVE（現行mainの土台） | CC001（EA, Phase1-4）, CC003（レガシーバックアップ, 同時点で凍結）, CC005/CC006の初版（v0.1時点、v0.2.0で全面改訂前） | 未割当 | 2026-07-28（`releases/v0.1.0/NOTES.md`の記載内容を確認） | なし（`releases/v0.1.0/NOTES.md`に写真からの手動確認値が参考記載されているが、パイプライン未検証のため`DATASET_REGISTRY.md`には未登録） | なし |
| VR002 | v0.2.0 — 最小構成の解析パイプライン完成（EA本体には変更なし） | `d1705dbbc3fd0295b11894b67e18a612ede39f1e` | `main` | ACTIVE（現行main） | CC005, CC006（`parse_mt4_report.py`全面改訂等）。EA(CC001)には変更なし | 未割当 | 2026-07-28（`pytest tests/ -q`で36 passed(0.53s)を実測確認。実MT4出力ファイルでの検証は引き続き未実施） | なし | なし |
| VR003 | v0.3.0（開発中）— Phase5-1 日次損失上限・連敗制限 | `13fc725a6a6e96fe2dd13af3970e88eeee821d73`（ブランチ先端は`1cea16ad8916e59dcb26a31c06a6f60546074ebe`） | `claude/ea-v0.3.0-risk-management`（**mainには未マージ、未タグ・未リリース**） | IMPLEMENTED_ON_UNMERGED_BRANCH | CC002（EA, Phase5-1）。CC005/CC006（解析パイプライン）には変更なし | 未割当 | 2026-07-28（コード読み取り確認のみ。コンパイル確認は`PENDING_USER_METAEDITOR_CONFIRMATION`） | DS002(UNVERIFIED_OBSERVATION) | なし（H002対象、未発行） |
| VR004 | インフラ（バージョン番号なし）— GitHub Releases自動化 | `8183f5424d82d39fcd0da1dcfafac0ca30a67404`（最新。系譜: `bb29b92b221697fbae57ba2e978a046796c1a462`「Automate GitHub Release creation on tag push」→ `f69882513c90c5088dc39f4823bb7b3fb3ce8269`「Sync release.yml to main: add workflow_dispatch for manual testing」→ `8183f5424d82d39fcd0da1dcfafac0ca30a67404`「Sync release.yml to main: bump actions/checkout to v5」。いずれも`git log`で実SHAを確認済み） | `main` | ACTIVE | 対象外（製品バージョンではなくCI/CD設定） | 未割当 | 2026-07-28（ワークフローファイルの存在のみ確認。実行結果の再検証は本作業のスコープ外） | なし | なし |
| VR005 | research-platform-v0.1.0（本研究基盤の初版） | `7ffe91ae143fc3fd1d6b1424e5cc197a68c302c9`（PR #8初版）、最新は本ブランチのHEAD | `claude/fx-research-platform-foundation-v0.1.0`（PR #8経由でmainへマージ済み。以降の追加作業は本ブランチ上で継続） | ACTIVE | CC007, CC008（仕様のみ）。CC001-CC006には変更なし | 未割当 | 2026-07-28 | なし | なし |

## 備考

- VR001の`Git Commit SHA`は、`releases/v0.1.0/NOTES.md`が確定した時点のコミットを採用した
  （EA本体ファイル自体の最終変更はCC001の`72ac293`だが、バージョンとして「確定」したのはこの
  ワークフロー確立コミット）。バージョンの定義（ファイル変更時点か確定コミット時点か）は
  今後統一ルールを検討する余地がある。
- VR003（v0.3.0開発中）はPR #8がマージされた現時点でも**mainには未マージ**のままである
  （`CODE_COMPONENT_REGISTRY.md` CC002、`RISK_ENGINE_SPEC.md`参照）。本registryの作成時点
  （2026-07-28）でこの状態を記録したものであり、`RESEARCH_PLATFORM_ROADMAP.md` Phase R1
  ステップ3（未マージPhase 5-1の扱い決定）が完了した時点で本行を更新する。

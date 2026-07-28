# Risk Engine Spec

`trading-system/RESEARCH_CHARTER.md` 第15節に基づく、Risk Engineの仕様整理。本文書は**既存EAコードの
確認結果の整理のみ**であり、コード変更は行っていない。

## 重要な前提: ブランチの状態について

このドキュメントは `claude/fx-research-platform-foundation-v0.1.0` ブランチ（`main`起点）上で作成した。
`main`時点の`trading-system/mt4/USDJPY_LowRisk_Trend_EA.mq4`は**v0.1.0 (Phase1-4)** であり、
日次損失上限・連敗制限のロジックは未実装（入力パラメータの妥当性検証のみ、コード内コメントでは
「Phase 6で機能実装予定」となっている）。

一方、本セッション内の会話では、別ブランチ`claude/ea-v0.3.0-risk-management`（このブランチの基点である
`main`にはまだマージされていない）上で、日次損失上限・連敗制限のロジックが実装され、当該ブランチの
コード内では「Phase 5-1」と呼称されていることを確認済み。**つまり同じ機能が、ブランチによって
「Phase 6」（main）と「Phase 5-1」（未マージブランチ）という異なる呼称になっている状態**であり、
これ自体がフェーズ番号の整合性の問題として`GAP_ANALYSIS.md`に記録した。

以下は、未マージブランチ`claude/ea-v0.3.0-risk-management`上のコード（本セッション内で読み取り済み）を
根拠とした整理である。**このリポジトリ(main起点の本ブランチ)には該当コードは存在しない**点に注意。

### ステータス: `[IMPLEMENTED_ON_UNMERGED_BRANCH]`

以下の日次損失上限・連敗制限（Phase 5-1）に関する記述はすべて、次の状態を前提とする。
**mainに実装済みという意味では一切ない。** 各フィールドの定義・現在値は
`trading-system/configs/risk_limits.yaml`の該当コメントと同期させること。

| フィールド | 値 |
|---|---|
| source_branch | `claude/ea-v0.3.0-risk-management` |
| merge_status | `NOT_MERGED_TO_MAIN` |
| compile_status | `PENDING_USER_METAEDITOR_CONFIRMATION`（当該ブランチの`trading-system/CHANGELOG.md`に「コンパイル確認・バックテスト検証待ちのため未タグ・未リリース」「コンパイル確認はユーザー環境のMetaEditorで実施が必要（このセッションではMQL4コンパイラを実行できないため、手動コードレビューのみ実施）」と明記されている。0 errors/0 warningsの確認は**まだ得られていない**） |
| backtest_status | `UNVERIFIED_OBSERVATION`（会話内スクリーンショットのみ。`research/data/DATASET_REGISTRY.md` DS002参照。パイプライン未検証） |
| full_test_plan_status | `PARTIALLY_COMPLETE`（`trading-system/mt4/TEST_PLAN_PHASE5-1.md`全20項目中、コードレビュー代替5項目(#11, #13, #14, #15, #16)のみ確認済み。実機ストラテジーテスターでの確認は未実施） |
| demo_forward_status | `NOT_STARTED` |
| live_approval_status | `NOT_APPROVED`（`AllowLiveTrading=false`を維持） |

## Risk Engineが管理すべき項目（憲章第15節）と現状の対応

| 憲章が定める管理項目 | 現状 | 該当箇所（未マージブランチ） | 分類 |
|---|---|---|---|
| 最大日次損失 | `[IMPLEMENTED_ON_UNMERGED_BRANCH]` 実装あり（当日ラッチ方式、回復しても当日中は解除しない） | `IsDailyLossLimitReached()`, `MaxDailyLossPercent`入力 | B（Signal/Risk分離を前提に移植可能） |
| 1取引リスク | 実装あり（残高×RiskPercent%からロット逆算） | `CalculateLotSize()`, `RiskPercent`入力 | B |
| ロット | 実装あり（最小ロット単位切り捨て、ブローカー上限考慮） | `CalculateLotSizeForBalance()`, `NormalizeLotDown()` | B |
| 同時保有数 | 実装あり（Symbol+Magic一致で最大1ポジション固定） | `HasOpenPosition()` | B |
| 緊急停止 | 部分実装（SL/TP設定失敗時の緊急決済のみ。手動/外部トリガーによる全体緊急停止は未実装） | `EmergencyCloseUnprotectedPosition()` | C |
| 連続損失 | `[IMPLEMENTED_ON_UNMERGED_BRANCH]` 実装あり（当日の連敗数カウント、上限到達で当日エントリー停止） | `IsMaxConsecutiveLossesReached()`, `MaxConsecutiveLosses`入力 | B |
| 最大ドローダウン | 未実装（EA内でDD自体を監視・停止する仕組みはない。`configs/acceptance_criteria.yaml`側でバックテスト後の合否判定に`max_drawdown_pct`があるのみ） | (該当なし) | D |
| スプレッド上限 | 実装あり | `IsSpreadAcceptable()`, `MaxSpreadPips`入力 | B |
| 発注制約 | 実装あり（リトライ上限、TradeContext待機、リトライ可否のエラー分類） | `SafeOrderSend()`, `WaitForTradeContext()`, `IsRetryableError()` | B |
| 口座制約 | 実装あり（デモ/実口座判定、`AllowLiveTrading`既定false） | `IsLiveTradingBlocked()` | B |
| 稼働時間制約 | 未実装（入力パラメータ`TradingStartHour`等はmain・未マージブランチ双方に存在するが、`TryEnter()`から呼ばれておらず、実際のフィルタリングは行われていない） | (該当なし、Phase 7で実装予定とコード内コメントに記載) | D |
| データ品質エラー時停止 | 部分実装（`OrderSelect`失敗時に「判定不能→到達扱い(ブロック)」という安全側フォールバックあり。ただし本憲章が求める「データソース全般の品質チェック」の枠組みではない） | `GetTodayRealizedNet()`, `GetFloatingLossOnly()`のok引数パターン | C |

分類凡例（`CURRENT_SYSTEM_AUDIT.md`と同一基準）:
A=そのまま流用可能 / B=修正すれば流用可能 / C=仮説として再検証が必要 / D=根拠不足（未実装） / E=重複・レガシー

## Signal EngineとRisk Engineの分離状況

現状のEA実装は、Signal（`CheckBuySignal()` / `CheckSellSignal()`のエントリー方向判定）とRisk
（日次損失・連敗・スプレッド・口座種別等の各種ブロック判定）が**同一の`TryEnter()`関数内で
逐次呼び出される形で密結合**している。憲章第15節が求める「Signal EngineとRisk Engineの完全分離」
（Signalの方向予測をRisk Engineが書き換えない、独立した`ALLOW`/`REDUCE`/`BLOCK`/`EMERGENCY_STOP`の
出力を持つ）は、現状のMQL4実装では構造的に満たされていない。

これは現行EAの設計が悪いという意味ではなく、MQL4の1ファイル・1EA構成という制約下で安全側に倒した
実装になっている、という事実の記録である。将来Decision Engine/Risk Engineを研究基盤側（Python）に
実装する場合は、このMQL4実装のロジックを「仕様」として参照しつつ、`DECISION_SCHEMA.md`が定める
分離構造で再実装することを想定する（Phase R7-R8、`RESEARCH_PLATFORM_ROADMAP.md`参照）。

## 未確定・要検討事項

- 最大ドローダウンによる自動停止（EA内でのリアルタイムDD監視）は、憲章が求める項目だが現状未実装。
  実装するかどうか、するとすればどのタイミング（Phase R8のRisk Engine統合時）で検討するかは未確定。
- `TradingStartHour`等の稼働時間制約は、main・未マージブランチ双方で入力パラメータのみ存在し未接続。
  H003（経済指標フィルター）とは別に、単純な時間帯制約についても既存の未接続入力をどう扱うか
  （EA側で先に接続するか、研究基盤側でF103として検証してから接続するか）は未確定。
- 本文書のRisk Engine整理は、未マージブランチのコード内容を前提にしている。当該ブランチがmainへ
  マージされた場合、本文書を更新する必要がある（現時点ではその予定・時期は未確定）。

# CHANGELOG

## v0.1.0 (Phase 1〜4 実装)

### 実装済み

- 入力パラメータ一式の宣言、`OnInit`での入力値検証（範囲外の値はエラー表示のうえEA停止）
- Symbol検証（USDJPY系サフィックスを許容、紛らわしい別シンボルは拒否）／時間足検証（H1固定）
- 20/75/200EMAによるトレンド判定（確定足shift=1基準）
- ADXフィルター
- 押し目/戻り判定：`PullbackLookbackBars`以内で最も新しいEMA接触足のみを候補とし、
  深く逸脱していた場合は古い足へフォールバックせずシグナル不成立とする方式
- ATRベースの損切り幅計算（Min/Max/ブローカーStopLevelでクランプ）、RewardRiskRatioによる利確幅計算
- リスク%からのロット自動計算（TickValue/TickSize/LotStep/MinLot/MaxLotを考慮、必ず切り捨て丸め）
- `SafeOrderSend`/`SafeOrderModify`/`SafeOrderClose`（リトライ上限付き、TradeContextBusy対応、IsTradeAllowed確認）
- ECNフォールバック（`EnableECNFallback`、初期値false。ストップ設定関連エラーのみ対象、Modify失敗時は緊急決済）
- 実口座誤稼働防止（`AllowLiveTrading`、初期値false。DEMO許可/REAL禁止/判定不能は安全側で禁止、
  ストラテジーテスター内は許可）
- `LastBarTime`のGlobalVariable永続化（EA再起動時も同一確定足からの重複発注を防止、初回セット時は
  直近確定足を処理済み扱いにして過去シグナルを追いかけない）
- Phase3ロット計算検証ログ（残高10万円×3パターンのシミュレーション出力）

### 未実装（今後のPhaseで対応）

- 建値移動・トレーリングストップ（Phase 5）
- 日次損失上限（DailyRiskReferenceBalance）・連敗制限・日次リセット（Phase 6）
- 取引時間フィルター・曜日フィルター・金曜クローズ（Phase 7）
- スプレッドフィルター強化・FreezeLevel考慮のOrderModify強化（Phase 8）
- README_JP.md / BACKTEST_GUIDE_JP.md / PARAMETERS_JP.md（Phase 9）

### 既知の制限

- 日次損失上限・連敗制限が未実装のため、v0.1をデモ口座で稼働させる場合は取引時間や損失を手動で監視すること
- 取引時間フィルターが未実装のため、流動性の低い時間帯でもシグナルが成立すればエントリーする
- コンパイル確認はユーザー環境のMetaEditorで実施が必要（開発セッション内ではMQL4コンパイラを実行できないため、
  手動コードレビューのみ実施）

//+------------------------------------------------------------------+
//| USDJPY_LowRisk_Trend_EA.mq4                                      |
//| USD/JPY H1 順張り（押し目買い・戻り売り）低リスク検証用EA         |
//| v0.3.0(開発中) - Phase 1〜4 + Phase 5-1(日次損失上限・連敗制限)   |
//|                                                                    |
//| 重要:                                                              |
//|  - バックテストおよびデモ口座での検証を目的とする                  |
//|  - 実口座での自動売買は AllowLiveTrading=true を明示しない限り     |
//|    ブロックされる（詳細はコード内 IsLiveTradingBlocked 参照）      |
//|  - ナンピン・マーチンゲール・両建て・グリッド取引は一切行わない    |
//|  - 未確定足（shift=0）は判定に一切使用しない                       |
//+------------------------------------------------------------------+
#property copyright "USDJPY_LowRisk_Trend_EA"
// #property version はMQL5 Marketの書式規約(xxx.yyy形式、メジャー1以上)に合わせた表記。
// 開発進捗としてのバージョン(v0.3.0開発中)はtrading-system/CHANGELOG.mdで管理する。
#property version   "1.00"
#property strict
#property description "USD/JPY H1 押し目買い・戻り売り 低リスク順張りEA (v0.3.0開発中: Phase1-4 + Phase5-1)"

#include <stdlib.mqh>   // ErrorDescription() を使用するため

//====================================================================
// 入力パラメータ
//====================================================================

// --- 識別 ---
input int    MagicNumber            = 20260714; // このEA専用のマジックナンバー

// --- 資金管理 ---
input double RiskPercent            = 0.5;   // 1トレードの許容損失（口座残高に対する%, 0.1〜1.0）
input double MaximumLot             = 1.0;   // 発注ロットの上限

// --- 日次/連敗制限 (Phase 5-1で実装) ---
input double MaxDailyLossPercent    = 2.0;   // 1日の許容損失（口座残高に対する%）。到達後は当日中ラッチされ回復しても解除しない
input int    MaxConsecutiveLosses   = 3;     // 最大許容連敗数（当日限定でカウント）

// --- トレンド判定EMA ---
input int    FastEMAPeriod          = 20;    // 短期EMA期間
input int    MiddleEMAPeriod        = 75;    // 中期EMA期間
input int    LongEMAPeriod          = 200;   // 長期EMA期間

// --- ATR / 損切り・利確 ---
input int    ATRPeriod              = 14;    // ATR期間
input double ATRStopMultiplier      = 1.5;   // 損切り幅 = ATR × この倍率
input double RewardRiskRatio        = 2.0;   // 利確幅 = 損切り幅 × この倍率
input double MinStopLossPips        = 5.0;   // 最低損切り幅(pips)
input double MaxStopLossPips        = 100.0; // 最大損切り幅(pips)

// --- ADXフィルター ---
input int    ADXPeriod              = 14;    // ADX期間
input double MinimumADX             = 20.0;  // エントリーに必要な最低ADX値

// --- 押し目/戻り判定 ---
input int    PullbackLookbackBars   = 5;     // 接触判定に遡る本数(shift=1を含む)
input double PullbackTolerancePips  = 3.0;   // 20EMA中心の接触許容帯(±pips)
input double MaxPullbackPenetrationPips = 10.0; // 最新接触足がこの幅を超えて逸脱していたら不成立
input bool   RequireSignalCandleDirection = false; // trueならシグナル確定足の陽線/陰線方向も要求

// --- スプレッド / 発注実行 ---
input double MaxSpreadPips          = 3.0;   // この値を超えるスプレッドでは新規注文しない
input int    Slippage               = 30;    // 許容スリッページ(points単位。5桁/3桁ブローカーではpipsの1/10)
input int    OrderRetryCount        = 3;     // 発注/変更/決済のリトライ上限回数
input int    OrderRetryDelayMs      = 150;   // リトライ間の待機時間(ミリ秒)
input bool   EnableECNFallback      = false; // ECN方式でSL/TP同時指定不可の場合のフォールバックを許可するか

// --- 取引時間フィルター (Phase 7で機能実装予定。現状は入力値検証のみ) ---
input int    TradingStartHour       = 8;     // 取引開始時刻(サーバー時間, 時)
input int    TradingStartMinute     = 0;     // 取引開始時刻(分)
input int    TradingEndHour         = 22;    // 取引終了時刻(サーバー時間, 時)
input int    TradingEndMinute       = 0;     // 取引終了時刻(分)
input int    FridayStopHour         = 21;    // 金曜日この時刻以降は新規注文停止(サーバー時間)

// --- 建値移動・トレーリング (Phase 5で機能実装予定。現状は入力値検証のみ) ---
input bool   EnableBreakEven        = true;  // 建値移動を有効にするか
input double BreakEvenAtR           = 1.0;   // 含み益がこのR到達で建値付近へ移動
input double BreakEvenOffsetPips    = 2.0;   // 建値からのオフセット(pips)
input bool   EnableTrailingStop     = false; // トレーリングストップを有効にするか(初期無効)
input bool   EnableFridayClose      = false; // 週末を跨ぐポジションを金曜に決済するか
input int    FridayCloseHour        = 23;    // 金曜決済時刻(サーバー時間)

// --- 売買方向 ---
input bool   EnableLong             = true;  // 買いエントリーを許可するか
input bool   EnableShort            = true;  // 売りエントリーを許可するか

// --- 実口座誤稼働防止 ---
input bool   AllowLiveTrading       = false; // 実口座での新規発注を許可するか(初期値は必ずfalse)

//====================================================================
// グローバル状態
//====================================================================
bool     g_initializedOk = false;
datetime g_lastProcessedBarTime = 0;

// --- Phase5-1: 日次損失上限・連敗制限用 ---
const double PNL_EPSILON = 0.01; // 損益0とみなす許容誤差(口座通貨単位)

int    g_dailyRefEstablishedDate = 0;   // DailyRiskReferenceBalanceが確立済みのServerDateInt。0=未確立、-1=確立失敗(判定不能)
double g_dailyRiskReferenceBalance = 0.0;

bool   g_dailyLossLimitLogged        = false; // 当日分の「到達しました」ログを出力済みか
bool   g_consecutiveLossLimitLogged  = false;
int    g_logSuppressionDate          = 0;     // 上記2フラグをリセットすべきかの判定に使うServerDateInt

//====================================================================
// ログ補助
//====================================================================
void LogInfo(string msg)  { Print("[INFO] ", msg); }
void LogError(string msg) { Print("[ERROR] ", msg); }

//====================================================================
// pips / points 変換 (3桁・5桁ブローカー対応)
//====================================================================
int PipDigitsAdjust()
{
   if(Digits==3 || Digits==5) return 10;
   return 1;
}

double PipSize()
{
   return Point * PipDigitsAdjust();
}

double PipsToPrice(double pips)
{
   return pips * PipSize();
}

double PriceToPips(double priceDistance)
{
   return priceDistance / PipSize();
}

//====================================================================
// Symbol / Period 検証
//====================================================================
bool ValidateSymbol()
{
   string sym = Symbol();
   string prefix = "USDJPY";
   int prefixLen = StringLen(prefix);

   if(StringSubstr(sym, 0, prefixLen) != prefix)
   {
      LogError("このEAはUSDJPY専用です。現在のSymbol: " + sym);
      return false;
   }

   if(StringLen(sym) > prefixLen)
   {
      ushort ch = StringGetCharacter(sym, prefixLen);
      bool isAlnum = ((ch>=48 && ch<=57) || (ch>=65 && ch<=90) || (ch>=97 && ch<=122));
      if(isAlnum)
      {
         LogError("USDJPYと紛らわしい別シンボルの可能性があるため停止します: " + sym);
         return false;
      }
   }
   return true;
}

bool ValidatePeriod()
{
   if(Period() != PERIOD_H1)
   {
      LogError("このEAはH1足専用です。現在の時間足コード: " + IntegerToString(Period()));
      return false;
   }
   return true;
}

//====================================================================
// 入力パラメータ検証
//====================================================================
bool ValidateInputs()
{
   bool ok = true;

   if(MagicNumber<=0) { LogError("MagicNumberは正の整数にしてください"); ok=false; }

   if(RiskPercent<0.1 || RiskPercent>1.0) { LogError("RiskPercentは0.1〜1.0の範囲にしてください: " + DoubleToString(RiskPercent,2)); ok=false; }
   if(MaximumLot<=0) { LogError("MaximumLotは正の値にしてください"); ok=false; }

   if(MaxDailyLossPercent<=0 || MaxDailyLossPercent>100) { LogError("MaxDailyLossPercentが不正です: " + DoubleToString(MaxDailyLossPercent,2)); ok=false; }
   if(MaxConsecutiveLosses<1) { LogError("MaxConsecutiveLossesは1以上にしてください"); ok=false; }

   if(FastEMAPeriod<1 || MiddleEMAPeriod<1 || LongEMAPeriod<1)
   { LogError("EMA期間は1以上にしてください"); ok=false; }
   if(!(FastEMAPeriod<MiddleEMAPeriod && MiddleEMAPeriod<LongEMAPeriod))
   { LogError("EMA期間は FastEMAPeriod < MiddleEMAPeriod < LongEMAPeriod の関係にしてください"); ok=false; }

   if(ATRPeriod<1) { LogError("ATRPeriodは1以上にしてください"); ok=false; }
   if(ATRStopMultiplier<=0) { LogError("ATRStopMultiplierは正の値にしてください"); ok=false; }
   if(RewardRiskRatio<=0) { LogError("RewardRiskRatioは正の値にしてください"); ok=false; }
   if(MinStopLossPips<0) { LogError("MinStopLossPipsは0以上にしてください"); ok=false; }
   if(MaxStopLossPips<=MinStopLossPips) { LogError("MaxStopLossPipsはMinStopLossPipsより大きくしてください"); ok=false; }

   if(ADXPeriod<1) { LogError("ADXPeriodは1以上にしてください"); ok=false; }
   if(MinimumADX<0 || MinimumADX>100) { LogError("MinimumADXは0〜100の範囲にしてください"); ok=false; }

   if(PullbackLookbackBars<1) { LogError("PullbackLookbackBarsは1以上にしてください"); ok=false; }
   if(PullbackTolerancePips<0) { LogError("PullbackTolerancePipsは0以上にしてください"); ok=false; }
   if(MaxPullbackPenetrationPips<0) { LogError("MaxPullbackPenetrationPipsは0以上にしてください"); ok=false; }

   if(MaxSpreadPips<=0) { LogError("MaxSpreadPipsは正の値にしてください"); ok=false; }
   if(Slippage<0) { LogError("Slippageは0以上にしてください"); ok=false; }
   if(OrderRetryCount<1) { LogError("OrderRetryCountは1以上にしてください"); ok=false; }
   if(OrderRetryDelayMs<0) { LogError("OrderRetryDelayMsは0以上にしてください"); ok=false; }

   if(TradingStartHour<0 || TradingStartHour>23) { LogError("TradingStartHourは0〜23にしてください"); ok=false; }
   if(TradingEndHour<0   || TradingEndHour>23)   { LogError("TradingEndHourは0〜23にしてください"); ok=false; }
   if(TradingStartMinute<0 || TradingStartMinute>59) { LogError("TradingStartMinuteは0〜59にしてください"); ok=false; }
   if(TradingEndMinute<0   || TradingEndMinute>59)   { LogError("TradingEndMinuteは0〜59にしてください"); ok=false; }
   if(FridayStopHour<0 || FridayStopHour>23) { LogError("FridayStopHourは0〜23にしてください"); ok=false; }
   if(FridayCloseHour<0 || FridayCloseHour>23) { LogError("FridayCloseHourは0〜23にしてください"); ok=false; }

   if(BreakEvenAtR<=0) { LogError("BreakEvenAtRは正の値にしてください"); ok=false; }
   if(BreakEvenOffsetPips<0) { LogError("BreakEvenOffsetPipsは0以上にしてください"); ok=false; }

   if(!EnableLong && !EnableShort) { LogError("EnableLongとEnableShortの両方をfalseにはできません"); ok=false; }

   return ok;
}

//====================================================================
// サーバー日付ユーティリティ
//====================================================================
int ServerDateInt(datetime t)
{
   return TimeYear(t) * 10000 + TimeMonth(t) * 100 + TimeDay(t);
}

//====================================================================
// GlobalVariable命名規則
//
// EA識別子・口座番号・接続サーバー名・Symbol・MagicNumberから求めた
// FNV-1a 32bitハッシュ(8桁16進)を使い、"LRT_<hash>_<用途名>" の形式にする。
// AccountServer()はブローカーによって長さが不定(20文字を超える場合もある)ため、
// 素の文字列連結ではなくハッシュ化することで63文字制限に確実に収める。
//
// 注意: FNV-1a 32bitは理論上衝突がゼロではない。「衝突しない保証」ではなく、
// 代表的な組み合わせ(口座番号・サーバー名・Symbol・MagicNumberを変えたケース)で
// 異なるハッシュ値になることを確認する、という実用上の位置づけとする。
//
// ストラテジーテスター実行中は"LRT_"の代わりに"TST_"を使い、実運用の値と
// 完全に分離する。
//====================================================================
uint SimpleHash32(string text)
{
   uint hash = 2166136261; // FNV-1a オフセット基底
   int len = StringLen(text);
   for(int i=0; i<len; i++)
   {
      hash = hash ^ (uint)StringGetCharacter(text, i);
      hash = hash * 16777619; // FNV素数(32bitで自然にラップアラウンドする)
   }
   return hash;
}

string GVHashHex()
{
   string keyBase = AccountServer() + "|" + IntegerToString(AccountNumber()) + "|" +
                    Symbol() + "|" + IntegerToString(MagicNumber);
   return StringFormat("%08X", SimpleHash32(keyBase));
}

string GVName(string suffix)
{
   string prefix = IsTesting() ? "TST" : "LRT";
   return prefix + "_" + GVHashHex() + "_" + suffix;
}

// ストラテジーテスター実行時、前回テストで残ったGlobalVariable(TST_プレフィックス)を
// 今回のテストへ持ち越さないよう、OnInitの冒頭で必ずクリアする。実運用(LRT_)側は対象外。
void ClearTesterGlobalVariablesIfNeeded()
{
   if(!IsTesting()) return;

   string prefix = "TST_" + GVHashHex() + "_";
   int deleted = GlobalVariablesDeleteAll(prefix);
   LogInfo("テスター用GlobalVariableをクリアしました prefix=" + prefix + " 削除件数=" + IntegerToString(deleted));
}

//====================================================================
// LastBarTime の永続化 (GlobalVariable)
//====================================================================
void InitLastProcessedBarTime()
{
   string name = GVName("LastBarTime");
   if(GlobalVariableCheck(name))
   {
      g_lastProcessedBarTime = (datetime)GlobalVariableGet(name);
      LogInfo("LastBarTimeを復元しました: " + TimeToString(g_lastProcessedBarTime));
   }
   else
   {
      // 初回セット時: 直近の確定足をすでに処理済みとして扱う
      // → セット直後にすでに完成しているシグナルを追いかけて発注しないようにする
      g_lastProcessedBarTime = iTime(Symbol(), PERIOD_H1, 1);
      GlobalVariableSet(name, (double)g_lastProcessedBarTime);
      LogInfo("LastBarTimeを初回初期化しました(直近確定足を処理済み扱い): " + TimeToString(g_lastProcessedBarTime));
   }
}

bool IsNewConfirmedBar()
{
   datetime currentBarTime = iTime(Symbol(), PERIOD_H1, 1);
   return (currentBarTime != g_lastProcessedBarTime);
}

void MarkBarProcessed()
{
   g_lastProcessedBarTime = iTime(Symbol(), PERIOD_H1, 1);
   GlobalVariableSet(GVName("LastBarTime"), (double)g_lastProcessedBarTime);
}

//====================================================================
// ヒストリー本数チェック
//====================================================================
bool HasSufficientHistory()
{
   int longestPeriod = LongEMAPeriod;
   if(ATRPeriod > longestPeriod) longestPeriod = ATRPeriod;
   if(ADXPeriod > longestPeriod) longestPeriod = ADXPeriod;
   int required = longestPeriod + PullbackLookbackBars + 10;
   int available = iBars(Symbol(), PERIOD_H1);
   if(available < required)
   {
      LogInfo("ヒストリー本数不足のためシグナル判定をスキップ (bars=" + IntegerToString(available) +
              " required=" + IntegerToString(required) + ")");
      return false;
   }
   return true;
}

//====================================================================
// トレンド判定 (EMA)
//====================================================================
double EMAValue(int period, int shift)
{
   return iMA(Symbol(), PERIOD_H1, period, 0, MODE_EMA, PRICE_CLOSE, shift);
}

// 1=上昇トレンド, -1=下降トレンド, 0=トレンドなし
int GetTrendDirection(int shift)
{
   double fast  = EMAValue(FastEMAPeriod,   shift);
   double mid   = EMAValue(MiddleEMAPeriod, shift);
   double slow  = EMAValue(LongEMAPeriod,   shift);
   double close = iClose(Symbol(), PERIOD_H1, shift);

   if(close>slow && fast>mid && mid>slow) return 1;
   if(close<slow && fast<mid && mid<slow) return -1;
   return 0;
}

//====================================================================
// ADXフィルター
//====================================================================
double GetADX(int shift)
{
   return iADX(Symbol(), PERIOD_H1, ADXPeriod, PRICE_CLOSE, MODE_MAIN, shift);
}

bool IsADXStrongEnough(int shift)
{
   return GetADX(shift) >= MinimumADX;
}

//====================================================================
// 押し目/戻り判定
// 仕様: PullbackLookbackBars以内で「最も新しい」EMA接触足のみを候補とする。
//       候補が深く逸脱していた場合、古い接触足へのフォールバックは行わず
//       シグナル全体を不成立とする。
//====================================================================
bool BarTouchesEMABand(int shift, double emaValue, double tolerancePips)
{
   double tol = PipsToPrice(tolerancePips);
   double high = iHigh(Symbol(), PERIOD_H1, shift);
   double low  = iLow(Symbol(), PERIOD_H1, shift);
   double bandTop    = emaValue + tol;
   double bandBottom = emaValue - tol;
   return (high >= bandBottom && low <= bandTop); // 値幅と許容帯が重なっているか
}

// direction: 1=買い(押し目, ローソクが下にどれだけ逸脱したか) / -1=売り(戻り, 上にどれだけ逸脱したか)
double CalculatePenetrationPips(int direction, int shift, double emaValue)
{
   double penetrationPrice = 0.0;
   if(direction==1)
   {
      double low = iLow(Symbol(), PERIOD_H1, shift);
      penetrationPrice = emaValue - low;
   }
   else
   {
      double high = iHigh(Symbol(), PERIOD_H1, shift);
      penetrationPrice = high - emaValue;
   }
   if(penetrationPrice<0) penetrationPrice = 0;
   return PriceToPips(penetrationPrice);
}

// PullbackLookbackBars以内で最も新しい接触足を探す(方向に依存しない)
bool FindNewestPullbackContact(int &contactShift)
{
   for(int shift=1; shift<=PullbackLookbackBars; shift++)
   {
      double emaValue = EMAValue(FastEMAPeriod, shift);
      if(BarTouchesEMABand(shift, emaValue, PullbackTolerancePips))
      {
         contactShift = shift;
         return true;
      }
   }
   contactShift = -1;
   return false;
}

bool IsRecoveryConfirmed(int direction)
{
   double close1 = iClose(Symbol(), PERIOD_H1, 1);
   double ema1   = EMAValue(FastEMAPeriod, 1);
   if(direction==1) return close1 > ema1;
   return close1 < ema1;
}

bool IsSignalCandleDirectionOk(int direction)
{
   if(!RequireSignalCandleDirection) return true;
   double open1  = iOpen(Symbol(), PERIOD_H1, 1);
   double close1 = iClose(Symbol(), PERIOD_H1, 1);
   if(direction==1) return close1 > open1; // 陽線を要求
   return close1 < open1;                  // 陰線を要求
}

bool CheckPullbackSignal(int direction)
{
   int contactShift;
   if(!FindNewestPullbackContact(contactShift))
      return false; // 接触足が見つからない → 不成立

   double emaAtContact = EMAValue(FastEMAPeriod, contactShift);
   double penetration = CalculatePenetrationPips(direction, contactShift, emaAtContact);

   if(penetration > MaxPullbackPenetrationPips)
      return false; // 最新接触足が深すぎる → 古い足へフォールバックせず不成立とする

   if(!IsRecoveryConfirmed(direction)) return false;
   if(!IsSignalCandleDirectionOk(direction)) return false;

   return true;
}

//====================================================================
// 買い/売りシグナル統合判定 (すべて確定足shift=1基準)
//====================================================================
bool CheckBuySignal()
{
   if(!EnableLong) return false;
   if(GetTrendDirection(1) != 1) return false;
   if(!IsADXStrongEnough(1)) return false;
   if(!CheckPullbackSignal(1)) return false;
   return true;
}

bool CheckSellSignal()
{
   if(!EnableShort) return false;
   if(GetTrendDirection(1) != -1) return false;
   if(!IsADXStrongEnough(1)) return false;
   if(!CheckPullbackSignal(-1)) return false;
   return true;
}

//====================================================================
// スプレッドフィルター
//====================================================================
double GetCurrentSpreadPips()
{
   double spreadPoints = MarketInfo(Symbol(), MODE_SPREAD);
   return spreadPoints / PipDigitsAdjust();
}

bool IsSpreadAcceptable()
{
   return GetCurrentSpreadPips() <= MaxSpreadPips;
}

//====================================================================
// 取引時間フィルター (Phase7)
//
// TradingStartHour:TradingStartMinute 〜 TradingEndHour:TradingEndMinute
// (サーバー時間)を許可範囲とする。開始>終了の場合は日をまたぐ範囲として扱う
// (例: 開始22:00・終了15:00なら「22:00〜翌15:00」が許可範囲)。
//====================================================================
bool IsWithinTradingHours()
{
   int nowMinutes   = TimeHour(TimeCurrent())*60 + TimeMinute(TimeCurrent());
   int startMinutes = TradingStartHour*60 + TradingStartMinute;
   int endMinutes   = TradingEndHour*60 + TradingEndMinute;

   if(startMinutes <= endMinutes)
      return (nowMinutes >= startMinutes && nowMinutes < endMinutes);
   else
      return (nowMinutes >= startMinutes || nowMinutes < endMinutes);
}

//====================================================================
// ポジション確認 (Symbol + MagicNumber 一致のみ)
//====================================================================
bool HasOpenPosition()
{
   for(int i=OrdersTotal()-1; i>=0; i--)
   {
      if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
      if(OrderSymbol()!=Symbol() || OrderMagicNumber()!=MagicNumber) continue;
      if(OrderType()==OP_BUY || OrderType()==OP_SELL) return true;
   }
   return false;
}

//====================================================================
// 日次損失上限・連敗制限 (Phase 5-1)
//
// 対象は Symbol()+MagicNumber 一致・OrderType が OP_BUY/OP_SELL の取引のみ。
// これにより手動取引・他EA・入出金(OP_BALANCE/OP_CREDIT)は自動的に除外される。
// 判定できない場合は必ず「到達扱い(=新規エントリー禁止)」に倒す。
// 新規エントリーのみを止め、既存ポジションの管理には一切影響しない。
//====================================================================

bool IsValidPositiveNumber(double v) { return (MathIsValidNumber(v) && v > 0.0); }

// --- 当日確定損益 / 保有中の含み損 ---

// 当日決済分(Symbol+Magic一致)の Profit+Commission+Swap 合計。
// 日付不一致の履歴に遭遇してもBREAKせず、全履歴を走査してフィルタする
// (MODE_HISTORYの並び順は決済時刻順を保証しないため)。
double GetTodayRealizedNet(bool &ok)
{
   ok = true;
   int today = ServerDateInt(TimeCurrent());
   double sum = 0.0;
   int total = OrdersHistoryTotal();

   for(int i=0; i<total; i++)
   {
      if(!OrderSelect(i, SELECT_BY_POS, MODE_HISTORY))
      {
         ok = false;
         return 0.0;
      }
      if(OrderSymbol()!=Symbol() || OrderMagicNumber()!=MagicNumber) continue;
      if(OrderType()!=OP_BUY && OrderType()!=OP_SELL) continue;
      if(ServerDateInt(OrderCloseTime())!=today) continue;

      sum += OrderProfit() + OrderCommission() + OrderSwap();
   }

   return sum;
}

// 保有中(Symbol+Magic一致)の含み損のみを注文ごとに判定して合算する。
// 全注文のfloating損益を先に合算してからMINを取るのではなく、個別の注文が
// 損失(<0)である場合のみ加算する。これにより、あるポジションの含み益で
// 別ポジションの含み損を相殺しない(安全側)。
double GetFloatingLossOnly(bool &ok)
{
   ok = true;
   double sum = 0.0;
   int total = OrdersTotal();

   for(int i=0; i<total; i++)
   {
      if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
      {
         ok = false;
         return 0.0;
      }
      if(OrderSymbol()!=Symbol() || OrderMagicNumber()!=MagicNumber) continue;
      if(OrderType()!=OP_BUY && OrderType()!=OP_SELL) continue;

      double orderNet = OrderProfit() + OrderCommission() + OrderSwap();
      if(orderNet < 0.0) sum += orderNet;
   }

   return sum;
}

// --- DailyRiskReferenceBalance ---

// 当日開始時点の残高を確立/復元する。
// 同日中にGlobalVariableへ確立済みの値があれば、それをそのまま復元する
// (再計算しない=EA再起動やIsDailyLossLimitReached()の繰り返し呼び出しで
// 基準がぶれないようにするため)。
void EstablishOrRestoreDailyRiskReferenceBalance()
{
   int today = ServerDateInt(TimeCurrent());

   bool dateExists    = GlobalVariableCheck(GVName("DailyRefDate"));
   bool balanceExists = GlobalVariableCheck(GVName("DailyRefBalance"));

   if(dateExists && balanceExists)
   {
      double storedDate = 0.0, storedBalance = 0.0;
      bool dateOk = GlobalVariableGet(GVName("DailyRefDate"), storedDate);
      bool balOk  = GlobalVariableGet(GVName("DailyRefBalance"), storedBalance);

      if(dateOk && balOk && ((int)storedDate)==today && IsValidPositiveNumber(storedBalance))
      {
         g_dailyRiskReferenceBalance = storedBalance;
         g_dailyRefEstablishedDate = today;
         LogInfo("DailyRiskReferenceBalanceを復元しました: " + DoubleToString(storedBalance, 2));
         return;
      }
      // 値が今日の日付でない、または不正 → 下の再確立処理へ進む
   }

   bool ok = false;
   double eaPnLToday = GetTodayRealizedNet(ok);
   if(!ok)
   {
      g_dailyRefEstablishedDate = -1; // 判定不能
      LogError("当日確定損益を取得できないため、DailyRiskReferenceBalanceを確立できません");
      return;
   }

   double reconstructed = AccountBalance() - eaPnLToday;
   double candidate = MathMin(AccountBalance(), reconstructed);

   if(!IsValidPositiveNumber(candidate))
   {
      g_dailyRefEstablishedDate = -1; // 判定不能
      LogError("DailyRiskReferenceBalanceの計算結果が不正です: " + DoubleToString(candidate, 2));
      return;
   }

   datetime setBalTime  = GlobalVariableSet(GVName("DailyRefBalance"), candidate);
   datetime setDateTime = GlobalVariableSet(GVName("DailyRefDate"), (double)today);

   if(setBalTime==0 || setDateTime==0)
   {
      g_dailyRefEstablishedDate = -1; // 保存に失敗した場合も未確立扱い(安全側)
      LogError("DailyRiskReferenceBalanceのGlobalVariable保存に失敗しました");
      return;
   }

   g_dailyRiskReferenceBalance = candidate;
   g_dailyRefEstablishedDate = today;

   if(eaPnLToday != 0.0)
      LogInfo("日中初回起動のため近似計算を使用: eaPnLToday=" + DoubleToString(eaPnLToday, 2) +
              " 採用値=" + DoubleToString(candidate, 2));
   else
      LogInfo("DailyRiskReferenceBalanceを確立しました: " + DoubleToString(candidate, 2));
}

// IsDailyLossLimitReached()の判定前に必ず呼び出す。メモリ上の確立済み日付と
// サーバー日付が異なる場合のみ再確立処理を行う(OnInit時の確立だけに頼らない)。
void EnsureDailyRiskReferenceBalance()
{
   int today = ServerDateInt(TimeCurrent());
   if(g_dailyRefEstablishedDate == today) return;
   EstablishOrRestoreDailyRiskReferenceBalance();
}

// --- 日次損失上限(当日ラッチ方式) ---
//
// 一度到達したら、その後に含み損が回復しても同一サーバー日付中はブロックし
// 続ける(動的解除しない)。到達日をGlobalVariableへ保存し、EA再起動後も
// 同日なら復元する。翌サーバー日付になった時点で、保存されている日付と
// 一致しなくなるため自然に解除される。
bool IsDailyLossLimitReached()
{
   EnsureDailyRiskReferenceBalance();
   int today = ServerDateInt(TimeCurrent());

   if(g_dailyRefEstablishedDate != today)
      return true; // 基準残高が未確立=判定不能 → 安全側

   double lockDateStored = 0.0;
   bool lockOk = GlobalVariableGet(GVName("DailyLossLockDate"), lockDateStored);
   if(lockOk && ((int)lockDateStored)==today)
      return true; // 既に当日到達済み(ラッチ)。回復していても継続してブロック

   bool netOk = false, floatOk = false;
   double todayRealizedNet = GetTodayRealizedNet(netOk);
   if(!netOk) return true;
   double floatingLossOnly = GetFloatingLossOnly(floatOk);
   if(!floatOk) return true;

   double dailyNet = todayRealizedNet + floatingLossOnly;
   double dailyLossAmount = MathMax(-dailyNet, 0.0);
   double dailyLossLimitAmount = g_dailyRiskReferenceBalance * MaxDailyLossPercent / 100.0;

   if(dailyLossAmount >= dailyLossLimitAmount)
   {
      datetime setResult = GlobalVariableSet(GVName("DailyLossLockDate"), (double)today);
      if(setResult==0)
         LogError("日次損失ラッチの保存に失敗しました。今回の判定は到達扱いを継続しますが、"
                  "再起動すると当日中でも復元できない可能性があります");
      return true;
   }

   return false;
}

// --- 最大連敗制限 ---

struct TradeRecord
{
   datetime closeTime;
   int      ticket;
   double   pnl;
};

// 当日決済分(Symbol+Magic一致)を全履歴から収集する。走査順やMT4内部の
// 並び順を一切仮定しない(日付不一致でもBREAKせずCONTINUEする)。
int CollectTodayClosedTrades(TradeRecord &records[], bool &ok)
{
   ok = true;
   int today = ServerDateInt(TimeCurrent());
   int total = OrdersHistoryTotal();
   int count = 0;

   ArrayResize(records, 0);

   for(int i=0; i<total; i++)
   {
      if(!OrderSelect(i, SELECT_BY_POS, MODE_HISTORY))
      {
         ok = false;
         ArrayResize(records, 0);
         return 0;
      }
      if(OrderSymbol()!=Symbol() || OrderMagicNumber()!=MagicNumber) continue;
      if(OrderType()!=OP_BUY && OrderType()!=OP_SELL) continue;
      if(ServerDateInt(OrderCloseTime())!=today) continue;

      count++;
      ArrayResize(records, count);
      records[count-1].closeTime = OrderCloseTime();
      records[count-1].ticket    = OrderTicket();
      records[count-1].pnl       = OrderProfit() + OrderCommission() + OrderSwap();
   }

   return count;
}

// aがbより「新しいか同時刻でticketが大きい」場合にtrue(=降順で先に来るべき)
bool IsNewerOrEqual(const TradeRecord &a, const TradeRecord &b)
{
   if(a.closeTime != b.closeTime) return a.closeTime > b.closeTime;
   return a.ticket >= b.ticket;
}

// OrderCloseTime降順、同時刻はOrderTicket降順で明示ソートする(挿入ソート)。
// 対象は当日分のみのため件数は少なく、計算量は問題にならない。
void SortTradeRecordsDesc(TradeRecord &records[])
{
   int n = ArraySize(records);
   for(int i=1; i<n; i++)
   {
      TradeRecord key = records[i];
      int j = i - 1;
      while(j>=0 && !IsNewerOrEqual(records[j], key))
      {
         records[j+1] = records[j];
         j--;
      }
      records[j+1] = key;
   }
}

// 新しい順に確認し、損失が連続した本数を数える。勝ちで打ち切り(=0リセットと
// 同義)。ほぼ0(|pnl|<=PNL_EPSILON)の取引は無視し、カウントも途切れさせない。
int GetConsecutiveLossCount(bool &ok)
{
   TradeRecord records[];
   int n = CollectTodayClosedTrades(records, ok);
   if(!ok) return 0;

   SortTradeRecordsDesc(records);

   int count = 0;
   for(int i=0; i<n; i++)
   {
      double pnl = records[i].pnl;
      if(pnl < -PNL_EPSILON) count++;
      else if(pnl > PNL_EPSILON) break;
      // else: ほぼ0 → 無視して次へ
   }
   return count;
}

// 連敗数は「新規エントリーが止まっている間は新しい決済が発生しない」ため、
// 一度到達すると日付が変わるまで再計算しても値が変わらない。日次損失上限とは
// 異なり、専用のラッチ(GlobalVariable)は不要と判断した。
bool IsMaxConsecutiveLossesReached()
{
   bool ok = false;
   int count = GetConsecutiveLossCount(ok);
   if(!ok) return true; // 判定不能 → 安全側
   return count >= MaxConsecutiveLosses;
}

// --- ログ抑制(2つの独立フラグ、サーバー日付変更後の最初のtickで解除) ---
void UpdateLogSuppressionState()
{
   int today = ServerDateInt(TimeCurrent());
   if(g_logSuppressionDate != today)
   {
      g_dailyLossLimitLogged = false;
      g_consecutiveLossLimitLogged = false;
      g_logSuppressionDate = today;
   }
}

//====================================================================
// 実口座誤稼働防止
//====================================================================
string TradeModeToString(int mode)
{
   switch(mode)
   {
      case ACCOUNT_TRADE_MODE_DEMO:    return "DEMO";
      case ACCOUNT_TRADE_MODE_CONTEST: return "CONTEST";
      case ACCOUNT_TRADE_MODE_REAL:    return "REAL";
      default:                         return "UNKNOWN";
   }
}

bool IsLiveTradingBlocked()
{
   if(IsTesting())
   {
      LogInfo("ストラテジーテスター内のため口座種別判定をスキップし、注文を許可します");
      return false;
   }

   ENUM_ACCOUNT_TRADE_MODE mode = (ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE);
   string modeStr = TradeModeToString(mode);
   LogInfo("口座種別判定: " + modeStr);

   if(AllowLiveTrading)
   {
      LogInfo("AllowLiveTrading=true のため口座種別に関わらず新規注文を許可します(自己責任)");
      return false;
   }

   if(mode==ACCOUNT_TRADE_MODE_DEMO) return false; // デモと明確に判定 → 許可
   if(mode==ACCOUNT_TRADE_MODE_REAL) return true;  // 実口座と判定 → 禁止

   // CONTESTや取得不能(UNKNOWN)等、想定外の結果は安全側として禁止
   return true;
}

//====================================================================
// ATRベースSL/TP計算
//====================================================================
double GetATRPips(int shift)
{
   double atrPrice = iATR(Symbol(), PERIOD_H1, ATRPeriod, shift);
   return PriceToPips(atrPrice);
}

double CalculateStopLossPips()
{
   double slPips = GetATRPips(1) * ATRStopMultiplier;

   double stopLevelPoints = MarketInfo(Symbol(), MODE_STOPLEVEL);
   double stopLevelPips = stopLevelPoints / PipDigitsAdjust();

   double minPips = MathMax(MinStopLossPips, stopLevelPips);
   if(slPips < minPips) slPips = minPips;
   if(slPips > MaxStopLossPips) slPips = MaxStopLossPips;

   return slPips;
}

double CalculateTakeProfitPips(double slPips)
{
   return slPips * RewardRiskRatio;
}

double CalculateStopLossPrice(int direction, double entryPrice, double slPips)
{
   double dist = PipsToPrice(slPips);
   if(direction==1) return NormalizeDouble(entryPrice - dist, Digits);
   return NormalizeDouble(entryPrice + dist, Digits);
}

double CalculateTakeProfitPrice(int direction, double entryPrice, double tpPips)
{
   double dist = PipsToPrice(tpPips);
   if(direction==1) return NormalizeDouble(entryPrice + dist, Digits);
   return NormalizeDouble(entryPrice - dist, Digits);
}

//====================================================================
// ロット自動計算
//
// 計算根拠:
//   許容損失額(円等) = 口座残高 × RiskPercent%
//   1pipあたりの損益(ロット1.0換算) = TickValue × (PipSize / TickSize)
//   必要ロット(丸め前) = 許容損失額 / (SLpips × 1pipあたりの損益)
//   丸め後ロット = FLOOR(丸め前ロット / LotStep) × LotStep  ※必ず切り捨て
//   丸め後ロットが最小ロット未満、または計算に使う値が不正な場合は
//   0.0 を返し、呼び出し側で「発注しない」と判定させる。
//====================================================================
double GetTickValuePerPip()
{
   double tickValue = MarketInfo(Symbol(), MODE_TICKVALUE);
   double tickSize  = MarketInfo(Symbol(), MODE_TICKSIZE);
   if(tickSize<=0 || tickValue<=0) return 0.0; // 異常値ガード
   return tickValue * (PipSize() / tickSize);
}

double NormalizeLotDown(double rawLot)
{
   double lotStep = MarketInfo(Symbol(), MODE_LOTSTEP);
   double minLot  = MarketInfo(Symbol(), MODE_MINLOT);
   if(lotStep<=0 || rawLot<=0) return 0.0;

   double steps = MathFloor(rawLot / lotStep);
   double lot = steps * lotStep;
   if(lot < minLot) return 0.0; // 最小ロット未満は発注しない扱い(0.0)
   return lot;
}

// balance/riskPercentを引数化し、Phase3の仮想ケース検証にも使い回せるようにする
double CalculateLotSizeForBalance(double balance, double riskPercent, double slPips)
{
   if(slPips<=0 || balance<=0 || riskPercent<=0) return 0.0;

   double riskAmount = balance * (riskPercent / 100.0);
   double pipValue = GetTickValuePerPip();
   if(pipValue<=0) return 0.0;

   double rawLot = riskAmount / (slPips * pipValue);
   double lot = NormalizeLotDown(rawLot);

   double brokerMaxLot = MarketInfo(Symbol(), MODE_MAXLOT);
   double maxLot = MathMin(MaximumLot, brokerMaxLot);
   if(lot > maxLot) lot = NormalizeLotDown(maxLot);

   return lot;
}

double CalculateLotSize(double slPips)
{
   double lot = CalculateLotSizeForBalance(AccountBalance(), RiskPercent, slPips);
   if(lot<=0)
   {
      LogInfo("CalculateLotSize: 計算結果が最小ロット未満、または計算不能のため発注しません");
      return 0.0;
   }

   double marginCheck = AccountFreeMarginCheck(Symbol(), OP_BUY, lot);
   if(marginCheck<0)
   {
      LogError("CalculateLotSize: 証拠金不足のため発注しません lot=" + DoubleToString(lot,2));
      return 0.0;
   }

   return lot;
}

//====================================================================
// Phase3 検証: ロット計算の仮想ケースログ出力
//====================================================================
void LotTestCase(double balance, double riskPercent, double slPips, string label)
{
   double allowedLoss = balance * (riskPercent / 100.0);
   double pipValue = GetTickValuePerPip();
   double tickValue = MarketInfo(Symbol(), MODE_TICKVALUE);
   double tickSize  = MarketInfo(Symbol(), MODE_TICKSIZE);
   double minLot    = MarketInfo(Symbol(), MODE_MINLOT);
   double lotStep   = MarketInfo(Symbol(), MODE_LOTSTEP);
   double maxLotBroker = MarketInfo(Symbol(), MODE_MAXLOT);

   double rawLot = (pipValue>0) ? allowedLoss/(slPips*pipValue) : 0.0;
   double lot = CalculateLotSizeForBalance(balance, riskPercent, slPips);

   LogInfo("[LotCalcTest] " + label + ": 残高=" + DoubleToString(balance,0) +
           " Risk=" + DoubleToString(riskPercent,2) + "% SL=" + DoubleToString(slPips,1) + "pips");
   LogInfo("  許容損失額(理論)=" + DoubleToString(allowedLoss,2));
   LogInfo("  TickValue=" + DoubleToString(tickValue,5) + " TickSize=" + DoubleToString(tickSize,5) +
           " MinLot=" + DoubleToString(minLot,2) + " LotStep=" + DoubleToString(lotStep,2) +
           " MaxLot(broker)=" + DoubleToString(maxLotBroker,2));
   LogInfo("  1pipあたり損益(ロット1.0換算)=" + DoubleToString(pipValue,4));
   LogInfo("  丸め前ロット=" + DoubleToString(rawLot,4) + "  丸め後ロット=" + DoubleToString(lot,2));

   if(lot<=0)
   {
      LogInfo("  → 丸め後ロットが最小ロット未満のため、このケースでは発注しない判定");
   }
   else
   {
      double actualLossAtSL = lot * slPips * pipValue;
      double diff = allowedLoss - actualLossAtSL;
      LogInfo("  丸め後ロットでの理論上の最大損失額=" + DoubleToString(actualLossAtSL,2));
      LogInfo("  差額(許容額-実損失額)=" + DoubleToString(diff,2) + " (0以上であることを確認)");
   }
}

void RunLotCalculationTests()
{
   LogInfo("===== ロット計算検証ログ (Phase3) =====");
   LotTestCase(100000, 0.5, 10, "ケースA");
   LotTestCase(100000, 0.5, 30, "ケースB");
   LotTestCase(100000, 1.0, 50, "ケースC");
   LogInfo("===== ロット計算検証ログ終了 =====");
}

//====================================================================
// エラー分類 (リトライ対象かどうか)
//====================================================================
bool IsRetryableError(int err)
{
   switch(err)
   {
      case ERR_REQUOTE:
      case ERR_OFF_QUOTES:
      case ERR_PRICE_CHANGED:
      case ERR_TRADE_CONTEXT_BUSY:
      case ERR_TRADE_TIMEOUT:
      case ERR_SERVER_BUSY:
      case ERR_NO_CONNECTION:
      case ERR_TOO_FREQUENT_REQUESTS:
         return true;
      default:
         return false;
   }
}

bool IsStopRelatedError(int err)
{
   return (err==ERR_INVALID_STOPS);
}

//====================================================================
// TradeContextBusy待機 (無限待機・無限リトライ禁止)
//====================================================================
bool WaitForTradeContext()
{
   for(int i=0; i<OrderRetryCount; i++)
   {
      if(IsStopped()) return false;
      if(!IsTradeContextBusy()) return true;
      Sleep(OrderRetryDelayMs);
      if(IsStopped()) return false;
   }
   return !IsTradeContextBusy();
}

//====================================================================
// 安全な発注/変更/決済ラッパー (リトライ上限付き、重複注文を防ぐ)
//====================================================================
int SafeOrderSend(int direction, double lot, double sl, double tp, string comment, int &lastError)
{
   lastError = 0;
   int cmd = (direction==1) ? OP_BUY : OP_SELL;

   for(int attempt=1; attempt<=OrderRetryCount; attempt++)
   {
      if(IsStopped()) { lastError = -1; return -1; }

      if(!IsTradeAllowed())
      {
         LogError("IsTradeAllowed()=false のため発注を中止します");
         lastError = -1;
         return -1;
      }

      if(!WaitForTradeContext())
      {
         LogError("TradeContext解放待ちがタイムアウトしました");
         lastError = -1;
         return -1;
      }

      RefreshRates();
      double execPrice = (cmd==OP_BUY) ? Ask : Bid;

      int ticket = OrderSend(Symbol(), cmd, lot, execPrice, Slippage, sl, tp, comment, MagicNumber, 0,
                              (cmd==OP_BUY) ? clrBlue : clrRed);

      if(ticket>=0)
      {
         LogInfo("発注成功: ticket=" + IntegerToString(ticket) + " attempt=" + IntegerToString(attempt) +
                 " price=" + DoubleToString(execPrice,Digits) + " lot=" + DoubleToString(lot,2));
         return ticket;
      }

      lastError = GetLastError();
      LogError("OrderSend失敗 attempt=" + IntegerToString(attempt) + "/" + IntegerToString(OrderRetryCount) +
               " error=" + IntegerToString(lastError) + " " + ErrorDescription(lastError));

      if(!IsRetryableError(lastError))
      {
         LogError("リトライ対象外のエラーのため中止します");
         return -1;
      }

      Sleep(OrderRetryDelayMs);
   }

   LogError("リトライ上限に達したため発注を諦めます");
   return -1;
}

bool SafeOrderModify(int ticket, double price, double sl, double tp)
{
   for(int attempt=1; attempt<=OrderRetryCount; attempt++)
   {
      if(IsStopped()) return false;
      if(!WaitForTradeContext()) return false;

      bool ok = OrderModify(ticket, price, sl, tp, 0, clrYellow);
      if(ok) return true;

      int err = GetLastError();
      LogError("OrderModify失敗 ticket=" + IntegerToString(ticket) + " attempt=" + IntegerToString(attempt) +
               " error=" + IntegerToString(err) + " " + ErrorDescription(err));

      if(!IsRetryableError(err)) return false;
      Sleep(OrderRetryDelayMs);
   }
   return false;
}

bool SafeOrderClose(int ticket)
{
   if(!OrderSelect(ticket, SELECT_BY_TICKET))
   {
      LogError("SafeOrderClose: OrderSelect失敗 ticket=" + IntegerToString(ticket));
      return false;
   }
   double lots = OrderLots();
   int cmd = OrderType();

   for(int attempt=1; attempt<=OrderRetryCount; attempt++)
   {
      if(IsStopped()) return false;
      if(!WaitForTradeContext()) return false;

      RefreshRates();
      double closePrice = (cmd==OP_BUY) ? Bid : Ask;

      bool ok = OrderClose(ticket, lots, closePrice, Slippage, clrOrange);
      if(ok) return true;

      int err = GetLastError();
      LogError("OrderClose失敗 ticket=" + IntegerToString(ticket) + " attempt=" + IntegerToString(attempt) +
               " error=" + IntegerToString(err) + " " + ErrorDescription(err));

      if(!IsRetryableError(err)) return false;
      Sleep(OrderRetryDelayMs);
   }
   return false;
}

void EmergencyCloseUnprotectedPosition(int ticket)
{
   if(!SafeOrderClose(ticket))
      LogError("緊急決済にも失敗しました。手動確認が必要です ticket=" + IntegerToString(ticket));
   else
      LogInfo("損切り未設定ポジションを緊急決済しました ticket=" + IntegerToString(ticket));
}

//====================================================================
// ECNフォールバック付きポジションオープン
//====================================================================
int OpenPositionWithECNFallback(int direction, double lot, double sl, double tp, string comment)
{
   int err = 0;
   int ticket = SafeOrderSend(direction, lot, sl, tp, comment, err);
   if(ticket>=0) return ticket;

   if(!EnableECNFallback)          return -1;
   if(!IsStopRelatedError(err))    return -1; // ストップ設定関連以外のエラーではフォールバックしない

   LogInfo("ECNフォールバック: SL/TPなしで再送信します");
   int err2 = 0;
   ticket = SafeOrderSend(direction, lot, 0, 0, comment, err2);
   if(ticket<0)
   {
      LogError("ECNフォールバック発注も失敗しました");
      return -1;
   }

   if(!OrderSelect(ticket, SELECT_BY_TICKET))
   {
      LogError("ECNフォールバック: 発注後のOrderSelectに失敗しました ticket=" + IntegerToString(ticket));
      return ticket;
   }

   bool modifyOk = SafeOrderModify(ticket, OrderOpenPrice(), sl, tp);
   if(!modifyOk)
   {
      LogError("ECNフォールバック: SL/TP設定に失敗。損切りなしポジションを放置しないため緊急決済します");
      EmergencyCloseUnprotectedPosition(ticket);
   }

   return ticket;
}

//====================================================================
// エントリー実行
//====================================================================
void ExecuteEntry(int direction)
{
   double slPips = CalculateStopLossPips();
   double lot = CalculateLotSize(slPips);
   if(lot<=0)
   {
      LogInfo("ロット計算結果が不正または最小ロット未満のため発注しません");
      return;
   }

   RefreshRates();
   double entryPrice = (direction==1) ? Ask : Bid;
   double slPrice = CalculateStopLossPrice(direction, entryPrice, slPips);
   double tpPips  = CalculateTakeProfitPips(slPips);
   double tpPrice = CalculateTakeProfitPrice(direction, entryPrice, tpPips);

   string comment = (direction==1) ? "LRT_BUY" : "LRT_SELL";
   int ticket = OpenPositionWithECNFallback(direction, lot, slPrice, tpPrice, comment);
   if(ticket<0)
      LogError("エントリーに失敗しました direction=" + IntegerToString(direction));
}

//====================================================================
// 新規エントリー判定 (確定足1本につき1回のみ呼び出される)
//====================================================================
void TryEnter()
{
   if(HasOpenPosition()) return; // 同時保有は最大1ポジション

   if(IsLiveTradingBlocked())
   {
      LogInfo("実口座判定のため新規注文をスキップしました");
      return;
   }

   if(!IsSpreadAcceptable())
   {
      LogInfo("スプレッド超過のため新規注文をスキップ: " + DoubleToString(GetCurrentSpreadPips(),1) + "pips");
      return;
   }

   if(!HasSufficientHistory()) return;

   if(IsDailyLossLimitReached())
   {
      if(!g_dailyLossLimitLogged)
      {
         LogInfo("日次損失上限に到達したため新規注文を停止しています(既存ポジションの管理は継続します)");
         g_dailyLossLimitLogged = true;
      }
      return;
   }

   if(IsMaxConsecutiveLossesReached())
   {
      if(!g_consecutiveLossLimitLogged)
      {
         LogInfo("最大連敗数に到達したため新規注文を停止しています(既存ポジションの管理は継続します)");
         g_consecutiveLossLimitLogged = true;
      }
      return;
   }

   if(!IsWithinTradingHours())
   {
      LogInfo("取引時間外のため新規注文をスキップ: " + TimeToString(TimeCurrent(), TIME_MINUTES) +
              " (許可範囲 " + IntegerToString(TradingStartHour) + ":" + IntegerToString(TradingStartMinute) +
              "-" + IntegerToString(TradingEndHour) + ":" + IntegerToString(TradingEndMinute) + ")");
      return;
   }

   if(CheckBuySignal())
   {
      ExecuteEntry(1);
      return;
   }
   if(CheckSellSignal())
   {
      ExecuteEntry(-1);
      return;
   }
}

//====================================================================
// EA本体
//====================================================================
int OnInit()
{
   g_initializedOk = false;

   if(!ValidateSymbol())  return INIT_PARAMETERS_INCORRECT;
   if(!ValidatePeriod())  return INIT_PARAMETERS_INCORRECT;
   if(!ValidateInputs())  return INIT_PARAMETERS_INCORRECT;

   ClearTesterGlobalVariablesIfNeeded(); // 前回テストのGlobalVariableを持ち越さない

   InitLastProcessedBarTime();

   LogInfo("=== USDJPY_LowRisk_Trend_EA v0.3.0(Phase5-1) 初期化 ===");
   LogInfo("Symbol=" + Symbol() + " Digits=" + IntegerToString(Digits) +
           " Point=" + DoubleToString(Point, Digits) + " MagicNumber=" + IntegerToString(MagicNumber));

   IsLiveTradingBlocked();   // 口座種別をログに出すために1回呼び出す
   RunLotCalculationTests(); // Phase3検証ログ

   // ここでの確立はログ・早期診断用。正しさの担保はEnsureDailyRiskReferenceBalance()による
   // 都度呼び出し(IsDailyLossLimitReached()の判定直前)に置いており、OnInit時の確立のみには
   // 依存しない。
   EnsureDailyRiskReferenceBalance();

   LogInfo("初期化完了。Phase5-2(建値移動/トレーリング)は未実装です。"
           + "取引時間フィルター(Phase7)は許可範囲 "
           + IntegerToString(TradingStartHour) + ":" + IntegerToString(TradingStartMinute)
           + "-" + IntegerToString(TradingEndHour) + ":" + IntegerToString(TradingEndMinute)
           + " で有効です。");

   g_initializedOk = true;
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   LogInfo("EA停止 reason=" + IntegerToString(reason));
}

void OnTick()
{
   if(!g_initializedOk) return;

   UpdateLogSuppressionState(); // サーバー日付変更後の最初のtickでログ抑制フラグを解除

   if(IsNewConfirmedBar())
   {
      // 判定結果に関わらず、まずこの足を「処理済み」として確定する。
      // これにより、同一足からの複数回発注・遅れたシグナルの追いかけ・
      // 発注失敗後の無限リトライを同時に防止する。
      MarkBarProcessed();
      TryEnter();
   }

   // Phase5-2でここにポジション管理(建値移動/トレーリング/金曜決済)を追加予定
}

# EXP-008: トレンド成熟度(trend_duration_bars)による買いエントリー除外検証

`EXPERIMENT_TEMPLATE.md`に基づく実験記録。**H006（`HYPOTHESIS_REGISTRY.md`）の事前登録実験。
ユーザーが2026-08-15、「根拠づけながら進めて」とH006の提案・進め方を承認したことを受けて発行する。
**本ファイル作成時点ではEAコードは一切変更していない**（後述「実装の要否」参照、実行には
別途明示的な承認が必要）。

## 基本情報

| フィールド | 内容 |
|---|---|
| experiment_id | EXP-008 |
| hypothesis_id | H006（トレンド成熟度による買いエントリー除外仮説） |
| title | trend_duration_bars>=50の買いエントリーを除外した場合のPF・期待値R検証 |
| evidence_level | H（検証前） |
| objective | 買いエントリーのうち、エントリー判定バーまでに`GetTrendDirection()`と同一のトレンド条件が50バー以上連続して成立していたもの（=伸びきったトレンドへの遅いエントリー）を除外した場合、買い方向のPF・期待値Rが改善するかを実バックテストで検証する |
| rationale | `O-006`（`OBSERVATION_REGISTRY.md`）で、`trend_duration_bars`を三分位に分けて全トレードのPF・勝率を再集計した結果、買いのみでExtended区分（三分位境界: DS004=48バー, DS010=52バー）がPF0.768(DS004)/0.756(DS010)と、Fresh/Established(PF1.26〜1.47)より明確に悪いことを確認した。ATRとの相関は弱く(r=-0.150)、独立した効果である可能性が高い |
| evidence_ids | なし |
| features | 新規: `trend_duration_bars`（既存の`GetTrendDirection()`判定を遡ってカウントする新規指標）。エントリー条件自体(EMA/ADX/押し目判定)・TP/SL・ロット計算は変更しない |
| target | 下記「acceptance_criteria」参照 |

## 重要な注意（閾値の根拠づけについて、結果を見た後に変更しない）

`trend_duration_bars`という特徴量、および以下の閾値50バーは、**`O-006`で観察したDS004/DS010の
データから直接導かれている**（同一データからの探索的発見という点でH004と同種のリスクを負う）。
具体的な決め方: DS004の三分位境界(Established/Extended間=48バー)とDS010の同境界(52バー)の
中間値を、きりの良い数値に丸めたものが50バーである。**この閾値は「効果が最大になる値」を
探索して選んだものではなく、中立的な三分位分割から機械的に導いた値**であることを明記する。
また、本実験ではこの閾値をこれ以上調整しない。結果が思わしくない場合も、閾値を変えて
再実験するのではなく、H006自体の判定材料として扱う。

`EXP-006`(H004)と同じ立て付けとして、「実際にEAへ実装して行う本バックテスト」を、まだ結果を
覗いていない最初の確認の場として扱う。

## 実装の要否（重要、実行前に承認が必要）

`TradingStartHour`や`EnableBreakEven`と異なり、`trend_duration_bars`は**EAに既存の入力パラメータ
が存在しない、完全に新規の特徴量**である。実装には以下が必要:

- 新規入力パラメータ`MaxBuyTrendDurationBars`(int, デフォルト値0=無効)を追加。0の場合は
  本フィルターを一切適用せず、既存の挙動を完全に維持する
- 新規関数`GetTrendDurationBars(int direction, int startShift)`を追加し、`startShift`から遡って
  `GetTrendDirection()`と同一のトレンド条件が連続して成立しているバー数を数える（`O-006`の
  `analysis/loss_regime_classification.py`の`compute_trend_duration()`と同一ロジックをMQL4へ移植）
- `CheckBuySignal()`の末尾（他のシグナル判定が全て真になった後）に
  `if(MaxBuyTrendDurationBars>0 && GetTrendDurationBars(1,1)>MaxBuyTrendDurationBars) return false;`
  を追加する。**`CheckSellSignal()`には一切手を加えない**（`O-006`で売りには効果が見られなかった
  ため、既存のH004/EXP-006のような「既存パラメータの対称性維持」の制約はなく、最初から買い限定
  で設計する）
- H006検証用の設定値: `MaxBuyTrendDurationBars=50`

**本ファイルの事前登録時点では、このコード変更は実施していない。実装するにはユーザーの
別途明示的な承認が必要（`RESEARCH_RULES.md`第11節、EAコード変更を伴うため）。実装する場合、
`EXP-006`/`EXP-007`と同様、新規ブランチ（例: `claude/ea-trend-maturity-filter`、基点は
`claude/ea-v0.3.0-risk-management`＝CC002/Phase5-1）を作成して実装することを推奨する。**

## 比較方法

| フィールド | 内容 |
|---|---|
| baseline | `EXP-002`(CC002, DS004)。買いサブセット(141件, PF1.059)を比較の基準とする |
| comparison_method | `MaxBuyTrendDurationBars=50`を実装したビルドで、`EXP-002`と同一期間・同一パラメータでバックテストを実行し、買いサブセットの期待値R・PF・取引数を比較する。売り方向は変更しないため参考記録にも通常含めない（変化があれば異常として調査する） |
| 変更点 | `trend_duration_bars`フィルターの導入(買いのみ)のみ。エントリー条件(EMA/ADX/押し目)・TP/SL・ロット計算・Phase5-1ロジック・時間帯フィルター・建値移動は一切変更しない |

## 事前登録した評価指標（Primary/Secondary/Guardrail、結果を見た後に変更しない）

| 区分 | 指標 | 期待する方向性 |
|---|---|---|
| Primary Metric | 買いサブセットの期待値R（実現R計算式、`EXP-006`/`EXP-007`と同一） | `EXP-002`買いサブセットを上回ること（正確な基準値は実行直前に`DS004`の生データから再計算して確定する。**EXP-007での反省を踏まえ、これを今回は確実に実施する**） |
| Secondary Metrics | 買いサブセットのPF、取引回数 | PFは`EXP-002`買いサブセット(1.059)を上回ることが望ましい。取引回数は`O-006`のExtended区分の比率(DS004で53/141=37.6%)相当減少する見込み |
| Guardrail Metrics | 最低取引件数、最大DD | 買いのみで最低80件以上（141件から37.6%程度の減少を見込んでも100件近く残るはずだが、安全側に80件を下限とする）。最大DDが`EXP-002`から悪化しないこと |

`rejection_criteria`: Primary Metric（買い期待値R）が`EXP-002`買いサブセット以下の場合、
`REJECTED`ではなく`HOLD`とする（`EXP-006`/`EXP-007`と同じ理由づけ。ただし本仮説は`O-006`で
ATR等との交絡を確認済み、かつ2データセットでの一貫性も確認済みであり、H004より事前の確からしさは
高いと位置づけている）。

## required_data_sources（憲章第8節）

- USDJPY H1のMT4 Strategy Testerレポート（`.htm`形式、操作履歴込み） — 必須
- 使用パラメータ一覧（`MaxBuyTrendDurationBars`の設定値を含む） — 必須
- EA Commit SHA（新規実装後に確定） — 必須
- コンパイル確認（0 errors / 0 warnings） — 必須
- Expertsログ（フィルターの発動回数を確認するため） — 必須（`EXP-006`/`EXP-007`と同様の理由）

## パラメータ・再現性情報

| フィールド | 内容 |
|---|---|
| parameters | `MaxBuyTrendDurationBars=50`。他は`EXP-002`と同一 |
| random_seed | 対象外 |
| code_version | 未確定（コード実装後に確定。新規ブランチを想定） |
| data_version | 未確定（実行後に`DATASET_REGISTRY.md`へ登録） |
| execution_date | 未実施（コード実装の承認待ち） |

## 事前登録チェックリスト

- [x] test_periodを実行前に確定している（`EXP-002`と同一期間）
- [x] acceptance_criteria（Primary/Secondary/Guardrail）を事前登録している
- [x] 未来データを参照する特徴量が含まれていない（`trend_duration_bars`はentry_time時点で判定可能な過去バーのみを使用）
- [x] H006が同一データからの探索的発見であることを明記し、閾値の決め方（中立的な三分位分割の中間値）を具体的に開示している
- [ ] EAコード変更の実施についてユーザーの承認を得ている（**未実施、本実験の実行条件**）
- [ ] 実装ブランチについてユーザーと合意している（未実施）

## limitations（事前に予期される限界）

- **同一データからの探索的発見**: H006は`O-006`でDS004/DS010（本実験のBaselineと重複するデータ）
  を対象に発見された仮説であり、本実験がその同一期間のデータで実行される場合、真のアウト・
  オブ・サンプル検証にはならない
- **DS010は真のOOSではない**: `O-006`での「再現確認」はDS004と大部分重複するトレード集合を
  使っており、独立した検証にはなっていない
- **閾値50バーの恣意性**: 三分位分割という中立的な手法から導いたとはいえ、三分位という分割数
  自体の選択（四分位や五分位ではなく）にも一定の裁量が入っている
- **経路依存効果**: `EXP-006`/`EXP-007`で確認された通り、Entry条件を変更するとそれ以降の
  値動きへの追従経路そのものが変わる可能性がある。取引数の減少見込み(37.6%)はあくまで
  静的な参考値であり、実際の減少幅は異なりうる

## reviewer

未定（人間の承認者を今後指定）

## status

`DRAFT`（Primary/Secondary/Guardrail Metricsの事前登録は完了。EAコード変更の承認待ちのため`READY`にはまだ進めない）

## created_at / updated_at

- created_at: 2026-08-15
- updated_at: 2026-08-15（事前登録。H006実験登録の承認を受けて発行。EAコード変更は未実施、別途承認が必要）

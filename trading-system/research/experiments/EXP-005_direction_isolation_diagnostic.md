# EXP-005: 方向別分離診断（Buy only / Sell only）

`EXPERIMENT_TEMPLATE.md`に基づく実験記録。**DIAG-001 Stage2完了後、ユーザーの明示的指示
（2026-08-10）により事前登録する。** 目的はH001が示す買い/売り非対称性が、方向自体の信号品質の
差なのか、それとも「両方向が同一の1ポジション枠を奪い合う」相互作用の産物なのかを切り分ける
**診断実験**である。`DIAG-001_ENTRY_EXIT_ANALYSIS.md`と同様、**「売りを止めれば勝てる」という
結論を先取りしない**（ユーザーの明示的な禁止事項）。

## 基本情報

| フィールド | 内容 |
|---|---|
| experiment_id | EXP-005 |
| hypothesis_id | H001（EMA20/75/200 + ADXによるUSDJPY H1トレンドフォローの正の期待値仮説）。`DIAG-001`のDIRECTION_ASYMMETRY(HIGH confidence)・ENTRY(MEDIUM-HIGH confidence)判定を補強する位置づけ |
| title | 方向別分離診断（Buy only / Sell only） |
| evidence_level | H（検証前。本実験も収益性のEvidence化を目的としない、`EXP-003`/`EXP-004`と同じ扱い） |
| objective | `EnableLong`/`EnableShort`を個別に無効化した2本のバックテストを実行し、方向非対称性（`DIAG-001`で確認: 買いPF≈1.03、売りPF≈0.40〔Rベース〕、売りのMFE_R<0.25率35〜37% vs 買い28%）が方向自体の信号品質の差か、ポジション枠の奪い合いによる相互作用かを診断する |
| rationale | `DIAG-001_ENTRY_EXIT_ANALYSIS.md`で、方向非対称性はポジションサイジングの影響ではなく実在すると確認済み（HIGH confidence）。ただし現行EAは`HasOpenPosition()`により同時保有最大1ポジションのため、買いシグナルの機会損失（売りポジション保有中は買えない）等の相互作用が非対称性の一部を作っている可能性が残る。これを切り分けるには、片方向のみを許可した独立実行が必要 |
| evidence_ids | なし |
| features | F001(EMA_FAST/MID/SLOW), F002(ADX14), F004(EMA20押し目/戻り接触判定)。エントリー条件自体は変更しない |
| target | 下記「比較方法」参照。収益性そのものの採否判断には使用しない |

## 比較方法（2本のRun、いずれも診断目的）

| Run | 設定 | 比較対象 |
|---|---|---|
| Run A (Buy only) | `EnableShort=false`, `EnableLong=true`。他は`EXP-002`と同一 | `EXP-002`の買いサブセット（141件、Rベース PF≈1.027、MFE_R<0.25率28.0%、`DIAG-001`参照）と比較 |
| Run B (Sell only) | `EnableLong=false`, `EnableShort=true`。他は`EXP-002`と同一 | `EXP-002`の売りサブセット（54件、Rベース PF≈0.402、MFE_R<0.25率35.6%、`DIAG-001`参照）と比較 |

**baseline選定についての注記**: `BACKTEST_COVERAGE_EXPANSION_PLAN.md`の優先3では、本来
`EXP-004`（CC001確定ビルド）確定後にBaselineとして使う計画だったが、`EXP-004`は本セッション時点で
まだ正しいCC001ビルドでの実行が完了していない（試行時にMetaEditorのファイル差し替えに失敗し、
実質`EXP-003`の再提出になっていたことが判明済み）。ユーザーの明示的指示により、本実験は
`EXP-004`を待たず**`EXP-002`（CC002, 確定ビルド）をBaselineとして**登録する。CC001とCC002は
エントリーロジック自体が同一であり（`RISK_ENGINE_SPEC.md`, `EXP-004`の「CC001固有の注意点」参照）、
`EXP-002`で日次損失上限は0回・連敗制限は2回のみの発動（`DIAG-001`Stage1で確認済み、影響は軽微）
のため、この代替は許容範囲と判断する。**より厳密な比較（真のCC001ビルドとの比較）が必要な場合は、
`EXP-004`完了後に別途`experiment_id`を発行する。**

## comparison_method

各Run（Buy only / Sell only）について、同一方向の`EXP-002`サブセットと以下を比較する。

- 取引数（1ポジション枠の競合が解消された分、増加するはずと予想される。増加しなければ
  相互作用が非対称性の主因ではないことを示す一材料になる）
- PF・勝率・平均実現R（Rベース、`DIAG-001`と同じ算出方法）
- MFE_R分布（可能であれば。操作履歴`.htm`が取得できた場合のみ、下記「必要データ」参照）

**判定の考え方（事前登録、結果を見た後に変更しない）**:

- 単独実行時の勝率・PFが`EXP-002`サブセットと**大きく変わらない**場合 → 非対称性は方向自体の
  信号品質の差であり、ポジション枠競合は主因ではない（`DIAG-001`のENTRY側判定を補強）
- 単独実行時に**取引数が大きく増え、かつ勝率・PFも改善する**場合 → ポジション枠競合が
  非対称性の一部を作っていた可能性がある（新しい機会が増えただけでなく質も改善するなら、
  奪い合いによる機会損失が単なる「回数減」以上の影響を持っていたことを示唆）
- 取引数は増えるが勝率・PFが変わらない、または悪化する場合 → 機会は増えたが質は変わらない
  （非対称性は方向自体の問題のまま）

いずれの結果でも、**「売りロジックを停止すべきか」という運用上のDecisionはここでは行わない**。
本実験はH001・DIAG-001の診断材料を追加するのみ。

## required_data_sources（憲章第8節）

- USDJPY H1のMT4 Strategy Testerレポート（`.htm`形式） — Run A・Run Bそれぞれ必須
- 操作履歴`.htm` — 任意（取得できればMFE/MAE分析まで拡張できるが、本MT4環境では保存不可と
  既知〔`EXP-003`/`EXP-004`と同じ制約〕。取得できない場合は取引数・PF・勝率等のレポート集計値
  のみで比較する） 
- 使用パラメータ一覧（`EnableLong`/`EnableShort`の値を含む） — 必須
- EA Commit SHA（CC002固定を想定） — 必須
- コンパイル確認 — 必須（前回`EXP-003`実行時に`COMPILE_CONFIRMED_BY_USER_SCREENSHOT`で確認済みの
  ビルドをそのまま使う場合は再コンパイル不要。EA本体を差し替えていなければ省略可）

## 検証用設定

| 設定 | 値 |
|---|---|
| 使用EAビルド | CC002（`claude/ea-v0.3.0-risk-management`, `13fc725a6a6e96fe2dd13af3970e88eeee821d73`）。`EXP-002`/`EXP-003`と同一ファイル |
| `EnableLong` / `EnableShort` | Run A: `true`/`false`（Buy only）。Run B: `false`/`true`（Sell only） |
| `MaxDailyLossPercent` / `MaxConsecutiveLosses` | `EXP-002`と同一の既定値（2.0 / 3）。本実験の主眼はリスク管理機能ではないため、既定値に固定する（`EXP-003`の非標準値0.3/20は使わない） |
| その他EAパラメータ | `EXP-002`と同一（`FastEMAPeriod=20, MiddleEMAPeriod=75, LongEMAPeriod=200, ADXPeriod=14, MinimumADX=20, ATRStopMultiplier=1.5, RewardRiskRatio=2.0, MinStopLossPips=5.0, MaxStopLossPips=100.0, RiskPercent=0.5, MaxSpreadPips=3.0`等） |
| 通貨ペア・時間足・期間・初期証拠金・モデル・スプレッド | `EXP-002`と同一（USDJPY, H1, 2025-07-21〜2026-07-27, 100,000, 全ティック, 現在値(5)） |

## パラメータ・再現性情報

| フィールド | 内容 |
|---|---|
| parameters | 上表参照。Run A/Bで`EnableLong`/`EnableShort`のみ異なる |
| random_seed | 対象外 |
| code_version | `13fc725a6a6e96fe2dd13af3970e88eeee821d73`（CC002、EAコード自体は変更しない） |
| data_version | 未確定（実行後に`DATASET_REGISTRY.md`へDS007・DS008等として登録） |
| execution_date | 未実施 |

## 事前登録チェックリスト

- [x] test_periodを実行前に確定している（`EXP-002`と同一期間）
- [x] 判定の考え方を事前登録している（上記「判定の考え方」節。結果を見た後に変更しない）
- [x] 未来データを参照する特徴量が含まれていない（`EXP-002`と同一のエントリーロジック）
- [x] code_version（コミットSHA）を記録済み。data_versionは実データ受領後
- [x] Baseline選定の代替理由（`EXP-004`未完了のため`EXP-002`を使用）を事前に明記している
- [ ] Expertsログ・操作履歴の取得可否をユーザーと合意している（未実施、実施時に確認）

## status

`READY`（事前登録完了。ユーザーによるMT4実行・データ提供待ち。Run A・Run Bの2本が必要）

## limitations（事前に予期される限界）

- Baselineが`EXP-002`（CC002）であり、当初計画の`EXP-004`（CC001確定ビルド）ではない。両者の
  エントリーロジックは同一と確認済みだが、厳密な意味での「唯一の変更点」ではなくなる
- 操作履歴`.htm`が取得できない場合、MFE/MAEベースの深い診断（`DIAG-001`Stage2相当）は
  Run A・Run Bには適用できず、レポート集計値（取引数・PF・勝率）のみの比較にとどまる
- サンプル数はさらに小さくなる見込み（片方向のみのため、`EXP-002`の141件/54件よりは増える
  可能性があるが、依然として初期評価帯に留まる可能性が高い）
- 本実験は診断目的であり、収益性の採否判定（ADOPTED/REJECTED）には使用しない

## ユーザーが次にMT4で行う操作

`EXP-002`実行時と同じCC002ビルド・同じ設定から、以下の項目「のみ」を変更して**2回**実行する。

**Run A（Buy only）**:
1. `EnableShort` を `true` → **`false`** に変更（他は`EXP-002`実行時のまま）
2. バックテストを実行
3. 「結果」タブをレポート`.htm`として保存し、アップロード

**Run B（Sell only）**:
1. `EnableLong` を `true` → **`false`** に変更、`EnableShort`は`true`に戻す
2. バックテストを実行
3. 「結果」タブをレポート`.htm`として保存し、アップロード

（操作履歴`.htm`が保存できる環境であれば、あわせて保存・アップロードしてください。本環境で
できないことは既に確認済みのため、無理に取得する必要はありません）

## reviewer

未定（人間の承認者を今後指定）

## created_at / updated_at

- created_at: 2026-08-10
- updated_at: 2026-08-10（事前登録。DIAG-001 Stage2完了後、ユーザー指示により発行）

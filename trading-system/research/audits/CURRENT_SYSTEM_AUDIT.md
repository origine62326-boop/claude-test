# Current System Audit

`RESEARCH_PLATFORM_ROADMAP.md` Phase R1に対応。既存リポジトリの構成要素を、研究基盤への流用可否で分類する。

分類凡例:

- **A**: Research Platformへそのまま流用可能
- **B**: 修正すれば流用可能
- **C**: 仮説として再検証が必要
- **D**: 根拠不足
- **E**: 重複・レガシー候補

Evidenceレベルは推測で引き上げていない。既存コードのコメントや設計意図は「実装の事実」ではあるが、
それ自体が外部Evidence（BIS/FRB等）ではないため、原則`H`（検証前の仮説の集合）または`U`
（分類不能・該当なし）としている。

**前提の注記**: この監査は`claude/fx-research-platform-foundation-v0.1.0`ブランチ（`main`起点）上で
実施した。`main`にはまだPhase 5-1（日次損失上限・連敗制限）がマージされておらず、EAはv0.1.0
(Phase1-4)の状態である。Phase 5-1関連の記述は、本セッション内で確認済みの別ブランチ
`claude/ea-v0.3.0-risk-management`（未マージ）の内容に基づく。

## 監査結果一覧

| component | current_purpose | current_status | evidence_level | classification | risks | leakage_risk | reproducibility_status | recommended_action | migration_phase |
|---|---|---|---|---|---|---|---|---|---|
| `USDJPY_LowRisk_Trend_EA/`（リポジトリルート、レガシーフォルダ） | v0.1.0時点のEAバックアップ | `LEGACY_BACKUP_NOTICE.md`により参照専用・更新停止と明記済み | U（バックアップという性質上、監査対象外） | E（重複・レガシー候補） | 低（既に読み取り専用として明記済み。誤って編集される可能性のみ） | 該当なし | 該当なし | 現状維持。削除はしない（憲章の削除禁止方針、および`LEGACY_BACKUP_NOTICE.md`自身が定める「十分なバックテスト・フォワードテスト・デモ運用が完了してから改めて提案」という条件に従う） | 対象外(R1棚卸しのみ) |
| `trading-system/mt4/USDJPY_LowRisk_Trend_EA.mq4`（現行EA本体、main時点） | USDJPY H1のEMA/ADXトレンドフォローEA、Phase1-4実装（トレンド判定・ATR SL/TP・ロット計算・安全発注） | main時点でv0.1.0。日次損失/連敗制限・建値移動/トレーリング・取引時間フィルターは入力検証のみで未接続 | H（実装は存在するが、外部Evidenceでの裏付けはない。[UNVERIFIED_OBSERVATION] 会話内の参考バックテストではPF<1の局面ありという未検証の観察がある。詳細はH001参照） | B（修正すれば流用可能。ロジック自体をSignal Engineの一仮説実装として研究基盤に取り込める） | 中（未接続の入力パラメータが存在し、設定しても効果がないという誤解を招きうる。コード内コメントでは本機能を「Phase 6」と呼称しており、未マージブランチの「Phase 5-1」と番号がずれている） | 低（未確定足を使わない設計が明記されている） | 未確認（研究基盤の`EXPERIMENT_TEMPLATE.md`形式でのウォークフォワード検証は未実施） | H001として仮説登録済み。売買ロジック自体は変更せず、まず研究基盤側でバックテスト結果を再現・検証する | Phase R1(状態固定・再現), R5 |
| Phase5-1 リスク管理（日次損失上限・連敗制限、未マージブランチ`claude/ea-v0.3.0-risk-management`） | 当日の損失上限到達・連敗到達で新規エントリーを停止する資金管理機能 | **[IMPLEMENTED_ON_UNMERGED_BRANCH]** 実装済みだがmainには未マージ（mainに実装済みと誤認しないこと）。テスト計画(`TEST_PLAN_PHASE5-1.md`)のうちコードレビューで代替した項目のみ確認済み、実機テスターでの確認は一部未実施(チェックリスト`☐`のまま)。source_branch/merge_status等の詳細区分は`RISK_ENGINE_SPEC.md`および`trading-system/configs/risk_limits.yaml`を参照 | H | C（仮説として再検証が必要。H002として登録済み） | 中（mainとの差分が大きくなるほどマージ時のコンフリクト・再検証コストが増える） | 低（当日決済分・保有中含み損のみを参照し、未確定情報は使わない設計） | 未確認 | H002の実験化。研究基盤側での検証と、EA側のマージ判断は別軸で進める（本作業はEA側を変更しない） | Phase R1(状態固定), R5 |
| EMA/ADX/ATRロジック（トレンド判定・強度フィルター・SL/TP計算） | 押し目買い・戻り売りのシグナル生成とリスク幅計算 | 実装済み（`GetTrendDirection`, `IsADXStrongEnough`, `CalculateStopLossPips`等） | H | B | 中（[UNVERIFIED_OBSERVATION] 会話内の参考バックテストで、勝率29.89%が理論上の損益分岐勝率33.3%をわずかに下回るという観察があるが、MT4 HTMLレポート等が揃っておらず未検証。優位性の有無は未確定） | 低 | 未確認 | F001-F004として特徴量登録済み。単体の予測力を`EXPERIMENT_TEMPLATE.md`で検証してから採否判断する | Phase R1(再現), R4, R5 |
| `fx_predict.py` + `fx_modules/`（LSTM予測） | Yahoo Finance日次終値によるUSD/JPY将来レート予測 | 実装済み、独立CLIツールとして動作（`python fx_predict.py`） | H | C（仮説として再検証が必要。研究基盤の評価指標(Direction Accuracy等)では未評価） | 中〜高（学習・推論ともにスプレッド/取引コストを含まない日次終値ベースであり、MT4側のバックテスト系(EA)とはデータ系統が異なる。モデルファイル自体はgitignore対象で版管理されていない） | 要確認（LSTM学習時のtrain/test分割方法が本監査時点で未精査。時系列データでの分割方法次第では将来データ混入リスクがある） | 未確認 | M002として登録済み。研究基盤の評価指標で評価するまで、EA側の売買判断に統合しない（ユーザー指示によりLSTMの自動統合は今回禁止事項） | Phase R4 |
| `trading-system/analysis/`配下の解析コード（`common.py`, `performance_metrics.py`, `direction_analysis.py`, `period_analysis.py`, `regime_analysis.py`, `time_analysis.py`, `trade_anomaly_check.py`, `compare_versions.py`等） | MT4バックテスト結果の指標計算・異常検知・期間別/方向別/レジーム別分析 | 実装済み、pytestあり（`trading-system/tests/`） | H（実装として存在するが、指標定義自体の外部Evidence裏付けは個別確認していない） | A〜B（PF/DD/勝率等の一般的な指標計算はそのまま流用可能。異常検知ロジックは`risk_limits.yaml`の値が実際のEA入力とズレていないか要確認） | 低（2026-07-28時点で`configs/risk_limits.yaml`のコメント・`implementation_status`ブロックを実装状況(`[IMPLEMENTED_ON_UNMERGED_BRANCH]`, merge_status等)と一致させる修正を実施済み。ただし同yamlは現時点でどのPythonコードからも読み込まれておらず、実際の異常検知への反映はまだない） | 低 | 部分的に確認済み（pytest fixtureベースでは通過。実MT4出力での検証はTODOとしてv0.2.0時点から申し送り継続中） | 研究基盤の`EXPERIMENT_TEMPLATE.md`から呼び出せる形への統合を検討（Phase R3）。`risk_limits.yaml`の`implementation_status`を実際に読み込んで異常検知に反映するかはPhase R2以降で検討 | Phase R2, R3 |
| MT4バックテストレポート解析（`parse_mt4_report.py`, `parse_mt4_trades.py`） | MT4のHTMLレポート・操作履歴を構造化データへ変換 | 実装済み、日英両レポート対応。ただし実際のMT4出力ファイルでの検証はTODO継続中(`reports/raw/`は`.gitkeep`のみ) | H | B | 中（実データでの検証未了のまま、本会話ではスクリーンショット(DS002)による手動確認のみで会話内考察を行っている） | 低 | 未確認（実データ未投入） | 次にユーザーから`.htm`レポートが提供された時点で、DS001として正式取り込みし、パイプラインの実データ検証を行う | Phase R2 |
| 既存README（`README.md`, `trading-system/README_JP.md`） | プロジェクトの利用方法説明 | ルート`README.md`は内容が「X運用PDCAツール」のみを説明しており、FX関連（`fx_predict.py`, `trading-system/`, EA）への言及がない | U | E寄りのD（重複ではないが、ドキュメント構成としての抜け。FXプロジェクト群への導線が root README に存在しない） | 低（機能への影響はないが、初見の読者がFX関連コンポーネントの存在に気づきにくい） | 該当なし | 該当なし | 研究基盤のREADME追記は`trading-system/README_JP.md`側に実施（本作業のスコープ）。root README.mdの構成見直しは本作業のスコープ外として別途提案 | 対象外 |
| 既存CHANGELOG（`trading-system/CHANGELOG.md`, `trading-system/mt4/CHANGELOG_EA.md`, レガシーフォルダの`CHANGELOG.md`） | バージョン変更履歴の記録 | 運用中、v0.1.0〜v0.2.0まで記録あり。v0.3.0(Phase5-1)は未マージブランチ側でのみ更新されている可能性 | U | A | 低 | 該当なし | 該当なし | 現状維持。本作業では研究基盤自体のバージョン方針を別途`GAP_ANALYSIS.md`および完了報告で提案する | 対象外 |
| 経済指標フィルター構想（新規エントリー停止） | 会話内で改善案として提案されたのみ、未実装 | アイデア段階 | H（H003として登録済み。2026-07-28時点でIDは`RESEARCH_CHARTER.md`とH003に統一済み） | D（根拠不足。有効な機能として最初から扱わないよう明示指示あり） | 中（MQL4に標準経済指標カレンダーAPIがなく、バックテスト用のポイントインタイムデータ整備が別途必要） | 高（経済指標データを後付けで取得する場合、発表時刻・改定履歴の扱いを誤ると未来データ混入になりやすい） | 未確認（未実装） | H003の実験化を優先。実装は行わない（今回の禁止事項にも該当） | Phase R2(データ), R5(実験) |
| GitHub Actions（`.github/workflows/release.yml`） | `vX.Y.Z`タグpushでGitHub Releaseを自動作成 | 稼働中（`actions/checkout@v5`, `workflow_dispatch`対応済み） | U | A | 低 | 該当なし | 該当なし | 現状維持。研究基盤のドキュメントリリースへ流用するかは今後検討（本作業ではタグ・Release作成は行わない） | 対象外 |
| 自動リリース（release automation、上記と同一機構） | 上記と同一 | 上記と同一 | U | E（GitHub Actionsの項目と重複するため、監査上は1コンポーネントとして統合） | 低 | 該当なし | 該当なし | 上記と統合管理 | 対象外 |
| 古いEAフォルダ（`USDJPY_LowRisk_Trend_EA/`） | 上記「レガシーフォルダ」行と同一対象 | 同上 | U | E | 低 | 該当なし | 該当なし | 上記「レガシーフォルダ」行と統合管理（ユーザー提示リストで別名として挙げられていたため、同一コンポーネントである旨をここに明記） | 対象外 |

## 補足: 「勝てそう」という理由だけの記述の有無について

上記監査対象の中で、`trading-system/README_JP.md`や`CHANGELOG.md`に「勝率」「利益」を目的として
記載している箇所はあるが、いずれも「バックテスト結果の記録」としての記述であり、根拠のない
断定的な勝率保証の記載は見当たらなかった。ただし`acceptance_criteria.yaml`のコメントに
「PASSしたからといって実口座投入を推奨するものではない」旨が明記されている一方、README側に
同等の免責文言がまだ十分ではないため、`GAP_ANALYSIS.md`および今回のREADME追記対象とする。

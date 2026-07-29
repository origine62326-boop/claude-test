# Gap Analysis

`CURRENT_SYSTEM_AUDIT.md`を踏まえた、研究基盤としての不足点・優先順位付け。

優先度定義:

- **P0**: 研究結果の信頼性を壊す問題
- **P1**: 再現性・安全性に関わる問題
- **P2**: 研究効率に関わる問題
- **P3**: 将来拡張

## P0: 研究結果の信頼性を壊す問題

1. **[2026-07-28 対応済み] 実データ未投入のままの分析結果が会話内に存在する。**
   本セッションのこれまでの会話では、ユーザーが共有したMT4 Strategy Testerのスクリーンショット
   （`DATASET_REGISTRY.md`のDS002）を根拠に、PF0.74・勝率29.89%・買い/売りの成績差といった分析を
   行っている。これは画像からの手動確認であり、`parse_mt4_report.py`等のパイプラインを通した
   正式な検証ではない。研究基盤としてこれを`EXPERIMENT_TEMPLATE.md`や`MODEL_REGISTRY.md`の
   正式な`metrics`として扱うと、再現不能な数値を根拠として引用することになる。
   → 対応: `DATASET_REGISTRY.md`(DS002)・`MODEL_REGISTRY.md`(M001)・`HYPOTHESIS_REGISTRY.md`(H001)の
   該当箇所すべてに`[UNVERIFIED_OBSERVATION]`タグを明記し、「MT4 HTMLレポート・使用パラメータ・
   コードSHA・データ条件・ファイルハッシュが揃うまで正式なResearch ResultやEvidenceとして登録しない」
   旨を統一的に記載した。今後は実際の`.htm`レポートをDS001として取り込み（Phase R1の残タスク）、
   パイプラインを通した数値のみを正式な実験結果として採用する。

2. **[2026-07-28 対応済み] HypothesisのID不一致（経済指標フィルター = 憲章ではH004、レジストリではH003）。**
   `RESEARCH_CHARTER.md`第5節の例示と`HYPOTHESIS_REGISTRY.md`の実登録で、同じ仮説（経済指標前後の
   新規エントリー停止）に異なるIDが割り当てられていた。将来この仮説を引用する際に誤ったIDを
   参照すると、異なる仮説と取り違えるリスクがある。
   → 対応: `RESEARCH_CHARTER.md`第5節の例示をプロジェクト非依存の一般例(例A〜例C)に改め、
   経済指標前後停止の参照をH003に統一した（変更理由・差分を憲章の改訂履歴に記録、本ユーザー
   承認をもって実施）。`HYPOTHESIS_REGISTRY.md`・`CURRENT_SYSTEM_AUDIT.md`の注記も解消済みとして更新した。

3. **[2026-07-28 対応済み] `trading-system/configs/risk_limits.yaml`のコメントが実装状況とズレている。**
   同ファイルは「max_daily_loss_percent: Phase6で実装予定(v0.1では未使用)」とコメントされていたが、
   本セッションで確認した未マージブランチ`claude/ea-v0.3.0-risk-management`では、この機能は
   「Phase 5-1」としてすでに実装済みだった。このyaml自体のコメントに「自動同期はしていない。
   ズレたままだと異常検知が誤判定する」と明記されており、`trade_anomaly_check.py`等の異常検知が
   将来のバージョンで誤判定する土台が既にできていた。
   → 対応: `risk_limits.yaml`に`implementation_status.daily_loss_and_consecutive_loss_limits`
   ブロックを追加し、source_branch/merge_status/compile_status/backtest_status/
   full_test_plan_status/demo_forward_status/live_approval_statusを明示。値は
   `RISK_ENGINE_SPEC.md`の`[IMPLEMENTED_ON_UNMERGED_BRANCH]`ステータスブロックと同期させた
   （YAML構文はpyyamlでパース確認済み）。ただし同yaml自体は現時点でどのPythonコードからも
   読み込まれていないため、`trade_anomaly_check.py`等への実際の反映はまだない（Phase R2以降で検討）。

## P1: 再現性・安全性に関わる問題

4. **main と `claude/ea-v0.3.0-risk-management` の乖離、およびPhase番号の不一致。**
   main上のEA(v0.1.0)は日次損失/連敗制限のコード内コメントを「Phase 6」としているのに対し、
   未マージブランチでは同機能を「Phase 5-1」と呼称している。ブランチ間でフェーズ番号の付け方が
   変わっており、今後どちらの番号体系を正式とするか未確定。
   → 対応(部分的): 本研究基盤側では、既存EAのPhase番号（Phase N）と研究基盤のPhase番号（Phase RN）を
   別体系として明記した（`RESEARCH_PLATFORM_ROADMAP.md`）。加えて、Phase5-1関連の記述すべてに
   `[IMPLEMENTED_ON_UNMERGED_BRANCH]`を明記し、main実装済みと誤認しない表現に統一した
   （`RISK_ENGINE_SPEC.md`, `CURRENT_SYSTEM_AUDIT.md`, `HYPOTHESIS_REGISTRY.md`(H002),
   `configs/risk_limits.yaml`）。ただしEA側のPhase番号自体の統一・mainへのマージ判断は
   本作業のスコープ外（既存EA変更禁止）のため未解消。`RESEARCH_PLATFORM_ROADMAP.md`のPhase R1
   残タスク（状態固定・バージョン整理）で扱う。次の承認事項として報告する。

5. **LSTM(`fx_predict.py`)の再現性が未確認。**
   train/validation/testの分割方法が本監査時点で未精査であり、時系列データに対して適切な
   分割（未来データ混入なし）がされているか確認できていない。モデルファイル自体も`data/`配下で
   gitignore対象となっており、`code_version`と紐づけたバージョン管理がされていない。
   → 対応: `MODEL_REGISTRY.md`にM002として「未評価」の状態で登録済み。Phase R4でベースライン比較を
   行う前に、分割方法の精査を優先事項として記録する。

6. **MT4バックテストレポート解析パイプラインが実データで未検証のまま継続している。**
   `trading-system/reports/raw/`は`.gitkeep`のみで、実際の`.htm`レポートが投入されていない。
   これはv0.2.0リリースノートの時点から「最優先のTODO」として申し送りされており、本監査時点でも
   未解消。
   → 対応: `DATASET_REGISTRY.md`のDS001として登録済み（未確定状態）。この実データ取り込みと
   既存バックテストの再現は、`RESEARCH_PLATFORM_ROADMAP.md`改訂によりPhase R2ではなく
   **Phase R1の残タスク**として先に完了させる方針に変更した（R2着手前に状態固定を優先するため）。
   ユーザーから実データが提供され次第、優先的に取り込む。

7. **Signal EngineとRisk Engineの分離が構造的に未達成。**
   現行EA(MQL4)は1ファイル内でシグナル判定とリスク判定が密結合しており、憲章第15節が求める
   独立した`ALLOW`/`REDUCE`/`BLOCK`/`EMERGENCY_STOP`出力を持つRisk Engineにはなっていない。
   → 対応: `RISK_ENGINE_SPEC.md`に現状を整理済み。Python側での分離実装はPhase R7-R8で
   別途検討する（本作業ではEA変更・新規実装ともに行わない）。

## P2: 研究効率に関わる問題

8. **root `README.md`にFX関連コンポーネントへの言及がない。**
   ルートの`README.md`はX(旧Twitter)運用PDCAツールの説明のみで、`fx_predict.py`や
   `trading-system/`への導線が存在しない。初見の読者が本研究基盤の存在に気づきにくい。
   → 対応: 本作業では`trading-system/README_JP.md`側への追記のみを行った（ユーザー指示の
   スコープ）。root README.mdの構成見直しは次の承認事項として報告する。

9. **台帳ファイルの形式チェックスクリプトが未実装。**
   ID重複・必須列欠落・リンク切れ等を機械的にチェックする仕組みがまだない。
   → 対応: `research/governance/RESEARCH_RULES.md`第12節に案を記載済み（未実装、承認待ち）。

10. **未接続のまま残っている入力パラメータ(`TradingStartHour`等)の扱い方針が未確定。**
    EA側に入力値検証のみ存在し、実際のフィルタリングには使われていない。研究基盤側で
    F103として先に仮説検証してからEA側に接続するのか、EA側で先に接続してから研究基盤で
    評価するのか、方針が未確定。
    → 対応: `FEATURE_REGISTRY.md`にF103として登録済み。方針決定は次の承認事項とする。

11. **[2026-07-28新規発見] `releases/v0.1.0/NOTES.md`記載の写真ベース参考値2件が`DATASET_REGISTRY.md`に
    未登録。** Phase R1ステップ2（`research/versions/BACKTEST_REPRODUCIBILITY.md`作成）の過程で発見。
    「約2年間/初期証拠金1万円: 527取引・PF1.06」「直近1年間/初期証拠金10万円: 192取引・PF0.76」という
    2件の参考値が、DS002と同様に画像ベース・パイプライン未検証のまま`releases/v0.1.0/NOTES.md`に
    記載されている。当該NOTES.md自体が「本パイプラインを通していない参考値であり、正式な記録ではない」
    と明記しているため信頼性を偽装するものではないが、`DATASET_REGISTRY.md`側での一元管理という
    観点では抜けている。
    → 対応: `BACKTEST_REPRODUCIBILITY.md`のBR003として記録済み。DS-ID発行は本作業のスコープ外
    （今回の依頼はVERSION/CODE_COMPONENT/BACKTEST_REPRODUCIBILITYの3ファイル作成のみ）のため、
    次の承認事項として報告する。

## P3: 将来拡張

11. **憲章が求めるモデル分離構成(Price/News/Interest Rate/Liquidity/Event/Regime/Ensemble)のうち、
    現状はPrice系(M001, M002)しか存在しない。** News/Interest Rate等のモデルは、対応するデータ
    ソースの整備自体がまだ行われていない。

12. **H003（経済指標フィルター）の検証に必要な経済指標カレンダーデータソースが未定。**
    ポイントインタイムでの過去データ整備が別途必要であり、データ取得方針（手動リスト、外部API等）が
    未確定。外部APIの新規接続は今回の禁止事項に該当するため、方針決定自体を次の承認事項とする。

13. **Decision Engine / Risk EngineのPython実装自体がまだ存在しない。**
    `DECISION_SCHEMA.md` / `RISK_ENGINE_SPEC.md`は仕様整理のみであり、Phase R7-R8で実装予定。

## まとめ

P0の3件は、PR #8レビュー（2026-07-28）での指摘を受け、いずれもドキュメント内の記述修正・
ID統一・ステータスタグ付与（`UNVERIFIED_OBSERVATION`, `IMPLEMENTED_ON_UNMERGED_BRANCH`）により
対応済み。ただし「実データの取り込みによる正式なResearch Result化」自体は、実際の`.htm`レポート
取得というユーザー側の作業が必要なため未完了であり、Phase R1の残タスクとして引き続き記録する。
P1のうちPhase番号不一致は部分対応、その他(LSTM再現性、パイプライン実データ検証、Signal/Risk分離)は
Phase R1(状態固定・再現)およびR7-R8で対応する。P2-P3は今後のPhaseで順次対応する。

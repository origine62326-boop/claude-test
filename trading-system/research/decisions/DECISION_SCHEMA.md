# Decision Schema

`trading-system/RESEARCH_CHARTER.md` 第16節に基づく、Decision Engineの出力仕様。**現時点では仕様定義のみであり、
Decision Engine自体は未実装**（`research/roadmap/RESEARCH_PLATFORM_ROADMAP.md` Phase R7で実装予定）。

## 出力

| フィールド | 型 | 説明 |
|---|---|---|
| decision | `"BUY" \| "SELL" \| "WAIT"` | 最終判断。WAITは正常な判断であり、無理にエントリーしない |

## 補助出力

| フィールド | 型 | 説明 |
|---|---|---|
| confidence | float | 判断の確信度 |
| expected_value | float | 期待値（R単位を推奨） |
| lower_confidence_bound | float | 期待値の信頼区間下限 |
| upper_confidence_bound | float | 期待値の信頼区間上限 |
| signal_model_id | string | 使用した`MODEL_REGISTRY.md`のmodel_id |
| hypothesis_ids | string[] | 根拠とした`HYPOTHESIS_REGISTRY.md`のhypothesis_id一覧 |
| evidence_ids | string[] | 根拠とした`EVIDENCE_REGISTRY.md`のevidence_id一覧 |
| data_quality_status | string | データ品質状態（例: OK, DEGRADED, INSUFFICIENT） |
| risk_status | `"ALLOW" \| "REDUCE" \| "BLOCK" \| "EMERGENCY_STOP"` | Risk Engineからの出力（`RISK_ENGINE_SPEC.md`参照） |
| reason_codes | string[] | 判断理由コード一覧 |
| generated_at | datetime | 生成時刻 |

## 判定ルール（憲章第15-16節）

1. Decision EngineはSignal Engineの方向予測とRisk Engineの出力を**別々に**受け取る。
2. SignalがBUYまたはSELLであっても、Risk Engineの出力が`BLOCK`または`EMERGENCY_STOP`の場合、
   最終的な`decision`は必ず`WAIT`とする。Risk EngineはSignalの方向予測そのものを書き換えない
   （Signal Engineの出力は`signal_model_id`の参照先にログとして残し、Decision Engineが上書きする形にする）。
3. `risk_status = REDUCE`の場合、`decision`自体はSignal側の方向を採用してよいが、ロット計算側で縮小する
   （ロット計算のロジックはRisk Engine側、`RISK_ENGINE_SPEC.md`参照）。
4. `RESEARCH_CHARTER.md`第8節のデータ品質ルールに該当する場合（価格データ欠損、API停止、
   未来データ混入疑い等）、`data_quality_status`を`INSUFFICIENT`とし、`decision = WAIT`を返す。
5. BUYまたはSELLを返す場合、必ず`hypothesis_ids` / `evidence_ids` / `data_quality_status` / `risk_status`を
   添付する。いずれかが欠落した状態でBUY/SELLを返してはならない。

## 未確定事項

- `confidence`の算出方法（憲章第10節の暫定勝率表とベイズ更新、またはモデルの予測確率のいずれを
  使うか）は未確定。Phase R4-R6で検証しながら決定する。
- `expected_value`の単位(R単位か金額単位か)は憲章第9.1節に合わせR単位を既定とするが、最終確定は
  実装時に`RESEARCH_RULES.md`側へ追記する。

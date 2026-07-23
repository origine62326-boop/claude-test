# このフォルダはレガシーバックアップです

**今後の開発は `trading-system/mt4/` を正規の配置場所として進めます。**
このフォルダ（`USDJPY_LowRisk_Trend_EA/`）は v0.1.0 固定時点のバックアップとして、
削除せずそのまま保持しています。

- 正規の開発場所: `trading-system/mt4/USDJPY_LowRisk_Trend_EA.mq4`
- 正規の変更履歴: `trading-system/CHANGELOG.md`
- 正規のバージョン記録: `trading-system/releases/`

このフォルダの内容は今後更新しません。参照専用（読み取り専用）として扱ってください。
削除は、十分なバックテスト・フォワードテスト・デモ運用が完了し、不要と判断した時点で
改めて提案します。

## v0.1.0時点での差分

`trading-system/mt4/` 作成時点でこのフォルダから複製したため、EA本体
(`USDJPY_LowRisk_Trend_EA.mq4`)は現在もバイト単位で完全に一致しています。
`CHANGELOG.md`は`trading-system/mt4/CHANGELOG_EA.md`へ複製後、統合済みの
注記が追加されている点のみが差分です。`README_MT4_JP.md`（MT4→Python連携の
手順書）は`trading-system/mt4/`側にのみ存在する新規ファイルです。

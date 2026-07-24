# releases/ ディレクトリについて

`trading-system/reports/` と `trading-system/outputs/` はパイプラインの**作業用出力**であり
gitignore対象（都度上書きされる想定）。それに対して、この `releases/` は**バージョンごとの
正式な記録**を残すためのディレクトリで、git管理下に置く。

## 1バージョンあたりの中身

```
releases/vX.Y.Z/
├─ NOTES.md              # このバージョンで何を変更したか、なぜ変更したか
├─ summary.md             # (データが揃い次第) outputs/summaries/ からコピーした確定版サマリー
├─ metrics.json           # (データが揃い次第) reports/analyzed/ からコピーした確定版指標
└─ comparison_vs_prev.md  # (データが揃い次第) 直前バージョンとの比較レポート
```

## 運用ルール（README_JP.md「バージョン管理ルール」と対応）

1. 既存ファイルを上書きする前にGitでコミットする
2. 重要な変更ごとにバージョンを付与する（`CHANGELOG.md` 参照のバージョニング方針）
3. `CHANGELOG.md` を更新する
4. `README_JP.md` に変更内容を追記する
5. そのバージョンでバックテストを実行したら、`scripts/run_analysis.py` の出力を
   このディレクトリの該当バージョンフォルダへコピーして記録する
6. 前バージョンがあれば `scripts/compare_backtests.py` で比較レポートを作成し、
   同様にコピーして記録する
7. `git tag vX.Y.Z` でタグを打ち、GitHubへプッシュする
8. GitHub Releaseは `.github/workflows/release.yml` により**自動作成される**。
   `vX.Y.Z` 形式のタグpushをトリガーに、このバージョンの `NOTES.md` があれば
   それをそのままRelease本文として使い、無ければGitHubの自動生成ノートを使う。
   人間の手動操作は不要。

## 現状の制約

`v0.1.0` の時点では、MT4から実際にエクスポートしたレポート/操作履歴ファイルでの
パイプライン検証がまだ完了していない（`TODO.md` 参照）。そのため `v0.1.0/` フォルダには
`summary.md` 等の確定版データはまだ含めておらず、`NOTES.md` に会話内で確認済みの
参考値（パイプライン未検証）を記載するに留めている。実データでの検証が済み次第、
本フォルダを正式なデータで更新する。

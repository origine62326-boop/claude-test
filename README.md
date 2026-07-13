# X運用 PDCAツール

X (旧Twitter) のアカウント運用をPDCAサイクルで継続改善するCLIツールです。  
Claude Code 上で完結して動作します。

## 機能概要

```
P - Plan   : PDCAサイクルと目標KPIを設定する
D - Do     : 投稿ログを記録する
C - Check  : 指標を入力し達成状況を確認する
A - Act    : 課題・改善アクションを管理する
R - Report : サイクルサマリーとMarkdownレポートを生成する
```

## 起動方法

```bash
python x_pdca.py
```

Python 3.10以上が必要です（標準ライブラリのみ、追加インストール不要）。

## ディレクトリ構成

```
x_pdca.py          # メインエントリーポイント
modules/
  plan.py          # Plan モジュール
  do.py            # Do モジュール
  check.py         # Check モジュール
  act.py           # Act モジュール
  report.py        # Report モジュール
  storage.py       # JSONストレージ共通処理
  ui.py            # CLI UI ユーティリティ
data/              # 運用データ (JSONファイル, gitignore対象)
  cycles.json      # PDCAサイクル
  posts.json       # 投稿ログ
  metrics.json     # 指標データ
  followers.json   # フォロワー推移
  actions.json     # 改善アクション
```

## PDCAサイクルの使い方

### 1. Plan (計画)
- 新しいサイクルを作成（週次/月次/カスタム）
- KPI目標を設定：投稿数・フォロワー増加数・インプレッション・エンゲージメント率
- コンテンツテーマとハッシュタグを計画

### 2. Do (実行)
- 投稿を記録（内容・タイプ・テーマ・ハッシュタグ・URL）
- 投稿タイプ: テキスト / 画像付き / 動画付き / スレッド / 引用リポスト / リプライ

### 3. Check (確認)
- 投稿ごとの指標を入力（インプレッション・いいね・RT・返信・ブックマーク）
- エンゲージメント率を自動計算
- フォロワー数の推移を記録
- 目標対比の達成状況をビジュアル表示

### 4. Act (改善)
- 振り返りを KPT フレームワークで記録（Keep / Problem / Try / アイデア）
- 改善アクションの優先度管理
- 未完了アクションを次サイクルへ引き継ぎ

### 5. Report (レポート)
- サイクルサマリーの表示
- フォロワー推移のテキストグラフ
- 全サイクル横断比較
- Markdownファイルへのエクスポート

## FX予測ツール (fx_predict.py)

USD/JPY の為替レート変動をLSTM（時系列機械学習モデル）で予測するCLIツールです。
Yahoo Financeから直近の日次終値を取得し、モデルを学習・保存した上で数営業日先のレートを予測します。

### 起動方法

```bash
pip install -r requirements.txt
python fx_predict.py
```

### 主なオプション

```
--forecast-days N   予測する営業日数 (default: 5)
--history-range R   取得する履歴範囲。1y/2y/5y など (default: 2y)
--window N          予測に使う直近日数の窓幅 (default: 20)
--epochs N          学習エポック数 (default: 40)
--retrain           保存済みモデルを使わず再学習する
--no-cache          レート履歴のキャッシュ(6時間)を使わず再取得する
```

学習済みモデルは `data/usdjpy_lstm.keras` に保存され、次回実行時は再学習せずに再利用されます（`--retrain` で強制再学習）。

> ⚠️ 本ツールの予測は過去データに基づく統計的推定であり、投資判断の根拠として利用しないでください。

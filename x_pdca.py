#!/usr/bin/env python3
"""
X運用 PDCAツール + エージェントホグワーツ
==========================================
X (旧Twitter) のアカウント運用をPDCAサイクルで改善するCLIツール。
エージェントワークフロー (ホグワーツ) で投稿制作を自動化。

使い方:
    python x_pdca.py

PDCAモジュール:
    Plan    - PDCAサイクルと目標KPIの設定
    Do      - 投稿ログの記録
    Check   - 指標入力と達成状況確認
    Act     - 課題・改善アクションの管理
    Report  - サイクルレポートの生成とExport

エージェントモジュール (ホグワーツ):
    Research  [ハーマイオニー] - テーマ・ネタ収集・ブリーフィング生成
    Writing   [ルーナ]         - 3スロット × ツリー文案管理
    Quality   [マルフォイ]     - 語尾・構成・トーン品質チェック
    Approval  [あなた]         - 承認ワークフロー (2〜3分)
    Schedule  [ロン]           - 7時・18時・21時 投稿スケジュール
    Monitor   [スネイプ]       - 全体監視・重複検出・改善提案
"""

import sys

from modules import ui
from modules.plan     import get_active_cycle
from modules          import plan, do, check, act, report
from modules          import research, writing, quality, approval, schedule, monitor


def _show_agent_status():
    """エージェントパイプラインの簡易ステータスを表示"""
    from modules.writing  import _load_drafts
    from modules.schedule import _load_schedule
    from collections import Counter

    drafts   = _load_drafts()
    sched    = _load_schedule()
    today    = ui.today_str()

    d_counts = Counter(d["status"] for d in drafts)
    s_today  = [s for s in sched if s["post_date"] == today]
    posted_today = sum(1 for s in s_today if s["status"] in ("posted", "measured"))

    parts = []
    if d_counts.get("review"):
        parts.append(f"{ui.Color.YELLOW}承認待ち:{d_counts['review']}件{ui.Color.RESET}")
    if d_counts.get("rejected"):
        parts.append(f"{ui.Color.RED}却下:{d_counts['rejected']}件{ui.Color.RESET}")
    if s_today:
        parts.append(f"{ui.Color.GREEN}本日投稿:{posted_today}/{len(s_today)}{ui.Color.RESET}")

    if parts:
        print(f"  エージェント: {' | '.join(parts)}")


def main():
    ui.header("X運用 PDCA + エージェントホグワーツ", ui.Color.CYAN)
    print(f"  {ui.Color.DIM}X運用をPDCAサイクル × エージェントワークフローで改善{ui.Color.RESET}")

    # アクティブサイクルを表示
    active = get_active_cycle()
    if active:
        print(f"\n  {ui.Color.GREEN}アクティブサイクル:{ui.Color.RESET} {active['name']}")
        print(f"  {ui.Color.DIM}{active['start_date']} ~ {active['end_date']}{ui.Color.RESET}")
    else:
        print(f"\n  {ui.Color.YELLOW}アクティブなサイクルがありません{ui.Color.RESET}")
        print(f"  {ui.Color.DIM}Planメニューから新しいサイクルを作成してください{ui.Color.RESET}")

    _show_agent_status()

    while True:
        choice = ui.menu("メインメニュー", [
            ("", f"{ui.Color.BOLD}── PDCA ──────────────────────────{ui.Color.RESET}"),
            ("P", "Plan     - 計画 (目標・サイクル設定)"),
            ("D", "Do       - 実行 (投稿ログ記録)"),
            ("C", "Check    - 確認 (指標入力・達成確認)"),
            ("A", "Act      - 改善 (課題・改善アクション)"),
            ("R", "Report   - レポート (サマリー・Export)"),
            ("", f"{ui.Color.BOLD}── エージェント (ホグワーツ) ──────{ui.Color.RESET}"),
            ("1", "Research - リサーチ・分析 [ハーマイオニー]"),
            ("2", "Writing  - ライティング  [ルーナ]"),
            ("3", "Quality  - 品質チェック  [マルフォイ]"),
            ("4", "Approval - あなたの承認"),
            ("5", "Schedule - 投稿スケジュール [ロン]"),
            ("6", "Monitor  - 監視・改善提案 [スネイプ]"),
            ("Q", "終了"),
        ])

        if choice == "P":
            plan.run()
        elif choice == "D":
            do.run()
        elif choice == "C":
            check.run()
        elif choice == "A":
            act.run()
        elif choice == "R":
            report.run()
        elif choice == "1":
            research.run()
        elif choice == "2":
            writing.run()
        elif choice == "3":
            quality.run()
        elif choice == "4":
            approval.run()
        elif choice == "5":
            schedule.run()
        elif choice == "6":
            monitor.run()
        elif choice == "Q":
            print(f"\n{ui.Color.DIM}X PDCA ツールを終了します。お疲れ様でした！{ui.Color.RESET}\n")
            sys.exit(0)
        elif choice == "":
            continue  # セパレーター行はスキップ

        # メニューに戻るたびにステータスを更新
        _show_agent_status()


if __name__ == "__main__":
    main()

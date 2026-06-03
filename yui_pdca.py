#!/usr/bin/env python3
"""
朝5時の結衣 - X運用PDCAツール
==============================
「夜勤帰りの孤独を発信する女性」アカウントの運用管理。

コンセプト : 朝5時に帰宅する工場女子・夜勤帰りの孤独世界観
ポジション : 競合(OL/JD/地雷)と被らない差別化85点
戦略       : 物語 > エロ  /  投稿比率 70%日常 20%恋愛 10%DMM
KPI目標    : 30日→300フォロワー  90日→1000  180日→5000

使い方:
    python yui_pdca.py
"""

import sys

from modules import ui
from modules_yui import plan, do, check, act, report, content, dmm, worldcheck
from modules_yui.plan import get_active_cycle


def main():
    ui.header("朝5時の結衣  X運用PDCAツール", ui.Color.RED)
    print(f"  {ui.Color.YELLOW}「夜勤帰りの孤独を発信する女性」{ui.Color.RESET}")
    print(f"  {ui.Color.DIM}みんなが起きる頃に私は寝る。{ui.Color.RESET}")

    active = get_active_cycle()
    if active:
        print(f"\n  {ui.Color.GREEN}アクティブサイクル:{ui.Color.RESET} {active['name']}")
        print(f"  {ui.Color.DIM}{active['start_date']} ~ {active['end_date']}{ui.Color.RESET}")

        # 進捗をワンライン表示
        from modules_yui.do import get_posts_for_cycle
        posts = get_posts_for_cycle(active["id"])
        goal_posts = active["goals"].get("posts", 0)
        bar_len = min(len(posts) * 20 // max(goal_posts, 1), 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        pct = round(len(posts) / max(goal_posts, 1) * 100)
        print(f"  {ui.Color.CYAN}投稿進捗:{ui.Color.RESET} {bar} {len(posts)}/{goal_posts}件 ({pct}%)")
    else:
        print(f"\n  {ui.Color.YELLOW}アクティブなサイクルがありません{ui.Color.RESET}")
        print(f"  {ui.Color.DIM}Planから30日テストサイクルを作成してください{ui.Color.RESET}")

    while True:
        choice = ui.menu("メインメニュー", [
            ("P", "Plan       - 計画 (サイクル・KPI設定)"),
            ("D", "Do         - 実行 (投稿記録・比率確認)"),
            ("C", "Check      - 確認 (指標入力・達成状況)"),
            ("A", "Act        - 改善 (課題・アクション管理)"),
            ("R", "Report     - レポート (サマリー・Export)"),
            ("I", "Content    - コンテンツ (テンプレ・フック文)"),
            ("M", "DMM        - アフィリエイト管理"),
            ("W", "WorldCheck - 世界観チェッカー"),
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
        elif choice == "I":
            content.run()
        elif choice == "M":
            dmm.run()
        elif choice == "W":
            worldcheck.run()
        elif choice == "Q":
            print(f"\n{ui.Color.DIM}お疲れ様でした。朝5時の帰り道も気をつけて。{ui.Color.RESET}\n")
            sys.exit(0)


if __name__ == "__main__":
    main()

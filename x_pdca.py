#!/usr/bin/env python3
"""
X運用 PDCAツール
================
X (旧Twitter) のアカウント運用をPDCAサイクルで改善するCLIツール。

使い方:
    python x_pdca.py

モジュール構成:
    Plan  - PDCAサイクルと目標KPIの設定
    Do    - 投稿ログの記録
    Check - 指標入力と達成状況確認
    Act   - 課題・改善アクションの管理
    Report- サイクルレポートの生成とExport
"""

import sys

from modules import ui
from modules.plan   import get_active_cycle
from modules        import plan, do, check, act, report


def main():
    ui.header("X運用 PDCAツール", ui.Color.CYAN)
    print(f"  {ui.Color.DIM}X (Twitter) 運用をPDCAサイクルで改善{ui.Color.RESET}")

    # アクティブサイクルを表示
    active = get_active_cycle()
    if active:
        print(f"\n  {ui.Color.GREEN}アクティブサイクル:{ui.Color.RESET} {active['name']}")
        print(f"  {ui.Color.DIM}{active['start_date']} ~ {active['end_date']}{ui.Color.RESET}")
    else:
        print(f"\n  {ui.Color.YELLOW}アクティブなサイクルがありません{ui.Color.RESET}")
        print(f"  {ui.Color.DIM}Planメニューから新しいサイクルを作成してください{ui.Color.RESET}")

    while True:
        choice = ui.menu("メインメニュー", [
            ("P", "Plan   - 計画 (目標・サイクル設定)"),
            ("D", "Do     - 実行 (投稿ログ記録)"),
            ("C", "Check  - 確認 (指標入力・達成確認)"),
            ("A", "Act    - 改善 (課題・改善アクション)"),
            ("R", "Report - レポート (サマリー・Export)"),
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
        elif choice == "Q":
            print(f"\n{ui.Color.DIM}X PDCA ツールを終了します。お疲れ様でした！{ui.Color.RESET}\n")
            sys.exit(0)


if __name__ == "__main__":
    main()

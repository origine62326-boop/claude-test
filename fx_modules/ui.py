"""
FX予測ツール用の表示ユーティリティ
"""


class Color:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    DIM    = "\033[2m"


def header(text: str):
    width = 56
    print(f"\n{Color.CYAN}{Color.BOLD}{'=' * width}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}  {text}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{'=' * width}{Color.RESET}")


def section(text: str):
    print(f"\n{Color.YELLOW}{Color.BOLD}--- {text} ---{Color.RESET}")


def success(text: str):
    print(f"{Color.GREEN}✓ {text}{Color.RESET}")


def error(text: str):
    print(f"{Color.RED}✗ {text}{Color.RESET}")


def info(text: str):
    print(f"{Color.BLUE}  {text}{Color.RESET}")

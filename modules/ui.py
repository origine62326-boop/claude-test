"""
共通UI/表示ユーティリティ
"""

from datetime import datetime


# ANSIカラーコード
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


def header(text: str, color: str = Color.CYAN):
    width = 52
    print(f"\n{color}{Color.BOLD}{'=' * width}{Color.RESET}")
    print(f"{color}{Color.BOLD}  {text}{Color.RESET}")
    print(f"{color}{Color.BOLD}{'=' * width}{Color.RESET}")


def section(text: str):
    print(f"\n{Color.YELLOW}{Color.BOLD}--- {text} ---{Color.RESET}")


def success(text: str):
    print(f"{Color.GREEN}✓ {text}{Color.RESET}")


def error(text: str):
    print(f"{Color.RED}✗ {text}{Color.RESET}")


def info(text: str):
    print(f"{Color.BLUE}  {text}{Color.RESET}")


def prompt(text: str, default: str = "") -> str:
    if default:
        result = input(f"{Color.WHITE}{text} [{default}]: {Color.RESET}").strip()
        return result if result else default
    return input(f"{Color.WHITE}{text}: {Color.RESET}").strip()


def prompt_int(text: str, default: int | None = None) -> int | None:
    hint = f" [{default}]" if default is not None else ""
    raw = input(f"{Color.WHITE}{text}{hint}: {Color.RESET}").strip()
    if not raw and default is not None:
        return default
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        error("数値を入力してください")
        return prompt_int(text, default)


def prompt_float(text: str, default: float | None = None) -> float | None:
    hint = f" [{default}]" if default is not None else ""
    raw = input(f"{Color.WHITE}{text}{hint}: {Color.RESET}").strip()
    if not raw and default is not None:
        return default
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        error("数値を入力してください")
        return prompt_float(text, default)


def menu(title: str, options: list[tuple[str, str]]) -> str:
    """
    メニューを表示してキーを返す
    options: [(key, label), ...]
    """
    section(title)
    for key, label in options:
        print(f"  {Color.CYAN}{Color.BOLD}{key}{Color.RESET}. {label}")
    print()
    valid_keys = [k for k, _ in options]
    while True:
        choice = input(f"{Color.WHITE}選択 ({'/'.join(valid_keys)}): {Color.RESET}").strip()
        if choice in valid_keys:
            return choice
        error(f"有効な選択肢: {', '.join(valid_keys)}")


def table(headers: list[str], rows: list[list], widths: list[int] | None = None):
    if not rows:
        info("データがありません")
        return
    if widths is None:
        widths = [max(len(str(h)), max(len(str(r[i])) for r in rows)) + 2
                  for i, h in enumerate(headers)]
    header_row = "  ".join(str(h).ljust(w) for h, w in zip(headers, widths))
    print(f"\n{Color.BOLD}{header_row}{Color.RESET}")
    print(Color.DIM + "-" * sum(w + 2 for w in widths) + Color.RESET)
    for row in rows:
        print("  ".join(str(c).ljust(w) for c, w in zip(row, widths)))


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")

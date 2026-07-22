"""pytest共通設定。trading-system直下をsys.pathへ追加し、analysis.xxx を import可能にする。"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

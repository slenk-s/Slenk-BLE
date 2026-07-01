"""src/main.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app import BLEApplication


def main():
    app = BLEApplication()
    app.run()


if __name__ == "__main__":
    main()
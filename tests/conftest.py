"""Shared fixtures for BLE tests."""

import sys
from pathlib import Path

# Ensure src/ is importable
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

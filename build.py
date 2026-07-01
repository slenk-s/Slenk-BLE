"""PyInstaller build script for BLE Upper Monitor.

Usage:
    pip install pyinstaller
    python build.py

Or manually:
    pyinstaller --onefile --windowed --name "BLE-Monitor" --add-data "src:src" src/main.py
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    src_dir = Path(__file__).parent / "src"
    main_script = src_dir / "main.py"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "BLE-Monitor",
        "--add-data", f"{src_dir}{os.pathsep}src",
        "--exclude", "PyQt5",
        "--hidden-import", "qasync",
        "--hidden-import", "bleak",
        "--hidden-import", "bleak.backends.winrt",
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "pyqtgraph",
        "--clean",
        "--noconfirm",
        str(main_script),
    ]

    print("Running PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    if result.returncode == 0:
        print("\nBuild successful! Executable at dist/BLE-Monitor.exe")
    else:
        print(f"\nBuild failed with exit code {result.returncode}")
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()

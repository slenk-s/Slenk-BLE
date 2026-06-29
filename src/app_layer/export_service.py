"""src/app_layer/export_service.py"""

import csv
import sqlite3
from pathlib import Path

from src.app_layer.data_cache import DataCache


class DataExportService:
    """导出到 CSV / Excel / SQLite。"""

    def __init__(self, data_cache: DataCache):
        self._cache = data_cache

    def to_csv(self, file_path: str | Path, address: str | None = None) -> int:
        data = self._cache.get_all(limit=100_000)
        if address:
            data = [d for d in data if d.address == address]
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["时间", "设备", "HEX数据", "ASCII", "解析结果"])
            for d in data:
                writer.writerow([
                    d.timestamp.isoformat(),
                    d.address,
                    d.raw_data.hex(" ").upper(),
                    d.raw_data.decode("ascii", errors="replace"),
                    str(d.parsed) if d.parsed else "",
                ])
        return len(data)

    def to_sqlite(self, file_path: str | Path, address: str | None = None) -> int:
        data = self._cache.get_all(limit=100_000)
        if address:
            data = [d for d in data if d.address == address]
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ble_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                device_address TEXT NOT NULL,
                raw_hex TEXT NOT NULL,
                ascii TEXT,
                parsed TEXT
            )
        """)
        count = 0
        for d in data:
            conn.execute(
                "INSERT INTO ble_data (timestamp, device_address, raw_hex, ascii, parsed) VALUES (?, ?, ?, ?, ?)",
                (
                    d.timestamp.isoformat(),
                    d.address,
                    d.raw_data.hex(" ").upper(),
                    d.raw_data.decode("ascii", errors="replace"),
                    str(d.parsed) if d.parsed else "",
                ),
            )
            count += 1
        conn.commit()
        conn.close()
        return count

    def _sanitize(self, text: str) -> str:
        """移除 openpyxl 不支持的 XML 控制字符（保留 \\t \\n \\r）。"""
        import re

        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)

    def to_excel(self, file_path: str | Path, address: str | None = None) -> int:
        import pandas as pd

        data = self._cache.get_all(limit=100_000)
        if address:
            data = [d for d in data if d.address == address]
        records = [
            {
                "时间": d.timestamp.isoformat(),
                "设备": d.address,
                "HEX": d.raw_data.hex(" ").upper(),
                "ASCII": self._sanitize(
                    d.raw_data.decode("ascii", errors="replace")
                ),
                "解析": str(d.parsed) if d.parsed else "",
            }
            for d in data
        ]
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(records)
        df.to_excel(str(path), index=False, engine="openpyxl")
        return len(data)

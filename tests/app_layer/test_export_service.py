"""Tests for DataExportService — CSV / SQLite / Excel 导出。"""

from datetime import datetime
from pathlib import Path

import pytest

from src.app_layer.data_cache import DataCache
from src.app_layer.export_service import DataExportService


@pytest.fixture
def cache() -> DataCache:
    """带测试数据的 DataCache。"""
    c = DataCache()
    c.push("AA:BB:CC:DD:EE:01", b"\x01\x02\x03", {"temp": 22.5})
    c.push("AA:BB:CC:DD:EE:01", b"\x04\x05", {"temp": 23.0})
    c.push("AA:BB:CC:DD:EE:02", b"\x0a\x0b", {"humidity": 60})
    return c


@pytest.fixture
def service(cache: DataCache) -> DataExportService:
    return DataExportService(cache)


class TestToCsv:
    """CSV 导出功能测试。"""

    def test_export_all_data(self, service: DataExportService, tmp_path: Path) -> None:
        file_path = tmp_path / "export.csv"
        count = service.to_csv(file_path)
        assert count == 3
        assert file_path.exists()
        content = file_path.read_text(encoding="utf-8")
        # 应有 BOM（读取时不剥离）
        assert content.startswith("﻿")
        # 表头
        assert "时间" in content
        assert "HEX数据" in content
        assert "ASCII" in content
        assert "解析结果" in content
        # 所有三条数据都应出现在内容中
        assert "AA:BB:CC:DD:EE:01" in content
        assert "AA:BB:CC:DD:EE:02" in content

    def test_export_filter_by_address(
        self, service: DataExportService, tmp_path: Path
    ) -> None:
        file_path = tmp_path / "filtered.csv"
        count = service.to_csv(file_path, address="AA:BB:CC:DD:EE:01")
        assert count == 2
        content = file_path.read_text(encoding="utf-8-sig")
        lines = content.strip().split("\n")
        assert len(lines) == 3  # header + 2 rows

    def test_export_empty_cache(self, tmp_path: Path) -> None:
        svc = DataExportService(DataCache())
        file_path = tmp_path / "empty.csv"
        count = svc.to_csv(file_path)
        assert count == 0
        content = file_path.read_text(encoding="utf-8")
        assert content.startswith("﻿")
        lines = content.strip().split("\n")
        assert len(lines) == 1  # header only

    def test_export_creates_parent_dir(
        self, service: DataExportService, tmp_path: Path
    ) -> None:
        file_path = tmp_path / "sub" / "dir" / "export.csv"
        count = service.to_csv(file_path)
        assert count == 3
        assert file_path.exists()

    def test_invalid_address_returns_zero(
        self, service: DataExportService, tmp_path: Path
    ) -> None:
        count = service.to_csv(tmp_path / "none.csv", address="00:00:00:00:00:00")
        assert count == 0
        content = (tmp_path / "none.csv").read_text(encoding="utf-8")
        assert content.startswith("﻿")


class TestToSqlite:
    """SQLite 导出功能测试。"""

    def test_export_all_data(self, service: DataExportService, tmp_path: Path) -> None:
        file_path = tmp_path / "export.db"
        count = service.to_sqlite(file_path)
        assert count == 3
        assert file_path.exists()
        # 验证数据库内容
        import sqlite3

        conn = sqlite3.connect(str(file_path))
        rows = conn.execute("SELECT COUNT(*) FROM ble_data").fetchone()[0]
        assert rows == 3
        devices = conn.execute(
            "SELECT DISTINCT device_address FROM ble_data"
        ).fetchall()
        assert len(devices) == 2
        conn.close()

    def test_export_filter_by_address(
        self, service: DataExportService, tmp_path: Path
    ) -> None:
        file_path = tmp_path / "filtered.db"
        count = service.to_sqlite(file_path, address="AA:BB:CC:DD:EE:02")
        assert count == 1

        import sqlite3

        conn = sqlite3.connect(str(file_path))
        rows = conn.execute("SELECT COUNT(*) FROM ble_data").fetchone()[0]
        assert rows == 1
        addr = conn.execute(
            "SELECT device_address FROM ble_data LIMIT 1"
        ).fetchone()[0]
        assert addr == "AA:BB:CC:DD:EE:02"
        conn.close()

    def test_export_empty_cache(self, tmp_path: Path) -> None:
        svc = DataExportService(DataCache())
        file_path = tmp_path / "empty.db"
        count = svc.to_sqlite(file_path)
        assert count == 0

        import sqlite3

        conn = sqlite3.connect(str(file_path))
        rows = conn.execute("SELECT COUNT(*) FROM ble_data").fetchone()[0]
        assert rows == 0
        conn.close()

    def test_export_idempotent(
        self, service: DataExportService, tmp_path: Path
    ) -> None:
        """多次导出到同一文件不应重复数据（覆盖式）。"""
        file_path = tmp_path / "dup.db"
        service.to_sqlite(file_path)
        count2 = service.to_sqlite(file_path)
        assert count2 == 3  # 覆盖式导出

    def test_export_creates_parent_dir(
        self, service: DataExportService, tmp_path: Path
    ) -> None:
        file_path = tmp_path / "nested" / "path" / "data.db"
        count = service.to_sqlite(file_path)
        assert count == 3
        assert file_path.exists()


class TestToExcel:
    """Excel 导出功能测试。"""

    def test_export_all_data(self, service: DataExportService, tmp_path: Path) -> None:
        file_path = tmp_path / "export.xlsx"
        count = service.to_excel(file_path)
        assert count == 3
        assert file_path.exists()
        # 验证文件大小非零
        assert file_path.stat().st_size > 0

    def test_export_filter_by_address(
        self, service: DataExportService, tmp_path: Path
    ) -> None:
        file_path = tmp_path / "filtered.xlsx"
        count = service.to_excel(file_path, address="AA:BB:CC:DD:EE:01")
        assert count == 2
        assert file_path.exists()

    def test_export_empty_cache(self, tmp_path: Path) -> None:
        svc = DataExportService(DataCache())
        file_path = tmp_path / "empty.xlsx"
        count = svc.to_excel(file_path)
        assert count == 0
        assert file_path.exists()

    def test_export_creates_parent_dir(
        self, service: DataExportService, tmp_path: Path
    ) -> None:
        file_path = tmp_path / "a" / "b" / "data.xlsx"
        count = service.to_excel(file_path)
        assert count == 3
        assert file_path.exists()

    def test_export_raw_hex_value(
        self, service: DataExportService, tmp_path: Path
    ) -> None:
        """验证 HEX 数据格式正确。"""
        file_path = tmp_path / "hex_check.xlsx"
        service.to_excel(file_path)
        import pandas as pd

        df = pd.read_excel(file_path, engine="openpyxl")
        assert len(df) == 3
        assert "HEX" in df.columns
        # 数据应包含正确格式的 HEX
        hex_vals = df["HEX"].tolist()
        assert any("01 02 03" in str(v) for v in hex_vals)

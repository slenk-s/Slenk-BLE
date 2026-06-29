"""tests/test_manager.py"""

import pytest
from src.ble.manager import BLEManager


def test_manager_init():
    mgr = BLEManager()
    assert mgr.scanner is not None
    assert mgr.connector is not None
    assert mgr.gatt is not None
    assert mgr.signals is not None
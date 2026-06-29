"""tests/test_scanner.py"""

import pytest
from src.ble.signals import BleSignals
from src.ble.scanner import Scanner


def test_scanner_initial_state():
    signals = BleSignals()
    scanner = Scanner(signals)
    assert scanner.discovered_devices == []
    assert scanner.is_scanning is False


@pytest.mark.asyncio
async def test_scanner_start_stop():
    signals = BleSignals()
    scanner = Scanner(signals)
    await scanner.start(timeout=5)
    assert scanner.is_scanning is True
    scanner.stop()
    assert scanner.is_scanning is False
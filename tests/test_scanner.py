"""tests/test_scanner.py"""

import pytest
from unittest.mock import AsyncMock, patch
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
    mock_bleak = AsyncMock()
    mock_bleak.start = AsyncMock()
    mock_bleak.stop = AsyncMock()

    with patch("src.ble.scanner.BleakScanner", return_value=mock_bleak):
        await scanner.start(timeout=5)
    assert scanner.is_scanning is True
    scanner.stop()
    assert scanner.is_scanning is False
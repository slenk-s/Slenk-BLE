"""tests/test_connector.py"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.ble.signals import BleSignals
from src.ble.connector import Connector


def _make_mock_client(is_connected=False, address="MockDevice"):
    """Helper to create a BleakClient mock with controllable is_connected."""
    client = MagicMock()
    client.address = address
    client.is_connected = is_connected
    client.connect = AsyncMock(side_effect=lambda: setattr(client, "is_connected", True))
    client.disconnect = AsyncMock(side_effect=lambda: setattr(client, "is_connected", False))
    return client


def test_connector_initial_state():
    signals = BleSignals()
    conn = Connector(signals)
    assert conn.connected_devices == []
    assert conn.max_connections == 5


def test_connector_custom_max():
    signals = BleSignals()
    conn = Connector(signals, max_connections=2)
    assert conn.max_connections == 2


def test_connector_max_reached():
    signals = BleSignals()
    conn = Connector(signals, max_connections=2)
    conn._clients = {"addr1": None, "addr2": None}
    assert conn._at_max_capacity() is True


def test_connector_not_at_max():
    signals = BleSignals()
    conn = Connector(signals, max_connections=2)
    conn._clients = {"addr1": None}
    assert conn._at_max_capacity() is False


@pytest.mark.asyncio
async def test_connect_success():
    signals = BleSignals()
    conn = Connector(signals)

    mock_client = _make_mock_client()

    with patch("src.ble.connector.BleakClient", return_value=mock_client):
        result = await conn.connect("AA:BB:CC:DD:EE:FF")

    assert result is True
    assert conn.is_connected("AA:BB:CC:DD:EE:FF") is True
    assert "AA:BB:CC:DD:EE:FF" in conn._clients
    mock_client.connect.assert_awaited_once()


@pytest.mark.asyncio
async def test_connect_already_connected():
    signals = BleSignals()
    conn = Connector(signals)

    mock_client = _make_mock_client(is_connected=True)
    conn._clients["AA:BB:CC:DD:EE:FF"] = mock_client

    result = await conn.connect("AA:BB:CC:DD:EE:FF")

    assert result is True
    mock_client.connect.assert_not_called()


@pytest.mark.asyncio
async def test_connect_at_max_capacity():
    signals = BleSignals()
    conn = Connector(signals, max_connections=1)
    conn._clients["addr1"] = _make_mock_client(is_connected=True)

    result = await conn.connect("AA:BB:CC:DD:EE:FF")

    assert result is False


@pytest.mark.asyncio
async def test_connect_failure_emits_signal(qtbot):
    signals = BleSignals()
    conn = Connector(signals)

    mock_client = _make_mock_client()
    mock_client.connect = AsyncMock(side_effect=Exception("Connection timeout"))

    with patch("src.ble.connector.BleakClient", return_value=mock_client):
        with qtbot.wait_signal(signals.connection_failed, timeout=2000):
            result = await conn.connect("AA:BB:CC:DD:EE:FF")

    assert result is False


@pytest.mark.asyncio
async def test_disconnect_success():
    signals = BleSignals()
    conn = Connector(signals)

    mock_client = _make_mock_client(is_connected=True)
    conn._clients["AA:BB:CC:DD:EE:FF"] = mock_client

    result = await conn.disconnect("AA:BB:CC:DD:EE:FF")

    assert result is True
    assert "AA:BB:CC:DD:EE:FF" not in conn._clients
    mock_client.disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_disconnect_not_connected():
    signals = BleSignals()
    conn = Connector(signals)

    result = await conn.disconnect("AA:BB:CC:DD:EE:FF")

    assert result is False


@pytest.mark.asyncio
async def test_disconnect_all():
    signals = BleSignals()
    conn = Connector(signals)

    mock1 = _make_mock_client(is_connected=True)
    mock2 = _make_mock_client(is_connected=True)

    conn._clients["addr1"] = mock1
    conn._clients["addr2"] = mock2

    await conn.disconnect_all()

    assert conn.connected_devices == []
    mock1.disconnect.assert_awaited_once()
    mock2.disconnect.assert_awaited_once()


def test_is_connected_true():
    signals = BleSignals()
    conn = Connector(signals)
    mock_client = _make_mock_client(is_connected=True)
    conn._clients["AA:BB:CC:DD:EE:FF"] = mock_client

    assert conn.is_connected("AA:BB:CC:DD:EE:FF") is True


def test_is_connected_false_not_in_pool():
    signals = BleSignals()
    conn = Connector(signals)

    assert conn.is_connected("AA:BB:CC:DD:EE:FF") is False


def test_is_connected_false_disconnected():
    signals = BleSignals()
    conn = Connector(signals)
    mock_client = _make_mock_client(is_connected=False)
    conn._clients["AA:BB:CC:DD:EE:FF"] = mock_client

    assert conn.is_connected("AA:BB:CC:DD:EE:FF") is False


def test_get_client_returns_client():
    signals = BleSignals()
    conn = Connector(signals)
    mock_client = _make_mock_client()
    conn._clients["AA:BB:CC:DD:EE:FF"] = mock_client

    assert conn.get_client("AA:BB:CC:DD:EE:FF") is mock_client


def test_get_client_returns_none():
    signals = BleSignals()
    conn = Connector(signals)

    assert conn.get_client("AA:BB:CC:DD:EE:FF") is None


def test_connected_devices_property():
    signals = BleSignals()
    conn = Connector(signals)
    mock_client = _make_mock_client(is_connected=True, address="MockDevice")
    conn._clients["AA:BB:CC:DD:EE:FF"] = mock_client

    devices = conn.connected_devices
    assert len(devices) == 1
    assert devices[0]["address"] == "AA:BB:CC:DD:EE:FF"
    assert devices[0]["name"] == "MockDevice"

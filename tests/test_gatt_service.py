"""tests/test_gatt_service.py"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.ble.signals import BleSignals
from src.ble.connector import Connector


def _make_mock_client():
    """Helper to create a BleakClient mock with async GATT methods."""
    client = MagicMock()
    client.is_connected = True
    client.get_services = AsyncMock()
    client.read_gatt_char = AsyncMock(return_value=b"test-data")
    client.write_gatt_char = AsyncMock()
    client.start_notify = AsyncMock()
    client.stop_notify = AsyncMock()
    return client


def test_gatt_service_init():
    from src.ble.gatt_service import GattService

    signals = BleSignals()
    connector = Connector(signals)
    gatt = GattService(signals, connector)

    assert gatt is not None
    assert gatt._signals is signals
    assert gatt._connector is connector
    assert gatt._notification_handles == {}


def test_gatt_service_notification_handles_init():
    from src.ble.gatt_service import GattService

    signals = BleSignals()
    connector = Connector(signals)
    gatt = GattService(signals, connector)

    assert isinstance(gatt._notification_handles, dict)


@pytest.mark.asyncio
async def test_discover_services_success(qtbot):
    from src.ble.gatt_service import GattService

    signals = BleSignals()
    connector = Connector(signals)
    gatt = GattService(signals, connector)

    mock_char = MagicMock()
    mock_char.uuid = "00002a00-0000-1000-8000-00805f9b34fb"
    mock_char.description = "Device Name"
    mock_char.properties = ["read", "write"]

    mock_service = MagicMock()
    mock_service.uuid = "0000180a-0000-1000-8000-00805f9b34fb"
    mock_service.description = "Device Information"
    mock_service.characteristics = [mock_char]

    mock_client = _make_mock_client()
    mock_client.get_services.return_value = [mock_service]
    connector._clients["AA:BB:CC:DD:EE:FF"] = mock_client

    with qtbot.wait_signal(signals.service_discovered, timeout=2000) as blocker:
        result = await gatt.discover_services("AA:BB:CC:DD:EE:FF")

    assert len(result) == 1
    assert result[0]["uuid"] == "0000180a-0000-1000-8000-00805f9b34fb"
    assert result[0]["description"] == "Device Information"
    assert len(result[0]["characteristics"]) == 1
    assert result[0]["characteristics"][0]["uuid"] == "00002a00-0000-1000-8000-00805f9b34fb"
    assert "read" in result[0]["characteristics"][0]["properties"]
    assert "write" in result[0]["characteristics"][0]["properties"]

    # Signal emitted
    emitted_address, emitted_services = blocker.args
    assert emitted_address == "AA:BB:CC:DD:EE:FF"
    assert emitted_services == result
    mock_client.get_services.assert_awaited_once()


@pytest.mark.asyncio
async def test_discover_services_not_connected():
    from src.ble.gatt_service import GattService

    signals = BleSignals()
    connector = Connector(signals)
    gatt = GattService(signals, connector)

    with pytest.raises(ConnectionError, match="未连接"):
        await gatt.discover_services("AA:BB:CC:DD:EE:FF")


@pytest.mark.asyncio
async def test_read_characteristic_success():
    from src.ble.gatt_service import GattService

    signals = BleSignals()
    connector = Connector(signals)
    gatt = GattService(signals, connector)

    mock_client = _make_mock_client()
    connector._clients["AA:BB:CC:DD:EE:FF"] = mock_client

    data = await gatt.read_characteristic(
        "AA:BB:CC:DD:EE:FF",
        "00002a00-0000-1000-8000-00805f9b34fb",
    )

    assert data == b"test-data"
    mock_client.read_gatt_char.assert_awaited_once_with(
        "00002a00-0000-1000-8000-00805f9b34fb"
    )


@pytest.mark.asyncio
async def test_read_characteristic_not_connected():
    from src.ble.gatt_service import GattService

    signals = BleSignals()
    connector = Connector(signals)
    gatt = GattService(signals, connector)

    with pytest.raises(ConnectionError, match="未连接"):
        await gatt.read_characteristic("AA:BB:CC:DD:EE:FF", "some-uuid")


@pytest.mark.asyncio
async def test_write_characteristic_success():
    from src.ble.gatt_service import GattService

    signals = BleSignals()
    connector = Connector(signals)
    gatt = GattService(signals, connector)

    mock_client = _make_mock_client()
    connector._clients["AA:BB:CC:DD:EE:FF"] = mock_client

    await gatt.write_characteristic(
        "AA:BB:CC:DD:EE:FF",
        "00002a00-0000-1000-8000-00805f9b34fb",
        b"\x01\x02\x03",
    )

    mock_client.write_gatt_char.assert_awaited_once_with(
        "00002a00-0000-1000-8000-00805f9b34fb",
        b"\x01\x02\x03",
    )


@pytest.mark.asyncio
async def test_write_characteristic_not_connected():
    from src.ble.gatt_service import GattService

    signals = BleSignals()
    connector = Connector(signals)
    gatt = GattService(signals, connector)

    with pytest.raises(ConnectionError, match="未连接"):
        await gatt.write_characteristic("AA:BB:CC:DD:EE:FF", "some-uuid", b"data")


@pytest.mark.asyncio
async def test_subscribe_success(qtbot):
    from src.ble.gatt_service import GattService

    signals = BleSignals()
    connector = Connector(signals)
    gatt = GattService(signals, connector)

    mock_client = _make_mock_client()
    connector._clients["AA:BB:CC:DD:EE:FF"] = mock_client

    await gatt.subscribe(
        "AA:BB:CC:DD:EE:FF",
        "00002a00-0000-1000-8000-00805f9b34fb",
    )

    assert "AA:BB:CC:DD:EE:FF" in gatt._notification_handles
    assert "00002a00-0000-1000-8000-00805f9b34fb" in gatt._notification_handles["AA:BB:CC:DD:EE:FF"]
    mock_client.start_notify.assert_awaited_once()


@pytest.mark.asyncio
async def test_subscribe_not_connected():
    from src.ble.gatt_service import GattService

    signals = BleSignals()
    connector = Connector(signals)
    gatt = GattService(signals, connector)

    with pytest.raises(ConnectionError, match="未连接"):
        await gatt.subscribe("AA:BB:CC:DD:EE:FF", "some-uuid")


@pytest.mark.asyncio
async def test_subscribe_idempotent():
    """Subscribing twice to same char should not call start_notify twice."""
    from src.ble.gatt_service import GattService

    signals = BleSignals()
    connector = Connector(signals)
    gatt = GattService(signals, connector)

    mock_client = _make_mock_client()
    connector._clients["AA:BB:CC:DD:EE:FF"] = mock_client

    await gatt.subscribe("AA:BB:CC:DD:EE:FF", "00002a00-0000-1000-8000-00805f9b34fb")
    await gatt.subscribe("AA:BB:CC:DD:EE:FF", "00002a00-0000-1000-8000-00805f9b34fb")

    mock_client.start_notify.assert_awaited_once()


@pytest.mark.asyncio
async def test_unsubscribe_success():
    from src.ble.gatt_service import GattService

    signals = BleSignals()
    connector = Connector(signals)
    gatt = GattService(signals, connector)

    mock_client = _make_mock_client()
    connector._clients["AA:BB:CC:DD:EE:FF"] = mock_client

    # Subscribe first
    await gatt.subscribe("AA:BB:CC:DD:EE:FF", "00002a00-0000-1000-8000-00805f9b34fb")
    assert len(gatt._notification_handles["AA:BB:CC:DD:EE:FF"]) == 1

    # Unsubscribe
    await gatt.unsubscribe("AA:BB:CC:DD:EE:FF", "00002a00-0000-1000-8000-00805f9b34fb")

    assert len(gatt._notification_handles["AA:BB:CC:DD:EE:FF"]) == 0
    mock_client.stop_notify.assert_awaited_once_with(
        "00002a00-0000-1000-8000-00805f9b34fb"
    )


@pytest.mark.asyncio
async def test_unsubscribe_not_connected():
    from src.ble.gatt_service import GattService

    signals = BleSignals()
    connector = Connector(signals)
    gatt = GattService(signals, connector)

    with pytest.raises(ConnectionError, match="未连接"):
        await gatt.unsubscribe("AA:BB:CC:DD:EE:FF", "some-uuid")


@pytest.mark.asyncio
async def test_notification_callback_emits_data_received(qtbot):
    """Verify the internal notification callback emits data_received signal."""
    from src.ble.gatt_service import GattService

    signals = BleSignals()
    connector = Connector(signals)
    gatt = GattService(signals, connector)

    mock_client = _make_mock_client()
    connector._clients["AA:BB:CC:DD:EE:FF"] = mock_client

    # Capture the callback that was passed to start_notify
    captured_callback = None

    async def _capture_callback(char_uuid, callback, **kwargs):
        nonlocal captured_callback
        captured_callback = callback

    mock_client.start_notify.side_effect = _capture_callback

    await gatt.subscribe("AA:BB:CC:DD:EE:FF", "00002a00-0000-1000-8000-00805f9b34fb")

    assert captured_callback is not None

    # Simulate a notification from the BLE device
    with qtbot.wait_signal(signals.data_received, timeout=2000) as blocker:
        captured_callback(123, b"\xde\xad\xbe\xef")

    emitted_address, emitted_data = blocker.args
    assert emitted_address == "AA:BB:CC:DD:EE:FF"
    assert emitted_data == b"\xde\xad\xbe\xef"

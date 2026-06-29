"""tests/app_layer/test_ota_service.py"""

import hashlib
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from src.app_layer.ota_service import OTAProgress, OTAService


# ── OTAProgress unit tests ──────────────────────────────────────────────


def test_ota_progress_initial_state():
    progress = OTAProgress(total_packets=100)
    assert progress.total_packets == 100
    assert progress.sent_packets == 0
    assert progress.failed_packets == 0
    assert progress.retries == 0
    assert progress.percentage == 0.0
    assert progress.done is False


def test_ota_progress_zero_total():
    progress = OTAProgress(total_packets=0)
    assert progress.percentage == 0.0
    assert progress.done is True


def test_ota_progress_partial():
    progress = OTAProgress(total_packets=100)
    progress.sent_packets = 50
    assert progress.percentage == 50.0
    assert progress.done is False


def test_ota_progress_done():
    progress = OTAProgress(total_packets=100)
    progress.sent_packets = 100
    assert progress.percentage == 100.0
    assert progress.done is True


# ── OTAService unit tests ───────────────────────────────────────────────


@pytest.fixture
def write_handler():
    return AsyncMock()


@pytest.fixture
def firmware_file():
    """Create a temporary firmware binary with known content."""
    data = b"\x00\x01\x02\x03" * 512  # 2048 bytes
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
        f.write(data)
        path = f.name
    yield Path(path)
    Path(path).unlink(missing_ok=True)


@pytest.fixture
def ota_service(write_handler):
    return OTAService(write_handler, mtu=240)


@pytest.mark.asyncio
async def test_start_update_full_flow(ota_service, write_handler, firmware_file):
    """Happy path: all packets sent successfully, completion packets emitted."""
    result = await ota_service.start_update(
        "AA:BB:CC:DD:EE:FF",
        "0000abcd-0000-1000-8000-00805f9b34fb",
        firmware_file,
    )

    # 2048 bytes / 240 mtu = 9 packets (ceiling: 8 full + 1 partial)
    assert result["total_packets"] == 9
    assert result["sent"] == 9
    assert result["failed"] == 0
    assert result["cancelled"] is False
    assert "sha256" in result

    # Verify firmware hash
    expected_sha = hashlib.sha256(firmware_file.read_bytes()).hexdigest()
    assert result["sha256"] == expected_sha

    # Verify write_handler was called: 9 data packets + 2 completion packets
    assert write_handler.call_count == 11

    # Last two calls should be the completion markers
    last_call_args = write_handler.call_args_list[-2]
    assert last_call_args[0][2].startswith(b"\xff")

    final_call_args = write_handler.call_args_list[-1]
    assert final_call_args[0][2] == b"\xfe"


@pytest.mark.asyncio
async def test_start_update_empty_firmware(ota_service, write_handler):
    """No packets sent for empty firmware; only completion markers."""
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as f:
        f.write(b"")
        path = f.name

    try:
        result = await ota_service.start_update(
            "AA:BB:CC:DD:EE:FF",
            "0000abcd-0000-1000-8000-00805f9b34fb",
            path,
        )
        assert result["total_packets"] == 0
        assert result["sent"] == 0
        assert result["failed"] == 0
        assert result["cancelled"] is False
        # Only the 2 completion packets
        assert write_handler.call_count == 2
    finally:
        Path(path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_cancel_during_update(ota_service, write_handler, firmware_file):
    """Cancel aborts the sending loop mid-way."""
    original_send = ota_service._send_packet

    async def cancel_after_few(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 3:
            ota_service.cancel()
        return await original_send(*args, **kwargs)

    call_count = 0
    ota_service._send_packet = cancel_after_few

    result = await ota_service.start_update(
        "AA:BB:CC:DD:EE:FF",
        "0000abcd-0000-1000-8000-00805f9b34fb",
        firmware_file,
    )

    assert result["cancelled"] is True
    assert result["sent"] < result["total_packets"]
    assert result["sent"] > 0
    # Should still send completion packets even when cancelled


@pytest.mark.asyncio
async def test_send_packet_retry_then_succeed(ota_service, write_handler):
    """_send_packet retries up to 3 times and succeeds."""
    ota_service.progress = OTAProgress(total_packets=1)
    # First two calls fail, third succeeds
    write_handler.side_effect = [Exception("write failed"), Exception("write failed"), None]

    result = await ota_service._send_packet(
        "AA:BB:CC:DD:EE:FF",
        "0000abcd-0000-1000-8000-00805f9b34fb",
        0,
        b"\x01\x02\x03",
    )

    assert result is True
    assert write_handler.call_count == 3
    assert ota_service.progress.retries == 2


@pytest.mark.asyncio
async def test_send_packet_all_retries_fail(ota_service, write_handler):
    """After 3 failed attempts, _send_packet returns False."""
    ota_service.progress = OTAProgress(total_packets=1)
    write_handler.side_effect = Exception("persistent error")

    result = await ota_service._send_packet(
        "AA:BB:CC:DD:EE:FF",
        "0000abcd-0000-1000-8000-00805f9b34fb",
        0,
        b"\x01\x02\x03",
    )

    assert result is False
    assert write_handler.call_count == 3
    assert ota_service.progress.retries == 3


@pytest.mark.asyncio
async def test_send_packet_header_format(ota_service, write_handler):
    """Packet header should be big-endian 2-byte sequence number."""
    await ota_service._send_packet(
        "AA:BB:CC:DD:EE:FF",
        "0000abcd-0000-1000-8000-00805f9b34fb",
        0x0102,  # seq = 258
        b"\xde\xad",
    )

    args, _ = write_handler.call_args
    packet = args[2]
    # Header should be 0x01 0x02 (big-endian for 258)
    assert packet[:2] == b"\x01\x02"
    assert packet[2:] == b"\xde\xad"


@pytest.mark.asyncio
async def test_start_update_progress_tracking(ota_service, write_handler, firmware_file):
    """Progress object tracks overall flow accurately."""
    result = await ota_service.start_update(
        "AA:BB:CC:DD:EE:FF",
        "0000abcd-0000-1000-8000-00805f9b34fb",
        firmware_file,
    )

    assert ota_service.progress is not None
    assert ota_service.progress.percentage == 100.0
    assert ota_service.progress.done is True
    assert ota_service.progress.sent_packets == result["sent"]


@pytest.mark.asyncio
async def test_write_handler_error_marked_as_failed(ota_service, write_handler, firmware_file):
    """When a packet exhausts retries, it increments failed_packets."""
    # Track which sequence numbers should fail for ALL their retries.
    # We examine the 2-byte header in the packet to determine the seq.
    fail_seqs = {3, 6}  # Packets with these sequence numbers will fail permanently

    def extract_seq_from_args(*args):
        packet = args[2]
        return int.from_bytes(packet[:2], "big")

    async def flaky_write(*args, **kwargs):
        seq = extract_seq_from_args(*args)
        if seq in fail_seqs:
            raise Exception("connection lost")
        return None

    write_handler.side_effect = flaky_write

    result = await ota_service.start_update(
        "AA:BB:CC:DD:EE:FF",
        "0000abcd-0000-1000-8000-00805f9b34fb",
        firmware_file,
    )

    # 2 packets failed (each exhausting 3 retries)
    assert result["failed"] == 2
    assert result["sent"] == result["total_packets"] - result["failed"]

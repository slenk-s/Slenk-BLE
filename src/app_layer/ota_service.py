"""src/app_layer/ota_service.py"""

import asyncio
import hashlib
from pathlib import Path

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class OTAProgress:
    """Tracks OTA firmware update progress."""

    def __init__(self, total_packets: int):
        self.total_packets = total_packets
        self.sent_packets = 0
        self.failed_packets = 0
        self.retries = 0

    @property
    def percentage(self) -> float:
        return (self.sent_packets / self.total_packets * 100) if self.total_packets > 0 else 0.0

    @property
    def done(self) -> bool:
        return self.sent_packets >= self.total_packets


class OTAService:
    """BLE OTA firmware upgrade service.

    Splits firmware into MTU-sized chunks, sends them over BLE
    with retry logic, and finalises with a SHA-256 checksum and
    reset command.
    """

    def __init__(self, write_handler, mtu: int = 240):
        self._write = write_handler
        self.mtu = mtu
        self.max_retries = 3
        self.progress: OTAProgress | None = None
        self._cancel = False

    async def start_update(self, address: str, char_uuid: str, firmware_path: str | Path) -> dict:
        """Run the full OTA firmware update flow.

        Returns a summary dict with total_packets, sent, failed,
        sha256 and cancelled status.
        """
        self._cancel = False
        firmware = Path(firmware_path).read_bytes()
        total = (len(firmware) + self.mtu - 1) // self.mtu
        self.progress = OTAProgress(total)

        sha256 = hashlib.sha256(firmware).hexdigest()

        for seq in range(total):
            if self._cancel:
                break
            offset = seq * self.mtu
            chunk = firmware[offset : offset + self.mtu]
            ok = await self._send_packet(address, char_uuid, seq, chunk)
            if ok:
                self.progress.sent_packets += 1
            else:
                self.progress.failed_packets += 1

        # Completion packet with SHA-256 checksum
        await self._write(address, char_uuid, b"\xFF" + sha256.encode())
        # Reset command
        await self._write(address, char_uuid, b"\xFE")

        return {
            "total_packets": total,
            "sent": self.progress.sent_packets,
            "failed": self.progress.failed_packets,
            "sha256": sha256,
            "cancelled": self._cancel,
        }

    async def _send_packet(self, address: str, char_uuid: str, seq: int, chunk: bytes) -> bool:
        """Send a single packet with up to ``max_retries`` attempts."""
        header = seq.to_bytes(2, "big")
        packet = header + chunk
        for attempt in range(self.max_retries):
            try:
                await self._write(address, char_uuid, packet)
                await asyncio.sleep(0.02)
                return True
            except Exception as e:
                logger.warning(
                    "OTA packet %d retry %d/%d: %s",
                    seq,
                    attempt + 1,
                    self.max_retries,
                    e,
                )
                self.progress.retries += 1
                await asyncio.sleep(0.1)
        return False

    def cancel(self) -> None:
        """Abort an in-progress OTA update."""
        self._cancel = True

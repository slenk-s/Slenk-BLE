"""src/app_layer/connection_manager.py"""

from enum import Enum, auto
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConnectionState(Enum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    DISCONNECTING = auto()


class ConnectionManager:
    """连接状态机 + 重连策略。"""

    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._states: dict[str, ConnectionState] = {}
        self._retry_counts: dict[str, int] = {}

    def get_state(self, address: str) -> ConnectionState:
        return self._states.get(address, ConnectionState.DISCONNECTED)

    def set_state(self, address: str, state: ConnectionState) -> None:
        old = self.get_state(address)
        self._states[address] = state
        logger.info("连接状态变更 [%s]: %s -> %s", address, old.name, state.name)

    def should_retry(self, address: str) -> bool:
        return self._retry_counts.get(address, 0) < self.max_retries

    def record_retry(self, address: str) -> int:
        count = self._retry_counts.get(address, 0) + 1
        self._retry_counts[address] = count
        return count

    def reset_retries(self, address: str) -> None:
        self._retry_counts.pop(address, None)

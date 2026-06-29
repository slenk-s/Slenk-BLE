"""Tests for ConnectionManager — 连接状态机 + 重连策略。"""

import pytest
from src.app_layer.connection_manager import ConnectionState, ConnectionManager


class TestConnectionState:
    """ConnectionState 枚举值测试。"""

    def test_has_four_states(self) -> None:
        assert len(ConnectionState) == 4

    def test_disconnected_is_default(self) -> None:
        assert (
            ConnectionState.DISCONNECTED.value
            < ConnectionState.CONNECTING.value
        )

    def test_state_order(self) -> None:
        """验证枚举定义顺序：DISCONNECTED < CONNECTING < CONNECTED < DISCONNECTING"""
        values = [s.value for s in ConnectionState]
        assert values == sorted(values), "枚举值应保持定义顺序"


class TestConnectionManager:
    """ConnectionManager 核心功能测试。"""

    def test_default_state_is_disconnected(self) -> None:
        mgr = ConnectionManager()
        assert mgr.get_state("AA:BB:CC:DD:EE:FF") == ConnectionState.DISCONNECTED

    def test_set_and_get_state(self) -> None:
        mgr = ConnectionManager()
        addr = "11:22:33:44:55:66"
        mgr.set_state(addr, ConnectionState.CONNECTING)
        assert mgr.get_state(addr) == ConnectionState.CONNECTING

    def test_set_state_transitions(self) -> None:
        mgr = ConnectionManager()
        addr = "AA:BB:CC:DD:EE:FF"
        mgr.set_state(addr, ConnectionState.CONNECTING)
        mgr.set_state(addr, ConnectionState.CONNECTED)
        mgr.set_state(addr, ConnectionState.DISCONNECTING)
        mgr.set_state(addr, ConnectionState.DISCONNECTED)
        assert mgr.get_state(addr) == ConnectionState.DISCONNECTED

    def test_states_are_independent_per_address(self) -> None:
        mgr = ConnectionManager()
        mgr.set_state("addr1", ConnectionState.CONNECTED)
        mgr.set_state("addr2", ConnectionState.CONNECTING)
        assert mgr.get_state("addr1") == ConnectionState.CONNECTED
        assert mgr.get_state("addr2") == ConnectionState.CONNECTING

    def test_should_retry_when_under_limit(self) -> None:
        mgr = ConnectionManager(max_retries=3)
        assert mgr.should_retry("dev-1") is True

    def test_should_not_retry_when_at_limit(self) -> None:
        mgr = ConnectionManager(max_retries=2)
        mgr.record_retry("dev-1")
        mgr.record_retry("dev-1")
        assert mgr.should_retry("dev-1") is False

    def test_should_not_retry_when_over_limit(self) -> None:
        mgr = ConnectionManager(max_retries=1)
        mgr.record_retry("dev-1")
        assert mgr.should_retry("dev-1") is False

    def test_record_retry_returns_count(self) -> None:
        mgr = ConnectionManager()
        assert mgr.record_retry("dev-1") == 1
        assert mgr.record_retry("dev-1") == 2
        assert mgr.record_retry("dev-1") == 3

    def test_retry_counts_are_independent_per_address(self) -> None:
        mgr = ConnectionManager()
        mgr.record_retry("a")
        mgr.record_retry("a")
        mgr.record_retry("b")
        assert mgr.should_retry("a") is True  # count=2, max=3
        assert mgr.should_retry("b") is True  # count=1, max=3

    def test_reset_retries_clears_count(self) -> None:
        mgr = ConnectionManager(max_retries=1)
        mgr.record_retry("dev-1")
        assert mgr.should_retry("dev-1") is False
        mgr.reset_retries("dev-1")
        assert mgr.should_retry("dev-1") is True

    def test_reset_retries_unknown_address(self) -> None:
        mgr = ConnectionManager()
        mgr.reset_retries("nonexistent")
        assert mgr.should_retry("nonexistent") is True

    def test_default_max_retries(self) -> None:
        mgr = ConnectionManager()
        assert mgr.max_retries == 3

    def test_default_retry_delay(self) -> None:
        mgr = ConnectionManager()
        assert mgr.retry_delay == 2.0

    def test_custom_retry_params(self) -> None:
        mgr = ConnectionManager(max_retries=5, retry_delay=1.5)
        assert mgr.max_retries == 5
        assert mgr.retry_delay == 1.5

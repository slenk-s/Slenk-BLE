"""Tests for DataCache — 环形缓冲区。"""

from datetime import datetime

from src.app_layer.data_cache import DataCache, DataPoint


class TestDataPoint:
    """DataPoint 数据类基础测试。"""

    def test_create_with_minimal_args(self) -> None:
        now = datetime.now()
        dp = DataPoint(timestamp=now, address="AA:BB:CC:DD:EE:FF", raw_data=b"\x01\x02")
        assert dp.timestamp == now
        assert dp.address == "AA:BB:CC:DD:EE:FF"
        assert dp.raw_data == b"\x01\x02"
        assert dp.parsed is None

    def test_create_with_parsed(self) -> None:
        dp = DataPoint(
            timestamp=datetime.now(),
            address="11:22:33:44:55:66",
            raw_data=b"\x03",
            parsed={"temperature": 25.5, "humidity": 60},
        )
        assert dp.parsed == {"temperature": 25.5, "humidity": 60}

    def test_immutable_fields(self) -> None:
        now = datetime.now()
        dp = DataPoint(timestamp=now, address="A:B:C:D:E:F", raw_data=b"\x00")
        assert dp.address == "A:B:C:D:E:F"
        assert dp.raw_data == b"\x00"


class TestDataCache:
    """DataCache 核心功能测试。"""

    def test_default_max_size(self) -> None:
        cache = DataCache()
        assert cache.max_size == 10_000

    def test_custom_max_size(self) -> None:
        cache = DataCache(max_size=50)
        assert cache.max_size == 50

    def test_push_and_get_channel(self) -> None:
        cache = DataCache()
        cache.push("AA:BB:CC:DD:EE:FF", b"\x01", {"rssi": -70})
        cache.push("AA:BB:CC:DD:EE:FF", b"\x02")

        channel = cache.get_channel("AA:BB:CC:DD:EE:FF")
        assert len(channel) == 2
        assert channel[0].raw_data == b"\x01"
        assert channel[1].raw_data == b"\x02"

    def test_get_channel_returns_newest_first(self) -> None:
        """get_channel 返回最新的 limit 条数据。"""
        cache = DataCache()
        addr = "11:22:33:44:55:66"
        for i in range(10):
            cache.push(addr, bytes([i]))
        channel = cache.get_channel(addr, limit=3)
        assert len(channel) == 3
        assert channel[0].raw_data == bytes([7])
        assert channel[2].raw_data == bytes([9])

    def test_get_channel_unknown_address(self) -> None:
        cache = DataCache()
        assert cache.get_channel("nonexistent") == []

    def test_get_channel_respects_limit(self) -> None:
        cache = DataCache()
        addr = "AA:BB:CC:DD:EE:FF"
        for i in range(50):
            cache.push(addr, bytes([i]))
        assert len(cache.get_channel(addr, limit=10)) == 10

    def test_get_all_returns_sorted_by_timestamp_desc(self) -> None:
        cache = DataCache()
        cache.push("a", b"\x01")
        cache.push("b", b"\x02")
        cache.push("a", b"\x03")

        all_data = cache.get_all(limit=10)
        assert len(all_data) == 3
        # Should be sorted by timestamp descending
        for i in range(len(all_data) - 1):
            assert all_data[i].timestamp >= all_data[i + 1].timestamp

    def test_get_all_respects_limit(self) -> None:
        cache = DataCache()
        for i in range(5):
            cache.push(f"dev-{i}", bytes([i]))
        assert len(cache.get_all(limit=2)) == 2

    def test_get_all_empty_cache(self) -> None:
        cache = DataCache()
        assert cache.get_all() == []

    def test_ring_buffer_evicts_oldest(self) -> None:
        cache = DataCache(max_size=3)
        addr = "AA:BB:CC:DD:EE:FF"
        cache.push(addr, b"\x01")
        cache.push(addr, b"\x02")
        cache.push(addr, b"\x03")
        cache.push(addr, b"\x04")  # should evict \x01

        channel = cache.get_channel(addr)
        assert len(channel) == 3
        assert channel[0].raw_data == b"\x02"
        assert channel[1].raw_data == b"\x03"
        assert channel[2].raw_data == b"\x04"

    def test_ring_buffer_per_device_independence(self) -> None:
        cache = DataCache(max_size=2)
        cache.push("dev-a", b"\x01")
        cache.push("dev-a", b"\x02")
        cache.push("dev-a", b"\x03")  # evicts \x01

        cache.push("dev-b", b"\x41")

        assert len(cache.get_channel("dev-a")) == 2
        assert len(cache.get_channel("dev-b")) == 1

    def test_clear_specific_channel(self) -> None:
        cache = DataCache()
        cache.push("a", b"\x01")
        cache.push("b", b"\x02")
        cache.clear(address="a")

        assert cache.get_channel("a") == []
        assert len(cache.get_channel("b")) == 1

    def test_clear_all_channels(self) -> None:
        cache = DataCache()
        cache.push("a", b"\x01")
        cache.push("b", b"\x02")
        cache.push("c", b"\x03")
        cache.clear()

        assert cache.get_channel("a") == []
        assert cache.get_channel("b") == []
        assert cache.get_channel("c") == []

    def test_clear_unknown_channel(self) -> None:
        cache = DataCache()
        cache.clear(address="nonexistent")
        # Should not raise
        assert True

    def test_device_count(self) -> None:
        cache = DataCache()
        assert cache.device_count() == 0

        cache.push("a", b"\x01")
        assert cache.device_count() == 1

        cache.push("b", b"\x02")
        assert cache.device_count() == 2

    def test_device_count_after_clear_channel(self) -> None:
        cache = DataCache()
        cache.push("a", b"\x01")
        cache.push("b", b"\x02")
        cache.clear(address="a")
        assert cache.device_count() == 1

    def test_device_count_after_clear_all(self) -> None:
        cache = DataCache()
        cache.push("a", b"\x01")
        cache.push("b", b"\x02")
        cache.clear()
        assert cache.device_count() == 0

    def test_push_adds_timestamp_automatically(self) -> None:
        cache = DataCache()
        before = datetime.now()
        cache.push("addr", b"\x01")
        after = datetime.now()

        dp = cache.get_channel("addr")[0]
        assert before <= dp.timestamp <= after

    def test_push_stores_parsed_data(self) -> None:
        cache = DataCache()
        parsed = {"rssi": -80, "tx_power": 4}
        cache.push("addr", b"\x05", parsed=parsed)
        dp = cache.get_channel("addr")[0]
        assert dp.parsed == parsed

    def test_get_channel_default_limit(self) -> None:
        cache = DataCache()
        addr = "dev"
        for i in range(200):
            cache.push(addr, bytes([i]))
        # default limit is 100
        assert len(cache.get_channel(addr)) == 100

    def test_get_all_default_limit(self) -> None:
        cache = DataCache()
        for i in range(200):
            cache.push(f"dev-{i}", bytes([i]))
        # default limit is 100
        assert len(cache.get_all()) == 100
"""Tests for KeyValue store helper functions."""

import json
from unittest.mock import AsyncMock, Mock

import pytest
from kryten.kv_store import (
    get_kv_store,
    get_or_create_kv_store,
    kv_delete,
    kv_get,
    kv_get_all,
    kv_keys,
    kv_put,
)


@pytest.fixture
def mock_nats_client():
    """Create a mock NATS client with JetStream."""
    client = Mock()
    js = Mock()
    kv = AsyncMock()

    # Setup JetStream mock - jetstream() returns the js object directly
    client.jetstream = Mock(return_value=js)
    js.key_value = AsyncMock(return_value=kv)
    js.create_key_value = AsyncMock(return_value=kv)

    return client, js, kv


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    logger = Mock()
    logger.info = Mock()
    logger.debug = Mock()
    logger.error = Mock()
    return logger


class TestGetKVStore:
    """Test get_kv_store function."""

    async def test_get_existing_bucket(self, mock_nats_client, mock_logger):
        """Test getting an existing KV bucket."""
        client, js, kv = mock_nats_client

        result = await get_kv_store(client, "test_bucket", mock_logger)

        assert result == kv
        js.key_value.assert_called_once_with("test_bucket")
        mock_logger.debug.assert_called()

    async def test_create_new_bucket(self, mock_nats_client, mock_logger):
        """Test that get_kv_store raises when bucket doesn't exist."""
        client, js, kv = mock_nats_client

        # Make key_value raise exception to simulate bucket not existing
        js.key_value.side_effect = Exception("Bucket not found")

        with pytest.raises(Exception, match="Bucket not found"):
            await get_kv_store(client, "new_bucket", mock_logger)

        mock_logger.error.assert_called()


class TestGetOrCreateKVStore:
    """Test get_or_create_kv_store function."""

    async def test_get_existing_bucket(self, mock_nats_client, mock_logger):
        """Test getting an existing KV bucket."""
        client, js, kv = mock_nats_client

        result = await get_or_create_kv_store(client, "test_bucket", logger=mock_logger)

        assert result == kv
        js.key_value.assert_called_once_with("test_bucket")
        mock_logger.debug.assert_called()

    async def test_create_new_bucket(self, mock_nats_client, mock_logger):
        """Test creating a new KV bucket when it doesn't exist."""
        client, js, kv = mock_nats_client

        # Make key_value raise exception to simulate bucket not existing
        js.key_value.side_effect = Exception("Bucket not found")

        result = await get_or_create_kv_store(
            client, "new_bucket",
            description="Test bucket",
            logger=mock_logger
        )

        assert result == kv
        js.create_key_value.assert_called_once()
        mock_logger.info.assert_called()


class TestKVGet:
    """Test kv_get function."""

    async def test_get_existing_key(self, mock_logger):
        """Test getting an existing key."""
        kv = AsyncMock()
        entry = Mock()
        entry.value = b"test_value"
        kv.get.return_value = entry

        result = await kv_get(kv, "test_key", logger=mock_logger)

        assert result == b"test_value"
        kv.get.assert_called_once_with("test_key")

    async def test_get_nonexistent_key(self, mock_logger):
        """Test getting a key that doesn't exist."""
        kv = AsyncMock()
        kv.get.return_value = None

        result = await kv_get(kv, "missing_key", default="default", logger=mock_logger)

        assert result == "default"

    async def test_get_with_json_parsing(self, mock_logger):
        """Test getting a key with JSON parsing."""
        kv = AsyncMock()
        entry = Mock()
        entry.value = json.dumps({"key": "value"}).encode('utf-8')
        kv.get.return_value = entry

        result = await kv_get(kv, "json_key", parse_json=True, logger=mock_logger)

        assert result == {"key": "value"}

    async def test_get_invalid_json(self, mock_logger):
        """Test getting a key with invalid JSON."""
        kv = AsyncMock()
        entry = Mock()
        entry.value = b"not valid json"
        kv.get.return_value = entry

        result = await kv_get(kv, "bad_json", default={}, parse_json=True, logger=mock_logger)

        assert result == {}
        mock_logger.error.assert_called()

    async def test_get_error_handling(self, mock_logger):
        """Test error handling when get fails."""
        kv = AsyncMock()
        kv.get.side_effect = Exception("Connection error")

        result = await kv_get(kv, "test_key", default="fallback", logger=mock_logger)

        assert result == "fallback"
        mock_logger.error.assert_called()


class TestKVPut:
    """Test kv_put function."""

    async def test_put_bytes(self, mock_logger):
        """Test putting bytes value."""
        kv = AsyncMock()

        result = await kv_put(kv, "test_key", b"test_value", logger=mock_logger)

        assert result is True
        kv.put.assert_called_once_with("test_key", b"test_value")

    async def test_put_string(self, mock_logger):
        """Test putting string value."""
        kv = AsyncMock()

        result = await kv_put(kv, "test_key", "test_value", logger=mock_logger)

        assert result is True
        kv.put.assert_called_once_with("test_key", b"test_value")

    async def test_put_with_json(self, mock_logger):
        """Test putting value with JSON serialization."""
        kv = AsyncMock()

        data = {"key": "value", "number": 42}
        result = await kv_put(kv, "test_key", data, as_json=True, logger=mock_logger)

        assert result is True
        call_args = kv.put.call_args[0]
        assert call_args[0] == "test_key"
        assert json.loads(call_args[1].decode('utf-8')) == data

    async def test_put_error_handling(self, mock_logger):
        """Test error handling when put fails."""
        kv = AsyncMock()
        kv.put.side_effect = Exception("Write error")

        result = await kv_put(kv, "test_key", "value", logger=mock_logger)

        assert result is False
        mock_logger.error.assert_called()


class TestKVDelete:
    """Test kv_delete function."""

    async def test_delete_key(self, mock_logger):
        """Test deleting a key."""
        kv = AsyncMock()

        result = await kv_delete(kv, "test_key", logger=mock_logger)

        assert result is True
        kv.delete.assert_called_once_with("test_key")

    async def test_delete_error_handling(self, mock_logger):
        """Test error handling when delete fails."""
        kv = AsyncMock()
        kv.delete.side_effect = Exception("Delete error")

        result = await kv_delete(kv, "test_key", logger=mock_logger)

        assert result is False
        mock_logger.error.assert_called()


class TestKVKeys:
    """Test kv_keys function."""

    async def test_get_keys(self, mock_logger):
        """Test getting all keys."""
        kv = AsyncMock()
        kv.keys.return_value = ["key1", "key2", "key3"]

        result = await kv_keys(kv, logger=mock_logger)

        assert result == ["key1", "key2", "key3"]

    async def test_get_keys_empty(self, mock_logger):
        """Test getting keys when store is empty."""
        kv = AsyncMock()
        kv.keys.return_value = None

        result = await kv_keys(kv, logger=mock_logger)

        assert result == []

    async def test_get_keys_error(self, mock_logger):
        """Test error handling when getting keys fails."""
        kv = AsyncMock()
        kv.keys.side_effect = Exception("Error getting keys")

        result = await kv_keys(kv, logger=mock_logger)

        assert result == []
        mock_logger.error.assert_called()


class TestKVGetAll:
    """Test kv_get_all function."""

    async def test_get_all_keys(self, mock_logger):
        """Test getting all key-value pairs."""
        kv = AsyncMock()
        kv.keys.return_value = ["key1", "key2"]

        # Setup mock entries
        entry1 = Mock()
        entry1.value = b"value1"
        entry2 = Mock()
        entry2.value = b"value2"

        async def mock_get(key):
            if key == "key1":
                return entry1
            elif key == "key2":
                return entry2
            return None

        kv.get = mock_get

        result = await kv_get_all(kv, logger=mock_logger)

        assert result == {"key1": b"value1", "key2": b"value2"}

    async def test_get_all_with_json(self, mock_logger):
        """Test getting all key-value pairs with JSON parsing."""
        kv = AsyncMock()
        kv.keys.return_value = ["config", "data"]

        entry1 = Mock()
        entry1.value = json.dumps({"setting": "value"}).encode('utf-8')
        entry2 = Mock()
        entry2.value = json.dumps({"count": 42}).encode('utf-8')

        async def mock_get(key):
            if key == "config":
                return entry1
            elif key == "data":
                return entry2
            return None

        kv.get = mock_get

        result = await kv_get_all(kv, parse_json=True, logger=mock_logger)

        assert result == {
            "config": {"setting": "value"},
            "data": {"count": 42}
        }

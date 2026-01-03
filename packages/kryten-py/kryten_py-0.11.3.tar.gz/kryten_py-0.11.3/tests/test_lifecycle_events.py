"""Tests for lifecycle events module."""

import asyncio
import json
from unittest.mock import AsyncMock, Mock

import pytest
from kryten.lifecycle_events import LifecycleEventPublisher


@pytest.fixture
def mock_nats_client():
    """Create a mock NATS client."""
    client = AsyncMock()
    client.subscribe = AsyncMock()
    client.publish = AsyncMock()
    return client


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    return logger


@pytest.fixture
async def lifecycle_publisher(mock_nats_client, mock_logger):
    """Create a lifecycle event publisher with default settings."""
    publisher = LifecycleEventPublisher(
        service_name="test_service",
        nats_client=mock_nats_client,
        logger=mock_logger,
        version="1.0.0",
        enable_heartbeat=False,  # Disable for simpler testing
        enable_discovery=True,  # Discovery is enabled by default
    )
    yield publisher
    if publisher.is_running:
        await publisher.stop()


@pytest.fixture
async def lifecycle_publisher_minimal(mock_nats_client, mock_logger):
    """Create a lifecycle event publisher with heartbeat/discovery disabled."""
    publisher = LifecycleEventPublisher(
        service_name="test_service",
        nats_client=mock_nats_client,
        logger=mock_logger,
        version="1.0.0",
        enable_heartbeat=False,
        enable_discovery=False,
    )
    yield publisher
    if publisher.is_running:
        await publisher.stop()


class TestLifecycleEventPublisher:
    """Test lifecycle event publisher functionality."""

    async def test_initialization(self, lifecycle_publisher):
        """Test publisher initialization."""
        assert lifecycle_publisher._service_name == "test_service"
        assert lifecycle_publisher._version == "1.0.0"
        assert not lifecycle_publisher.is_running
        assert lifecycle_publisher._hostname is not None

    async def test_start(self, lifecycle_publisher, mock_nats_client):
        """Test starting the publisher with discovery enabled."""
        await lifecycle_publisher.start()

        assert lifecycle_publisher.is_running
        assert lifecycle_publisher._start_time is not None

        # Should subscribe to both restart notices and discovery polls
        assert mock_nats_client.subscribe.call_count == 2

        # Check first subscription (restart notices)
        calls = mock_nats_client.subscribe.call_args_list
        restart_call = calls[0]
        assert restart_call[0][0] == "kryten.lifecycle.group.restart"

        # Check second subscription (discovery polls)
        discovery_call = calls[1]
        assert discovery_call[0][0] == "kryten.service.discovery.poll"

    async def test_start_minimal(self, lifecycle_publisher_minimal, mock_nats_client):
        """Test starting publisher with discovery disabled."""
        await lifecycle_publisher_minimal.start()

        assert lifecycle_publisher_minimal.is_running
        # Only restart notices subscription
        mock_nats_client.subscribe.assert_called_once_with(
            "kryten.lifecycle.group.restart", cb=lifecycle_publisher_minimal._handle_restart_notice
        )

    async def test_start_already_running(self, lifecycle_publisher, mock_logger):
        """Test starting when already running."""
        await lifecycle_publisher.start()
        await lifecycle_publisher.start()  # Second start

        mock_logger.warning.assert_called_with("Lifecycle event publisher already running")

    async def test_stop(self, lifecycle_publisher):
        """Test stopping the publisher."""
        mock_sub = AsyncMock()
        mock_discovery_sub = AsyncMock()
        lifecycle_publisher._subscription = mock_sub
        lifecycle_publisher._discovery_subscription = mock_discovery_sub
        lifecycle_publisher._running = True

        await lifecycle_publisher.stop()

        assert not lifecycle_publisher.is_running
        assert lifecycle_publisher._subscription is None
        assert lifecycle_publisher._discovery_subscription is None
        mock_sub.unsubscribe.assert_called_once()
        mock_discovery_sub.unsubscribe.assert_called_once()

    async def test_publish_startup(self, lifecycle_publisher, mock_nats_client, mock_logger):
        """Test publishing startup event."""
        await lifecycle_publisher.start()
        await lifecycle_publisher.publish_startup(domain="cytu.be", channel="test")

        # Check publish was called
        assert mock_nats_client.publish.called
        call_args = mock_nats_client.publish.call_args
        subject = call_args[0][0]
        data = json.loads(call_args[0][1].decode("utf-8"))

        assert subject == "kryten.lifecycle.test_service.startup"
        assert data["service"] == "test_service"
        assert data["version"] == "1.0.0"
        assert data["domain"] == "cytu.be"
        assert data["channel"] == "test"
        assert "timestamp" in data
        assert "hostname" in data

    async def test_publish_shutdown(self, lifecycle_publisher, mock_nats_client):
        """Test publishing shutdown event."""
        await lifecycle_publisher.start()
        await lifecycle_publisher.publish_shutdown(reason="Test shutdown")

        call_args = mock_nats_client.publish.call_args
        subject = call_args[0][0]
        data = json.loads(call_args[0][1].decode("utf-8"))

        assert subject == "kryten.lifecycle.test_service.shutdown"
        assert data["reason"] == "Test shutdown"

    async def test_publish_connected(self, lifecycle_publisher, mock_nats_client):
        """Test publishing connected event."""
        await lifecycle_publisher.start()
        await lifecycle_publisher.publish_connected("NATS", servers=["nats://localhost:4222"])

        call_args = mock_nats_client.publish.call_args
        subject = call_args[0][0]
        data = json.loads(call_args[0][1].decode("utf-8"))

        assert subject == "kryten.lifecycle.test_service.connected"
        assert data["target"] == "NATS"
        assert data["servers"] == ["nats://localhost:4222"]

    async def test_publish_disconnected(self, lifecycle_publisher, mock_nats_client):
        """Test publishing disconnected event."""
        await lifecycle_publisher.start()
        await lifecycle_publisher.publish_disconnected("CyTube", reason="Connection lost")

        call_args = mock_nats_client.publish.call_args
        subject = call_args[0][0]
        data = json.loads(call_args[0][1].decode("utf-8"))

        assert subject == "kryten.lifecycle.test_service.disconnected"
        assert data["target"] == "CyTube"
        assert data["reason"] == "Connection lost"

    async def test_publish_group_restart(self, lifecycle_publisher, mock_nats_client):
        """Test publishing groupwide restart notice."""
        await lifecycle_publisher.start()
        await lifecycle_publisher.publish_group_restart(
            reason="Config update", delay_seconds=10, initiator="admin"
        )

        call_args = mock_nats_client.publish.call_args
        subject = call_args[0][0]
        data = json.loads(call_args[0][1].decode("utf-8"))

        assert subject == "kryten.lifecycle.group.restart"
        assert data["reason"] == "Config update"
        assert data["delay_seconds"] == 10
        assert data["initiator"] == "admin"

    async def test_restart_callback(self, lifecycle_publisher):
        """Test restart notice callback."""
        callback_called = False
        callback_data = None

        async def restart_callback(data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = data

        lifecycle_publisher.on_restart_notice(restart_callback)
        await lifecycle_publisher.start()

        # Simulate restart notice
        msg = Mock()
        msg.data = json.dumps(
            {"initiator": "test", "reason": "Test restart", "delay_seconds": 5}
        ).encode("utf-8")

        await lifecycle_publisher._handle_restart_notice(msg)

        assert callback_called
        assert callback_data is not None
        assert callback_data["reason"] == "Test restart"

    async def test_handle_invalid_restart_notice(self, lifecycle_publisher, mock_logger):
        """Test handling invalid restart notice JSON."""
        await lifecycle_publisher.start()

        msg = Mock()
        msg.data = b"invalid json"

        await lifecycle_publisher._handle_restart_notice(msg)

        # Should log error but not crash
        assert mock_logger.error.called

    async def test_uptime_calculation(self, lifecycle_publisher, mock_nats_client):
        """Test that uptime is calculated correctly."""
        await lifecycle_publisher.start()

        # Wait a bit
        await asyncio.sleep(0.1)

        await lifecycle_publisher.publish_shutdown()

        call_args = mock_nats_client.publish.call_args
        data = json.loads(call_args[0][1].decode("utf-8"))

        assert data["uptime_seconds"] is not None
        assert data["uptime_seconds"] >= 0.1

    async def test_publish_heartbeat(self, lifecycle_publisher, mock_nats_client):
        """Test publishing heartbeat event."""
        await lifecycle_publisher.start()
        await lifecycle_publisher.publish_heartbeat()

        # Find heartbeat call
        for call in mock_nats_client.publish.call_args_list:
            subject = call[0][0]
            if "heartbeat" in subject:
                data = json.loads(call[0][1].decode("utf-8"))
                assert subject == "kryten.lifecycle.test_service.heartbeat"
                assert data["service"] == "test_service"
                assert data["version"] == "1.0.0"
                assert "uptime_seconds" in data
                return
        pytest.fail("Heartbeat not published")

    async def test_handle_discovery_poll(self, lifecycle_publisher, mock_nats_client):
        """Test that discovery poll triggers startup re-announcement."""
        await lifecycle_publisher.start()
        mock_nats_client.publish.reset_mock()

        # Simulate discovery poll
        msg = Mock()
        msg.data = b"{}"

        await lifecycle_publisher._handle_discovery_poll(msg)

        # Should publish startup event
        assert mock_nats_client.publish.called
        call_args = mock_nats_client.publish.call_args
        subject = call_args[0][0]
        assert subject == "kryten.lifecycle.test_service.startup"


class TestHeartbeat:
    """Tests for automatic heartbeat functionality."""

    @pytest.fixture
    async def heartbeat_publisher(self, mock_nats_client, mock_logger):
        """Create publisher with heartbeat enabled."""
        publisher = LifecycleEventPublisher(
            service_name="heartbeat_test",
            nats_client=mock_nats_client,
            logger=mock_logger,
            version="1.0.0",
            heartbeat_interval=1,  # Use integer for interval
            enable_heartbeat=True,
            enable_discovery=False,
        )
        yield publisher
        if publisher.is_running:
            await publisher.stop()

    async def test_heartbeat_loop_publishes(self, heartbeat_publisher, mock_nats_client):
        """Test that heartbeat loop publishes periodic heartbeats."""
        await heartbeat_publisher.start()

        # Wait for a couple heartbeats
        await asyncio.sleep(0.25)

        await heartbeat_publisher.stop()

        # Should have published at least one heartbeat
        heartbeat_calls = [
            call for call in mock_nats_client.publish.call_args_list if "heartbeat" in call[0][0]
        ]
        assert len(heartbeat_calls) >= 1

    async def test_heartbeat_task_created(self, heartbeat_publisher):
        """Test that heartbeat task is created on start."""
        await heartbeat_publisher.start()

        assert heartbeat_publisher._heartbeat_task is not None
        assert not heartbeat_publisher._heartbeat_task.done()

        await heartbeat_publisher.stop()

        assert heartbeat_publisher._heartbeat_task is None

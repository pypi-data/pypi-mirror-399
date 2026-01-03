"""Tests for MockKrytenClient."""

import pytest
from kryten.mock import MockKrytenClient


@pytest.fixture
def mock_config():
    """Test configuration."""
    return {
        "nats": {"servers": ["nats://localhost:4222"]},
        "channels": [{"domain": "cytu.be", "channel": "test"}],
    }


@pytest.mark.asyncio
async def test_mock_client_connect(mock_config):
    """Test mock client connection."""
    client = MockKrytenClient(mock_config)

    assert not client.is_connected

    await client.connect()

    assert client.is_connected


@pytest.mark.asyncio
async def test_mock_client_context_manager(mock_config):
    """Test mock client as context manager."""
    client = MockKrytenClient(mock_config)

    assert not client.is_connected

    async with client:
        assert client.is_connected

    assert not client.is_connected


@pytest.mark.asyncio
async def test_mock_client_send_chat(mock_config):
    """Test recording chat commands."""
    client = MockKrytenClient(mock_config)

    async with client:
        correlation_id = await client.send_chat("test", "Hello world!")

        assert correlation_id
        commands = client.get_published_commands()
        assert len(commands) == 1

        cmd = commands[0]
        assert cmd["action"] == "chat"
        assert cmd["data"]["message"] == "Hello world!"
        assert cmd["channel"] == "test"
        assert cmd["correlation_id"] == correlation_id


@pytest.mark.asyncio
async def test_mock_client_multiple_commands(mock_config):
    """Test recording multiple commands."""
    client = MockKrytenClient(mock_config)

    async with client:
        await client.send_chat("test", "Message 1")
        await client.send_chat("test", "Message 2")
        await client.add_media("test", "yt", "abc123")

        commands = client.get_published_commands()
        assert len(commands) == 3
        assert commands[0]["action"] == "chat"
        assert commands[1]["action"] == "chat"
        assert commands[2]["action"] == "queue"


@pytest.mark.asyncio
async def test_mock_client_clear_commands(mock_config):
    """Test clearing recorded commands."""
    client = MockKrytenClient(mock_config)

    async with client:
        await client.send_chat("test", "Test")
        assert len(client.get_published_commands()) == 1

        client.clear_published_commands()
        assert len(client.get_published_commands()) == 0


@pytest.mark.asyncio
async def test_mock_client_event_handler(mock_config):
    """Test event handler registration and simulation."""
    client = MockKrytenClient(mock_config)
    received_events = []

    @client.on("chatmsg")
    async def handle_chat(event):
        received_events.append(event)

    async with client:
        await client.simulate_event(
            "chatmsg",
            {"username": "alice", "message": "Hello!"},
        )

        # Give handler time to execute
        import asyncio

        await asyncio.sleep(0.1)

        assert len(received_events) == 1
        # Event is now converted to ChatMessageEvent
        event = received_events[0]
        assert event.username == "alice"
        assert event.message == "Hello!"


@pytest.mark.asyncio
async def test_mock_client_health(mock_config):
    """Test health status."""
    client = MockKrytenClient(mock_config)

    health = client.health()
    assert not health.connected
    assert health.commands_sent == 0

    async with client:
        health = client.health()
        assert health.connected

        await client.send_chat("test", "Test")

        health = client.health()
        assert health.commands_sent == 1

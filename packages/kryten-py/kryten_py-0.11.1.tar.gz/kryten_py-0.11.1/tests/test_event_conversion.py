"""Tests for event conversion from RawEvent to typed events."""


import pytest
from kryten import MockKrytenClient
from kryten.models import (
    ChangeMediaEvent,
    ChatMessageEvent,
    PlaylistUpdateEvent,
    RawEvent,
    UserJoinEvent,
    UserLeaveEvent,
)


@pytest.fixture
def mock_config():
    """Test configuration."""
    return {
        "nats": {"servers": ["nats://localhost:4222"]},
        "channels": [{"domain": "test", "channel": "test"}],
    }


@pytest.mark.asyncio
async def test_chatmsg_conversion_nested_user(mock_config):
    """Test chatmsg event with nested user structure."""
    client = MockKrytenClient(mock_config)
    received_events = []

    @client.on("chatmsg")
    async def handler(event):
        received_events.append(event)

    async with client:
        await client.simulate_event(
            "chatmsg",
            {
                "user": {"name": "alice", "rank": 2},
                "msg": "Hello!",
                "time": 1234567890000,
            },
        )

        import asyncio

        await asyncio.sleep(0.1)

        assert len(received_events) == 1
        event = received_events[0]
        assert isinstance(event, ChatMessageEvent)
        assert event.username == "alice"
        assert event.message == "Hello!"
        assert event.rank == 2


@pytest.mark.asyncio
async def test_chatmsg_conversion_flat_structure(mock_config):
    """Test chatmsg event with flat structure."""
    client = MockKrytenClient(mock_config)
    received_events = []

    @client.on("chatmsg")
    async def handler(event):
        received_events.append(event)

    async with client:
        await client.simulate_event(
            "chatmsg",
            {"username": "bob", "message": "Hi there!", "rank": 1, "time": 1234567890000},
        )

        import asyncio

        await asyncio.sleep(0.1)

        assert len(received_events) == 1
        event = received_events[0]
        assert isinstance(event, ChatMessageEvent)
        assert event.username == "bob"
        assert event.message == "Hi there!"
        assert event.rank == 1


@pytest.mark.asyncio
async def test_pm_conversion(mock_config):
    """Test PM event conversion."""
    client = MockKrytenClient(mock_config)
    received_events = []

    @client.on("pm")
    async def handler(event):
        received_events.append(event)

    async with client:
        await client.simulate_event(
            "pm",
            {"username": "charlie", "msg": "Secret!", "rank": 3, "time": 1234567890000},
        )

        import asyncio

        await asyncio.sleep(0.1)

        assert len(received_events) == 1
        event = received_events[0]
        assert isinstance(event, ChatMessageEvent)
        assert event.username == "charlie"
        assert event.message == "Secret!"
        assert event.rank == 3


@pytest.mark.asyncio
async def test_adduser_conversion(mock_config):
    """Test user join event conversion."""
    client = MockKrytenClient(mock_config)
    received_events = []

    @client.on("adduser")
    async def handler(event):
        received_events.append(event)

    async with client:
        await client.simulate_event(
            "addUser",
            {"name": "david", "rank": 1, "time": 1234567890000},
        )

        import asyncio

        await asyncio.sleep(0.1)

        assert len(received_events) == 1
        event = received_events[0]
        assert isinstance(event, UserJoinEvent)
        assert event.username == "david"
        assert event.rank == 1


@pytest.mark.asyncio
async def test_userleave_conversion(mock_config):
    """Test user leave event conversion."""
    client = MockKrytenClient(mock_config)
    received_events = []

    @client.on("userleave")
    async def handler(event):
        received_events.append(event)

    async with client:
        await client.simulate_event(
            "userLeave",
            {"name": "eve", "time": 1234567890000},
        )

        import asyncio

        await asyncio.sleep(0.1)

        assert len(received_events) == 1
        event = received_events[0]
        assert isinstance(event, UserLeaveEvent)
        assert event.username == "eve"


@pytest.mark.asyncio
async def test_changemedia_conversion(mock_config):
    """Test media change event conversion."""
    client = MockKrytenClient(mock_config)
    received_events = []

    @client.on("changemedia")
    async def handler(event):
        received_events.append(event)

    async with client:
        await client.simulate_event(
            "changeMedia",
            {
                "type": "yt",
                "id": "dQw4w9WgXcQ",
                "title": "Test Video",
                "seconds": 212,
                "uid": 42,
                "time": 1234567890000,
            },
        )

        import asyncio

        await asyncio.sleep(0.1)

        assert len(received_events) == 1
        event = received_events[0]
        assert isinstance(event, ChangeMediaEvent)
        assert event.media_type == "yt"
        assert event.media_id == "dQw4w9WgXcQ"
        assert event.title == "Test Video"
        assert event.duration == 212
        assert event.uid == 42


@pytest.mark.asyncio
async def test_playlist_conversion(mock_config):
    """Test playlist update event conversion."""
    client = MockKrytenClient(mock_config)
    received_events = []

    @client.on("playlist")
    async def handler(event):
        received_events.append(event)

    async with client:
        await client.simulate_event(
            "playlist",
            {"action": "add", "uid": 123, "time": 1234567890000},
        )

        import asyncio

        await asyncio.sleep(0.1)

        assert len(received_events) == 1
        event = received_events[0]
        assert isinstance(event, PlaylistUpdateEvent)
        assert event.action == "add"
        assert event.uid == 123


@pytest.mark.asyncio
async def test_unknown_event_returns_raw(mock_config):
    """Test that unknown event types return RawEvent."""
    client = MockKrytenClient(mock_config)
    received_events = []

    @client.on("unknownevent")
    async def handler(event):
        received_events.append(event)

    async with client:
        await client.simulate_event(
            "unknownEvent",
            {"some": "data"},
        )

        import asyncio

        await asyncio.sleep(0.1)

        assert len(received_events) == 1
        event = received_events[0]
        assert isinstance(event, RawEvent)
        assert event.event_name == "unknownEvent"
        assert event.payload == {"some": "data"}

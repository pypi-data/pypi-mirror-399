"""Tests for event models."""

from datetime import datetime, timezone

import pytest
from kryten.models import (
    ChangeMediaEvent,
    ChatMessageEvent,
    PlaylistUpdateEvent,
    RawEvent,
    UserJoinEvent,
    UserLeaveEvent,
)


def test_raw_event_creation():
    """Test creating a RawEvent."""
    event = RawEvent(
        event_name="chatMsg",
        payload={"user": "alice", "msg": "hello"},
        channel="lounge",
        domain="cytu.be",
    )

    assert event.event_name == "chatMsg"
    assert event.payload == {"user": "alice", "msg": "hello"}
    assert event.channel == "lounge"
    assert event.domain == "cytu.be"
    assert event.correlation_id  # Should be generated
    assert event.timestamp  # Should be generated


def test_raw_event_immutable():
    """Test that RawEvent is immutable."""
    event = RawEvent(
        event_name="chatMsg",
        payload={},
        channel="lounge",
        domain="cytu.be",
    )

    with pytest.raises(Exception):  # noqa: B017
        event.event_name = "different"  # type: ignore


def test_raw_event_to_bytes():
    """Test serializing RawEvent to bytes."""
    event = RawEvent(
        event_name="chatMsg",
        payload={"user": "alice"},
        channel="lounge",
        domain="cytu.be",
    )

    data = event.to_bytes()
    assert isinstance(data, bytes)
    assert b"chatMsg" in data
    assert b"alice" in data


def test_chat_message_event():
    """Test ChatMessageEvent model."""
    event = ChatMessageEvent(
        username="alice",
        message="Hello world!",
        timestamp=datetime.now(timezone.utc),
        rank=1,
        channel="lounge",
        domain="cytu.be",
        correlation_id="test-123",
    )

    assert event.username == "alice"
    assert event.message == "Hello world!"
    assert event.rank == 1

    with pytest.raises(ValueError):
        ChatMessageEvent(
            username="user",
            message="msg",
            timestamp=datetime.now(),
            rank=0,
            channel="ch",
            domain="dom",
            # Missing correlation_id
        )  # type: ignore[call-arg]


def test_user_join_event():
    """Test UserJoinEvent model."""
    event = UserJoinEvent(
        username="bob",
        rank=2,
        timestamp=datetime.now(timezone.utc),
        channel="lounge",
        domain="cytu.be",
        correlation_id="test-456",
    )

    assert event.username == "bob"
    assert event.rank == 2


def test_user_leave_event():
    """Test UserLeaveEvent model."""
    event = UserLeaveEvent(
        username="charlie",
        timestamp=datetime.now(timezone.utc),
        channel="lounge",
        domain="cytu.be",
        correlation_id="test-789",
    )

    assert event.username == "charlie"


def test_change_media_event():
    """Test ChangeMediaEvent model."""
    event = ChangeMediaEvent(
        media_type="yt",
        media_id="dQw4w9WgXcQ",
        title="Test Video",
        duration=212,
        uid=42,
        timestamp=datetime.now(timezone.utc),
        channel="lounge",
        domain="cytu.be",
        correlation_id="test-abc",
    )

    assert event.media_type == "yt"
    assert event.media_id == "dQw4w9WgXcQ"
    assert event.title == "Test Video"
    assert event.duration == 212
    assert event.uid == 42


def test_playlist_update_event():
    """Test PlaylistUpdateEvent model."""
    event = PlaylistUpdateEvent(
        action="add",
        uid=123,
        timestamp=datetime.now(timezone.utc),
        channel="lounge",
        domain="cytu.be",
        correlation_id="test-def",
    )

    assert event.action == "add"
    assert event.uid == 123


def test_playlist_update_event_without_uid():
    """Test PlaylistUpdateEvent with no uid (e.g., clear action)."""
    event = PlaylistUpdateEvent(
        action="clear",
        uid=None,
        timestamp=datetime.now(timezone.utc),
        channel="lounge",
        domain="cytu.be",
        correlation_id="test-ghi",
    )

    assert event.action == "clear"
    assert event.uid is None

"""Tests for subject builder."""

import pytest
from kryten.models import RawEvent
from kryten.subject_builder import (
    build_command_subject,
    build_event_subject,
    build_subject,
    parse_subject,
    sanitize_token,
)


def test_sanitize_token_basic():
    """Test basic token sanitization."""
    assert sanitize_token("MyChannel") == "mychannel"
    assert sanitize_token("Test Channel") == "test-channel"
    assert sanitize_token("Test_Channel") == "test_channel"


def test_sanitize_token_special_chars():
    """Test sanitizing special characters."""
    assert sanitize_token("Channel!@#") == "channel"
    assert sanitize_token("Test*Channel") == "testchannel"
    assert sanitize_token("Test>Channel") == "testchannel"


def test_sanitize_token_unicode():
    """Test Unicode characters are preserved."""
    assert sanitize_token("café") == "café"


def test_sanitize_token_empty():
    """Test empty string handling."""
    assert sanitize_token("") == ""


def test_build_subject_basic():
    """Test building basic subject."""
    subject = build_subject("cytu.be", "lounge", "chatMsg")
    assert subject == "kryten.events.cytube.lounge.chatmsg"


def test_build_subject_normalizes_case():
    """Test that subject components are normalized."""
    subject = build_subject("CYTU.BE", "LOUNGE", "ChatMsg")
    assert subject == "kryten.events.cytube.lounge.chatmsg"


def test_build_subject_sanitizes_channel():
    """Test that channel name is sanitized."""
    subject = build_subject("cytu.be", "Test Channel", "chatMsg")
    assert subject == "kryten.events.cytube.test-channel.chatmsg"


def test_build_subject_empty_component():
    """Test that empty components raise ValueError."""
    # Note: With the new format, domain is ignored (always "cytube")
    # but we still validate channel and event
    with pytest.raises(ValueError, match="Channel cannot be empty"):
        build_subject("cytu.be", "", "chatMsg")

    with pytest.raises(ValueError, match="Event name cannot be empty"):
        build_subject("cytu.be", "lounge", "")


def test_build_event_subject():
    """Test building subject from RawEvent."""
    event = RawEvent(
        event_name="chatMsg",
        payload={},
        channel="lounge",
        domain="cytu.be",
    )

    subject = build_event_subject(event)
    assert subject == "kryten.events.cytube.lounge.chatmsg"


def test_build_command_subject():
    """Test building command subject."""
    # New signature: build_command_subject(service, domain="", channel="", action="")
    # We pass "robot" as service
    subject = build_command_subject("robot")
    assert subject == "kryten.robot.command"


def test_build_command_subject_sanitizes():
    """Test command subject sanitization."""
    subject = build_command_subject("My Service")
    assert subject == "kryten.my-service.command"


def test_parse_subject_basic():
    """Test parsing basic subject."""
    components = parse_subject("kryten.events.cytube.lounge.chatMsg")

    assert components["prefix"] == "kryten.events"
    assert components["channel"] == "lounge"
    assert components["event_name"] == "chatMsg"


def test_parse_subject_with_hyphens():
    """Test parsing subject with hyphenated channel name."""
    components = parse_subject("kryten.events.cytube.test-channel.chatMsg")

    assert components["channel"] == "test-channel"
    assert components["event_name"] == "chatMsg"


def test_parse_subject_invalid_prefix():
    """Test parsing subject with wrong prefix."""
    with pytest.raises(ValueError, match="Invalid subject prefix"):
        parse_subject("wrong.prefix.cytube.lounge.chatMsg")


def test_parse_subject_too_short():
    """Test parsing subject with too few components."""
    with pytest.raises(ValueError, match="Invalid subject"):
        parse_subject("kryten.events.cytube")


def test_parse_subject_empty():
    """Test parsing empty subject."""
    with pytest.raises(ValueError, match="Subject cannot be empty"):
        parse_subject("")

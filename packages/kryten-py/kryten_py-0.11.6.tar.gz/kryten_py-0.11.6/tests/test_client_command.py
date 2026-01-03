import json
from unittest.mock import AsyncMock

import pytest
from kryten.client import KrytenClient, build_command_subject


@pytest.mark.asyncio
async def test_send_command():
    # Setup
    config = {
        "nats": {"servers": ["nats://localhost:4222"]},
        "channels": [{"domain": "test.com", "channel": "test"}],
        "service": {"name": "test-service"},
    }

    client = KrytenClient(config)
    client._connected = True
    # Mock private __nats member
    client._nats = AsyncMock()

    # Test data
    service = "robot"
    cmd_type = "test_cmd"
    body = "test body"

    # Execute
    await client.send_command(service, cmd_type, body)

    # Verify
    expected_subject = build_command_subject(service)
    client._nats.publish.assert_called_once()

    call_args = client._nats.publish.call_args
    assert call_args[0][0] == expected_subject

    payload = json.loads(call_args[0][1].decode("utf-8"))
    assert payload["command"] == cmd_type  # Changed from "type"
    assert payload["args"] == {"value": body}  # Changed from "body"
    assert payload["meta"]["source"] == "test-service"
    assert payload["meta"]["domain"] == "test.com"  # Default from config
    assert payload["meta"]["channel"] == "lounge"  # Default


@pytest.mark.asyncio
async def test_send_command_custom_channel():
    # Setup
    config = {
        "nats": {"servers": ["nats://localhost:4222"]},
        "channels": [{"domain": "test.com", "channel": "test"}],
    }

    client = KrytenClient(config)
    client._connected = True
    # Mock private __nats member
    client._nats = AsyncMock()

    # Execute
    await client.send_command("llm", "query", "hello", domain="custom.com", channel="mychan")

    # Verify
    call_args = client._nats.publish.call_args
    payload = json.loads(call_args[0][1].decode("utf-8"))
    assert payload["meta"]["domain"] == "custom.com"
    assert payload["meta"]["channel"] == "mychan"
    assert payload["meta"]["source"] == "kryten-client"  # Default when no service config

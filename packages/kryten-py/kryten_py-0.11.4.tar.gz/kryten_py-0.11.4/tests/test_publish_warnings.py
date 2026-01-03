from unittest.mock import AsyncMock, MagicMock

import pytest
from kryten.client import KrytenClient


@pytest.mark.asyncio
async def test_publish_warning():
    # Setup
    config = {
        "nats": {"servers": ["nats://localhost:4222"]},
        "channels": [{"domain": "test.com", "channel": "test"}],
        "service": {"name": "test-service"},
    }

    logger = MagicMock()
    client = KrytenClient(config, logger=logger)
    client._connected = True
    client._nats = AsyncMock()  # Access private member

    # Test 1: Publish to command subject (should warn)
    await client.publish("kryten.command.robot", b"{}")
    logger.warning.assert_called_with(
        "Use 'send_command()' instead of 'publish()' for sending commands: kryten.command.robot"
    )

    # Test 2: Publish to own event subject (should NOT warn)
    logger.reset_mock()
    await client.publish("kryten.events.test-service.something", b"{}")
    logger.warning.assert_not_called()

    # Test 3: Publish to foreign event subject (should warn)
    logger.reset_mock()
    await client.publish("kryten.events.other-service.something", b"{}")
    logger.warning.assert_called_with(
        "Publishing event to foreign service subject: kryten.events.other-service.something. Expected prefix: kryten.events.test-service."
    )

    # Test 4: Publish to legacy cytube event (should warn about deprecation)
    logger.reset_mock()
    await client.publish("kryten.events.cytube.lounge.chatMsg", b"{}")
    logger.warning.assert_called_with(
        "Publishing to legacy 'kryten.events.cytube.*' subject: kryten.events.cytube.lounge.chatMsg. This format is deprecated."
    )

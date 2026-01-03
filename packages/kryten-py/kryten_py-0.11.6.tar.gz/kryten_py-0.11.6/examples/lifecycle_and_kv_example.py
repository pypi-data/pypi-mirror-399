"""Example: Using Lifecycle Events and KV Store

This example demonstrates how to use the new lifecycle event publishing
and KeyValue store helper functions in kryten-py v0.3.0.
"""

import asyncio
import logging

from kryten import (
    KrytenClient,
    LifecycleEventPublisher,
)


async def main():
    """Example usage of lifecycle events and KV store."""

    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger("example")

    # Configuration
    config = {
        "nats": {"servers": ["nats://localhost:4222"]},
        "channels": [{"domain": "cytu.be", "channel": "lounge"}],
    }

    async with KrytenClient(config, logger=logger) as client:
        # Get NATS client for lifecycle and KV store
        nats_client = client._nats

        # ===== Lifecycle Events =====

        # Initialize lifecycle event publisher
        lifecycle = LifecycleEventPublisher(
            service_name="example_bot", nats_client=nats_client, logger=logger, version="1.0.0"  # type: ignore[arg-type]
        )
        await lifecycle.start()

        # Register restart handler
        async def handle_restart(data):
            """Handle groupwide restart notice."""
            reason = data.get("reason", "Unknown")
            delay = data.get("delay_seconds", 5)
            logger.warning(f"Restart requested: {reason}, shutting down in {delay}s")
            await asyncio.sleep(delay)
            # Trigger shutdown
            await client.stop()

        lifecycle.on_restart_notice(handle_restart)

        # Publish startup event
        await lifecycle.publish_connected("NATS")
        await lifecycle.publish_startup(config_version="1.0", features=["chat", "moderation"])

        # ===== KeyValue Store =====

        # Store configuration
        await client.kv_put(
            "example_bot_state",
            "config",
            {"enabled": True, "max_messages": 100, "timeout": 30},
            as_json=True,
        )

        # Store simple values
        await client.kv_put("example_bot_state", "last_user", "Alice")
        await client.kv_put("example_bot_state", "message_count", "42")

        # Retrieve values
        config_data = await client.kv_get("example_bot_state", "config", parse_json=True)
        logger.info(f"Loaded config: {config_data}")

        last_user = await client.kv_get("example_bot_state", "last_user")
        if last_user:
            logger.info(f"Last user: {last_user.decode('utf-8')}")

        # Get with default
        unknown = await client.kv_get("example_bot_state", "unknown_key", default="default_value")
        logger.info(f"Unknown key returned: {unknown}")

        # ===== Event Handlers =====

        @client.on("chatmsg")
        async def handle_chat(event):
            """Handle chat messages."""
            logger.info(f"{event.username}: {event.message}")

            # Update KV store with last message info
            await client.kv_put("example_bot_state", "last_user", event.username)

            # Simple echo command
            if event.message.startswith("!echo "):
                text = event.message[6:]
                await client.send_chat(event.channel, f"Echo: {text}")

        @client.on("usercount")
        async def handle_usercount(event):
            """Track user count in KV store."""
            count = event.payload.get("count", 0)
            await client.kv_put("example_bot_state", "current_users", str(count))
            logger.info(f"User count: {count}")

        # ===== Run Bot =====

        logger.info("Bot is ready! Press Ctrl+C to stop.")

        try:
            await client.run()
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        finally:
            # Publish shutdown events
            await lifecycle.publish_disconnected("CyTube", reason="User shutdown")
            await lifecycle.publish_shutdown(reason="User requested shutdown")
            await lifecycle.stop()
            logger.info("Cleanup complete")


if __name__ == "__main__":
    asyncio.run(main())

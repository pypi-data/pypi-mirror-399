"""Simple echo bot example."""

import asyncio
import logging

from kryten import ChatMessageEvent, KrytenClient


async def main():
    """Simple echo bot that repeats user messages."""

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Configuration
    config = {
        "nats": {
            "servers": ["nats://localhost:4222"],
            # Uncomment for authentication:
            # "user": "kryten",
            # "password": "secret"
        },
        "channels": [{"domain": "cytu.be", "channel": "lounge"}],
    }

    # Create and run bot
    async with KrytenClient(config) as client:

        @client.on("chatmsg")
        async def on_chat(event: ChatMessageEvent):
            """Echo user messages."""
            # Don't echo ourselves
            if event.username != "EchoBot":
                await client.send_chat(event.channel, f"{event.username} said: {event.message}")

        print("Echo bot started! Press Ctrl+C to stop.")
        await client.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")

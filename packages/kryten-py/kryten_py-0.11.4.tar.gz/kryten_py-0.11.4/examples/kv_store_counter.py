"""Example: Simple Message Counter Using KV Store

This example demonstrates how to use NATS JetStream KeyValue store
to persist data across bot restarts. It counts messages per user.
"""

import asyncio
import logging

from kryten import (
    ChatMessageEvent,
    KrytenClient,
)


async def main():
    """Count messages per user using persistent KV store."""

    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger("counter_bot")

    # Configuration
    config = {
        "nats": {"servers": ["nats://localhost:4222"]},
        "channels": [{"domain": "cytu.be", "channel": "lounge"}],
    }

    async with KrytenClient(config, logger=logger) as client:
        # Load existing counts on startup
        counts = await client.kv_get_all("message_counts", parse_json=True)
        logger.info(f"Loaded {len(counts)} user message counts from KV store")

        @client.on("chatmsg")
        async def handle_chat(event: ChatMessageEvent):
            """Count messages per user."""
            username = event.username

            # Get current count for this user
            current_count = await client.kv_get(
                "message_counts", f"user:{username}", default=0, parse_json=True
            )

            # Increment count
            new_count = current_count + 1

            # Save back to KV store
            await client.kv_put("message_counts", f"user:{username}", new_count, as_json=True)

            logger.info(f"{username} has sent {new_count} messages")

            # Respond to !stats command
            if event.message == "!stats":
                await client.send_chat(
                    event.channel,
                    f"{username}: You've sent {new_count} messages!",
                    domain=event.domain,
                )

            # Respond to !leaderboard command
            elif event.message == "!leaderboard":
                all_counts = await client.kv_get_all("message_counts", parse_json=True)

                # Sort by count descending
                sorted_users = sorted(
                    all_counts.items(),
                    key=lambda x: x[1] if isinstance(x[1], int) else 0,
                    reverse=True,
                )[:5]

                if sorted_users:
                    leaderboard = "Top 5 chatters: " + ", ".join(
                        f"{user.replace('user:', '')}: {count}" for user, count in sorted_users
                    )
                else:
                    leaderboard = "No messages counted yet!"

                await client.send_chat(event.channel, leaderboard, domain=event.domain)

        logger.info("Counter bot started. Commands: !stats, !leaderboard")
        logger.info("Press Ctrl+C to stop")

        # Run the bot
        try:
            await client.run()
        except KeyboardInterrupt:
            logger.info("Shutting down...")


if __name__ == "__main__":
    asyncio.run(main())

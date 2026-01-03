#!/usr/bin/env python3
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from kryten import KrytenClient  # noqa: E402


async def main():
    config = {
        "nats": {"servers": ["nats://localhost:4222"]},
        "channels": [{"domain": "cytu.be", "channel": "420grindhouse"}]
    }

    client = KrytenClient(config)
    await client.connect()

    try:
        stats = await client.get_stats()
        print("Full stats structure:")
        print(json.dumps(stats, indent=2))

    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

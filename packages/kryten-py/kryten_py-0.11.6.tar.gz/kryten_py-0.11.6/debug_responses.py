#!/usr/bin/env python3
"""Debug script to see actual response structure."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from kryten import KrytenClient  # noqa: E402


async def debug_responses():
    config = {
        "nats": {"servers": ["nats://localhost:4222"]},
        "channels": [{"domain": "cytu.be", "channel": "420grindhouse"}],
    }

    client = KrytenClient(config)
    await client.connect()

    try:
        print("Testing ping...")
        request = {"service": "robot", "command": "system.ping"}
        response = await client.nats_request("kryten.robot.command", request, timeout=5.0)
        print("Ping response:")
        print(json.dumps(response, indent=2))
        print()

        print("Testing get_stats...")
        request = {"service": "robot", "command": "system.stats"}
        response = await client.nats_request("kryten.robot.command", request, timeout=5.0)
        print("Stats response (keys only):")
        print(f"  success: {response.get('success')}")
        print(f"  data keys: {list(response.get('data', {}).keys())}")
        print()

        print("Testing reload...")
        request = {"service": "robot", "command": "system.reload"}
        response = await client.nats_request("kryten.robot.command", request, timeout=5.0)
        print("Reload response:")
        print(json.dumps(response, indent=2))

    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(debug_responses())

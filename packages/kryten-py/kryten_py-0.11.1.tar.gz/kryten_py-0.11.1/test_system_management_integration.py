#!/usr/bin/env python3
"""Integration tests for KrytenClient system management methods.

Tests the 5 new system management methods against a running Kryten-Robot instance:
- get_stats()
- get_config()
- ping()
- reload_config()
- shutdown() [validation only, won't actually shutdown]
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for development testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kryten import KrytenClient  # noqa: E402


class TestResult:
    """Track test results."""

    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error = None
        self.details = None

    def success(self, details=None):
        self.passed = True
        self.details = details

    def fail(self, error):
        self.passed = False
        self.error = str(error)


async def test_ping(client: KrytenClient) -> TestResult:
    """Test system ping for alive check."""
    result = TestResult("ping()")

    try:
        response = await client.ping()

        # Validate response structure
        if "pong" not in response:
            result.fail("Missing 'pong' in response")
            return result

        if "timestamp" not in response:
            result.fail("Missing 'timestamp' in response")
            return result

        if "uptime_seconds" not in response:
            result.fail("Missing 'uptime_seconds' in response")
            return result

        if response["pong"] is not True:
            result.fail(f"Expected pong=True, got '{response['pong']}'")
            return result

        # Try to parse timestamp
        try:
            datetime.fromisoformat(response["timestamp"].replace("Z", "+00:00"))
        except Exception as e:
            result.fail(f"Invalid timestamp format: {e}")
            return result

        result.success(
            {
                "pong": response["pong"],
                "timestamp": response["timestamp"],
                "uptime_seconds": round(response["uptime_seconds"], 2),
                "version": response.get("version", "N/A"),
                "response_time": "< 2s",
            }
        )

    except Exception as e:
        result.fail(e)

    return result


async def test_get_stats(client: KrytenClient) -> TestResult:
    """Test getting comprehensive runtime statistics."""
    result = TestResult("get_stats()")

    try:
        stats = await client.get_stats()

        # Validate required top-level keys
        required_keys = ["uptime_seconds", "events", "commands", "connections", "state"]
        missing = [k for k in required_keys if k not in stats]
        if missing:
            result.fail(f"Missing required keys: {missing}")
            return result

        # Validate uptime is a number
        if not isinstance(stats["uptime_seconds"], int | float) or stats["uptime_seconds"] < 0:
            result.fail(f"Invalid uptime_seconds: {stats['uptime_seconds']}")
            return result

        # Validate events structure
        events = stats["events"]
        if not isinstance(events.get("published"), int):
            result.fail("events.published must be int")
            return result

        if not isinstance(events.get("rate_1min"), int | float):
            result.fail("events.rate_1min must be numeric")
            return result

        # Validate commands structure (may be empty if command subscriber not running)
        commands = stats["commands"]
        if commands:  # Only validate if populated
            if "total_received" in commands and not isinstance(commands.get("total_received"), int):
                result.fail("commands.total_received must be int")
                return result

            if "succeeded" in commands and not isinstance(commands.get("succeeded"), int):
                result.fail("commands.succeeded must be int")
                return result

        # Validate queries structure (alternative to commands)
        if "queries" in stats:
            queries = stats["queries"]
            if "processed" in queries and not isinstance(queries.get("processed"), int):
                result.fail("queries.processed must be int")
                return result

        # Validate connections structure
        connections = stats["connections"]
        if "cytube" not in connections or "nats" not in connections:
            result.fail("Missing cytube or nats in connections")
            return result

        # Validate state structure (check for either format)
        state = stats["state"]
        state_keys = [
            "users",
            "playlist",
            "emotes",
            "users_online",
            "playlist_items",
            "emotes_count",
        ]
        if not any(k in state for k in state_keys):
            result.fail(f"Missing state keys, got: {list(state.keys())}")
            return result

        # Build result with flexible keys
        result_data = {
            "uptime_hours": round(stats["uptime_seconds"] / 3600, 2),
            "events_total": stats["events"]["published"],
            "events_rate_1min": round(stats["events"]["rate_1min"], 2),
        }

        # Add commands or queries stats
        if commands:
            result_data["commands_total"] = commands.get("total_received", 0)
            result_data["commands_succeeded"] = commands.get("succeeded", 0)
        elif "queries" in stats:
            result_data["queries_processed"] = stats["queries"].get("processed", 0)

        result_data.update(
            {
                "cytube_connected": connections["cytube"].get("connected", False),
                "nats_connected": connections["nats"].get("connected", False),
                "users_count": state.get("users") or state.get("users_online", 0),
                "playlist_count": state.get("playlist") or state.get("playlist_items", 0),
                "emotes_count": state.get("emotes") or state.get("emotes_count", 0),
                "memory_rss_mb": stats.get("memory", {}).get("rss_mb", "N/A"),
            }
        )

        result.success(result_data)

    except Exception as e:
        result.fail(e)

    return result


async def test_get_config(client: KrytenClient) -> TestResult:
    """Test getting configuration with password redaction."""
    result = TestResult("get_config()")

    try:
        config = await client.get_config()

        # Validate required top-level keys
        required_keys = ["cytube", "nats", "commands", "health", "log_level"]
        missing = [k for k in required_keys if k not in config]
        if missing:
            result.fail(f"Missing required keys: {missing}")
            return result

        # Validate CyTube config
        cytube = config["cytube"]
        if not all(k in cytube for k in ["domain", "channel"]):
            result.fail("Missing domain or channel in cytube config")
            return result

        # Check password redaction
        if "password" in cytube:
            if cytube["password"] != "***REDACTED***":
                result.fail("CyTube password not redacted")
                return result

        # Validate NATS config
        nats = config["nats"]
        if "servers" not in nats:
            result.fail("Missing servers in nats config")
            return result

        # Check NATS password redaction
        if "password" in nats and nats["password"]:
            if nats["password"] != "***REDACTED***":
                result.fail("NATS password not redacted")
                return result

        # Validate commands config
        commands_cfg = config["commands"]
        if "enabled" not in commands_cfg:
            result.fail("Missing enabled in commands config")
            return result

        result.success(
            {
                "domain": cytube["domain"],
                "channel": cytube["channel"],
                "nats_servers": nats["servers"],
                "commands_enabled": commands_cfg["enabled"],
                "health_enabled": config["health"].get("enabled", False),
                "log_level": config["log_level"],
                "passwords_redacted": True,
            }
        )

    except Exception as e:
        result.fail(e)

    return result


async def test_reload_config(client: KrytenClient) -> TestResult:
    """Test configuration reload (no actual changes)."""
    result = TestResult("reload_config()")

    try:
        response = await client.reload_config()

        # Validate response structure
        required_keys = ["success", "message", "changes", "errors"]
        missing = [k for k in required_keys if k not in response]
        if missing:
            result.fail(f"Missing required keys: {missing}")
            return result

        if not isinstance(response["success"], bool):
            result.fail("success must be boolean")
            return result

        if not isinstance(response["changes"], dict):
            result.fail("changes must be dict")
            return result

        if not isinstance(response["errors"], list):
            result.fail("errors must be list")
            return result

        # For unchanged config, should succeed with no changes
        result.success(
            {
                "success": response["success"],
                "message": response["message"],
                "changes_count": len(response["changes"]),
                "errors_count": len(response["errors"]),
            }
        )

    except Exception as e:
        result.fail(e)

    return result


async def test_shutdown_validation(client: KrytenClient) -> TestResult:
    """Test shutdown parameter validation (won't actually shutdown)."""
    result = TestResult("shutdown() validation")

    try:
        # Test 1: Invalid delay (too high)
        try:
            await client.shutdown(delay_seconds=400, reason="Test")
            result.fail("Should have rejected delay > 300")
            return result
        except ValueError as e:
            if "between 0 and 300" not in str(e):
                result.fail(f"Wrong error message: {e}")
                return result

        # Test 2: Invalid delay (negative)
        try:
            await client.shutdown(delay_seconds=-5, reason="Test")
            result.fail("Should have rejected negative delay")
            return result
        except ValueError as e:
            if "between 0 and 300" not in str(e):
                result.fail(f"Wrong error message: {e}")
                return result

        # Test 3: Invalid delay (non-integer)
        try:
            await client.shutdown(delay_seconds="invalid", reason="Test")
            result.fail("Should have rejected non-integer delay")
            return result
        except (ValueError, TypeError):
            pass  # Expected

        result.success(
            {
                "validation": "All parameter validations working correctly",
                "note": "Shutdown not actually triggered",
            }
        )

    except Exception as e:
        result.fail(e)

    return result


async def run_tests():
    """Run all integration tests."""
    print("=" * 80)
    print("KrytenClient System Management Integration Tests")
    print("=" * 80)
    print("\nConnecting to NATS...")

    # Configure client
    config = {
        "nats": {"servers": ["nats://localhost:4222"]},
        "channels": [{"domain": "cytu.be", "channel": "420grindhouse"}],
    }

    client = KrytenClient(config)

    try:
        await client.connect()
        print("✅ Connected to NATS\n")

        # Run tests in order
        tests = [
            test_ping,
            test_get_stats,
            test_get_config,
            test_reload_config,
            test_shutdown_validation,
        ]

        results = []
        for test_func in tests:
            print(f"Running {test_func.__name__}...")
            test_result = await test_func(client)
            results.append(test_result)

            if test_result.passed:
                print("  ✅ PASSED")
                if test_result.details:
                    for key, value in test_result.details.items():
                        print(f"     {key}: {value}")
            else:
                print(f"  ❌ FAILED: {test_result.error}")
            print()

        # Summary
        print("=" * 80)
        print("Test Summary")
        print("=" * 80)

        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed)

        for r in results:
            status = "✅" if r.passed else "❌"
            print(f"{status} {r.name}")

        print(f"\nTotal: {len(results)} tests")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")

        if failed > 0:
            print("\n❌ Some tests failed!")
            sys.exit(1)
        else:
            print("\n✅ All tests passed!")
            sys.exit(0)

    except Exception as e:
        print(f"\n❌ Test setup failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    finally:
        await client.disconnect()
        print("\nDisconnected from NATS")


if __name__ == "__main__":
    asyncio.run(run_tests())

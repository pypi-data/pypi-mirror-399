"""Tests for metrics server."""

from unittest.mock import MagicMock

import pytest
from kryten.metrics_server import BaseMetricsServer, SimpleMetricsServer


class ConcreteMetricsServer(BaseMetricsServer):
    """Concrete implementation for testing."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.custom_value = 42

    async def _collect_custom_metrics(self) -> list[str]:
        return [
            "# HELP test_custom_metric A custom metric",
            "# TYPE test_custom_metric gauge",
            f"test_custom_metric {self.custom_value}",
            "",
        ]

    async def _get_health_details(self) -> dict:
        return {
            "custom_status": "ok",
            "custom_value": self.custom_value,
        }


class TestSimpleMetricsServer:
    """Tests for SimpleMetricsServer."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test server initialization."""
        server = SimpleMetricsServer(
            service_name="test-service",
            port=8888
        )

        assert server.service_name == "test-service"
        assert server.port == 8888
        assert server._running is False

    @pytest.mark.asyncio
    async def test_custom_metrics_callback(self):
        """Test custom metrics via callback."""
        async def my_metrics():
            return ["# HELP foo Foo metric", "foo 123"]

        server = SimpleMetricsServer(
            service_name="test",
            metrics_callback=my_metrics
        )

        result = await server._collect_custom_metrics()
        assert "foo 123" in result

    @pytest.mark.asyncio
    async def test_custom_metrics_sync_callback(self):
        """Test custom metrics with sync callback."""
        def my_metrics():
            return ["# HELP bar Bar metric", "bar 456"]

        server = SimpleMetricsServer(
            service_name="test",
            metrics_callback=my_metrics
        )

        result = await server._collect_custom_metrics()
        assert "bar 456" in result

    @pytest.mark.asyncio
    async def test_health_callback(self):
        """Test health details via callback."""
        async def my_health():
            return {"db": "connected", "items": 100}

        server = SimpleMetricsServer(
            service_name="test",
            health_callback=my_health
        )

        result = await server._get_health_details()
        assert result["db"] == "connected"
        assert result["items"] == 100

    @pytest.mark.asyncio
    async def test_collect_all_metrics(self):
        """Test full metrics collection."""
        server = SimpleMetricsServer(
            service_name="myservice",
            port=8080
        )

        metrics = await server._collect_all_metrics()

        assert "myservice_uptime_seconds" in metrics
        assert "myservice_service_status" in metrics

    @pytest.mark.asyncio
    async def test_collect_metrics_with_client(self):
        """Test metrics collection with client."""
        mock_client = MagicMock()
        mock_client._running = True

        server = SimpleMetricsServer(
            service_name="myservice",
            client=mock_client
        )

        metrics = await server._collect_all_metrics()

        assert "myservice_nats_connected 1" in metrics


class TestConcreteMetricsServer:
    """Tests for concrete BaseMetricsServer implementation."""

    @pytest.mark.asyncio
    async def test_custom_metrics(self):
        """Test custom metrics from subclass."""
        server = ConcreteMetricsServer(service_name="concrete")

        result = await server._collect_custom_metrics()

        assert "test_custom_metric 42" in result

    @pytest.mark.asyncio
    async def test_health_details(self):
        """Test health details from subclass."""
        server = ConcreteMetricsServer(service_name="concrete")

        result = await server._get_health_details()

        assert result["custom_status"] == "ok"
        assert result["custom_value"] == 42

    @pytest.mark.asyncio
    async def test_build_health_response(self):
        """Test full health response."""
        server = ConcreteMetricsServer(service_name="concrete")

        health = await server._build_health_response()

        assert health["service"] == "concrete"
        assert health["status"] in ["healthy", "degraded"]
        assert "uptime_seconds" in health
        assert health["custom_status"] == "ok"

    @pytest.mark.asyncio
    async def test_health_response_with_connected_client(self):
        """Test health response with connected NATS client."""
        mock_client = MagicMock()
        mock_client._running = True

        server = ConcreteMetricsServer(
            service_name="test",
            client=mock_client
        )

        health = await server._build_health_response()

        assert health["nats_connected"] is True
        assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_response_with_disconnected_client(self):
        """Test health response with disconnected NATS client."""
        mock_client = MagicMock()
        mock_client._running = False

        server = ConcreteMetricsServer(
            service_name="test",
            client=mock_client
        )

        health = await server._build_health_response()

        assert health["nats_connected"] is False
        assert health["status"] == "degraded"


class TestMetricsServerLifecycle:
    """Tests for server start/stop lifecycle."""

    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Test server start and stop."""
        server = SimpleMetricsServer(
            service_name="test",
            port=18282  # Use non-standard port for testing
        )

        # Start server
        await server.start()
        assert server._running is True
        assert server._site is not None

        # Stop server
        await server.stop()
        assert server._running is False

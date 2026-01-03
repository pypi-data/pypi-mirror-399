"""Shared test fixtures and configuration."""


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "asyncio: mark test as async")

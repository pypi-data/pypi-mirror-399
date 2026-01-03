# Kryten-py Developer Guide

This document provides comprehensive information for developers working on the kryten-py library itself.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Design Patterns](#design-patterns)
- [Testing Strategy](#testing-strategy)
- [Code Quality](#code-quality)
- [Release Process](#release-process)
- [Contributing Guidelines](#contributing-guidelines)
- [Troubleshooting](#troubleshooting)

## Architecture Overview

### System Context

```
┌─────────────────┐
│   Bot/Service   │
│   (User Code)   │
└────────┬────────┘
         │
         │ imports & uses
         ▼
┌─────────────────┐
│   kryten-py     │◄─── This Library
│   (Python Lib)  │
└────────┬────────┘
         │
         │ NATS protocol
         ▼
┌─────────────────┐
│  NATS Message   │
│      Bus        │
└────────┬────────┘
         │
         │ subscribes/publishes
         ▼
┌─────────────────┐
│  Kryten Bridge  │
│  (Node.js/TS)   │
└────────┬────────┘
         │
         │ WebSocket
         ▼
┌─────────────────┐
│  CyTube Server  │
└─────────────────┘
```

### Message Flow

**Event Flow (CyTube → Bot)**:
1. CyTube emits event over WebSocket
2. Kryten Bridge receives and transforms to NATS message
3. NATS publishes on `cytube.events.{domain}.{channel}.{event_name}`
4. kryten-py subscribes and dispatches to registered handlers
5. User's handler function executes

**Command Flow (Bot → CyTube)**:
1. User code calls command method (e.g., `send_chat()`)
2. kryten-py constructs NATS message with correlation ID
3. NATS publishes on `cytube.commands.{channel}.{action}`
4. Kryten Bridge receives and forwards over WebSocket
5. CyTube server executes command

### Key Design Decisions

1. **Async-Only API**: Enforces modern async patterns, simplifies concurrency
2. **Decorator-Based Handlers**: Clean, Pythonic event registration
3. **Pydantic v2 Models**: Type-safe configuration and events with validation
4. **NATS Wildcards**: Single subscription handles all events efficiently
5. **Correlation IDs**: Distributed tracing for debugging
6. **Mock Client**: Testing without external dependencies

## Development Setup

### Prerequisites

- **Python 3.11+** (required for TaskGroup, improved typing)
- **Poetry 1.7+** (dependency management)
- **Git** (version control)
- **NATS Server** (optional, for integration tests)

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd kryten-py

# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
uv sync

# Activate virtual environment
poetry shell

# Verify installation
uv run pytest
uv run mypy src/kryten
uv run ruff check src
uv run black --check src
```

### IDE Setup

**VS Code** (recommended):
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

**PyCharm**:
- Set Poetry environment as project interpreter
- Enable MyPy plugin
- Configure Black as formatter
- Enable Ruff linter

## Project Structure

```
kryten-py/
├── src/kryten/              # Main package source
│   ├── __init__.py          # Public API exports
│   ├── client.py            # KrytenClient implementation
│   ├── mock.py              # MockKrytenClient for testing
│   ├── config.py            # Configuration Pydantic models
│   ├── models.py            # Event Pydantic models
│   ├── health.py            # Health monitoring models
│   ├── exceptions.py        # Exception hierarchy
│   ├── subject_builder.py   # NATS subject utilities
│   └── py.typed             # PEP 561 marker for type hints
│
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest fixtures
│   ├── test_config.py       # Configuration tests
│   ├── test_models.py       # Event model tests
│   ├── test_subject_builder.py  # Subject builder tests
│   └── test_mock.py         # Mock client tests
│
├── examples/                # Example bots
│   └── echo_bot.py          # Simple echo bot
│
├── docs/                    # Documentation (future)
│   └── api/                 # API reference (future)
│
├── .github/                 # GitHub Actions (future)
│   └── workflows/
│       └── test.yml
│
├── pyproject.toml           # Poetry config & dependencies
├── README.md                # User documentation
├── DEVELOPER.md             # This file
├── STATUS.md                # Implementation status
├── LICENSE                  # MIT License
└── .gitignore               # Git ignore patterns
```

## Core Components

### 1. KrytenClient (`client.py`)

**Purpose**: Main async client for interacting with CyTube via NATS.

**Key Responsibilities**:
- NATS connection lifecycle management
- Event subscription with wildcard patterns
- Handler registration and dispatch
- Command publishing with retry logic
- Health metrics tracking
- Connection callbacks (error, disconnect, reconnect)

**Implementation Details**:

```python
# Handler storage structure
self._handlers: dict[
    str,  # event_name (lowercase)
    list[tuple[
        Callable[[Any], Any],  # handler function
        str | None,            # channel filter
        str | None             # domain filter
    ]]
]
```

**Connection Flow**:
1. `connect()` → Establish NATS connection
2. Subscribe to `cytube.events.{domain}.{channel}.>` per channel
3. Register message callback → `_handle_raw_message()`
4. Parse subject → Extract domain, channel, event_name
5. Match handlers → Check filters
6. Dispatch → Invoke matching handlers with timeout

**Command Flow**:
1. User calls command method (e.g., `send_chat()`)
2. Build subject via `build_command_subject()`
3. Serialize payload to JSON bytes
4. Call `_publish()` with retry logic
5. Track metrics (commands_sent, errors)

**Error Handling**:
- Connection errors → KrytenConnectionError
- Validation errors → KrytenValidationError
- Publish errors → PublishError (after retries)
- Handler errors → Logged, execution continues
- Timeouts → KrytenTimeoutError

### 2. MockKrytenClient (`mock.py`)

**Purpose**: Test double for unit testing without NATS.

**Key Features**:
- Same API surface as KrytenClient
- Records all published commands for assertion
- Simulates event delivery to handlers
- No network dependencies

**Usage Pattern**:
```python
async with MockKrytenClient(config) as client:
    @client.on("chatmsg")
    async def handler(event):
        pass
    
    await client.send_chat("lounge", "test")
    
    commands = client.get_published_commands()
    assert len(commands) == 1
    assert commands[0]["action"] == "sendChat"
```

### 3. Configuration (`config.py`)

**Purpose**: Type-safe configuration with validation.

**Models**:
- `NatsConfig`: NATS connection settings (servers, auth, TLS)
- `ChannelConfig`: CyTube channel specification (domain, channel)
- `KrytenConfig`: Complete client configuration

**Features**:
- Pydantic v2 validation
- Field constraints (non-empty strings, positive numbers)
- Class methods: `from_json()`, `from_yaml()`
- Environment variable substitution: `${VAR_NAME}`

**Example**:
```json
{
  "nats": {
    "servers": ["nats://localhost:4222"],
    "user": "${NATS_USER}",
    "password": "${NATS_PASSWORD}"
  },
  "channels": [
    {"domain": "cytu.be", "channel": "lounge"}
  ],
  "retry_attempts": 3,
  "handler_timeout": 30.0
}
```

### 4. Event Models (`models.py`)

**Purpose**: Type-safe event data models.

**Base Model**:
- `RawEvent`: Immutable frozen model with all event data
  - Auto-generates timestamp (UTC)
  - Auto-generates correlation_id (UUID4)
  - `to_bytes()` → JSON serialization for NATS

**Typed Events**:
- `ChatMessageEvent`: Chat messages
- `UserJoinEvent`: User joined channel
- `UserLeaveEvent`: User left channel
- `ChangeMediaEvent`: Media changed
- `PlaylistUpdateEvent`: Playlist modified

**Future Extension**: Add more event types as CyTube expands.

### 5. Subject Builder (`subject_builder.py`)

**Purpose**: NATS subject construction and parsing.

**Functions**:
- `sanitize_token()`: Remove invalid characters for NATS
- `build_subject()`: Generic subject builder
- `build_event_subject()`: Event subject format
- `build_command_subject()`: Command subject format
- `parse_subject()`: Extract domain, channel, event from subject

**Subject Formats**:
```
Events:   cytube.events.{domain}.{channel}.{event_name}
Commands: cytube.commands.{channel}.{action}
```

**NATS Constraints**:
- Max length: 255 characters
- Allowed: alphanumeric, `-`, `_`, `.`, `*`, `>`
- No spaces or special characters

**TLD Detection**: Heuristic to extract domain from full hostname
- `localhost` → `localhost`
- `cytu.be` → `cytu.be`
- `sync.example.com` → `example.com`

### 6. Health Monitoring (`health.py`)

**Purpose**: Client health status and metrics.

**Models**:
- `ChannelInfo`: Per-channel connection info
  - domain, channel, connected, subscribed
- `HealthStatus`: Overall client status
  - state (connecting, connected, disconnected, error)
  - uptime, events_received, commands_sent
  - errors, avg_latency, handlers_registered

**Usage**:
```python
status = client.health()
print(f"State: {status.state}")
print(f"Events: {status.events_received}")
print(f"Errors: {status.errors}")
```

### 7. Exceptions (`exceptions.py`)

**Purpose**: Domain-specific exception hierarchy.

**Hierarchy**:
```
KrytenError (base)
├── KrytenConnectionError      # NATS connection failures
├── KrytenValidationError      # Config/payload validation
├── KrytenTimeoutError         # Operation timeouts
├── PublishError               # Message publish failures
└── HandlerError               # Handler execution errors
```

**Usage**:
```python
try:
    await client.connect()
except KrytenConnectionError as e:
    logger.error(f"Connection failed: {e}")
```

## Design Patterns

### 1. Decorator Pattern (Event Handlers)

**Why**: Clean, Pythonic API for registering event handlers.

```python
@client.on("chatmsg")
async def handle_chat(event: ChatMessageEvent):
    print(f"{event.username}: {event.message}")
```

**Implementation**:
- `on()` returns a decorator function
- Decorator stores handler in `_handlers` dict with filters
- Filters applied during dispatch (channel, domain)

### 2. Context Manager (Async)

**Why**: RAII pattern ensures proper cleanup.

```python
async with KrytenClient(config) as client:
    @client.on("chatmsg")
    async def handler(event):
        pass
    await client.run()
# Automatic disconnect on exit
```

**Implementation**:
- `__aenter__()` → calls `connect()`
- `__aexit__()` → calls `disconnect()`

### 3. Observer Pattern (Event Dispatch)

**Why**: Decouple event source from handlers.

**Flow**:
1. NATS message arrives
2. Subject parsed to determine event type
3. All matching handlers notified
4. Handlers execute concurrently (TaskGroup)

### 4. Strategy Pattern (Mock vs Real Client)

**Why**: Same interface, different implementations.

- `KrytenClient`: Real NATS connection
- `MockKrytenClient`: In-memory simulation

**Benefit**: Tests use mock, production uses real.

### 5. Builder Pattern (Subject Construction)

**Why**: Complex subject creation logic encapsulated.

```python
subject = build_event_subject(
    domain="cytu.be",
    channel="lounge",
    event_name="chatmsg"
)
# → "cytube.events.cytu.be.lounge.chatmsg"
```

### 6. Retry Pattern (Publish Commands)

**Why**: Transient network failures should be recoverable.

**Implementation**:
- Exponential backoff: 0.1s, 0.2s, 0.4s, ...
- Configurable max attempts (default: 3)
- Final failure → PublishError

## Testing Strategy

### Test Organization

```
tests/
├── test_config.py           # Configuration validation
├── test_models.py           # Event model serialization
├── test_subject_builder.py  # Subject parsing/building
└── test_mock.py             # Mock client behavior
```

### Test Categories

**1. Unit Tests** (Current: 43 tests)
- Configuration validation (11 tests)
- Event model creation (11 tests)
- Subject builder logic (15 tests)
- Mock client behavior (7 tests)

**2. Integration Tests** (Future)
- Real NATS connection
- End-to-end message flow
- Kryten Bridge integration
- Use testcontainers for NATS

**3. Property-Based Tests** (Future)
- Use Hypothesis for fuzzing
- Subject builder edge cases
- Configuration combinations

### Coverage Goals

- **Current**: 60% (588 statements, 233 missed)
- **Target**: 80%+ overall
- **Critical paths**: 95%+ (connection, dispatch, publish)

**Uncovered Areas** (High Priority):
- `client.py` connection lifecycle (lines 62-97)
- `client.py` message handling (lines 642-686)
- `client.py` retry logic (lines 763-775)
- `mock.py` simulate_event (lines 334-362)

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=kryten --cov-report=html

# Specific test file
uv run pytest tests/test_config.py

# Specific test function
uv run pytest tests/test_config.py::test_nats_config_valid

# Verbose output
uv run pytest -v

# Stop on first failure
uv run pytest -x

# Run in parallel (requires pytest-xdist)
uv run pytest -n auto
```

### Writing Tests

**Example Test**:
```python
import pytest
from kryten import MockKrytenClient, ChatMessageEvent

@pytest.mark.asyncio
async def test_send_chat_records_command():
    """Test that send_chat records the command."""
    config = {
        "nats": {"servers": ["nats://localhost:4222"]},
        "channels": [{"domain": "cytu.be", "channel": "test"}]
    }
    
    async with MockKrytenClient(config) as client:
        await client.send_chat("test", "Hello, world!")
        
        commands = client.get_published_commands()
        assert len(commands) == 1
        assert commands[0]["action"] == "sendChat"
        assert commands[0]["payload"]["message"] == "Hello, world!"
```

**Best Practices**:
- Use `pytest.mark.asyncio` for async tests
- Use fixtures for common setup (see `conftest.py`)
- Test both success and failure cases
- Mock external dependencies (NATS)
- Clear, descriptive test names
- One assertion per test (when practical)

## Code Quality

### Type Checking (MyPy)

**Configuration** (`pyproject.toml`):
```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Run**:
```bash
uv run mypy src/kryten
```

**Standards**:
- 100% type hint coverage
- Strict mode enabled
- No `Any` types without justification
- Proper generic types (Callable[[T], R])

### Linting (Ruff)

**Configuration** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
select = ["E", "W", "F", "I", "B", "C4", "UP"]
```

**Run**:
```bash
# Check
uv run ruff check src

# Auto-fix
uv run ruff check --fix src
```

**Rules**:
- E/W: PEP 8 style
- F: Pyflakes errors
- I: Import sorting
- B: Bugbear (common mistakes)
- C4: Comprehensions
- UP: Modern Python upgrades

### Formatting (Black)

**Configuration** (`pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ["py311"]
```

**Run**:
```bash
# Check
uv run black --check src

# Format
uv run black src
```

**Standards**:
- 100 character line length
- Double quotes for strings
- Trailing commas in multi-line structures

### Pre-Commit Checks

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
set -e

echo "Running pre-commit checks..."

# Format check
uv run black --check src tests

# Lint
uv run ruff check src tests

# Type check
uv run mypy src/kryten

# Tests
uv run pytest

echo "All checks passed!"
```

## Release Process

### Version Management

**Semantic Versioning** (SemVer):
- **Major** (1.0.0): Breaking API changes
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.0.1): Bug fixes

**Update Version**:
```bash
# pyproject.toml
[tool.poetry]
version = "0.2.0"

# src/kryten/__init__.py
__version__ = "0.2.0"
```

### Release Checklist

1. **Update Version Numbers**
   - `pyproject.toml`
   - `src/kryten/__init__.py`
   - Update `CHANGELOG.md`

2. **Run Full Test Suite**
   ```bash
   uv run pytest --cov=kryten
   uv run mypy src/kryten
   uv run ruff check src
   uv run black --check src
   ```

3. **Build Package**
   ```bash
   uv build
   ```

4. **Test Installation**
   ```bash
   # In separate virtualenv
   pip install dist/kryten_py-0.2.0-py3-none-any.whl
   python -c "from kryten import KrytenClient; print('OK')"
   ```

5. **Tag Release**
   ```bash
   git tag -a v0.2.0 -m "Release 0.2.0"
   git push origin v0.2.0
   ```

6. **Publish to PyPI**
   ```bash
   uv publish
   ```

7. **GitHub Release**
   - Create release from tag
   - Attach wheel and sdist
   - Copy changelog entries

### Changelog Format

```markdown
## [0.2.0] - 2025-01-15

### Added
- New command: `set_shuffle_playlist()`
- Health monitoring dashboard example

### Changed
- Improved error messages in connection failures
- Updated nats-py to 2.12.0

### Fixed
- Bug in subject parsing for localhost domains
- Race condition in handler dispatch

### Deprecated
- `old_method()` will be removed in 1.0.0

### Security
- Updated dependencies to patch CVE-XXXX-YYYY
```

## Contributing Guidelines

### Getting Started

1. **Fork Repository**
2. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

4. **Run Quality Checks**
   ```bash
   uv run pytest
   uv run mypy src/kryten
   uv run ruff check src
   uv run black src
   ```

5. **Commit Changes**
   ```bash
   git commit -m "feat: add amazing feature"
   ```

6. **Push to Fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open Pull Request**

### Commit Message Format

**Conventional Commits**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build/tooling changes

**Examples**:
```
feat(client): add voteskip command

Implement voteskip command to allow bots to initiate
skip votes on current media.

Closes #42

fix(subject): handle localhost domain correctly

The subject parser was incorrectly handling localhost
domains. Updated TLD detection logic to special-case
localhost.

Fixes #38
```

### Code Review Checklist

**For Authors**:
- [ ] Tests pass locally
- [ ] Type checking passes
- [ ] Linting passes
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] No merge conflicts

**For Reviewers**:
- [ ] Code follows project style
- [ ] Tests cover new functionality
- [ ] No obvious bugs or edge cases
- [ ] Documentation is clear
- [ ] Breaking changes justified
- [ ] Performance implications considered

### Areas for Contribution

**High Priority**:
- GitHub Actions CI/CD workflow
- Integration tests with NATS
- Increase test coverage to 80%+
- More example bots

**Medium Priority**:
- Additional event type models
- Automatic reconnection logic improvements
- Performance benchmarking
- Logging improvements

**Low Priority**:
- Web dashboard for monitoring
- Plugin system for extensions
- Alternative serialization formats

## Troubleshooting

### Common Issues

**1. Import Errors After Install**

```python
# Error
ModuleNotFoundError: No module named 'kryten'

# Solution
uv sync  # Reinstall in development mode
```

**2. Type Checking Fails on Callable**

```python
# Error
Missing type parameters for generic type "Callable"

# Solution
from collections.abc import Callable
handler: Callable[[Event], None]  # Specify types
```

**3. Tests Hang or Timeout**

```python
# Error
asyncio.TimeoutError in tests

# Solution
# Add timeout marker
@pytest.mark.timeout(5)
async def test_something():
    ...
```

**4. NATS Connection Refused**

```python
# Error
KrytenConnectionError: Connection refused

# Solution
# Check NATS server is running
docker run -p 4222:4222 nats:latest
```

**5. Handler Not Triggered**

```python
# Problem
Handler registered but never called

# Check
1. Event name matches exactly (case-insensitive)
2. Channel/domain filters match
3. Subscription established before events arrive
4. client.run() is called
```

### Debugging Tips

**Enable Debug Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Inspect Handler Registration**:
```python
client = KrytenClient(config)

@client.on("chatmsg")
async def handler(event):
    pass

print(client._handlers)  # Internal inspection
```

**Test Subject Parsing**:
```python
from kryten.subject_builder import parse_subject

subject = "cytube.events.cytu.be.lounge.chatmsg"
parsed = parse_subject(subject)
print(parsed)  # {'domain': 'cytu.be', 'channel': 'lounge', 'event': 'chatmsg'}
```

**Mock NATS Messages**:
```python
async with MockKrytenClient(config) as client:
    @client.on("chatmsg")
    async def handler(event):
        print(f"Received: {event}")
    
    # Simulate event
    await client.simulate_event(
        "chatmsg",
        {"username": "test", "message": "hello"}
    )
```

### Performance Profiling

**cProfile**:
```bash
python -m cProfile -o output.prof examples/echo_bot.py
python -m pstats output.prof
```

**Memory Profiling** (memory_profiler):
```python
from memory_profiler import profile

@profile
async def main():
    async with KrytenClient(config) as client:
        await client.run()
```

**Asyncio Debugging**:
```python
import asyncio

# Enable debug mode
asyncio.run(main(), debug=True)
```

## Additional Resources

### Documentation
- [NATS Python Client](https://github.com/nats-io/nats.py)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Async Programming](https://docs.python.org/3/library/asyncio.html)

### Tools
- [Poetry](https://python-poetry.org/)
- [MyPy](https://mypy.readthedocs.io/)
- [Ruff](https://docs.astral.sh/ruff/)
- [Black](https://black.readthedocs.io/)
- [Pytest](https://docs.pytest.org/)

### Community
- [GitHub Issues](https://github.com/your-org/kryten-py/issues)
- [Discussions](https://github.com/your-org/kryten-py/discussions)
- [Discord](https://discord.gg/your-server)

---

**Last Updated**: December 2025  
**Document Version**: 1.0  
**Maintainers**: Kryten-py Core Team

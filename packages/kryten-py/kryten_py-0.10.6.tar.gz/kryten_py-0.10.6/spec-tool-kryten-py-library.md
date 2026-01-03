---
title: Kryten Python Library - CyTube NATS Integration Wrapper
version: 1.0
date_created: 2025-01-26
last_updated: 2025-01-26
owner: Development Team
tags: [tool, library, python, nats, cytube, microservices]
---

# Introduction

This specification defines the **kryten-py** library, a Python package that provides a high-level, developer-friendly API for building microservices that interact with CyTube servers via the Kryten bridge and NATS message bus. The library wraps the complexity of NATS connection management, message serialization, subject routing, and event handling into an intuitive, type-safe interface.

The library serves two primary use cases:
1. **Event Consumers**: Microservices that subscribe to CyTube events (chat messages, media changes, user actions) and react accordingly
2. **Command Publishers**: Applications that send commands to CyTube (chat messages, playlist manipulation, moderation actions)

By providing a unified, well-documented API, kryten-py enables rapid development of CyTube integrations such as chat bots, automated DJs, moderation tools, analytics systems, and more.

## 1. Purpose & Scope

### Purpose

The kryten-py library aims to:
- **Abstract NATS complexity**: Hide low-level NATS connection, subscription, and publishing details
- **Provide type safety**: Use Pydantic models and type hints for all data structures
- **Enable rapid development**: Offer high-level methods for common CyTube operations
- **Ensure reliability**: Include automatic reconnection, error handling, and graceful degradation
- **Support observability**: Provide structured logging, metrics, and health monitoring
- **Facilitate testing**: Enable easy mocking and unit testing of microservices

### Scope

**In Scope**:
- Async Python API (primary interface)
- NATS connection management with authentication and TLS
- Event subscription with decorator-based handlers
- Command publishing for all CyTube actions
- Configuration via dictionaries or Pydantic models
- Type-safe data models for events and commands
- Comprehensive error handling and retry logic
- Health monitoring and connection status
- Graceful shutdown handling
- Unit testing utilities (mock NATS client)

**Out of Scope**:
- Synchronous (blocking) API wrapper
- Direct CyTube Socket.IO connection (use Kryten bridge instead)
- CyTube server implementation
- NATS server deployment/configuration
- Web UI or CLI tools (separate packages)
- Non-Python language bindings

### Target Audience

- Python developers building CyTube microservices
- Bot developers creating chat automation
- System integrators connecting CyTube to external services
- DevOps engineers deploying CyTube-connected applications

### Assumptions

- Kryten bridge is deployed and operational with NATS enabled
- NATS server is accessible from application environment
- Python 3.11+ runtime is available
- Developers have basic understanding of async/await patterns
- CyTube server is operational and channels are configured

## 2. Definitions

| Term | Definition |
|------|------------|
| **Kryten Bridge** | Bidirectional gateway service connecting CyTube Socket.IO to NATS message bus |
| **NATS** | High-performance messaging system supporting pub/sub and request/reply patterns |
| **CyTube** | Synchronized media streaming platform with chat and playlist features |
| **Subject** | Hierarchical NATS message routing key (e.g., `cytube.events.cytu.be.lounge.chatmsg`) |
| **Event** | Message published by Kryten from CyTube to NATS (e.g., chat message received) |
| **Command** | Message published by client to NATS for Kryten to execute on CyTube (e.g., send chat) |
| **Handler** | Async function decorated to process specific event types |
| **Correlation ID** | UUID tracking event/command through distributed system for tracing |
| **Raw Event** | Unprocessed CyTube Socket.IO event wrapped with metadata (timestamp, correlation ID) |
| **Channel** | CyTube room where users watch media and chat (e.g., "lounge") |
| **Domain** | CyTube server hostname (e.g., "cytu.be") |

## 3. Requirements, Constraints & Guidelines

### Functional Requirements

#### Core Client

- **REQ-001**: Library MUST provide `KrytenClient` class as primary interface for all operations
- **REQ-002**: Client MUST support async/await patterns exclusively (no blocking operations)
- **REQ-003**: Client MUST establish NATS connection with configurable servers, authentication, and TLS
- **REQ-004**: Client MUST support connecting to multiple channels simultaneously
- **REQ-005**: Client MUST provide async context manager protocol (`async with`) for resource management

#### Event Subscription

- **REQ-006**: Client MUST support subscribing to CyTube events via NATS subjects
- **REQ-007**: Client MUST provide decorator-based event handler registration (`@client.on("event_name")`)
- **REQ-008**: Client MUST support wildcard subscriptions (e.g., all events from channel, all chat events)
- **REQ-009**: Client MUST deserialize NATS messages into typed Pydantic models
- **REQ-010**: Client MUST pass correlation IDs through event handlers for distributed tracing
- **REQ-011**: Client MUST support registering multiple handlers for same event type
- **REQ-012**: Client MUST invoke handlers concurrently using asyncio task spawning

#### Command Publishing

- **REQ-013**: Client MUST provide high-level methods for all CyTube commands (chat, playlist, moderation)
- **REQ-014**: Client MUST serialize command data into JSON payloads for NATS
- **REQ-015**: Client MUST publish commands to correct NATS subjects (`cytube.commands.{channel}.{action}`)
- **REQ-016**: Client MUST validate command parameters using Pydantic models before publishing
- **REQ-017**: Client MUST support publishing to specific channels or broadcast to all connected channels
- **REQ-018**: Client MUST generate correlation IDs for commands to enable request tracking

#### Connection Management

- **REQ-019**: Client MUST automatically reconnect to NATS on connection loss with exponential backoff
- **REQ-020**: Client MUST resubscribe to all event handlers after reconnection
- **REQ-021**: Client MUST provide `connect()` and `disconnect()` methods for explicit lifecycle management
- **REQ-022**: Client MUST drain pending messages before disconnecting
- **REQ-023**: Client MUST expose connection state (connected, connecting, disconnected, error)

#### Error Handling

- **REQ-024**: Client MUST raise typed exceptions for all error conditions (connection, validation, timeout)
- **REQ-025**: Client MUST log errors with structured context (correlation ID, event type, error details)
- **REQ-026**: Client MUST support configurable retry policies for transient failures
- **REQ-027**: Client MUST provide error callbacks for unhandled exceptions in event handlers
- **REQ-028**: Client MUST NOT crash on invalid event payloads (log and skip instead)

#### Configuration

- **REQ-029**: Client MUST accept configuration as dictionary or Pydantic `KrytenConfig` model
- **REQ-030**: Configuration MUST support environment variable substitution (e.g., `${NATS_TOKEN}`)
- **REQ-031**: Configuration MUST include NATS servers, credentials, channels, and optional settings
- **REQ-032**: Configuration MUST validate required fields and provide clear error messages
- **REQ-033**: Configuration MUST support loading from JSON/YAML files via helper function

#### Observability

- **REQ-034**: Client MUST use structured logging compatible with Python logging module
- **REQ-035**: Client MUST log connection lifecycle events (connected, reconnecting, disconnected)
- **REQ-036**: Client MUST log all published commands with correlation IDs
- **REQ-037**: Client MUST log all received events with correlation IDs
- **REQ-038**: Client MUST provide `health()` method returning connection status and statistics
- **REQ-039**: Client MUST track metrics (events received, commands sent, errors, latency)

#### Testing Support

- **REQ-040**: Library MUST provide `MockKrytenClient` for unit testing without NATS
- **REQ-041**: Mock client MUST support simulating event delivery to handlers
- **REQ-042**: Mock client MUST record published commands for verification
- **REQ-043**: Mock client MUST support simulating connection failures and reconnection

### Non-Functional Requirements

#### Performance

- **NFR-001**: Client MUST handle 1000+ events per second per channel without message loss
- **NFR-002**: Event handlers MUST execute concurrently without blocking each other
- **NFR-003**: Command publishing MUST complete within 100ms under normal conditions
- **NFR-004**: Memory usage MUST remain stable under continuous operation (no leaks)

#### Reliability

- **NFR-005**: Client MUST automatically recover from transient network failures within 30 seconds
- **NFR-006**: Client MUST maintain message ordering within same NATS subject
- **NFR-007**: Client MUST gracefully handle NATS server restarts without data loss
- **NFR-008**: Client MUST support at-least-once message delivery guarantees

#### Security

- **SEC-001**: Client MUST support NATS authentication (username/password, token, NKey)
- **SEC-002**: Client MUST support TLS encryption for NATS connections
- **SEC-003**: Client MUST NOT log sensitive credentials in plain text
- **SEC-004**: Client MUST validate event payloads to prevent injection attacks

#### Compatibility

- **COM-001**: Library MUST support Python 3.11+ (required for TaskGroup and asyncio improvements)
- **COM-002**: Library MUST depend only on stable, well-maintained packages (nats-py, pydantic, etc.)
- **COM-003**: Library MUST follow semantic versioning (MAJOR.MINOR.PATCH)
- **COM-004**: Library MUST maintain backward compatibility within major version

### Constraints

- **CON-001**: Library is Python-only (no C extensions for portability)
- **CON-002**: NATS subject length MUST NOT exceed 255 characters
- **CON-003**: Event payloads MUST be valid JSON (enforced by NATS serialization)
- **CON-004**: Channel and domain names MUST be sanitized for NATS subject compatibility
- **CON-005**: Maximum concurrent event handlers per event type is 1000 (asyncio task limit)

### Guidelines

- **GUD-001**: Prefer explicit configuration over implicit defaults
- **GUD-002**: Use Pydantic models for all structured data (events, commands, config)
- **GUD-003**: Follow PEP 8 style guide and use type hints everywhere
- **GUD-004**: Provide comprehensive docstrings with examples for all public APIs
- **GUD-005**: Use async context managers for resource cleanup
- **GUD-006**: Log at INFO level for lifecycle events, DEBUG for detailed traces
- **GUD-007**: Raise exceptions for programmer errors (bad config), log for runtime errors (network)
- **GUD-008**: Keep handler functions focused and avoid blocking operations

### Patterns

- **PAT-001**: Use decorator pattern for event handler registration
- **PAT-002**: Use builder pattern for complex command construction
- **PAT-003**: Use dependency injection for testability (accept logger, config)
- **PAT-004**: Use correlation IDs for distributed tracing across services
- **PAT-005**: Use exponential backoff for retry logic with jitter

## 4. Interfaces & Data Contracts

### Core Client Interface

```python
from typing import Optional, Callable, Awaitable, Any, Dict, List
from pydantic import BaseModel
import logging


class KrytenClient:
    """High-level client for CyTube interaction via NATS.
    
    Examples:
        Basic usage with context manager:
        
        >>> config = {
        ...     "nats": {"servers": ["nats://localhost:4222"]},
        ...     "channels": [{"domain": "cytu.be", "channel": "lounge"}]
        ... }
        >>> 
        >>> async with KrytenClient(config) as client:
        ...     @client.on("chatmsg")
        ...     async def handle_chat(event: ChatMessageEvent):
        ...         print(f"{event.username}: {event.message}")
        ...     
        ...     await client.send_chat("lounge", "Hello from bot!")
        ...     await client.run()  # Run until stopped
    """
    
    def __init__(
        self,
        config: Dict[str, Any] | KrytenConfig,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize client with configuration.
        
        Args:
            config: Dictionary or KrytenConfig model with NATS and channel settings
            logger: Optional logger instance (creates default if None)
        """
        ...
    
    async def connect(self) -> None:
        """Establish NATS connection and subscribe to configured channels.
        
        Raises:
            ConnectionError: If NATS connection fails after retries
            ValidationError: If configuration is invalid
        """
        ...
    
    async def disconnect(self) -> None:
        """Gracefully close NATS connection and cleanup resources."""
        ...
    
    async def __aenter__(self) -> "KrytenClient":
        """Async context manager entry (calls connect)."""
        ...
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit (calls disconnect)."""
        ...
    
    def on(
        self,
        event_name: str,
        channel: Optional[str] = None,
        domain: Optional[str] = None
    ) -> Callable[[Callable], Callable]:
        """Decorator to register event handler.
        
        Args:
            event_name: CyTube event type (e.g., "chatmsg", "adduser")
            channel: Optional specific channel filter (None = all channels)
            domain: Optional specific domain filter (None = all domains)
        
        Returns:
            Decorator function
        
        Examples:
            Handle all chat messages:
            
            >>> @client.on("chatmsg")
            ... async def on_chat(event: ChatMessageEvent):
            ...     print(event.message)
            
            Handle chat only from specific channel:
            
            >>> @client.on("chatmsg", channel="lounge")
            ... async def on_lounge_chat(event: ChatMessageEvent):
            ...     print(f"Lounge: {event.message}")
        """
        ...
    
    async def run(self) -> None:
        """Start event processing loop (runs until stop() called).
        
        This method blocks and processes events indefinitely. Call stop()
        from another task or signal handler to exit gracefully.
        """
        ...
    
    async def stop(self) -> None:
        """Request graceful shutdown of event processing loop."""
        ...
    
    # Command Publishing - Chat
    
    async def send_chat(
        self,
        channel: str,
        message: str,
        *,
        domain: Optional[str] = None
    ) -> str:
        """Send chat message to channel.
        
        Args:
            channel: Channel name
            message: Message text
            domain: Optional domain (uses first configured if None)
        
        Returns:
            Correlation ID for tracking
        
        Examples:
            >>> correlation_id = await client.send_chat("lounge", "Hello!")
        """
        ...
    
    async def send_pm(
        self,
        channel: str,
        username: str,
        message: str,
        *,
        domain: Optional[str] = None
    ) -> str:
        """Send private message to user.
        
        Args:
            channel: Channel name
            username: Target username
            message: Message text
            domain: Optional domain
        
        Returns:
            Correlation ID
        """
        ...
    
    # Command Publishing - Playlist
    
    async def add_media(
        self,
        channel: str,
        media_type: str,
        media_id: str,
        *,
        position: str = "end",
        domain: Optional[str] = None
    ) -> str:
        """Add media to playlist.
        
        Args:
            channel: Channel name
            media_type: Media type (e.g., "yt", "vm", "dm")
            media_id: Media ID (YouTube video ID, etc.)
            position: "end" or "next"
            domain: Optional domain
        
        Returns:
            Correlation ID
        
        Examples:
            >>> await client.add_media("lounge", "yt", "dQw4w9WgXcQ")
        """
        ...
    
    async def delete_media(
        self,
        channel: str,
        uid: int,
        *,
        domain: Optional[str] = None
    ) -> str:
        """Delete media from playlist.
        
        Args:
            channel: Channel name
            uid: Playlist item unique ID
            domain: Optional domain
        
        Returns:
            Correlation ID
        """
        ...
    
    async def move_media(
        self,
        channel: str,
        uid: int,
        position: int,
        *,
        domain: Optional[str] = None
    ) -> str:
        """Move media to new position in playlist."""
        ...
    
    async def jump_to(
        self,
        channel: str,
        uid: int,
        *,
        domain: Optional[str] = None
    ) -> str:
        """Jump to specific media in playlist."""
        ...
    
    async def clear_playlist(
        self,
        channel: str,
        *,
        domain: Optional[str] = None
    ) -> str:
        """Clear entire playlist."""
        ...
    
    async def shuffle_playlist(
        self,
        channel: str,
        *,
        domain: Optional[str] = None
    ) -> str:
        """Shuffle playlist order."""
        ...
    
    async def set_temp(
        self,
        channel: str,
        uid: int,
        is_temp: bool = True,
        *,
        domain: Optional[str] = None
    ) -> str:
        """Set temporary flag on playlist item."""
        ...
    
    # Command Publishing - Playback
    
    async def pause(
        self,
        channel: str,
        *,
        domain: Optional[str] = None
    ) -> str:
        """Pause current media."""
        ...
    
    async def play(
        self,
        channel: str,
        *,
        domain: Optional[str] = None
    ) -> str:
        """Resume playback."""
        ...
    
    async def seek(
        self,
        channel: str,
        time_seconds: float,
        *,
        domain: Optional[str] = None
    ) -> str:
        """Seek to specific time in current media."""
        ...
    
    # Command Publishing - Moderation
    
    async def kick_user(
        self,
        channel: str,
        username: str,
        reason: Optional[str] = None,
        *,
        domain: Optional[str] = None
    ) -> str:
        """Kick user from channel."""
        ...
    
    async def ban_user(
        self,
        channel: str,
        username: str,
        reason: Optional[str] = None,
        *,
        domain: Optional[str] = None
    ) -> str:
        """Ban user from channel."""
        ...
    
    async def voteskip(
        self,
        channel: str,
        *,
        domain: Optional[str] = None
    ) -> str:
        """Vote to skip current media."""
        ...
    
    # Status & Health
    
    def health(self) -> HealthStatus:
        """Get current health status and metrics.
        
        Returns:
            HealthStatus model with connection state and statistics
        """
        ...
    
    @property
    def is_connected(self) -> bool:
        """Check if NATS connection is active."""
        ...
    
    @property
    def channels(self) -> List[ChannelInfo]:
        """Get list of configured channels."""
        ...
```

### Configuration Models

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any


class NatsConfig(BaseModel):
    """NATS connection configuration."""
    
    servers: List[str] = Field(
        ...,
        description="List of NATS server URLs (e.g., ['nats://localhost:4222'])"
    )
    user: Optional[str] = Field(None, description="NATS username for authentication")
    password: Optional[str] = Field(None, description="NATS password")
    token: Optional[str] = Field(None, description="NATS token for authentication")
    tls_cert: Optional[str] = Field(None, description="Path to TLS client certificate")
    tls_key: Optional[str] = Field(None, description="Path to TLS client key")
    tls_ca: Optional[str] = Field(None, description="Path to TLS CA certificate")
    connect_timeout: int = Field(10, description="Connection timeout in seconds", ge=1)
    reconnect_time_wait: int = Field(2, description="Seconds between reconnection attempts", ge=1)
    max_reconnect_attempts: int = Field(-1, description="Max reconnect attempts (-1 = infinite)")
    ping_interval: int = Field(120, description="Ping interval in seconds", ge=1)
    max_pending_size: int = Field(65536, description="Max pending bytes", ge=1024)
    
    @field_validator("servers")
    @classmethod
    def validate_servers(cls, v: List[str]) -> List[str]:
        """Ensure at least one server is provided."""
        if not v:
            raise ValueError("At least one NATS server must be configured")
        return v


class ChannelConfig(BaseModel):
    """CyTube channel configuration."""
    
    domain: str = Field(..., description="CyTube server domain (e.g., 'cytu.be')")
    channel: str = Field(..., description="Channel name (e.g., 'lounge')")
    
    @field_validator("domain", "channel")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure domain and channel are not empty."""
        if not v or not v.strip():
            raise ValueError("Domain and channel must not be empty")
        return v.strip()


class KrytenConfig(BaseModel):
    """Complete Kryten client configuration."""
    
    nats: NatsConfig = Field(..., description="NATS connection settings")
    channels: List[ChannelConfig] = Field(
        ...,
        description="List of CyTube channels to connect to"
    )
    retry_attempts: int = Field(3, description="Command retry attempts", ge=0, le=10)
    retry_delay: float = Field(1.0, description="Initial retry delay in seconds", ge=0.1)
    handler_timeout: float = Field(30.0, description="Max handler execution time", ge=1.0)
    max_concurrent_handlers: int = Field(1000, description="Max concurrent handlers", ge=1)
    log_level: str = Field("INFO", description="Logging level")
    
    @field_validator("channels")
    @classmethod
    def validate_channels(cls, v: List[ChannelConfig]) -> List[ChannelConfig]:
        """Ensure at least one channel is configured."""
        if not v:
            raise ValueError("At least one channel must be configured")
        return v
    
    @classmethod
    def from_json(cls, path: str) -> "KrytenConfig":
        """Load configuration from JSON file with environment variable substitution."""
        ...
    
    @classmethod
    def from_yaml(cls, path: str) -> "KrytenConfig":
        """Load configuration from YAML file with environment variable substitution."""
        ...
```

### Event Models

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict, Optional


class RawEvent(BaseModel):
    """Raw CyTube event with metadata."""
    
    event_name: str = Field(..., description="Socket.IO event name")
    payload: Dict[str, Any] = Field(..., description="Raw event data")
    channel: str = Field(..., description="Channel name")
    domain: str = Field(..., description="CyTube domain")
    timestamp: datetime = Field(..., description="UTC timestamp")
    correlation_id: str = Field(..., description="UUID for tracing")


class ChatMessageEvent(BaseModel):
    """Chat message event."""
    
    username: str = Field(..., description="Username of sender")
    message: str = Field(..., description="Chat message text")
    timestamp: datetime = Field(..., description="Message timestamp")
    rank: int = Field(..., description="User rank (0=guest, 1=member, etc.)")
    channel: str = Field(..., description="Channel name")
    domain: str = Field(..., description="Domain name")
    correlation_id: str = Field(..., description="Trace ID")


class UserJoinEvent(BaseModel):
    """User joined channel event."""
    
    username: str
    rank: int
    timestamp: datetime
    channel: str
    domain: str
    correlation_id: str


class UserLeaveEvent(BaseModel):
    """User left channel event."""
    
    username: str
    timestamp: datetime
    channel: str
    domain: str
    correlation_id: str


class ChangeMediaEvent(BaseModel):
    """Media changed event."""
    
    media_type: str = Field(..., description="Media type (yt, vm, dm, etc.)")
    media_id: str = Field(..., description="Media ID")
    title: str = Field(..., description="Media title")
    duration: int = Field(..., description="Duration in seconds")
    uid: int = Field(..., description="Playlist item UID")
    timestamp: datetime
    channel: str
    domain: str
    correlation_id: str


class PlaylistUpdateEvent(BaseModel):
    """Playlist updated event."""
    
    action: str = Field(..., description="Action: add, delete, move, clear")
    uid: Optional[int] = Field(None, description="Item UID if applicable")
    timestamp: datetime
    channel: str
    domain: str
    correlation_id: str


# Additional event models for: pm, usercount, login, rank, voteskip, etc.
```

### Health & Status Models

```python
from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime


class HealthStatus(BaseModel):
    """Client health status and metrics."""
    
    connected: bool = Field(..., description="Whether NATS is connected")
    state: str = Field(..., description="Connection state: connected, connecting, disconnected, error")
    uptime_seconds: float = Field(..., description="Seconds since connection established")
    channels: List[str] = Field(..., description="List of connected channels")
    events_received: int = Field(..., description="Total events received")
    commands_sent: int = Field(..., description="Total commands sent")
    errors: int = Field(..., description="Total errors encountered")
    avg_event_latency_ms: float = Field(..., description="Average event processing time")
    last_event_time: Optional[datetime] = Field(None, description="Timestamp of last event")
    handlers_registered: int = Field(..., description="Number of event handlers")


class ChannelInfo(BaseModel):
    """Information about connected channel."""
    
    domain: str
    channel: str
    subscribed: bool = Field(..., description="Whether actively subscribed")
    events_received: int = Field(..., description="Events from this channel")
```

### Exception Hierarchy

```python
class KrytenError(Exception):
    """Base exception for all Kryten library errors."""
    pass


class ConnectionError(KrytenError):
    """NATS connection failed or lost."""
    pass


class ValidationError(KrytenError):
    """Invalid configuration or data."""
    pass


class TimeoutError(KrytenError):
    """Operation timed out."""
    pass


class PublishError(KrytenError):
    """Failed to publish command to NATS."""
    pass


class HandlerError(KrytenError):
    """Event handler raised unhandled exception."""
    pass
```

## 5. Acceptance Criteria

### Client Initialization

- **AC-001**: Given valid configuration dict, When KrytenClient is instantiated, Then client initializes without error
- **AC-002**: Given invalid configuration (missing servers), When KrytenClient is instantiated, Then ValidationError is raised with clear message
- **AC-003**: Given KrytenConfig model, When passed to KrytenClient, Then configuration is accepted

### Connection Management

- **AC-004**: Given client is initialized, When connect() is called, Then NATS connection is established within timeout
- **AC-005**: Given NATS server is unreachable, When connect() is called, Then ConnectionError is raised after retries
- **AC-006**: Given client is connected, When disconnect() is called, Then connection closes gracefully and pending messages are drained
- **AC-007**: Given client is used as async context manager, When entering context, Then connect() is called automatically
- **AC-008**: Given client is used as async context manager, When exiting context, Then disconnect() is called automatically

### Event Subscription

- **AC-009**: Given handler decorated with @client.on("chatmsg"), When chat event is received, Then handler is invoked with ChatMessageEvent
- **AC-010**: Given multiple handlers for same event, When event is received, Then all handlers execute concurrently
- **AC-011**: Given handler for specific channel, When event from different channel arrives, Then handler is NOT invoked
- **AC-012**: Given handler raises exception, When event is processed, Then exception is logged but other handlers continue
- **AC-013**: Given client is reconnected, When connection is restored, Then all handlers are resubscribed automatically

### Command Publishing

- **AC-014**: Given client is connected, When send_chat() is called, Then message is published to cytube.commands.{channel}.chat
- **AC-015**: Given invalid channel name, When command is published, Then ValidationError is raised before publishing
- **AC-016**: Given NATS publish fails, When command is sent, Then PublishError is raised after retries
- **AC-017**: Given command is published, When successful, Then correlation ID is returned
- **AC-018**: Given all command methods (playlist, playback, moderation), When called, Then correct NATS subjects and payloads are used

### Health Monitoring

- **AC-019**: Given client is connected, When health() is called, Then HealthStatus shows connected=True and valid metrics
- **AC-020**: Given client is disconnected, When health() is called, Then HealthStatus shows connected=False
- **AC-021**: Given events are processed, When health() is called, Then events_received counter is incremented
- **AC-022**: Given commands are sent, When health() is called, Then commands_sent counter is incremented

### Error Handling

- **AC-023**: Given NATS connection drops, When client is running, Then automatic reconnection is attempted with exponential backoff
- **AC-024**: Given invalid event payload (malformed JSON), When event is received, Then error is logged and event is skipped
- **AC-025**: Given handler exceeds timeout, When event is processed, Then handler is cancelled and TimeoutError is logged
- **AC-026**: Given exception occurs in handler, When handler executes, Then HandlerError is logged with correlation ID

### Configuration Loading

- **AC-027**: Given valid JSON config file, When KrytenConfig.from_json() is called, Then configuration is loaded successfully
- **AC-028**: Given config with environment variables (${VAR}), When loaded, Then variables are substituted with values
- **AC-029**: Given invalid config file, When loading, Then ValidationError is raised with specific field errors

### Testing Support

- **AC-030**: Given MockKrytenClient, When used in tests, Then commands are recorded without NATS connection
- **AC-031**: Given MockKrytenClient, When simulate_event() is called, Then registered handlers are invoked
- **AC-032**: Given MockKrytenClient, When get_published_commands() is called, Then list of commands with payloads is returned

## 6. Test Automation Strategy

### Test Levels

- **Unit Tests**: Test individual components (subject builder, serialization, validation) in isolation
- **Integration Tests**: Test client with real NATS server (using Docker container)
- **End-to-End Tests**: Test full workflow with Kryten bridge and CyTube (manual or CI with fixtures)
- **Mock Tests**: Test applications using MockKrytenClient without external dependencies

### Testing Frameworks

- **pytest**: Primary testing framework with async support (pytest-asyncio)
- **pytest-cov**: Code coverage measurement and reporting
- **pytest-mock**: Mocking utilities for dependencies
- **testcontainers**: Docker container management for NATS in integration tests

### Test Data Management

- Use factory functions to generate valid test events and commands
- Provide fixture files with realistic CyTube event payloads
- Generate synthetic event streams for load testing
- Use property-based testing (Hypothesis) for edge cases

### CI/CD Integration

- Run unit tests on every commit (GitHub Actions)
- Run integration tests on pull requests (with NATS container)
- Measure code coverage and enforce 80% minimum
- Run linting (ruff, mypy) and formatting (black) checks
- Publish test results and coverage reports

### Coverage Requirements

- **Minimum 80% overall code coverage**
- **100% coverage for public API methods** (KrytenClient interface)
- **90% coverage for critical paths** (connection, publishing, error handling)
- **Exception paths must be tested** (network failures, invalid data)

### Performance Testing

- Measure event throughput (events/second) under load
- Test concurrent handler execution with 100+ simultaneous events
- Verify memory stability over 24-hour run (no leaks)
- Test reconnection behavior under network instability

### Testing Examples

```python
import pytest
from kryten import KrytenClient, MockKrytenClient, ChatMessageEvent


@pytest.fixture
def config():
    """Test configuration."""
    return {
        "nats": {"servers": ["nats://localhost:4222"]},
        "channels": [{"domain": "cytu.be", "channel": "test"}]
    }


@pytest.mark.asyncio
async def test_send_chat_publishes_to_nats(config):
    """Test that send_chat publishes to correct NATS subject."""
    client = MockKrytenClient(config)
    
    async with client:
        correlation_id = await client.send_chat("test", "Hello!")
        
        # Verify command was published
        commands = client.get_published_commands()
        assert len(commands) == 1
        assert commands[0]["subject"] == "cytube.commands.test.chat"
        assert commands[0]["data"]["message"] == "Hello!"
        assert commands[0]["correlation_id"] == correlation_id


@pytest.mark.asyncio
async def test_event_handler_receives_event(config):
    """Test that decorated handler receives events."""
    client = MockKrytenClient(config)
    received_events = []
    
    @client.on("chatmsg")
    async def handle_chat(event: ChatMessageEvent):
        received_events.append(event)
    
    async with client:
        # Simulate receiving event
        await client.simulate_event("chatmsg", {
            "username": "alice",
            "message": "Hello!",
            "timestamp": "2024-01-15T10:30:00Z",
            "rank": 1
        })
        
        # Give handlers time to execute
        await asyncio.sleep(0.1)
        
        assert len(received_events) == 1
        assert received_events[0].username == "alice"
        assert received_events[0].message == "Hello!"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_real_nats_connection():
    """Integration test with real NATS server (requires Docker)."""
    # Uses testcontainers to spin up NATS
    with NatsContainer() as nats:
        config = {
            "nats": {"servers": [nats.get_connection_url()]},
            "channels": [{"domain": "test.local", "channel": "test"}]
        }
        
        client = KrytenClient(config)
        async with client:
            assert client.is_connected
            correlation_id = await client.send_chat("test", "Integration test")
            assert correlation_id
```

## 7. Rationale & Context

### Design Decisions

#### Async-First API

**Decision**: Library provides only async/await interface, no synchronous wrapper.

**Rationale**: 
- Modern Python applications use asyncio for I/O-bound operations
- NATS client (nats-py) is async-native
- Sync wrapper adds complexity and maintenance burden
- Forces developers to write scalable, non-blocking code
- Simplifies implementation (no threading, no blocking calls)

**Alternative Considered**: Provide both sync and async APIs like `requests` vs `httpx`. Rejected due to doubled API surface and limited use case for blocking operations in microservices.

#### Decorator-Based Event Handlers

**Decision**: Use `@client.on("event_name")` decorator pattern for handler registration.

**Rationale**:
- Familiar pattern from web frameworks (Flask, FastAPI)
- Clear, declarative syntax showing intent
- Enables handler registration before connection
- Supports multiple handlers per event naturally
- Easy to test (handlers are just async functions)

**Alternative Considered**: Callback registration via `client.add_handler("event", callback)`. Rejected as less Pythonic and requires manual tracking of handler references.

#### Pydantic for Data Validation

**Decision**: Use Pydantic models for all configuration, events, and commands.

**Rationale**:
- Type safety with runtime validation
- Automatic JSON serialization/deserialization
- Clear schema documentation through models
- IDE autocomplete support
- Validation error messages are descriptive
- Widely adopted in Python ecosystem (FastAPI, etc.)

**Alternative Considered**: Use dataclasses or plain dicts. Rejected due to lack of validation and serialization capabilities.

#### Correlation IDs for Tracing

**Decision**: Generate UUID correlation IDs for all commands and preserve them through events.

**Rationale**:
- Enables distributed tracing across microservices
- Helps debug issues in production
- Standard practice in cloud-native applications
- Minimal overhead (UUID generation is fast)
- Can integrate with APM tools (OpenTelemetry, etc.)

**Alternative Considered**: No tracing IDs. Rejected due to difficulty troubleshooting distributed systems without request tracking.

#### Auto-Reconnection Logic

**Decision**: Automatically reconnect to NATS on connection loss with exponential backoff.

**Rationale**:
- Microservices must be resilient to transient failures
- Manual reconnection burden on developers is error-prone
- NATS client provides reconnection hooks natively
- Exponential backoff prevents thundering herd
- Applications should recover from network blips automatically

**Alternative Considered**: Crash on disconnect and rely on process supervisor (systemd, k8s). Rejected as too disruptive for temporary network issues.

### Event vs Command Separation

The library maintains clear separation between **events** (inbound from CyTube) and **commands** (outbound to CyTube):

- **Events** follow subject pattern: `cytube.events.{domain}.{channel}.{event_name}`
- **Commands** follow subject pattern: `cytube.commands.{channel}.{action}`

This separation enables:
- Different security policies (e.g., read-only bots can subscribe but not publish)
- Independent scaling of producers vs consumers
- Clear data flow visualization
- Simplified testing (mock events, verify commands)

### Why NATS Over Direct Socket.IO

Using NATS as intermediary instead of direct CyTube Socket.IO connections provides:

1. **Decoupling**: Microservices don't need CyTube connection details
2. **Scalability**: Multiple microservices consume same events without CyTube load
3. **Reliability**: NATS persists messages during consumer downtime (with persistence enabled)
4. **Polyglot**: Non-Python services can integrate via NATS
5. **Observability**: NATS provides monitoring, logging, tracing out-of-box
6. **Security**: Centralized authentication and TLS at NATS level

The kryten-py library abstracts this architecture, letting developers focus on business logic rather than infrastructure.

## 8. Dependencies & External Integrations

### Runtime Dependencies

#### Core Libraries

- **PLT-001**: Python 3.11 or higher - Required for TaskGroup, improved asyncio, and typing features
  - **Rationale**: Modern async patterns, better performance, structural pattern matching
  - **Constraints**: Cannot use Python 3.10 or lower

- **PLT-002**: nats-py >= 2.9.0 - Official NATS client library
  - **Purpose**: NATS connection, pub/sub, authentication
  - **Constraints**: Must support async/await, TLS, JWT auth

- **PLT-003**: Pydantic >= 2.0.0 - Data validation and serialization
  - **Purpose**: Configuration models, event models, validation
  - **Constraints**: Pydantic v2 API (not compatible with v1)

#### Optional Dependencies

- **PLT-004**: PyYAML >= 6.0 - YAML configuration file parsing
  - **Purpose**: Load config from YAML files
  - **Optional**: Only needed if using `KrytenConfig.from_yaml()`

- **PLT-005**: python-dotenv >= 1.0.0 - Environment variable loading
  - **Purpose**: Load .env files for local development
  - **Optional**: Only needed if using environment variable substitution

### Development Dependencies

- **pytest >= 7.0** - Testing framework
- **pytest-asyncio >= 0.21** - Async test support
- **pytest-cov >= 4.0** - Code coverage
- **pytest-mock >= 3.10** - Mocking utilities
- **testcontainers >= 3.7** - Docker containers for integration tests
- **black >= 23.0** - Code formatting
- **ruff >= 0.1** - Fast linting
- **mypy >= 1.0** - Type checking
- **hypothesis >= 6.0** - Property-based testing

### External Systems

#### NATS Server

- **EXT-001**: NATS Server 2.x - Message bus for event distribution
  - **Purpose**: Pub/sub messaging between Kryten bridge and microservices
  - **Requirements**: 
    - NATS core server or NATS Streaming (for persistence)
    - Network accessible from application environment
    - Sufficient resources (1 CPU, 512MB RAM minimum)
  - **SLA Requirements**: 99.9% uptime, <10ms latency
  - **Authentication**: Username/password, token, or NKey
  - **TLS**: Optional but recommended for production

#### Kryten Bridge

- **EXT-002**: Kryten Bridge Service - CyTube to NATS gateway
  - **Purpose**: Bidirectional bridge between CyTube Socket.IO and NATS
  - **Requirements**:
    - Kryten bridge deployed and connected to CyTube
    - Commands enabled in Kryten configuration (`commands.enabled = true`)
    - Event publishing enabled (`events.enabled = true`)
    - NATS connection configured in bridge
  - **SLA Requirements**: Same as CyTube availability
  - **Configuration**: Must use compatible subject patterns

#### CyTube Server

- **EXT-003**: CyTube Server - Synchronized media platform
  - **Purpose**: Target system for commands, source of events
  - **Requirements**:
    - CyTube server operational with accessible Socket.IO endpoint
    - Channel created and accessible
    - Bot account with appropriate permissions (for commands)
  - **SLA Requirements**: Per CyTube instance SLA
  - **Constraints**: Rate limits may apply to commands

### Infrastructure Dependencies

#### Container Runtime (Optional)

- **INF-001**: Docker or Podman - Container runtime for integration tests
  - **Purpose**: Run NATS server in testcontainers
  - **Optional**: Only required for integration tests
  - **Requirements**: Docker 20.x+ or Podman 3.x+

#### Python Environment

- **INF-002**: Python Virtual Environment - Isolated Python installation
  - **Purpose**: Dependency isolation for development and deployment
  - **Recommended**: venv, virtualenv, conda, or Poetry

### Compliance Dependencies

- **COM-001**: Python Package Index (PyPI) - Package distribution
  - **Purpose**: Library installation via pip
  - **Requirements**: Package metadata follows PEP 621
  - **Constraints**: Must not have dependency conflicts with common packages

- **COM-002**: Semantic Versioning 2.0 - Versioning scheme
  - **Purpose**: Clear version communication for breaking changes
  - **Requirements**: MAJOR.MINOR.PATCH format
  - **Guidelines**: Bump MAJOR for breaking changes, MINOR for features, PATCH for fixes

## 9. Examples & Edge Cases

### Basic Example: Simple Chat Bot

```python
import asyncio
from kryten import KrytenClient, ChatMessageEvent


async def main():
    """Simple echo bot that repeats user messages."""
    
    config = {
        "nats": {
            "servers": ["nats://localhost:4222"],
            "user": "kryten",
            "password": "secret"
        },
        "channels": [
            {"domain": "cytu.be", "channel": "lounge"}
        ]
    }
    
    async with KrytenClient(config) as client:
        @client.on("chatmsg")
        async def on_chat(event: ChatMessageEvent):
            """Echo user messages."""
            if event.username != "MyBot":  # Don't echo ourselves
                await client.send_chat(
                    event.channel,
                    f"{event.username} said: {event.message}"
                )
        
        print("Echo bot started!")
        await client.run()  # Run until Ctrl+C


if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Example: DJ Bot with Playlist Management

```python
import asyncio
from kryten import KrytenClient, ChatMessageEvent, ChangeMediaEvent, PlaylistUpdateEvent


class DJBot:
    """Automated DJ that manages playlist and responds to commands."""
    
    def __init__(self, config):
        self.client = KrytenClient(config)
        self.playlist_queue = []
        self.auto_dj_enabled = True
        
        # Register handlers
        self.client.on("chatmsg")(self.handle_chat)
        self.client.on("changemedia")(self.handle_media_change)
        self.client.on("playlist")(self.handle_playlist_update)
    
    async def handle_chat(self, event: ChatMessageEvent):
        """Handle chat commands."""
        msg = event.message.strip().lower()
        
        if msg == "!autodj on":
            self.auto_dj_enabled = True
            await self.client.send_chat(event.channel, "Auto-DJ enabled!")
        
        elif msg == "!autodj off":
            self.auto_dj_enabled = False
            await self.client.send_chat(event.channel, "Auto-DJ disabled!")
        
        elif msg.startswith("!queue "):
            # Add video to queue
            video_id = msg[7:].strip()
            self.playlist_queue.append(video_id)
            await self.client.send_chat(
                event.channel,
                f"Added to queue (position {len(self.playlist_queue)})"
            )
    
    async def handle_media_change(self, event: ChangeMediaEvent):
        """Handle media changes."""
        print(f"Now playing: {event.title} ({event.duration}s)")
        
        # Check if playlist is getting short
        if self.auto_dj_enabled:
            # In real implementation, would check actual playlist length
            await self.add_from_queue(event.channel)
    
    async def handle_playlist_update(self, event: PlaylistUpdateEvent):
        """Handle playlist updates."""
        if event.action == "clear":
            print("Playlist cleared!")
            await self.refill_playlist(event.channel)
    
    async def add_from_queue(self, channel: str):
        """Add next video from queue."""
        if self.playlist_queue:
            video_id = self.playlist_queue.pop(0)
            await self.client.add_media(channel, "yt", video_id, position="end")
            print(f"Added queued video: {video_id}")
    
    async def refill_playlist(self, channel: str):
        """Refill playlist with queued videos."""
        for video_id in self.playlist_queue[:5]:  # Add up to 5
            await self.client.add_media(channel, "yt", video_id)
        self.playlist_queue = self.playlist_queue[5:]
    
    async def run(self):
        """Start the bot."""
        async with self.client:
            print("DJ Bot started!")
            await self.client.run()


if __name__ == "__main__":
    config = {
        "nats": {"servers": ["nats://localhost:4222"]},
        "channels": [{"domain": "cytu.be", "channel": "music"}]
    }
    
    bot = DJBot(config)
    asyncio.run(bot.run())
```

### Edge Case: Multi-Channel Bot with Channel-Specific Handlers

```python
import asyncio
from kryten import KrytenClient, ChatMessageEvent


async def main():
    """Bot that operates on multiple channels with different behaviors."""
    
    config = {
        "nats": {"servers": ["nats://localhost:4222"]},
        "channels": [
            {"domain": "cytu.be", "channel": "lounge"},
            {"domain": "cytu.be", "channel": "movies"},
            {"domain": "test.cytube.local", "channel": "testing"}
        ]
    }
    
    async with KrytenClient(config) as client:
        # Global handler for all channels
        @client.on("chatmsg")
        async def global_chat(event: ChatMessageEvent):
            """Log all chat messages."""
            print(f"[{event.channel}] {event.username}: {event.message}")
        
        # Channel-specific handler for lounge
        @client.on("chatmsg", channel="lounge")
        async def lounge_only(event: ChatMessageEvent):
            """Respond only in lounge."""
            if "hello" in event.message.lower():
                await client.send_chat(event.channel, f"Hi {event.username}!")
        
        # Domain-specific handler
        @client.on("chatmsg", domain="test.cytube.local")
        async def test_domain_only(event: ChatMessageEvent):
            """Special handling for test domain."""
            await client.send_chat(event.channel, "[TEST MODE] Message received")
        
        await client.run()


if __name__ == "__main__":
    asyncio.run(main())
```

### Edge Case: Error Handling and Reconnection

```python
import asyncio
import logging
from kryten import KrytenClient, ChatMessageEvent, ConnectionError, HandlerError


logging.basicConfig(level=logging.INFO)


async def main():
    """Bot with comprehensive error handling."""
    
    config = {
        "nats": {
            "servers": [
                "nats://primary:4222",
                "nats://backup:4222"  # Fallback server
            ],
            "max_reconnect_attempts": -1,  # Infinite retries
            "reconnect_time_wait": 5
        },
        "channels": [{"domain": "cytu.be", "channel": "lounge"}],
        "retry_attempts": 3,
        "handler_timeout": 10.0
    }
    
    client = KrytenClient(config)
    
    @client.on("chatmsg")
    async def risky_handler(event: ChatMessageEvent):
        """Handler that might fail."""
        try:
            # Simulate external API call that might fail
            await asyncio.sleep(0.5)
            if "error" in event.message.lower():
                raise ValueError("Simulated error in handler")
            
            await client.send_chat(event.channel, "Message processed!")
        
        except Exception as e:
            # Handler exceptions are caught by client, but we can log locally
            logging.error(f"Handler error: {e}", exc_info=True)
    
    # Try to connect with retries
    max_connection_attempts = 5
    for attempt in range(max_connection_attempts):
        try:
            await client.connect()
            break
        except ConnectionError as e:
            logging.error(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_connection_attempts - 1:
                await asyncio.sleep(5)
            else:
                raise
    
    try:
        # Monitor health while running
        health_task = asyncio.create_task(monitor_health(client))
        run_task = asyncio.create_task(client.run())
        
        # Wait for either task to complete
        done, pending = await asyncio.wait(
            [health_task, run_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel remaining tasks
        for task in pending:
            task.cancel()
    
    finally:
        await client.disconnect()
        logging.info("Bot shut down gracefully")


async def monitor_health(client: KrytenClient):
    """Periodically check client health."""
    while True:
        await asyncio.sleep(30)
        health = client.health()
        
        logging.info(
            f"Health: connected={health.connected}, "
            f"events={health.events_received}, "
            f"commands={health.commands_sent}, "
            f"errors={health.errors}"
        )
        
        if not health.connected:
            logging.warning("Client is disconnected! Waiting for reconnection...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Received Ctrl+C, shutting down...")
```

### Edge Case: Testing with MockKrytenClient

```python
import pytest
from kryten import MockKrytenClient, ChatMessageEvent


@pytest.mark.asyncio
async def test_bot_command_parsing():
    """Test bot command parsing without real NATS."""
    
    config = {
        "nats": {"servers": ["nats://localhost:4222"]},
        "channels": [{"domain": "test.local", "channel": "test"}]
    }
    
    client = MockKrytenClient(config)
    responses = []
    
    @client.on("chatmsg")
    async def handle_command(event: ChatMessageEvent):
        """Parse and respond to commands."""
        if event.message.startswith("!ping"):
            await client.send_chat(event.channel, "Pong!")
            responses.append("pong")
        elif event.message.startswith("!hello"):
            await client.send_chat(event.channel, f"Hi {event.username}!")
            responses.append("hello")
    
    async with client:
        # Simulate user commands
        await client.simulate_event("chatmsg", {
            "username": "alice",
            "message": "!ping",
            "timestamp": "2024-01-15T10:00:00Z",
            "rank": 1
        })
        
        await client.simulate_event("chatmsg", {
            "username": "bob",
            "message": "!hello",
            "timestamp": "2024-01-15T10:01:00Z",
            "rank": 1
        })
        
        # Give handlers time to run
        await asyncio.sleep(0.1)
    
    # Verify responses
    assert "pong" in responses
    assert "hello" in responses
    
    # Verify commands were sent
    commands = client.get_published_commands()
    assert len(commands) == 2
    assert commands[0]["data"]["message"] == "Pong!"
    assert commands[1]["data"]["message"] == "Hi bob!"
```

## 10. Validation Criteria

The kryten-py library implementation must satisfy the following validation criteria before release:

### Functional Validation

- **VAL-001**: All 18+ command methods (chat, playlist, playback, moderation) publish to correct NATS subjects
- **VAL-002**: Event handlers registered with `@client.on()` receive events matching their filters
- **VAL-003**: Client successfully connects to NATS with all supported authentication methods (user/pass, token, NKey, TLS)
- **VAL-004**: Client automatically reconnects after connection loss and resubscribes to all handlers
- **VAL-005**: Configuration validation catches all invalid configurations and provides clear error messages
- **VAL-006**: Health status accurately reflects connection state, metrics, and handler counts

### Non-Functional Validation

- **VAL-007**: Event throughput exceeds 1000 events/sec per channel under load testing
- **VAL-008**: Memory usage remains stable (no leaks) during 24-hour continuous operation
- **VAL-009**: Command publishing latency is <100ms for 99th percentile under normal conditions
- **VAL-010**: Reconnection completes within 30 seconds after transient network failure

### Code Quality Validation

- **VAL-011**: Test coverage is ≥80% overall, 100% for public API methods
- **VAL-012**: All public APIs have docstrings with examples and type hints
- **VAL-013**: Code passes linting (ruff) and type checking (mypy) with zero errors
- **VAL-014**: Code follows PEP 8 style guide and Black formatting

### Integration Validation

- **VAL-015**: Library works with real NATS server in integration tests
- **VAL-016**: Library successfully interacts with Kryten bridge in end-to-end tests
- **VAL-017**: MockKrytenClient accurately simulates real client behavior for testing
- **VAL-018**: Example code in documentation runs without errors

### Documentation Validation

- **VAL-019**: README includes quick start guide, installation instructions, and basic examples
- **VAL-020**: API reference documentation is generated from docstrings (Sphinx/MkDocs)
- **VAL-021**: Migration guide is provided for upgrading between major versions
- **VAL-022**: Troubleshooting guide covers common issues and solutions

### Acceptance Testing Checklist

Run the following manual acceptance tests before release:

1. **Install and Import**: `pip install kryten-py && python -c "from kryten import KrytenClient"`
2. **Configuration Loading**: Load config from JSON, YAML, and dict successfully
3. **Connection**: Connect to NATS with user/pass, token, and verify connection
4. **Event Handling**: Register handler, simulate event, verify handler is called
5. **Command Publishing**: Send chat message, verify NATS message is published
6. **Reconnection**: Kill NATS server, verify client reconnects when restarted
7. **Error Handling**: Send invalid command, verify ValidationError is raised
8. **Health Monitoring**: Call `health()`, verify metrics are accurate
9. **Graceful Shutdown**: Call `disconnect()`, verify clean shutdown without errors
10. **Mock Testing**: Use MockKrytenClient in test, verify commands are captured

All criteria must be met before tagging a release.

## 11. Related Specifications / Further Reading

### Internal Specifications

- **LLM Chat Bot Specifications** (in same repository):
  - `requirements.md` - High-level requirements for LLM Chat Bot using kryten-py
  - `spec-architecture-design.md` - Architecture showing kryten-py integration
  - `spec-data-contracts.md` - Event schemas for CyTube events
  - `spec-configuration.md` - YAML configuration patterns
  - `spec-observability.md` - Logging and metrics for microservices

### External References

#### NATS Documentation
- [NATS Documentation](https://docs.nats.io/) - Official NATS docs
- [NATS Python Client](https://github.com/nats-io/nats.py) - nats-py library
- [NATS Subject-Based Messaging](https://docs.nats.io/nats-concepts/subjects) - Subject patterns and wildcards
- [NATS Security](https://docs.nats.io/running-a-nats-service/configuration/securing_nats) - Authentication and TLS

#### Python & Async
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html) - Official asyncio guide
- [PEP 492 - Coroutines with async and await syntax](https://www.python.org/dev/peps/pep-0492/)
- [Real Python asyncio Tutorial](https://realpython.com/async-io-python/)

#### Pydantic
- [Pydantic Documentation](https://docs.pydantic.dev/) - Data validation library
- [Pydantic Settings Management](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Config from env vars

#### CyTube
- [CyTube GitHub](https://github.com/calzoneman/sync) - CyTube server source
- [CyTube API Documentation](https://github.com/calzoneman/sync/blob/3.0/docs/socket.io.md) - Socket.IO events

#### Testing
- [pytest Documentation](https://docs.pytest.org/) - Testing framework
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/) - Async test support
- [testcontainers-python](https://testcontainers-python.readthedocs.io/) - Docker containers for tests

#### Distributed Tracing
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/) - Observability framework
- [Correlation IDs Best Practices](https://hilton.org.uk/blog/microservices-correlation-id) - Distributed tracing patterns

### Implementation Guides

- **Kryten CLI Source Code** - Reference implementation showing NATS interaction patterns
- **Kryten Bridge Documentation** - Details on bridge configuration and message formats
- **Sprint Task Documentation** - 96-task breakdown for LLM Chat Bot implementation using kryten-py

---

**Version History**:
- 1.0 (2025-01-26): Initial specification created based on Kryten CLI reference implementation and LLM Chat Bot requirements

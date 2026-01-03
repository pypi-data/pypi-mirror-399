# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.11.2] - 2025-12-31

### Fixed
- **Type Safety**: Resolved all `mypy` strict mode errors across the codebase.
  - Renamed `__nats` to `_nats` in `KrytenClient` for better internal access control.
  - Fixed callback signatures for `subscribe_request_reply`.
  - Added safe type casts for JSON deserialization.
  - Fixed private attribute access in tests.
- **Examples**: Fixed type errors in `lifecycle_and_kv_example.py`.

## [0.11.1] - 2025-12-31

### Fixed
- **CI**: Fixed formatting issues (`black`) and updated CI configuration to include `pydantic.mypy` plugin.
- **Linting**: Resolved formatting discrepancies in multiple files.

## [0.11.0] - 2025-12-31

### Changed
- **Release**: Minor version bump for coordinated ecosystem release.

## [0.10.6] - 2025-12-31

### Fixed
- **Linting**: Resolved various Ruff and Pylint errors (import sorting, whitespace, line length).
- **Tests**: Fixed `pytest.raises(Exception)` anti-pattern in `test_models.py` (switched to specific exceptions).
- **Examples**: Fixed undefined variables (`kv`, `kv_put`) in `examples/lifecycle_and_kv_example.py` by using `client.kv_put`.
- **Mock Client**: 
  - Renamed `send_command_v2` to `send_command` in `MockKrytenClient` to match `KrytenClient` interface.
  - Aligned `send_command` arguments with `KrytenClient` (type, body, domain, channel).
  - Fixed null channel access in `send_command` by using first configured channel if None.

## [0.10.5] - 2025-12-28

### Changed
- **Logging**: Improved NATS connection logging to include the list of configured servers.

## [0.10.4] - 2025-12-28

### Refactored
- **Command Sending Architecture**: Replaced legacy `_send_command` with private `__send_command`.
  - Enforces strict encapsulation of command sending logic.
  - Returns `request_id` (UUID) for command tracking.
  - Updates all dependent methods (`send_chat`, `send_pm`, `add_media`, etc.) to use the new private method.
  - Ensures consistent subject building via `build_command_subject`.

## [0.10.3] - 2025-12-28

### Fixed
- Fixed `AttributeError: 'KrytenClient' object has no attribute '_nats'` by updating internal references to use private `__nats` attribute.

## [0.10.2] - 2025-12-26

### Fixed
- Added `send_command` method to `MockKrytenClient` to match `KrytenClient` interface.

## [0.10.1] - Unreleased

### Added

- **Service Discovery Endpoints**: `LifecycleEventPublisher.set_endpoints()` method
  - Allows services to register health and metrics endpoints
  - Endpoint info included in startup and heartbeat events
  - Enables `kryten system services` command to show service URLs

- **Get Services API**: `KrytenClient.get_services()` method
  - Query registered microservices from kryten-robot
  - Returns service info including version, hostname, endpoints, heartbeat status

### Fixed

- **Custom Metadata in Payloads**: `_build_base_payload()` now includes custom metadata
  - Previously `set_metadata()` and `update_metadata()` values weren't sent

## [0.9.7] - 2025-07-27

### Fixed

- **KV Store Config Conflict**: `get_kv_store()` no longer attempts to create buckets
  - Buckets are created by kryten-robot with specific configuration (max_value_size, etc.)
  - Creating buckets with default config caused "stream name already in use with a different configuration" errors
  - Now raises an exception with clear message if bucket doesn't exist

## [0.9.4] - 2025-12-13

### Changed

- **Sync release**: Version sync with kryten ecosystem (kryten-cli, kryten-robot, kryten-userstats)

## [0.9.3] - 2025-12-14

### Changed

- **aiohttp now required**: Made aiohttp a required dependency instead of optional
  - Fixes `ModuleNotFoundError: No module named 'aiohttp'` when installing kryten-cli via pipx
  - Removed `metrics` extra since it's no longer needed

## [0.9.0] - 2025-12-12

### Added

- **NATS Request-Reply**: New `nats_request()` method for request-reply pattern
  - Send request and wait for single response
  - Configurable timeout (default 5.0s)
  - Auto-encodes dict payloads to JSON
  - Returns parsed JSON response

- **Request-Reply Subscriptions**: New `subscribe_request_reply()` method
  - Subscribe to subjects expecting request-reply pattern
  - Handler receives parsed request, returns response dict
  - Auto-encodes response as JSON

### Fixed

- **MetricsServer Graceful Shutdown**: Fixed `stop()` method to properly handle None state
  - Check for None runner/site before cleanup
  - Prevents AttributeError on early shutdown

## [0.8.1] - 2025-12-10

### Fixed

- **aiohttp Dependency**: Added aiohttp as optional dependency for metrics server
  - Install with `pip install kryten-py[metrics]` or include aiohttp manually

## [0.8.0] - 2025-07-27

### Added

- **ServiceConfig**: New configuration model for service identity and lifecycle settings
  - `name`: Service name for lifecycle events
  - `version`: Service version string
  - `enable_lifecycle`: Auto-publish startup/shutdown events
  - `enable_heartbeat`: Publish periodic heartbeats
  - `heartbeat_interval`: Heartbeat interval in seconds (5-300s, default 30s)
  - `enable_discovery`: Respond to service discovery polls

- **Automatic Heartbeats**: When service config is provided with heartbeat enabled:
  - Background task publishes heartbeat events at configured interval
  - Heartbeats include service name, version, hostname, and uptime
  - Published to `kryten.lifecycle.{service}.heartbeat`

- **Service Discovery**: Automatic response to service discovery polls:
  - Subscribes to `kryten.service.discovery.poll`
  - Re-announces service via startup event when poll received
  - Enables runtime discovery of running services

- **Arbitrary Subject Subscriptions**: New `subscribe()` method on KrytenClient
  - Subscribe to any NATS subject with custom handler
  - Supports wildcards (`*`, `>`)
  - Returns subscription object for later unsubscription

- **Generic Publish**: New `publish()` method on KrytenClient
  - Publish to any NATS subject
  - Accepts bytes, string, or dict (auto-JSON encoded)

- **Lifecycle Integration**: KrytenClient now manages lifecycle automatically
  - Publishes startup event on `connect()`
  - Publishes shutdown event on `disconnect()`
  - `on_group_restart()` method to handle coordinated restart notices
  - `lifecycle` property exposes LifecycleEventPublisher

- **New Lifecycle Events**:
  - `publish_heartbeat()`: Manual heartbeat publication
  - Discovery poll handling with auto-announce

### Changed

- **Disconnect Method**: Now accepts optional `reason` parameter for shutdown event
- **LifecycleEventPublisher**: Enhanced constructor with new parameters
  - `heartbeat_interval`: Configure heartbeat timing
  - `enable_heartbeat`: Toggle heartbeat feature
  - `enable_discovery`: Toggle discovery response

## [0.7.0] - 2025-07-27

### Fixed

- **NATS Subject Pattern**: Fixed subscription pattern from `cytube.events.{domain}.{channel}.>` 
  to `kryten.events.cytube.{channel}.>` to match Kryten-Robot's event publishing format

## [0.5.9] - 2025-12-09

### Added

- **Version Discovery**: Added `get_version()` method to KrytenClient
  - Queries `kryten.robot.command` with `system.version` command
  - Returns semantic version string of running Kryten-Robot instance
  - Enables client applications to check server compatibility
  - Allows enforcement of minimum version requirements
  - Example usage with `packaging` library for version comparison included in docstring

## [0.5.8] - 2025-12-09

### Added

- **Channel Discovery**: Added `get_channels()` method to KrytenClient
  - Queries `kryten.robot.command` with `system.channels` to discover available channels
  - Returns list of channel info dictionaries (domain, channel, connected status)
  - Enables automatic channel discovery for CLI tools and applications
  - Supports future multi-channel deployments

## [0.5.7] - 2025-12-09

### Changed

- Version bump to trigger PyPI release after v0.5.6 release process issue
- All changes from v0.5.6 included (Python 3.10 support)

## [0.5.6] - 2025-12-09

### Changed

- **Compatibility**: Lowered minimum Python version requirement from 3.11 to 3.10
  - No Python 3.11+ specific features are used in the codebase
  - Dependencies (pydantic ≥3.9, nats-py ≥3.7) support Python 3.10
  - Updated tooling configuration (black, ruff, mypy) to target Python 3.10

## [0.5.5] - 2025-12-09

### Fixed

- **Documentation**: Added missing moderation methods to README API reference
  - `mute_user()` - Mute user from chatting (rank 2+)
  - `shadow_mute_user()` - Shadow mute user (only mods see messages, rank 2+)
  - `unmute_user()` - Remove mute/shadow mute (rank 2+)
  - `assign_leader()` - Give/remove leader status (rank 2+)
  - `play_next()` - Skip to next video immediately (rank 2+)
  - These methods have always been functional, just undocumented in the main README

## [0.5.4] - 2025-12-09

### Fixed

- **Documentation**: Removed anti-pattern of importing `nats` directly in README examples
  - All Lifecycle Events examples now use `client._nats` instead of `import nats`
  - All KeyValue Store examples now use `client.kv_*` methods instead of standalone helpers
  - Monitoring examples updated to use KrytenClient context
  - Users should never import `nats` directly - always use KrytenClient's built-in methods

## [0.4.0] - 2025-12-08

### Changed - BREAKING

- **Subject Format Redesign**: Complete overhaul of NATS subject structure for robustness
  - Changed prefix from `cytube.*` to `kryten.*` for better namespace clarity
  - Events: `kryten.events.cytube.{channel}.{event}` (was `cytube.events.{domain}.{channel}.{event}`)
  - Commands: `kryten.commands.cytube.{channel}.{action}` (was `cytube.commands.{domain}.{channel}.{action}`)
  - Domain variations (cy.tube, cytu.be, Cytu.BE) all normalize to "cytube" literal
  - Channels normalized: lowercase, dots removed, spaces to hyphens
  - **This is case-insensitive**: "420Grindhouse" and "420grindhouse" match the same subject

- **Aggressive Normalization**: New `normalize_token()` function replaces domain-specific logic
  - Removes ALL dots from domains/channels (cy.tube → cytube)
  - Lowercase everything
  - Consistent matching regardless of input variations

### Fixed

- Eliminated case-sensitivity brittleness in NATS subjects
- Domain dot variations no longer cause routing failures
- Commands now reliably reach intended channels

### Migration Required

**Kryten-Robot must be updated** to match the new subject format. Both kryten-py and Kryten-Robot subject_builder.py files must use the same logic.

## [0.3.4] - 2025-12-08

### Fixed

- **Command Subject Builder**: Fixed `build_command_subject()` to preserve dots in domain names (e.g., `cy.tube`)
  - Previously sanitized domain which removed dots, breaking commands to domains with dots
  - Now matches event subject behavior by only lowercasing domain, preserving dots
  - Fixes issue where commands to `cy.tube` were sent to `cytube` instead

## [0.3.3] - 2025-12-06

### Added

- **KrytenClient KV Store Methods**: Added high-level KeyValue store methods to KrytenClient class
  - `get_kv_bucket(bucket_name)` - Get or create a KV bucket
  - `kv_get(bucket_name, key, default, parse_json)` - Get value from KV store
  - `kv_put(bucket_name, key, value, as_json)` - Put value into KV store
  - `kv_delete(bucket_name, key)` - Delete key from KV store
  - `kv_keys(bucket_name)` - List all keys in bucket
  - `kv_get_all(bucket_name, parse_json)` - Get all key-value pairs

### Changed

- KV store operations now accessible directly through KrytenClient without needing separate NATS connection
- Microservices can now use only KrytenClient for all NATS interactions (no direct nats-py imports needed)

## [0.3.1] - 2025-12-06

### Changed

- **Documentation**: Updated README.md with comprehensive documentation for new features
  - Added "Lifecycle Events" section with usage examples and monitoring patterns
  - Added "KeyValue Store" section with basic operations, JSON serialization, and bulk operations
  - Updated feature list to highlight lifecycle events and KV store capabilities
  - Added reference to `lifecycle_and_kv_example.py` in examples section

## [0.3.0] - 2025-12-06

### Added

- **Lifecycle Events**: New `LifecycleEventPublisher` class for service lifecycle management
  - Publish startup/shutdown events
  - Publish connection/disconnection events
  - Subscribe to groupwide restart notices
  - Includes service metadata (version, hostname, uptime)
- **KeyValue Store Helpers**: New `kv_store` module with utility functions for NATS JetStream KV stores
  - `get_kv_store()`: Get or create KV bucket
  - `kv_get()`: Get value with optional JSON parsing
  - `kv_put()`: Put value with optional JSON serialization
  - `kv_delete()`: Delete key from store
  - `kv_keys()`: List all keys in store
  - `kv_get_all()`: Get all key-value pairs

### Changed
- Updated version to 0.3.0 for new feature release

## [0.2.3] - 2025-12-05

### Fixed

- **Command Subject**: Fixed NATS command subject to include domain (`cytube.commands.{domain}.{channel}.{action}`) to match Kryten bridge subscription pattern

## [0.2.2] - 2025-12-05

### Fixed
- Fixed PM command to send `message` parameter (not `msg`) to match Kryten bridge's `send_pm()` function signature

## [0.2.1] - 2025-12-05

### Fixed
- **PM Command**: Changed PM message field from `"message"` to `"msg"` to match CyTube Socket.IO expectations
- **Payload Type**: Updated `RawEvent.payload` to accept any type, not just dictionaries
- **Event Conversion**: Added type check to skip conversion for non-dict payloads

### Removed
- **NATS Config**: Removed unsupported `max_pending_size` parameter from NATS connection

## [0.2.0] - 2024-12-04

### Added
- **Typed Event Conversion**: Automatic conversion of `RawEvent` to specific typed event models
  - `ChatMessageEvent` for chat messages and PMs
  - `UserJoinEvent` for user joins
  - `UserLeaveEvent` for user leaves
  - `ChangeMediaEvent` for media changes
  - `PlaylistUpdateEvent` for playlist updates
- Flexible payload parsing supporting both nested CyTube format and flat test format
- Support for both "msg" and "message" field names in chat events
- Comprehensive test suite for event conversion (`test_event_conversion.py`)
- Fallback to `RawEvent` for unknown event types (backward compatible)

### Changed
- Event handlers now receive typed event objects instead of `RawEvent`
- `MockKrytenClient` mirrors event conversion behavior for consistent testing
- Updated echo bot example to use typed `ChatMessageEvent` attributes

### Fixed
- Username extraction now handles both nested `{user: {name, rank}}` and flat `{username, rank}` structures
- PM events properly converted to `ChatMessageEvent`

## [0.1.0] - 2024-12-01

### Added
- Initial release of kryten-py
- Core `KrytenClient` for CyTube interaction via NATS
- Event handler registration with `@client.on()` decorator
- Channel and domain filtering for event handlers
- Comprehensive command API:
  - Chat commands: `send_chat()`, `send_pm()`
  - Playlist commands: `add_media()`, `delete_media()`, `move_media()`, `jump_to()`, `clear_playlist()`, `shuffle_playlist()`, `set_temp()`
  - Playback commands: `pause()`, `play()`, `seek()`
  - Moderation commands: `kick_user()`, `ban_user()`, `voteskip()`
- Health monitoring and metrics (`health()`, `channels`)
- `MockKrytenClient` for testing without NATS connection
- Connection management with async context manager support
- Configurable retry logic with exponential backoff
- NATS reconnection handling
- Pydantic-based configuration validation
- Comprehensive test suite (51 tests, 58% coverage)

### Documentation
- README with quickstart guide and examples
- API documentation for all public methods
- Configuration guide (CONFIG.md)
- Implementation notes (IMPLEMENTATION_NOTES.md)
- Echo bot example application

[0.2.0]: https://github.com/yourusername/kryten-py/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/yourusername/kryten-py/releases/tag/v0.1.0

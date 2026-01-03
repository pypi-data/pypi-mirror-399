# Deployment & Monitoring Guide

This guide covers how to deploy `kryten-py` services effectively, monitor their health, and integrate with the Kryten ecosystem's service registry.

## 1. Service Lifecycle Protocol

Kryten services participate in a lifecycle protocol to announce their presence and status.

### Configuration
Enable lifecycle management in your `ServiceConfig`:

```python
config = KrytenConfig(
    # ... nats/channels config ...
    service=ServiceConfig(
        name="my-bot",          # Unique service name
        version="1.0.0",
        enable_heartbeat=True,  # Send periodic heartbeats
        heartbeat_interval=30,  # Seconds (default: 30)
        health_port=8080        # Optional HTTP health endpoint
    )
)
```

### Protocol Events
The `KrytenClient` automatically handles these events:

1.  **Startup:** Publishes `kryten.lifecycle.my-bot.startup` on connection.
    *   Payload: `{ "service": "my-bot", "hostname": "...", "version": "1.0.0", ... }`
2.  **Heartbeat:** Publishes `kryten.lifecycle.my-bot.heartbeat` every 30s.
    *   Payload: Includes uptime and metadata.
3.  **Shutdown:** Publishes `kryten.lifecycle.my-bot.shutdown` on `disconnect()`.
4.  **Discovery:** Responds to `kryten.service.discovery.poll` by re-broadcasting startup info.

## 2. Health Monitoring

### Internal Health Check (`client.health()`)
You can programmatically access the client's internal health state. This is useful for building your own `/health` HTTP endpoints.

```python
health = client.health()

print(f"Status: {health.state}")           # connected, connecting, disconnected
print(f"Uptime: {health.uptime_seconds}s")
print(f"Events: {health.events_received}")
print(f"Errors: {health.errors}")
print(f"Latency: {health.avg_event_latency_ms}ms")
```

### Monitoring Metrics
The `HealthStatus` object tracks:
*   **Connection State:** Critical for readiness probes.
*   **Event Counters:** `events_received`, `commands_sent`.
*   **Error Rate:** `errors` count. Sudden spikes indicate issues.
*   **Latency:** `avg_event_latency_ms` tracks processing time of your handlers.

## 3. Deployment Considerations

### Docker / Containerization
*   **Signal Handling:** Ensure your container orchestrator sends `SIGINT` or `SIGTERM`. `KrytenClient.run()` catches these (via `asyncio` loop) to perform a graceful shutdown.
*   **Health Checks:** If exposing an HTTP port (via `health_port` config), configure your orchestrator (Kubernetes/Docker Swarm) to probe `/health`.

### Logging
`kryten-py` uses the standard Python `logging` module.
*   **Default:** Logs to stderr with configured level (`INFO` by default).
*   **Integration:** Pass your own `Logger` instance to `KrytenClient` to integrate with structured logging systems (JSON logs, Sentry, etc.).

```python
import logging
logger = logging.getLogger("my-service")
# ... configure handlers ...
client = KrytenClient(config, logger=logger)
```

## 4. Groupwide Restarts

The library supports coordinated restarts (e.g., for configuration updates).

### Handling Restart Requests
Your service can listen for "Group Restart" signals issued by administrators.

```python
# Register a callback for restart notices
client.on_group_restart(handle_restart)

async def handle_restart(data):
    initiator = data.get("initiator")
    reason = data.get("reason")
    delay = data.get("delay_seconds", 5)
    
    logger.warning(f"Restart requested by {initiator}: {reason}")
    
    # Perform any custom cleanup if needed
    # Note: You don't need to exit immediately; the orchestrator 
    # or a separate mechanism usually handles the process restart.
    # This callback is for preparation (draining queues, saving state).
```

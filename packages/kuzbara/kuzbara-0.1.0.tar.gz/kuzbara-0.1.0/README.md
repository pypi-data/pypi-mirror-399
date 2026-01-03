# Kuzbara 🌿

Fresh, organic health checks for Python.

Kuzbara (Arabic for Coriander) is a robust, standard-compliant health check library. It solves the biggest pain point in modern Python services: **Running async and sync checks together without blocking your app.**

It automatically detects your database drivers (SQLAlchemy, asyncpg, psycopg2, redis-py) and executes them in the correct mode (Native Async or Threaded Sync).

## Features

*   ⚡ **Hybrid Runner**: Safely runs blocking I/O (Disk, Psycopg2) alongside async tasks (Asyncpg, Redis) in the same request.
*   🔌 **Universal Probes**: One `PostgresProbe` class handles asyncpg, psycopg, and SQLAlchemy automatically.
*   📜 **IETF Compliant**: Returns `application/health+json` (RFC Draft).
*   🛡️ **Zero-Dependency Core**: The base library has 0 external requirements.

## Installation

```bash
pip install kuzbara
```

Optional extras:

```bash
pip install "kuzbara[http]"   # For checking external APIs (httpx)
pip install "kuzbara[system]" # For checking Memory usage (psutil)
```

## Quick Start

### 1. The Registry

Define your checks in a central file (e.g., `health.py`).

```python
from kuzbara import HealthCheck
from kuzbara.probes import PostgresProbe, RedisProbe, DiskProbe

# Create the registry
health = HealthCheck(name="payment-service")

# --- Database Check ---
# You just pass the connection/pool. Kuzbara figures out the driver.
# Works with: asyncpg, psycopg2, psycopg3, SQLAlchemy (Sync & Async)
health.add_probe(PostgresProbe(
    conn=db_pool, 
    name="main-db"
))

# --- Redis Check ---
# Works with: redis-py (Sync) and redis.asyncio (Async)
health.add_probe(RedisProbe(
    client=redis_client, 
    name="cache-layer"
))

# --- System Check ---
# Runs in a thread automatically to avoid blocking the event loop
health.add_probe(DiskProbe(path="/", warning_mb=500))
```

### 2. The API (FastAPI Example)

Expose the check in your application.

```python
from fastapi import FastAPI
from kuzbara.adapters.fastapi import create_health_router
from .health import health # Import your registry

app = FastAPI()

# Adds the /health endpoint
app.include_router(create_health_router(health))
```

### The Output

Hitting `GET /health` returns a structured IETF JSON response.

```json
{
  "status": "warn",
  "version": "1.0.0",
  "checks": {
    "main-db": [
      {
        "status": "pass",
        "componentType": "datastore",
        "observedValue": 1,
        "time": "2023-10-27T10:00:00Z"
      }
    ],
    "disk": [
      {
        "status": "warn",
        "componentType": "system",
        "output": "Disk space low: 450MB < 500MB",
        "observedValue": 450
      }
    ]
  }
}
```

## Available Probes

| Probe | Description | Dependencies |
| :--- | :--- | :--- |
| `PostgresProbe` | Universal SQL check. Auto-detects driver. | None (uses your existing driver) |
| `RedisProbe` | Checks Redis connectivity (Sync/Async). | None (uses your existing client) |
| `HttpProbe` | Checks external APIs (e.g. Stripe, Auth0). | `httpx` |
| `DiskProbe` | Checks free disk space. | Standard Library |
| `MemoryProbe` | Checks RAM usage. | `psutil` |

## Writing Custom Probes

Subclass `BaseProbe` and implement `check()`. If you define `async def check()`, it runs on the loop. If you define `def check()`, it runs in a thread.

```python
from kuzbara import BaseProbe, WarnCondition

class MyServiceProbe(BaseProbe):
    async def check(self):
        # Your logic here
        if some_value > 10:
             raise WarnCondition("Value is high but acceptable")
        return "OK"
```

## License

[MIT](LICENSE)

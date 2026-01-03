import asyncio
import inspect
from typing import Any, Union

from kuzbara.probes.base import BaseProbe

class RedisProbe(BaseProbe):
    """
    Health check for Redis.
    
    Compatible with:
    - redis-py (Sync): redis.Redis(...)
    - redis-py (Async): redis.asyncio.Redis(...)
    """
    def __init__(self, client: Any, name: str = "redis", timeout: float = 3.0):
        super().__init__(name, timeout, component_type="datastore")
        self.client = client
        
        # Auto-detect: Is the client's 'ping' method async?
        # This determines how we execute the check.
        self.is_async_client = inspect.iscoroutinefunction(client.ping)

    async def check(self) -> str:
        """
        Pings Redis. Returns 'PONG' on success.
        """
        if self.is_async_client:
            # Native Async Execution
            if not await self.client.ping():
                raise ConnectionError("Redis ping failed (returned False)")
        else:
            # Sync Client: Offload to thread to ensure we don't block the loop
            # Note: The Runner *could* handle this if we made check() sync,
            # but wrapping it here allows this single class to support BOTH drivers.
            await asyncio.to_thread(self._sync_ping)
            
        return "PONG"

    def _sync_ping(self):
        """Helper for blocking sync calls."""
        if not self.client.ping():
            raise ConnectionError("Redis ping failed (returned False)")
import inspect
import asyncio
from typing import Any
from enum import Enum, auto

from kuzbara.probes.base import BaseProbe

class SQLDriverType(Enum):
    ASYNCPG = auto()       # async
    PSYCOPG_ASYNC = auto() # async (psycopg 3)
    PSYCOPG_SYNC = auto()  # sync (psycopg 2 or 3)
    SQLALCHEMY_ASYNC = auto()
    SQLALCHEMY_SYNC = auto()
    UNKNOWN = auto()

class PostgresProbe(BaseProbe):
    """
    Universal PostgreSQL Health Check.
    Auto-detects the driver type (Sync vs Async) from the connection object.
    """
    def __init__(
        self, 
        conn: Any,  # Pool, Engine, or Connection
        name: str = "postgres", 
        timeout: float = 5.0,
        query: str = "SELECT 1"
    ):
        super().__init__(name, timeout, component_type="datastore")
        self.conn = conn
        self.query = query
        self.driver_type = self._detect_driver(conn)

        if self.driver_type == SQLDriverType.UNKNOWN:
            # We fail at startup so the user knows immediately
            raise ValueError(f"Unsupported connection object: {type(conn)}")

    def _detect_driver(self, conn: Any) -> SQLDriverType:
        """Heuristics to identify the driver."""
        conn_type = str(type(conn))
        
        # 1. asyncpg
        if ("asyncpg" in conn_type or "MockAsyncpg" in conn_type) and hasattr(conn, "fetchval"):
            return SQLDriverType.ASYNCPG
        
        # 2. SQLAlchemy
        if "sqlalchemy" in conn_type or "MockSQLAlchemy" in conn_type:
             if hasattr(conn, "connect"): # Engine
                 if "AsyncEngine" in conn_type:
                     return SQLDriverType.SQLALCHEMY_ASYNC
                 return SQLDriverType.SQLALCHEMY_SYNC

        # 3. Psycopg (v3 or v2)
        if hasattr(conn, "execute"): 
             # Psycopg3 async connection has an async execute
             if inspect.iscoroutinefunction(conn.execute):
                 return SQLDriverType.PSYCOPG_ASYNC
             return SQLDriverType.PSYCOPG_SYNC

        # 4. Psycopg Connection Pools (getconn)
        if hasattr(conn, "getconn"): 
            return SQLDriverType.PSYCOPG_SYNC
            
        return SQLDriverType.UNKNOWN

    async def check(self) -> Any:
        """
        Dispatches to the correct logic based on detection.
        """
        # --- ASYNC PATHS (Native await) ---
        if self.driver_type == SQLDriverType.ASYNCPG:
            return await self.conn.fetchval(self.query)

        elif self.driver_type == SQLDriverType.SQLALCHEMY_ASYNC:
            from sqlalchemy import text
            async with self.conn.connect() as connection:
                result = await connection.execute(text(self.query))
                return result.scalar()

        elif self.driver_type == SQLDriverType.PSYCOPG_ASYNC:
             cur = await self.conn.execute(self.query)
             return await cur.fetchone()

        # --- SYNC PATHS (Threaded wrapper) ---
        # We must wrap blocking calls in to_thread so we don't freeze the loop
        return await asyncio.to_thread(self._execute_sync)

    def _execute_sync(self):
        """Pure blocking logic for sync drivers."""
        if self.driver_type == SQLDriverType.SQLALCHEMY_SYNC:
            from sqlalchemy import text
            with self.conn.connect() as connection:
                return connection.execute(text(self.query)).scalar()

        elif self.driver_type == SQLDriverType.PSYCOPG_SYNC:
            # Handle Pool vs Connection
            if hasattr(self.conn, "getconn"): # Pool
                conn = self.conn.getconn()
                try:
                    with conn.cursor() as cur:
                        cur.execute(self.query)
                        return cur.fetchone()[0]
                finally:
                    self.conn.putconn(conn)
            else: # Raw Connection
                 with self.conn.cursor() as cur:
                    cur.execute(self.query)
                    return cur.fetchone()[0]
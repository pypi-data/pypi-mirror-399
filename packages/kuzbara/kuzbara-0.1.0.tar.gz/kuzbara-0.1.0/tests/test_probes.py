import pytest
import inspect
from unittest.mock import MagicMock
from kuzbara.probes.sql import PostgresProbe, SQLDriverType
from kuzbara.probes.redis import RedisProbe

# --- Mocks for SQL Drivers ---

class MockAsyncpgPool:
    """Fake asyncpg pool (has fetchval)"""
    async def fetchval(self, query):
        return 1

class MockPsycopg2Connection:
    """Fake psycopg2 connection (has cursor)"""
    def cursor(self):
        return MagicMock()

class MockSQLAlchemyEngine:
    """Fake SQLAlchemy Engine (has connect)"""
    def connect(self):
        return MagicMock()

# --- Mocks for Redis ---

class MockRedisSync:
    def ping(self):
        return True

class MockRedisAsync:
    async def ping(self):
        return True

# --- Tests ---

def test_postgres_detects_asyncpg():
    pool = MockAsyncpgPool()
    probe = PostgresProbe(conn=pool)
    assert probe.driver_type == SQLDriverType.ASYNCPG
    # Verify it treats check() as a coroutine
    assert inspect.iscoroutinefunction(probe.check)

def test_postgres_detects_psycopg2():
    conn = MockPsycopg2Connection()
    # Mocking getconn to simulate a Pool
    conn.getconn = lambda: conn 
    
    probe = PostgresProbe(conn=conn)
    assert probe.driver_type == SQLDriverType.PSYCOPG_SYNC

def test_redis_detects_async_client():
    client = MockRedisAsync()
    probe = RedisProbe(client=client)
    assert probe.is_async_client is True

def test_redis_detects_sync_client():
    client = MockRedisSync()
    probe = RedisProbe(client=client)
    assert probe.is_async_client is False
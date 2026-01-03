import asyncio
import pytest
import time
from kuzbara import BaseProbe, HealthStatus
from kuzbara.runner import AsyncRunner
from kuzbara.exceptions import WarnCondition

# --- Mocks ---

class MockAsyncProbe(BaseProbe):
    async def check(self):
        await asyncio.sleep(0.01) # Simulate I/O
        return "async_ok"

class MockSyncProbe(BaseProbe):
    def check(self):
        time.sleep(0.01) # Simulate blocking I/O
        return "sync_ok"

class MockFailProbe(BaseProbe):
    async def check(self):
        raise ValueError("boom")

class MockWarnProbe(BaseProbe):
    async def check(self):
        raise WarnCondition("careful now")

# --- Tests ---

@pytest.mark.asyncio
async def test_async_runner_hybrid_execution():
    """
    Verifies that AsyncRunner handles both Sync and Async probes correctly.
    """
    probes = [
        MockAsyncProbe(name="async_p"),
        MockSyncProbe(name="sync_p")
    ]
    
    runner = AsyncRunner(probes)
    result = await runner.execute()

    assert result["status"] == HealthStatus.PASS
    checks = result["checks"]
    
    # Check Async Probe
    assert checks["async_p"][0]["status"] == "pass"
    assert checks["async_p"][0]["observedValue"] == "async_ok"
    
    # Check Sync Probe (Should have been wrapped in thread)
    assert checks["sync_p"][0]["status"] == "pass"
    assert checks["sync_p"][0]["observedValue"] == "sync_ok"

@pytest.mark.asyncio
async def test_runner_aggregates_status():
    """
    Verifies that one FAIL causes the global status to be FAIL.
    """
    probes = [
        MockAsyncProbe(name="ok"),
        MockFailProbe(name="bad")
    ]
    
    runner = AsyncRunner(probes)
    result = await runner.execute()

    assert result["status"] == HealthStatus.FAIL
    assert result["checks"]["bad"][0]["status"] == "fail"
    assert result["checks"]["bad"][0]["output"] == "boom"

@pytest.mark.asyncio
async def test_runner_warn_logic():
    """
    Verifies that WARN does not cause a global FAIL.
    """
    probes = [
        MockAsyncProbe(name="ok"),
        MockWarnProbe(name="slow")
    ]
    
    runner = AsyncRunner(probes)
    result = await runner.execute()

    assert result["status"] == HealthStatus.WARN
    assert result["checks"]["slow"][0]["status"] == "warn"
    assert result["checks"]["slow"][0]["output"] == "careful now"
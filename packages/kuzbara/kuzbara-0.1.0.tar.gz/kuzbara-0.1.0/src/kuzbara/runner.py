import asyncio
import inspect
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

# These imports will work once we create the other files
from kuzbara.domain import ProbeResult, HealthStatus
from kuzbara.probes.base import BaseProbe
from kuzbara.utils import aggregate_results
from kuzbara.exceptions import WarnCondition

class BaseRunner:
    def __init__(self, probes: List[BaseProbe], global_timeout: float = 30.0):
        self.probes = probes
        self.global_timeout = global_timeout

    def _safe_sync_execution(self, probe: BaseProbe) -> ProbeResult:
        """
        Runs a sync probe safely.
        Used by BOTH runners to execute sync logic in threads.
        """
        start = time.perf_counter()
        try:
            # 1. Execute the blocking check
            # We rely on the driver's internal timeout.
            result = probe.check()
            
            duration_ms = (time.perf_counter() - start) * 1000
            timeout_ms = probe.timeout * 1000
            
            # 2. Timeout Warning (Soft Timeout)
            if duration_ms > timeout_ms:
                return probe._build_result(
                    status=HealthStatus.WARN,
                    output=f"Slow response: {duration_ms:.0f}ms (threshold: {timeout_ms:.0f}ms)",
                    observed_value=result,
                    latency_ms=duration_ms
                )

            # 3. Success
            return probe._build_result(
                status=HealthStatus.PASS, 
                observed_value=result, 
                latency_ms=duration_ms
            )

        except WarnCondition as w:
            # 4. Explicit Warning from Probe
            duration_ms = (time.perf_counter() - start) * 1000
            return probe._build_result(
                status=HealthStatus.WARN,
                output=str(w),
                latency_ms=duration_ms
            )

        except Exception as e:
            # 5. Failure / Crash
            duration_ms = (time.perf_counter() - start) * 1000
            return probe._build_result(
                status=HealthStatus.FAIL,
                output=str(e),
                latency_ms=duration_ms
            )

class AsyncRunner(BaseRunner):
    """
    For ASGI apps (FastAPI, Litestar).
    Uses native asyncio for maximum concurrency.
    """
    async def execute(self) -> Dict[str, Any]:
        tasks = []
        for probe in self.probes:
            if inspect.iscoroutinefunction(probe.check):
                # Native Async: Let BaseProbe.run handle it (includes timeouts)
                tasks.append(probe.run())
            else:
                # Sync: Offload to thread to unblock the event loop
                tasks.append(self._run_sync_in_thread(probe))

        try:
            # Enforce global timeout for the whole suite
            async with asyncio.timeout(self.global_timeout):
                results = await asyncio.gather(*tasks, return_exceptions=True)
        except TimeoutError:
            # Fail fast if the whole suite hangs
            return aggregate_results([], version="1.0.0") 

        clean_results = self._normalize_results(results)
        return aggregate_results(clean_results)

    async def _run_sync_in_thread(self, probe: BaseProbe) -> ProbeResult:
        return await asyncio.to_thread(self._safe_sync_execution, probe)

    def _normalize_results(self, results) -> List[ProbeResult]:
        clean = []
        for res in results:
            if isinstance(res, ProbeResult):
                clean.append(res)
            elif isinstance(res, Exception):
                # Catches unhandled crashes in tasks (e.g. syntax errors in probe)
                clean.append(ProbeResult(
                    status=HealthStatus.FAIL, 
                    name="runner", 
                    output=f"Runner Exception: {str(res)}"
                ))
        return clean


class SyncRunner(BaseRunner):
    """
    For WSGI apps (Flask, Django).
    Uses a ThreadPool + a Single-Loop Batcher for Async probes.
    """
    def execute(self) -> Dict[str, Any]:
        sync_probes = []
        async_probes = []

        # Sort probes into buckets
        for probe in self.probes:
            if inspect.iscoroutinefunction(probe.check):
                async_probes.append(probe)
            else:
                sync_probes.append(probe)

        results = []
        
        # We use a ThreadPool to run everything in parallel
        with ThreadPoolExecutor() as executor:
            # 1. Submit Sync Probes (Standard threading)
            futures = [
                executor.submit(self._safe_sync_execution, probe) 
                for probe in sync_probes
            ]

            # 2. Submit Async Batch (The Magic Trick)
            # We spin up ONE event loop to run ALL async probes together.
            if async_probes:
                futures.append(executor.submit(self._run_async_batch, async_probes))

            # 3. Gather Results
            for future in futures:
                try:
                    res = future.result(timeout=self.global_timeout)
                    if isinstance(res, list):
                        results.extend(res) # The async batch returns a list
                    else:
                        results.append(res) # Sync probes return single items
                except Exception:
                    # Catch thread/timeout errors here if needed
                    pass

        return aggregate_results(results)

    def _run_async_batch(self, probes: List[BaseProbe]) -> List[ProbeResult]:
        """
        Creates a temporary event loop to run all async probes concurrently.
        """
        async def batch():
            # Run all async probes in parallel inside this ephemeral loop
            return await asyncio.gather(*[p.run() for p in probes])
        
        return asyncio.run(batch())
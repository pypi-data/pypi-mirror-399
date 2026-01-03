import time
import asyncio
import inspect
from abc import ABC, abstractmethod
from typing import Any, Union, Awaitable

from kuzbara.domain import ProbeResult, HealthStatus
from kuzbara.exceptions import WarnCondition

class BaseProbe(ABC):
    def __init__(self, name: str, timeout: float = 5.0, component_type: str = "component"):
        self._name = name
        self.timeout = timeout
        self.component_type = component_type

    @property
    def name(self) -> str:
        return self._name

    async def run(self) -> ProbeResult:
        """
        The uniform entry point used by the AsyncRunner.
        Handles timing, exceptions, and timeouts for ASYNC execution.
        """
        start = time.perf_counter()
        try:
            # Enforce the per-probe timeout here (Async Context)
            async with asyncio.timeout(self.timeout):
                if inspect.iscoroutinefunction(self.check):
                    result = await self.check()
                else:
                    # Fallback if a sync probe is called in run() directly
                    result = self.check()
            
            duration_ms = (time.perf_counter() - start) * 1000
            return self._build_result(
                status=HealthStatus.PASS, 
                observed_value=result,
                latency_ms=duration_ms
            )

        except TimeoutError:
            duration_ms = (time.perf_counter() - start) * 1000
            return self._build_result(
                status=HealthStatus.FAIL,
                output=f"Timeout after {self.timeout}s",
                latency_ms=duration_ms
            )
        except WarnCondition as w:
            duration_ms = (time.perf_counter() - start) * 1000
            return self._build_result(
                status=HealthStatus.WARN,
                output=str(w),
                latency_ms=duration_ms
            )
        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            return self._build_result(
                status=HealthStatus.FAIL,
                output=str(e),
                latency_ms=duration_ms
            )

    @abstractmethod
    def check(self) -> Union[Any, Awaitable[Any]]:
        """
        User implementation. 
        Returns observed value or raises Exception.
        """
        pass

    def _build_result(self, status: HealthStatus, output: str = None, 
                      observed_value: Any = None, latency_ms: float = 0) -> ProbeResult:
        return ProbeResult(
            status=status,
            name=self.name,
            component_type=self.component_type,
            output=output,
            observed_value=observed_value,
            metadata={"latency_ms": round(latency_ms, 2)}
        )
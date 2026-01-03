import shutil
from typing import Any

from kuzbara.probes.base import BaseProbe
from kuzbara.exceptions import WarnCondition

class DiskProbe(BaseProbe):
    """
    Checks free disk space.
    Zero dependencies (uses standard library).
    """
    def __init__(
        self, 
        path: str = "/", 
        name: str = "disk",
        warning_mb: int = 1000,   # 1 GB
        critical_mb: int = 100    # 100 MB
    ):
        super().__init__(name, component_type="system")
        self.path = path
        self.warning_mb = warning_mb
        self.critical_mb = critical_mb

    def check(self) -> float:
        """
        Returns free space in MB.
        This is a synchronous method, so the Runner will automatically
        execute it in a thread pool to avoid blocking the event loop.
        """
        total, used, free = shutil.disk_usage(self.path)
        free_mb = free / (1024 * 1024)
        
        # 1. Critical Failure (FAIL)
        if free_mb < self.critical_mb:
            raise OSError(f"Disk space critical: {free_mb:.0f}MB < {self.critical_mb}MB")

        # 2. Warning (WARN)
        if free_mb < self.warning_mb:
            raise WarnCondition(f"Disk space low: {free_mb:.0f}MB < {self.warning_mb}MB")

        # 3. Healthy (PASS)
        return round(free_mb, 2)


class MemoryProbe(BaseProbe):
    """
    Checks available memory.
    Requires: pip install psutil
    """
    def __init__(
        self, 
        name: str = "memory", 
        warning_percent: float = 85.0, 
        critical_percent: float = 95.0
    ):
        super().__init__(name, component_type="system")
        self.warning_percent = warning_percent
        self.critical_percent = critical_percent
        
        # Runtime check for optional dependency
        try:
            import psutil
            self._psutil = psutil
        except ImportError:
            raise ImportError("MemoryProbe requires 'psutil'. Install it via: pip install pulse-guard[system]")

    def check(self) -> float:
        mem = self._psutil.virtual_memory()
        usage_percent = mem.percent
        
        if usage_percent > self.critical_percent:
            raise OSError(f"Memory critical: {usage_percent}%")
        
        if usage_percent > self.warning_percent:
            raise WarnCondition(f"Memory high: {usage_percent}%")
            
        return usage_percent
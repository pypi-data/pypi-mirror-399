from enum import StrEnum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Union

class HealthStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"

@dataclass(frozen=True)
class ProbeResult:
    """
    The standardized output of a single check.
    Maps to the IETF JSON schema.
    """
    status: HealthStatus
    name: str
    component_type: Optional[str] = None
    observed_value: Union[str, int, float, None] = None
    observed_unit: Optional[str] = None
    output: Optional[str] = None
    time: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_healthy(self) -> bool:
        return self.status in (HealthStatus.PASS, HealthStatus.WARN)
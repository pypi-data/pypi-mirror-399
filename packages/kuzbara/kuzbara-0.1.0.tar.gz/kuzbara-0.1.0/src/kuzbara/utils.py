from typing import List, Dict, Any
from kuzbara.domain import ProbeResult, HealthStatus

def aggregate_results(results: List[ProbeResult], version: str = "1.0.0") -> Dict[str, Any]:
    global_status = HealthStatus.PASS
    checks = {}

    # Sort checks by name so the JSON output is deterministic (easier to test)
    sorted_results = sorted(results, key=lambda r: r.name)

    for res in sorted_results:
        # Build the IETF "check" object
        check_data = {
            "status": res.status,
            "componentType": res.component_type,
            "observedValue": res.observed_value,
            "time": res.time
        }
        # Only add optional fields if they exist to keep the JSON payload clean
        if res.output:
            check_data["output"] = res.output
        if res.observed_unit:
            check_data["observedUnit"] = res.observed_unit
        
        checks[res.name] = [check_data]

        # Strictest Wins Logic: FAIL overrides WARN, WARN overrides PASS
        if res.status == HealthStatus.FAIL:
            global_status = HealthStatus.FAIL
        elif res.status == HealthStatus.WARN and global_status != HealthStatus.FAIL:
            global_status = HealthStatus.WARN

    return {
        "status": global_status,
        "version": version,
        "checks": checks
    }
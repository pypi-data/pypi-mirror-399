from typing import Dict, List, Optional
from kuzbara.probes.base import BaseProbe

class HealthCheck:
    def __init__(
        self, 
        name: str = "app", 
        version: str = "0.0.1", 
        global_timeout: float = 30.0
    ):
        """
        The central registry for your health checks.
        
        :param name: Service name (e.g. "payment-api")
        :param version: Service version (e.g. git commit hash)
        :param global_timeout: Max time in seconds for the entire suite to run.
        """
        self.name = name
        self.version = version
        self.global_timeout = global_timeout
        self.probes: Dict[str, BaseProbe] = {}

    def add_probe(self, probe: BaseProbe):
        """Register a single probe."""
        self.probes[probe.name] = probe

    def add_probes(self, probes: List[BaseProbe]):
        """Register multiple probes at once."""
        for probe in probes:
            self.add_probe(probe)
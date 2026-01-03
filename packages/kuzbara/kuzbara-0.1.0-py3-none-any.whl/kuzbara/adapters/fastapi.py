from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from kuzbara.main import HealthCheck
from kuzbara.runner import AsyncRunner
from kuzbara.domain import HealthStatus

# RFC Draft defined media type
MEDIA_TYPE_HEALTH_JSON = "application/health+json"

class HealthRouter:
    def __init__(self, health_check: HealthCheck, path: str = "/health"):
        self.health_check = health_check
        self.path = path
        self.router = APIRouter()
        self.router.add_api_route(
            self.path, 
            self.endpoint, 
            methods=["GET"],
            response_class=JSONResponse,
            # Document the RFC content type response for Swagger UI
            responses={
                200: {"content": {MEDIA_TYPE_HEALTH_JSON: {}}},
                503: {"content": {MEDIA_TYPE_HEALTH_JSON: {}}},
            }
        )

    async def endpoint(self, response: Response):
        # 1. Instantiate Runner with config from the Registry
        runner = AsyncRunner(
            probes=self.health_check.probes.values(),
            global_timeout=self.health_check.global_timeout
        )

        # 2. Execute the checks
        result = await runner.execute()

        # 3. Map Status to HTTP Code
        # FAIL = 503 (Service Unavailable), everything else is 200 OK
        if result["status"] == HealthStatus.FAIL:
            response.status_code = 503
        else:
            response.status_code = 200
        
        # 4. Enforce RFC Content-Type
        response.headers["Content-Type"] = MEDIA_TYPE_HEALTH_JSON
        return result

# Convenience factory function
def create_health_router(health_check: HealthCheck, path: str = "/health") -> APIRouter:
    return HealthRouter(health_check, path).router
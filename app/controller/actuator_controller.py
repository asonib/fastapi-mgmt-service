import time
import platform
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from app.config.settings import settings
from app.schema.dtos import (
    ActuatorIndexResponse,
    ActuatorLink,
    ActuatorHealthResponse,
    HealthComponent,
    ActuatorInfoResponse,
)

router = APIRouter(prefix="/actuator", tags=["Actuator"])
START_TIME = time.time()


@router.get("", response_model=ActuatorIndexResponse)
async def actuator_index(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return ActuatorIndexResponse(
        links={
            "self": ActuatorLink(href=f"{base_url}/actuator"),
            "health": ActuatorLink(href=f"{base_url}/actuator/health"),
            "info": ActuatorLink(href=f"{base_url}/actuator/info"),
            "metrics": ActuatorLink(href=f"{base_url}/actuator/metrics"),
        }
    )


@router.get("/health", response_model=ActuatorHealthResponse)
async def health_check():
    return ActuatorHealthResponse(
        status="UP",
        components={
            "ping": HealthComponent(status="UP"),
            "diskSpace": HealthComponent(status="UP"),
        },
    )


@router.get("/health/liveness", status_code=status.HTTP_200_OK)
async def liveness_probe():
    return {"status": "UP"}


@router.get("/health/readiness", status_code=status.HTTP_200_OK)
async def readiness_probe():
    return {"status": "UP"}


@router.get("/info", response_model=ActuatorInfoResponse)
async def app_info():
    return ActuatorInfoResponse(
        app={
            "name": getattr(settings, "APP_NAME", "fastapi-mgmt-service"),
            "environment": getattr(settings, "ENV", "dev"),
            "python_version": platform.python_version(),
        }
    )


@router.get("/metrics")
async def metrics():
    uptime = round(time.time() - START_TIME, 2)
    return JSONResponse(
        content={
            "names": ["process.uptime"],
            "measurements": [{"statistic": "VALUE", "value": uptime}],
        }
    )
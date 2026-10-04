from fastapi import APIRouter
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready"}


@router.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

from fastapi import APIRouter, Depends, Response

from app.api.dependencies.auth import UserContext, get_current_user

router = APIRouter(prefix="/tiles", tags=["tiles"])


@router.get("/vector/{dataset_version_id}/{z}/{x}/{y}.mvt")
async def get_vector_tile(
    dataset_version_id: str,
    z: int,
    x: int,
    y: int,
    _user: UserContext = Depends(get_current_user),
) -> Response:
    # Placeholder empty MVT until tile-worker produces assets.
    return Response(content=b"", media_type="application/vnd.mapbox-vector-tile")


@router.get("/raster/{dataset_version_id}/{z}/{x}/{y}.png")
async def get_raster_tile(
    dataset_version_id: str,
    z: int,
    x: int,
    y: int,
    _user: UserContext = Depends(get_current_user),
) -> Response:
    return Response(content=b"", media_type="image/png")

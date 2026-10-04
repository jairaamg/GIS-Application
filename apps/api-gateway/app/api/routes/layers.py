from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies.auth import UserContext, get_current_user
from app.schemas.layer import Layer, LayerCreate, LayerList

router = APIRouter(prefix="/layers", tags=["layers"])

_LAYERS: dict[str, Layer] = {}


@router.get("", response_model=LayerList)
async def list_layers(
    project_id: str = Query(...),
    _user: UserContext = Depends(get_current_user),
) -> LayerList:
    items = [layer for layer in _LAYERS.values() if str(layer.project_id) == project_id]
    return LayerList(items=items)


@router.post("", response_model=Layer, status_code=201)
async def create_layer(
    body: LayerCreate,
    _user: UserContext = Depends(get_current_user),
) -> Layer:
    now = datetime.now(timezone.utc)
    layer = Layer(
        id=uuid4(),
        project_id=body.project_id,
        dataset_version_id=body.dataset_version_id,
        name=body.name,
        layer_type=body.layer_type,
        visible=body.visible,
        opacity=body.opacity,
        min_zoom=body.min_zoom,
        max_zoom=body.max_zoom,
        z_index=body.z_index,
        style_json=body.style_json,
        source_json=body.source_json,
        created_at=now,
        updated_at=now,
    )
    _LAYERS[str(layer.id)] = layer
    return layer


@router.get("/{layer_id}", response_model=Layer)
async def get_layer(layer_id: str, _user: UserContext = Depends(get_current_user)) -> Layer:
    layer = _LAYERS.get(layer_id)
    if not layer:
        raise HTTPException(status_code=404, detail="Layer not found")
    return layer

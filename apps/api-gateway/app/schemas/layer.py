from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class LayerCreate(BaseModel):
    project_id: UUID
    dataset_version_id: UUID
    name: str = Field(min_length=1, max_length=200)
    layer_type: str
    visible: bool = True
    opacity: float = Field(default=1.0, ge=0, le=1)
    min_zoom: float | None = None
    max_zoom: float | None = None
    z_index: int = 0
    style_json: dict[str, Any] = Field(default_factory=dict)
    source_json: dict[str, Any] = Field(default_factory=dict)


class Layer(BaseModel):
    id: UUID
    project_id: UUID
    dataset_version_id: UUID
    name: str
    layer_type: str
    visible: bool
    opacity: float
    min_zoom: float | None = None
    max_zoom: float | None = None
    z_index: int
    style_json: dict[str, Any]
    source_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class LayerList(BaseModel):
    items: list[Layer]

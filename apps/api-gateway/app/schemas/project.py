from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    organization_id: UUID


class Project(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str | None = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class ProjectList(BaseModel):
    items: list[Project]

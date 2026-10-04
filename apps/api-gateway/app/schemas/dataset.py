from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class DatasetStatus(str, Enum):
    UPLOADING = "UPLOADING"
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


class DatasetCreate(BaseModel):
    project_id: UUID
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    dataset_type: str
    source_format: str
    content_type: str | None = None
    size_bytes: int | None = None


class Dataset(BaseModel):
    id: UUID
    project_id: UUID
    organization_id: UUID
    name: str
    description: str | None = None
    dataset_type: str
    source_format: str
    status: DatasetStatus
    current_version_id: UUID | None = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class DatasetPage(BaseModel):
    items: list[Dataset]
    total: int = 0
    limit: int = 50
    offset: int = 0


class DatasetUploadSession(BaseModel):
    dataset: Dataset
    upload_url: str
    object_key: str
    expires_in_seconds: int = 3600

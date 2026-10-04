from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    CANCELLED = "CANCELLED"


class ProcessingRequest(BaseModel):
    job_type: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class Job(BaseModel):
    id: UUID
    dataset_id: UUID | None = None
    dataset_version_id: UUID | None = None
    job_type: str
    status: JobStatus
    progress: float = 0
    parameters_json: dict[str, Any] = Field(default_factory=dict)
    result_json: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None

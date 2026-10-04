from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies.auth import UserContext, get_current_user
from app.schemas.dataset import (
    Dataset,
    DatasetCreate,
    DatasetPage,
    DatasetStatus,
    DatasetUploadSession,
)
from app.schemas.job import Job, JobStatus, ProcessingRequest

router = APIRouter(prefix="/datasets", tags=["datasets"])

_DATASETS: dict[str, Dataset] = {}
_JOBS: dict[str, Job] = {}


@router.get("", response_model=DatasetPage)
async def list_datasets(
    project_id: str | None = None,
    status: DatasetStatus | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _user: UserContext = Depends(get_current_user),
) -> DatasetPage:
    items = list(_DATASETS.values())
    if project_id:
        items = [d for d in items if str(d.project_id) == project_id]
    if status:
        items = [d for d in items if d.status == status]
    page = items[offset : offset + limit]
    return DatasetPage(items=page, total=len(items), limit=limit, offset=offset)


@router.post("", response_model=DatasetUploadSession, status_code=201)
async def create_dataset(
    body: DatasetCreate,
    user: UserContext = Depends(get_current_user),
) -> DatasetUploadSession:
    now = datetime.now(timezone.utc)
    dataset_id = uuid4()
    object_key = f"quarantine/{body.project_id}/{dataset_id}/source"
    dataset = Dataset(
        id=dataset_id,
        project_id=body.project_id,
        organization_id=uuid4(),
        name=body.name,
        description=body.description,
        dataset_type=body.dataset_type,
        source_format=body.source_format,
        status=DatasetStatus.UPLOADING,
        created_by=user.user_id or uuid4(),
        created_at=now,
        updated_at=now,
    )
    _DATASETS[str(dataset.id)] = dataset
    return DatasetUploadSession(
        dataset=dataset,
        upload_url=f"/api/v1/uploads/{dataset.id}",
        object_key=object_key,
    )


@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset(
    dataset_id: str,
    _user: UserContext = Depends(get_current_user),
) -> Dataset:
    dataset = _DATASETS.get(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.delete("/{dataset_id}", status_code=204)
async def archive_dataset(
    dataset_id: str,
    _user: UserContext = Depends(get_current_user),
) -> None:
    dataset = _DATASETS.get(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    dataset.status = DatasetStatus.ARCHIVED
    dataset.updated_at = datetime.now(timezone.utc)


@router.post("/{dataset_id}/process", response_model=Job, status_code=202)
async def process_dataset(
    dataset_id: str,
    body: ProcessingRequest,
    _user: UserContext = Depends(get_current_user),
) -> Job:
    dataset = _DATASETS.get(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    now = datetime.now(timezone.utc)
    job = Job(
        id=uuid4(),
        dataset_id=dataset.id,
        dataset_version_id=dataset.current_version_id,
        job_type=body.job_type,
        status=JobStatus.QUEUED,
        parameters_json=body.parameters,
        created_at=now,
    )
    _JOBS[str(job.id)] = job
    dataset.status = DatasetStatus.PROCESSING
    dataset.updated_at = now
    return job

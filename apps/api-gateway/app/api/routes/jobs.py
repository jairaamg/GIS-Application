from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.auth import UserContext, get_current_user
from app.api.routes.datasets import _JOBS
from app.schemas.job import Job, JobStatus

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: str, _user: UserContext = Depends(get_current_user)) -> Job:
    job = _JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}", response_model=Job, status_code=202)
async def cancel_job(job_id: str, _user: UserContext = Depends(get_current_user)) -> Job:
    job = _JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = JobStatus.CANCEL_REQUESTED
    return job

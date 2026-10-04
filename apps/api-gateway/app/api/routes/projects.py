from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends

from app.api.dependencies.auth import UserContext, get_current_user
from app.schemas.project import Project, ProjectCreate, ProjectList

router = APIRouter(prefix="/projects", tags=["projects"])

_STORE: dict[str, Project] = {}


@router.get("", response_model=ProjectList)
async def list_projects(_user: UserContext = Depends(get_current_user)) -> ProjectList:
    return ProjectList(items=list(_STORE.values()))


@router.post("", response_model=Project, status_code=201)
async def create_project(
    body: ProjectCreate,
    user: UserContext = Depends(get_current_user),
) -> Project:
    now = datetime.now(timezone.utc)
    project = Project(
        id=uuid4(),
        organization_id=body.organization_id,
        name=body.name,
        description=body.description,
        created_by=user.user_id or uuid4(),
        created_at=now,
        updated_at=now,
    )
    _STORE[str(project.id)] = project
    return project


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    _user: UserContext = Depends(get_current_user),
) -> Project:
    from fastapi import HTTPException

    project = _STORE.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

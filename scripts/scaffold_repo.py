#!/usr/bin/env python3
"""Bootstrap the GIS platform monorepo skeleton from architecture docs."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip("\n") if content.startswith("\n") else content, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def move_architecture_docs() -> None:
    dest = ROOT / "docs" / "architecture"
    dest.mkdir(parents=True, exist_ok=True)
    for name in [
        "01-system-context.md",
        "02-hld.md",
        "03-lld.md",
        "04-api-openapi.yaml",
        "05-event-schema.yaml",
        "06-database-schema.sql",
        "07-layer-model.json",
        "08-processing-job-model.json",
        "09-license-policy.md",
        "10-threat-model.md",
        "12-docker-compose.yml",
        "13-local-development.md",
        "14-golden-datasets.md",
        "MANIFEST.json",
    ]:
        src = ROOT / name
        if src.exists():
            shutil.move(str(src), str(dest / name))
            print(f"moved {name} -> docs/architecture/")
    adr_src = ROOT / "11-adr"
    adr_dest = dest / "11-adr"
    if adr_src.exists():
        if adr_dest.exists():
            shutil.rmtree(adr_dest)
        shutil.move(str(adr_src), str(adr_dest))
        print("moved 11-adr -> docs/architecture/11-adr/")


def main() -> None:
    move_architecture_docs()

    write(
        ROOT / ".gitignore",
        """
# Secrets / env
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.egg-info/
dist/
build/
.coverage
htmlcov/

# Node
node_modules/
apps/web/dist/
*.tsbuildinfo
.npm/
.vite/

# IDE / OS
.idea/
.vscode/
*.swp
.DS_Store
Thumbs.db

# Data / local runtime
data/
tmp/
*.log
coverage/
sbom/
license-reports/
""",
    )

    write(
        ROOT / ".env.example",
        """
# Copy to .env — never commit .env
DATABASE_URL=postgresql+asyncpg://gis:gis_dev_only@localhost:5432/gis
NATS_URL=nats://localhost:4222
VALKEY_URL=redis://localhost:6379/0
OBJECT_STORE_ENDPOINT=http://localhost:8333
OIDC_ISSUER=http://localhost:8080/realms/gis
OIDC_CLIENT_ID=gis-web
OIDC_CLIENT_SECRET=change-me-dev-only
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Frontend (public)
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_OIDC_ISSUER=http://localhost:8080/realms/gis
VITE_OIDC_CLIENT_ID=gis-web
""",
    )

    write(
        ROOT / "docker-compose.yml",
        """
services:

  postgres:
    image: postgres:17
    environment:
      POSTGRES_DB: gis
      POSTGRES_USER: gis
      POSTGRES_PASSWORD: gis_dev_only
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docs/architecture/06-database-schema.sql:/docker-entrypoint-initdb.d/001-schema.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U gis -d gis"]
      interval: 5s
      timeout: 5s
      retries: 20

  nats:
    image: nats:2
    command: ["-js", "-m", "8222"]
    ports:
      - "4222:4222"
      - "8222:8222"
    volumes:
      - nats_data:/data
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8222/healthz"]
      interval: 5s
      timeout: 3s
      retries: 20

  valkey:
    image: valkey/valkey:8
    ports:
      - "6379:6379"
    volumes:
      - valkey_data:/data

  seaweedfs:
    image: chrislusf/seaweedfs:3
    command: ["server", "-dir=/data", "-s3"]
    ports:
      - "8333:8333"
      - "9000:9000"
      - "9333:9333"
    volumes:
      - seaweed_data:/data

  keycloak:
    image: quay.io/keycloak/keycloak:26
    command: ["start-dev"]
    environment:
      KC_BOOTSTRAP_ADMIN_USERNAME: admin
      KC_BOOTSTRAP_ADMIN_PASSWORD: admin_dev_only
    ports:
      - "8080:8080"

  api:
    build:
      context: ./apps/api-gateway
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql+asyncpg://gis:gis_dev_only@postgres:5432/gis
      NATS_URL: nats://nats:4222
      VALKEY_URL: redis://valkey:6379/0
      OBJECT_STORE_ENDPOINT: http://seaweedfs:8333
      OIDC_ISSUER: http://keycloak:8080/realms/gis
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      nats:
        condition: service_healthy

  web:
    build:
      context: ./apps/web
    environment:
      VITE_API_BASE_URL: http://localhost:8000/api/v1
    ports:
      - "5173:5173"
    depends_on:
      - api

volumes:
  postgres_data:
  nats_data:
  valkey_data:
  seaweed_data:
""",
    )

    write(
        ROOT / "Makefile",
        """
.PHONY: infra-up infra-down api web test lint license-scan sbom migrate

infra-up:
\tdocker compose up -d postgres nats valkey seaweedfs keycloak

infra-down:
\tdocker compose down

api:
\tcd apps/api-gateway && python -m uvicorn app.main:app --reload --port 8000

web:
\tcd apps/web && npm run dev

test:
\tcd apps/api-gateway && pytest -q
\tcd apps/web && npm test -- --run

lint:
\tcd apps/api-gateway && ruff check . && ruff format --check .
\tcd apps/web && npm run typecheck

migrate:
\tcd apps/api-gateway && alembic upgrade head

license-scan:
\t@echo "Run SBOM/license scan in CI against pinned dependency versions."

sbom:
\t@mkdir -p sbom && echo "Generate SBOM artifacts into ./sbom"
""",
    )

    write(
        ROOT / "pyproject.toml",
        """
[project]
name = "gis-platform"
version = "0.1.0"
description = "Open-source 2D/3D GIS platform monorepo"
requires-python = ">=3.12"
readme = "README.md"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["apps/api-gateway/tests", "workers"]
""",
    )

    write(
        ROOT / "README.md",
        """
# Open-Source 2D/3D GIS Platform

Web GIS platform for ingesting, processing, cataloguing, serving and visualizing heterogeneous 2D/3D geospatial datasets.

## Stack

- **Frontend:** React + TypeScript, MapLibre (2D), deck.gl (3D)
- **API:** FastAPI (API Gateway / BFF + modular domains)
- **Processing:** GDAL/OGR, PDAL workers via NATS JetStream
- **Data:** PostgreSQL metadata, SeaweedFS object storage, Valkey cache
- **Identity:** Keycloak (OIDC)

## Repository layout

```text
apps/
  api-gateway/     FastAPI BFF + domain modules
  web/             React map application
workers/           Async GIS processing workers
packages/
  contracts/       Shared API/event contracts
docs/architecture/ Architecture baseline (HLD/LLD/ADRs)
infra/             Infra helpers and Keycloak realm stub
```

## Quick start

```bash
cp .env.example .env
docker compose up -d postgres nats valkey seaweedfs keycloak

# API
cd apps/api-gateway
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Web
cd apps/web
npm install
npm run dev
```

- API docs: http://localhost:8000/docs
- Web app: http://localhost:5173
- Keycloak: http://localhost:8080
- NATS monitor: http://localhost:8222

## Architecture docs

See [`docs/architecture/`](docs/architecture/) for system context, HLD, LLD, OpenAPI, events, schema and ADRs.

## Status

This repository starts from the architecture baseline. Day-one services are modular inside the API gateway; workers and tile serving scale independently.
""",
    )

    # --- packages/contracts ---
    write(
        ROOT / "packages" / "contracts" / "README.md",
        """
# Contracts

Versioned shared contracts only. Do not put ORM models or service internals here.

- OpenAPI: `docs/architecture/04-api-openapi.yaml`
- Events: `docs/architecture/05-event-schema.yaml`
- Layer model: `docs/architecture/07-layer-model.json`
- Job model: `docs/architecture/08-processing-job-model.json`
""",
    )
    write(
        ROOT / "packages" / "contracts" / "python" / "gis_contracts" / "__init__.py",
        '''
"""Shared contract helpers for GIS platform services."""

EVENT_SCHEMA_VERSION = 1

__all__ = ["EVENT_SCHEMA_VERSION"]
''',
    )
    write(
        ROOT / "packages" / "contracts" / "python" / "gis_contracts" / "events.py",
        '''
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EventEnvelope(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    version: int = 1
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tenant_id: str | None = None
    producer: str
    correlation_id: str
    causation_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
''',
    )
    write(
        ROOT / "packages" / "contracts" / "python" / "pyproject.toml",
        """
[project]
name = "gis-contracts"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["pydantic>=2.0"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["gis_contracts*"]
""",
    )

    # --- API gateway ---
    api = ROOT / "apps" / "api-gateway"
    write(
        api / "requirements.txt",
        """
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
pydantic>=2.9.0
pydantic-settings>=2.6.0
sqlalchemy[asyncio]>=2.0.36
asyncpg>=0.30.0
alembic>=1.14.0
httpx>=0.28.0
nats-py>=2.9.0
redis>=5.2.0
python-multipart>=0.0.17
opentelemetry-api>=1.28.0
opentelemetry-sdk>=1.28.0
prometheus-client>=0.21.0
ruff>=0.8.0
pytest>=8.3.0
pytest-asyncio>=0.24.0
""",
    )
    write(
        api / "Dockerfile",
        """
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic.ini .
COPY alembic ./alembic

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    )
    write(
        api / "alembic.ini",
        """
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://gis:gis_dev_only@localhost:5432/gis

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
""",
    )
    write(
        api / "alembic" / "env.py",
        '''
from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config.settings import get_settings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = None


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
''',
    )
    write(
        api / "alembic" / "script.py.mako",
        """
\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
\"\"\"
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
""",
    )
    write(
        api / "alembic" / "versions" / ".gitkeep",
        "",
    )

    write(
        api / "app" / "__init__.py",
        '"""API Gateway / BFF for the GIS platform."""\n',
    )
    write(
        api / "app" / "config" / "__init__.py",
        "",
    )
    write(
        api / "app" / "config" / "settings.py",
        '''
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://gis:gis_dev_only@localhost:5432/gis"
    nats_url: str = "nats://localhost:4222"
    valkey_url: str = "redis://localhost:6379/0"
    object_store_endpoint: str = "http://localhost:8333"
    oidc_issuer: str = "http://localhost:8080/realms/gis"
    oidc_client_id: str = "gis-web"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    service_name: str = "api-gateway"


@lru_cache
def get_settings() -> Settings:
    return Settings()
''',
    )

    write(
        api / "app" / "schemas" / "__init__.py",
        "",
    )
    write(
        api / "app" / "schemas" / "common.py",
        '''
from typing import Any

from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorBody
''',
    )
    write(
        api / "app" / "schemas" / "project.py",
        '''
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
''',
    )
    write(
        api / "app" / "schemas" / "dataset.py",
        '''
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
''',
    )
    write(
        api / "app" / "schemas" / "layer.py",
        '''
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
''',
    )
    write(
        api / "app" / "schemas" / "job.py",
        '''
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
''',
    )

    write(
        api / "app" / "api" / "__init__.py",
        "",
    )
    write(
        api / "app" / "api" / "dependencies" / "__init__.py",
        "",
    )
    write(
        api / "app" / "api" / "dependencies" / "auth.py",
        '''
from dataclasses import dataclass
from uuid import UUID

from fastapi import Header, HTTPException, status


@dataclass
class UserContext:
    subject: str
    user_id: UUID | None = None
    tenant_id: UUID | None = None
    roles: list[str] | None = None


async def get_current_user(
    authorization: str | None = Header(default=None),
) -> UserContext:
    """Dev stub: accept missing auth in local development.

    Production services must validate Keycloak JWTs at the boundary.
    """
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
        return UserContext(subject=token[:32] or "anonymous", roles=["developer"])
    # Allow unauthenticated local bootstrap so the skeleton boots without Keycloak.
    return UserContext(subject="local-dev", roles=["developer"])


def require_role(user: UserContext, role: str) -> None:
    roles = user.roles or []
    if role not in roles and "developer" not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
''',
    )

    write(
        api / "app" / "api" / "routes" / "__init__.py",
        "",
    )
    write(
        api / "app" / "api" / "routes" / "health.py",
        '''
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
''',
    )
    write(
        api / "app" / "api" / "routes" / "projects.py",
        '''
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
''',
    )
    write(
        api / "app" / "api" / "routes" / "datasets.py",
        '''
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
''',
    )
    write(
        api / "app" / "api" / "routes" / "jobs.py",
        '''
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
''',
    )
    write(
        api / "app" / "api" / "routes" / "layers.py",
        '''
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
''',
    )
    write(
        api / "app" / "api" / "routes" / "tiles.py",
        '''
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
''',
    )

    for pkg in (
        "application",
        "application/commands",
        "application/queries",
        "application/handlers",
        "domain",
        "domain/entities",
        "domain/value_objects",
        "domain/services",
        "domain/repositories",
        "infrastructure",
        "infrastructure/db",
        "infrastructure/storage",
        "infrastructure/messaging",
        "infrastructure/gis",
    ):
        write(api / "app" / pkg / "__init__.py", "")

    write(
        api / "app" / "domain" / "repositories" / "protocols.py",
        '''
from typing import AsyncIterator, Protocol
from uuid import UUID


class DatasetRepository(Protocol):
    async def get(self, dataset_id: UUID): ...
    async def save(self, dataset) -> None: ...


class ObjectStore(Protocol):
    async def put(self, key: str, stream, content_type: str): ...
    async def get(self, key: str) -> AsyncIterator[bytes]: ...
    async def delete(self, key: str) -> None: ...


class EventBus(Protocol):
    async def publish(self, subject: str, event) -> None: ...
''',
    )

    write(
        api / "app" / "infrastructure" / "messaging" / "nats_bus.py",
        '''
from __future__ import annotations

import json
from typing import Any


class NatsEventBus:
    """Thin placeholder for NATS JetStream publishing."""

    def __init__(self, url: str) -> None:
        self.url = url
        self._nc = None

    async def connect(self) -> None:
        # Connection wired during service bootstrap.
        return None

    async def publish(self, subject: str, event: Any) -> None:
        payload = event.model_dump_json() if hasattr(event, "model_dump_json") else json.dumps(event)
        # Placeholder: log-only until NATS client is connected in runtime bootstrap.
        print(f"[nats-stub] publish {subject}: {payload[:200]}")
''',
    )

    write(
        api / "app" / "main.py",
        '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import datasets, health, jobs, layers, projects, tiles
from app.config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title="Open-Source 2D/3D GIS Platform API",
    version="0.1.0",
    description="API Gateway / BFF — modular domains for day-one development.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(projects.router, prefix="/api/v1")
app.include_router(datasets.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(layers.router, prefix="/api/v1")
app.include_router(tiles.router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": settings.service_name,
        "docs": "/docs",
        "health": "/health/live",
    }
''',
    )

    write(
        api / "tests" / "test_health.py",
        '''
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_live() -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_project() -> None:
    response = client.post(
        "/api/v1/projects",
        json={
            "name": "Demo",
            "description": "Skeleton project",
            "organization_id": "11111111-1111-1111-1111-111111111111",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Demo"
''',
    )

    # --- Workers ---
    for worker in ("metadata_worker", "gdal_worker", "pdal_worker", "tile_worker", "preview_worker"):
        write(
            ROOT / "workers" / worker / "__init__.py",
            "",
        )
        write(
            ROOT / "workers" / worker / "__main__.py",
            f'''
"""{worker.replace("_", "-")} entrypoint.

Consumes NATS jobs, claims work atomically, runs isolated processing, publishes results.
"""
from __future__ import annotations

import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("{worker}")


async def run() -> None:
    logger.info("Starting {worker} (stub). Connect to NATS and claim jobs here.")
    while True:
        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(run())
''',
        )
        write(
            ROOT / "workers" / worker / "Dockerfile",
            f"""
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.9.2

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages || \\
    pip3 install --no-cache-dir -r requirements.txt

COPY . /app/workers/{worker}
WORKDIR /app
CMD ["python3", "-m", "workers.{worker}"]
""",
        )

    write(
        ROOT / "workers" / "requirements.txt",
        """
nats-py>=2.9.0
pydantic>=2.9.0
httpx>=0.28.0
""",
    )
    write(
        ROOT / "workers" / "__init__.py",
        "",
    )
    write(
        ROOT / "workers" / "README.md",
        """
# Workers

Stateless NATS JetStream consumers:

| Worker | Responsibility |
|---|---|
| `metadata_worker` | Format detection, CRS, bounds, checksums |
| `gdal_worker` | Vector/raster conversion (GDAL/OGR) |
| `pdal_worker` | Point cloud indexing (PDAL) |
| `tile_worker` | MVT / raster / terrain tiles |
| `preview_worker` | Preview assets |

Run locally:

```bash
python -m workers.gdal_worker
```
""",
    )

    # --- Web app ---
    web = ROOT / "apps" / "web"
    write(
        web / "package.json",
        json.dumps(
            {
                "name": "gis-web",
                "private": True,
                "version": "0.1.0",
                "type": "module",
                "scripts": {
                    "dev": "vite",
                    "build": "tsc -b && vite build",
                    "preview": "vite preview",
                    "typecheck": "tsc -b --pretty false",
                    "test": "vitest run",
                },
                "dependencies": {
                    "@tanstack/react-query": "^5.62.0",
                    "deck.gl": "^9.0.0",
                    "maplibre-gl": "^4.7.0",
                    "react": "^18.3.1",
                    "react-dom": "^18.3.1",
                    "react-map-gl": "^7.1.7",
                    "zustand": "^5.0.0",
                },
                "devDependencies": {
                    "@types/react": "^18.3.12",
                    "@types/react-dom": "^18.3.1",
                    "@vitejs/plugin-react": "^4.3.4",
                    "typescript": "^5.7.2",
                    "vite": "^6.0.0",
                    "vitest": "^2.1.8",
                },
            },
            indent=2,
        )
        + "\n",
    )
    write(
        web / "tsconfig.json",
        json.dumps(
            {
                "compilerOptions": {
                    "target": "ES2022",
                    "useDefineForClassFields": True,
                    "lib": ["ES2022", "DOM", "DOM.Iterable"],
                    "module": "ESNext",
                    "skipLibCheck": True,
                    "moduleResolution": "bundler",
                    "allowImportingTsExtensions": True,
                    "isolatedModules": True,
                    "moduleDetection": "force",
                    "noEmit": True,
                    "jsx": "react-jsx",
                    "strict": True,
                    "noUnusedLocals": True,
                    "noUnusedParameters": True,
                    "noFallthroughCasesInSwitch": True,
                    "baseUrl": ".",
                    "paths": {"@/*": ["src/*"]},
                },
                "include": ["src"],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        web / "tsconfig.node.json",
        json.dumps(
            {
                "compilerOptions": {
                    "target": "ES2022",
                    "lib": ["ES2023"],
                    "module": "ESNext",
                    "skipLibCheck": True,
                    "moduleResolution": "bundler",
                },
                "include": ["vite.config.ts"],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        web / "vite.config.ts",
        """
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
  },
});
""",
    )
    write(
        web / "index.html",
        """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>GIS Platform</title>
    <link href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css" rel="stylesheet" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
""",
    )
    write(
        web / "Dockerfile",
        """
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 5173
CMD ["nginx", "-g", "daemon off;"]
""",
    )
    write(
        web / "src" / "main.tsx",
        """
import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { App } from "./App";
import "./styles.css";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);
""",
    )
    write(
        web / "src" / "App.tsx",
        """
import { useState } from "react";
import { MapShell } from "./map/MapShell";
import { useUiStore } from "./state/uiStore";

export function App() {
  const mode = useUiStore((s) => s.mode);
  const setMode = useUiStore((s) => s.setMode);
  const [projectName] = useState("Demo Project");

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <strong>GIS Platform</strong>
          <span className="muted"> / {projectName}</span>
        </div>
        <div className="mode-toggle">
          <button className={mode === "2d" ? "active" : ""} onClick={() => setMode("2d")}>
            2D
          </button>
          <button className={mode === "3d" ? "active" : ""} onClick={() => setMode("3d")}>
            3D
          </button>
        </div>
      </header>
      <main className="workspace">
        <aside className="sidebar">
          <h2>Layers</h2>
          <p className="muted">Upload datasets and add layers via the API.</p>
          <ul>
            <li>Basemap</li>
            <li className="muted">No project layers yet</li>
          </ul>
        </aside>
        <section className="map-pane">
          <MapShell mode={mode} />
        </section>
      </main>
    </div>
  );
}
""",
    )
    write(
        web / "src" / "styles.css",
        """
:root {
  color-scheme: light;
  --bg: #0f172a;
  --panel: #111827;
  --text: #e5e7eb;
  --muted: #9ca3af;
  --accent: #38bdf8;
  --border: #1f2937;
  font-family: "Segoe UI", system-ui, sans-serif;
}

* { box-sizing: border-box; }
html, body, #root { height: 100%; margin: 0; }
body { background: var(--bg); color: var(--text); }

.app { display: flex; flex-direction: column; height: 100%; }
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border);
  background: var(--panel);
}
.muted { color: var(--muted); margin-left: 0.35rem; }
.mode-toggle { display: flex; gap: 0.35rem; }
.mode-toggle button {
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
  padding: 0.35rem 0.75rem;
  cursor: pointer;
}
.mode-toggle button.active {
  border-color: var(--accent);
  color: var(--accent);
}
.workspace { display: grid; grid-template-columns: 260px 1fr; flex: 1; min-height: 0; }
.sidebar {
  border-right: 1px solid var(--border);
  padding: 1rem;
  background: #0b1220;
  overflow: auto;
}
.sidebar h2 { margin: 0 0 0.5rem; font-size: 1rem; }
.sidebar ul { list-style: none; padding: 0; margin: 1rem 0 0; }
.sidebar li { padding: 0.4rem 0; border-bottom: 1px solid var(--border); }
.map-pane { position: relative; min-height: 0; }
.map-root { position: absolute; inset: 0; }
.map-fallback {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  background: radial-gradient(circle at 30% 20%, #1e293b, #020617 70%);
}
""",
    )
    write(
        web / "src" / "state" / "uiStore.ts",
        """
import { create } from "zustand";

export type MapMode = "2d" | "3d";

type UiState = {
  mode: MapMode;
  setMode: (mode: MapMode) => void;
};

export const useUiStore = create<UiState>((set) => ({
  mode: "2d",
  setMode: (mode) => set({ mode }),
}));
""",
    )
    write(
        web / "src" / "map" / "types.ts",
        """
export type Bounds = [number, number, number, number];

export type ViewState = {
  longitude: number;
  latitude: number;
  zoom: number;
  pitch?: number;
  bearing?: number;
};

export type VisualizationLayer = {
  id: string;
  type: string;
  visible: boolean;
  opacity: number;
  source: Record<string, unknown>;
  style: Record<string, unknown>;
};

export interface MapController {
  setView(view: ViewState): void;
  fitBounds(bounds: Bounds): void;
  addLayer(layer: VisualizationLayer): void;
  removeLayer(layerId: string): void;
  setLayerVisibility(layerId: string, visible: boolean): void;
}
""",
    )
    write(
        web / "src" / "map" / "MapShell.tsx",
        """
import { useEffect, useRef } from "react";
import type { MapMode } from "../state/uiStore";

type Props = { mode: MapMode };

/**
 * Renderer-neutral shell. MapLibre / deck.gl adapters plug in here.
 * Until map assets load, show an atmospheric fallback so the app boots offline.
 */
export function MapShell({ mode }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    let map: { remove: () => void } | null = null;

    async function boot() {
      if (!containerRef.current) return;
      try {
        const maplibregl = await import("maplibre-gl");
        if (cancelled || !containerRef.current) return;
        map = new maplibregl.Map({
          container: containerRef.current,
          style: {
            version: 8,
            sources: {
              osm: {
                type: "raster",
                tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
                tileSize: 256,
                attribution: "© OpenStreetMap",
              },
            },
            layers: [{ id: "osm", type: "raster", source: "osm" }],
          },
          center: [77.209, 28.6139],
          zoom: 4,
          pitch: mode === "3d" ? 60 : 0,
          bearing: mode === "3d" ? 20 : 0,
        });
      } catch {
        // Keep fallback visible when maplibre cannot initialize.
      }
    }

    void boot();
    return () => {
      cancelled = true;
      map?.remove();
    };
  }, [mode]);

  return (
    <div className="map-root">
      <div ref={containerRef} className="map-root" />
      <div className="map-fallback" aria-hidden>
        <div>
          <div>{mode.toUpperCase()} map shell</div>
          <div className="muted">MapLibre + deck.gl adapters ready for layers</div>
        </div>
      </div>
    </div>
  );
}
""",
    )
    write(
        web / "src" / "api" / "client.ts",
        """
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`API ${response.status}: ${path}`);
  }
  return response.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`API ${response.status}: ${path}`);
  }
  return response.json() as Promise<T>;
}
""",
    )
    write(
        web / "src" / "vite-env.d.ts",
        """
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_OIDC_ISSUER: string;
  readonly VITE_OIDC_CLIENT_ID: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
""",
    )
    write(
        web / "src" / "App.test.ts",
        """
import { describe, expect, it } from "vitest";

describe("scaffold", () => {
  it("boots test runner", () => {
    expect(true).toBe(true);
  });
});
""",
    )

    # --- infra ---
    write(
        ROOT / "infra" / "keycloak" / "README.md",
        """
# Keycloak

Create a `gis` realm with:

- client `gis-web` (public, PKCE)
- client `gis-api` (confidential, for service-to-service if needed)
- roles: `org_admin`, `project_editor`, `project_viewer`

Export the realm JSON here once configured (`gis-realm.json`).
""",
    )
    write(
        ROOT / "infra" / "nats" / "README.md",
        """
# NATS JetStream

Streams (initial):

- `DATASET_EVENTS`
- `PROCESSING_EVENTS`
- `LAYER_EVENTS`

Consumers map 1:1 to workers where possible. Exactly-once semantics are not assumed; workers must be idempotent.
""",
    )

    # --- CI ---
    write(
        ROOT / ".github" / "workflows" / "ci.yml",
        """
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  api:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/api-gateway
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: pytest -q

  web:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/web
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm install
      - run: npm run typecheck
      - run: npm test
      - run: npm run build

  license-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: License policy reminder
        run: |
          echo "Pin dependency versions and run SBOM/license scan before production."
          test -f docs/architecture/09-license-policy.md
""",
    )

    write(
        ROOT / "docs" / "architecture" / "README.md",
        """
# Architecture baseline

Artifacts generated 2026-10-04. Implementation lives in `apps/`, `workers/`, and `packages/`.

See root `README.md` for bootstrap instructions.
""",
    )

    print("Scaffold complete.")


if __name__ == "__main__":
    main()

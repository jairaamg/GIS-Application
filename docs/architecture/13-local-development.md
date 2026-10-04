# Local Development

## 1. Prerequisites

Recommended:

- Git
- Docker Engine / Docker Desktop
- Docker Compose v2
- Node.js LTS
- Python 3.12+
- make
- curl
- jq

For GIS development:

- GDAL
- PDAL

The containerized workers should be the authoritative runtime for integration tests.

## 2. Repository bootstrap

```bash
git clone <repository>
cd gis-platform
cp .env.example .env
```

Never commit `.env`.

## 3. Start infrastructure

```bash
docker compose -f 12-docker-compose.yml up -d postgres nats valkey seaweedfs keycloak
```

Check:

```bash
docker compose -f 12-docker-compose.yml ps
```

## 4. Start API

```bash
cd apps/api-gateway
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API:

```text
http://localhost:8000
```

OpenAPI:

```text
http://localhost:8000/docs
```

## 5. Start frontend

```bash
cd apps/web
npm ci
npm run dev
```

Open:

```text
http://localhost:5173
```

## 6. Environment variables

Minimum:

```text
DATABASE_URL
NATS_URL
VALKEY_URL
OBJECT_STORE_ENDPOINT
OIDC_ISSUER
OIDC_CLIENT_ID
OIDC_CLIENT_SECRET
```

Never put service credentials in frontend variables.

Only `VITE_*` values are public.

## 7. Development flow

```text
1. create project
2. upload dataset
3. validate
4. inspect metadata
5. process
6. create layer
7. open 2D
8. switch 3D
```

## 8. Test

Backend:

```bash
pytest -q
```

Frontend:

```bash
npm test
npm run build
```

Lint:

```bash
ruff check .
ruff format --check .
```

TypeScript:

```bash
npm run typecheck
```

## 9. License scan

Before a pull request:

```bash
make license-scan
make sbom
```

The repository CI must fail on unknown or prohibited licenses.

## 10. Database migration

Development:

```bash
alembic upgrade head
```

Create:

```bash
alembic revision --autogenerate -m "describe change"
```

Never manually edit a production database.

## 11. Worker development

Workers should run locally against NATS:

```bash
python -m workers.gdal_worker
python -m workers.pdal_worker
```

or as Compose services.

## 12. Debugging

Useful endpoints:

```text
GET /health/live
GET /health/ready
GET /metrics
```

NATS monitoring:

```text
http://localhost:8222
```

Keycloak:

```text
http://localhost:8080
```

## 13. Production-like local mode

Use the same container images used in CI:

```bash
docker compose -f 12-docker-compose.yml build
docker compose -f 12-docker-compose.yml up
```

## 14. Reset local state

WARNING: destructive.

```bash
docker compose -f 12-docker-compose.yml down -v
```

Then restart.

## 15. Developer rules

- Never commit secrets.
- Never commit customer datasets.
- Never bypass license CI.
- Never add an unapproved dependency.
- Never access another service's database directly.
- Never put GIS binaries in PostgreSQL.
- Never put millions of features in React state.
- Never execute uploaded files outside sandboxed workers.

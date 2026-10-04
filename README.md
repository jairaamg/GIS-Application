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
# Windows: .venv\Scripts\activate
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

# High-Level Design — Open-Source 2D/3D GIS Platform

## 1. Goals

Build a scalable, modular GIS platform with:

- React + TypeScript frontend
- Python + FastAPI backend
- 2D MapLibre rendering
- 3D deck.gl rendering
- GDAL/OGR and PDAL processing
- PostgreSQL metadata
- SeaweedFS object storage
- NATS JetStream asynchronous processing
- Keycloak identity
- OpenTelemetry/Prometheus observability
- optional AI extension

## 2. Logical architecture

```text
                    +----------------------+
                    | React Web Application|
                    +----------+-----------+
                               |
                       HTTPS / WS / SSE
                               |
                    +----------v-----------+
                    | API Gateway / BFF    |
                    +----------+-----------+
                               |
       +-----------------------+------------------------+
       |             |             |          |         |
       v             v             v          v         v
   Identity       Catalog       Dataset    Project    Search
   Service        Service       Service    Service    Service
                                   |
                                   v
                           Processing Service
                                   |
                                NATS
                                   |
                 +-----------------+----------------+
                 |                 |                |
              GDAL Worker      PDAL Worker     Tile Worker
                 |                 |                |
                 +-----------------+----------------+
                                   |
                         +---------+---------+
                         |                   |
                         v                   v
                    PostgreSQL          SeaweedFS
```

## 3. Services

### API Gateway/BFF
- authentication propagation
- routing
- API aggregation
- rate limiting
- correlation IDs
- WebSocket/SSE routing

### Identity Service
Use Keycloak as the identity provider. Application services validate tokens and enforce resource permissions.

### Catalog Service
Owns dataset metadata, versions, spatial bounds, source/derived assets and catalog queries.

### Dataset Service
Owns upload lifecycle, checksums, object references and dataset state.

### Project Service
Owns projects, saved views, layer membership and project configuration.

### Processing Service
Creates jobs and publishes asynchronous work.

### Search Service
Initially PostgreSQL-backed. Keep an interface for a future dedicated search engine.

### Tile Service
Serves MVT, raster, terrain and 3D assets. It must be independently scalable.

### Worker services
Stateless workers consuming NATS jobs:
- metadata-worker
- gdal-worker
- pdal-worker
- tile-worker
- preview-worker

### AI Gateway
Optional future service. It exposes controlled tools and model-provider adapters.

## 4. Data architecture

```text
Source file
   |
   v
Quarantine object
   |
   v
Validation
   |
   v
Immutable source version
   |
   +--> metadata in PostgreSQL
   |
   +--> derived vector MVT/GeoJSON
   |
   +--> raster COG/tiles
   |
   +--> terrain tiles
   |
   +--> point-cloud EPT/COPC
   |
   +--> 3D Tiles/GLB
```

## 5. Canonical web representations

| Data | Canonical web representation |
|---|---|
| Vector | MVT / GeoJSON |
| Raster | COG / raster tiles |
| Terrain | terrain tiles |
| Point cloud | EPT / COPC |
| 3D model | 3D Tiles / glTF / GLB |
| Metadata | PostgreSQL JSONB |

## 6. Scaling

Stateless API services scale horizontally.

Workers scale independently by workload:

```text
gdal-worker   CPU/memory intensive
pdal-worker   CPU/memory intensive
tile-worker   CPU/IO intensive
preview-worker IO intensive
ai-worker     optional GPU
```

Use queue depth and processing latency as scaling signals.

## 7. Availability

- PostgreSQL: primary + backup/replication strategy.
- SeaweedFS: replicated object storage in production.
- NATS JetStream: clustered in production.
- API services: >=2 replicas for production.
- Tile service: horizontally scalable.
- Workers: disposable and idempotent.

## 8. Security

- OIDC/OAuth2 through Keycloak
- JWT validation at service boundaries
- project/resource RBAC
- object access checks
- upload validation
- isolated processing workers
- network policies
- secret management
- audit events
- dependency/SBOM/license gates

## 9. AI extension

AI must use tools:

```text
AI -> Tool Registry -> Authorization -> Domain API
```

Never:

```text
AI -> direct database
AI -> direct object store
```

AI model providers are adapters, not core dependencies.

## 10. Architectural trade-offs

### Why MapLibre + deck.gl?
MapLibre is the 2D map engine; deck.gl provides GPU-oriented data visualization and 3D layers. The domain layer remains renderer-neutral.

### Why GDAL/PDAL?
They provide broad geospatial ingestion/processing capabilities without forcing browser clients to understand every source format.

### Why NATS?
Processing is naturally asynchronous. A broker decouples upload/API latency from expensive processing.

### Why PostgreSQL?
Strong transactional metadata store with mature operational characteristics.

### Why object storage?
Large GIS binaries and derived assets should not be stored in relational tables.

## 11. Deployment topology

Development:

```text
Docker Compose
```

Production:

```text
Kubernetes
  ingress
  API deployments
  worker deployments
  PostgreSQL HA
  object storage cluster
  NATS cluster
  observability stack
```

## 12. Non-functional targets

Initial targets:

- API p95 < 300 ms for normal metadata operations
- cached tile p95 < 200 ms
- 60 FPS target for normal interactive scenes
- progressive loading for large datasets
- no browser loading of entire large source files
- all processing jobs resumable/retryable where safe

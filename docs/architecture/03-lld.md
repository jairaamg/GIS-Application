# Low-Level Design — Open-Source 2D/3D GIS Platform

## 1. Backend package layout

Each Python service follows:

```text
app/
  api/
    routes/
    dependencies/
  application/
    commands/
    queries/
    handlers/
  domain/
    entities/
    value_objects/
    services/
    repositories/
  infrastructure/
    db/
    storage/
    messaging/
    gis/
  schemas/
  config/
  main.py
tests/
```

Do not share ORM models between services.

Share only versioned contracts/types in a small contracts package.

## 2. Dataset domain

### Dataset

```text
id
project_id
name
description
dataset_type
source_format
status
current_version_id
created_by
created_at
updated_at
```

### DatasetVersion

```text
id
dataset_id
version_number
source_object_key
source_sha256
source_size
detected_format
crs
bbox
min_z
max_z
metadata_json
status
created_at
```

### Asset

```text
id
dataset_version_id
asset_type
object_key
content_type
size_bytes
sha256
metadata_json
created_at
```

## 3. Layer domain

```text
Layer
  id
  project_id
  dataset_version_id
  name
  layer_type
  visible
  opacity
  min_zoom
  max_zoom
  z_index
  style_json
  source_json
  created_at
  updated_at
```

Layer types:

```text
VECTOR
RASTER
TERRAIN
POINT_CLOUD
MESH
MODEL_3D
BUILDING
HEATMAP
ELEVATION
ANNOTATION
```

## 4. Repository interfaces

```python
class DatasetRepository(Protocol):
    async def get(self, dataset_id: UUID) -> Dataset | None: ...
    async def save(self, dataset: Dataset) -> None: ...
```

```python
class ObjectStore(Protocol):
    async def put(self, key: str, stream, content_type: str) -> ObjectRef: ...
    async def get(self, key: str) -> AsyncIterator[bytes]: ...
    async def delete(self, key: str) -> None: ...
```

```python
class EventBus(Protocol):
    async def publish(self, subject: str, event: EventEnvelope) -> None: ...
```

## 5. Upload sequence

```text
React
 |
 | POST /datasets
 v
Dataset API
 |
 | create dataset/version
 v
PostgreSQL
 |
 | signed/direct upload target
 v
SeaweedFS
 |
 | upload complete
 v
Dataset API
 |
 | dataset.uploaded
 v
NATS
 |
 v
Validation worker
 |
 +-- format detection
 +-- checksum
 +-- CRS
 +-- bounds
 +-- metadata
 |
 v
dataset.validated
 |
 v
Processing worker
```

## 6. Job execution

A worker must:

1. consume message
2. validate event schema
3. claim job atomically
4. update RUNNING
5. create isolated workspace
6. execute tool with limits
7. validate output
8. upload derived assets
9. commit metadata
10. mark SUCCEEDED
11. publish completion event

On failure:

```text
transient -> retry with backoff
permanent -> FAILED
```

## 7. Idempotency

Use:

```text
job_id
dataset_version_id
operation
processor_version
```

as deterministic processing identity.

A repeated job must either return the existing successful result or safely replace the same derived asset version.

## 8. Processing isolation

Every GIS process runs in a restricted worker/container:

```text
CPU quota
memory quota
disk quota
timeout
non-root user
read-only base filesystem
temporary writable workspace
restricted network
```

## 9. API service conventions

HTTP status:

```text
200 success
201 created
202 accepted for async job
204 deleted
400 validation
401 unauthenticated
403 unauthorized
404 not found
409 conflict
413 payload too large
422 semantic validation
429 rate limited
500 internal
503 dependency unavailable
```

Error body:

```json
{
  "error": {
    "code": "DATASET_NOT_READY",
    "message": "Dataset has not completed processing.",
    "request_id": "req_123",
    "details": {}
  }
}
```

## 10. Frontend rendering architecture

```text
Project
  |
  +-- LayerModel[]
          |
          +-- renderer adapter
                |
                +-- MapLibre adapter
                +-- deck.gl adapter
```

React should own UI state, not millions of GIS objects.

Use TanStack Query for server state and a small client state store for UI state.

## 11. Map controller

```typescript
interface MapController {
  setView(view: ViewState): void;
  fitBounds(bounds: Bounds): void;
  addLayer(layer: VisualizationLayer): void;
  removeLayer(layerId: string): void;
  setLayerVisibility(layerId: string, visible: boolean): void;
}
```

## 12. Elevation abstraction

```typescript
interface ElevationSource {
  id: string;
  minZoom?: number;
  maxZoom?: number;
  getElevation(lon: number, lat: number): Promise<number | null>;
}
```

Keep vertical datum metadata with the dataset.

## 13. Tile request flow

```text
Browser
 -> Tile API
 -> cache
 -> object store
```

For database-backed vector tiles:

```text
Browser
 -> Tile API
 -> spatial query
 -> MVT encoding
 -> cache
```

## 14. Event contract

All events have:

```text
event_id
event_type
version
timestamp
correlation_id
tenant_id
producer
payload
```

Events are immutable.

## 15. Database access

Services use SQLAlchemy + async PostgreSQL driver.

Rules:

- no cross-service table access
- no database credentials in frontend
- transactions around state changes
- migrations through Alembic
- indexes documented with query purpose

## 16. Cache

Valkey keys:

```text
tile:{hash}
dataset:metadata:{id}
job:status:{id}
project:{id}
```

TTL must be explicit.

## 17. Authorization

Every resource lookup follows:

```text
authenticate
 -> identify tenant/project
 -> authorize action
 -> execute query
```

Never fetch an object and authorize later if the query can enforce access.

## 18. AI tools

Example tool:

```python
async def find_datasets(
    user_context: UserContext,
    query: DatasetSearchQuery
) -> list[DatasetSummary]:
    authorize(user_context, "dataset:read")
    ...
```

AI receives structured results, not unrestricted SQL/database access.

## 19. Testing

Unit:
- domain services
- validation
- style rules
- authorization

Integration:
- PostgreSQL
- NATS
- object store
- GDAL
- PDAL

E2E:
- upload -> process -> layer -> 2D -> 3D

Performance:
- MVT
- large point clouds
- large raster
- terrain
- 3D Tiles

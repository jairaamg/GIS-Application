# System Context — Open-Source 2D/3D GIS Platform

## 1. Purpose

A web platform for ingesting, processing, cataloguing, serving, analysing and visualizing heterogeneous 2D and 3D GIS datasets.

Primary user journeys:

1. Upload a GIS dataset.
2. Automatically validate and inspect it.
3. Extract CRS, bounds, geometry, dimensions and elevation metadata.
4. Convert it to browser-optimized representations.
5. Add it to a project as a layer.
6. View the same project in 2D or 3D.
7. Query, style, measure and analyse data.
8. Later, ask an AI assistant to perform authorized GIS operations.

## 2. System boundary

### Inside the platform

- React/TypeScript web application
- FastAPI APIs
- identity and access management
- dataset/catalog/project metadata
- upload and object storage
- GDAL/OGR processing
- PDAL point-cloud processing
- tile generation and serving
- 2D/3D visualization
- asynchronous jobs/events
- observability/audit
- optional AI gateway

### Outside the platform

- end-user browsers
- source GIS files
- external basemaps, if enabled
- external identity providers, if later integrated
- optional external AI providers, if explicitly approved

## 3. Context diagram

```text
+-------------------+
| GIS User / Admin  |
+---------+---------+
          |
          | HTTPS / WebSocket
          v
+-----------------------------+
| React Web Application       |
| MapLibre + deck.gl          |
+-------------+---------------+
              |
              v
+-----------------------------+
| API Gateway / BFF           |
| FastAPI                     |
+-------------+---------------+
              |
     +--------+---------+-------------------+
     |                  |                   |
     v                  v                   v
+---------+       +-----------+       +-----------+
| Identity|       | Catalog / |       | Dataset / |
| Service |       | Project   |       | Job APIs  |
+---------+       +-----------+       +-----------+
                         |
                         v
                 +---------------+
                 | NATS          |
                 | JetStream     |
                 +-------+-------+
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
     +---------+    +---------+    +----------+
     | GDAL    |    | PDAL    |    | Tile     |
     | Worker  |    | Worker  |    | Worker   |
     +----+----+    +----+----+    +----+-----+
          |              |              |
          +--------------+--------------+
                         |
              +----------+----------+
              |                     |
              v                     v
        +-----------+         +-----------+
        | PostgreSQL|         | SeaweedFS |
        | metadata  |         | objects   |
        +-----------+         +-----------+

Optional future:
React -> AI Gateway -> GIS Tools -> same authorization -> same services
```

## 4. External actors

### Viewer
Can open projects and view permitted layers.

### Analyst
Can query, measure, style, filter and create derived layers.

### Editor
Can upload datasets and modify project/layer configuration.

### Project Admin
Can manage project membership and data.

### System Admin
Can manage platform configuration, jobs and operational controls.

## 5. Key architectural principles

- Browser renders optimized representations, not arbitrary source formats.
- Heavy processing is asynchronous.
- Services communicate through explicit APIs/events.
- Object storage holds binaries; PostgreSQL holds metadata/state.
- Rendering is behind a domain-level layer abstraction.
- AI is optional and never bypasses authorization.
- All production dependencies are subject to automated license/SBOM policy.
- Source data is treated as untrusted.
- Every long-running operation is represented as a job.
- Every dataset has immutable versions.

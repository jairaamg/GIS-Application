# ADR-001: Microservices with Explicit Domain Boundaries

## Status
Accepted

## Decision
Use independently deployable FastAPI services for identity integration, catalog, dataset, project, processing, search and tile concerns.

## Rationale
GIS processing has different scaling characteristics from metadata APIs. Separating workers prevents heavy GDAL/PDAL operations from blocking API workloads.

## Consequences
Positive:
- independent scaling
- fault isolation
- clearer ownership
- asynchronous processing

Negative:
- operational complexity
- distributed tracing required
- contract/version management required

## Guardrail
Do not split every domain into a service on day one. A service must have an independent scaling, security or lifecycle reason.

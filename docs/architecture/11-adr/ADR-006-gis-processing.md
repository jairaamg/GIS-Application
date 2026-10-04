# ADR-006: GDAL/OGR and PDAL as Processing Engines

## Status
Accepted

## Decision
Use GDAL/OGR for broad raster/vector processing and PDAL for point-cloud processing.

## Rationale
Both are mature geospatial processing ecosystems and avoid implementing format parsers in application code.

## Consequences
Native binary dependencies require controlled container builds, version pinning and SBOM/license scanning.

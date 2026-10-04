# ADR-003: Canonical Web Representations

## Status
Accepted

## Decision
Normalize source datasets into a small set of web representations: MVT/GeoJSON, COG/raster tiles, terrain tiles, EPT/COPC and 3D Tiles/glTF.

## Rationale
Browser support for every source GIS format is impractical.

## Consequences
Processing time and derived storage increase, but frontend complexity and runtime risk decrease.

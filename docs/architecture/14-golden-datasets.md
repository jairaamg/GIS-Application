# Golden Dataset Test Suite

## 1. Purpose

The golden dataset suite prevents regressions in:

- ingestion
- metadata extraction
- CRS handling
- geometry handling
- elevation
- tiling
- point-cloud processing
- 2D rendering
- 3D rendering
- performance

## 2. Dataset rules

Golden datasets must be:

- legally distributable for project testing
- small enough for CI where possible
- versioned
- checksum pinned
- accompanied by license/provenance metadata

Never add a third-party dataset merely because it is downloadable.

## 3. Required dataset matrix

| ID | Dataset | Format | Purpose |
|---|---|---|---|
| G01 | points-small | GeoJSON | basic vector |
| G02 | polygons-small | GeoJSON | polygon rendering |
| G03 | lines-small | GeoJSON | line rendering |
| G04 | vector-large | MVT | tile performance |
| G05 | vector-package | GeoPackage | source ingestion |
| G06 | vector-shape | Shapefile | legacy vector ingestion |
| G07 | raster-dem | GeoTIFF | elevation |
| G08 | raster-cog | COG | cloud-optimized raster |
| G09 | lidar-small | LAS | point cloud |
| G10 | lidar-compressed | LAZ | point cloud |
| G11 | lidar-copc | COPC | hierarchical point cloud |
| G12 | model-small | GLB | 3D model |
| G13 | tiles-small | 3D Tiles | 3D tiles |
| G14 | geojson-z | GeoJSON-Z | elevation-aware vector |
| G15 | multispectral | GeoTIFF | multiband raster |

## 4. Golden metadata

For every dataset store:

```text
filename
format
sha256
license
source
expected_crs
expected_bbox
expected_min_z
expected_max_z
expected_geometry_type
expected_asset_types
```

## 5. CI tests

### Ingestion

```text
file detected
format detected
checksum calculated
CRS detected
bounds calculated
metadata persisted
```

### Vector

```text
feature count
geometry validity
tile generation
style rendering
picking
```

### Raster

```text
dimensions
band count
NoData
CRS
min/max
tile generation
```

### Elevation

```text
min elevation
max elevation
terrain generation
vertical metadata preserved
```

### Point cloud

```text
point count
bounds
classification
LOD hierarchy
progressive loading
```

### 3D

```text
model metadata
bounding box
asset validation
3D tile traversal
```

## 6. Performance benchmarks

Record:

```text
ingest time
metadata extraction time
processing time
derived asset size
first tile latency
p95 tile latency
browser first render
frame rate
peak browser memory
```

## 7. Regression policy

A release cannot silently change:

- CRS interpretation
- axis order
- elevation units
- vertical datum metadata
- feature counts
- geometry validity
- tile bounds

Any intentional change requires an ADR or test update.

## 8. Test data repository

Recommended layout:

```text
tests/data/golden/
  G01-points-small/
    data.geojson
    manifest.json
  G02-polygons-small/
    data.geojson
    manifest.json
  ...
```

## 9. Manifest example

```json
{
  "id": "G07",
  "name": "raster-dem",
  "format": "GeoTIFF",
  "sha256": "<sha256>",
  "license": "<verified-license>",
  "source": "<verified-source>",
  "expected": {
    "crs": "EPSG:4326",
    "bands": 1,
    "minZ": 100,
    "maxZ": 500
  }
}
```

Do not invent expected values; calculate and review them when the dataset is onboarded.

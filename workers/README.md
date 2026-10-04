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

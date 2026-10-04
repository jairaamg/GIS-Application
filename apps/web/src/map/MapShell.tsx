import { useEffect, useRef } from "react";
import type { MapMode } from "../state/uiStore";

type Props = { mode: MapMode };

/**
 * Renderer-neutral shell. MapLibre / deck.gl adapters plug in here.
 * Until map assets load, show an atmospheric fallback so the app boots offline.
 */
export function MapShell({ mode }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    let map: { remove: () => void } | null = null;

    async function boot() {
      if (!containerRef.current) return;
      try {
        const maplibregl = await import("maplibre-gl");
        if (cancelled || !containerRef.current) return;
        map = new maplibregl.Map({
          container: containerRef.current,
          style: {
            version: 8,
            sources: {
              osm: {
                type: "raster",
                tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
                tileSize: 256,
                attribution: "© OpenStreetMap",
              },
            },
            layers: [{ id: "osm", type: "raster", source: "osm" }],
          },
          center: [77.209, 28.6139],
          zoom: 4,
          pitch: mode === "3d" ? 60 : 0,
          bearing: mode === "3d" ? 20 : 0,
        });
      } catch {
        // Keep fallback visible when maplibre cannot initialize.
      }
    }

    void boot();
    return () => {
      cancelled = true;
      map?.remove();
    };
  }, [mode]);

  return (
    <div className="map-root">
      <div ref={containerRef} className="map-root" />
      <div className="map-fallback" aria-hidden>
        <div>
          <div>{mode.toUpperCase()} map shell</div>
          <div className="muted">MapLibre + deck.gl adapters ready for layers</div>
        </div>
      </div>
    </div>
  );
}

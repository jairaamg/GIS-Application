import { useState } from "react";
import { MapShell } from "./map/MapShell";
import { useUiStore } from "./state/uiStore";

export function App() {
  const mode = useUiStore((s) => s.mode);
  const setMode = useUiStore((s) => s.setMode);
  const [projectName] = useState("Demo Project");

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <strong>GIS Platform</strong>
          <span className="muted"> / {projectName}</span>
        </div>
        <div className="mode-toggle">
          <button className={mode === "2d" ? "active" : ""} onClick={() => setMode("2d")}>
            2D
          </button>
          <button className={mode === "3d" ? "active" : ""} onClick={() => setMode("3d")}>
            3D
          </button>
        </div>
      </header>
      <main className="workspace">
        <aside className="sidebar">
          <h2>Layers</h2>
          <p className="muted">Upload datasets and add layers via the API.</p>
          <ul>
            <li>Basemap</li>
            <li className="muted">No project layers yet</li>
          </ul>
        </aside>
        <section className="map-pane">
          <MapShell mode={mode} />
        </section>
      </main>
    </div>
  );
}

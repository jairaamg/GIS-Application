# ADR-002: MapLibre + deck.gl Rendering

## Status
Accepted

## Decision
Use MapLibre GL JS for map-centric 2D rendering and deck.gl for GPU-oriented data/3D rendering.

## Rationale
The combination separates map navigation/style concerns from large-scale custom visualization.

## Consequences
The application requires a renderer-neutral layer model so the domain does not depend on either library.

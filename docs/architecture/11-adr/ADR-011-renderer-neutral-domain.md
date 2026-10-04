# ADR-011: Renderer-Neutral Layer Domain

## Status
Accepted

## Decision
The domain model represents datasets/layers/styles without depending on MapLibre or deck.gl classes.

## Rationale
Rendering engines may change. Domain concepts should remain stable.

## Consequences
Adapters are required but replacement of the renderer does not require rewriting dataset/project services.

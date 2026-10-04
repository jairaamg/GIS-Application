# ADR-005: NATS JetStream for Async Processing

## Status
Accepted

## Decision
Use NATS JetStream for dataset and processing events.

## Rationale
GIS conversion and tiling are long-running and should not be tied to HTTP request latency.

## Consequences
Consumers must be idempotent and event contracts must be versioned.

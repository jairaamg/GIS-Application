# ADR-004: Object Storage for GIS Assets

## Status
Accepted

## Decision
Store original and derived GIS binaries in object storage; store metadata and references in PostgreSQL.

## Rationale
Large binary assets do not belong in relational rows.

## Consequences
Object lifecycle, checksums and retention policies become first-class concerns.

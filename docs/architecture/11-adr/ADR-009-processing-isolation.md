# ADR-009: Sandbox GIS Processing

## Status
Accepted

## Decision
Uploaded GIS files are processed only in isolated, resource-limited worker environments.

## Rationale
GIS parsers process complex untrusted binary inputs and can be CPU/memory intensive.

## Consequences
Workers need resource policies, temporary storage and operational monitoring.

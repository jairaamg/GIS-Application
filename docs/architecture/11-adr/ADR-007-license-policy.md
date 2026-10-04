# ADR-007: Permissive-Only Dependency Policy

## Status
Accepted

## Decision
Production dependencies must use an approved permissive-license allowlist. Unknown and copyleft licenses are blocked by default.

## Rationale
The product requirement prioritizes low licensing and redistribution risk.

## Consequences
Some otherwise useful GIS components may be excluded. Each release needs SBOM and notice generation.

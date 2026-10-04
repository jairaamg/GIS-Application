# ADR-010: Monorepo for Initial Development

## Status
Accepted

## Decision
Start with one repository containing apps, workers, contracts and infrastructure. Deploy services independently.

## Rationale
A monorepo makes API/event contracts, license gates and integration tests easier to coordinate while the architecture is still evolving.

## Consequences
Repository tooling must enforce ownership and boundaries. The repository must not become a shared-database monolith.

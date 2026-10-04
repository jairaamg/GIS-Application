# ADR-008: AI as an Optional Tool-Based Plane

## Status
Accepted

## Decision
AI is isolated behind an AI Gateway and Tool Registry. AI uses authorized domain tools rather than direct data access.

## Rationale
This permits future local or external models without changing the GIS core and prevents model providers from becoming architectural dependencies.

## Consequences
Tool contracts must be stable and every AI action must be auditable.

# Threat Model — 2D/3D GIS Platform

## 1. Scope

Threat model covers:

- browser
- API gateway
- FastAPI services
- object storage
- PostgreSQL
- NATS
- GIS workers
- tile service
- identity
- future AI tools

## 2. Assets

High-value assets:

- source datasets
- derived datasets
- project metadata
- credentials/tokens
- user identity
- authorization data
- processing infrastructure
- audit records
- AI tool permissions

## 3. Trust boundaries

```text
Internet
  |
  | untrusted
  v
Ingress
  |
  +---- Browser
  |
  v
API boundary
  |
  +---- service network
  |
  v
Processing boundary
  |
  +---- untrusted uploaded files
```

## 4. Major threats

### T1: Malicious GIS file

Risk:
- parser vulnerability
- decompression bomb
- malformed geometry
- resource exhaustion

Controls:
- MIME + magic-byte detection
- file size limits
- archive limits
- isolated worker
- CPU/memory/disk/time limits
- no root
- restricted network
- patched GDAL/PDAL
- quarantine before processing

### T2: SSRF through GIS data

Risk:
Some formats or processing operations may reference external resources.

Controls:
- disable worker network by default
- allowlist required endpoints
- never permit arbitrary URL fetching
- sanitize metadata
- reject unexpected remote references

### T3: Unauthorized dataset access

Controls:
- tenant/project RBAC
- authorization before object-key resolution
- object keys are opaque
- signed URLs short-lived
- audit downloads

### T4: Token theft

Controls:
- short-lived access tokens
- secure browser storage strategy
- HTTPS
- refresh token controls
- token audience validation
- CSP

### T5: SQL injection

Controls:
- parameterized SQL
- ORM/query builder
- no string-built SQL
- least-privilege DB users

### T6: Object storage abuse

Controls:
- per-user/project quotas
- content-length limits
- checksum
- lifecycle policies
- private buckets/collections
- no public object store

### T7: NATS message forgery

Controls:
- authenticated service connections
- subject permissions
- TLS in production
- schema validation
- event IDs
- idempotent consumers

### T8: Job denial of service

Controls:
- queue limits
- quotas
- priority limits
- per-project concurrency
- timeout
- resource limits

### T9: Path traversal

Controls:
- never derive filesystem path directly from filename
- generate object keys
- canonicalize paths
- use isolated workspaces

### T10: Malicious 3D model

Controls:
- sanitize/validate assets
- isolate conversion
- restrict resource usage
- validate output
- never execute embedded content

### T11: XSS through GIS metadata

Controls:
- escape rendered metadata
- no dangerouslySetInnerHTML
- Content Security Policy
- sanitize HTML if HTML is intentionally supported

### T12: AI prompt injection

Future AI risk:
A dataset description/feature attribute may contain instructions intended to manipulate the AI.

Controls:
- treat all GIS text as untrusted
- AI cannot elevate permissions
- tools enforce authorization
- tool allowlist
- structured outputs
- no arbitrary code execution
- confirmation for destructive operations

### T13: AI data exfiltration

Controls:
- AI receives only authorized data
- field-level minimization
- tool-specific scopes
- configurable model routing
- optional local model
- audit tool calls

### T14: Supply-chain compromise

Controls:
- pinned versions
- SBOM
- dependency scanning
- signature verification where available
- reproducible/controlled builds
- license allowlist
- minimal runtime images

## 5. Security principles

- least privilege
- deny by default
- defense in depth
- zero trust between services
- untrusted input isolation
- immutable dataset versions
- auditable privileged actions
- no direct AI database access

## 6. Security acceptance criteria

A release is blocked if:

- critical vulnerability exists without approved exception
- unknown dependency license exists
- anonymous dataset access is possible
- uploaded file can execute with worker privileges
- service can access another tenant's data
- AI can bypass authorization

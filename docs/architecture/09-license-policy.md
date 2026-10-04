# Open-Source License and Dependency Policy

## 1. Intent

The platform is designed to minimize licensing, royalty and vendor-lock-in risk.

This document is an engineering policy, not legal advice. No software architecture can guarantee zero legal obligations. Even permissively licensed software may require preservation of notices/attributions, and datasets, basemaps, fonts, imagery and models can have independent terms.

## 2. Default approved license families

The default allowlist is:

- MIT
- BSD-2-Clause
- BSD-3-Clause
- Apache-2.0
- ISC
- 0BSD
- Zlib
- X11
- PostgreSQL License
- Python Software Foundation License
- PSF-2.0

The compliance owner may explicitly approve additional SPDX identifiers after review.

## 3. Default prohibited licenses

Do not introduce dependencies under:

- GPL-2.0
- GPL-3.0
- AGPL
- LGPL
- SSPL
- BSL
- Elastic License
- Commons Clause
- proprietary licenses
- source-available licenses
- custom/unknown licenses

This is intentionally conservative.

## 4. Core technology verification

At architecture approval time, the following core projects have permissive licenses according to their upstream repositories:

| Component | License |
|---|---|
| React | MIT |
| FastAPI | MIT |
| MapLibre GL JS | BSD-3-Clause |
| deck.gl | MIT |
| Valkey | BSD-3-Clause |

MapLibre's repository also contains notices for third-party components; therefore the compliance process must inspect the complete dependency tree rather than assuming one license covers all transitive code.

GDAL/OGR, PDAL, NATS, SeaweedFS, Keycloak and all other runtime dependencies must be pinned to reviewed versions and included in the generated SBOM before release.

## 5. Runtime image policy

Do not treat a container image's repository name as sufficient licensing evidence.

For every production image record:

- image digest
- source repository
- Dockerfile/source
- OS packages
- language packages
- licenses
- SBOM
- vulnerability report

Prefer building organization-owned images from pinned source/package versions.

## 6. Data license policy

The software license policy does not make third-party GIS data free to use.

Each imported dataset must carry:

```text
data_source
license
attribution_required
usage_restrictions
redistribution_allowed
commercial_use_allowed
provenance
```

External basemaps and imagery are NOT automatically approved.

## 7. Dependency gate

CI must fail if:

```text
license == UNKNOWN
OR license not in approved_allowlist
OR dependency has unapproved source
OR required notice is missing
```

## 8. SBOM

Generate SPDX or CycloneDX SBOMs for:

- frontend
- each Python service
- each worker image
- infrastructure images
- production deployment bundle

Store SBOMs with release artifacts.

## 9. Version pinning

Production dependencies must use exact versions/digests.

Avoid:

```text
latest
*
floating git branches
unbounded dependency ranges
```

## 10. Notices

For BSD/Apache/MIT dependencies, preserve required copyright/license notices in the distribution where applicable.

Generate a NOTICE bundle during release.

## 11. Review process

Any new dependency requires:

1. business justification
2. upstream repository
3. exact version
4. SPDX license
5. transitive dependency report
6. security scan
7. license gate
8. owner approval

## 12. Release gate

No production release unless:

```text
SBOM generated
license scan passed
security scan passed
notices generated
source versions pinned
dataset licenses reviewed
```

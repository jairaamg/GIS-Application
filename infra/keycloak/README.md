# Keycloak

Create a `gis` realm with:

- client `gis-web` (public, PKCE)
- client `gis-api` (confidential, for service-to-service if needed)
- roles: `org_admin`, `project_editor`, `project_viewer`

Export the realm JSON here once configured (`gis-realm.json`).

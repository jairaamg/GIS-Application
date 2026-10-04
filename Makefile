.PHONY: infra-up infra-down api web test lint license-scan sbom migrate

infra-up:
	docker compose up -d postgres nats valkey seaweedfs keycloak

infra-down:
	docker compose down

api:
	cd apps/api-gateway && python -m uvicorn app.main:app --reload --port 8000

web:
	cd apps/web && npm run dev

test:
	cd apps/api-gateway && pytest -q
	cd apps/web && npm test -- --run

lint:
	cd apps/api-gateway && ruff check . && ruff format --check .
	cd apps/web && npm run typecheck

migrate:
	cd apps/api-gateway && alembic upgrade head

license-scan:
	@echo "Run SBOM/license scan in CI against pinned dependency versions."

sbom:
	@mkdir -p sbom && echo "Generate SBOM artifacts into ./sbom"

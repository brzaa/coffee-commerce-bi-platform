.PHONY: setup up pipeline metabase-setup logs down dbt-build dbt-test

setup:
	cp .env.example .env

up:
	docker compose up -d warehouse metabase nginx

pipeline:
	docker compose --profile pipeline run --rm pipeline

metabase-setup:
	docker compose --profile setup run --rm metabase-setup

logs:
	docker compose logs -f --tail=200 warehouse metabase nginx

down:
	docker compose down

dbt-build:
	docker compose --profile pipeline run --rm pipeline dbt build --project-dir /app/analytics --profiles-dir /app/analytics

dbt-test:
	docker compose --profile pipeline run --rm pipeline dbt test --project-dir /app/analytics --profiles-dir /app/analytics

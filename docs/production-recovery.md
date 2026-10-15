# Product API — Production Recovery Runbook

## 1. Current architecture

- EC2: Docker Compose, FastAPI, Celery, Redis, Flower
- Nginx: Reverse proxy to FastAPI
- Database: AWS RDS PostgreSQL
- Configuration: AWS SSM Parameter Store

## 2. Known-good image

Image: product_api-fastapi:day11-known-good

This tag is stored locally on EC2.
It does not provide disaster recovery if local Docker storage is lost.

## 3. Pre-deployment checks

- Confirm the current application is healthy.
- Record the running FastAPI image ID.
- Preserve the known-good image before rebuilding.
- Verify database migration backward compatibility.
- Ensure the recovery image supports current SSM configuration.

## 4. Health verification

docker inspect product_api --format '{{.State.Health.Status}}'

curl -fsS --max-time 5 http://127.0.0.1/health/ready

Expected response:
{"status":"ready"}

## 5. Recovery command — manual approval required

Do not execute until a failed deployment is confirmed
and database compatibility has been reviewed.

docker compose \
  -f docker-compose.yml \
  -f docker-compose.recovery.yml \
  up -d --no-deps --no-build fastapi

This recreates only the FastAPI service.
A brief interruption may occur.

Before executing recovery, validate the merged Compose configuration:

docker compose \
  -f docker-compose.yml \
  -f docker-compose.recovery.yml \
  config --quiet

Confirm the selected image, health check, environment configuration,
and port mappings are compatible with the known-good release.

## 6. Post-recovery verification

- Confirm the running image matches the known-good image ID.
- Confirm Docker health status becomes healthy.
- Confirm /health/ready returns HTTP 200.
- Verify critical application endpoints.
- Review FastAPI and Nginx error logs.

## 7. Recovery limitations

- The recovery image is stored only on this EC2 instance.
- The local tag must not be overwritten or deleted.
- The September 30 rollback image is not compatible with
  the current SSM-based configuration.
- Application rollback does not reverse database migrations.
- This procedure does not restore lost RDS data.
- No automatic rollback is configured.

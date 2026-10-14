#!/usr/bin/env bash

set -u

HEALTH_URL="${HEALTH_URL:-http://127.0.0.1/health/ready}"

HTTP_CODE=$(curl \
  --silent \
  --output /dev/null \
  --write-out "%{http_code}" \
  --max-time 5 \
  "$HEALTH_URL")

CURL_EXIT_CODE=$?
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [ "$CURL_EXIT_CODE" -eq 0 ] && [ "$HTTP_CODE" = "200" ]; then
    echo "$TIMESTAMP SUCCESS health_ready HTTP=$HTTP_CODE"
    exit 0
else
    echo "$TIMESTAMP FAILURE health_ready HTTP=$HTTP_CODE curl_exit=$CURL_EXIT_CODE"
    exit 1
fi

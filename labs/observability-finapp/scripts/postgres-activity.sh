#!/usr/bin/env bash

set -euo pipefail

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

POSTGRES_USER="${POSTGRES_USER:-sreadmin}"
POSTGRES_DB="${POSTGRES_DB:-production}"

docker compose exec postgres \
  psql \
  -U "${POSTGRES_USER}" \
  -d "${POSTGRES_DB}" \
  -c "
SELECT
  pid,
  state,
  wait_event_type,
  wait_event,
  query
FROM pg_stat_activity
WHERE state <> 'idle';
"

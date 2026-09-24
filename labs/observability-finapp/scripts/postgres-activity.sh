#!/usr/bin/env bash

set -euo pipefail

docker compose exec postgres   psql   -U "${POSTGRES_USER}"   -d "${POSTGRES_DB}"   -c "
SELECT
  pid,
  state,
  wait_event_type,
  wait_event,
  query
FROM pg_stat_activity
WHERE state <> 'idle';
"

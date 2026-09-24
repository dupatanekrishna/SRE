# Query Cheat Sheet

## Prometheus

```promql
http_server_duration_milliseconds_count{http_target="/db"}
```

```promql
count_over_time(http_server_duration_milliseconds_count{http_target="/db"}[2m])
```

```promql
rate(http_server_duration_milliseconds_count{http_target="/db"}[2m])
```

```promql
sum(rate(http_server_duration_milliseconds_sum{http_target="/db"}[1m]))
/
sum(rate(http_server_duration_milliseconds_count{http_target="/db"}[1m]))
```

CPU:
```promql
100 - (
  avg by (instance) (
    rate(node_cpu_seconds_total{mode="idle"}[5m])
  ) * 100
)
```

Memory:
```promql
100 * (
  1 -
  node_memory_MemAvailable_bytes /
  node_memory_MemTotal_bytes
)
```

## Loki

```logql
{service_name="finapp-backend"}
```

```logql
{service_name="finapp-backend"} |= "GET /db"
```

## PostgreSQL

```sql
SELECT pid, state, wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE state <> 'idle';
```

```sql
SELECT pg_blocking_pids(<blocked_pid>);
```

## rate() lesson

If a counter is not increasing:

```text
90
90
90
90
```

then its rate is zero. If both histogram sum rate and count rate are zero, the average latency division can become NaN. Keep traffic flowing while testing a rate-based latency alert.

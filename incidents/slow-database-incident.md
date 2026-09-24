# Incident Case Study: Slow Database Request

## Symptom

The `/db` endpoint latency increased from a few milliseconds to about 3 seconds.

## Injection

The test query was intentionally changed to:

```sql
SELECT version(), pg_sleep(3);
```

## Detection

Prometheus observed average latency around:

```text
3018 ms
```

The alert condition was:

```text
average /db latency > 1000 ms for 30 seconds
```

The alert moved to `PENDING` and then `FIRING`.

## Investigation

### Metrics
Prometheus showed elevated request latency.

### Traces
Tempo/OpenTelemetry showed:

```text
GET /db
  └── SELECT
```

The SQL span identified the slow operation.

### PostgreSQL
`pg_stat_activity` showed the backend waiting in:

```text
wait_event_type = Timeout
wait_event      = PgSleep
```

with the query:

```sql
SELECT version(), pg_sleep(3);
```

## Mitigation

The query was restored to:

```sql
SELECT version();
```

## Verification

After mitigation:

- application latency returned to normal
- Prometheus latency dropped below threshold
- the alert stopped firing

## RCA structure

```text
Impact
Detection
Timeline
Root cause
Mitigation
Recovery validation
Preventive actions
```

## SRE lesson

A successful incident response does not stop at fixing the symptom. Recovery must be validated using the same signals that detected the incident.

# Observability + Alerting Deep Dive

## Lab components

- Flask backend
- PostgreSQL 17
- OpenTelemetry Python SDK
- OpenTelemetry Collector
- Prometheus
- Grafana
- Loki
- Tempo
- Node Exporter
- Alertmanager
- Slack incident channel

## Telemetry pipeline

```text
Flask application
  ↓ OTLP HTTP :4318
OpenTelemetry Collector
  ├── metrics → Prometheus exporter :8889
  ├── logs    → Loki
  └── traces  → Tempo

Prometheus scrapes :8889
Grafana queries Prometheus/Loki/Tempo
Prometheus forwards alerts to Alertmanager
Alertmanager sends notifications to Slack
```

## Prometheus timing

Lab configuration:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
```

Why this mattered:

A `rate(...[1m])` expression needs enough points in the range. A scrape interval close to the range window can leave too little data for useful rate calculations.

## Debug sequence used

Raw counter:

```promql
http_server_duration_milliseconds_count{http_target="/db"}
```

Raw sum:

```promql
http_server_duration_milliseconds_sum{http_target="/db"}
```

Samples in range:

```promql
count_over_time(
  http_server_duration_milliseconds_count{http_target="/db"}[2m]
)
```

Counter rate:

```promql
rate(http_server_duration_milliseconds_count{http_target="/db"}[2m])
```

Average latency:

```promql
sum(rate(http_server_duration_milliseconds_sum{http_target="/db"}[1m]))
/
sum(rate(http_server_duration_milliseconds_count{http_target="/db"}[1m]))
```

## Why rate became 0

If the counter samples are:

```text
90
90
90
90
90
```

there is no increase.

Therefore:

```text
rate(count) = 0
```

If numerator and denominator rates are both zero, average latency may become `NaN`.

The fix in the test was not to fake the alert threshold; it was to generate continuous slow traffic and ensure the scrape/evaluation windows were sensible.

## Alert rule

```yaml
groups:
  - name: finapp-alerts
    rules:
      - alert: FinAppHighDBLatency
        expr: |
          sum(rate(http_server_duration_milliseconds_sum{http_target="/db"}[1m]))
          /
          sum(rate(http_server_duration_milliseconds_count{http_target="/db"}[1m]))
          > 1000
        for: 30s
        labels:
          severity: warning
        annotations:
          summary: "FinApp /db latency is high"
          description: "Average /db latency has exceeded 1000 ms."
```

Observed lifecycle:

```text
INACTIVE
→ PENDING (~3018ms)
→ FIRING
```

## Incident injection

```sql
SELECT version(), pg_sleep(3);
```

This produced ~3-second requests.

## Trace evidence

```text
Trace ID = one request

GET /db span
  └── SELECT span
```

The SQL span showed where the delay was spent.

## PostgreSQL evidence

```text
state           = active
wait_event_type = Timeout
wait_event      = PgSleep
```

## Alertmanager

Concept:

```text
Prometheus detects
→ Alertmanager routes/groups/deduplicates
→ Slack receives incident notification
```

Keep webhook credentials out of Git.

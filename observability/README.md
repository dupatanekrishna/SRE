# Observability Lab

## Stack

- OpenTelemetry SDK and Collector
- Prometheus
- Grafana
- Loki
- Tempo
- Alertmanager
- Slack notifications
- PostgreSQL test database
- Flask backend

## Telemetry flow

```text
Flask application
  |
  | OTLP HTTP
  v
OpenTelemetry Collector
  |--------------------|-------------------|
  v                    v                   v
Prometheus exporter    Loki                Tempo
  |
  v
Prometheus
  |
  v
Grafana
```

## Metrics

Flask HTTP metrics were exported through OpenTelemetry and exposed by the Collector in Prometheus format.

Example metric names:

```text
http_server_duration_milliseconds_bucket
http_server_duration_milliseconds_sum
http_server_duration_milliseconds_count
```

Average request latency over a time window:

```promql
sum(rate(http_server_duration_milliseconds_sum{http_target="/db"}[1m]))
/
sum(rate(http_server_duration_milliseconds_count{http_target="/db"}[1m]))
```

## Prometheus scrape configuration

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "node-exporter"
    static_configs:
      - targets: ["host.docker.internal:9100"]

  - job_name: "otel-app-metrics"
    static_configs:
      - targets: ["host.docker.internal:8889"]
```

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

## Alert lifecycle observed

```text
INACTIVE → PENDING → FIRING → RESOLVED/INACTIVE
```

A useful lesson from the lab: a rate-based latency alert needs enough samples in the selected window and active traffic during evaluation.

## Logs

Application logs were exported via OpenTelemetry to Loki and queried in Grafana.

Examples:

```logql
{service_name="finapp-backend"}
{service_name="finapp-backend"} |= "GET /db"
```

## Traces

Flask and psycopg2 instrumentation produced a trace with:

- one HTTP span for `GET /db`
- one child SQL span for `SELECT`

Mental model:

```text
Metric → WHAT is abnormal?
Trace  → WHERE is time being spent?
Log    → WHAT happened?
```

## Alertmanager → Slack

Prometheus forwards firing alerts to Alertmanager, which routes them to a Slack incident channel.

```text
Prometheus → Alertmanager → Slack
```

Webhook URLs and credentials are deliberately excluded from this repository.

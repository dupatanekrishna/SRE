# Observability Experimental Lab — Flask + PostgreSQL + OpenTelemetry

This folder is a **repeatable SRE experiment** showing how a small application, database and observability stack work together.

## Architecture

```text
Flask Backend
   |
   | OTLP HTTP
   v
OpenTelemetry Collector
   |--------------------|--------------------|
   v                    v                    v
Prometheus exporter     Loki                 Tempo
   |                    logs                 traces
   v
Prometheus
   |
   | alert rules
   v
Alertmanager
   |
   v
Slack

Prometheus + Loki + Tempo
           |
           v
        Grafana

GET /db → psycopg2 → PostgreSQL
```

## Components in the experiment

| Component | Purpose | Port |
|---|---|---:|
| Flask backend | Test application and DB endpoint | 8080 |
| PostgreSQL 17 | Database dependency | 5432 |
| OpenTelemetry Collector | Receive/process/export telemetry | 4317, 4318, 8889 |
| Prometheus | Metrics + PromQL + alert evaluation | 9090 |
| Grafana | Visualization | 3000 |
| Loki | Logs backend | 3100 |
| Tempo | Traces backend | 3200 |
| Node Exporter | Host metrics | 9100 |
| Alertmanager | Alert routing | 9093 |
| Slack | Incident notification | external |

## What I tested

- Flask instrumentation using OpenTelemetry
- psycopg2 database spans
- metrics/logs/traces exported through OTLP
- OTel Collector pipelines
- Prometheus scraping Collector-exported metrics
- Grafana with Prometheus, Loki and Tempo
- Prometheus latency alert
- Alertmanager → Slack notification
- PostgreSQL wait investigation using `pg_stat_activity`
- correlation: metrics → traces → logs → DB evidence

## Quick start

```bash
cd labs/observability-finapp
cp .env.example .env
cp alertmanager.yml.example alertmanager.yml
docker compose up -d --build
docker compose ps
```

Never commit the real Slack webhook or passwords.

## Healthy baseline

Keep:

```text
DB_SLEEP_SECONDS=0
```

Then:

```bash
./scripts/generate-traffic.sh
```

## Inject the slow database incident

Change:

```text
DB_SLEEP_SECONDS=3
```

Then:

```bash
docker compose up -d --build backend
./scripts/generate-traffic.sh
```

The backend executes:

```sql
SELECT version(), pg_sleep(3);
```

Expected latency is roughly 3 seconds.

## Investigation

Prometheus:
```promql
sum(rate(http_server_duration_milliseconds_sum{http_target="/db"}[1m]))
/
sum(rate(http_server_duration_milliseconds_count{http_target="/db"}[1m]))
```

Loki:
```logql
{service_name="finapp-backend"} |= "GET /db"
```

PostgreSQL:
```bash
./scripts/postgres-activity.sh
```

Expected DB wait during the incident:
```text
wait_event_type = Timeout
wait_event      = PgSleep
```

Trace shape:
```text
GET /db
  └── SELECT
```

## Alert lifecycle

```text
INACTIVE → PENDING → FIRING
```

Alert path:
```text
Prometheus → Alertmanager → Slack
```

## Recover

Set:

```text
DB_SLEEP_SECONDS=0
```

Then:

```bash
docker compose up -d --build backend
```

Generate traffic and verify the latency and alert return to normal.

## Core SRE lesson

```text
METRIC → WHAT is abnormal?
TRACE  → WHERE is time being spent?
LOG    → WHAT happened?
DB     → WHAT is the dependency doing?
```

See [MANUAL_SETUP.md](MANUAL_SETUP.md) for the original one-container-at-a-time experiment.

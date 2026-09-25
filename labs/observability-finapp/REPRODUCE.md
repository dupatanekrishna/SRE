# Reproduce the Complete Observability Lab

This guide recreates the complete container stack used in the experiment.

## Expected final stack

After startup, `docker ps` should show these logical components:

```text
alertmanager
finapp-backend
prometheus
otel-collector
tempo
loki
grafana
node-exporter
postgres-sre
```

Equivalent architecture:

```text
                         +----------------+
                         |   PostgreSQL   |
                         |      :5432     |
                         +-------^--------+
                                 |
                           psycopg2 / SQL
                                 |
+--------+ OTLP HTTP +-----------+---------+
| Client |---------->|   Flask Backend     |
+--------+            |       :8080         |
                      +----------+-----------+
                                 |
                                 | metrics / logs / traces
                                 v
                      +----------------------+
                      | OpenTelemetry        |
                      | Collector            |
                      | :4317 :4318 :8889    |
                      +----+---------+-------+
                           |         |
                    metrics|         |logs/traces
                           |         |
                           v         +------------+
                    +------------+                |
                    | Prometheus |                |
                    |   :9090    |                |
                    +-----+------+                |
                          |                       |
                     alert|                       |
                          v                       |
                  +---------------+               |
                  | Alertmanager  |               |
                  |    :9093      |               |
                  +-------+-------+               |
                          |                       |
                          v                       v
                        Slack             +------+------+
                                          | Loki :3100  |
                                          | Tempo :3200 |
                                          +------+------+
                                                 |
                                                 v
                                           +-----------+
                                           | Grafana   |
                                           |   :3000   |
                                           +-----------+

Node Exporter :9100 → Prometheus
```

## Files that recreate the stack

```text
docker-compose.yml
backend/Dockerfile
backend/requirements.txt
backend/app.py
otel-config.yaml
prometheus.yml
alert-rules.yml
tempo.yaml
alertmanager.yml.example
grafana/provisioning/datasources/datasources.yaml
.env.example
```

## Step 1 — clone and enter the lab

```bash
git clone https://github.com/dupatanekrishna/SRE.git
cd SRE/labs/observability-finapp
```

## Step 2 — prepare local configuration

```bash
cp .env.example .env
cp alertmanager.yml.example alertmanager.yml
```

Edit `.env` and choose local-only passwords.

If Slack notification is required, edit `alertmanager.yml` and add a real Incoming Webhook URL locally.

Do not commit either file with real secrets.

## Step 3 — start the complete stack

```bash
docker compose up -d --build
```

## Step 4 — confirm all containers

```bash
docker ps
```

Expected names:

```text
alertmanager
finapp-backend
prometheus
otel-collector
tempo
loki
grafana
node-exporter
postgres-sre
```

## Step 5 — health/readiness checks

```bash
curl -s http://localhost:8080/
curl -s http://localhost:8080/db
curl -s http://localhost:9090/-/ready
curl -s http://localhost:9093/-/ready
curl -s http://localhost:3200/ready
curl -s http://localhost:8889/metrics | head
```

Open:

```text
Backend       http://localhost:8080
Grafana       http://localhost:3000
Prometheus    http://localhost:9090
Alertmanager  http://localhost:9093
Tempo         http://localhost:3200
Loki          http://localhost:3100
Node Exporter http://localhost:9100/metrics
```

## Step 6 — healthy experiment

In `.env`:

```text
DB_SLEEP_SECONDS=0
```

Apply the backend configuration:

```bash
docker compose up -d --build backend
```

Generate traffic:

```bash
bash scripts/generate-traffic.sh
```

## Step 7 — inject the same slow-database incident

Change `.env`:

```text
DB_SLEEP_SECONDS=3
```

Then:

```bash
docker compose up -d --build backend
bash scripts/generate-traffic.sh
```

The application now executes the equivalent of:

```sql
SELECT version(), pg_sleep(3);
```

Expected:

```text
DB request: ~3.0s
```

## Step 8 — verify metrics

Prometheus:

```promql
sum(rate(http_server_duration_milliseconds_sum{http_target="/db"}[1m]))
/
sum(rate(http_server_duration_milliseconds_count{http_target="/db"}[1m]))
```

The alert rule fires when average `/db` latency remains above 1000 ms for 30 seconds.

```text
INACTIVE → PENDING → FIRING
```

## Step 9 — verify traces

Grafana → Tempo.

Expected relationship:

```text
GET /db
   └── SELECT
```

One Trace ID represents the request. Separate Span IDs represent the HTTP and SQL operations.

## Step 10 — verify logs

Grafana → Loki:

```logql
{service_name="finapp-backend"}
```

or:

```logql
{service_name="finapp-backend"} |= "GET /db"
```

## Step 11 — verify PostgreSQL evidence

```bash
bash scripts/postgres-activity.sh
```

During the injected delay, expect evidence similar to:

```text
state           = active
wait_event_type = Timeout
wait_event      = PgSleep
query            SELECT version(), pg_sleep(...)
```

## Step 12 — verify alert delivery

Flow:

```text
Application latency
    ↓
OTel metric
    ↓
Prometheus
    ↓
FinAppHighDBLatency
    ↓
Alertmanager
    ↓
Slack
```

## Step 13 — recover

Set:

```text
DB_SLEEP_SECONDS=0
```

Then:

```bash
docker compose up -d --build backend
```

Keep some healthy traffic flowing and confirm:

- request latency returns to normal
- Prometheus expression drops
- alert resolves
- SQL span is no longer artificially delayed

## Step 14 — stop

```bash
docker compose down
```

Remove local persistent lab data too:

```bash
docker compose down -v
```

## One-command helpers

A `Makefile` is included:

```bash
make setup
make up
make status
make healthy
make slow
make traffic
make db-activity
make down
```

This is intended as a reproducible learning lab, not a production deployment.

# Original Manual Docker Experiment

The experiment was originally built **one component at a time**. This makes the network and telemetry relationships easier to understand.

## 1. Network

```bash
docker network create observability
```

## 2. PostgreSQL

```bash
docker run -d   --name postgres-sre   --network observability   -p 5432:5432   -e POSTGRES_USER=sreadmin   -e POSTGRES_PASSWORD='<LOCAL-LAB-PASSWORD>'   -e POSTGRES_DB=production   -v postgres-data:/var/lib/postgresql/data   postgres:17
```

## 3. Node Exporter

```bash
docker run -d   --name node-exporter   --network observability   -p 9100:9100   prom/node-exporter
```

With Colima on macOS, remember that these metrics reflect the Linux Docker/Colima environment rather than the full macOS host exactly.

## 4. Loki

```bash
docker run -d   --name loki   --network observability   -p 3100:3100   grafana/loki:latest
```

## 5. Tempo

```bash
docker run -d   --name tempo   --network observability   -p 3200:3200   -v "$(pwd)/tempo.yaml:/etc/tempo.yaml"   grafana/tempo:latest   -config.file=/etc/tempo.yaml
```

Do not publish Tempo host ports 4317/4318 when the OTel Collector already owns those host ports. Tempo receives OTLP internally through the Docker network.

## 6. OTel Collector

```bash
docker run -d   --name otel-collector   --network observability   -p 4317:4317   -p 4318:4318   -p 8889:8889   -v "$(pwd)/otel-config.yaml:/etc/otelcol-contrib/config.yaml"   otel/opentelemetry-collector-contrib:latest
```

## 7. Alertmanager

```bash
cp alertmanager.yml.example alertmanager.yml
```

Add the local Slack webhook, then:

```bash
docker run -d   --name alertmanager   --network observability   -p 9093:9093   -v "$(pwd)/alertmanager.yml:/etc/alertmanager/alertmanager.yml"   prom/alertmanager
```

```bash
curl http://localhost:9093/-/ready
```

## 8. Prometheus

```bash
docker run -d   --name prometheus   --network observability   -p 9090:9090   -v "$(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml"   -v "$(pwd)/alert-rules.yml:/etc/prometheus/alert-rules.yml"   prom/prometheus
```

```bash
curl http://localhost:9090/-/ready
```

Validate configuration:

```bash
docker run --rm   --entrypoint /bin/promtool   -v "$(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml"   -v "$(pwd)/alert-rules.yml:/etc/prometheus/alert-rules.yml"   prom/prometheus   check config /etc/prometheus/prometheus.yml
```

## 9. Grafana

```bash
docker run -d   --name grafana   --network observability   -p 3000:3000   grafana/grafana
```

Datasource URLs inside the Docker network:

```text
Prometheus  http://prometheus:9090
Loki        http://loki:3100
Tempo       http://tempo:3200
```

## 10. Backend

```bash
docker build -t finapp-backend:lab ./backend
```

```bash
docker run -d   --name finapp-backend   --network observability   -p 8080:8080   -e DB_HOST=postgres-sre   -e DB_PORT=5432   -e DB_NAME=production   -e DB_USER=sreadmin   -e DB_PASSWORD='<LOCAL-LAB-PASSWORD>'   -e DB_SLEEP_SECONDS=0   -e OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318   finapp-backend:lab
```

## 11. Expected final container set

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

## 12. Incident test

Healthy:
```text
DB_SLEEP_SECONDS=0
```

Slow:
```text
DB_SLEEP_SECONDS=3
```

Then generate continuous traffic and investigate:

```text
Metrics → Prometheus
Logs    → Loki
Traces  → Tempo
Alert   → Alertmanager → Slack
DB wait → pg_stat_activity
```

This manual version is intentionally preserved because it makes every component and dependency explicit.

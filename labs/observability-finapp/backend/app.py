import logging
import os

import psycopg2
from flask import Flask, jsonify

from opentelemetry import _logs, metrics, trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

OTEL_BASE = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318")

resource = Resource.create({
    "service.name": "finapp-backend",
    "environment": "lab",
})

# Logs
logger_provider = LoggerProvider(resource=resource)
_logs.set_logger_provider(logger_provider)

logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(
        OTLPLogExporter(endpoint=f"{OTEL_BASE}/v1/logs")
    )
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logging.getLogger().addHandler(
    LoggingHandler(
        level=logging.INFO,
        logger_provider=logger_provider,
    )
)

# Metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=f"{OTEL_BASE}/v1/metrics"),
    export_interval_millis=15000,
)

metrics.set_meter_provider(
    MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
    )
)

# Traces
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)

tracer_provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(endpoint=f"{OTEL_BASE}/v1/traces")
    )
)

Psycopg2Instrumentor().instrument()

# Flask
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/")
def home():
    logging.info("GET / health request")
    return jsonify({
        "service": "finapp-backend",
        "status": "ok",
    })

@app.route("/db")
def database_check():
    sleep_seconds = float(os.getenv("DB_SLEEP_SECONDS", "0"))
    conn = None
    cur = None

    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "postgres"),
            port=int(os.getenv("DB_PORT", "5432")),
            dbname=os.getenv("DB_NAME", "production"),
            user=os.getenv("DB_USER", "sreadmin"),
            password=os.environ["DB_PASSWORD"],
        )

        cur = conn.cursor()

        # 0 = healthy baseline
        # 3 = reproduce the slow DB incident
        cur.execute(
            "SELECT version(), pg_sleep(%s);",
            (sleep_seconds,),
        )

        row = cur.fetchone()

        logging.info(
            "GET /db succeeded; simulated DB sleep=%ss",
            sleep_seconds,
        )

        return jsonify({
            "status": "database connection successful",
            "postgres_version": row[0],
            "simulated_sleep_seconds": sleep_seconds,
        })

    except Exception as exc:
        logging.exception("GET /db failed: %s", exc)
        return jsonify({
            "status": "database connection failed",
            "error": str(exc),
        }), 500

    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)

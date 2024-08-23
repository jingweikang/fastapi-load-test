import time
from typing import Tuple
import os
from fastapi import FastAPI

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from opentelemetry.sdk.resources import Resource

from opentelemetry import metrics
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import ASGIApp

# Get global meter provider
provider = metrics.get_meter_provider()
meter = provider.get_meter("fastapiloadtest.middleware")

REQUESTS = meter.create_counter(
    name="fastapi_requests_total",
    description="Total count of requests by method and path.",
)

RESPONSES = meter.create_counter(
    name="fastapi_responses_total",
    description="Total count of responses by method, path and status codes.",
)
REQUESTS_PROCESSING_TIME = meter.create_histogram(
    name="fastapi_requests_duration_seconds",
    description="Histogram of requests processing time by path (in milliseconds)",
    unit="ms",
)
EXCEPTIONS = meter.create_counter(
    name="fastapi_exceptions_total",
    description="Total count of exceptions raised by path and exception type",
)

REQUESTS_IN_PROGRESS = meter.create_up_down_counter(
    name="fastapi_requests_in_progress",
    description="Gauge of requests by method and path currently being processed",
)

class OtelMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, app_name: str = "fastapi-load-test") -> None:
        super().__init__(app)
        self.app_name = app_name

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        method = request.method
        path, is_handled_path = self.get_path(request)

        if not is_handled_path:
            return await call_next(request)

        base_attributes = {"method": method, "path": path, "app_name": self.app_name}
        REQUESTS_IN_PROGRESS.add(amount=1, attributes=base_attributes)
        REQUESTS.add(amount=1, attributes=base_attributes)
        before_time = time.perf_counter()
        try:
            response = await call_next(request)
        except BaseException as e:
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            EXCEPTIONS.add(amount=1, attributes={**base_attributes, **{"exception_type": type(e).__name__}})
            raise e from None
        else:
            status_code = response.status_code
            after_time = time.perf_counter()

            REQUESTS_PROCESSING_TIME.record(amount=(after_time - before_time) * 1000, attributes=base_attributes)
        finally:
            RESPONSES.add(amount=1, attributes={**base_attributes, **{"status_code": status_code}})
            REQUESTS_IN_PROGRESS.add(amount=-1, attributes=base_attributes)

        return response

    @staticmethod
    def get_path(request: Request) -> Tuple[str, bool]:
        for route in request.app.routes:
            match, child_scope = route.matches(request.scope)
            if match == Match.FULL:
                return route.path, True

        return request.url.path, False

def setting_otlp(app: FastAPI, app_name: str = "fastapi-load-test") -> None:
    # Setting OpenTelemetry
    OTEL_METRICS_ENDPOINT = os.environ.get("OTEL_METRICS_ENDPOINT", "observability:4317")
    OTEL_TRACES_ENDPOINT = os.environ.get("OTEL_TRACES_ENDPOINT", "observability:4317")
    OTEL_METRICS_EXPORT_INTERVAL = int(os.environ.get("OTEL_METRICS_EXPORT_INTERVAL", 60000))

    # set the service name to show in traces
    resource = Resource.create(attributes={
        "service.name": app_name,
        "compose_service": app_name
    })

    # set the tracer provider
    tracer = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer)

    FastAPIInstrumentor.instrument_app(app=app, tracer_provider=tracer)

    tracer.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_TRACES_ENDPOINT, insecure=True)))

    # set meter provider
    metric_exporter = OTLPMetricExporter(endpoint=OTEL_METRICS_ENDPOINT, insecure=True)
    meter_provider = MeterProvider(
        metric_readers=[
            PeriodicExportingMetricReader(exporter=metric_exporter, export_interval_millis=OTEL_METRICS_EXPORT_INTERVAL),
        ],
    )
    metrics.set_meter_provider(meter_provider=meter_provider)

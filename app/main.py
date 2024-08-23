import os
import time
import asyncio
from fastapi import FastAPI
from app.observability import OtelMiddleware, setting_otlp

app = FastAPI(
    title="FastAPI load test",
    docs_url="/docs",
    redoc_url="/redoc",
)
setting_otlp(app=app)
app.add_middleware(OtelMiddleware)

IO_DELAY_S = float(os.environ.get("IO_DELAY_S", 1))

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/async-delay/{delay_ms}")
async def async_delay(delay_ms: int) -> int:
    await asyncio.sleep(delay_ms/1000)
    return delay_ms

@app.get('/sync-delay/{delay_ms}')
def sync_delay(delay_ms: int) -> float:
    time.sleep(delay_ms/1000)
    return delay_ms

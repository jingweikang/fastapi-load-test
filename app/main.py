import os
import time
import asyncio
from fastapi import FastAPI

app = FastAPI()

IO_DELAY_S = float(os.environ.get("IO_DELAY_S", 1))

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/async-example")
async def get_async() -> float:
    await asyncio.sleep(IO_DELAY_S)
    return IO_DELAY_S

@app.get('/sync-example')
def get_sync() -> float:
    time.sleep(IO_DELAY_S)
    return IO_DELAY_S

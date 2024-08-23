import asyncio
import aiohttp
from typing import Any, Dict
import numpy as np
import yaml

async def get_forever(url, mean_delay_ms: int, stddev_delay_ms: int):
    delay_ms = int(np.random.normal(mean_delay_ms, stddev_delay_ms, 1))
    async with aiohttp.ClientSession() as session:
        while True:
            delay_ms = int(np.random.normal(mean_delay_ms, stddev_delay_ms, 1))
            async with session.get(f"{url}/{delay_ms}") as response:
                await response.text()


async def request_forever(endpoint_cfg: Dict[str, Any]):
    name = endpoint_cfg.get("NAME", "")
    url = endpoint_cfg.get("URL", "")
    concurrency = endpoint_cfg.get("CONCURRENCY", 0)
    mean_delay_ms = endpoint_cfg.get("MEAN_DELAY_MS", 200)
    stddev_delay_ms = endpoint_cfg.get("STDDEV_DELAY_MS", 25)
    tasks = []
    for i in range(concurrency):
        print(f"{name}, {i}")
        task = asyncio.create_task(get_forever(url, mean_delay_ms, stddev_delay_ms))
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    return
            


async def main(config: Dict[str, Any]):
    tasks = []
    for endpoint_cfg in config.get("ENDPOINTS", []):
        task = asyncio.create_task(request_forever(endpoint_cfg))
        tasks.append(task)
    await asyncio.gather(*tasks)
    return

if __name__ == "__main__":
    with open("client/config.yaml", 'r') as stream:
        config = yaml.safe_load(stream)
    
    asyncio.run(main(config))

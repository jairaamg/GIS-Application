"""gdal-worker entrypoint.

Consumes NATS jobs, claims work atomically, runs isolated processing, publishes results.
"""
from __future__ import annotations

import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gdal_worker")


async def run() -> None:
    logger.info("Starting gdal_worker (stub). Connect to NATS and claim jobs here.")
    while True:
        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(run())

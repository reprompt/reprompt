from __future__ import annotations

from datetime import datetime

import aiohttp
import asyncio

import logging

from . import config

from .background_task_manager import BackgroundTaskManager
from functools import partial

logger = logging.getLogger(__name__)


async def write_traces_task(traces):
    timestamp = datetime.now().isoformat()
    data = {"traces": [{"function_calls": traces, "timestamp": timestamp}]}
    if config.api_key is None:
        print("API key is required to upload traces")
        return
    try:
        async with aiohttp.ClientSession() as session:
            logger.debug(f"Uploading traces asynchronously")
            async with session.post(
                f"{config.api_base_url}/api/tracer/upload_batch",
                json=data,
                headers={"Content-Type": "application/json", "apiKey": config.api_key},
            ) as response:
                if response.status != 200:
                    logger.error(f"Failed to upload batch: {response.status}")
                else:
                    logger.debug("Batch uploaded successfully")
    except aiohttp.ClientError:
        logger.error("Cannot connect to reprompt to upload traces")


def write_traces(traces):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(write_traces_task([trace.get_trace_info() for trace in traces]))
    else:
        # Handling the case where loop is not running is tricky
        # It's usually not recommended to try to start the loop yourself in a library function
        print("Event loop is not running. Can't schedule write_traces_task.")


class FunctionTrace:
    def __init__(self, func_name, func_inputs):
        logger.debug(f"Creating trace for function {func_name}")
        self.func_name = func_name
        self.start_time = datetime.now()
        self.end_time = None
        self.duration = None
        self.func_inputs = func_inputs
        self.func_outputs = None

    def end_trace(self, func_outputs):
        logger.debug(f"Ending trace for function {self.func_name}")
        self.func_outputs = func_outputs
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()

    def get_trace_info(self):
        return {
            "function_name": self.func_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration,
            "function_inputs": self.func_inputs,
            "function_outputs": self.func_outputs,
        }


async def get_edits(input: str) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.api_base_url}/api/overrides/get_example_overrides",
                json={"input": input},
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch edits: {response.status}")
                    return None
                else:
                    logger.debug("fetched example overrides")
                    return await response.json()
    except aiohttp.ClientError:
        logger.error("Cannot connect to reprompt to fetch edits")

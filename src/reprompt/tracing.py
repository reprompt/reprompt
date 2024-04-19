from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from functools import partial

import aiohttp

from . import config
from .background_task_manager import BackgroundTaskManager

logger = logging.getLogger(__name__)


# Core business logic for uploading traces
async def upload_traces(data):
    if config.api_key is None:
        print("API key is required to upload traces")
        return
    try:
        async with aiohttp.ClientSession() as session:
            logger.debug("Uploading traces asynchronously")
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


# Asynchronous wrapper
async def write_traces_async(traces):
    timestamp = datetime.now().isoformat()
    data = {"traces": [{"function_calls": traces, "timestamp": timestamp}]}
    await upload_traces(data)


# Synchronous wrapper
async def write_traces_sync(traces):
    timestamp = datetime.now().isoformat()
    data = {"traces": [{"function_calls": traces, "timestamp": timestamp}]}
    await upload_traces(data)


# Unified interface to call either sync or async based on need
async def write_traces(traces, async_mode=False):
    traces = [trace.get_trace_info() for trace in traces]
    if async_mode:
        asyncio.create_task(write_traces_async(traces))
    else:
        await write_traces_sync(traces)


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
                headers={"Content-Type": "application/json", "apiKey": config.api_key},
            ) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch edits: {response.status}")
                    return None
                else:
                    logger.debug("fetched example overrides")
                    return await response.json()
    except aiohttp.ClientError:
        logger.error("Cannot connect to reprompt to fetch edits")

from __future__ import annotations

from datetime import datetime

import aiohttp

from . import config


async def write_traces_to_file(traces):
    timestamp = datetime.now().isoformat()
    data = {"traces": [{"function_calls": traces, "timestamp": timestamp}]}
    if config.api_key is None:
        print("API key is required to upload traces")
        return
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.api_base_url}/api/tracer/upload_batch",
                json=data,
                headers={"Content-Type": "application/json", "apiKey": config.api_key},
            ) as response:
                if response.status != 200:
                    print("Failed to upload batch")
                else:
                    print("Batch uploaded successfully")
    except aiohttp.ClientError:
        print("Cannot connect to tracer")


class FunctionTrace:
    def __init__(self, func_name, func_inputs):
        self.func_name = func_name
        self.start_time = datetime.now()
        self.end_time = None
        self.duration = None
        self.func_inputs = func_inputs
        self.func_outputs = None

    def end_trace(self, func_outputs):
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

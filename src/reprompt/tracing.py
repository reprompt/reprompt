from __future__ import annotations

from datetime import datetime

import aiohttp

from .config import api_base_url, api_key


async def write_traces_to_file(traces):
    timestamp = datetime.now().isoformat()
    data = {"traces": [{"function_calls": traces, "timestamp": timestamp}]}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{api_base_url}/api/tracer/upload_batch",
                json=data,
                headers={"Content-Type": "application/json", "apiKey": api_key},
            ) as response:
                if response.status != 200:
                    print("Failed to upload batch")
                else:
                    print("Batch uploaded successfully")
    except aiohttp.ClientError:
        print("Cannot connect to tracer")


class FunctionTrace:
    def __init__(self, func_name, request_details):
        self.func_name = func_name
        self.start_time = datetime.now()
        self.end_time = None
        self.duration = None
        self.request_details = request_details
        self.response_details = None

    def end_trace(self, response_details):
        self.response_details = response_details
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()

    def get_trace_info(self):
        return {
            "function_name": self.func_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration,
            "request_details": self.request_details,
            "response_details": self.response_details,
        }

"""Reprompt"""

from __future__ import annotations

import datetime
import logging
import os

import aiohttp

from .custom_httpx import setup_monkey_patch
from .tracing import FunctionTrace

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IMPORTANT: setting version for Reprompt package
__version__ = "0.0.6"
__all__ = ["FunctionTrace", "init", "write_traces_to_file"]


async def write_traces_to_file(traces):
    timestamp = datetime.now().isoformat()
    data = {"traces": [{"function_calls": traces, "timestamp": timestamp}]}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:3001/api/tracer/upload_batch",
                json=data,
                headers={"Content-Type": "application/json", "apiKey": "a"},
            ) as response:
                if response.status != 200:
                    print("Failed to upload batch")
                else:
                    print("Batch uploaded successfully")
    except aiohttp.ClientError:
        print("Cannot connect to tracer")


def init(api_base_url: str = None, api_key: str = None):
    """
    Initializes the reprompt SDK with the given API base URL and API key.
    Both parameters can have default values and can also be read from environment variables.
    """
    # Default values or environment variables
    api_base_url = api_base_url or os.getenv("REPROMPT_API_BASE_URL", "http://repromptai.com/")
    api_key = api_key or os.getenv("REPROMPT_API_KEY")

    if not api_key:
        logger.error("API key is required but was not provided. Monkey patching will not be applied.")
        return

    try:
        # Apply the monkey patch
        setup_monkey_patch()
        logger.info("All HTTPX calls will now be intercepted and logged by Reprompt.")
    except ImportError as e:
        logger.error(f"Required module not found: {e}. Monkey patching not applied.")

    logger.info(f"reprompt initialized with API Base URL: {api_base_url} and API Key: {api_key}")

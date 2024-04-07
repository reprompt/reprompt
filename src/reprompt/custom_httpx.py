"""Module providing a function printing python version."""

from __future__ import annotations

import asyncio
import logging

import httpx

from reprompt.tracing import FunctionTrace, write_traces_to_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Save the original send method to call it later
_original_send = httpx.Client.send


def openai_trace_request_response(request, response):
    """
    Logs the details of the request and response for api.openai.com calls and schedules the upload of trace data.
    """
    request_info = {
        "url": str(request.url),
        "method": request.method,
        "headers": dict(request.headers),
        "content": request.content.decode("utf-8") if request.content else None,
    }

    response_info = {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "content": response.text,
    }

    trace = FunctionTrace("OpenAI API Call", request_info)
    trace.end_trace(response_info)

    # Log the trace info
    # logger.debug.(json.dumps(trace.get_trace_info(), indent=2))

    # Schedule the upload of trace data
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(write_traces_to_file([trace.get_trace_info()]))
    else:
        asyncio.run(write_traces_to_file([trace.get_trace_info()]))


def custom_send(self, request, *args, **kwargs):
    """
    Custom send method to intercept requests to api.openai.com.
    """
    # Check if the request is for api.openai.com
    if "api.openai.com" in request.url.host:
        # Call the original send method
        response = _original_send(self, request, *args, **kwargs)

        # Log the request and response details
        openai_trace_request_response(request, response)
    else:
        # If not targeting api.openai.com, call the original send method without logging
        response = _original_send(self, request, *args, **kwargs)

    return response


def setup_monkey_patch():
    """
    Replace the httpx send method with the custom one
    """
    httpx.Client.send = custom_send

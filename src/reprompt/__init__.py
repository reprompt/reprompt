"""Reprompt"""

from __future__ import annotations
from typing import Callable
import logging
import functools
import datetime
import json

from .tracing import FunctionTrace

# IMPORTANT: setting version for Reprompt package
__version__ = "0.0.5"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TraceLogger:
    @staticmethod
    def log_request(func: Callable, *args, **kwargs):
        """
        Log the request made to the OpenAI API.
        """
        request_info = {
            "function": func.__name__,
            "args": args,
            "kwargs": kwargs,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        logger.info("Request to OpenAI: %s", json.dumps(request_info))

    @staticmethod
    def log_response(response):
        """
        Log the response from the OpenAI API.
        """
        response_info = {"response": response, "timestamp": datetime.datetime.now().isoformat()}
        logger.info("Response from OpenAI: %s", json.dumps(response_info))


def with_tracing(func):
    """
    Decorator to add tracing around a function call.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        TraceLogger.log_request(func, *args, **kwargs)
        result = func(*args, **kwargs)
        TraceLogger.log_response(result)
        return result

    return wrapper


from .custom_httpx import setup_monkey_patch


def start_trace(API_KEY=None):
    """
    Sets up monkey patching to intercept and log all HTTPX calls.
    """
    try:
        # Apply the monkey patch
        setup_monkey_patch()

        logger.info("All HTTPX calls will now be intercepted and logged.")
        logger.info("reprompt - Trace setup initialized with API_KEY: %s", API_KEY)

    except ImportError as e:
        logger.info(f"Required module not found: {e}. Monkey patching not applied.")
        logger.info("reprompt - Trace setup initialized with API_KEY: %s", API_KEY)

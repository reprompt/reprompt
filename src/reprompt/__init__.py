#   -------------------------------------------------------------
#   Copyright (c) Microsoft Corporation. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   -------------------------------------------------------------
"""Python Package Template"""
from __future__ import annotations
from typing import Callable

__version__ = "0.0.3"

import logging
import functools
import datetime
import json

# Configure logging
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
            "timestamp": datetime.datetime.now().isoformat()
        }
        logger.info("Request to OpenAI: %s", json.dumps(request_info))

    @staticmethod
    def log_response(response):
        """
        Log the response from the OpenAI API.
        """
        response_info = {
            "response": response,
            "timestamp": datetime.datetime.now().isoformat()
        }
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

def start_trace(API_KEY=None):
    """
    Enhances the OpenAI API calls with tracing functionality if the openai module is available.
    Takes an optional API_KEY argument for potential future use.
    """
    try:
        import openai
        from openai.api_resources import ChatCompletion, Completion


        def apply_tracing():
            """
            Apply the tracing decorator to OpenAI API methods.
            """
            print('i got the tracing')
            print('appliedit')
            for cls in [ChatCompletion, Completion]:
                original_create = cls.create
                cls.create = with_tracing(original_create)

        apply_tracing()
        logger.info("reprompt - Trace setup initialized with API_KEY: %s", API_KEY)
    except ImportError:
        logger.info("OpenAI module not found. Tracing not applied.")
        logger.info("reprompt - Trace setup initialized with API_KEY: %s", API_KEY)
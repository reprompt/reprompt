"""Reprompt"""

from __future__ import annotations

import logging

from . import config
from .custom_httpx import setup_monkey_patch
from .tracing import FunctionTrace

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IMPORTANT: setting version for Reprompt package
__version__ = "0.0.6"
# IMPORTANT: All the functions we want to expose publicly from the reprompt module
__all__ = ["FunctionTrace", "init", "write_traces_to_file"]


def init(api_base_url: str = None, api_key: str = None, autocapture: bool = True):
    """
    Initializes the reprompt SDK with the given API base URL and API key.
    If api_base_url or api_key is not None in the arguments, we override the global variable.
    """
    if api_base_url is not None:
        config.api_base_url = api_base_url
    if api_key is not None:
        config.api_key = api_key

    if not config.api_key:
        logger.error("API key is required but was not provided. Monkey patching will not be applied.")
        return

    if autocapture:
        try:
            # Apply the monkey patch
            setup_monkey_patch()
            logger.info("All HTTPX calls will now be intercepted and logged by Reprompt.")
        except ImportError as e:
            logger.error(f"Required module not found: {e}. Monkey patching not applied.")

    logger.info(f"reprompt initialized with API Base URL: {config.api_base_url} and API Key: {config.api_key}")

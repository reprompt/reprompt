"""Reprompt"""

from __future__ import annotations

import logging

from . import config
from .tracing import FunctionTrace, get_edits, write_traces, write_traces_sync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IMPORTANT: setting version for Reprompt package
__version__ = "0.0.7.7"
# IMPORTANT: All the functions we want to expose publicly from the reprompt module
__all__ = ["init", "FunctionTrace", "write_traces", "get_edits", "write_traces_sync"]


def init(api_base_url: str = None, api_key: str = None, debug: bool = False):
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
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

    logger.debug(
        f"reprompt v{__version__} initialized with API Base URL: {config.api_base_url} and API Key: {config.api_key}"
    )

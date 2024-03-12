#   -------------------------------------------------------------
#   Copyright (c) Microsoft Corporation. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   -------------------------------------------------------------
"""Python Package Template"""
from __future__ import annotations

__version__ = "0.0.3"

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
    # Use the apiKey for something, like authenticating with the openai API or configuring the tracing behavior.

def start_trace(API_KEY=None):
    """
    Placeholder for starting trace functionality. Currently does not perform actual tracing.
    Takes an optional API_KEY argument for potential future use.
    """
    logger.info("reprompt - Trace setup initialized with API_KEY: %s", API_KEY)

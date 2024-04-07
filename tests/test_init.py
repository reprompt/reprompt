import pytest
from unittest.mock import patch, MagicMock
from reprompt import start_trace, FunctionTrace
import logging


@patch("reprompt.setup_monkey_patch")
def test_start_trace(mock_setup_monkey_patch):
    start_trace("test_api_key")
    mock_setup_monkey_patch.assert_called_once()


def test_function_trace_initialization():
    trace = FunctionTrace("TestFunction", {})
    # Assuming FunctionTrace modifies some internal state or has other side effects
    # Test those effects here
    # Example:
    # assert trace.some_internal_state == expected_value


def test_function_trace_end_trace():
    trace = FunctionTrace("TestFunction", {})
    trace.end_trace({"response": "TestResponse"})
    # Test the effects of ending a trace, if observable beyond logging
    # Example:
    # assert trace.has_ended is True

from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from openai import OpenAI

import reprompt
from reprompt.custom_httpx import openai_trace_request_response


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {"choices": [{"text": "Test response"}]}


@pytest.fixture
def mock_trace_function():
    """Mock the tracing function to capture trace data."""
    with patch("reprompt.custom_httpx.openai_trace_request_response") as mock:
        yield mock


def openai_call():
    reprompt.init(api_key="blatest")
    client = OpenAI()

    completion = client.completions.create(
        model="gpt-3.5-turbo-instruct", prompt="Say this is a test", max_tokens=7, temperature=0
    )


def test_openai_api_call_traced_correctly(mock_openai_response, mock_trace_function):
    # Mock the OpenAI API call to return a predefined response
    with patch("openai.Completion.create", return_value=mock_openai_response):
        # Perform the API call
        openai_call()

        # Verify the trace function was called
        mock_trace_function.assert_called_once()

        # Extract the request and response passed to the trace function
        args, kwargs = mock_trace_function.call_args
        request, response = args

        # Verify the request and response contain expected data
        assert "api.openai.com" in request.url.host
        assert response.status_code == 200
        assert json.loads(request.content) == {
            "model": "gpt-3.5-turbo-instruct",
            "prompt": "Say this is a test",
            "max_tokens": 7,
            "temperature": 0,
        }

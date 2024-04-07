from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import reprompt


@patch("reprompt.setup_monkey_patch")
def test_init(mock_setup_monkey_patch):
    reprompt.init(api_base_url="http://example.com", api_key="blah")
    mock_setup_monkey_patch.assert_called_once()


import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List
from pydantic import BaseModel

from vidai.providers.strategies import ToolPolyfillProvider
from vidai.exceptions import StructuredOutputError

# Test Models
class UserProfile(BaseModel):
    name: str
    age: int

class SimpleProvider(ToolPolyfillProvider):
    """Concrete implementation for testing."""
    def execute_request(self, client, model, messages, stream=False, **kwargs):
        pass

@pytest.fixture
def provider():
    config = MagicMock()
    return SimpleProvider(config=config)

def test_transform_request_converts_response_format_to_tools(provider):
    """Test that response_format is converted to tools."""
    # Setup
    raw_kwargs = {
        "response_format": {"type": "json_schema", "json_schema": {"name": "UserProfile", "schema": UserProfile.model_json_schema()}},
        "other_arg": "value"
    }
    
    # Execute
    kwargs = provider.transform_request(raw_kwargs)
    
    # Verify
    assert "response_format" not in kwargs
    assert "tools" in kwargs
    assert kwargs["tool_choice"]["type"] == "function"
    assert kwargs["tool_choice"]["function"]["name"] == "UserProfile"
    
    tool = kwargs["tools"][0]
    assert tool["type"] == "function"
    assert tool["function"]["name"] == "UserProfile"
    assert "parameters" in tool["function"]
    
    # Verify state side effect
    assert provider.tool_polyfill_name == "UserProfile"

def test_transform_response_is_passthrough(provider):
    """Test that transform_response returns strictly passed through response."""
    # Setup
    mock_response = {"choices": []}
    
    # Execute
    result = provider.transform_response(mock_response)
    
    # Verify
    assert result == mock_response
    

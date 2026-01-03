import pytest
from unittest.mock import MagicMock, patch
from typing import List
from pydantic import BaseModel

from vidai import Vidai, VidaiConfig
from vidai.models import EnhancedResponse
from vidai.providers.anthropic import AnthropicProvider

class UserInfo(BaseModel):
    name: str
    age: int

@pytest.fixture
def client():
    config = VidaiConfig(provider="anthropic")
    return Vidai(api_key="test-key", config=config)

def test_responses_create_with_pydantic_polyline(client):
    """Test that responses.create handles Pydantic models via polyfill."""
    
    # Mock the provider's execute_response_request
    # We need to spy on the provider instance inside the client
    provider = client._structured_processor.provider
    assert isinstance(provider, AnthropicProvider)
    
    # Mock return value simulating a tool call from Anthropic
    mock_chat_completion = MagicMock()
    mock_chat_completion.id = "msg_123"
    mock_chat_completion.created = 1234567890
    mock_chat_completion.model = "claude-3-opus"
    mock_chat_completion.object = "chat.completion"
    mock_chat_completion.usage = {"input_tokens": 10, "output_tokens": 20}
    
    # Mock tool call response
    mock_message = MagicMock()
    mock_message.content = None
    mock_tool_call = MagicMock()
    mock_tool_call.id = "call_abc"
    mock_tool_call.type = "function"
    mock_tool_call.function.name = "UserInfo" # Should match sanitized model name
    mock_tool_call.function.arguments = '{"name": "Alice", "age": 30}'
    mock_message.tool_calls = [mock_tool_call]
    
    mock_chat_completion.choices = [MagicMock(message=mock_message)]
    
    # Patch execute_request to return our mock
    with patch.object(provider, 'execute_request', return_value=mock_chat_completion) as mock_execute:
        
        # Call create with Pydantic model
        response = client.responses.create(
            model="claude-3-opus",
            input="Who is Alice?",
            response_format=UserInfo
        )
        
        # Verify provider received tools
        call_kwargs = mock_execute.call_args[1]
        assert "tools" in call_kwargs
        assert len(call_kwargs["tools"]) == 1
        assert call_kwargs["tools"][0]["function"]["name"] == "UserInfo"
        assert call_kwargs["tool_choice"]["function"]["name"] == "UserInfo"
        
        # Verify response wrapper unwrapped it
        assert isinstance(response, EnhancedResponse)
        assert len(response.output) == 1
        output_item = response.output[0]
        
        # Should be converted to a message with the JSON content
        assert output_item.type == "message"
        assert output_item.role == "assistant"
        # Since it was unwrapped from tool call arguments into content
        assert output_item.content[0].text == '{"name": "Alice", "age": 30}'

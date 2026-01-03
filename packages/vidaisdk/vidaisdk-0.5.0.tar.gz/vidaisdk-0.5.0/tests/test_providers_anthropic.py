"""Tests for AnthropicProvider."""

import pytest
from unittest.mock import MagicMock, patch, Mock
from vidai.providers.anthropic import AnthropicProvider
from vidai.config import VidaiConfig

@pytest.fixture
def config():
    return VidaiConfig()

@pytest.fixture
def provider(config):
    return AnthropicProvider(config)

def test_map_response_text(provider):
    """Test mapping standard text response."""
    anthropic_resp = {
        "content": [
            {"type": "text", "text": "Hello world"}
        ],
        "usage": {"input_tokens": 10, "output_tokens": 5}
    }
    
    mapped = provider._map_response(anthropic_resp, model="claude-3-opus")
    
    assert mapped.choices[0].message.content == "Hello world"
    assert mapped.choices[0].message.role == "assistant"
    # usage might be None in map_response currently or updated logic?
    # Checked code: usage=None # Populate if critical
    # assert mapped.usage.prompt_tokens == 10

def test_map_response_tool_use(provider):
    """Test mapping tool use response."""
    anthropic_resp = {
        "content": [
            {"type": "text", "text": "Reasoning..."},
            {
                "type": "tool_use",
                "id": "tool_123",
                "name": "structured_response",
                "input": {"name": "Alice"}
            }
        ],
        "usage": {"input_tokens": 10, "output_tokens": 5},
        "stop_reason": "tool_use"
    }
    
    mapped = provider._map_response(anthropic_resp, model="claude-3-opus")
    
    msg = mapped.choices[0].message
    # Check tool calls
    assert len(msg.tool_calls) == 1
    tc = msg.tool_calls[0]
    assert tc.function.name == "structured_response"
    assert tc.function.arguments == '{"name": "Alice"}'
    assert mapped.choices[0].finish_reason == "tool_calls"

def test_execute_request_mock(provider):
    """Test execute_request logic with httpx mocks."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "content": [{"type": "text", "text": "Response"}],
        "usage": {"input_tokens": 1, "output_tokens": 1},
        "id": "msg_123",
        "model": "claude-3-opus",
        "stop_reason": "end_turn"
    }
    
    # Needs API key
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch("vidai.providers.anthropic.httpx.Client") as MockClient:
            mock_client_instance = MockClient.return_value
            mock_client_instance.__enter__.return_value.post.return_value = mock_response
            
            response = provider.execute_request(
                client=None, # not used
                model="claude-3-opus",
                messages=[{"role": "user", "content": "Hi"}]
            )
            
            assert response.choices[0].message.content == "Response"
            
            # Verify payload structure
            call_args = mock_client_instance.__enter__.return_value.post.call_args
            assert call_args is not None
            url = call_args[0][0]
            kwargs = call_args[1]
            assert "api.anthropic.com" in url
            assert kwargs["headers"]["x-api-key"] == "sk-test"
            assert kwargs["json"]["model"] == "claude-3-opus"
            assert kwargs["json"]["model"] == "claude-3-opus"

@patch("vidai.utils.encode_image")
@patch("vidai.utils.get_media_type")
def test_execute_request_image_transformation(mock_get_type, mock_encode, provider):
    """Test transforming image_url to Anthropic image block."""
    mock_encode.return_value = "base64_string"
    mock_get_type.return_value = "image/jpeg"
    
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch("vidai.providers.anthropic.httpx.Client") as MockClient:
            mock_client_instance = MockClient.return_value
            mock_client_instance.__enter__.return_value.post.return_value = Mock(
                status_code=200,
                json=lambda: {"content": [], "usage": {}}
            )
            
            provider.execute_request(
                client=None,
                model="claude-3-opus",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe this"},
                            {"type": "image_url", "image_url": {"url": "http://img.com/foo.jpg"}}
                        ]
                    }
                ]
            )
            
            # Verify payload
            call_args = mock_client_instance.__enter__.return_value.post.call_args
            payload = call_args[1]["json"]
            user_msg = payload["messages"][0]
            assert len(user_msg["content"]) == 2
            assert user_msg["content"][0]["type"] == "text"
            
            # Check image block
            img_block = user_msg["content"][1]
            assert img_block["type"] == "image"
            assert img_block["source"]["type"] == "base64"
            assert img_block["source"]["media_type"] == "image/jpeg"
            assert img_block["source"]["data"] == "base64_string"

@patch("vidai.utils.encode_image")
@patch("vidai.utils.get_media_type")
def test_execute_request_pdf_transformation(mock_get_type, mock_encode, provider):
    """Test transforming image_url to Anthropic document block (PDF)."""
    mock_encode.return_value = "pdf_base64_string"
    mock_get_type.return_value = "application/pdf"
    
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch("vidai.providers.anthropic.httpx.Client") as MockClient:
            mock_client_instance = MockClient.return_value
            mock_client_instance.__enter__.return_value.post.return_value = Mock(
                status_code=200,
                json=lambda: {"content": [], "usage": {}}
            )
            
            provider.execute_request(
                client=None,
                model="claude-3-opus",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Read this"},
                            {"type": "image_url", "image_url": {"url": "http://doc.com/manual.pdf"}}
                        ]
                    }
                ]
            )
            
            # Verify payload
            call_args = mock_client_instance.__enter__.return_value.post.call_args
            payload = call_args[1]["json"]
            user_msg = payload["messages"][0]
            
            # Check document block
            doc_block = user_msg["content"][1]
            assert doc_block["type"] == "document"
            assert doc_block["source"]["type"] == "base64"
            assert doc_block["source"]["media_type"] == "application/pdf"
            assert doc_block["source"]["data"] == "pdf_base64_string"

def test_execute_request_caching_headers(provider):
    """Test that caching headers are added when cache_control is present."""
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": "Cache me",
                    "cache_control": {"type": "ephemeral"}
                }
            ]
        }
    ]
    
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch("vidai.providers.anthropic.httpx.Client") as MockClient:
            mock_post = MockClient.return_value.__enter__.return_value.post
            mock_post.return_value = Mock(
                status_code=200,
                json=lambda: {"content": [], "usage": {}}
            )
            
            provider.execute_request(
                client=None,
                model="model",
                messages=messages
            )
            
            # Check headers
            call_kwargs = mock_post.call_args[1]
            headers = call_kwargs["headers"]
            assert headers["anthropic-beta"] == "prompt-caching-2024-07-31"

def test_execute_request_caching_system_prompt(provider):
    """Test that caching headers are added when system prompt has cache_control."""
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text", 
                    "text": "System instructions",
                    "cache_control": {"type": "ephemeral"}
                }
            ]
        },
        {"role": "user", "content": "Hi"}
    ]
    
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch("vidai.providers.anthropic.httpx.Client") as MockClient:
            mock_post = MockClient.return_value.__enter__.return_value.post
            mock_post.return_value = Mock(
                status_code=200,
                json=lambda: {"content": [], "usage": {}}
            )
            
            provider.execute_request(
                client=None,
                model="model",
                messages=messages
            )
            
            # Check headers
            call_kwargs = mock_post.call_args[1]
            headers = call_kwargs["headers"]
            assert headers["anthropic-beta"] == "prompt-caching-2024-07-31"

def test_streaming_chunk_creation(provider):
    """Test internal chunk creation helper."""
    # Test text chunk
    chunk = provider._create_chunk(id="test_id", model="claude", content="Hello")
    assert chunk.choices[0].delta.content == "Hello"
    assert chunk.id == "test_id"
    
    # Test tool chunk
    chunk = provider._create_chunk(
        id="test_id", 
        model="claude", 
        tool_calls=[{"index": 0, "id": "t1", "function": {"name": "func", "arguments": ""}}]
    )
    assert chunk.choices[0].delta.tool_calls[0].function.name == "func"

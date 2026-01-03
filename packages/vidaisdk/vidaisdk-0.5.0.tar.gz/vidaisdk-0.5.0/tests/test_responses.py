
import pytest
from unittest.mock import MagicMock, patch
from vidai import Vidai, VidaiConfig
from vidai.models import EnhancedResponse
from vidai.providers.anthropic import AnthropicProvider

@pytest.fixture
def mock_openai_response():
    resp = MagicMock()
    resp.id = "resp_123"
    resp.object = "response"
    resp.created = 1234567890
    resp.model = "gpt-4o"
    resp.output = [{"type": "message", "role": "assistant", "content": "Hello"}]
    resp.usage = None
    return resp

def test_responses_create_default(mock_openai_response):
    """Test standard Responses API creation (OpenAI default)."""
    with patch("openai.resources.responses.Responses.create", return_value=mock_openai_response) as mock_create:
        client = Vidai(api_key="test")
        
        # Ensure provider is NOT used (default to openai)
        client._structured_processor.provider = None
        
        resp = client.responses.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hi"}]
        )
        
        mock_create.assert_called_once()
        assert isinstance(resp, EnhancedResponse)
        assert resp.id == "resp_123"
        # Object parity: output item content is a list of blocks
        # EnhancedResponse wraps output. If expecting text, check first output item.
        assert resp.output[0].content[0].text == "Hello"

def test_responses_delegation_to_provider():
    """Test delegation to a provider adapter."""
    mock_provider = MagicMock()
    mock_provider.execute_response_request.return_value = MagicMock(
        id="prov_123",
        object="response",
        created=111,
        model="claude-3",
        output=[{"type": "message", "role": "assistant", "content": "Claude says hi"}],
        usage=None
    )
    
    client = Vidai(api_key="test")
    client._structured_processor.provider = mock_provider
    
    resp = client.responses.create(
        model="claude-3-sonnet",
        messages=[{"role": "user", "content": "Hi"}]
    )
    
    mock_provider.execute_response_request.assert_called_once()
    assert resp.id == "prov_123"
    assert resp.model == "claude-3"
    assert resp.output[0].content[0].text == "Claude says hi"

def test_anthropic_execute_response_request():
    """Test Anthropic provider's conversion logic."""
    provider = AnthropicProvider(config=VidaiConfig())
    
    # Mock return from execute_request (which returns ChatCompletion)
    mock_cc = MagicMock()
    mock_cc.id = "msg_123"
    mock_cc.created = 999
    mock_cc.model = "claude-3"
    mock_cc.choices = [
        MagicMock(message=MagicMock(content="Anthropic Content", tool_calls=None))
    ]
    mock_cc.usage = None
    
    with patch.object(provider, "execute_request", return_value=mock_cc):
        result = provider.execute_response_request(
            client=None,
            model="claude-3",
            messages=[]
        )
        
        assert result.id == "msg_123"
        assert result.object == "response"
        assert len(result.output) == 1
        # Provider response adapter returns dict-like items in output list
        assert result.output[0]["content"] == "Anthropic Content"

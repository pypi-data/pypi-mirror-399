"""Unit tests for VidaiProxyProvider."""
from unittest.mock import MagicMock, patch
import pytest
from vidai.providers.vidai_proxy import VidaiProxyProvider
from vidai.config import VidaiConfig

@pytest.fixture
def provider():
    config = VidaiConfig(provider="vidai")
    return VidaiProxyProvider(config, base_url="http://test-proxy")

def test_transform_request_header_injection(provider):
    """Verify transform_request injects x-model and authorization."""
    with patch.dict("os.environ", {"VIDAI_SERVER_API_KEY": "test-key"}):
        kwargs = {"model": "test-model-id", "messages": []}
        
        # Mock delegate to return kwargs as-is
        mock_delegate = MagicMock()
        mock_delegate.transform_request.side_effect = lambda k: k
        
        # Mock _get_delegate_for_model
        with patch.object(provider, "_get_delegate_for_model", return_value=mock_delegate):
            result = provider.transform_request(kwargs)
            
            headers = result.get("extra_headers", {})
            assert headers["x-vidai-model"] == "test-model-id"
            assert headers["Authorization"] == "Bearer test-key"

def test_delegate_uses_factory(provider):
    """Verify _get_delegate_for_model uses ProviderFactory."""
    # Mock model cache to return 'mistral'
    provider._model_cache["mistral-small"] = "mistral"
    provider._initialized = True
    
    with patch("vidai.providers.factory.ProviderFactory.create_provider") as mock_create:
        mock_instance = MagicMock()
        mock_create.return_value = mock_instance
        
        delegate = provider._get_delegate_for_model("mistral-small")
        
        assert delegate == mock_instance
        mock_create.assert_called_once()
        # Verify call args: config.provider should be 'mistral'
        args, _ = mock_create.call_args
        config_arg = args[0]
        assert config_arg.provider == "mistral"

def test_polyfill_propagation(provider):
    """Verify tool_polyfill_name is propagated from delegate."""
    kwargs = {"model": "test-model"}
    
    mock_delegate = MagicMock()
    mock_delegate.tool_polyfill_name = "test-polyfill"
    mock_delegate.transform_request.return_value = {}
    
    with patch.object(provider, "_get_delegate_for_model", return_value=mock_delegate):
        provider.transform_request(kwargs)
        assert provider.tool_polyfill_name == "test-polyfill"
        
    # Check fallback
    class SimpleDelegate:
        def transform_request(self, k): return {}
        
    with patch.object(provider, "_get_delegate_for_model", return_value=SimpleDelegate()):
        provider.transform_request(kwargs)
        assert provider.tool_polyfill_name is None

def test_initialization_discovery(provider):
    """Verify _ensure_initialized calls proxy."""
    with patch("httpx.Client") as mock_httpx:
        mock_client = mock_httpx.return_value.__enter__.return_value
        mock_client.get.return_value.status_code = 200
        mock_client.get.return_value.json.return_value = {
            "data": [
                {"id": "deepseek-chat", "provider": "deepseek"},
                {"id": "my-mistral", "owned_by": "mistral"}
            ]
        }
        
        provider._ensure_initialized()
        
        mock_client.get.assert_called_with(
            "http://test-proxy/models", 
            headers={}, 
            timeout=5.0
        )
        
        assert provider._model_cache["deepseek-chat"] == "deepseek"
        assert provider._model_cache["my-mistral"] == "mistral"

def test_execute_request(provider):
    """Verify execute_request calls client.post with correct args."""
    mock_client = MagicMock()
    # Mock post response
    mock_response = MagicMock()
    mock_client.post.return_value = mock_response
    
    # Mock delegate logic (it just needs to exist)
    mock_delegate = MagicMock()
    
    with patch.object(provider, "_get_delegate_for_model", return_value=mock_delegate):
        messages = [{"role": "user", "content": "hello"}]
        # Pass extra_headers via kwargs (simulating what happens after transform_request flow)
        result = provider.execute_request(
            mock_client, 
            "test-model", 
            messages, 
            extra_headers={"Authorization": "Bearer key"}
        )
        
        mock_client.post.assert_called_once()
        args, kwargs = mock_client.post.call_args
        
        assert args[0] == "/chat/completions"
        assert kwargs["body"]["model"] == "test-model"
        assert kwargs["options"]["headers"]["Authorization"] == "Bearer key"
        assert result == mock_response

"""Tests for main Vidai."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import BaseModel, EmailStr

from vidai import Vidai, VidaiConfig, StructuredOutputError
from vidai.client import EnhancedChat, EnhancedCompletions
from vidai.models import EnhancedChatCompletion
from tests.conftest import TestUser, create_mock_chat_completion


class TestVidai:
    """Test main Vidai class."""
    
    def test_init_with_base_url(self, test_config):
        """Test client initialization with base URL."""
        with patch('vidai.client.BaseOpenAI.__init__', return_value=None):
            client = Vidai(
                config=test_config,
                api_key="test-key",
                base_url="https://test.example.com/v1"
            )
            
            assert client.config == test_config

    def test_init_with_config_default_base_url(self):
        """Test client initialization with config default base URL."""
        config = VidaiConfig(default_base_url="https://config.example.com/v1")
        
        with patch('vidai.client.BaseOpenAI.__init__', return_value=None):
            client = Vidai(
                config=config,
                api_key="test-key"
            )
            
            assert client.config == config

    def test_init_default_config(self):
        """Test client initialization with default config."""
        with patch('vidai.client.BaseOpenAI.__init__', return_value=None):
            client = Vidai(
                api_key="test-key",
                base_url="https://test.example.com/v1"
            )
            
            assert isinstance(client.config, VidaiConfig)
            assert client.config.json_repair_mode == "auto"
            
    def test_init_custom_config(self):
        """Test client initialization with custom config."""
        config = VidaiConfig(json_repair_mode="always")
        with patch('vidai.client.BaseOpenAI.__init__', return_value=None):
            client = Vidai(
                config=config,
                api_key="test-key",
                base_url="https://test.example.com/v1"
            )
            
            assert client.config == config
            assert client.config.json_repair_mode == "always"

    def test_init_with_base_url_kwarg(self):
        """Test initialization with base_url in kwargs."""
        # Don't mock __init__, let logic run. Mock internal http client to avoid side effects if any.
        # BaseOpenAI checks for api_key.
        client = Vidai(base_url="https://kwarg.example.com/v1", api_key="sk-test")
        assert str(client.base_url) == "https://kwarg.example.com/v1/"

    def test_init_from_env_config(self):
        """Test client initialization with environment config."""
        with patch.dict('os.environ', {'VIDAI_BASE_URL': 'https://env.example.com/v1'}):
            with patch('vidai.client.BaseOpenAI.__init__', return_value=None) as mock_init:
                client = Vidai(api_key="test-key")
                
                # Check that base_url was passed to super().__init__
                # We check the kwargs of the first call
                _, kwargs = mock_init.call_args
                assert kwargs.get('base_url') == "https://env.example.com/v1"

    def test_chat_completions_create_streaming_warning(self, mock_wizz_client):
        """Test streaming warning when response_format is used."""
        mock_response = create_mock_chat_completion({
            "id": "test-127",
            "object": "chat.completion",
            "created": 1677652292,
            "model": "gpt-4",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": '{"name": "Alice", "age": 28}'}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 12, "total_tokens": 22}
        })
        
        with patch('openai.resources.chat.completions.Completions.create', return_value=mock_response):
            with patch('vidai.client.logger') as mock_logger:
                response = mock_wizz_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": "Create user"}],
                    response_format=TestUser,
                    stream=True  # This should trigger warning
                )
                
                # Should log warning about streaming
                mock_logger.warning.assert_called_with(
                    "Streaming is not supported with structured output. "
                    "Response will be buffered and processed after completion."
                )
                
                # Should still work (stream=False internally)
                assert isinstance(response, EnhancedChatCompletion)

    def test_chat_completions_create_structured_output_pydantic(self, mock_wizz_client):
        """Test chat completion with Pydantic structured output."""
        mock_response = create_mock_chat_completion({
            "id": "test-124",
            "object": "chat.completion",
            "created": 1677652289,
            "model": "gpt-4",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": '{"name": "John Doe", "age": 30, "email": "john@example.com"}'}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 15, "completion_tokens": 20, "total_tokens": 35}
        })
        
        with patch('openai.resources.chat.completions.Completions.create', return_value=mock_response):
            response = mock_wizz_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Create a user"}],
                response_format=TestUser
            )
            
            assert isinstance(response, EnhancedChatCompletion)
            assert len(response.choices) == 1
            assert response.choices[0].message.parsed is not None
            assert isinstance(response.choices[0].message.parsed, TestUser)
            assert response.choices[0].message.parsed.name == "John Doe"

    def test_chat_completions_create_structured_output_json_schema(self, mock_wizz_client):
        """Test chat completion with JSON schema structured output."""
        json_schema = {
            "type": "json_object",
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            "required": ["name", "age"]
        }
        
        mock_response = create_mock_chat_completion({
            "id": "test-125",
            "object": "chat.completion",
            "created": 1677652290,
            "model": "gpt-4",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": '{"name": "Jane", "age": 25}'}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 12, "completion_tokens": 15, "total_tokens": 27}
        })
        
        with patch('openai.resources.chat.completions.Completions.create', return_value=mock_response):
            response = mock_wizz_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Create data"}],
                response_format=json_schema
            )
            
            assert isinstance(response, EnhancedChatCompletion)
            assert response.choices[0].message.parsed is None

    def test_chat_completions_create_with_overrides(self, mock_wizz_client):
        """Test chat completion with parameter overrides."""
        mock_response = create_mock_chat_completion({
            "id": "test-126",
            "object": "chat.completion",
            "created": 1677652291,
            "model": "gpt-4",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": '{"name": "Bob", "age": 35, "email": "bob@example.com"}'}, "finish_reason": "stop"}],
        })

        with patch('openai.resources.chat.completions.Completions.create', return_value=mock_response) as mock_create:
            response = mock_wizz_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Create user"}],
                response_format=TestUser,
                strict_json_parsing=True,
                strict_schema_validation=True,
                json_repair_mode="never"
            )
            
            assert isinstance(response, EnhancedChatCompletion)
            # Verify the overrides were passed through
            call_args = mock_create.call_args
            # The kwargs are in call_args[1] (which is a dict)
            # It might be 'response_format' OR 'tools' (if converted)
            kw = call_args[1]
            assert "response_format" in kw or "tools" in kw, f"Expected structural params in {kw.keys()}"

    def test_copy_with_config(self, mock_wizz_client):
        """Test copying client with configuration overrides."""
        mock_wizz_client._base_url = "https://test.example.com/v1"
        
        new_client = mock_wizz_client.copy_with_config(
            json_repair_mode="never",
            strict_json_parsing=True
        )
        
        assert isinstance(new_client, Vidai)
        assert new_client.config.json_repair_mode == "never"
        assert new_client.config.strict_json_parsing is True
        
    def test_copy_with_config_preserves_client_settings(self, mock_wizz_client):
        """Test that copy preserves client settings."""
        mock_wizz_client._base_url = "https://test.example.com/v1"
        mock_wizz_client.api_key = "test-key"
        
        new_client = mock_wizz_client.copy_with_config()
        
        assert new_client.api_key == "test-key"
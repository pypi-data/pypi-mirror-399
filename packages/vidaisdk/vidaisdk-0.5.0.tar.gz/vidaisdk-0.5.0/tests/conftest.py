"""Test configuration and fixtures."""

import pytest
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch
from decimal import Decimal

from pydantic import BaseModel, Field, EmailStr

from vidai.config import VidaiConfig
from vidai import Vidai
from tests.mocks.responses import MOCK_RESPONSES


class TestUser(BaseModel):
    """Test Pydantic model for structured output testing."""
    name: str
    age: int
    email: EmailStr


class TestUserOptional(BaseModel):
    """Test Pydantic model with optional fields."""
    name: str
    age: int
    email: EmailStr
    phone: str = None


@pytest.fixture
def test_config():
    """Default test configuration."""
    return VidaiConfig(
        json_repair_mode="auto",
        json_repair_feedback=True,
        strict_json_parsing=False,
        strict_schema_validation=False,
        track_request_transformation=True,
        track_json_repair=True,
        log_level="WARNING"
    )


@pytest.fixture
def strict_config():
    """Strict test configuration."""
    return VidaiConfig(
        json_repair_mode="never",
        json_repair_feedback=True,
        strict_json_parsing=True,
        strict_schema_validation=True,
        track_request_transformation=True,
        track_json_repair=True,
        log_level="ERROR"
    )


@pytest.fixture
def mock_wizz_client(test_config):
    """Mock Vidai for testing."""
    with patch('vidai.client.BaseOpenAI.__init__', return_value=None):
        client = Vidai(
            config=test_config,
            api_key="test-key",
            base_url="https://test.example.com/v1"
        )
        # Mock the parent methods and attributes
        client._client = Mock()
        client._client.chat = Mock()
        client._client.chat.completions = Mock()
        client._client.chat.completions.create = Mock()
        # Mock required attributes
        client.max_retries = 3
        client._idempotency_key = None
        client._api_key_provider = None
        client._version = "1.0.0"
        client._platform = "python"
        client.api_key = "test-key"
        client._custom_headers = {}
        client._project = None
        client.organization = "test-org"
        client._base_url = "https://test.example.com/v1"
        client.timeout = 60.0
        return client



@pytest.fixture
def mock_response_data():
    """Mock response data for testing."""
    return MOCK_RESPONSES


@pytest.fixture
def sample_pydantic_model():
    """Sample Pydantic model for testing."""
    return TestUser


@pytest.fixture
def sample_json_schema():
    """Sample JSON schema for testing."""
    return {
        "type": "json_object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"}
        },
        "required": ["name", "age", "email"]
    }


@pytest.fixture
def valid_json_response():
    """Valid JSON response fixture."""
    return {
        "id": "test-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    }


@pytest.fixture
def invalid_json_response():
    """Invalid JSON response fixture."""
    return {
        "id": "test-124",
        "object": "chat.completion",
        "created": 1677652289,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"name": "John Doe", "age": 30, "email": "john@example.com",}'
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    }


@pytest.fixture
def non_json_response():
    """Non-JSON response fixture."""
    return {
        "id": "test-125",
        "object": "chat.completion",
        "created": 1677652290,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "I'm sorry, I cannot generate JSON content at this time."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    }


def create_mock_chat_completion(response_data: Dict[str, Any]):
    """Create a mock ChatCompletion object from response data."""
    from openai.types.chat import ChatCompletion
    
    mock_completion = Mock(spec=ChatCompletion)
    mock_completion.id = response_data["id"]
    mock_completion.object = response_data["object"]
    mock_completion.created = response_data["created"]
    mock_completion.model = response_data["model"]
    
    # Convert choices dicts to Mock objects
    choices = []
    for choice_data in response_data["choices"]:
        mock_choice = Mock()
        mock_choice.index = choice_data.get("index")
        mock_choice.finish_reason = choice_data.get("finish_reason")
        
        # Handle message object
        if "message" in choice_data:
            mock_message = Mock()
            mock_message.role = choice_data["message"].get("role")
            mock_message.content = choice_data["message"].get("content")
            mock_message.function_call = choice_data["message"].get("function_call")
            mock_message.tool_calls = choice_data["message"].get("tool_calls")
            mock_choice.message = mock_message
            
        choices.append(mock_choice)
        
    mock_completion.choices = choices
    mock_completion.usage = response_data.get("usage")
    
    # Add model_dump method
    mock_completion.model_dump.return_value = response_data
    
    return mock_completion
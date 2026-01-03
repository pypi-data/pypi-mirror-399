"""Tests for VLLMProvider."""

import pytest
from unittest.mock import MagicMock, patch
from vidai.providers.vllm import VLLMProvider
from vidai.config import VidaiConfig

@pytest.fixture
def config():
    return VidaiConfig()

@pytest.fixture
def provider(config):
    return VLLMProvider(config)

def test_properties_and_response(provider):
    """Test standard properties and pass-through response."""
    assert provider.should_use_tool_polyfill is False
    
    resp = {"choices": []}
    assert provider.transform_response(resp) == resp

def test_transform_request_guided_json_conversion(provider):
    """Test response_format is converted to guided_json."""
    messages = [{"role": "user", "content": "Hi"}]
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}}
    }
    
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "test_schema",
            "schema": schema,
            "strict": True
        }
    }
    
    kwargs = {
        "model": "vllm-model",
        "messages": messages,
        "response_format": response_format,
        "stream": False
    }
    
    new_kwargs = provider.transform_request(kwargs)
    
    # Check transformation
    assert "response_format" not in new_kwargs
    assert "extra_body" in new_kwargs
    assert new_kwargs["extra_body"]["guided_json"] == schema

def test_transform_request_no_structured_output(provider):
    """Test standard requests pass through untouched."""
    kwargs = {
        "model": "vllm-model",
        "messages": [{"role": "user", "content": "Hi"}],
        "stream": False
    }
    
    new_kwargs = provider.transform_request(kwargs.copy())
    
    # compare dicts equality
    assert new_kwargs == kwargs

def test_transform_request_merges_extra_body(provider):
    """Test guided_json is added without deleting existing extra_body."""
    schema = {"type": "object"}
    response_format = {
        "type": "json_schema",
        "json_schema": {"schema": schema}
    }
    
    kwargs = {
        "model": "vllm-model", 
        "response_format": response_format,
        "extra_body": {"existing_param": "foo"}
    }
    
    new_kwargs = provider.transform_request(kwargs)
    
    assert new_kwargs["extra_body"]["existing_param"] == "foo"
    assert new_kwargs["extra_body"]["guided_json"] == schema

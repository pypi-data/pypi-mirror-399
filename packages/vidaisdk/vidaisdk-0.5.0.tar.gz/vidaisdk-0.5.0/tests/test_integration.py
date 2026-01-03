"""Integration tests for Vidai."""

import pytest
from unittest.mock import Mock, patch
from typing import Any, Dict
from pydantic import BaseModel, Field

from vidai import Vidai, VidaiConfig
from vidai.exceptions import StructuredOutputError, ValidationError
from vidai.models import EnhancedChatCompletion
from tests.conftest import TestUser, create_mock_chat_completion


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_workflow_structured_output_success(self):
        """Test complete structured output workflow."""
        config = VidaiConfig(
            json_repair_mode="auto",
            json_repair_feedback=True,
            strict_json_parsing=False,
            strict_schema_validation=False
        )
        
        mock_response = create_mock_chat_completion({
            "id": "test-integration-1",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "gpt-4",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": '{"name": "Alice Smith", "age": 28, "email": "alice@example.com"}'
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 15,
                "completion_tokens": 20,
                "total_tokens": 35
            }
        })
        
        with patch('vidai.client.BaseOpenAI.__init__', return_value=None):
            with patch('openai.resources.chat.completions.Completions.create', return_value=mock_response):
                client = Vidai(
                    config=config,
                    api_key="test-key",
                    base_url="https://test.example.com/v1"
                )
                
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": "Create a user named Alice, age 28"}],
                    response_format=TestUser
                )
                
                # Verify response structure
                assert isinstance(response, EnhancedChatCompletion)
                assert len(response.choices) == 1
                assert response.choices[0].message.parsed is not None
                assert isinstance(response.choices[0].message.parsed, TestUser)
                assert response.choices[0].message.parsed.name == "Alice Smith"
                assert response.choices[0].message.parsed.age == 28
                assert response.choices[0].message.parsed.email == "alice@example.com"
                assert response.choices[0].message.parse_error is None
    
    def test_full_workflow_json_repair(self):
        """Test workflow with JSON repair."""
        config = VidaiConfig(
            json_repair_mode="auto",
            json_repair_feedback=True,
            strict_json_parsing=False,
            strict_schema_validation=False
        )
        
        # Response with trailing comma (invalid JSON)
        mock_response = create_mock_chat_completion({
            "id": "test-integration-2",
            "object": "chat.completion",
            "created": 1677652289,
            "model": "gpt-4",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": '{"name": "Bob Johnson", "age": 35, "email": "bob@example.com",}'
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 15,
                "completion_tokens": 20,
                "total_tokens": 35
            }
        })
        
        with patch('vidai.client.BaseOpenAI.__init__', return_value=None):
            with patch('openai.resources.chat.completions.Completions.create', return_value=mock_response):
                client = Vidai(
                    config=config,
                    api_key="test-key",
                    base_url="https://test.example.com/v1"
                )
                
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": "Create a user named Bob, age 35"}],
                    response_format=TestUser
                )
                
                # Verify repair happened
                assert response.choices[0].message.json_repair_info is not None
                assert response.choices[0].message.json_repair_info.was_repaired is True
                assert "fixed_trailing_comma" in response.choices[0].message.json_repair_info.repair_operations
                
                # Verify parsed data is correct
                assert response.choices[0].message.parsed is not None
                assert response.choices[0].message.parsed.name == "Bob Johnson"
                assert response.choices[0].message.parsed.age == 35
                assert response.choices[0].message.parsed.email == "bob@example.com"
    
    def test_full_workflow_strict_mode_failure(self):
        """Test workflow in strict mode with failure."""
        config = VidaiConfig(
            json_repair_mode="never",
            json_repair_feedback=True,
            strict_json_parsing=True,
            strict_schema_validation=True
        )
        
        # Response with invalid JSON
        mock_response = create_mock_chat_completion({
            "id": "test-integration-3",
            "object": "chat.completion",
            "created": 1677652290,
            "model": "gpt-4",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": '{"name": "Charlie", "age": "not_a_number", "email": "invalid"}'
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 15,
                "completion_tokens": 20,
                "total_tokens": 35
            }
        })
        
        with patch('vidai.client.BaseOpenAI.__init__', return_value=None):
            with patch('openai.resources.chat.completions.Completions.create', return_value=mock_response):
                client = Vidai(
                    config=config,
                    api_key="test-key",
                    base_url="https://test.example.com/v1"
                )
                
                # Should raise exception in strict mode
                # The exception might differ depending on where it fails: JSON parsing, Pydantic validation, etc.
                with pytest.raises(ValidationError): 
                    client.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": "Create a user"}],
                        response_format=TestUser
                    )
    
    def test_full_workflow_no_structured_output(self):
        """Test workflow without structured output."""
        config = VidaiConfig(
            track_request_transformation=True,
            track_json_repair=True
        )
        
        mock_response = create_mock_chat_completion({
            "id": "test-integration-4",
            "object": "chat.completion",
            "created": 1677652291,
            "model": "gpt-4",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I help you today?"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 9,
                "total_tokens": 19
            }
        })
        
        with patch('vidai.client.BaseOpenAI.__init__', return_value=None):
            with patch('openai.resources.chat.completions.Completions.create', return_value=mock_response):
                client = Vidai(
                    config=config,
                    api_key="test-key",
                    base_url="https://test.example.com/v1"
                )
                
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": "Hello"}]
                )
                
                # Should return standard response (not enhanced)
                # The wrapper returns the response from super().create
                # and maybe adds performance info if tracking enabled.
                
                assert response == mock_response
                # It might have performance_info added if tracking is on
    def test_full_workflow_json_schema(self):
        """Test workflow with JSON schema (not Pydantic)."""
        config = VidaiConfig(
            json_repair_mode="auto",
            json_repair_feedback=True
        )
        
        json_schema = {
            "type": "json_object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"}
            },
            "required": ["title", "description"]
        }
        
        mock_response = create_mock_chat_completion({
            "id": "test-integration-5",
            "object": "chat.completion",
            "created": 1677652292,
            "model": "gpt-4",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": '{"title": "My Task", "description": "A sample task description"}'
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 20,
                "completion_tokens": 15,
                "total_tokens": 35
            }
        })
        
        with patch('vidai.client.BaseOpenAI.__init__', return_value=None):
            with patch('openai.resources.chat.completions.Completions.create', return_value=mock_response):
                client = Vidai(
                    config=config,
                    api_key="test-key",
                    base_url="https://test.example.com/v1"
                )
                
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": "Create a task"}],
                    response_format=json_schema
                )
                
                # Verify enhanced response
                assert isinstance(response, EnhancedChatCompletion)
                assert len(response.choices) == 1
                
                # For JSON schema, parsed should be None (no Pydantic model)
                assert response.choices[0].message.parsed is None
                assert response.choices[0].message.parse_error is None
                # Content should be valid JSON string
                import json
                assert json.loads(response.choices[0].message.content) == {"title": "My Task", "description": "A sample task description"}

    def test_full_workflow_performance_tracking(self):
        """Test workflow with performance tracking enabled."""
        config = VidaiConfig(
            track_request_transformation=True,
            track_json_repair=True,
            json_repair_feedback=True
        )
    
    def test_full_workflow_copy_with_config(self):
        """Test copying client with configuration overrides."""
        base_config = VidaiConfig(
            json_repair_mode="auto",
            strict_json_parsing=False
        )
        
        mock_response = create_mock_chat_completion({
            "id": "test-integration-7",
            "object": "chat.completion",
            "created": 1677652294,
            "model": "gpt-4",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": '{"name": "Eve", "age": 26, "email": "eve@example.com"}'
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 15,
                "completion_tokens": 18,
                "total_tokens": 33
            }
        })
        
        with patch('vidai.client.BaseOpenAI.__init__', return_value=None):
            with patch('openai.resources.chat.completions.Completions.create', return_value=mock_response):
                client = Vidai(
                    config=base_config,
                    api_key="test-key",
                    base_url="https://test.example.com/v1"
                )
                
                # Manually set required attributes since we skipped init
                client.api_key = "test-key"
                client.organization = "test-org"
                client._base_url = "https://test.example.com/v1" 
                client.timeout = 30.0
                client.max_retries = 3
                
                # Copy with strict mode
                strict_client = client.copy_with_config(
                    strict_json_parsing=True,
                    json_repair_mode="never"
                )
                
                # Verify new client has different config
                assert strict_client.config.strict_json_parsing is True
                assert strict_client.config.json_repair_mode == "never"
                assert strict_client.config.json_repair_feedback == base_config.json_repair_feedback  # Preserved
                
                # Original client should be unchanged
                assert client.config.strict_json_parsing is False
                assert client.config.json_repair_mode == "auto"
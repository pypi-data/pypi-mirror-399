"""Tests for all 5 provider mock responses."""

import pytest

from tests.mocks.responses import (
    MOCK_RESPONSES,
    OPENAI_RESPONSES,
    ANTHROPIC_RESPONSES,
    MISTRAL_RESPONSES,
    GEMINI_RESPONSES,
    VLLM_RESPONSES,
    TEST_USER_SCHEMA,
    INVALID_JSON_SAMPLES,
    VALID_JSON_SAMPLES
)
from vidai.utils import extract_json_from_response


class TestMockResponses:
    """Test mock response data for all providers."""
    
    def test_mock_responses_structure(self):
        """Test that mock responses have correct structure."""
        assert "openai" in MOCK_RESPONSES
        assert "anthropic" in MOCK_RESPONSES
        assert "mistral" in MOCK_RESPONSES
        assert "gemini" in MOCK_RESPONSES
        assert "vllm" in MOCK_RESPONSES
        
        # Each provider should have required response types
        for provider, responses in MOCK_RESPONSES.items():
            assert "valid_json" in responses
            assert "invalid_json" in responses or any("invalid" in key for key in responses.keys())
    
    def test_openai_responses(self):
        """Test OpenAI mock responses."""
        responses = OPENAI_RESPONSES
        
        # Valid JSON response
        valid = responses["valid_json"]
        assert "choices" in valid
        assert valid["choices"][0]["message"]["content"] == '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
        
        # Invalid JSON with trailing comma
        invalid_trailing = responses["invalid_json_trailing_comma"]
        assert invalid_trailing["choices"][0]["message"]["content"].endswith(',}')
        
        # Invalid JSON with single quotes
        invalid_single = responses["invalid_json_single_quotes"]
        config = invalid_single["choices"][0]["message"]["content"]
        assert config.startswith("{")
        assert "'" in config
        assert '"' not in config
        
        # Non-JSON content
        non_json = responses["non_json_content"]
        assert "I'm sorry" in non_json["choices"][0]["message"]["content"]
    
    def test_anthropic_responses(self):
        """Test Anthropic mock responses."""
        responses = ANTHROPIC_RESPONSES
        
        # Valid JSON response
        valid = responses["valid_json"]
        assert "content" in valid
        assert isinstance(valid["content"], list)
        assert valid["content"][0]["type"] == "text"
        assert '"name": "John Doe"' in valid["content"][0]["text"]
        
        # Tool call format
        tool_call = responses["tool_call_format"]
        assert tool_call["content"][0]["type"] == "tool_use"
        assert "input" in tool_call["content"][0]
        assert isinstance(tool_call["content"][0]["input"], dict)
    
    def test_mistral_responses(self):
        """Test Mistral mock responses."""
        responses = MISTRAL_RESPONSES
        
        # Valid JSON response
        valid = responses["valid_json"]
        assert "choices" in valid
        assert valid["choices"][0]["message"]["role"] == "assistant"
        
        # Guided decoding response
        guided = responses["guided_decoding"]
        assert "choices" in guided
        assert '"name": "John Doe"' in guided["choices"][0]["message"]["content"]
    
    def test_gemini_responses(self):
        """Test Gemini mock responses."""
        responses = GEMINI_RESPONSES
        
        # Valid JSON response
        valid = responses["valid_json"]
        assert "candidates" in valid
        assert isinstance(valid["candidates"], list)
        assert len(valid["candidates"]) > 0
        
        candidate = valid["candidates"][0]
        assert "content" in candidate
        assert "parts" in candidate["content"]
        assert isinstance(candidate["content"]["parts"], list)
        assert "text" in candidate["content"]["parts"][0]
    
    def test_vllm_responses(self):
        """Test VLLM mock responses."""
        responses = VLLM_RESPONSES
        
        # Valid JSON response
        valid = responses["valid_json"]
        assert "choices" in valid
        assert valid["model"] == "llama-3-8b-instruct"
        assert '"name": "John Doe"' in valid["choices"][0]["message"]["content"]
        
        # Guided JSON response
        guided = responses["guided_json"]
        assert "choices" in guided
        assert guided["choices"][0]["message"]["role"] == "assistant"
    
    def test_json_extraction_openai(self):
        """Test JSON extraction from OpenAI responses."""
        response = OPENAI_RESPONSES["valid_json"]
        json_content = extract_json_from_response(response)
        
        assert json_content is not None
        assert json_content == '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
    
    def test_json_extraction_anthropic(self):
        """Test JSON extraction from Anthropic responses."""
        response = ANTHROPIC_RESPONSES["valid_json"]
        json_content = extract_json_from_response(response)
        
        assert json_content is not None
        assert json_content == '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
    
    def test_json_extraction_anthropic_tool_use(self):
        """Test JSON extraction from Anthropic tool_use responses."""
        response = ANTHROPIC_RESPONSES["tool_call_format"]
        json_content = extract_json_from_response(response)
        
        assert json_content is not None
        assert json_content == '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
    
    def test_json_extraction_gemini(self):
        """Test JSON extraction from Gemini responses."""
        response = GEMINI_RESPONSES["valid_json"]
        json_content = extract_json_from_response(response)
        
        assert json_content is not None
        assert json_content == '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
    
    def test_json_extraction_vllm(self):
        """Test JSON extraction from VLLM responses."""
        response = VLLM_RESPONSES["valid_json"]
        json_content = extract_json_from_response(response)
        
        assert json_content is not None
        assert json_content == '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
    
    def test_invalid_json_samples(self):
        """Test invalid JSON sample data."""
        assert len(INVALID_JSON_SAMPLES) > 0
        
        for invalid_json in INVALID_JSON_SAMPLES:
            # All should be invalid JSON
            import json
            with pytest.raises(json.JSONDecodeError):
                json.loads(invalid_json)
    
    def test_valid_json_samples(self):
        """Test valid JSON sample data."""
        assert len(VALID_JSON_SAMPLES) > 0
        
        for valid_json in VALID_JSON_SAMPLES:
            # All should be valid JSON
            import json
            parsed = json.loads(valid_json)
            assert isinstance(parsed, dict)
            assert "name" in parsed
            assert "age" in parsed
    
    def test_test_user_schema(self):
        """Test test user schema."""
        assert TEST_USER_SCHEMA["type"] == "json_object"
        assert "properties" in TEST_USER_SCHEMA
        assert "name" in TEST_USER_SCHEMA["properties"]
        assert "age" in TEST_USER_SCHEMA["properties"]
        assert "email" in TEST_USER_SCHEMA["properties"]
        assert "required" in TEST_USER_SCHEMA
        assert "name" in TEST_USER_SCHEMA["required"]
        assert "age" in TEST_USER_SCHEMA["required"]
        assert "email" in TEST_USER_SCHEMA["required"]
    
    def test_streaming_responses(self):
        """Test streaming response data."""
        # OpenAI streaming
        openai_streaming = OPENAI_RESPONSES.get("streaming_valid")
        if openai_streaming:
            assert isinstance(openai_streaming, list)
            assert len(openai_streaming) > 0
            assert any("data:" in chunk for chunk in openai_streaming)
        
        # Anthropic streaming
        anthropic_streaming = ANTHROPIC_RESPONSES.get("streaming_valid")
        if anthropic_streaming:
            assert isinstance(anthropic_streaming, list)
            assert len(anthropic_streaming) > 0
            assert any("event:" in chunk for chunk in anthropic_streaming)
    
    def test_response_consistency(self):
        """Test that all providers have consistent valid JSON content."""
        expected_json = '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
        
        providers = ["openai", "anthropic", "mistral", "gemini", "vllm"]
        
        for provider in providers:
            if provider in MOCK_RESPONSES:
                response = MOCK_RESPONSES[provider]["valid_json"]
                json_content = extract_json_from_response(response)
                
                # All should extract the same JSON content
                assert json_content == expected_json, f"Provider {provider} has different JSON content"
    
    def test_response_structure_completeness(self):
        """Test that all responses have required fields."""
        required_fields = ["id", "object", "created", "model"]
        
        for provider_name, responses in MOCK_RESPONSES.items():
            for response_name, response in responses.items():
                if isinstance(response, dict) and "choices" in response:
                    # OpenAI-style response
                    for field in required_fields:
                        assert field in response, f"{provider_name}.{response_name} missing {field}"
                    
                    # Check choices structure
                    assert "choices" in response
                    assert len(response["choices"]) > 0
                    choice = response["choices"][0]
                    assert "message" in choice or "delta" in choice
                    
                    if "message" in choice:
                        assert "role" in choice["message"]
                        assert "content" in choice["message"] or choice["message"].get("content") is None
                
                elif isinstance(response, dict) and "candidates" in response:
                    # Gemini-style response
                    assert "candidates" in response
                    assert len(response["candidates"]) > 0
                    candidate = response["candidates"][0]
                    assert "content" in candidate
                    assert "parts" in candidate["content"]
                    assert len(candidate["content"]["parts"]) > 0
"""Tests for Vidai models."""

import pytest
from pydantic import BaseModel, EmailStr, ValidationError

from vidai.models import (
    EnhancedChatCompletionMessage,
    JsonRepairInfo,
    PerformanceInfo,
    StructuredOutputRequest,
    ProxyHeaders
)
from tests.conftest import TestUser


class TestJsonRepairInfo:
    """Test JsonRepairInfo class."""
    
    def test_init_repaired(self):
        """Test initialization for repaired JSON."""
        info = JsonRepairInfo(
            was_repaired=True,
            repair_time_ms=2.5,
            repair_operations=["fixed_trailing_comma", "added_missing_quotes"],
            original_error="Invalid JSON"
        )
        
        assert info.was_repaired is True
        assert info.repair_time_ms == 2.5
        assert len(info.repair_operations) == 2
        assert "fixed_trailing_comma" in info.repair_operations
        assert "added_missing_quotes" in info.repair_operations
        assert info.original_error == "Invalid JSON"
    
    def test_init_not_repaired(self):
        """Test initialization for non-repaired JSON."""
        info = JsonRepairInfo(
            was_repaired=False,
            repair_time_ms=0.0,
            repair_operations=[]
        )
        
        assert info.was_repaired is False
        assert info.repair_time_ms == 0.0
        assert info.repair_operations == []
        assert info.original_error is None
    
    def test_equality(self):
        """Test JsonRepairInfo equality."""
        info1 = JsonRepairInfo(
            was_repaired=True,
            repair_time_ms=2.5,
            repair_operations=["fixed_trailing_comma"]
        )
        info2 = JsonRepairInfo(
            was_repaired=True,
            repair_time_ms=2.5,
            repair_operations=["fixed_trailing_comma"]
        )
        info3 = JsonRepairInfo(
            was_repaired=False,
            repair_time_ms=0.0,
            repair_operations=[]
        )
        
        assert info1 == info2
        assert info1 != info3
    
    def test_repr(self):
        """Test JsonRepairInfo string representation."""
        info = JsonRepairInfo(
            was_repaired=True,
            repair_time_ms=2.5,
            repair_operations=["fixed_trailing_comma"]
        )
        
        repr_str = repr(info)
        assert "JsonRepairInfo(" in repr_str
        assert "was_repaired=True" in repr_str
        assert "repair_time_ms=2.5" in repr_str
        assert "fixed_trailing_comma" in repr_str


class TestPerformanceInfo:
    """Test PerformanceInfo class."""
    
    def test_init_all_values(self):
        """Test initialization with all values."""
        info = PerformanceInfo(
            request_transformation_time_ms=1.5,
            json_repair_time_ms=2.3,
            total_sdk_overhead_ms=5.8
        )
        
        assert info.request_transformation_time_ms == 1.5
        assert info.json_repair_time_ms == 2.3
        assert info.total_sdk_overhead_ms == 5.8
    
    def test_init_partial_values(self):
        """Test initialization with partial values."""
        info = PerformanceInfo(
            request_transformation_time_ms=1.5
        )
        
        assert info.request_transformation_time_ms == 1.5
        assert info.json_repair_time_ms is None
        assert info.total_sdk_overhead_ms is None
    
    def test_init_default(self):
        """Test default initialization."""
        info = PerformanceInfo()
        
        assert info.request_transformation_time_ms is None
        assert info.json_repair_time_ms is None
        assert info.total_sdk_overhead_ms is None
    
    def test_repr(self):
        """Test PerformanceInfo string representation."""
        info = PerformanceInfo(
            request_transformation_time_ms=1.5,
            json_repair_time_ms=2.3,
            total_sdk_overhead_ms=5.8
        )
        
        repr_str = repr(info)
        assert "PerformanceInfo(" in repr_str
        assert "request_transformation_time_ms=1.5" in repr_str
        assert "json_repair_time_ms=2.3" in repr_str
        assert "total_sdk_overhead_ms=5.8" in repr_str


class TestStructuredOutputRequest:
    """Test StructuredOutputRequest class."""
    
    def test_init_pydantic_model(self):
        """Test initialization with Pydantic model."""
        request = StructuredOutputRequest(TestUser)
        
        assert request.response_format == TestUser
        assert request.is_pydantic_model is True
        assert request.is_json_schema is False
        assert request.strict_json_parsing is None
        assert request.strict_schema_validation is None
        assert request.json_repair_mode is None
    
    def test_init_json_schema(self):
        """Test initialization with JSON schema."""
        schema = {"type": "json_object", "properties": {"name": {"type": "string"}}}
        request = StructuredOutputRequest(schema)
        
        assert request.response_format == schema
        assert request.is_pydantic_model is False
        assert request.is_json_schema is True
        assert request.strict_json_parsing is None
        assert request.strict_schema_validation is None
        assert request.json_repair_mode is None
    
    def test_init_with_overrides(self):
        """Test initialization with parameter overrides."""
        request = StructuredOutputRequest(
            TestUser,
            strict_json_parsing=True,
            strict_schema_validation=True,
            json_repair_mode="never"
        )
        
        assert request.strict_json_parsing is True
        assert request.strict_schema_validation is True
        assert request.json_repair_mode == "never"
    
    def test_invalid_response_format_not_model(self):
        """Test invalid response format (not a model)."""
        with pytest.raises(ValueError, match="response_format must be a Pydantic BaseModel class"):
            StructuredOutputRequest("not_a_model")
    
    def test_invalid_response_format_not_subclass(self):
        """Test invalid response format (not a BaseModel subclass)."""
        class NotBaseModel:
            pass
        
        with pytest.raises(ValueError, match="response_format must be a Pydantic BaseModel class"):
            StructuredOutputRequest(NotBaseModel)
    
    def test_invalid_json_schema_type(self):
        """Test invalid JSON schema (wrong type)."""
        schema = {"type": "invalid_type"}
        
        with pytest.raises(ValueError, match="response_format dict must have type"):
            StructuredOutputRequest(schema)
    
    def test_invalid_json_schema_missing_type(self):
        """Test invalid JSON schema (missing type)."""
        schema = {"properties": {"name": {"type": "string"}}}
        
        with pytest.raises(ValueError, match="response_format dict must have type"):
            StructuredOutputRequest(schema)
    
    def test_valid_json_schema_types(self):
        """Test valid JSON schema types."""
        for schema_type in ["json_object", "json_schema"]:
            schema = {"type": schema_type, "properties": {"name": {"type": "string"}}}
            request = StructuredOutputRequest(schema)
            
            assert request.is_json_schema is True
            assert request.response_format == schema


class TestEnhancedChatCompletionMessage:
    """Test EnhancedChatCompletionMessage class."""
    
    def test_init_minimal(self):
        """Test minimal initialization."""
        message = EnhancedChatCompletionMessage(role="assistant")
        
        assert message.role == "assistant"
        assert message.content is None
        assert message.parsed is None
        assert message.parse_error is None
        assert message.json_repair_info is None
        assert message.performance_info is None
    
    def test_init_full(self):
        """Test full initialization."""
        parsed_user = TestUser(name="John", age=30, email="john@example.com")
        repair_info = JsonRepairInfo(
            was_repaired=True,
            repair_time_ms=2.5,
            repair_operations=["fixed_trailing_comma"]
        )
        perf_info = PerformanceInfo(total_sdk_overhead_ms=5.0)
        
        message = EnhancedChatCompletionMessage(
            content="Hello",
            role="assistant",
            function_call={"name": "test", "arguments": "{}"},
            tool_calls=[{
                "id": "call_123",
                "type": "function",
                "function": {"name": "test_tool", "arguments": "{}"}
            }],
            parsed=parsed_user,
            parse_error=None,
            json_repair_info=repair_info,
            performance_info=perf_info
        )
        
        assert message.content == "Hello"
        assert message.role == "assistant"
        assert message.function_call.name == "test"
        assert message.tool_calls[0].id == "call_123"
        assert message.parsed == parsed_user
        assert message.parse_error is None
        assert message.json_repair_info == repair_info
        assert message.performance_info == perf_info
    
    def test_init_with_parse_error(self):
        """Test initialization with parse error."""
        error = ValueError("Parse failed")
        
        message = EnhancedChatCompletionMessage(
            content="Invalid content",
            role="assistant",
            parse_error=error
        )
        
        assert message.content == "Invalid content"
        assert message.role == "assistant"
        assert message.parse_error == error
        assert message.parsed is None
    
    def test_inheritance_from_openai(self):
        """Test that it properly inherits from OpenAI ChatCompletionMessage."""
        message = EnhancedChatCompletionMessage(
            content="Hello",
            role="assistant"
        )
        
        # Should have all the OpenAI message attributes
        assert hasattr(message, 'content')
        assert hasattr(message, 'role')
        assert hasattr(message, 'function_call')
        assert hasattr(message, 'tool_calls')


class TestProxyHeaders:
    """Test ProxyHeaders class."""
    
    def test_to_dict_defaults(self):
        """Test conversion to dict with defaults."""
        headers = ProxyHeaders(
            provider="openai",
            model="gpt-4o"
        )
        
        header_dict = headers.to_dict()
        
        assert header_dict["x-vidai-provider"] == "openai"
        assert header_dict["x-vidai-model"] == "gpt-4o"
        assert header_dict["x-vidai-version"] == "0.5.0"
        
    def test_to_dict_custom_version(self):
        """Test conversion to dict with custom version."""
        headers = ProxyHeaders(
            provider="anthropic",
            model="claude-3",
            version="1.2.3"
        )
        
        header_dict = headers.to_dict()
        
        assert header_dict["x-vidai-provider"] == "anthropic"
        assert header_dict["x-vidai-model"] == "claude-3"
        assert header_dict["x-vidai-version"] == "1.2.3"
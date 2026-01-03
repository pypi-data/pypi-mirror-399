"""Tests for Vidai exceptions."""

import pytest

from vidai.exceptions import (
    VidaiError,
    StructuredOutputError,
    JSONRepairError,
    ValidationError,
    ConfigurationError,
    PerformanceError
)


class TestVidaiError:
    """Test base VidaiError class."""
    
    def test_init_minimal(self):
        """Test minimal initialization."""
        error = VidaiError("Test error")
        
        assert str(error) == "Test error"
        assert error.provider is None
        assert error.model is None
        assert error.raw_response is None
    
    def test_init_full(self):
        """Test full initialization."""
        raw_response = {"id": "test", "content": "data"}
        error = VidaiError(
            "Test error",
            provider="openai",
            model="gpt-4",
            raw_response=raw_response
        )
        
        assert str(error) == "Test error"
        assert error.provider == "openai"
        assert error.model == "gpt-4"
        assert error.raw_response == raw_response
    
    def test_inheritance(self):
        """Test that VidaiError inherits from Exception."""
        error = VidaiError("Test")
        
        assert isinstance(error, Exception)
        assert isinstance(error, BaseException)


class TestStructuredOutputError:
    """Test StructuredOutputError class."""
    
    def test_init_minimal(self):
        """Test minimal initialization."""
        error = StructuredOutputError("Structured output failed")
        
        assert str(error) == "Structured output failed"
        assert error.raw_content is None
        assert error.validation_error is None
        assert error.provider is None
        assert error.model is None
    
    def test_init_full(self):
        """Test full initialization."""
        validation_error = ValueError("Validation failed")
        error = StructuredOutputError(
            "Structured output failed",
            raw_content='{"invalid": json}',
            validation_error=validation_error,
            provider="anthropic",
            model="claude-3-5-sonnet"
        )
        
        assert str(error) == "Structured output failed"
        assert error.raw_content == '{"invalid": json}'
        assert error.validation_error == validation_error
        assert error.provider == "anthropic"
        assert error.model == "claude-3-5-sonnet"
    
    def test_inheritance(self):
        """Test that StructuredOutputError inherits from VidaiError."""
        error = StructuredOutputError("Test")
        
        assert isinstance(error, VidaiError)
        assert isinstance(error, Exception)


class TestJSONRepairError:
    """Test JSONRepairError class."""
    
    def test_init_minimal(self):
        """Test minimal initialization."""
        error = JSONRepairError("JSON repair failed")
        
        assert str(error) == "JSON repair failed"
        assert error.original_error is None
        assert error.provider is None
        assert error.model is None
    
    def test_init_full(self):
        """Test full initialization."""
        original_error = ValueError("Original error")
        error = JSONRepairError(
            "JSON repair failed",
            original_error=original_error,
            provider="mistral",
            model="mistral-large"
        )
        
        assert str(error) == "JSON repair failed"
        assert error.original_error == original_error
        assert error.provider == "mistral"
        assert error.model == "mistral-large"
    
    def test_inheritance(self):
        """Test that JSONRepairError inherits from VidaiError."""
        error = JSONRepairError("Test")
        
        assert isinstance(error, VidaiError)
        assert isinstance(error, Exception)


class TestValidationError:
    """Test ValidationError class."""
    
    def test_init_minimal(self):
        """Test minimal initialization."""
        error = ValidationError("Validation failed")
        
        assert str(error) == "Validation failed"
        assert error.pydantic_error is None
        assert error.provider is None
        assert error.model is None
    
    def test_init_full(self):
        """Test full initialization."""
        pydantic_error = ValueError("Pydantic error")
        error = ValidationError(
            "Validation failed",
            pydantic_error=pydantic_error,
            provider="gemini",
            model="gemini-pro"
        )
        
        assert str(error) == "Validation failed"
        assert error.pydantic_error == pydantic_error
        assert error.provider == "gemini"
        assert error.model == "gemini-pro"
    
    def test_inheritance(self):
        """Test that ValidationError inherits from VidaiError."""
        error = ValidationError("Test")
        
        assert isinstance(error, VidaiError)
        assert isinstance(error, Exception)


class TestConfigurationError:
    """Test ConfigurationError class."""
    
    def test_init(self):
        """Test initialization."""
        error = ConfigurationError("Configuration invalid")
        
        assert str(error) == "Configuration invalid"
    
    def test_inheritance(self):
        """Test that ConfigurationError inherits from VidaiError."""
        error = ConfigurationError("Test")
        
        assert isinstance(error, VidaiError)
        assert isinstance(error, Exception)


class TestPerformanceError:
    """Test PerformanceError class."""
    
    def test_init_minimal(self):
        """Test minimal initialization."""
        error = PerformanceError("Performance error")
        
        assert str(error) == "Performance error"
        assert error.operation is None
        assert error.timing_data is None
    
    def test_init_full(self):
        """Test full initialization."""
        timing_data = {"duration_ms": 5.2, "operation": "test"}
        error = PerformanceError(
            "Performance error",
            operation="test_operation",
            timing_data=timing_data
        )
        
        assert str(error) == "Performance error"
        assert error.operation == "test_operation"
        assert error.timing_data == timing_data
    
    def test_inheritance(self):
        """Test that PerformanceError inherits from VidaiError."""
        error = PerformanceError("Test")
        
        assert isinstance(error, VidaiError)
        assert isinstance(error, Exception)


class TestExceptionHierarchy:
    """Test exception hierarchy and relationships."""
    
    def test_all_inherit_from_wizz_error(self):
        """Test that all custom exceptions inherit from VidaiError."""
        exceptions = [
            StructuredOutputError,
            JSONRepairError,
            ValidationError,
            ConfigurationError,
            PerformanceError
        ]
        
        for exc_class in exceptions:
            # Should inherit from VidaiError
            assert issubclass(exc_class, VidaiError)
            # Should inherit from Exception
            assert issubclass(exc_class, Exception)
    
    def test_wizz_error_inheritance(self):
        """Test VidaiError inheritance."""
        assert issubclass(VidaiError, Exception)
        assert issubclass(VidaiError, BaseException)
    
    def test_exception_chaining(self):
        """Test exception chaining works correctly."""
        original_error = ValueError("Original")
        
        # Test with from_exception
        try:
            raise JSONRepairError("Wrapped error") from original_error
        except JSONRepairError as e:
            assert e.__cause__ is original_error
            assert str(e) == "Wrapped error"
    
    def test_exception_attributes_preserved(self):
        """Test that exception attributes are preserved."""
        raw_response = {"test": "data"}
        validation_error = ValueError("Validation failed")
        
        error = StructuredOutputError(
            "Test error",
            raw_content='{"test": "data"}',
            validation_error=validation_error,
            provider="openai",
            model="gpt-4"
        )
        
        # All attributes should be accessible
        assert error.raw_content == '{"test": "data"}'
        assert error.validation_error == validation_error
        assert error.provider == "openai"
        assert error.model == "gpt-4"
        assert error.raw_response is None  # Not set in this exception type
    
    def test_exception_repr(self):
        """Test exception string representations."""
        error = VidaiError(
            "Test message",
            provider="openai",
            model="gpt-4"
        )
        
        # Should include the message
        assert "Test message" in str(error)
        assert "Test message" in repr(error)
"""Custom exceptions for Vidai."""

from typing import Any, Dict, Optional


class VidaiError(Exception):
    """Base exception for all Vidai errors."""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        raw_response: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.model = model
        self.raw_response = raw_response

# Alias for backward compatibility
VidaiClientError = VidaiError


class StructuredOutputError(VidaiError):
    """Raised when structured output processing fails in strict mode."""
    
    def __init__(
        self,
        message: str,
        raw_content: Optional[str] = None,
        validation_error: Optional[Exception] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        super().__init__(message, provider=provider, model=model)
        self.raw_content = raw_content
        self.validation_error = validation_error


class JSONRepairError(VidaiError):
    """Raised when JSON repair fails."""
    
    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        super().__init__(message, provider=provider, model=model)
        self.original_error = original_error


class ValidationError(VidaiError):
    """Raised when Pydantic schema validation fails."""
    
    def __init__(
        self,
        message: str,
        pydantic_error: Optional[Exception] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        super().__init__(message, provider=provider, model=model)
        self.pydantic_error = pydantic_error


class ConfigurationError(VidaiError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str) -> None:
        super().__init__(message)


class PerformanceError(VidaiError):
    """Raised when performance tracking encounters issues."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        timing_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.operation = operation
        self.timing_data = timing_data
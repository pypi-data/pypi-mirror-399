"""Structured output processing engine for Vidai."""

import json
import time
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from pydantic import BaseModel

from .config import VidaiConfig
from .exceptions import StructuredOutputError, ValidationError as VidaiValidationError
from .models import (
    EnhancedChatCompletionMessage,
    JsonRepairInfo,
    PerformanceInfo,
    StructuredOutputRequest
)
from .performance import PerformanceTracker
from .utils import (
    extract_json_from_response,
    is_valid_json,
    repair_json_string,
    validate_pydantic_model,
    setup_logging,
    logger
)


from .providers import BaseProvider

class StructuredOutputProcessor:
    """Handles structured output processing logic."""
    
    def __init__(self, config: VidaiConfig, provider: Optional[Any] = None) -> None:
        """Initialize structured output processor.
        
        Args:
            config: Configuration settings
            provider: Provider adapter instance
        """
        self.config = config
        self.provider = provider
    
    def process_request(
        self,
        *,
        response_format: Union[Type[BaseModel], Dict[str, Any], None],
        messages: List[Dict[str, Any]],
        strict_json_parsing: Optional[bool] = None,
        strict_schema_validation: Optional[bool] = None,
        json_repair_mode: Optional[str] = None,
        **kwargs
    ) -> Tuple[Dict[str, Any], Optional[Any]]:
        """Process request parameters for structured output support.
        
        Returns:
            Modified request parameters
        """
        # Create structured output request
        structured_request = StructuredOutputRequest(
            response_format=response_format,
            strict_json_parsing=strict_json_parsing,
            strict_schema_validation=strict_schema_validation,
            json_repair_mode=json_repair_mode
        )
        
        # Add response format to request
        if structured_request.is_pydantic_model:
            # Convert Pydantic model to JSON schema
            model_class = structured_request.response_format
            json_schema = model_class.model_json_schema()
            
            # Enforce strict schema requirements if strict=True
            if structured_request.strict_schema_validation or structured_request.strict_schema_validation is None:
                self._enforce_strict_schema(json_schema)
            
            # Use native structured output by default
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": model_class.__name__,
                    "schema": json_schema,
                    "strict": structured_request.strict_schema_validation if structured_request.strict_schema_validation is not None else True
                }
            }
        elif structured_request.is_json_schema:
            kwargs["response_format"] = structured_request.response_format
            
        # Apply provider-specific transformations (e.g., polyfills)
        if self.provider:
            kwargs = self.provider.transform_request(kwargs)
            # Update request object if provider set polyfill info
            if hasattr(self.provider, "tool_polyfill_name") and self.provider.tool_polyfill_name:
                 structured_request.tool_polyfill_name = self.provider.tool_polyfill_name

        # kwargs["stream"] = True # Removed forced streaming
        return kwargs, structured_request

    def _enforce_strict_schema(self, schema: Dict[str, Any]) -> None:
        """Recursively enforce strict schema requirements for OpenAI."""
        if schema.get("type") == "object":
            schema["additionalProperties"] = False
            
            # Ensure all properties are required
            if "properties" in schema:
                schema["required"] = list(schema["properties"].keys())
                
                # Recursively process properties
                for prop in schema["properties"].values():
                    self._enforce_strict_schema(prop)
            
            # OpenAI doesn't allow 'title' in strict mode usually, but mostly ignores it. 
            pass
        
        elif schema.get("type") == "array":
            if "items" in schema:
                self._enforce_strict_schema(schema["items"])
                
        # Handle definitions/defs
        if "$defs" in schema:
            for def_schema in schema["$defs"].values():
                self._enforce_strict_schema(def_schema)
        if "definitions" in schema:
            for def_schema in schema["definitions"].values():
                self._enforce_strict_schema(def_schema)
                self._enforce_strict_schema(def_schema)
    
    def process_response(
        self,
        response: Dict[str, Any],
        structured_request: StructuredOutputRequest,
        performance_tracker: Optional[PerformanceTracker] = None
    ) -> EnhancedChatCompletionMessage:
        """Process a structured output response.
        
        Args:
            response: Raw response from provider
            structured_request: Original structured output request
            performance_tracker: Performance tracker for timing
            
        Returns:
            Enhanced message with parsed data and metadata
        """
        # Allow provider to transform response first
        if self.provider:
            response = self.provider.transform_response(response)

        # Extract JSON content
        json_content = None
        
        # Check for tool-based polyfill extraction first
        if structured_request.tool_polyfill_name:
            if "choices" in response and response["choices"]:
                message = response["choices"][0].get("message", {})
                tool_calls = message.get("tool_calls") or []
                
                for tool_call in tool_calls:
                    function = tool_call.get("function", {})
                    if function.get("name") == structured_request.tool_polyfill_name:
                        json_content = function.get("arguments")
                        break
        
        # Fallback to standard extraction if not found or not using polyfill
        if not json_content:
            json_content = extract_json_from_response(response)
        
        if not json_content:
            error_msg = "No JSON content found in response"
            logger.error(error_msg)
            
            if self.config.strict_json_parsing:
                raise StructuredOutputError(error_msg)
            
            return self._create_error_message(response, structured_request, error_msg)
        
        # Process JSON content
        return self._process_json_content(
            json_content,
            response,
            structured_request,
            performance_tracker
        )
    
    def _process_json_content(
        self,
        json_content: str,
        response: Dict[str, Any],
        structured_request: StructuredOutputRequest,
        performance_tracker: Optional[PerformanceTracker] = None
    ) -> EnhancedChatCompletionMessage:
        """Process JSON content from response.
        
        Args:
            json_content: JSON string from response
            response: Full response dictionary
            structured_request: Original structured output request
            performance_tracker: Performance tracker for timing
            
        Returns:
            Enhanced message with processed data
        """
        # Create effective config for this request
        effective_config = self._get_effective_config(structured_request)
        
        # Repair JSON if needed
        repaired_json, repair_info = self._repair_json(
            json_content, effective_config, performance_tracker
        )
        
        # Validate against Pydantic model if applicable
        parsed_model = None
        parse_error = None
        
        if structured_request.is_pydantic_model:
            model_class = structured_request.response_format
            parsed_model, parse_error = validate_pydantic_model(
                repaired_json, model_class, effective_config
            )
        
        # Create enhanced message
        base_message = self._extract_base_message(response)
        
        return EnhancedChatCompletionMessage(
            content=repaired_json,
            role=base_message.get("role", "assistant"),
            function_call=base_message.get("function_call"),
            tool_calls=base_message.get("tool_calls"),
            parsed=parsed_model,
            parse_error=parse_error,
            json_repair_info=repair_info if effective_config.json_repair_feedback else None,
            performance_info=performance_tracker.end_tracking() if performance_tracker else None
        )
    
    def _get_effective_config(
        self,
        structured_request: StructuredOutputRequest
    ) -> VidaiConfig:
        """Get effective configuration for this request.
        
        Args:
            structured_request: Structured output request
            
        Returns:
            Effective configuration with request-specific overrides
        """
        overrides = {}
        
        if structured_request.strict_json_parsing is not None:
            overrides["strict_json_parsing"] = structured_request.strict_json_parsing
        
        if structured_request.strict_schema_validation is not None:
            overrides["strict_schema_validation"] = structured_request.strict_schema_validation
        
        if structured_request.json_repair_mode is not None:
            overrides["json_repair_mode"] = structured_request.json_repair_mode
        
        return self.config.copy(**overrides) if overrides else self.config
    
    def _repair_json(
        self,
        json_content: str,
        config: VidaiConfig,
        performance_tracker: Optional[PerformanceTracker] = None
    ) -> tuple[str, Optional[JsonRepairInfo]]:
        """Repair JSON string if needed.
        
        Args:
            json_content: JSON string to repair
            config: Configuration for repair settings
            performance_tracker: Performance tracker for timing
            
        Returns:
            Tuple of (repaired_json, repair_info)
        """
        if not config.track_json_repair:
            return repair_json_string(json_content, config)
        
        if performance_tracker:
            performance_tracker.start_operation("json_repair")
        
        try:
            result = repair_json_string(json_content, config)
            return result
        finally:
            if performance_tracker:
                repair_time_ms = performance_tracker.end_operation("json_repair")
                # Update repair info with tracked time
                repaired_json, repair_info = result
                if repair_info.was_repaired:
                    repair_info.repair_time_ms = repair_time_ms
                return repaired_json, repair_info
    
    def _extract_base_message(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract base message from response.
        
        Args:
            response: Response dictionary
            
        Returns:
            Base message dictionary
        """
        if "choices" in response:
            choice = response["choices"][0]
            if "message" in choice:
                return choice["message"]
        
        # Anthropic format
        if "content" in response:
            return {"role": "assistant", "content": response["content"]}
        
        # Default
        return {"role": "assistant", "content": None}
    
    def _create_error_message(
        self,
        response: Dict[str, Any],
        structured_request: StructuredOutputRequest,
        error_message: str
    ) -> EnhancedChatCompletionMessage:
        """Create an error message.
        
        Args:
            response: Response dictionary
            structured_request: Structured output request
            error_message: Error message
            
        Returns:
            Enhanced message with error information
        """
        base_message = self._extract_base_message(response)
        
        return EnhancedChatCompletionMessage(
            content=base_message.get("content"),
            role=base_message.get("role", "assistant"),
            function_call=base_message.get("function_call"),
            tool_calls=base_message.get("tool_calls"),
            parsed=None,
            parse_error=Exception(error_message),
            json_repair_info=None,
            performance_info=None
        )
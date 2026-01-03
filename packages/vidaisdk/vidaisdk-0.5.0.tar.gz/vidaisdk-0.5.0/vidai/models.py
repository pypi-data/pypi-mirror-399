"""Enhanced response models for Vidai."""

from typing import Any, Dict, List, Optional, Type, Union
from dataclasses import dataclass

from pydantic import BaseModel
from openai.types.chat import ChatCompletionMessage
from openai.types.completion_usage import CompletionUsage

from .performance import PerformanceInfo


@dataclass
class JsonRepairInfo:
    """Information about JSON repair operations."""
    was_repaired: bool
    repair_time_ms: float
    repair_operations: List[str]
    original_error: Optional[str] = None


class EnhancedChatCompletionMessage(ChatCompletionMessage):
    """Enhanced chat completion message with additional Vidai features."""
    
    def __init__(
        self,
        *,
        content: Optional[str] = None,
        role: str,
        function_call: Optional[Dict[str, Any]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        parsed: Optional[BaseModel] = None,
        parse_error: Optional[Exception] = None,
        json_repair_info: Optional[JsonRepairInfo] = None,
        performance_info: Optional[PerformanceInfo] = None,
        **kwargs
    ) -> None:
        super().__init__(
            content=content,
            role=role,
            function_call=function_call,
            tool_calls=tool_calls,
            **kwargs
        )
        self.parsed = parsed
        self.parse_error = parse_error
        self.json_repair_info = json_repair_info
        self.performance_info = performance_info


@dataclass
class EnhancedChoice:
    """Enhanced choice wrapper."""
    index: int
    message: EnhancedChatCompletionMessage
    finish_reason: str = "stop"

class EnhancedChatCompletion:
    """Enhanced chat completion with additional metadata."""
    
    def __init__(
        self,
        *,
        id: str,
        choices: List[EnhancedChoice],
        created: int,
        model: str,
        object: str = "chat.completion",
        system_fingerprint: Optional[str] = None,
        usage: Optional[CompletionUsage] = None,
        performance_info: Optional[PerformanceInfo] = None,
        **kwargs
    ) -> None:
        self.id = id
        self.choices = choices
        self.created = created
        self.model = model
        self.object = object
        self.system_fingerprint = system_fingerprint
        self.usage = usage
        self.performance_info = performance_info
        for key, value in kwargs.items():
            setattr(self, key, value)


class StructuredOutputRequest:
    """Request parameters for structured output."""
    
    def __init__(
        self,
        response_format: Union[Type[BaseModel], Dict[str, Any]],
        strict_json_parsing: Optional[bool] = None,
        strict_schema_validation: Optional[bool] = None,
        json_repair_mode: Optional[str] = None,
    ) -> None:
        """
        Initialize structured output request.
        
        Args:
            response_format: Pydantic model class or JSON schema dict
            strict_json_parsing: Override global strict JSON parsing setting
            strict_schema_validation: Override global strict schema validation setting
            json_repair_mode: Override global JSON repair mode
        """
        self.response_format = response_format
        self.strict_json_parsing = strict_json_parsing
        self.strict_schema_validation = strict_schema_validation
        self.json_repair_mode = json_repair_mode
        self.tool_polyfill_name: Optional[str] = None
        
        # Validate response format
        if isinstance(response_format, dict):
            if response_format.get("type") not in {"json_object", "json_schema"}:
                raise ValueError(
                    "response_format dict must have type 'json_object' or 'json_schema'"
                )
        elif not (isinstance(response_format, type) and issubclass(response_format, BaseModel)):
            raise ValueError(
                "response_format must be a Pydantic BaseModel class or "
                "a dict with type 'json_object' or 'json_schema'"
            )
    
    @property
    def is_pydantic_model(self) -> bool:
        """Check if response_format is a Pydantic model."""
        return isinstance(self.response_format, type) and issubclass(self.response_format, BaseModel)
    
    @property
    def is_json_schema(self) -> bool:
        """Check if response_format is a JSON schema dict."""
        return isinstance(self.response_format, dict)


@dataclass
class ProxyHeaders:
    """Standardized headers for Vidai proxy interaction."""
    provider: str
    model: str
    version: str = "0.5.0"

    def to_dict(self) -> Dict[str, str]:
        return {
            "x-vidai-provider": self.provider,
            "x-vidai-model": self.model,
            "x-vidai-version": self.version,
        }


# --- Responses API Models (Object Parity) ---

class ResponseFormatText(BaseModel):
    """Format of the text output."""
    type: str = "text"

class ResponseOutputText(BaseModel):
    """Text content item in a response message."""
    text: str
    type: str = "output_text"
    annotations: Optional[List[Any]] = None
    logprobs: Optional[List[Any]] = None

class ResponseOutputMessage(BaseModel):
    """Message item in the response output list."""
    id: Optional[str] = None
    content: List[ResponseOutputText]
    role: str = "assistant"
    status: str = "completed"
    type: str = "message"

class EnhancedResponse(BaseModel):
    """
    Enhanced response object for Responses API.
    Mirrors `openai.types.responses.response.Response` structure.
    """
    id: str
    object: str = "response"
    created: Optional[int] = None
    model: str
    output: List[ResponseOutputMessage]
    usage: Optional[Any] = None
    performance_info: Optional[PerformanceInfo] = None
    
    # Allow extra fields for flexibility
    model_config = {"extra": "allow"}

    @property
    def created_at(self) -> Optional[float]:
        """Alias for created timestamp to match native key if needed."""
        return float(self.created) if self.created else None
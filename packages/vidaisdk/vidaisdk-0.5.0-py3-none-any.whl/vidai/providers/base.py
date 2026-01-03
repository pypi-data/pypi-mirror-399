from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import VidaiConfig

class BaseProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, config: "VidaiConfig", base_url: Optional[str] = None):
        self.config = config
        self.base_url = base_url

    @abstractmethod
    def transform_request(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Transform request parameters before sending to API."""
        pass

    @abstractmethod
    def transform_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Transform response data after receiving from API."""
        pass
    
    def execute_response_request(
        self, 
        client: Any, 
        model: str, 
        **kwargs
    ) -> Any:
        """Execute a 'responses' API request.
        
        Args:
            client: The raw client instance (OpenAI or compatible).
            model: Model identifier.
            messages: List of messages.
            **kwargs: Additional arguments.
            
        Returns:
            Raw response object (not wrapped in EnhancedResponse yet).
            
        Raises:
            NotImplementedError: If provider does not support this API.
        """
        raise NotImplementedError(f"Provider {self.__class__.__name__} does not support responses API.")
    
    @property
    def should_use_tool_polyfill(self) -> bool:
        """Whether this provider needs tool-use polyfill for structured output."""
        return False

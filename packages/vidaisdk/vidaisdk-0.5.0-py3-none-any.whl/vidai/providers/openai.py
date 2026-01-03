from typing import Any, Dict
from .base import BaseProvider

from .strategies import ToolPolyfillProvider

class OpenAIProvider(ToolPolyfillProvider):
    """Standard provider for OpenAI and fully compatible APIs.
    
    Inherits from ToolPolyfillProvider to enable generic polyfill for 
    Responses API and robust structured output support via tools if needed.
    """
    pass

from typing import Optional
from ..config import VidaiConfig
from .base import BaseProvider
from .openai import OpenAIProvider
from .strategies import ToolPolyfillProvider
from .anthropic import AnthropicProvider
from .gemini import GeminiProvider
from .groq import GroqProvider
from .deepseek import DeepSeekProvider
from .vllm import VLLMProvider
from .vidai_proxy import VidaiProxyProvider

class ProviderFactory:
    """Factory for creating provider instances."""
    
    @staticmethod
    def create_provider(config: VidaiConfig, base_url: Optional[str] = None) -> BaseProvider:
        """Create a provider based on configuration."""
        # 1. Check for explicit overrides in config first (highest priority)
        if config.provider:
            if config.provider == "vidai" or config.provider == "proxy":
                return VidaiProxyProvider(config, base_url)
            elif config.provider == "anthropic":
                return AnthropicProvider(config, base_url)
            elif config.provider == "gemini":
                return GeminiProvider(config, base_url)
            elif config.provider == "groq":
                return GroqProvider(config, base_url)
            elif config.provider == "deepseek":
                return DeepSeekProvider(config, base_url)
            elif config.provider == "vllm":
                return VLLMProvider(config, base_url)
            elif config.provider == "openai":
                return OpenAIProvider(config, base_url)

        method = config.structured_output_method
        if method == "tool_fill":
            return ToolPolyfillProvider(config, base_url)
        
        # 2. Check base_url for auto-detection
        url_to_check = base_url or config.default_base_url or ""
        
        if "generativelanguage.googleapis.com" in url_to_check:
            return GeminiProvider(config, base_url)
            
        if "groq.com" in url_to_check:
            return GroqProvider(config, base_url)
            
        if "deepseek.com" in url_to_check:
            return DeepSeekProvider(config, base_url)
            
        if "anthropic.com" in url_to_check:
            return AnthropicProvider(config, base_url)
        
        # 3. Default to OpenAI (Native)
        return OpenAIProvider(config, base_url)

from typing import Any, Dict, List, Optional
import httpx
from .base import BaseProvider
from .strategies import ToolPolyfillProvider

class VidaiProxyProvider(ToolPolyfillProvider):
    """Facade provider for Vidai Server proxy with auto-discovery."""

    def __init__(self, config, base_url: Optional[str] = None):
        super().__init__(config, base_url)
        self._delegates: Dict[str, BaseProvider] = {}
        self._model_cache: Dict[str, str] = {} # model_id -> provider_type
        self._initialized = False
        self.tool_polyfill_name: Optional[str] = None

    def _ensure_initialized(self):
        """Lazy load models from proxy."""
        if self._initialized:
            return

        base_url = self.base_url or self.config.default_base_url or "http://localhost:8000"
        url = f"{base_url.rstrip('/')}/models"
        
        
        import os
        headers = {}
        api_key = os.getenv("VIDAI_SERVER_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            with httpx.Client() as client:
                response = client.get(url, headers=headers, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("data", []):
                        m_id = model.get("id")
                        # Use provider or owned_by as source of truth
                        p_source = model.get("provider") or model.get("owned_by") or "openai"
                        self._model_cache[m_id] = self._normalize_provider(p_source)
        except Exception:
            # Silent fail allows generic fallback
            pass
            
        self._initialized = True

    def _normalize_provider(self, name: str) -> str:
        """Normalize provider name to internal key."""
        name = name.lower()
        if "anthropic" in name: return "anthropic"
        if "deepseek" in name: return "deepseek"
        if "gemini" in name or "google" in name: return "gemini"
        if "groq" in name: return "groq"
        # Pass through unknown names (e.g. 'mistral', 'cohere') to Factory
        # Factory will handle them (or default to OpenAI if unregistered)
        return name

    def _get_delegate_for_model(self, model: str) -> BaseProvider:
        """Get or create delegate for model."""
        self._ensure_initialized()
        
        # Default to OpenAI if unknown
        provider_type = self._model_cache.get(model, "openai")
        
        if provider_type not in self._delegates:
            # Use ProviderFactory to create delegate
            # This avoids duplicating registration logic here.
            # Local import to avoid circular dependency
            from .factory import ProviderFactory
            
            # Create a localized config for this specific provider type
            # We clone the current config but override the 'provider' field
            # to trick the Factory into creating the correct concrete provider.
            # VidaiConfig has a copy method.
            delegate_config = self.config.copy(provider=provider_type)
            
            self._delegates[provider_type] = ProviderFactory.create_provider(delegate_config, self.base_url)
                
        return self._delegates[provider_type]

    def transform_request(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate request transformation."""
        model = kwargs.get("model")
        if not model:
            return kwargs
            
        delegate = self._get_delegate_for_model(model)
        transformed = delegate.transform_request(kwargs)
        
        # Inject Headers
        extra_headers = transformed.get("extra_headers", {})
        extra_headers["x-vidai-model"] = model
        
        # We can also inject x-provider if we want
        provider_type = self._model_cache.get(model, "openai")
        extra_headers["x-vidai-provider"] = provider_type
        
        # Inject Authorization for delegates that manage their own connection (e.g. Anthropic)
        import os
        api_key = os.getenv("VIDAI_SERVER_API_KEY")
        if api_key:
            extra_headers["Authorization"] = f"Bearer {api_key}"
            
        transformed["extra_headers"] = extra_headers
        
        # Propagate Polyfill Info (for Structured Output extraction)
        # Note: This limits concurrent usage of same client instance for different provider types
        # if using Structured Output. acceptable constraint for now.
        if hasattr(delegate, "tool_polyfill_name"):
            self.tool_polyfill_name = delegate.tool_polyfill_name
        else:
            self.tool_polyfill_name = None
            
        return transformed

    def transform_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate response transformation logic."""
        # No transformation needed; Proxy ensures OpenAI-compatible format.
        return response

    def execute_request(self, client: Any, model: str, messages: List[Dict[str, Any]], stream: bool = False, **kwargs) -> Any:
        """Execute request via delegate or default client."""
        delegate = self._get_delegate_for_model(model)
        
        # Execute via the standard OpenAI client (configured for VidaiProxy).
        # We bypass delegate.execute_request() to enforce consistent Proxy Authentication
        # and standard OpenAI wire format for all models.
        from openai.types.chat import ChatCompletion
        
        # Prepare headers
        extra_headers = kwargs.pop("extra_headers", {})
        
        # Prepare payload
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        
        # Execute using OpenAI's wrapper signature
        # post(path, cast_to, body, options)
        # Note: If stream=True, we must provide stream_cls and handle it.
        
        if stream:
            from openai import Stream
            from openai.types.chat import ChatCompletionChunk
            return client.post(
                "/chat/completions",
                body=payload,
                cast_to=ChatCompletionChunk, 
                stream=True,
                stream_cls=Stream[ChatCompletionChunk],
                options={"headers": extra_headers}
            )
            
        return client.post(
            "/chat/completions",
            body=payload,
            cast_to=ChatCompletion,
            options={"headers": extra_headers}
        )

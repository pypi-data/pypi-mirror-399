from .strategies import ToolPolyfillProvider

class GroqProvider(ToolPolyfillProvider):
    """Provider adapter for Groq.
    
    Groq supports native structured output (JSON mode), but often benefits
    from the tool-based polyfill approach for complex or strictly typed
    schemas to ensure higher reliability across different Llama models.
    """
    pass

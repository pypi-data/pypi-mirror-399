from typing import Any, Dict
from .strategies import ToolPolyfillProvider

class GeminiProvider(ToolPolyfillProvider):
    """Provider adapter for Google Gemini (via OpenAI-compatible endpoint).
    
    This provider uses the Google Gemini OpenAI-compatible API but injects
    structured output support via the ToolPolyfillProvider mechanism.
    
    It also transforms image URLs to base64 data URIs because the Gemini
    OpenAI-compat layer does not reliably fetch public URLs.
    """
    
    def transform_request(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        # First apply tool polyfill logic (super)
        kwargs = super().transform_request(kwargs)
        
        # Then transform images
        messages = kwargs.get("messages", [])
        if not messages:
            return kwargs
            
        from ..utils import encode_file, get_media_type
        
        new_messages = []
        for msg in messages:
            content = msg.get("content")
            if isinstance(content, list):
                new_content = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "image_url":
                        url = block["image_url"]["url"]
                        if not url.startswith("data:"):
                            # Convert to base64 data URI
                            b64_data = encode_file(url)
                            media_type = get_media_type(url)
                            data_uri = f"data:{media_type};base64,{b64_data}"
                            
                            # Replace URL with Base64
                            new_block = block.copy()
                            new_block["image_url"] = {"url": data_uri}
                            new_content.append(new_block)
                        else:
                            new_content.append(block)
                    else:
                        new_content.append(block)
                
                new_msg = msg.copy()
                new_msg["content"] = new_content
                new_messages.append(new_msg)
            else:
                new_messages.append(msg)
                
        kwargs["messages"] = new_messages
        return kwargs

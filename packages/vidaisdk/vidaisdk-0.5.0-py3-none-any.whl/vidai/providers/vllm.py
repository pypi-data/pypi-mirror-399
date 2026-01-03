from typing import Any, Dict
import json
from .base import BaseProvider

class VLLMProvider(BaseProvider):
    """Provider adapter for vLLM (OpenAI-compatible).
    
    vLLM supports an OpenAI-compatible server but adds specific parameters
    for guided generation (constrained decoding).
    
    This provider transforms `response_format` containing a JSON schema
    into vLLM's `guided_json` parameter.
    """
    
    def transform_request(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Transform request to use vLLM's guided decoding if structured output is requested."""
        response_format = kwargs.get("response_format")
        
        # Check if this is a JSON schema request
        if response_format and isinstance(response_format, dict) and \
           response_format.get("type") == "json_schema":
            
            json_schema_obj = response_format.get("json_schema", {})
            schema = json_schema_obj.get("schema")
            
            if schema:
                # vLLM expects 'guided_json' in the request body (extra_body)
                # It accepts the raw schema object or string
                extra_body = kwargs.get("extra_body", {})
                extra_body["guided_json"] = schema
                kwargs["extra_body"] = extra_body
                
                # Remove response_format so it doesn't confuse standard parameters
                # (though vLLM might ignore it, it's cleaner to remove)
                kwargs.pop("response_format")
                
        return kwargs

    def transform_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """No special response transformation needed for vLLM."""
        return response
        
    @property
    def should_use_tool_polyfill(self) -> bool:
        """vLLM has native guided generation, so we don't need tool polyfill."""
        return False

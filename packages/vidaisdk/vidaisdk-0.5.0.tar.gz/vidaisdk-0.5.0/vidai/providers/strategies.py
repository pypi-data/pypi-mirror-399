import json
from typing import Any, Dict, List, Optional
from .base import BaseProvider

class ToolPolyfillProvider(BaseProvider):
    """Provider that polyfills structured output using tool calls."""
    
    def __init__(self, config, base_url: Optional[str] = None):
        super().__init__(config, base_url)
        self.tool_polyfill_name: Optional[str] = None
        self.was_wrapped: bool = False

    def transform_request(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Convert response_format to tools if present."""
        response_format = kwargs.get("response_format")
        
        # Only polyfill if it's a json_schema type request
        if response_format and isinstance(response_format, dict) and \
           response_format.get("type") == "json_schema":
            
            json_schema_obj = response_format.get("json_schema", {})
            schema = json_schema_obj.get("schema")
            name = json_schema_obj.get("name", "structured_response")
            
            if schema:
                # 1. Resolve Refs (inline $defs) to prevent multi-tool hallucination
                defs = schema.get("$defs") or schema.get("definitions") or {}
                resolved_schema = self._resolve_schema_refs(schema, defs)
                
                # 2. Ensure root is Object (OpenAI/Gemini requirement)
                self.was_wrapped = False
                if resolved_schema.get("type") != "object":
                     resolved_schema = {
                         "type": "object",
                         "properties": {"q_response": resolved_schema},
                         "required": ["q_response"],
                         "additionalProperties": False
                     }
                     self.was_wrapped = True
                
                # 3. Strip titles to prevent tool hallucination
                resolved_schema = self._strip_titles(resolved_schema)

                # Sanitize tool name
                tool_name = "".join(c for c in name if c.isalnum() or c == "_") or "structured_response"
                self.tool_polyfill_name = tool_name
                
                tool_definition = {
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "description": f"Output response as {tool_name}",
                        "parameters": resolved_schema,
                        "strict": json_schema_obj.get("strict", True)
                    }
                }
                
                # Debug tool definition
                # print(f"DEBUG: Tool Definition for {tool_name}: {json.dumps(tool_definition, indent=2)}")
                
                # Replace response_format with tool choice
                kwargs.pop("response_format")
                kwargs["tools"] = [tool_definition]
                kwargs["tool_choice"] = {"type": "function", "function": {"name": tool_name}}
                
        return kwargs

    def transform_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract JSON from tool call if polyfill was used."""
        if not self.tool_polyfill_name:
            return response
            
        # If wrapped, we need to unwrap the arguments in the response
        if self.was_wrapped and "choices" in response:
            for choice in response["choices"]:
                message = choice.get("message", {})
                tool_calls = message.get("tool_calls")
                if tool_calls:
                    for tool_call in tool_calls:
                         if tool_call.get("function", {}).get("name") == self.tool_polyfill_name:
                             args = tool_call["function"].get("arguments")
                             if isinstance(args, str):
                                 try:
                                     arg_dict = json.loads(args)
                                     if "q_response" in arg_dict:
                                         # Unwrap and re-serialize to match expected output
                                         tool_call["function"]["arguments"] = json.dumps(arg_dict["q_response"])
                                 except Exception:
                                     pass # formatting error, let processor handle
        
        return response

    def _resolve_schema_refs(self, schema: Any, defs: Dict[str, Any]) -> Any:
        """Recursively resolve $ref in schema using provided definitions."""
        if not isinstance(schema, dict):
            return schema
            
        # Handle Reference
        if "$ref" in schema:
            ref_key = schema["$ref"].split("/")[-1]
            if ref_key in defs:
                # Retrieve definition and resolve its internal refs
                definition = defs[ref_key]
                return self._resolve_schema_refs(definition, defs)
            return schema # Unresolved ref
            
        # Recurse into properties/items
        new_schema = {}
        for k, v in schema.items():
            if k in ("$defs", "definitions"):
                continue # Strip definitions from output (now inlined)
            
            if k == "properties" and isinstance(v, dict):
                 new_props = {}
                 for prop_name, prop_schema in v.items():
                     new_props[prop_name] = self._resolve_schema_refs(prop_schema, defs)
                 new_schema[k] = new_props
            elif k == "items" and isinstance(v, dict):
                 new_schema[k] = self._resolve_schema_refs(v, defs)
            elif k == "anyOf" and isinstance(v, list):
                 new_schema[k] = [self._resolve_schema_refs(i, defs) for i in v]
            else:
                 new_schema[k] = v # shallow copy non-container fields
                 
        return new_schema

    def _strip_titles(self, schema: Any) -> Any:
        """Recursively remove 'title' fields from schema to prevent tool hallucination."""
        if not isinstance(schema, dict):
            return schema
            
        new_schema = {}
        for k, v in schema.items():
            if k == "title":
                continue
            
            if isinstance(v, dict):
                new_schema[k] = self._strip_titles(v)
            elif isinstance(v, list):
                new_schema[k] = [self._strip_titles(i) for i in v]
            else:
                new_schema[k] = v
        
        return new_schema
    
    @property
    def should_use_tool_polyfill(self) -> bool:
        return True

    def execute_response_request(self, client: Any, model: str, **kwargs) -> Any:
        """Execute a response request using generic polyfill (via chat.completions).
        
        This enables Responses API support for any provider that supports Chat Completions,
        including DeepSeek, WizzServer, Gemini, Groq, etc.
        """
        # 1. Normalize Input to Messages
        messages = kwargs.pop("messages", None)
        input_data = kwargs.pop("input", None)
        
        # Map Responses API params to Completions API params
        if "max_output_tokens" in kwargs:
            kwargs["max_tokens"] = kwargs.pop("max_output_tokens")
        
        if messages is None:
            if input_data is None:
                raise ValueError("Either 'messages' or 'input' must be provided.")
            if isinstance(input_data, str):
                messages = [{"role": "user", "content": input_data}]
            elif isinstance(input_data, list):
                # Handle list of strings or multimodal
                # Simple case: list of strings -> list of user messages?
                # or list of content blocks for one user message?
                # OpenAI Responses API spec usually treats 'input' as a single prompt unless it's messages.
                # If input is list[str], it's typically batching? No, Responses API is usually single.
                # Let's assume input list -> single user message with content list if simple blocks,
                # or just failover to messages if complex.
                # For VidaiSDK ease: input list -> single message content
                messages = [{"role": "user", "content": input_data}]
        
        # 2. Call Chat Completions (Delegate to standard client)
        # Note: We enforce stream=False for the generic polyfill for now to simplify
        # mapping back to a single Response object.
        # kwargs["stream"] = False  <-- Removed to enable streaming
        
        # This uses the configured client (which might be headers-patched Proxy or standard OpenAI)
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        
        if kwargs.get("stream"):
            return self._stream_response(completion)
        
        # 3. Map to Response Object
        from types import SimpleNamespace
        
        output_items = []
        if completion.choices:
            choice = completion.choices[0]
            message = choice.message
            
            # Content
            if message.content:
                output_items.append({
                    "type": "message",
                    "role": "assistant",
                    "content": message.content
                })
                
            # Tool Calls (Polyfill Unwrapping logic)
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    if self.tool_polyfill_name and tool_call.function.name == self.tool_polyfill_name:
                         # Unwrap: Treat arguments as the main content message
                         output_items.append({
                            "type": "message",
                            "role": "assistant",
                            "content": tool_call.function.arguments
                        })
                    else:
                        output_items.append({
                            "type": "tool_call",
                            "id": tool_call.id,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        })

        response = SimpleNamespace()
        response.id = completion.id
        response.object = "chat.completion"
        response.created = completion.created
        response.model = completion.model
        response.usage = completion.usage
        response.output = output_items
        
        return response

    def _stream_response(self, completion_stream):
        """Yield response chunks from completion stream."""
        # This is a basic implementation to yield raw chunks appropriately wrapped
        # Ideally we map them to Response Deltas, but Responses API streaming
        # format is different (content_delta vs message_delta).
        
        # For polyfill purposes, we will yield the completion chunks but ensure
        # clients consuming 'responses' stream can handle them. 
        # Typically generic clients expect consistency.
        
        for chunk in completion_stream:
             # Just pass through the chunk for now as a baseline
             # Or wrap if needed. Responses API chunks usually look like:
             # props: output_delta, usage, ... 
             # vs ChatCompletionProps: choices[0].delta.
             
             # We should probably map delta content to output_delta
             yield chunk

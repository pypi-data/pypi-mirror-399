from typing import Any, Dict, List, Optional
import os
import json
import uuid
import time
import httpx
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.completion_usage import CompletionUsage
from ..utils import logger
from .strategies import ToolPolyfillProvider

class AnthropicProvider(ToolPolyfillProvider):
    """Provider adapter for Anthropic (Native)."""

    # transform_request and transform_response inherited from ToolPolyfillProvider
    # This enables structured output via tool polyfilling automatically.

    def execute_request(self, client: Any, model: str, messages: List[Dict[str, Any]], stream: bool = False, max_tokens: Optional[int] = None, **kwargs) -> Any:
        """Execute request against Anthropic API.
        
        Args:
            client: OpenAI client instance (not used for native Anthropic).
            model: Model identifier (e.g., 'claude-3-5-sonnet-20240620').
            messages: List of messages in OpenAI format.
            stream: Whether to stream the response.
            max_tokens: Max tokens (required by Anthropic, defaults to 1024 if missing).
            **kwargs: Additional parameters (temperature, etc.).
            
        Returns:
            ChatCompletion object or generator for streaming.
            
        Raises:
            ValueError: If ANTHROPIC_API_KEY is missing.
            Exception: If API request fails.
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required for Anthropic provider.")
            
        # Ensure max_tokens is present (required by Anthropic)
        if max_tokens is None:
            max_tokens = kwargs.get("max_tokens", 1024)

        # Transform Messages
        system_prompt = None
        anthropic_messages = []
        
        from ..utils import encode_image, get_media_type
        
        # Check for caching
        enable_caching = False
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            
            if role == "system":
                # Check if system prompt has cache_control (special case passing dict)
                # OpenAI system prompt is usually string. If list/dict, check options.
                if isinstance(content, list):
                     for block in content:
                         if isinstance(block, dict) and "cache_control" in block:
                             enable_caching = True
                system_prompt = content
            elif role == "user":
                if isinstance(content, str):
                    anthropic_messages.append({"role": "user", "content": content})
                elif isinstance(content, list):
                    # Handle multimodal content
                    new_content = []
                    for block in content:
                        if isinstance(block, dict):
                            # Check for cache_control
                            if "cache_control" in block:
                                enable_caching = True
                            
                            if block.get("type") == "text":
                                new_content.append(block) # Pass through (including cache_control)
                            elif block.get("type") == "image_url":
                                url = block["image_url"]["url"]
                                
                                # Determine if base64 or url
                                if url.startswith("data:"):
                                    # Parse data URI
                                    header, data = url.split(",", 1)
                                    media_type = header.split(":")[1].split(";")[0]
                                    b64_data = data
                                else:
                                    # Download/Load
                                    b64_data = encode_image(url)
                                    media_type = get_media_type(url)
                                
                                block_content = {
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": b64_data
                                    }
                                }
                                
                                if media_type == "application/pdf":
                                    block_content["type"] = "document"
                                else:
                                    block_content["type"] = "image"
                                    
                                # Pass through cache_control if present on the image_url block
                                if "cache_control" in block:
                                    block_content["cache_control"] = block["cache_control"]
                                    
                                new_content.append(block_content)
                    anthropic_messages.append({"role": "user", "content": new_content})
                else:
                    anthropic_messages.append({"role": "user", "content": content})
            elif role == "assistant":
                anthropic_messages.append({"role": "assistant", "content": content or ""})

        payload = {
            "model": model,
            "messages": anthropic_messages,
            "stream": stream,
            "max_tokens": max_tokens
        }
        
        if system_prompt:
             # If system prompt is complex (list), pass it directly (Anthropic supports list for system)
             # But usually OpenAI system is string. 
             # If user passes list for system to enable caching on system, we handle it.
             payload["system"] = system_prompt

        # Add other parameters
        for k, v in kwargs.items():
            if k not in ["messages", "model", "stream"]:
                payload[k] = v
        
        # Handle tools
        if "tools" in kwargs:
            payload["tools"] = self._map_tools(kwargs["tools"])
            
        # Handle tool_choice
        if "tool_choice" in kwargs:
            payload["tool_choice"] = self._map_tool_choice(kwargs["tool_choice"])

        # Prepare headers
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        # Add beta header for caching if detected
        if enable_caching:
            headers["anthropic-beta"] = "prompt-caching-2024-07-31"

        if stream:
            return self._execute_streaming(payload, headers, model)

        # Determine URL
        # If base_url matches OpenAI default, ignore it and use Anthropic default
        if self.base_url and "api.openai.com" not in self.base_url:
            base_url = self.base_url
        else:
            base_url = "https://api.anthropic.com/v1"
            
        url = f"{base_url.rstrip('/')}/messages"

        # Non-streaming execution
        with httpx.Client() as http_client:
            response = http_client.post(
                url,
                headers=headers,
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Anthropic API Error: {response.text}")
                
            return self._map_response(response.json(), model)

    def _execute_streaming(self, payload: Dict[str, Any], headers: Dict[str, Any], model: str) -> Any:
        """Execute streaming request and yield OpenAI-compatible chunks.
        
        Args:
            payload: Request payload for Anthropic API.
            headers: Headers for the request.
            model: Model identifier.
            
        Returns:
            Generator yielding ChatCompletionChunk objects.
        """
        # Use httpx.stream
        payload["stream"] = True
        
        # Generator function
        def generator():
            # Determine URL
            base_url = self.base_url or "https://api.anthropic.com/v1"
            url = f"{base_url.rstrip('/')}/messages"

            with httpx.Client() as client:
                with client.stream("POST", url, headers=headers, json=payload, timeout=60.0) as response:
                    if response.status_code != 200:
                         # Non-streaming error response
                         error_text = response.read().decode("utf-8")
                         raise Exception(f"Anthropic Streaming Error: {error_text}")

                    # SSE Parsing State
                    current_event = None
                    
                    for line in response.iter_lines():
                        if not line:
                            continue
                            
                        if line.startswith("event: "):
                            current_event = line[7:].strip()
                            continue
                        
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            
                            if current_event == "ping":
                                continue
                                
                            if current_event == "message_start":
                                # Initial message info
                                try:
                                    data = json.loads(data_str)
                                    yield self._create_chunk(
                                        id=data["message"]["id"],
                                        model=model,
                                        role="assistant",
                                        content="" # Initial role chunk
                                    )
                                except json.JSONDecodeError:
                                    # Skip malformed chunks to avoid crashing the stream
                                    continue
                                continue
                                
                            if current_event == "content_block_start":
                                try:
                                    data = json.loads(data_str)
                                    block = data["content_block"]
                                    if block["type"] == "text":
                                        yield self._create_chunk(id=None, model=model, content=block["text"])
                                    elif block["type"] == "tool_use":
                                        # Start of tool call
                                        yield self._create_chunk(
                                            id=None, 
                                            model=model, 
                                            tool_calls=[{
                                                "index": data["index"],
                                                "id": block["id"],
                                                "type": "function",
                                                "function": {
                                                    "name": block["name"],
                                                    "arguments": ""
                                                }
                                            }]
                                        )
                                except (json.JSONDecodeError, KeyError):
                                    continue
                                continue

                            if current_event == "content_block_delta":
                                try:
                                    data = json.loads(data_str)
                                    delta = data["delta"]
                                    if delta["type"] == "text_delta":
                                        yield self._create_chunk(id=None, model=model, content=delta["text"])
                                    elif delta["type"] == "input_json_delta":
                                        # Partial JSON for tool
                                        yield self._create_chunk(
                                            id=None,
                                            model=model,
                                            tool_calls=[{
                                                "index": data["index"],
                                                "function": {
                                                    "arguments": delta["partial_json"]
                                                }
                                            }]
                                        )
                                except (json.JSONDecodeError, KeyError):
                                    continue
                                continue

                            if current_event == "message_stop":
                                # Finish
                                yield self._create_chunk(id=None, model=model, finish_reason="stop")
                                continue

        return generator()

    def _create_chunk(self, id: Optional[str], model: str, content: Optional[str] = None, role: Optional[str] = None, tool_calls: Optional[List[Dict[str, Any]]] = None, finish_reason: Optional[str] = None) -> Any:
        """Create an OpenAI ChatCompletionChunk.
        
        Args:
            id: Message ID.
            model: Model identifier.
            content: Content delta.
            role: Role delta.
            tool_calls: Tool call deltas.
            finish_reason: Finish reason.
            
        Returns:
            ChatCompletionChunk object.
        """
        # Check openai version for strict typing, using simplified dict-like construction for reliability for now
        # Ideally we construct ChatCompletionChunk objects
        from openai.types.chat import ChatCompletionChunk
        from openai.types.chat.chat_completion_chunk import Choice, ChoiceDelta, ChoiceDeltaToolCall, ChoiceDeltaToolCallFunction
        
        delta_kwargs = {}
        if role:
            delta_kwargs["role"] = role
        if content is not None:
             delta_kwargs["content"] = content
        if tool_calls:
            # properly construct ChoiceDeltaToolCall
            mapped_tool_calls = []
            for tc in tool_calls:
                func_args = {}
                if "function" in tc:
                     if "name" in tc["function"]:
                         func_args["name"] = tc["function"]["name"]
                     if "arguments" in tc["function"]:
                         func_args["arguments"] = tc["function"]["arguments"]
                
                mapped_tool_calls.append(ChoiceDeltaToolCall(
                    index=tc.get("index", 0),
                    id=tc.get("id"),
                    type="function" if tc.get("type") else None,
                    function=ChoiceDeltaToolCallFunction(**func_args) if func_args else None
                ))
            delta_kwargs["tool_calls"] = mapped_tool_calls

        return ChatCompletionChunk(
            id=id or str(uuid.uuid4()),
            choices=[
                Choice(
                    delta=ChoiceDelta(**delta_kwargs),
                    finish_reason=finish_reason,
                    index=0
                )
            ],
            created=int(time.time()),
            model=model,
            object="chat.completion.chunk"
        )

    def _map_tools(self, openai_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map OpenAI tools to Anthropic tools.
        
        Args:
            openai_tools: List of OpenAI-style tool definitions.
            
        Returns:
            List of Anthropic-style tool definitions.
        """
        anthropic_tools = []
        for tool in openai_tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                tool_def = {
                    "name": func.get("name"),
                    "input_schema": func.get("parameters")
                }
                if func.get("description"):
                    tool_def["description"] = func.get("description")
                anthropic_tools.append(tool_def)
        return anthropic_tools

    def _map_tool_choice(self, tool_choice: Any) -> Dict[str, Any]:
        """Map OpenAI tool_choice to Anthropic tool_choice.
        
        Args:
            tool_choice: OpenAI tool choice (string or dict).
            
        Returns:
            Anthropic tool choice dict.
        """
        if tool_choice == "auto":
            return {"type": "auto"}
        elif tool_choice == "required":
            return {"type": "any"}
        elif isinstance(tool_choice, dict) and tool_choice.get("type") == "function":
             return {"type": "tool", "name": tool_choice["function"]["name"]}
        return {"type": "auto"} # Default

    def _map_response(self, data: Dict[str, Any], model: str) -> ChatCompletion:
        """Map Anthropic response to OpenAI ChatCompletion.
        
        Args:
            data: Raw JSON response from Anthropic API.
            model: Model identifier.
            
        Returns:
            ChatCompletion object.
        """
        content = ""
        tool_calls = []
        
        for block in data.get("content", []):
            if block["type"] == "text":
                content += block["text"]
            elif block["type"] == "tool_use":
                tool_calls.append({
                    "id": block["id"],
                    "type": "function",
                    "function": {
                        "name": block["name"],
                        "arguments": json.dumps(block["input"])
                    }
                })
        
        message_kwargs = {
            "role": "assistant",
            "content": content if content else None
        }
        
        if tool_calls:
            message_kwargs["tool_calls"] = tool_calls
            
        finish_reason = "stop"
        if data.get("stop_reason") == "tool_use":
            finish_reason = "tool_calls"
        elif data.get("stop_reason") == "max_tokens":
            finish_reason = "length"

        return ChatCompletion(
            id=data.get("id", str(uuid.uuid4())),
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(**message_kwargs),
                    finish_reason=finish_reason
                )
            ],
            created=int(time.time()),
            model=model,
            object="chat.completion",
            usage=self._map_usage(data.get("usage", {}))
        )

    def _map_usage(self, anthropic_usage: Dict[str, int]) -> Optional[CompletionUsage]:
        """Map Anthropic usage to OpenAI CompletionUsage.
        
        Args:
            anthropic_usage: Anthropic usage dict.
            
        Returns:
            CompletionUsage object or None.
        """
        if not anthropic_usage:
            return None
            
        input_tokens = anthropic_usage.get("input_tokens", 0)
        output_tokens = anthropic_usage.get("output_tokens", 0)
        
        # Add cache tokens to input_tokens? 
        # OpenAI doesn't have standard fields for granular cache stats yet in CompletionUsage
        # (though they have prompt_tokens_details).
        # We will populate standard fields and try to pass extras.
        
        usage = CompletionUsage(
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens
        )
        
        # Inject extra cache fields if present
        cache_creation = anthropic_usage.get("cache_creation_input_tokens")
        cache_read = anthropic_usage.get("cache_read_input_tokens")
        
        if cache_read is not None:
            usage.cache_read_input_tokens = cache_read # Dynamic attribute
            
        return usage

    def execute_response_request(
        self, 
        client: Any, 
        model: str, 
        **kwargs
    ) -> Any:
        """Execute request using Anthropic API and map to Response object."""
        # Reuse existing execute_request but adapt the output
        
        # Responses API doesn't support streaming yet in our implementation (or is different)
        # So we force stream=False for now or handle it via execute_request
        stream = kwargs.pop("stream", False)
        if stream:
             logger.warning("Streaming not yet supported for Responses API on Anthropic provider.")
             stream = False

        # Handle 'input' parameter conversion to 'messages'
        # Responses API uses 'input' which can be str or list of items
        response_input = kwargs.pop("input", None)
        messages = kwargs.pop("messages", []) # Should be empty usually
        
        if response_input:
            if isinstance(response_input, str):
                messages.append({"role": "user", "content": response_input})
            elif isinstance(response_input, list):
                # Simple mapping: assume input items are roughly compatible with message content parts
                # or just treat them as user message content
                # For basic verification, we assume text or list of text/image
                content_parts = []
                for item in response_input:
                    if isinstance(item, str):
                        content_parts.append({"type": "text", "text": item})
                    elif isinstance(item, dict) and "type" in item:
                         content_parts.append(item)
                
                if content_parts:
                    messages.append({"role": "user", "content": content_parts if len(content_parts) > 1 else content_parts[0]["text"] if content_parts[0]["type"] == "text" else content_parts})

        # Map 'max_output_tokens' to 'max_tokens' for Anthropic
        if "max_output_tokens" in kwargs:
            kwargs["max_tokens"] = kwargs.pop("max_output_tokens")
        elif "max_tokens" not in kwargs:
            # Anthropic requires max_tokens to be set
            kwargs["max_tokens"] = 1024 # Default safety limit

        # Use existing method to get a ChatCompletion object
        chat_completion = self.execute_request(client, model, messages, stream=False, **kwargs)
        
        # Convert ChatCompletion to "Response" object structure
        # This mocks the openai.types.Response object structure
        
        output_items = []
        choice = chat_completion.choices[0]
        message = choice.message
        
        if message.content:
            output_items.append({
                "type": "message",
                "role": "assistant",
                "content": message.content
            })
            
        if message.tool_calls:
            for tool_call in message.tool_calls:
                # Check for polyfill unwrapping
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
                        },
                        # Responses API might wrap this differently, aligning with generic 'function' type
                    })

        # Dynamically create an object that looks like the Response object
        # Since we might not be able to instantiate the real one easily without valid server data, 
        # we create a compatible class or Mock
        from vidai.models import EnhancedResponse
        
        # We need to return an object that has .id, .created, etc.
        # EnhancedResponses will wrap it again, but expects these fields on the "raw" response.
        
        class ProviderResponseAdapter:
            def __init__(self, cc):
                self.id = cc.id
                self.created = cc.created
                self.model = cc.model
                self.object = "response"
                self.usage = cc.usage
                self.output = output_items
        
        return ProviderResponseAdapter(chat_completion)

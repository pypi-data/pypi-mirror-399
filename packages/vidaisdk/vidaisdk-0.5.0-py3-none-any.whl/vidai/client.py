"""Main Vidai OpenAI-compatible wrapper."""

import time
from typing import Any, Dict, Optional, Type, Union

from openai import OpenAI as BaseOpenAI
from openai.resources.chat import Chat
from openai.resources.chat.completions import Completions
from openai.resources.responses import Responses
from openai.types.chat import ChatCompletion

from pydantic import BaseModel

from vidai.config import VidaiConfig
from vidai.exceptions import StructuredOutputError
from vidai.models import EnhancedChatCompletion, EnhancedChatCompletionMessage, ProxyHeaders, EnhancedResponse
from vidai.performance import PerformanceTracker
from vidai.structured_output import StructuredOutputProcessor
from vidai.utils import merge_configs, setup_logging, logger


class EnhancedCompletions(Completions):
    """Enhanced completions resource with structured output support."""
    
    def __init__(self, client: BaseOpenAI, config: VidaiConfig, structured_processor: StructuredOutputProcessor) -> None:
        super().__init__(client)
        self.config = config
        self._structured_processor = structured_processor
        
    def create(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        response_format: Optional[Union[Type[BaseModel], Dict[str, Any]]] = None,
        strict_json_parsing: Optional[bool] = None,
        strict_schema_validation: Optional[bool] = None,
        json_repair_mode: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ChatCompletion, EnhancedChatCompletion]:
        """Create a chat completion with structured output support.
        
        Args:
            model: Model name to use
            messages: List of chat messages
            response_format: Pydantic model class or JSON schema for structured output
            strict_json_parsing: Override global strict JSON parsing setting
            strict_schema_validation: Override global strict schema validation setting
            json_repair_mode: Override global JSON repair mode
            stream: Whether to stream response
            **kwargs: Additional arguments passed to OpenAI
            
        Returns:
            Chat completion with enhanced features for structured output
            
        Raises:
            StructuredOutputError: If structured output fails in strict mode
            ValueError: If invalid parameters are provided
        """
        # Validate streaming with structured output
        if stream and response_format:
            logger.warning(
                "Streaming is not supported with structured output. "
                "Response will be buffered and processed after completion."
            )
            stream = False
        
        # Initialize performance tracking
        performance_tracker = None
        if self.config.track_request_transformation:
            performance_tracker = PerformanceTracker(enabled=True)
            performance_tracker.start_tracking()
        
        try:
            # Process structured output request
            if response_format:
                if performance_tracker:
                    performance_tracker.start_operation("request_transformation")
                
                processed_kwargs, structured_request = self._structured_processor.process_request(
                    response_format=response_format,
                    strict_json_parsing=strict_json_parsing,
                    strict_schema_validation=strict_schema_validation,
                    json_repair_mode=json_repair_mode,
                    model=model,
                    messages=messages,
                    stream=stream,
                    **kwargs
                )
                
                if performance_tracker:
                    performance_tracker.end_operation("request_transformation")
            else:
                processed_kwargs = kwargs
                structured_request = None
            
            # Apply provider transformation ONLY if not already processed
            # _structured_processor.process_request already calls transform_request
            if not structured_request:
                # Combine messages and kwargs for transformation
                request_params = processed_kwargs.copy()
                request_params["messages"] = messages
                request_params["stream"] = stream
                
                provider = getattr(self._structured_processor, "provider", None)
                if provider:
                    request_params = provider.transform_request(request_params)
                
                # Update locals based on transformed params
                messages = request_params.pop("messages", messages)
                stream = request_params.pop("stream", stream)
                processed_kwargs = request_params
            
            # Remove duplicated parameters from kwargs if they were re-inserted
            # This is safety cleanup for the else path or if provider put them back
            if "messages" in processed_kwargs:
                processed_kwargs.pop("messages")
            if "stream" in processed_kwargs:
                processed_kwargs.pop("stream")
            
            # Remove model from kwargs if present (it's passed as arg)
            processed_kwargs.pop('model', None)
            
            # Make API call
            if performance_tracker:
                performance_tracker.start_operation("api_call")
            
            provider = getattr(self._structured_processor, "provider", None)
            
            if provider and hasattr(provider, "execute_request"):
                # Delegate entirely to provider adapter
                response = provider.execute_request(
                    client=self._client,
                    model=model,
                    messages=messages,
                    stream=stream,
                    **processed_kwargs
                )
            else:
                # Use standard OpenAI client
                response = super().create(
                    model=model,
                    messages=messages,
                    stream=stream,
                    **processed_kwargs
                )
            
            if performance_tracker:
                performance_tracker.end_operation("api_call")
            
            # Process structured output response
            if structured_request:
                return self._process_structured_response(
                    response, structured_request, performance_tracker
                )
            else:
                # Return standard response with performance info
                if performance_tracker:
                    perf_info = performance_tracker.end_tracking()
                    # Add performance info to response if possible
                    if hasattr(response, '__dict__'):
                        response.performance_info = perf_info
                
                return response
        
        except Exception as e:
            if performance_tracker:
                try:
                    performance_tracker.end_tracking()
                except Exception:
                    # Ignore errors during cleanup to preserve original exception
                    pass
            
            logger.error(f"Chat completion failed: {e}")
            raise

    def _process_structured_response(
        self,
        response: ChatCompletion,
        structured_request,
        performance_tracker: Optional[PerformanceTracker] = None
    ) -> EnhancedChatCompletion:
        """Process structured output response.
        
        Args:
            response: Raw response from OpenAI
            structured_request: Structured output request info
            performance_tracker: Performance tracker for timing
            
        Returns:
            Enhanced chat completion
        """
        # Convert response to dict for processing
        response_dict = response.model_dump()
        if performance_tracker:
            performance_tracker.start_operation("structure_processing")
            
        # Debug: Check raw response
        # print(f"DEBUG: Processing response from {getattr(self._structured_processor, 'provider', 'unknown')}: {response}")
        
        enhanced_message = self._structured_processor.process_response(
            response_dict,
            structured_request,
            performance_tracker
        )
        # Debug: Check result
        # print(f"DEBUG: Processed result: {enhanced_message}")
        
        from vidai.models import EnhancedChoice

        # Create enhanced completion
        return EnhancedChatCompletion(
            id=response.id,
            choices=[
                EnhancedChoice(
                    index=0,
                    message=enhanced_message,
                    finish_reason=response.choices[0].finish_reason if response.choices else "stop"
                )
            ],
            created=response.created,
            model=response.model,
            object=response.object,
            system_fingerprint=getattr(response, 'system_fingerprint', None),
            usage=getattr(response, 'usage', None),
            performance_info=enhanced_message.performance_info
        )


class EnhancedChat(Chat):
    """Enhanced chat resource."""
    
    def __init__(self, client: BaseOpenAI, config: VidaiConfig, structured_processor: StructuredOutputProcessor) -> None:
        super().__init__(client)
        self._enhanced_completions = EnhancedCompletions(client, config, structured_processor)
        
    @property
    def completions(self) -> EnhancedCompletions:
        return self._enhanced_completions


class EnhancedResponses(Responses):
    """Enhanced responses resource."""
    
    def __init__(self, client: BaseOpenAI, config: VidaiConfig, structured_processor: StructuredOutputProcessor) -> None:
        super().__init__(client)
        self.config = config
        self._structured_processor = structured_processor

    def create(
        self,
        *,
        model: str,
        **kwargs
    ):
        """Create a response."""
        # Capture performance if enabled prior to processing
        performance_tracker = None
        if self.config.track_request_transformation:
            performance_tracker = PerformanceTracker(enabled=True)
            performance_tracker.start_tracking()
            performance_tracker.start_operation("api_call")

        try:
            # 1. Process Structured Output Request
            # Extract arguments specific to structured output
            response_format = kwargs.pop("response_format", None)
            
            # VidaiSDK specific overrides
            strict_json_parsing = kwargs.pop("strict_json_parsing", None)
            strict_schema_validation = kwargs.pop("strict_schema_validation", None) 
            json_repair_mode = kwargs.pop("json_repair_mode", None)
            
            structured_request = None
            
            # Only process if we have a structured output indicator (Pydantic model)
            # or if explicit config overrides are present that imply we want processing.
            # Native kwargs (schema dict) are passed through unless we want tool-polyfill via provider.
            
            should_process = (
                response_format is not None and 
                (isinstance(response_format, type) or self._structured_processor.provider)
            )

            if should_process:
                # This modifies kwargs in-place (e.g. converting pydantic to json_schema)
                # and returns a request object we can use for post-processing if needed
                msgs = kwargs.pop("messages", [])
                kwargs, structured_request = self._structured_processor.process_request(
                    response_format=response_format, 
                    messages=msgs,
                    strict_json_parsing=strict_json_parsing,
                    strict_schema_validation=strict_schema_validation,
                    json_repair_mode=json_repair_mode,
                    **kwargs
                )
                # Put messages back for downstream
                kwargs["messages"] = msgs
            
            # Check if we should delegate to provider adapter
            provider = getattr(self._structured_processor, "provider", None)
            
            if provider and hasattr(provider, "execute_response_request"):
                 try:
                    response = provider.execute_response_request(
                        client=self._client,
                        model=model,
                        **kwargs
                    )
                 except NotImplementedError:
                     # Fallback to OpenAI native if provider doesn't support it 
                     # (though if it's OpenAIProvider it should handle or fall through)
                     response = super().create(
                        model=model,
                        **kwargs
                    )
            else:
                # Default OpenAI behavior
                response = super().create(
                    model=model,
                    **kwargs
                )
            
            if performance_tracker:
                performance_tracker.end_operation("api_call")
                perf_info = performance_tracker.end_tracking()
                
                # Convert output dicts to Pydantic objects for Object Parity
                from vidai.models import EnhancedResponse, ResponseOutputMessage, ResponseOutputText
                
                typed_output = []
                # response.output is a list of dicts or objects
                # Native OpenAI returns objects, Polyfills might return dicts
                
                raw_output = getattr(response, "output", [])
                
                for item in raw_output:
                    if isinstance(item, dict):
                        # Convert dict to object
                        # content might be a string (JSON string) or list
                        raw_content = item.get("content")
                        
                        if isinstance(raw_content, str):
                            # Normalize single string content to list of Text objects
                            content_objs = [ResponseOutputText(text=raw_content)]
                        elif isinstance(raw_content, list):
                            # Recursively parse content items
                            content_objs = []
                            for c in raw_content:
                                if isinstance(c, dict):
                                    content_objs.append(ResponseOutputText(**c))
                                elif isinstance(c, ResponseOutputText):
                                    content_objs.append(c)
                                else:
                                    # Fallback for unknown
                                    content_objs.append(ResponseOutputText(text=str(c)))
                        else:
                             content_objs = []

                        typed_output.append(ResponseOutputMessage(
                            id=item.get("id"),
                            role=item.get("role", "assistant"),
                            content=content_objs,
                            type=item.get("type", "message")
                        ))
                    elif hasattr(item, "content"):
                         # Already an object? Just append or clone
                         # Ensure content is list of texts if specific type needed
                         # For now assume native object is compatible or pass through
                         # But likely we want to wrap it in OUR type for consistency
                         # Native: item.content is list of ResponseOutputText
                         
                         native_content = item.content
                         content_objs = []
                         if isinstance(native_content, list):
                             for c in native_content:
                                 if hasattr(c, "text"):
                                      content_objs.append(ResponseOutputText(text=c.text))
                                 else:
                                      content_objs.append(ResponseOutputText(text=str(c)))
                                      
                         typed_output.append(ResponseOutputMessage(
                             id=getattr(item, "id", None),
                             role=getattr(item, "role", "assistant"),
                             content=content_objs,
                             type=getattr(item, "type", "message")
                         ))

                # Wrap response in EnhancedResponse (Pydantic Model)
                return EnhancedResponse(
                    id=response.id,
                    object=response.object,
                    created=getattr(response, "created", None),
                    model=response.model,
                    output=typed_output,
                    usage=response.usage,
                    performance_info=perf_info
                )
                
            return response
            
        except Exception as e:
            if performance_tracker:
                 try:
                     performance_tracker.end_tracking()
                 except: 
                     pass
            raise e


class Vidai(BaseOpenAI):
    """Vidai wrapper for OpenAI-compatible APIs."""
    
    def __init__(
        self,
        *,
        config: Optional[VidaiConfig] = None,
        base_url: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize Vidai.
        
        Args:
            config: Configuration settings (defaults to env vars)
            base_url: Base URL for API (required if not in config)
            **kwargs: Additional arguments passed to OpenAI client
        """
        # Initialize configuration
        self.config = config or VidaiConfig.from_env()
        
        # Determine base URL
        if base_url:
            final_base_url = base_url
        elif self.config.default_base_url:
            final_base_url = self.config.default_base_url
        else:
            final_base_url = "https://api.openai.com/v1"
        
        # Setup logging
        setup_logging(self.config)
        
        # Initialize provider adapter
        from .providers import ProviderFactory
        self._provider = ProviderFactory.create_provider(self.config, base_url=final_base_url)

        # Initialize structured output processor
        self._structured_processor = StructuredOutputProcessor(self.config, self._provider)
        
        # Initialize parent OpenAI client
        super().__init__(base_url=final_base_url, **kwargs)
        
        # Set max_retries attribute for compatibility
        self.max_retries = 3
        
        # Initialize enhanced resources
        self._enhanced_chat = EnhancedChat(self, self.config, self._structured_processor)
        self._enhanced_responses = EnhancedResponses(self, self.config, self._structured_processor)
        
        logger.info(f"Vidai initialized with base_url: {final_base_url}")
    
    @property
    def chat(self) -> EnhancedChat:
        return self._enhanced_chat

    @property
    def responses(self) -> EnhancedResponses:
        return self._enhanced_responses

    def copy_with_config(self, **config_overrides) -> "Vidai":
        """Create a copy of client with configuration overrides.
        
        Args:
            **config_overrides: Configuration parameters to override
            
        Returns:
            New Vidai with overridden configuration
        """
        new_config = self.config.copy(**config_overrides)
        
        return self.__class__(
            config=new_config,
            base_url=self.base_url,
            api_key=self.api_key,
            organization=self.organization,
            timeout=self.timeout,
            max_retries=self.max_retries
        )
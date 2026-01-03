"""Mock response data for testing all 5 providers."""

from typing import Dict, Any, List

# OpenAI mock responses
OPENAI_RESPONSES = {
    "valid_json": {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    },
    "invalid_json_trailing_comma": {
        "id": "chatcmpl-124",
        "object": "chat.completion",
        "created": 1677652289,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"name": "John Doe", "age": 30, "email": "john@example.com",}'
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    },
    "invalid_json_single_quotes": {
        "id": "chatcmpl-125",
        "object": "chat.completion",
        "created": 1677652290,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "{'name': 'John Doe', 'age': 30, 'email': 'john@example.com'}"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    },
    "invalid_json_missing_bracket": {
        "id": "chatcmpl-126",
        "object": "chat.completion",
        "created": 1677652291,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"name": "John Doe", "age": 30, "email": "john@example.com"'
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    },
    "non_json_content": {
        "id": "chatcmpl-127",
        "object": "chat.completion",
        "created": 1677652292,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "I'm sorry, I cannot generate JSON content at this time."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    },
    "streaming_valid": [
        "data: {\"id\": \"chatcmpl-128\", \"object\": \"chat.completion.chunk\", \"created\": 1677652293, \"model\": \"gpt-4\", \"choices\": [{\"index\": 0, \"delta\": {\"role\": \"assistant\"}, \"finish_reason\": null}]}\n\n",
        "data: {\"id\": \"chatcmpl-128\", \"object\": \"chat.completion.chunk\", \"created\": 1677652293, \"model\": \"gpt-4\", \"choices\": [{\"index\": 0, \"delta\": {\"content\": \"{\\\"name\\\": \\\"John\"}, \"finish_reason\": null}]}\n\n",
        "data: {\"id\": \"chatcmpl-128\", \"object\": \"chat.completion.chunk\", \"created\": 1677652293, \"model\": \"gpt-4\", \"choices\": [{\"index\": 0, \"delta\": {\"content\": \" Doe\\\", \\\"age\\\": 30}\"}, \"finish_reason\": null}]}\n\n",
        "data: {\"id\": \"chatcmpl-128\", \"object\": \"chat.completion.chunk\", \"created\": 1677652293, \"model\": \"gpt-4\", \"choices\": [{\"index\": 0, \"delta\": {\"content\": \"}\"}, \"finish_reason\": \"stop\"}]}\n\n",
        "data: [DONE]\n\n"
    ]
}

# Anthropic mock responses
ANTHROPIC_RESPONSES = {
    "valid_json": {
        "id": "msg_123",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
            }
        ],
        "model": "claude-3-5-sonnet",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {
            "input_tokens": 10,
            "output_tokens": 15
        }
    },
    "tool_call_format": {
        "id": "msg_124",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "tool_use",
                "id": "toolu_123",
                "name": "generate_json",
                "input": {"name": "John Doe", "age": 30, "email": "john@example.com"}
            }
        ],
        "model": "claude-3-5-sonnet",
        "stop_reason": "tool_use",
        "stop_sequence": None,
        "usage": {
            "input_tokens": 10,
            "output_tokens": 15
        }
    },
    "invalid_json": {
        "id": "msg_125",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "{'name': 'John Doe', 'age': 30, 'email': 'john@example.com',}"
            }
        ],
        "model": "claude-3-5-sonnet",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {
            "input_tokens": 10,
            "output_tokens": 15
        }
    },
    "streaming_valid": [
        "event: message_start\ndata: {\"type\": \"message_start\", \"message\": {\"id\": \"msg_126\", \"type\": \"message\", \"role\": \"assistant\", \"content\": [], \"model\": \"claude-3-5-sonnet\", \"stop_reason\": null, \"stop_sequence\": null, \"usage\": {\"input_tokens\": 10, \"output_tokens\": 0}}}\n\n",
        "event: content_block_start\ndata: {\"type\": \"content_block_start\", \"index\": 0, \"content_block\": {\"type\": \"text\", \"text\": \"\"}}\n\n",
        "event: content_block_delta\ndata: {\"type\": \"content_block_delta\", \"index\": 0, \"delta\": {\"type\": \"text_delta\", \"text\": \"{\\\"name\\\": \\\"John\"}}\n\n",
        "event: content_block_delta\ndata: {\"type\": \"content_block_delta\", \"index\": 0, \"delta\": {\"type\": \"text_delta\", \"text\": \" Doe\\\", \\\"age\\\": 30}\"}\n\n",
        "event: content_block_delta\ndata: {\"type\": \"content_block_delta\", \"index\": 0, \"delta\": {\"type\": \"text_delta\", \"text\": \"}\"}}\n\n",
        "event: message_stop\ndata: {\"type\": \"message_stop\"}\n\n"
    ]
}

# Mistral mock responses
MISTRAL_RESPONSES = {
    "valid_json": {
        "id": "cmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "mistral-large",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    },
    "guided_decoding": {
        "id": "cmpl-124",
        "object": "chat.completion",
        "created": 1677652289,
        "model": "mistral-large",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    },
    "invalid_json": {
        "id": "cmpl-125",
        "object": "chat.completion",
        "created": 1677652290,
        "model": "mistral-large",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"name": "John Doe", "age": 30, "email": "john@example.com",}'
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    }
}

# Gemini mock responses
GEMINI_RESPONSES = {
    "valid_json": {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
                        }
                    ],
                    "role": "model"
                },
                "finishReason": "STOP",
                "index": 0,
                "safetyRatings": [
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "probability": "NEGLIGIBLE"},
                    {"category": "HARM_CATEGORY_HARASSMENT", "probability": "NEGLIGIBLE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "probability": "NEGLIGIBLE"}
                ]
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 5,
            "candidatesTokenCount": 15,
            "totalTokenCount": 20
        }
    },
    "candidates_format": {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
                        }
                    ],
                    "role": "model"
                },
                "finishReason": "STOP",
                "index": 0
            }
        ]
    },
    "invalid_json": {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "{'name': 'John Doe', 'age': 30, 'email': 'john@example.com'}"
                        }
                    ],
                    "role": "model"
                },
                "finishReason": "STOP",
                "index": 0
            }
        ]
    }
}

# VLLM mock responses
VLLM_RESPONSES = {
    "valid_json": {
        "id": "cmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "llama-3-8b-instruct",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    },
    "guided_json": {
        "id": "cmpl-124",
        "object": "chat.completion",
        "created": 1677652289,
        "model": "llama-3-8b-instruct",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    },
    "invalid_json": {
        "id": "cmpl-125",
        "object": "chat.completion",
        "created": 1677652290,
        "model": "llama-3-8b-instruct",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"name": "John Doe", "age": 30, "email": "john@example.com",}'
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    }
}

# Combined mock responses
MOCK_RESPONSES = {
    "openai": OPENAI_RESPONSES,
    "anthropic": ANTHROPIC_RESPONSES,
    "mistral": MISTRAL_RESPONSES,
    "gemini": GEMINI_RESPONSES,
    "vllm": VLLM_RESPONSES
}

# Test data fixtures
TEST_USER_SCHEMA = {
    "type": "json_object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["name", "age", "email"]
}

INVALID_JSON_SAMPLES = [
    '{"name": "John", "age": 30,}',  # trailing comma
    "{'name': 'John', 'age': 30}",  # single quotes
    '{"name": "John", "age": 30',   # missing closing brace
    '{"name": "John", age: 30}',    # unquoted key
]

VALID_JSON_SAMPLES = [
    '{"name": "John", "age": 30, "email": "john@example.com"}',
    '{"name": "Jane", "age": 25, "email": "jane@example.com"}',
    '{"name": "Bob", "age": 35, "email": "bob@example.com"}',
]
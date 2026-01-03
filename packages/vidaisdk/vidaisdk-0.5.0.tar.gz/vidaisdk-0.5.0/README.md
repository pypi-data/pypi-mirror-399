# Vidai

Universal OpenAI-compatible Client with structured output guarantees and provider abstraction.

## Installation

```bash
pip install vidaisdk
```

## Quick Start

```python
import os
from vidai import Vidai
from pydantic import BaseModel

# Optional: Alias as OpenAI for drop-in compatibility if desired
# from vidai import Vidai as OpenAI

class User(BaseModel):
    name: str
    age: int

client = Vidai(
    api_key=os.environ.get("OPENAI_API_KEY"),
    # It sends requests to OpenAI by default,
    # but strictly validates/repairs responses locally
)
# If you want to use a custom base_url or proxy, you can do this:
# client = Vidai(
#     api_key="your-key",
#     base_url="https://your-proxy.com/v1"
# )

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Create a user named John, age 25"}],
    response_format=User
)

user = response.choices[0].message.parsed
print(user.name)  # "John"
print(user.age)   # 25
```

### Using with Vidai Server (Auto-Discovery)

Vidai acts as a smart facade when connected to a Vidai Server proxy. It automatically discovers available models and applies provider-specific optimizations (like Claude tool-use) without any client-side configuration changes.

1. Set your environment:
```bash
export VIDAI_PROVIDER=vidai
export VIDAI_BASE_URL=http://localhost:8000/v1
export VIDAI_SERVER_API_KEY=sk-...
```

2. Use the client as usual:
```python
client = Vidai() # Automatically detects 'vidai' provider from env
# Automatically routes to Anthropic, DeepSeek, Google based on model name
response = client.chat.completions.create(model="claude-3-haiku", ...)
```


## Features

- **Drop-in Compatibility**: 100% compatible with OpenAI SDK API (Completions & Responses)
- **Responses API**: Type-safe, object-based access normalized across all providers.
- **Structured Output Guarantees**: Automatic JSON repair and validation
- **Performance Tracking**: Monitor SDK overhead and repair times
- **Provider Agnostic**: Works with any AI provider through your proxy
- **Developer Friendly**: Clear error messages and debugging support

## Documentation
    
See the [GitHub Repository](https://github.com/vidaiUK/vidaisdk) for the latest updates.

## License

Apache-2.0
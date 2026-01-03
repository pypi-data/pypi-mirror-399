import os
import json
from vidai import Vidai, VidaiConfig

# --- Feature: Tool/Function Calling ---
# This example demonstrates letting the model call a defined function.
# Default Provider: Anthropic (Can be swapped with OpenAI, Gemini, etc.)
# Note: For Anthropic, we use VidaiConfig(provider="anthropic")

api_key = os.getenv("ANTHROPIC_API_KEY")
config = VidaiConfig(provider="anthropic")

client = Vidai(
    api_key=api_key, 
    base_url="https://api.anthropic.com/v1",
    config=config
)

# 1. Define the tool
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["location"]
        }
    }
}]

print("--- Tool Calling (Weather) ---")

response = client.chat.completions.create(
    model="claude-3-5-sonnet-20240620",
    messages=[{"role": "user", "content": "What's the weather in London in Celsius?"}],
    tools=tools,
    tool_choice="auto"
)

# 2. Handle the tool call
message = response.choices[0].message
if message.tool_calls:
    tool_call = message.tool_calls[0]
    print(f"Tool Called: {tool_call.function.name}")
    args = json.loads(tool_call.function.arguments)
    print(f"Arguments: {args}")
else:
    print("Response:", message.content)

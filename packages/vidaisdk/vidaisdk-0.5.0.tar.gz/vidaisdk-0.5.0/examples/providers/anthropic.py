import os
from vidai import Vidai, VidaiConfig

# Vidai automatically handles message formatting for Anthropic
api_key = os.getenv("ANTHROPIC_API_KEY")

# Explicitly set provider to 'anthropic' for correct adapter usage if not using a proxy
config = VidaiConfig(provider="anthropic")

client = Vidai(
    api_key=api_key,
    base_url="https://api.anthropic.com/v1",
    config=config
)

print("--- Anthropic Example ---")
response = client.chat.completions.create(
    model="claude-3-5-sonnet-20240620",
    messages=[{"role": "user", "content": "Haiku about code."}]
)
print(f"Response: {response.choices[0].message.content}")

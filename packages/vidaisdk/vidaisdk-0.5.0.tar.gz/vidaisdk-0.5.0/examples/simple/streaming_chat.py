import os
from vidai import Vidai

# --- Feature: Streaming ---
# This example demonstrates real-time token streaming.
# Default Provider: Groq (Can be swapped with OpenAI, Anthropic, etc.)
# Groq is excellent for demonstrating high-speed streaming.

api_key = os.getenv("GROQ_API_KEY")
client = Vidai(
    api_key=api_key, 
    base_url="https://api.groq.com/openai/v1"
)

print("--- Streaming Chat ---")
print("Bot: ", end="", flush=True)

# 1. Enable stream=True
stream = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Write a short poem about speed."}],
    stream=True
)

# 2. Iterate over chunks
for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)

print("\n--- End of Stream ---")

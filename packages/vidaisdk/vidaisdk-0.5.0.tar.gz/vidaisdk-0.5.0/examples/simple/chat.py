import os
from vidai import Vidai

# Simple chat example
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Please set OPENAI_API_KEY")
    exit(1)

client = Vidai(api_key=api_key)

# 1. Completions API (Standard)
print("--- Completions API ---")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello world!"}]
)
print(response.choices[0].message.content)

# 2. Responses API (Object-based)
print("\n--- Responses API ---")
response = client.responses.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello world!"}]
)
# Access content safely via object model
for item in response.output:
    if item.type == "message":
        print(item.content[0].text)

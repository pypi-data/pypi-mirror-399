import os
from vidai import Vidai

# Set via env or explicitly
api_key = os.getenv("OPENAI_API_KEY")

# OpenAI is the default provider config
client = Vidai(api_key=api_key)

print("--- OpenAI Example ---")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Explain quantum computing in one sentence."}]
)
print(f"Response: {response.choices[0].message.content}")

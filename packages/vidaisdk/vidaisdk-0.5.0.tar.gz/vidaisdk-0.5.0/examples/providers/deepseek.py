import os
from vidai import Vidai

# DeepSeek is fully OpenAI compatible
api_key = os.getenv("DEEPSEEK_API_KEY")

client = Vidai(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)

print("--- DeepSeek Example ---")
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "What is Python?"}]
)
print(f"Response: {response.choices[0].message.content}")

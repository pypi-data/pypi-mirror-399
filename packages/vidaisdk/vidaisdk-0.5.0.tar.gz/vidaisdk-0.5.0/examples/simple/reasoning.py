import os
from vidai import Vidai

# --- Feature: Reasoning / Thinking Models ---
# This example demonstrates using a "thinking" model that outputs reasoning process.
# Default Provider: DeepSeek (Can be swapped with OpenAI o1, etc.)
# Note: Vidai handles standardizing reasoning token output where possible.

api_key = os.getenv("DEEPSEEK_API_KEY")
client = Vidai(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)

print("--- Reasoning Task ---")

# 1. Ask a complex logic question
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[
        {"role": "user", "content": "If I have 3 apples and you take 2, how many do you have?"}
    ]
)

# For DeepSeek, reasoning content might be in the main content or specific fields depending on the adapter
# Vidai ensures the final answer is in message.content
print(f"Final Answer: {response.choices[0].message.content}")

# (Optional: Some providers expose reasoning_content separately, inspect response if needed)
if hasattr(response.choices[0].message, "reasoning_content"):
     print(f"Reasoning Trace: {response.choices[0].message.reasoning_content[:100]}...")

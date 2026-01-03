import os
from vidai import Vidai, VidaiConfig

# Uses Google's OpenAI-compatible endpoint
api_key = os.getenv("GEMINI_API_KEY")

client = Vidai(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

print("--- Gemini Example ---")
# Gemini Models often have prefixes like 'models/' or just 'gemini-1.5-flash'
response = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=[{"role": "user", "content": "List 3 planets."}]
)
print(f"Response: {response.choices[0].message.content}")

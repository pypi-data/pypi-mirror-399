import os
from vidai import Vidai

# --- Feature: Vision / Multimodal ---
# This example demonstrates analyzing an image URL.
# Default Provider: Google Gemini (Can be swapped with OpenAI GPT-4o, Anthropic Claude 3.5, etc.)

api_key = os.getenv("GEMINI_API_KEY")
client = Vidai(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

print("--- Image Analysis ---")

# 1. Pass image_url in content list
response = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=[
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": "What is in this image?"},
                {
                    "type": "image_url", 
                    "image_url": {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"}
                }
            ]
        }
    ]
)

print("Description:", response.choices[0].message.content)

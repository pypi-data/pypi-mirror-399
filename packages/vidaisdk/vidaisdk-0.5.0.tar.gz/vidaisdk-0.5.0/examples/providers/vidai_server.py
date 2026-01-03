import os
from vidai import Vidai, VidaiConfig

# Vidai Server acts as a gateway
api_key = os.getenv("VIDAI_SERVER_API_KEY")
base_url = os.getenv("VIDAI_BASE_URL", "http://localhost:3000/v1")

# Use 'vidai-server' provider to enable specific headers/tracing
config = VidaiConfig(provider="vidai-server", track_request_transformation=True)

client = Vidai(
    api_key=api_key,
    base_url=base_url,
    config=config
)

print("--- Vidai Server Example ---")
# The server handles model routing
response = client.chat.completions.create(
    model="gpt-4o-mini", # Or any mapped model
    messages=[{"role": "user", "content": "Are you running on a server?"}]
)
print(f"Response: {response.choices[0].message.content}")

# Check performance headers if available
if response.choices[0].finish_reason:
    print(f"Finish Reason: {response.choices[0].finish_reason}")


import os
import time
from dotenv import load_dotenv
from vidai import Vidai, VidaiConfig

def load_env():
    """Simple .env loader"""
    try:
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k] = v
    except FileNotFoundError:
        print("No .env file found. Assuming env vars are set.")

def verify_caching():
    print("--- Verifying Anthropic Prompt Caching ---")
    load_env()
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Skipping: ANTHROPIC_API_KEY not found")
        return

    client = Vidai(
        api_key=api_key,
        config=VidaiConfig(provider="anthropic")
    )
    
    # Large system prompt to make caching worth it
    large_text = "This is a large text context that repeats. " * 500
    
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": f"Here is some context: {large_text}",
                    "cache_control": {"type": "ephemeral"} # CACHE MARKER
                },
                {
                    "type": "text", 
                    "text": "What is the third word in the context?"
                }
            ]
        }
    ]
    
    model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
    print(f"Using model: {model}")

    # First Run (Cache Creation)
    print("\n1. First Run (Expect Cache Creation)...")
    start = time.time()
    try:
        resp1 = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=100
        )
        print(f"Response: {resp1.choices[0].message.content}")
        # Note: Vidai wraps response, need to check if we expose raw usage with cache stats
        # Standard OpenAI usage object doesn't have cache stats usually.
        # But we pass through extra fields? Let's check.
        # If mapped object filters it out, we might need to inspect raw response or check logs.
        # But let's assume Vidai passes `usage` dict as is or mapped `Usage` object.
        # standard Usage has `prompt_tokens`, `completion_tokens`, `total_tokens`.
        # Anthropic adds `cache_creation_input_tokens` and `cache_read_input_tokens` to usage.
        # We need to verify if these are accessible.
        
        # Accessing underlying dict if possible, or attributes if added to model
        usage = resp1.usage
        print(f"Usage: {usage}")
        # Check attributes via dict access if model allows
        if hasattr(usage, "model_extra"):
             print(f"Usage Extra: {usage.model_extra}")
        elif isinstance(usage, dict):
             print(f"Usage Dict: {usage}")
             
    except Exception as e:
        print(f"Error: {e}")

    # Second Run (Cache Hit)
    print("\n2. Second Run (Expect Cache Hit)...")
    try:
        resp2 = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=100
        )
        print(f"Response: {resp2.choices[0].message.content}")
        print(f"Usage: {resp2.usage}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_caching()

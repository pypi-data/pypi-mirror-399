import os
from vidai import Vidai, VidaiConfig

# Mock API key to avoid error during init
os.environ["OPENAI_API_KEY"] = "sk-test"

def verify_dropin():
    """Verify drop-in replacement architecture."""
    client = Vidai(api_key="test-key", base_url="https://api.example.com/v1")
    
    print(f"Client type: {type(client)}")
    print(f"Chat resource type: {type(client.chat)}")
    print(f"Completions resource type: {type(client.chat.completions)}")
    
    # Assertions
    assert isinstance(client, Vidai), "Client is not a Vidai instance"
    assert "vidai.client.EnhancedChat" in str(type(client.chat)), "Chat resource not enhanced"
    
    print("SUCCESS: Drop-in replacement architecture verified.")

if __name__ == "__main__":
    verify_dropin()

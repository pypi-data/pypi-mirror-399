"""Comprehensive VidaiProxy verification suite."""
import os
import sys
from dotenv import load_dotenv

# Add project root to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, root_dir)

import vidai
print(f"DEBUG: Using vidai from {vidai.__file__}")

from vidai import Vidai, VidaiConfig

load_dotenv()

MODELS_TO_TEST = [
    {"id": "deepseek-chat", "expected_provider": "deepseek"},
    {"id": "deepseek-reasoner", "expected_provider": "deepseek"},
    {"id": "moonshotai/kimi-k2-instruct-0905", "expected_provider": "groq"}, 
    {"id": "models/gemini-2.5-flash", "expected_provider": "gemini"},
    {"id": "qwen/qwen3-235b-a22b-thinking-2507", "expected_provider": "openai"}, 
    {"id": "claude-haiku-4-5-20251001", "expected_provider": "anthropic"},
]

def run_suite():
    print("🚀 Starting Proxy Verification Suite...")
    
    # Check Env
    vidai_key = os.getenv("VIDAI_SERVER_API_KEY")
    base_url = os.getenv("VIDAI_BASE_URL", "http://localhost:3000/v1")
    
    if not vidai_key:
        print("❌ Missing VIDAI_SERVER_API_KEY")
        return

    config = VidaiConfig(provider="vidai", log_level="WARNING")
    client = Vidai(base_url=base_url, api_key=vidai_key, config=config)
    
    # Force ensure initialized to print cache
    client._provider._ensure_initialized()
    print(f"📦 Discovered Models: {len(client._provider._model_cache)} found.")
    
    success_count = 0
    
    for test_case in MODELS_TO_TEST:
        model = test_case["id"]
        expected = test_case["expected_provider"]
        
        print(f"\n🧪 Testing Model: {model}")
        
        # Verify Routing Decision
        # Just calling _get_delegate_for_model triggers the decision logic
        delegate = client._provider._get_delegate_for_model(model)
        delegate_name = type(delegate).__name__
        
        # Map class name to simple name for verification
        actual_provider = "openai"
        if "Anthropic" in delegate_name: actual_provider = "anthropic"
        elif "DeepSeek" in delegate_name: actual_provider = "deepseek"
        elif "Gemini" in delegate_name: actual_provider = "gemini"
        elif "Groq" in delegate_name: actual_provider = "groq"
        
        # Check mapping
        if actual_provider != expected:
            print(f"⚠️  Routing Warning: Mapped to {actual_provider}, expected {expected}")
        else:
            print(f"✅ Routing Correct: Mapped to {actual_provider}")
            
        # Attempt Call
        try:
            print(f"   Sending request...")
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hello. Short reply."}]
            )
            print(f"   ✅ Success! Response: {response.choices[0].message.content[:50]}...")
            success_count += 1
        except Exception as e:
            print(f"   ❌ Call Failed: {e}")
            
    print(f"\n🎉 Suite Complete. {success_count}/{len(MODELS_TO_TEST)} Succeeded.")

if __name__ == "__main__":
    run_suite()

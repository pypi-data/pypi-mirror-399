"""Real world verification of Vidai (Completions & Responses)."""
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from vidai import Vidai, VidaiConfig

# Load env
load_dotenv()

def verify_provider(name, client, model, supports_responses=True):
    print(f"\n🚀 Verifying Provider: {name} (Model: {model})")
    
    # 1. Test Chat Completions (Legacy)
    try:
        print(f"  [Completions] Sending request...")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'Completions OK' briefly."}],
            max_tokens=20
        )
        content = response.choices[0].message.content.strip()
        print(f"  ✅ [Completions] Success: {content}")
    except Exception as e:
        print(f"  ❌ [Completions] Failed: {e}")

    # 2. Test Responses (New)
    if not supports_responses:
         print(f"  Existing skipping [Responses] for {name} (Not fully implemented yet)")
         return

    try:
        print(f"  [Responses] Sending request...")
        # Note: 'responses' API uses 'input' instead of 'messages'
        response = client.responses.create(
            model=model,
            input="Say 'Responses OK' briefly.",
            max_output_tokens=20
        )
        
        content = "N/A"
        if hasattr(response, "output"):
            # Inspect output items
            for item in response.output:
                if isinstance(item, dict):
                     # Native API structure might vary, looking for message/content
                     if item.get("type") == "message":
                         content = item.get("content")
                         break
                     # Fallback for simple text output if structure differs
                     if "content" in item:
                         content = item["content"]
        
        print(f"  ✅ [Responses] Success: {content}")
        
        if hasattr(response, "performance_info") and response.performance_info and response.performance_info.total_sdk_overhead_ms:
             print(f"     Latency (Overhead): {response.performance_info.total_sdk_overhead_ms:.2f}ms")

    except Exception as e:
        print(f"  ❌ [Responses] Failed: {e}")

    # 3. Test Structured Output Polyfill (Responses)
    if not supports_responses:
         # Skip explicitly if verification failed above
         return
    
    # Run structured output on all providers now to verify universal polyfill
    if name == "OpenAI" or name == "VidaiServer":
        # VidaiServer might fail if model missing, but let's try
        # OpenAI fails on auth, so skip
        if name == "OpenAI": return

    try:
        print(f"  [Structured Responses] Sending request with Pydantic model...")
        
        from pydantic import BaseModel
        class MathReasoning(BaseModel):
            steps: list[str]
            final_answer: str

        response = client.responses.create(
            model=model,
            input="Solve 2x + 5 = 15",
            response_format=MathReasoning,
            max_output_tokens=1000
        )
        
        found_json = False
        content = "N/A"
        
        if hasattr(response, "output"):
            for item in response.output:
                # Polyfill should unwrap tool call into a message with content
                # Response output items are ResponseOutputMessage objects
                if hasattr(item, "content") and isinstance(item.content, list):
                     # Check first text block
                     if item.content and hasattr(item.content[0], "text"):
                         content = item.content[0].text
                         if "final_answer" in content:
                             found_json = True
                             break
                elif isinstance(item, dict) and item.get("type") == "message":
                     content = item.get("content")
                     if content and "final_answer" in str(content):
                         found_json = True
                         break
        
        if found_json:
            print(f"  ✅ [Structured Responses] Success: Found JSON content in message output.")
            # print(f"     Content: {content[:100]}...")
        else:
            print(f"  ❌ [Structured Responses] Failed: No JSON content found in output messages.")
            print(f"     Output: {response.output}")

    except Exception as e:
        print(f"  ❌ [Structured Responses] Failed: {e}")

def verify_real_world():
    print("🔎 Starting Verification Suite for All Providers...")

    # --- OpenAI ---
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")
    if openai_key:
        client = Vidai(
            api_key=openai_key,
            base_url="https://api.openai.com/v1"
        )
        verify_provider("OpenAI", client, openai_model)
    
    # --- Anthropic ---
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")
    if anthropic_key:
        # Important: Provider needs to be set to 'anthropic' for mapping to work
        config = VidaiConfig(provider="anthropic")
        client = Vidai(
            api_key=anthropic_key, 
            base_url="https://api.anthropic.com/v1", # Just in case default isn't set
            config=config
        )
        verify_provider("Anthropic", client, anthropic_model)

    # --- OpenRouter ---
    or_key = os.getenv("OPENROUTER_API_KEY")
    or_model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-5-sonnet")
    if or_key:
        client = Vidai(
            api_key=or_key,
            base_url="https://openrouter.ai/api/v1"
        )
        # Verify responses via polyfill
        verify_provider("OpenRouter", client, or_model, supports_responses=True)
        
    # --- DeepSeek ---
    ds_key = os.getenv("DEEPSEEK_API_KEY")
    ds_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    if ds_key:
        client = Vidai(
            api_key=ds_key,
            base_url="https://api.deepseek.com/v1"
        )
        verify_provider("DeepSeek", client, ds_model, supports_responses=True)
    
    # --- VidaiServer ---
    vidai_key = os.getenv("VIDAI_SERVER_API_KEY")
    # Default to a model guaranteed to exist in dev/mock server
    vidai_model = os.getenv("WIZZSERVER_MODEL")
    vidai_base = os.getenv("VIDAI_BASE_URL", "http://localhost:3000/v1")
    
    if vidai_key:
        client = Vidai(
            api_key=vidai_key,
            base_url=vidai_base,
            # VidaiServer should support all features if compatible
            config=VidaiConfig(provider="vidai-server") 
        )
        verify_provider("VidaiServer", client, vidai_model, supports_responses=True)

if __name__ == "__main__":
    verify_real_world()

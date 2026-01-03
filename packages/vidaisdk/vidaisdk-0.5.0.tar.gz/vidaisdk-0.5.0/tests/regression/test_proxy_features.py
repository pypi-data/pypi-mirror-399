"""Verification of VidaiProxy advanced features (Streaming, Tools, Structured Output)."""
import os
import sys
import json
from dotenv import load_dotenv
from pydantic import BaseModel

# Add project root to path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, root_dir)

from vidai import Vidai, VidaiConfig

load_dotenv()

def verify_features():
    print("🚀 Starting Proxy Features Verification...")
    
    vidai_key = os.getenv("VIDAI_SERVER_API_KEY")
    base_url = os.getenv("VIDAI_BASE_URL", "http://localhost:3000/v1")
    
    if not vidai_key:
        print("❌ Missing VIDAI_SERVER_API_KEY")
        return

    config = VidaiConfig(provider="vidai", log_level="WARNING")
    client = Vidai(base_url=base_url, api_key=vidai_key, config=config)

    MODELS = [
        "deepseek-chat",
        "claude-haiku-4-5-20251001",
        "models/gemini-2.5-flash",
        "moonshotai/kimi-k2-instruct-0905",
        "qwen/qwen3-235b-a22b-thinking-2507"
    ]

    results = {}

    for model in MODELS:
        print(f"\n===========================================")
        print(f"🧪 Testing Model: {model}")
        print(f"===========================================")
        model_results = {"streaming": "❓", "tools": "❓", "structured": "❓"}
        
        # 1. Test Streaming
        print(f"🌊 Testing Streaming...")
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Count to 3."}],
                stream=True
            )
            chunks = 0
            content_acc = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                content_acc += content
                if content: chunks += 1
            
            if chunks > 0 and len(content_acc) > 0:
                print(f"   ✅ Success! ({chunks} chunks)")
                model_results["streaming"] = "✅"
            else:
                print(f"   ⚠️ Received empty stream.")
                model_results["streaming"] = "⚠️ Empty"
        except Exception as e:
            msg = str(e)
            if "does not support" in msg or "not supported" in msg:
                print(f"   ⚠️ Not Supported: {msg}")
                model_results["streaming"] = "⚠️ N/A"
            else:
                print(f"   ❌ Failed: {msg}")
                model_results["streaming"] = "❌ Error"

        # 2. Test Tool Use
        print(f"🔨 Testing Tool Use...")
        tools = [{
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                    "required": ["location"]
                }
            }
        }]
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "What is the weather in Tokyo?"}],
                tools=tools
            )
            # Check if tool called
            msg = response.choices[0].message
            if msg.tool_calls:
                tc = msg.tool_calls[0]
                print(f"   ✅ Tool Call: {tc.function.name}")
                model_results["tools"] = "✅"
            else:
                print(f"   ⚠️ No tool call. Content: {msg.content[:50]}...")
                model_results["tools"] = "⚠️ Ignored"
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            model_results["tools"] = "❌ Error"
            
        # 3. Test Structured Output (Simple)
        print(f"🏗️ Testing Structured Output...")
        class City(BaseModel):
            name: str
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "city: Paris"}],
                response_format=City
            )
            data = response.choices[0].message.parsed
            if isinstance(data, City) and "Paris" in data.name:
                 print(f"   ✅ Success: {data}")
                 model_results["structured"] = "✅"
            else:
                 print(f"   ❌ Failed validation. Data: {data}")
                 model_results["structured"] = "❌ Validation"
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            model_results["structured"] = "❌ Error"
            
        results[model] = model_results

    # Print Matrix Summary
    print("\n\n📊 Verification Matrix Summary")
    print(f"{'Model':<40} | {'Stream':<10} | {'Tools':<10} | {'Struct':<10}")
    print("-" * 80)
    for m, r in results.items():
        print(f"{m[:40]:<40} | {r['streaming']:<10} | {r['tools']:<10} | {r['structured']:<10}")

if __name__ == "__main__":
    verify_features()

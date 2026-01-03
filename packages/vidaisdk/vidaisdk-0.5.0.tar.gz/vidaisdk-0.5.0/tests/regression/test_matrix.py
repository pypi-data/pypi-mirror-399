
import os
import sys
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from vidai import Vidai, VidaiConfig
from pydantic import BaseModel

class MathProblem(BaseModel):
    answer: str
    steps: List[str]

load_dotenv()

PROVIDERS = {
    "Anthropic": {
        "env_key": "ANTHROPIC_API_KEY",
        "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620"),
        "config": VidaiConfig(provider="anthropic")
    }
}

RESULTS = {}

def get_client(name):
    info = PROVIDERS[name]
    key = os.getenv(info["env_key"])
    if not key:
        return None, None
    
    kwargs = {
        "api_key": key,
    }
    if "base_url" in info:
        kwargs["base_url"] = info["base_url"]
    if "config" in info:
        kwargs["config"] = info["config"]
    
    return Vidai(**kwargs), info["model"]

def test_basic_chat(client, model, use_responses=False):
    try:
        if use_responses:
            resp = client.responses.create(model=model, input="Hello", max_output_tokens=10)
            return "✅" if resp else "❌"
        else:
            resp = client.chat.completions.create(model=model, messages=[{"role":"user","content":"Hello"}], max_tokens=10)
            return "✅" if resp.choices else "❌"
    except Exception as e:
        return f"❌ ({str(e)[:20]})"

def test_structured(client, model, use_responses=False):
    try:
        if use_responses:
            resp = client.responses.create(model=model, input="2+2=?", response_format=MathProblem, max_output_tokens=100)
            # Check content for json
            if hasattr(resp, "output") and str(resp.output): return "✅"
            return "❌ No Output"
        else:
            # Not natively supported by this test script for completions yet? 
            # Vidai supports it via structured_processor but needs hooking.
            # But standard client calls don't use it automatically unless logic is invoked.
            # Actually Vidai chat.completions.create DOES invoke it if response_format is Pydantic.
            resp = client.chat.completions.create(model=model, messages=[{"role":"user","content":"2+2=?"}], response_format=MathProblem, max_tokens=100)
            return "✅" if resp.choices[0].message.parsed else "❌"
    except Exception as e:
        return f"❌ ({str(e)[:20]})"

def test_streaming(client, model, use_responses=False):
    try:
        if use_responses:
             # Streaming not yet supported/verified in polyfill
             # But let's try
             resp = client.responses.create(model=model, input="Count to 5", stream=True)
             if hasattr(resp, "__iter__"): 
                 chunks = list(resp) # Consume
                 return "✅" if len(chunks) > 0 else "❌ Empty"
             return "❌ Not Stream"
        else:
            resp = client.chat.completions.create(model=model, messages=[{"role":"user","content":"Count to 5"}], stream=True)
            chunks = list(resp)
            return "✅" if len(chunks) > 0 else "❌ Empty"
    except Exception as e:
        return f"❌ ({str(e)[:20]})"

def test_tools(client, model, use_responses=False):
    tool = {
        "type": "function",
        "function": {
            "name": "get_weather",
            "parameters": {"type":"object", "properties": {"location": {"type":"string"}}}
        }
    }
    input_text = "Weather in Tokyo?"
    try:
        if use_responses:
            resp = client.responses.create(model=model, input=input_text, tools=[tool])
            # Check for tool call in output
            # Output items should contain tool call
            found = False
            for item in resp.output:
                 if isinstance(item, dict) and item.get("type") == "tool_call": found = True
            return "✅" if found else "❌ No Call"
        else:
            resp = client.chat.completions.create(model=model, messages=[{"role":"user","content":input_text}], tools=[tool])
            return "✅" if resp.choices[0].message.tool_calls else "❌ No Call"
    except Exception as e:
        return f"❌ ({str(e)[:20]})"


def run_matrix():
    # Header
    cols = ["Provider", "API", "Basic", "Structured", "Stream", "Tools"]
    print(f"{cols[0]:<12} | {cols[1]:<12} | {cols[2]:<8} | {cols[3]:<10} | {cols[4]:<8} | {cols[5]:<8}")
    print("-" * 80)
    
    for name in PROVIDERS:
        client, model = get_client(name)
        if not client:
            print(f"{name:<12} | SKIPPED (No Key)")
            continue
            
        for api in ["Completions", "Responses"]:
            use_resp = (api == "Responses")
            
            res_basic = test_basic_chat(client, model, use_resp)
            res_struct = test_structured(client, model, use_resp)
            res_stream = test_streaming(client, model, use_resp)
            res_tools = test_tools(client, model, use_resp)
            
            print(f"{name:<12} | {api:<12} | {res_basic:<8} | {res_struct:<10} | {res_stream:<8} | {res_tools:<8}")

if __name__ == "__main__":
    run_matrix()

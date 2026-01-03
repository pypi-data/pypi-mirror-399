#!/usr/bin/env python3
"""
Real-World Test Suite for Vidai.
Runs a set of verification tests against configured providers in the environment.

Usage:
    export OPENAI_API_KEY=sk-...
    export OPENAI_MODEL=gpt-4
    export GROQ_API_KEY=gsk-...
    export GROQ_MODEL=llama3-70b-8192
    
    python examples/real_world_suite.py
"""

import os
import sys
import json
import time
import inspect
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass
from enum import Enum

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from pydantic import BaseModel, Field

# Ensure we can import vidai
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from vidai import Vidai, VidaiConfig

# --- Configuration & Discovery ---

@dataclass
class ProviderConfig:
    name: str
    api_key: str
    base_url: Optional[str]
    model: str
    supports_tools: bool = True
    supports_structured_output: bool = True
    supports_streaming: bool = True
    supports_streaming: bool = True
    supports_reasoning: bool = False
    vidai_config_overrides: Dict[str, Any] = None

def discover_providers() -> List[ProviderConfig]:
    providers = []
    
    # OpenAI
    if os.getenv("OPENAI_API_KEY"):
        providers.append(ProviderConfig(
            name="OpenAI",
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"), # Default None (standard OpenAI)
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            supports_reasoning=True # e.g. o1-preview
        ))

    # OpenRouter
    if os.getenv("OPENROUTER_API_KEY"):
        providers.append(ProviderConfig(
            name="OpenRouter",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
            supports_structured_output=True,
            supports_tools=True,
            vidai_config_overrides={"structured_output_method": "tool_fill"} # OpenRouter: Keep explicit since URL is generic
        ))

    # Google Gemini
    if os.getenv("GEMINI_API_KEY"):
        model = os.getenv("GEMINI_MODEL")
        if not model:
            print("WARNING: GEMINI_MODEL not set. Skipping Gemini or it might fail.")
            
        providers.append(ProviderConfig(
            name="Gemini",
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url=os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
            model=model,
            supports_structured_output=True, # Supports response_format
            supports_tools=True
            # No override needed: Factory detects 'generativelanguage.googleapis.com'
        ))

    # Groq
    if os.getenv("GROQ_API_KEY"):
        providers.append(ProviderConfig(
            name="Groq",
            api_key=os.getenv("GROQ_API_KEY"),
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            supports_structured_output=True, # Groq supports JSON mode mostly
            # No override needed: Factory detects 'groq.com'
        ))

    # Together AI
    if os.getenv("TOGETHER_API_KEY"):
        providers.append(ProviderConfig(
            name="Together",
            api_key=os.getenv("TOGETHER_API_KEY"),
            base_url=os.getenv("TOGETHER_BASE_URL", "https://api.together.xyz/v1"),
            model=os.getenv("TOGETHER_MODEL", "meta-llama/Llama-3-70b-chat-hf"),
            vidai_config_overrides={"structured_output_method": "tool_fill"} 
            # Together logic not added to factory yet, keep override or add to factory?
            # Keeping override for now as example of manual config.
        ))
        
    # DeepSeek
    if os.getenv("DEEPSEEK_API_KEY"):
        providers.append(ProviderConfig(
            name="DeepSeek",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            supports_reasoning=True
            # No override needed: Factory detects 'deepseek.com'
        ))

    # Anthropic (Native)
    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append(ProviderConfig(
            name="Anthropic",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            # Vidai adapter will handle the URL translation, but generally we might set a base
            # However, for native adapters, the adapter might ignore the base_url passed to OpenAI client
            base_url="https://api.anthropic.com/v1",  # This triggers the factory
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620"),
            supports_structured_output=True, # Polyfilled via tools
            supports_tools=True
        ))
        
    # Wizz Proxy (Wizz Server)
    if os.getenv("VIDAI_SERVER_API_KEY"):
        providers.append(ProviderConfig(
            name="VidaiProxy",
            api_key=os.getenv("VIDAI_SERVER_API_KEY"),
            base_url=os.getenv("VIDAI_BASE_URL", "http://localhost:8000/v1"),
            model=os.getenv("WIZZSERVER_MODEL", "gpt-4o-mini"), # Default to a model the proxy handles
            supports_structured_output=True,
            supports_tools=True
        ))

    return providers

# --- Test Definitions ---

class UserProfile(BaseModel):
    name: str
    age: int
    occupation: str
    hobbies: List[str]

def test_basic_chat(client: Vidai, config: ProviderConfig):
    """Test standard chat completion."""
    print(f"  [Running] Basic Chat ({config.model})...", end="", flush=True)
    response = client.chat.completions.create(
        model=config.model,
        messages=[{"role": "user", "content": "Say 'Hello World' and nothing else."}]
    )
    content = response.choices[0].message.content
    if "Hello World" in content:
        print(" ✅ PASSED")
    else:
        print(f" ❌ FAILED (Content: {content})")

def test_streaming(client: Vidai, config: ProviderConfig):
    """Test streaming completion."""
    if not config.supports_streaming:
        print("  [Skipped] Streaming (Not supported)")
        return

    print(f"  [Running] Streaming ({config.model})...", end="", flush=True)
    stream = client.chat.completions.create(
        model=config.model,
        messages=[{"role": "user", "content": "Count to 5."}],
        stream=True
    )
    
    collected_content = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            collected_content += chunk.choices[0].delta.content
            
    if len(collected_content) > 0:
        print(" ✅ PASSED")
    else:
        print(" ❌ FAILED (No content received)")

def test_tool_use(client: Vidai, config: ProviderConfig):
    """Test tool calling capabilities."""
    if not config.supports_tools:
        print("  [Skipped] Tool Use (Not supported)")
        return

    print(f"  [Running] Tool Use ({config.model})...", end="", flush=True)
    
    tools = [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    }]
    
    response = client.chat.completions.create(
        model=config.model,
        messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
        tools=tools,
        tool_choice="auto"
    )
    
    msg = response.choices[0].message
    if msg.tool_calls and msg.tool_calls[0].function.name == "get_weather":
        print(" ✅ PASSED")
    else:
        print(f" ❌ FAILED (No tool call or wrong tool: {msg.content})")

def test_structured_output(client: Vidai, config: ProviderConfig):
    """Test structured output extraction."""
    if not config.supports_structured_output:
        print("  [Skipped] Structured Output (Not supported)")
        return

    print(f"  [Running] Structured Output ({config.model})...", end="", flush=True)
    
    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "user", "content": "Create a user profile for Alice, 30, Engineer, likes hiking."}
        ],
        response_format=UserProfile
    )
    
    if response.choices[0].parsed and response.choices[0].parsed.name == "Alice":
        print(" ✅ PASSED")
    else:
        print(f" ❌ FAILED (Parse error or wrong data: {response.choices[0].parse_error})")

def test_thinking_model(client: Vidai, config: ProviderConfig):
    """Test thinking/reasoning model capabilities."""
    if not config.supports_reasoning:
        return # Skip silently if not marked as supported

    print(f"  [Running] Thinking Model ({config.model})...", end="", flush=True)
    # This is highly provider specific, so we just check if it crashes or returns content
    try:
        response = client.chat.completions.create(
            model=config.model,
            messages=[{"role": "user", "content": "Solve 2x + 5 = 15."}]
        )
        if response.choices[0].message.content:
             print(" ✅ PASSED")
        else:
             print(" ❌ FAILED (No content)")
    except Exception as e:
        print(f" ❌ FAILED (Exception: {e})")

def test_large_context(client: Vidai, config: ProviderConfig):
    """Test handling of large context (approx 4k tokens)."""
    print(f"  [Running] Large Context ({config.model})...", end="", flush=True)
    
    # Create a long text (~4000 tokens worth of text)
    # Using a simple repetitive pattern to ensure compressibility but high token count
    base_text = "The quick brown fox jumps over the lazy dog. "
    large_input = base_text * 400
    
    try:
        response = client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize this text in 10 words: {large_input}"}
            ]
        )
        content = response.choices[0].message.content
        if content and len(content) > 0:
             print(" ✅ PASSED")
        else:
             print(" ❌ FAILED (No content)")
    except Exception as e:
        print(f" ❌ FAILED (Exception: {e})")

# --- Main Runner ---

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run Vidai Real-World Compatibility Suite")
    parser.add_argument("--provider", type=str, help="Run specific provider (case-insensitive sub-match)", default=None)
    parser.add_argument("--list", action="store_true", help="List available providers and exit")
    args = parser.parse_args()

    print("===========================================")
    print("   Vidai Real-World Compatibility Suite")
    print("=" * 43)
    
    all_providers = discover_providers()
    
    if args.list:
        print("Available Providers:")
        for p in all_providers:
            print(f" - {p.name}")
        return

    # Filter providers
    if args.provider:
        providers = [p for p in all_providers if args.provider.lower() in p.name.lower()]
        if not providers:
            print(f"No providers found matching '{args.provider}'")
            return
    else:
        providers = all_providers

    if not providers:
        print("No providers configured in environment or matching filter.")
        print("Please set OPENAI_API_KEY, GROQ_API_KEY, etc.")
        sys.exit(0)

    print(f"Discovered {len(providers)} providers: {', '.join(p.name for p in providers)}")
    print("")
    
    for p in providers:
        print(f"Testing Provider: {p.name}")
        print("-" * 30)
        
        try:
            client_config = VidaiConfig(track_request_transformation=True)
            if p.vidai_config_overrides:
                client_config = client_config.copy(**p.vidai_config_overrides)

            client = Vidai(
                api_key=p.api_key,
                base_url=p.base_url,
                config=client_config
            )
            
            test_basic_chat(client, p)
            test_streaming(client, p)
            test_tool_use(client, p)
            test_structured_output(client, p)
            test_thinking_model(client, p)
            test_large_context(client, p)
            
        except Exception as e:
            print(f"CRITICAL ERROR initializing {p.name}: {e}")
            
        print("\n")

if __name__ == "__main__":
    main()

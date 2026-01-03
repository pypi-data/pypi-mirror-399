
import os
import sys
import base64
import json
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from vidai import Vidai
from vidai.config import VidaiConfig

# Setup Color Logging
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_pass(msg):
    print(f"{Colors.OKGREEN}[PASS] {msg}{Colors.ENDC}")

def print_fail(msg):
    print(f"{Colors.FAIL}[FAIL] {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKBLUE}[INFO] {msg}{Colors.ENDC}")

# --- Models for Structured Output ---
class WeatherResponse(BaseModel):
    location: str
    temperature: float
    conditions: str
    unit: str = Field(description="Unit of temperature, e.g., 'celsius' or 'fahrenheit'")

# --- Verification Functions ---

def verify_gemini_json(client: Vidai, model: str):
    print_info(f"Testing Gemini JSON Mode with model: {model}")
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "What is the weather in Tokyo? Give me a realistic hypothetical JSON response."}
            ],
            response_format=WeatherResponse
        )
        response = completion.choices[0].message.parsed
        if isinstance(response, WeatherResponse):
            print_pass(f"Gemini JSON: Got valid WeatherResponse: {response}")
        else:
            print_fail(f"Gemini JSON: Response was not WeatherResponse model. Got: {type(response)}")
    except Exception as e:
        print_fail(f"Gemini JSON Error: {e}")

def verify_gemini_vision(client: Vidai, model: str):
    print_info(f"Testing Gemini Vision with model: {model}")
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is in this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                            },
                        },
                    ],
                }
            ],
        )
        content = completion.choices[0].message.content
        if content and len(content) > 10:
            print_pass(f"Gemini Vision: Got description: {content[:50]}...")
        else:
            print_fail("Gemini Vision: Got empty or too short response")
    except Exception as e:
        print_fail(f"Gemini Vision Error: {e}")

def verify_anthropic_vision(client: Vidai, model: str):
    print_info(f"Testing Anthropic Vision with model: {model}")
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is in this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                            },
                        },
                    ],
                }
            ],
        )
        content = completion.choices[0].message.content
        if content and len(content) > 10:
            print_pass(f"Anthropic Vision: Got description: {content[:50]}...")
        else:
            print_fail("Anthropic Vision: Got empty or too short response")
    except Exception as e:
        print_fail(f"Anthropic Vision Error: {e}")

def verify_gemini_document(client: Vidai, model: str):
    print_info(f"Testing Gemini Document (PDF) with model: {model}")
    # Small dummy PDF
    pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What does this document say?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": pdf_url,
                            },
                        },
                    ],
                }
            ],
        )
        content = completion.choices[0].message.content
        if content and "Dummy" in content:
            print_pass(f"Gemini Document: Got expected text: {content[:50]}...")
        else:
            print_fail(f"Gemini Document: Response didn't match expected. Got: {content}")
    except Exception as e:
        print_fail(f"Gemini Document Error: {e}")

def verify_anthropic_document(client: Vidai, model: str):
    print_info(f"Testing Anthropic Document (PDF) with model: {model}")
    pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What does this document say?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": pdf_url,
                            },
                        },
                    ],
                }
            ],
            extra_headers={"anthropic-beta": "pdfs-2024-09-25"} # Required for PDFs
        )
        content = completion.choices[0].message.content
        if content and "Dummy" in content:
            print_pass(f"Anthropic Document: Got expected text: {content[:50]}...")
        else:
            print_fail(f"Anthropic Document: Response didn't match expected. Got: {content}")
    except Exception as e:
        print_fail(f"Anthropic Document Error: {e}")

def load_env():
    """Simple .env loader"""
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Removing comments if inline
                    if ' #' in value:
                        value = value.split(' #')[0]
                    os.environ[key.strip()] = value.strip()
    except FileNotFoundError:
        print_fail(".env file not found")

def main():
    load_env()
    
    # Load settings from environment
    gemini_key = os.getenv("GEMINI_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini_base = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")

    print_info("--- Starting Verification ---")

    # 1. Test Gemini
    if gemini_key:
        print_info("Initializing Gemini Client...")
        gemini_config = VidaiConfig(
            provider="gemini",
            default_base_url=gemini_base
        )
        gemini_client = Vidai(
            api_key=gemini_key,
            base_url=gemini_base,
            config=gemini_config
        )
        
        verify_gemini_json(gemini_client, gemini_model)
        verify_gemini_vision(gemini_client, gemini_model)
        verify_gemini_document(gemini_client, gemini_model)
    else:
        print_fail("Skipping Gemini tests: GEMINI_API_KEY not found")

    print("\n" + "="*30 + "\n")

    # 2. Test Anthropic
    if anthropic_key:
        print_info("Initializing Anthropic Client...")
        anthropic_config = VidaiConfig(
            provider="anthropic"
        )
        anthropic_client = Vidai(
            api_key=anthropic_key,
            config=anthropic_config
        )
        
        verify_anthropic_vision(anthropic_client, anthropic_model)
        verify_anthropic_document(anthropic_client, anthropic_model)
    else:
        print_fail("Skipping Anthropic tests: ANTHROPIC_API_KEY not found")

if __name__ == "__main__":
    main()

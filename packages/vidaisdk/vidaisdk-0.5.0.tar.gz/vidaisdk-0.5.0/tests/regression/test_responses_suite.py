"""
Vidai Responses API Regression Suite
=========================================

Runs the same test cases as `regression_suite.py` but using `client.responses.create`.
Validates that the Responses API (and its polyfills) produce correct structured data.
"""

import os
import sys
import argparse
import time
from typing import Any, List, Optional
from dataclasses import dataclass

from pydantic import BaseModel
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from vidai import Vidai, VidaiConfig
from tests.regression.test_provider_discovery import discover_providers
# Reuse test cases directly
from tests.regression.test_completions_suite import create_test_cases, RegressionTestCase

# --- Adapter for Compatibility ---

@dataclass
class MockMessage:
    content: str
    parsed: Optional[BaseModel] = None
    tool_calls: Optional[List[Any]] = None

@dataclass
class MockChoice:
    message: MockMessage

@dataclass
class MockCompletion:
    choices: List[MockChoice]

class ResponseToCompletionAdapter:
    """
    Adapts an EnhancedResponse to look like a ChatCompletion 
    for reuse of existing regression validators.
    """
    def __init__(self, response: Any, response_format: Optional[type[BaseModel]] = None):
        self.response = response
        self.response_format = response_format
        
    @property
    def choices(self) -> List[MockChoice]:
        # Extract first item from output
        if not self.response.output:
            return []
            
        item = self.response.output[0]
        # item is ResponseOutputMessage (Object)
        
        # content is List[ResponseOutputText]
        text_content = ""
        if item.content and hasattr(item.content[0], "text"):
            text_content = item.content[0].text
        elif item.content:
            text_content = str(item.content) # Fallback
            
        # Parse if we have a format
        parsed_obj = None
        if self.response_format and text_content:
            try:
                # Manual parse to match auto-parse behavior of completions
                parsed_obj = self.response_format.model_validate_json(text_content)
            except:
                pass
                
        # Handle Tool Calls
        # Responses API might return tool calls differently or inside content
        # For now, if we see tool calls in the raw dict (if it leaked) or special content type
        tool_calls = None
        # Note: Current Refactor logic maps output to Message/Text types. 
        # For tool polyfill, the 'content' string IS the JSON for the tool call or the structured output.
        # So we treat structured output validation as primary.
        # Real tool calls (FunctionDef) might be missing from this simple mapping unless we mapped them.
        # But `verify_real_responses.py` showed we get JSON strings for extracted data.
        
        return [MockChoice(message=MockMessage(
            content=text_content,
            parsed=parsed_obj,
            tool_calls=tool_calls 
        ))]

# --- Runner ---

def run_suite():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Vidai Responses API Regression")
    parser.add_argument("--provider", type=str, default=None)
    args = parser.parse_args()
    
    print("\nStarting RESPONSES API Regression Suite...")
    providers = discover_providers()
    if args.provider:
        providers = [p for p in providers if args.provider.lower() in p.name.lower()]
        
    test_cases = create_test_cases()
    results = {}

    for p in providers:
        print(f"\n>> Testing Provider: {p.name} (Responses API)")
        print("=" * 60)
        
        try:
            client = Vidai(
                api_key=p.api_key, 
                base_url=p.base_url,
                config=VidaiConfig(track_request_transformation=True).copy(**(p.vidai_config_overrides or {}))
            )
        except Exception as e:
            print(f"Skipping {p.name}: {e}")
            continue

        results[p.name] = {"passed": 0, "failed": 0, "errors": []}

        for case in test_cases:
            # Skip Tool Call specific tests if Adapter logic is incomplete for native tools
            # We focus on Structured Output primarily for Responses API
            if case.tools and not case.response_format:
                # Skipping raw tool call tests for now unless we implement full tool adaptation
                continue

            print(f"[{case.id}] {case.name:<30} ... ", end="", flush=True)
            
            try:
                start_time = time.time()
                
                # EXECUTE RESPONSES API
                resp = client.responses.create(
                    model=p.model,
                    messages=[{"role": "user", "content": case.prompt}],
                    response_format=case.response_format 
                    # Note: We don't pass 'tools' unless it's a tool test, which we skipped above
                )
                
                duration = time.time() - start_time
                
                # ADAPT TO COMPLETION API FORMAT
                adapter = ResponseToCompletionAdapter(resp, case.response_format)
                
                # VALIDATE
                if case.validate(adapter):
                    print(f"✅ PASS ({duration:.2f}s)")
                    results[p.name]["passed"] += 1
                else:
                    print(f"❌ FAIL")
                    results[p.name]["failed"] += 1
                    results[p.name]["errors"].append(f"{case.id}: Validation Failed")

            except Exception as e:
                print(f"❌ ERROR: {e}")
                results[p.name]["failed"] += 1
                results[p.name]["errors"].append(f"{case.id}: {str(e)}")
                if "401" in str(e) or "404" in str(e):
                     break

    print("\nSUMMARY")
    for p, r in results.items():
        print(f"{p}: {r['passed']} Pass, {r['failed']} Fail")

if __name__ == "__main__":
    run_suite()

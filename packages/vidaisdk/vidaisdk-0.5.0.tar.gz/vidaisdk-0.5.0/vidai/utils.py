"""Utility functions for Vidai."""

import base64
import httpx
import json
import logging
import re
import sys
import time
from typing import Any, Dict, List, Optional, Tuple, Type

import json_repair
from pydantic import BaseModel, ValidationError

from .config import VidaiConfig
from .exceptions import JSONRepairError, ValidationError as VidaiValidationError
from .models import JsonRepairInfo

def encode_file(file_input: str) -> str:
    """Encode file (image/pdf) to base64.
    
    Args:
        file_input: URL or local path to file.
        
    Returns:
        Base64 encoded string.
    """
    if file_input.startswith(('http://', 'https://')):
        headers = {'User-Agent': 'Vidai/1.0'}
        response = httpx.get(file_input, headers=headers)
        response.raise_for_status()
        return base64.b64encode(response.content).decode('utf-8')
    
    try:
        with open(file_input, "rb") as file_obj:
            return base64.b64encode(file_obj.read()).decode('utf-8')
    except Exception:
        # Assume it's already base64 or fail
        return file_input

# Alias for backward compatibility
encode_image = encode_file

def get_media_type(file_input: str) -> str:
    """Get media type from URL/path.
    
    Raises:
        ValueError: If file type is not supported.
    """
    ext = file_input.lower()
    if ext.endswith('.png'):
        return "image/png"
    elif ext.endswith(('.jpg', '.jpeg')):
        return "image/jpeg"
    elif ext.endswith('.webp'):
        return "image/webp"
    elif ext.endswith('.gif'):
        return "image/gif"
    elif ext.endswith('.pdf'):
        return "application/pdf"
    
    # Fail fast for known unsupported types
    if ext.endswith(('.xls', '.xlsx', '.csv', '.doc', '.docx')):
        raise ValueError(f"Unsupported file format for '{file_input}'. Only Images and PDFs are currently supported.")
        
    # Default failure for safety
    raise ValueError(f"Could not determine media type for '{file_input}'. Supported formats: png, jpg, jpeg, webp, gif, pdf.")


# Setup logger
logger = logging.getLogger("vidai")
logger.setLevel(logging.WARNING)

def setup_logging(config: VidaiConfig) -> None:
    """Setup logging for Vidai."""
    # Only add handler if not already present
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(
            "[Vidai] %(levelname)s: %(message)s"
        ))
        logger.addHandler(handler)
    
    logger.setLevel(getattr(logging, config.log_level))


def extract_json_from_response(response: Dict[str, Any]) -> Optional[str]:
    """Extract JSON content from various provider response formats.
    
    Args:
        response: Raw response from provider
        
    Returns:
        JSON string if found, None otherwise
    """
    # OpenAI format
    if "choices" in response:
        choice = response["choices"][0]
        if "message" in choice:
            content = choice["message"].get("content")
            if content:
                return content
            
            # Check for tool_calls in OpenAI format (used by Gemini Polyfill)
            tool_calls = choice["message"].get("tool_calls")
            if tool_calls and isinstance(tool_calls, list):
                # Assume first tool call contains the structured output
                args = tool_calls[0].get("function", {}).get("arguments")
                if args:
                    return args
    
    # Anthropic format
    if "content" in response:
        content_list = response["content"]
        if isinstance(content_list, list):
            for item in content_list:
                if item.get("type") == "text":
                    return item.get("text")
                elif item.get("type") == "tool_use":
                    content = item.get("input")
                    if isinstance(content, dict):
                        return json.dumps(content)
                    return content
    
    # Gemini format
    if "candidates" in response:
        candidates = response["candidates"]
        if candidates:
            candidate = candidates[0]
            if "content" in candidate:
                content = candidate["content"]
                if "parts" in content:
                    parts = content["parts"]
                    if parts:
                        return parts[0].get("text")
    
    # Direct content
    if "content" in response and isinstance(response["content"], str):
        return response["content"]
    
    return None


def is_valid_json(json_str: str) -> bool:
    """Check if a string is valid JSON.
    
    Args:
        json_str: String to check
        
    Returns:
        True if valid JSON, False otherwise
    """
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def detect_repair_operations(original: str, repaired: str) -> List[str]:
    """Detect what operations were performed during JSON repair.
    
    Args:
        original: Original JSON string
        repaired: Repaired JSON string
        
    Returns:
        List of repair operation descriptions
    """
    operations = []
    
    # Check for single quote fixes
    if original.count("'") != repaired.count("'"):
        operations.append("fixed_single_quotes")
    
    # Check for trailing comma fixes
    # Check for trailing commas before closing braces or brackets using regex
    trailing_comma_pattern = r",\s*[}\]]"
    if re.search(trailing_comma_pattern, original) and not re.search(trailing_comma_pattern, repaired):
        operations.append("fixed_trailing_comma")
    elif original.rstrip().endswith(',') and not repaired.rstrip().endswith(','):
        # Also check end of string trailing comma
        operations.append("fixed_trailing_comma")
    
    # Check for bracket fixes
    if original.count("{") != repaired.count("{") or original.count("}") != repaired.count("}"):
        operations.append("fixed_brackets")
    
    # Check for square bracket fixes
    if original.count("[") != repaired.count("[") or original.count("]") != repaired.count("]"):
        operations.append("fixed_brackets")
    
    # Check for quote fixes around keys/values
    original_quotes = original.count('"')
    repaired_quotes = repaired.count('"')
    if repaired_quotes > original_quotes:
        operations.append("added_missing_quotes")
    
    # Check for escape character fixes
    if '\\' in repaired and '\\' not in original:
        operations.append("fixed_escape_characters")
    
    return operations


def repair_json_string(
    json_str: str,
    config: VidaiConfig
) -> tuple[str, Optional[JsonRepairInfo]]:
    """Repair a JSON string based on configuration.
    
    Args:
        json_str: JSON string to repair
        config: Configuration settings
        
    Returns:
        Tuple of (repaired_json, repair_info)
        
    Raises:
        JSONRepairError: If repair fails and is required
    """
    if is_valid_json(json_str):
        return json_str, JsonRepairInfo(
            was_repaired=False,
            repair_time_ms=0.0,
            repair_operations=[]
        )
    
    # Check if repair should be attempted
    should_repair = (
        config.json_repair_mode == "always" or
        (config.json_repair_mode == "auto" and not is_valid_json(json_str))
    )
    
    if not should_repair:
        if config.json_repair_feedback:
            logger.warning("JSON repair disabled but invalid JSON detected")
        return json_str, JsonRepairInfo(
            was_repaired=False,
            repair_time_ms=0.0,
            repair_operations=[],
            original_error="Invalid JSON but repair disabled"
        )
    
    # Attempt repair
    try:
        start_time = time.perf_counter()
        
        repaired = json_repair.repair_json(json_str)
        
        repair_time = (time.perf_counter() - start_time) * 1000
        operations = detect_repair_operations(json_str, repaired)
        
        if config.json_repair_feedback:
            logger.info(f"JSON repaired in {repair_time:.2f}ms: {', '.join(operations)}")
        
        return repaired, JsonRepairInfo(
            was_repaired=True,
            repair_time_ms=repair_time,
            repair_operations=operations
        )
        
    except Exception as e:
        error_msg = f"JSON repair failed: {e}"
        logger.error(error_msg)
        
        if config.strict_json_parsing:
            raise JSONRepairError(
                error_msg,
                original_error=e
            )
        
        return json_str, JsonRepairInfo(
            was_repaired=False,
            repair_time_ms=0.0,
            repair_operations=[],
            original_error=error_msg
        )


def validate_pydantic_model(
    json_str: str,
    model_class: Type[BaseModel],
    config: VidaiConfig
) -> tuple[Optional[BaseModel], Optional[Exception]]:
    """Validate JSON string against a Pydantic model.
    
    Args:
        json_str: JSON string to validate
        model_class: Pydantic model class
        config: Configuration settings
        
    Returns:
        Tuple of (parsed_model, validation_error)
    """
    try:
        parsed = model_class.model_validate_json(json_str)
        return parsed, None
    except ValidationError as e:
        if config.strict_schema_validation:
            raise VidaiValidationError(
                f"Schema validation failed: {e}",
                pydantic_error=e
            )
        
        if config.json_repair_feedback:
            logger.warning(f"Schema validation failed: {e}")
        
        return None, e
    except Exception as e:
        if config.strict_schema_validation:
            raise VidaiValidationError(
                f"Unexpected validation error: {e}",
                pydantic_error=e
            )
        
        return None, e


def merge_configs(
    base_config: VidaiConfig,
    **overrides
) -> VidaiConfig:
    """Merge base configuration with overrides.
    
    Args:
        base_config: Base configuration
        **overrides: Configuration overrides
        
    Returns:
        Merged configuration
    """
    return base_config.copy(**overrides)


def safe_get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Safely get nested value from dictionary using dot notation.
    
    Args:
        data: Dictionary to get value from
        path: Dot-separated path (e.g., "choices.0.message.content")
        default: Default value if path not found
        
    Returns:
        Value at path or default
    """
    keys = path.split('.')
    current = data
    
    try:
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                current = current[int(key)]
            else:
                return default
        return current
    except (KeyError, IndexError, TypeError):
        return default
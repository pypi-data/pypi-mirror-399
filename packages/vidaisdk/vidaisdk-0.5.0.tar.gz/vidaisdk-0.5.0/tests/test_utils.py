"""Tests for utility functions."""

import pytest
from unittest.mock import patch, Mock

from vidai.config import VidaiConfig
from vidai.utils import (
    extract_json_from_response,
    is_valid_json,
    detect_repair_operations,
    repair_json_string,
    validate_pydantic_model,
    safe_get_nested_value,
    merge_configs,
    setup_logging,
    logger,
    encode_file,
    get_media_type
)
from vidai.exceptions import JSONRepairError, ValidationError as WizzValidationError
from tests.conftest import TestUser

class TestMediaUtils:
    """Test media utility functions."""
    
    def test_get_media_type_valid(self):
        """Test valid media type detection."""
        assert get_media_type("image.png") == "image/png"
        assert get_media_type("image.jpg") == "image/jpeg"
        assert get_media_type("image.jpeg") == "image/jpeg"
        assert get_media_type("image.webp") == "image/webp"
        assert get_media_type("image.gif") == "image/gif"
        assert get_media_type("doc.pdf") == "application/pdf"
        # case insensitive
        assert get_media_type("IMAGE.PNG") == "image/png"

    def test_get_media_type_invalid(self):
        """Test invalid media type detection."""
        with pytest.raises(ValueError, match="Unsupported file format"):
            get_media_type("sheet.xlsx")
            
        with pytest.raises(ValueError, match="Could not determine media type"):
            get_media_type("unknown_file")

    @patch("vidai.utils.httpx.get")
    def test_encode_file_url(self, mock_get):
        """Test encoding file from URL."""
        mock_response = Mock()
        mock_response.content = b"fake_content"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        encoded = encode_file("http://example.com/image.png")
        
        assert encoded == "ZmFrZV9jb250ZW50" # base64 for 'fake_content' matches
        
        # Le's verify call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == "http://example.com/image.png"
        assert kwargs["headers"]["User-Agent"] == "Vidai/1.0"

    def test_encode_file_local(self):
        """Test encoding local file."""
        from unittest.mock import mock_open
        with patch("builtins.open", mock_open(read_data=b"local_content")):
            encoded = encode_file("/path/to/local.png")
            # b"local_content" -> base64
            import base64
            expected = base64.b64encode(b"local_content").decode("utf-8")
            assert encoded == expected

    def test_encode_file_fallback(self):
        """Test fallback when file open fails (assume already base64 or raw)."""
        # If open fails, it returns input
        with patch("builtins.open", side_effect=FileNotFoundError):
            assert encode_file("not_a_file_path") == "not_a_file_path"


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_extract_json_openai_format(self):
        """Test extracting JSON from OpenAI format."""
        response = {
            "choices": [
                {
                    "message": {
                        "content": '{"name": "John", "age": 30}'
                    }
                }
            ]
        }
        
        json_content = extract_json_from_response(response)
        assert json_content == '{"name": "John", "age": 30}'
    
    def test_extract_json_anthropic_format(self):
        """Test extracting JSON from Anthropic format."""
        response = {
            "content": [
                {"type": "text", "text": '{"name": "John", "age": 30}'}
            ]
        }
        
        json_content = extract_json_from_response(response)
        assert json_content == '{"name": "John", "age": 30}'
    
    def test_extract_json_anthropic_tool_use(self):
        """Test extracting JSON from Anthropic tool_use format."""
        response = {
            "content": [
                {"type": "tool_use", "input": '{"name": "John", "age": 30}'}
            ]
        }
        
        json_content = extract_json_from_response(response)
        assert json_content == '{"name": "John", "age": 30}'
    
    def test_extract_json_gemini_format(self):
        """Test extracting JSON from Gemini format."""
        response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": '{"name": "John", "age": 30}'}
                        ]
                    }
                }
            ]
        }
        
        json_content = extract_json_from_response(response)
        assert json_content == '{"name": "John", "age": 30}'
    
    def test_extract_json_direct_content(self):
        """Test extracting JSON from direct content."""
        response = {
            "content": '{"name": "John", "age": 30}'
        }
        
        json_content = extract_json_from_response(response)
        assert json_content == '{"name": "John", "age": 30}'
    
    def test_extract_json_not_found(self):
        """Test extracting JSON when not found."""
        response = {"other": "data"}
        
        json_content = extract_json_from_response(response)
        assert json_content is None
    
    def test_is_valid_json_true(self):
        """Test valid JSON detection."""
        assert is_valid_json('{"name": "John", "age": 30}') is True
        assert is_valid_json('[]') is True
        assert is_valid_json('null') is True
        assert is_valid_json('"string"') is True
        assert is_valid_json('123') is True
    
    def test_is_valid_json_false(self):
        """Test invalid JSON detection."""
        assert is_valid_json('{"name": "John", "age": 30,}') is False  # trailing comma
        assert is_valid_json("{'name': 'John', 'age': 30}") is False  # single quotes
        assert is_valid_json('{"name": "John", "age": 30') is False  # missing brace
        assert is_valid_json('not json') is False
        assert is_valid_json('') is False
        assert is_valid_json(None) is False
    
    def test_detect_repair_operations_trailing_comma(self):
        """Test detecting trailing comma repair."""
        original = '{"name": "John", "age": 30,}'
        repaired = '{"name": "John", "age": 30}'
        
        operations = detect_repair_operations(original, repaired)
        assert "fixed_trailing_comma" in operations
    
    def test_detect_repair_operations_single_quotes(self):
        """Test detecting single quote repair."""
        original = "{'name': 'John', 'age': 30}"
        repaired = '{"name": "John", "age": 30}'
        
        operations = detect_repair_operations(original, repaired)
        assert "fixed_single_quotes" in operations
    
    def test_detect_repair_operations_extended(self):
        """Test extended repair operation detection."""
        # End of string trailing comma
        assert "fixed_trailing_comma" in detect_repair_operations('{"a": 1,}', '{"a": 1}')
        
        # Square brackets
        assert "fixed_brackets" in detect_repair_operations('[1, 2', '[1, 2]')
        assert "fixed_brackets" in detect_repair_operations('1, 2]', '[1, 2]')


class TestSafeGetNestedValue:
    """Test safe_get_nested_value function."""
    
    def test_get_existing_value(self):
        """Test getting existing nested value."""
        data = {"a": {"b": {"c": 1}}}
        assert safe_get_nested_value(data, "a.b.c") == 1
    
    def test_get_list_item(self):
        """Test getting value from list."""
        data = {"a": [{"b": 1}]}
        assert safe_get_nested_value(data, "a.0.b") == 1
    
    def test_get_missing_value(self):
        """Test getting missing value returns default."""
        data = {"a": 1}
        assert safe_get_nested_value(data, "b", default="default") == "default"
        assert safe_get_nested_value(data, "a.b", default="default") == "default"
    
    def test_invalid_path_types(self):
        """Test handling of invalid types in path traversal."""
        data = {"a": 1}
        # "a" is int, cannot traverse into it
        assert safe_get_nested_value(data, "a.b", default="default") == "default"


class TestMergeConfigs:
    """Test merge_configs function."""
    
    def test_merge_configs(self):
        """Test merging configurations."""
        base = VidaiConfig(json_repair_mode="auto", strict_json_parsing=False)
        merged = merge_configs(base, json_repair_mode="always", strict_json_parsing=True)
        
        assert merged.json_repair_mode == "always"
        assert merged.strict_json_parsing is True
        # Original should be unchanged
        assert base.json_repair_mode == "auto"
    def test_detect_repair_operations_missing_quotes(self):
        """Test detecting missing quotes repair."""
        original = '{name: "John", "age": 30}'
        repaired = '{"name": "John", "age": 30}'
        
        operations = detect_repair_operations(original, repaired)
        assert "added_missing_quotes" in operations
    
    def test_detect_repair_operations_end_comma(self):
        """Test detecting end of string trailing comma."""
        # Use case where regex (comma before brace) doesn't catch it
        # e.g. unclosed object with trailing comma
        original = '{"a": 1,'
        repaired = '{"a": 1}'
        assert "fixed_trailing_comma" in detect_repair_operations(original, repaired)

    def test_detect_repair_operations_escape_characters(self):
        """Test detecting escape character repair."""
        original = '{"name": "John\nDoe"}'
        repaired = '{"name": "John\\nDoe"}'
        
        operations = detect_repair_operations(original, repaired)
        assert "fixed_escape_characters" in operations
    
    def test_detect_repair_operations_no_changes(self):
        """Test detecting no repair operations."""
        original = '{"name": "John", "age": 30}'
        repaired = '{"name": "John", "age": 30}'
        
        operations = detect_repair_operations(original, repaired)
        assert operations == []
    
    @patch('vidai.utils.json_repair.repair_json')
    def test_repair_json_string_generic_exception(self, mock_repair, test_config):
        """Test generic exception during repair."""
        mock_repair.side_effect = Exception("Surprise error")
        
        # Should return original string and error info if not strict
        json_str = '{"invalid": }'
        repaired, info = repair_json_string(json_str, test_config)
        
        assert repaired == json_str
        assert info.was_repaired is False
        assert "JSON repair failed" in info.original_error
        
        # Should raise if strict
        strict_config = test_config.copy(strict_json_parsing=True)
        with pytest.raises(JSONRepairError):
            repair_json_string(json_str, strict_config)
    """Test repairing valid JSON string."""
    @patch('vidai.utils.json_repair.repair_json')
    def test_repair_json_string_valid(self, mock_repair, test_config):
        """Test repairing valid JSON string."""
        mock_repair.return_value = '{"name": "John", "age": 30}'
        
        json_str = '{"name": "John", "age": 30}'
        repaired, repair_info = repair_json_string(json_str, test_config)
        
        assert repaired == json_str
        assert repair_info.was_repaired is False
        assert repair_info.repair_time_ms == 0.0
        assert repair_info.repair_operations == []
        # Should not call repair for valid JSON
        mock_repair.assert_not_called()
    
    @patch('vidai.utils.json_repair.repair_json')
    @patch('vidai.utils.time.perf_counter')
    def test_repair_json_string_invalid_auto(self, mock_time, mock_repair, test_config):
        """Test repairing invalid JSON string in auto mode."""
        mock_time.side_effect = [0.0, 0.001]  # 1ms timing
        mock_repair.return_value = '{"name": "John", "age": 30}'
        
        json_str = '{"name": "John", "age": 30,}'
        repaired, repair_info = repair_json_string(json_str, test_config)
        
        assert repaired == '{"name": "John", "age": 30}'
        assert repair_info.was_repaired is True
        assert repair_info.repair_time_ms == 1.0
        mock_repair.assert_called_once_with(json_str)
    
    @patch('vidai.utils.json_repair.repair_json')
    def test_repair_json_string_disabled(self, mock_repair):
        """Test repairing JSON string when disabled."""
        config = VidaiConfig(json_repair_mode="never")
        
        json_str = '{"name": "John", "age": 30,}'
        repaired, repair_info = repair_json_string(json_str, config)
        
        assert repaired == json_str
        assert repair_info.was_repaired is False
        assert "repair disabled" in repair_info.original_error
        mock_repair.assert_not_called()
    
    @patch('vidai.utils.json_repair.repair_json')
    def test_repair_json_string_always(self, mock_repair, test_config):
        """Test repairing JSON string in always mode."""
        config = test_config.copy(json_repair_mode="always")
        
        # Even in always mode, valid JSON is skipped for optimization
        # unless we forcibly change implementation. Current implementation skips valid JSON.
        json_str = '{"name": "John", "age": 30}'
        repaired, repair_info = repair_json_string(json_str, config)
        
        assert repaired == json_str
        assert repair_info.was_repaired is False
        mock_repair.assert_not_called()
    
    @patch('vidai.utils.logger')
    def test_setup_logging(self, mock_logger, test_config):
        """Test logging setup."""
        setup_logging(test_config)
        
        mock_logger.setLevel.assert_called_once()
    
    @patch('vidai.utils.logger')
    def test_setup_logging_already_configured(self, mock_logger, test_config):
        """Test logging setup when already configured."""
        mock_logger.handlers = [Mock()]  # Already has handler
        
        setup_logging(test_config)
        
        # Should not add another handler
        assert len(mock_logger.addHandler.call_args_list) == 0
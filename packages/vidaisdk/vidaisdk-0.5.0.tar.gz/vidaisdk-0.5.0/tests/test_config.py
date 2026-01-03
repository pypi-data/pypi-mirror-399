"""Tests for Vidai configuration."""

import os
import pytest
from unittest.mock import patch

from vidai.config import VidaiConfig
from vidai.exceptions import ConfigurationError


class TestVidaiConfig:
    """Test VidaiConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = VidaiConfig()
        
        assert config.json_repair_mode == "auto"
        assert config.json_repair_feedback is True
        assert config.strict_json_parsing is False
        assert config.strict_schema_validation is False
        assert config.track_request_transformation is True
        assert config.track_json_repair is True
        assert config.log_level == "WARNING"
        assert config.default_base_url is None
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = VidaiConfig(
            json_repair_mode="always",
            json_repair_feedback=False,
            strict_json_parsing=True,
            strict_schema_validation=True,
            track_request_transformation=False,
            track_json_repair=False,
            log_level="DEBUG",
            default_base_url="https://test.example.com/v1"
        )
        
        assert config.json_repair_mode == "always"
        assert config.json_repair_feedback is False
        assert config.strict_json_parsing is True
        assert config.strict_schema_validation is True
        assert config.track_request_transformation is False
        assert config.track_json_repair is False
        assert config.log_level == "DEBUG"
        assert config.default_base_url == "https://test.example.com/v1"
    
    def test_invalid_json_repair_mode(self):
        """Test invalid JSON repair mode."""
        with pytest.raises(ValueError, match="json_repair_mode must be one of"):
            VidaiConfig(json_repair_mode="invalid")
    
    def test_invalid_log_level(self):
        """Test invalid log level."""
        with pytest.raises(ValueError, match="log_level must be one of"):
            VidaiConfig(log_level="INVALID")
    
    @patch.dict(os.environ, {
        "VIDAI_JSON_REPAIR": "never",
        "VIDAI_JSON_FEEDBACK": "false",
        "VIDAI_STRICT_JSON": "true",
        "VIDAI_STRICT_SCHEMA": "true",
        "VIDAI_TRACK_TRANSFORM": "false",
        "VIDAI_TRACK_REPAIR": "false",
        "VIDAI_LOG_LEVEL": "ERROR",
        "VIDAI_BASE_URL": "https://env.example.com/v1"
    })
    def test_from_env(self):
        """Test configuration from environment variables."""
        config = VidaiConfig.from_env()
        
        assert config.json_repair_mode == "never"
        assert config.json_repair_feedback is False
        assert config.strict_json_parsing is True
        assert config.strict_schema_validation is True
        assert config.track_request_transformation is False
        assert config.track_json_repair is False
        assert config.log_level == "ERROR"
        assert config.default_base_url == "https://env.example.com/v1"
    
    def test_from_env_defaults(self):
        """Test configuration from environment with defaults."""
        # Clear any existing env vars
        env_vars = [
            "VIDAI_JSON_REPAIR", "VIDAI_JSON_FEEDBACK", "VIDAI_STRICT_JSON",
            "VIDAI_STRICT_SCHEMA", "VIDAI_TRACK_TRANSFORM", "VIDAI_TRACK_REPAIR",
            "VIDAI_LOG_LEVEL", "VIDAI_BASE_URL"
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
        
        config = VidaiConfig.from_env()
        
        assert config.json_repair_mode == "auto"
        assert config.json_repair_feedback is True
        assert config.strict_json_parsing is False
        assert config.strict_schema_validation is False
        assert config.track_request_transformation is True
        assert config.track_json_repair is True
        assert config.log_level == "WARNING"
        assert config.default_base_url is None
    
    def test_copy_with_overrides(self):
        """Test copying configuration with overrides."""
        original = VidaiConfig(
            json_repair_mode="auto",
            json_repair_feedback=True,
            strict_json_parsing=False
        )
        
        # Copy with some overrides
        copied = original.copy(
            json_repair_mode="never",
            strict_json_parsing=True
        )
        
        # Check overrides applied
        assert copied.json_repair_mode == "never"
        assert copied.strict_json_parsing is True
        
        # Check original values preserved
        assert copied.json_repair_feedback is True
        assert copied.strict_schema_validation is False
        
        # Check original unchanged
        assert original.json_repair_mode == "auto"
        assert original.strict_json_parsing is False
    
    def test_copy_no_overrides(self):
        """Test copying configuration without overrides."""
        original = VidaiConfig(
            json_repair_mode="always",
            json_repair_feedback=False
        )
        
        copied = original.copy()
        
        # Should be identical
        assert copied.json_repair_mode == "always"
        assert copied.json_repair_feedback is False
        assert copied.strict_json_parsing is False
        assert copied.strict_schema_validation is False
    
    def test_repr(self):
        """Test string representation of configuration."""
        config = VidaiConfig(
            json_repair_mode="auto",
            json_repair_feedback=True,
            default_base_url="https://test.com/v1"
        )
        
        repr_str = repr(config)
        assert "VidaiConfig(" in repr_str
        assert "json_repair_mode='auto'" in repr_str
        assert "json_repair_feedback=True" in repr_str
        assert "default_base_url='https://test.com/v1'" in repr_str
    
    def test_all_boolean_env_vars(self):
        """Test all boolean environment variable parsing."""
        boolean_vars = [
            ("VIDAI_JSON_FEEDBACK", "json_repair_feedback"),
            ("VIDAI_STRICT_JSON", "strict_json_parsing"),
            ("VIDAI_STRICT_SCHEMA", "strict_schema_validation"),
            ("VIDAI_TRACK_TRANSFORM", "track_request_transformation"),
            ("VIDAI_TRACK_REPAIR", "track_json_repair")
        ]
        
        for env_var, config_attr in boolean_vars:
            # Test true values
            for true_val in ["true", "True", "TRUE", "1"]:
                with patch.dict(os.environ, {env_var: true_val}):
                    config = VidaiConfig.from_env()
                    assert getattr(config, config_attr) is True
            
            # Test false values
            for false_val in ["false", "False", "FALSE", "0"]:
                with patch.dict(os.environ, {env_var: false_val}):
                    config = VidaiConfig.from_env()
                    assert getattr(config, config_attr) is False
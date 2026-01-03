"""Configuration management for Vidai."""

import os
from typing import Optional


class VidaiConfig:
    """Configuration settings for Vidai behavior."""
    
    def __init__(
        self,
        *,
        json_repair_mode: str = "auto",
        json_repair_feedback: bool = True,
        strict_json_parsing: bool = False,
        strict_schema_validation: bool = False,
        track_request_transformation: bool = True,
        track_json_repair: bool = True,
        log_level: str = "WARNING",
        default_base_url: Optional[str] = None,
        structured_output_method: str = "native",
        provider: Optional[str] = None,
    ) -> None:
        """
        Initialize Vidai configuration.
        
        Args:
            json_repair_mode: When to repair JSON ("auto", "always", "never")
            json_repair_feedback: Whether to provide repair feedback
            strict_json_parsing: Fail fast on invalid JSON
            strict_schema_validation: Fail fast on schema validation errors
            track_request_transformation: Track request transformation timing
            track_json_repair: Track JSON repair timing
            log_level: Logging level for Vidai
            default_base_url: Default base URL (None = require explicit)
            structured_output_method: "native" (API param) or "tool_fill" (tool-use polyfill)
            provider: Explicitly forced provider ("openai", "anthropic", "gemini", etc.)
        """
        self.json_repair_mode = json_repair_mode
        self.json_repair_feedback = json_repair_feedback
        self.strict_json_parsing = strict_json_parsing
        self.strict_schema_validation = strict_schema_validation
        self.track_request_transformation = track_request_transformation
        self.track_json_repair = track_json_repair
        self.log_level = log_level
        self.default_base_url = default_base_url
        self.structured_output_method = structured_output_method
        self.provider = provider
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration values."""
        if self.json_repair_mode not in {"auto", "always", "never"}:
            raise ValueError(
                f"json_repair_mode must be one of 'auto', 'always', 'never', "
                f"got {self.json_repair_mode!r}"
            )
        
        if self.structured_output_method not in {"native", "tool_fill"}:
            raise ValueError(
                f"structured_output_method must be one of 'native', 'tool_fill', "
                f"got {self.structured_output_method!r}"
            )
        
        if self.log_level not in {"DEBUG", "INFO", "WARNING", "ERROR"}:
            raise ValueError(
                f"log_level must be one of 'DEBUG', 'INFO', 'WARNING', 'ERROR', "
                f"got {self.log_level!r}"
            )



    @staticmethod
    def _parse_bool(value: Optional[str], default: bool) -> bool:
        """Parse boolean from string/env var."""
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")
    
    @classmethod
    def from_env(cls) -> "VidaiConfig":
        """Create configuration from environment variables."""
        return cls(
            json_repair_mode=os.getenv("VIDAI_JSON_REPAIR", "auto"),
            json_repair_feedback=cls._parse_bool(os.getenv("VIDAI_JSON_FEEDBACK"), True),
            strict_json_parsing=cls._parse_bool(os.getenv("VIDAI_STRICT_JSON"), False),
            strict_schema_validation=cls._parse_bool(os.getenv("VIDAI_STRICT_SCHEMA"), False),
            track_request_transformation=cls._parse_bool(os.getenv("VIDAI_TRACK_TRANSFORM"), True),
            track_json_repair=cls._parse_bool(os.getenv("VIDAI_TRACK_REPAIR"), True),
            log_level=os.getenv("VIDAI_LOG_LEVEL", "WARNING"),
            default_base_url=os.getenv("VIDAI_BASE_URL"),
            structured_output_method=os.getenv("VIDAI_STRUCTURED_OUTPUT_METHOD", "native"),
            provider=os.getenv("VIDAI_PROVIDER"),
        )
    
    def copy(self, **overrides) -> "VidaiConfig":
        """Create a copy of the configuration with optional overrides."""
        # Get current values as dict
        current_values = {
            "json_repair_mode": self.json_repair_mode,
            "json_repair_feedback": self.json_repair_feedback,
            "strict_json_parsing": self.strict_json_parsing,
            "strict_schema_validation": self.strict_schema_validation,
            "track_request_transformation": self.track_request_transformation,
            "track_json_repair": self.track_json_repair,
            "log_level": self.log_level,
            "default_base_url": self.default_base_url,
            "structured_output_method": self.structured_output_method,
            "provider": self.provider,
        }
        
        # Apply overrides
        current_values.update(overrides)
        
        return VidaiConfig(**current_values)
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            f"VidaiConfig("
            f"json_repair_mode={self.json_repair_mode!r}, "
            f"json_repair_feedback={self.json_repair_feedback!r}, "
            f"strict_json_parsing={self.strict_json_parsing!r}, "
            f"strict_schema_validation={self.strict_schema_validation!r}, "
            f"track_request_transformation={self.track_request_transformation!r}, "
            f"track_json_repair={self.track_json_repair!r}, "
            f"log_level={self.log_level!r}, "
            f"default_base_url={self.default_base_url!r}, "
            f"structured_output_method={self.structured_output_method!r}, "
            f"provider={self.provider!r})"
        )
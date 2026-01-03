
import pytest
import os
from unittest.mock import MagicMock, patch

from vidai.config import VidaiConfig
from vidai.providers import ProviderFactory
from vidai.providers.anthropic import AnthropicProvider
from vidai.providers.gemini import GeminiProvider
from vidai.providers.groq import GroqProvider
from vidai.providers.base import BaseProvider

@pytest.fixture
def config():
    return VidaiConfig()

def test_create_provider_anthropic_detection(config):
    """Test detection of Anthropic provider via URL."""
    # Native Anthropic URL
    provider = ProviderFactory.create_provider(
        config, 
        base_url="https://api.anthropic.com/v1"
    )
    assert isinstance(provider, AnthropicProvider)

def test_create_provider_gemini_detection(config):
    """Test detection of Gemini provider via URL."""
    provider = ProviderFactory.create_provider(
        config,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    assert isinstance(provider, GeminiProvider)

def test_create_provider_groq_detection(config):
    """Test detection of Groq provider via URL."""
    provider = ProviderFactory.create_provider(
        config,
        base_url="https://api.groq.com/openai/v1"
    )
    assert isinstance(provider, GroqProvider)

def test_create_provider_default(config):
    """Test fallback to BaseProvider (OpenAI)."""
    provider = ProviderFactory.create_provider(
        config,
        base_url="https://api.openai.com/v1"
    )
    # Depending on implementation, might return BaseProvider or specific OpenAIProvider
    # Factory currently returns BaseProvider for unknown/standard URLs
    assert isinstance(provider, BaseProvider)
    assert not isinstance(provider, (AnthropicProvider, GeminiProvider, GroqProvider))

def test_create_provider_with_openai_base(config):
    """Test standard OpenAI compatible URL."""
    provider = ProviderFactory.create_provider(
        config,
        base_url="https://api.openai.com/v1"
    )
    assert isinstance(provider, BaseProvider)

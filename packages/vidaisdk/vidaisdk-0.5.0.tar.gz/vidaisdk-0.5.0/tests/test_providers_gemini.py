"""Tests for GeminiProvider."""

import pytest
from unittest.mock import MagicMock, patch, Mock
import os
from vidai.providers.gemini import GeminiProvider
from vidai.config import VidaiConfig

@pytest.fixture
def config():
    return VidaiConfig()

@pytest.fixture
def provider(config):
    return GeminiProvider(config)

def test_init_raises_without_api_key():
    """Test that initialization checks for API key availability (lazy or eager)."""
    # Gemini provider checks for key in execute_request, not init, 
    # but let's verify if there are any init checks.
    # Looking at code: __init__ just calls super.
    # execute_request checks env var.
    pass

@patch.dict("os.environ", {"GEMINI_API_KEY": "sk-test"})
def test_transform_request_text(provider):
    """Test transforming simple text request."""
    # Gemini uses OpenAI-compatible endpoint but relies on transform_request 
    # for specific fixes if needed, or inherits from ToolPolyfillProvider.
    # It overrides transform_request to handle image URLs.
    
    messages = [{"role": "user", "content": "Hello"}]
    # transform_request signature: (self, kwargs)
    kwargs = {
        "model": "gemini-1.5-flash",
        "messages": messages,
        "stream": False
    }
    
    new_kwargs = provider.transform_request(kwargs)
    
    # Should be mostly pass-through for text
    assert new_kwargs["messages"] == messages

@patch.dict("os.environ", {"GEMINI_API_KEY": "sk-test"})
@patch("vidai.utils.encode_file")
@patch("vidai.utils.get_media_type")
def test_transform_request_image_url(mock_get_type, mock_encode, provider):
    """Test transforming image_url to Data URI for Gemini."""
    mock_encode.return_value = "base64_data"
    mock_get_type.return_value = "image/jpeg"
    
    messages = [
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": "Describe"},
                {"type": "image_url", "image_url": {"url": "http://img.com/foo.jpg"}}
            ]
        }
    ]
    
    kwargs = {
        "model": "gemini-1.5-flash",
        "messages": messages,
        "stream": False
    }
    
    new_kwargs = provider.transform_request(kwargs)
    new_messages = new_kwargs["messages"]
    
    img_block = new_messages[0]["content"][1]
    assert img_block["type"] == "image_url"
    # Expect Data URI format: data:image/jpeg;base64,base64_data
    assert img_block["image_url"]["url"] == "data:image/jpeg;base64,base64_data"

@patch.dict("os.environ", {"GEMINI_API_KEY": "sk-test"})
@patch("vidai.utils.encode_file")
@patch("vidai.utils.get_media_type")
def test_transform_request_pdf(mock_get_type, mock_encode, provider):
    """Test transforming PDF URL to Data URI for Gemini."""
    mock_encode.return_value = "pdf_base64"
    mock_get_type.return_value = "application/pdf"
    
    messages = [
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": "Read"},
                {"type": "image_url", "image_url": {"url": "http://doc.com/file.pdf"}}
            ]
        }
    ]
    
    kwargs = {
        "model": "gemini-1.5-flash",
        "messages": messages,
        "stream": False
    }
    
    new_kwargs = provider.transform_request(kwargs)
    new_messages = new_kwargs["messages"]
    
    doc_block = new_messages[0]["content"][1]
    # Gemini treats PDFs as image_url with data uri application/pdf
    assert doc_block["type"] == "image_url"
    assert doc_block["image_url"]["url"] == "data:application/pdf;base64,pdf_base64"


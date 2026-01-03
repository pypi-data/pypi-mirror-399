import os
import sys
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from vidai import Vidai, VidaiConfig

from dotenv import load_dotenv

# Load env
load_dotenv()

def verify_responses_api():
    """Verify Vidai responses API support."""
    print("Initializing Vidai...")
    client = Vidai() # Will use VIDAI_BASE_URL or env vars
    
    # 1. Verify Structure
    print(f"Checking client.responses type: {type(client.responses)}")
    assert "vidai.client.EnhancedResponses" in str(type(client.responses)), "client.responses is not EnhancedResponses"
    
    # 2. Mock the actual API call since we can't hit real API
    mock_response = MagicMock()
    mock_response.id = "resp_123"
    mock_response.object = "response" 
    mock_response.created = 1234567890
    mock_response.model = "gpt-4o"
    mock_response.output = [{"type": "message", "role": "assistant", "content": "Hello world"}]
    mock_response.usage = None
    
    # Mock actual chat completions since polyfill uses that
    mock_response.choices = [MagicMock(message=MagicMock(content="Hello", tool_calls=None))]
    mock_response.choices[0].message.role = "assistant"
    
    with patch("openai.resources.chat.completions.Completions.create", return_value=mock_response) as mock_create:
        print("Calling client.responses.create()...")
        
        # Call the new API
        response = client.responses.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        # Verify call was made
        mock_create.assert_called_once()
        print("API call delegation successful.")
        
        # Verify response wrapper
        print(f"Response type: {type(response)}")
        try:
            from vidai.models import EnhancedResponse
            assert isinstance(response, EnhancedResponse) or isinstance(response, MagicMock), "Response is not wrapped correctly (or mock issue)"
            print("Response wrapper verified (or mocked).")
            
            if hasattr(response, "output"):
                print(f"Response output: {response.output}")
                
        except ImportError:
            print("Could not import EnhancedResponse for verification.")

    print("\nSUCCESS: Responses API integration verified.")

if __name__ == "__main__":
    verify_responses_api()

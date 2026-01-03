import os
import sys
from pydantic import BaseModel
from vidai import Vidai, VidaiConfig
from dotenv import load_dotenv

load_dotenv()

# Define Pydantic model
class UserInfo(BaseModel):
    name: str
    age: int

def verify_real_responses():
    print("Initializing Vidai...")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in env.")
        return
        
    client = Vidai(api_key=api_key)
    
    providers = [
        {
            "name": "DeepSeek",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "base_url": "https://api.deepseek.com", # Official URL
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        },
        {
            "name": "Groq",
            "api_key": os.getenv("GROQ_API_KEY"),
            "base_url": "https://api.groq.com/openai/v1", # Official URL
            "model": os.getenv("GROQ_MODEL", "llama3-8b-8192") 
        },
         {
            "name": "VidaiServer",
            "api_key": os.getenv("VIDAI_SERVER_API_KEY"),
            "base_url": os.getenv("VIDAI_BASE_URL", "http://localhost:3000/v1"),
            "model": os.getenv("WIZZSERVER_MODEL")
        }
    ]

    for p in providers:
        print(f"\n--- Testing {p['name']} ---")
        if not p['api_key']:
            print(f"⏩ SKIPPING: {p['name']} API Key not found.")
            continue
            
        print(f"Model: {p['model']}, Base: {p['base_url']}")
        client = Vidai(api_key=p['api_key'], base_url=p['base_url'])
        
        try:
            resp = client.responses.create(
                model=p['model'],
                messages=[{"role": "user", "content": "Create a user named Alice, age 30."}],
                response_format=UserInfo
            )
            print(f"Response Type: {type(resp)}")
            
            if hasattr(resp, "output"):
                 print(f"✅ SUCCESS: output is List. Count: {len(resp.output)}")
                 for i, item in enumerate(resp.output):
                     print(f"  Item {i}: {item}")
                     
                     # VERIFY OBJECT PARITY (Dot Notation Access)
                     # OpenAI Native structure: item.content is List[ResponseOutputText]
                     # item.content[0].text contains the string
                     
                     if hasattr(item, "content") and isinstance(item.content, list):
                         if item.content and hasattr(item.content[0], "text"):
                             text_content = item.content[0].text
                             print(f"  ✅ Object Access Success: item.content[0].text = {text_content[:50]}...")
                         else:
                             text_content = str(item.content)
                         
                         if "Alice" in text_content:
                             print("  ✅ Content Verified")
                         else:
                             print("  ❌ Content Mismatch")
                     else:
                         print(f"  ❌ FAILURE: Content is not a list of objects. Type: {type(getattr(item, 'content', None))}")
                         
                 print(f"Full Response Object: {resp}")
            else:
                 print(f"❌ FAILURE: Output is not a list or missing. Type: {type(getattr(resp, 'output', None))}")

        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    verify_real_responses()

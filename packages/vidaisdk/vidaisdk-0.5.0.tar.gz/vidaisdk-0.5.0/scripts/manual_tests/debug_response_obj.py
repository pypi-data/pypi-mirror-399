what import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    resp = client.responses.create(
        model="gpt-4o-mini",
        input="hi"
    )
    print("Response dir:", dir(resp))
    print("Response dict:", resp.model_dump())
except Exception as e:
    print(e)

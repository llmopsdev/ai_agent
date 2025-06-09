import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
if sys.argv[1]:
    prompt = sys.argv[1]
    model = "gemini-2.0-flash-001"
    messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    res = client.models.generate_content(model=model, contents=messages)
else:
    print("Error no prompt provided")
    sys.exit(1)
if len(sys.argv) > 2 and sys.argv[2] == "--verbose":
    print(f"User prompt: {prompt}")
    print(f"Prompt tokens: {res.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {res.usage_metadata.candidates_token_count}")
    sys.exit(0)
else:
    print(res.text)

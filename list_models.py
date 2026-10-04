import google.generativeai as genai
import os

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in environment.")
else:
    genai.configure(api_key=api_key)
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print("Available models:")
        for name in models:
            print(name)
    except Exception as e:
        print(f"Error listing models: {e}")

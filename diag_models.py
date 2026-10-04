import google.generativeai as genai
import os

api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

test_names = [
    "models/gemini-2.0-flash",
    "models/gemini-1.5-flash-latest",
    "models/gemini-flash-latest",
    "models/gemini-pro-latest"
]

for name in test_names:
    print(f"\nTesting: {name}")
    try:
        model = genai.GenerativeModel(name)
        response = model.generate_content("test")
        print(f"SUCCESS: {name}")
        # If success, stop here
        break
    except Exception as e:
        print(f"FAILURE: {name} - {e}")

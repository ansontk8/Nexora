import google.generativeai as genai
import os

api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models_to_try = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-2.0-flash-exp",
    "gemini-pro"
]

with open("model_test_results.txt", "w") as f:
    f.write(f"Testing models with API key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}\n")
    for m_name in models_to_try:
        f.write(f"Testing {m_name}...\n")
        try:
            model = genai.GenerativeModel(m_name)
            response = model.generate_content("Hello")
            f.write(f"✅ {m_name} worked!\n")
        except Exception as e:
            f.write(f"❌ {m_name} failed: {e}\n")

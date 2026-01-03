"""
List available Gemini models
"""
import os
import google.generativeai as genai

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY not set")
    exit(1)

genai.configure(api_key=api_key)

print("Available Gemini models:")
print("="*60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  • {model.name}")
        print(f"    Display name: {model.display_name}")
        print(f"    Methods: {', '.join(model.supported_generation_methods)}")
        print()

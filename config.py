import os
from google import genai

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "models/gemini-2.5-flash"

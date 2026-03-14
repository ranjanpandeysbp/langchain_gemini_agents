from langchain_google_genai import ChatGoogleGenerativeAI

import os
from dotenv import load_dotenv

# Load environment variables from .env file
# By default, it looks for a .env file in the current directory
# You can also specify a path: load_dotenv(dotenv_path='path/to/.env')
load_dotenv()
# Disable LangSmith tracing to suppress API key warning
os.environ["LANGCHAIN_TRACING_V2"] = "false"  # Disable LangChain tracing to avoid LangSmith API key warnings
api_key = os.getenv('GEMINI_API_KEY')
model = os.getenv('GEMINI_MODEL')

llm = ChatGoogleGenerativeAI(
    model=model,
    temperature=0.7,#temperature controls how random or creative the LLM’s responses are.
    google_api_key=api_key
)

response = llm.invoke("Explain machine learning in simple terms")

print(response.content)
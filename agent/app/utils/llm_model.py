"""LLM model initialization and configuration."""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_llm_model(temperature: float = 0.3) -> ChatGoogleGenerativeAI:
    """
    Create and return a configured LLM model.
    """
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=temperature,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
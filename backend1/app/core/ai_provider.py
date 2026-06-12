from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_ollama import OllamaLLM


ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
LOCAL_ENV = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(ROOT_ENV)
load_dotenv(LOCAL_ENV, override=False)

CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3").strip()
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434").strip()
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "").strip()

model = OllamaLLM(
    model=CHAT_MODEL,
    base_url=OLLAMA_API_URL,
    api_key=OLLAMA_API_KEY or None,
    temperature=0.3,
)


async def generate_reply(prompt: str) -> str:
    response = model.invoke(prompt)
    return str(response).strip()

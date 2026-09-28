"""Configuração do cliente DeepSeek."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import AsyncOpenAI

DEEPSEEK_BASE_URL = "https://api.deepseek.com"

MODEL_REASONER = "deepseek-reasoner"
MODEL_CHAT = "deepseek-chat"

DEEPSEEK_MODEL = MODEL_REASONER


@dataclass(frozen=True)
class DeepSeekConfig:
    model: str
    temperature: float = 0.0


CODE_REVIEWER = DeepSeekConfig(model=MODEL_REASONER, temperature=0.0)
GIT_AGENT = DeepSeekConfig(model=MODEL_CHAT, temperature=0.2)


def create_deepseek_client() -> AsyncOpenAI:
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Defina a variavel de ambiente DEEPSEEK_API_KEY antes de executar o programa."
        )
    return AsyncOpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
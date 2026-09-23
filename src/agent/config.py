"""Configuração do cliente DeepSeek."""

import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-flash"


def create_deepseek_client() -> AsyncOpenAI:
    """Cria um cliente configurado exclusivamente para a API da DeepSeek."""
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Defina a variável de ambiente DEEPSEEK_API_KEY antes de executar o programa."
        )

    return AsyncOpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)

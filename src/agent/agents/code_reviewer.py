"""Agente de revisão de código."""

from agents import Agent, OpenAIChatCompletionsModel, set_tracing_disabled

from ..config import DEEPSEEK_MODEL, create_deepseek_client
from ..tools.file_tools import create_write_corrected_file_tool, read_file_tool


def create_agent(file_path: str, fix: bool = False) -> Agent:
    """Cria o agente revisor conectado à DeepSeek."""
    set_tracing_disabled(True)
    model = OpenAIChatCompletionsModel(
        model=DEEPSEEK_MODEL,
        openai_client=create_deepseek_client(),
    )
    instructions = """Você é um agente especializado em revisão de código Python.

Sua função é analisar código Python e apontar possíveis bugs, problemas de
legibilidade, problemas de estrutura e melhorias. Use a ferramenta de leitura
para obter o conteúdo do arquivo solicitado. Seja claro e objetivo.
"""
    tools = [read_file_tool]
    if fix:
        instructions += """
Você está no modo de correção. Após analisar o arquivo, corrija os problemas
encontrados e use write_corrected_file para salvar o conteúdo completo corrigido.
Não altere outros arquivos. Na resposta final, resuma as correções aplicadas.
"""
        tools.append(create_write_corrected_file_tool(file_path))
    return Agent(name="Code Reviewer", instructions=instructions, model=model, tools=tools)

"""Agente para inspeção e operações Git controladas."""

from agents import Agent, OpenAIChatCompletionsModel, set_tracing_disabled

from ..config import DEEPSEEK_MODEL, create_deepseek_client
from ..services.repository import GitRepository
from ..tools.git_tools import create_git_tools


def create_agent(repository_path: str, allow_write: bool = False) -> Agent:
    """Cria um agente Git limitado ao repositório indicado."""
    set_tracing_disabled(True)
    repository = GitRepository(repository_path)
    model = OpenAIChatCompletionsModel(
        model=DEEPSEEK_MODEL,
        openai_client=create_deepseek_client(),
    )
    instructions = """Você é um agente Git cuidadoso. Analise o estado do repositório
usando somente as ferramentas disponíveis e responda em português. Nunca sugira
ou execute push, merge, rebase, reset, checkout de arquivos, remoções ou comandos
de terminal genéricos. Se a solicitação exigir uma operação indisponível, explique
o que o usuário deve confirmar ou executar manualmente."""
    if allow_write:
        instructions += """\nA preparação de arquivos e a criação de commit foram autorizadas.
Antes de usá-las, mostre o diff e confirme na resposta quais arquivos e mensagem
serão usados. Nunca inclua arquivos não solicitados."""
    return Agent(
        name="Git Agent",
        instructions=instructions,
        model=model,
        tools=create_git_tools(repository, allow_write=allow_write),
    )

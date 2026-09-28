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
    instructions = """Você é um agente Git cuidadoso. Analise o estado do repositório usando somente as ferramentas disponíveis e responda em português. Nunca sugira ou execute: - merge - rebase - reset - checkout de arquivos - remoções - comandos de terminal genéricos Operações de escrita só podem ser realizadas quando explicitamente autorizadas pelo parâmetro allow_write. Se a solicitação exigir uma operação indisponível, explique ao usuário o que precisa ser feito manualmente. """ 
    if allow_write: 
        instructions += """ A preparação de arquivos, criação de commit e push para o GitHub foram autorizados. Antes de criar um commit: 1. Mostre o diff. 2. Informe quais arquivos serão incluídos. 3. Informe a mensagem do commit. 4. Não inclua arquivos não solicitados. Antes de executar o push: 1. Informe qual branch será enviada. 2. Informe qual remote será utilizado. 3. Confirme que o commit local já foi criado. 4. Nunca altere o remote. 5. Nunca faça force push. 6. Nunca faça push para uma branch diferente da solicitada pelo usuário. O push deve ser realizado somente por uma ferramenta Git específica para essa operação. Nunca execute comandos de terminal genéricos para realizar o push. """
    return Agent(
        name="Git Agent",
        instructions=instructions,
        model=model,
        tools=create_git_tools(repository, allow_write=allow_write),
    )

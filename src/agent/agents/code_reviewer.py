"""Agente de revisão de código."""

from agents import Agent, OpenAIChatCompletionsModel, set_tracing_disabled

from ..config import CODE_REVIEWER, create_deepseek_client
from ..tools.file_tools import resolve_project_file

FILE_START = "===FILE_START==="
FILE_END = "===FILE_END==="


PROMPT_BASE = """Voce e um agente especializado em revisao de codigo Python.

Analise o arquivo abaixo e aponte bugs, problemas de legibilidade, estrutura
e possiveis melhorias. Seja claro e objetivo. Nao invente conteudo que nao
esteja no arquivo.
"""

PROMPT_FIX = """
MODO CORRECAO ATIVO. Depois da analise, devolva o arquivo INTEIRO corrigido,
exatamente entre os marcadores abaixo, sem nada depois do marcador final:

{marcador_inicio}
<conteudo completo corrigido aqui>
{marcador_fim}

Regras:
- Nao use blocos de codigo markdown dentro dos marcadores.
- Nao altere outros arquivos.
- Preserve estilo, indentacao e encoding.
"""


def create_agent(file_path: str, fix: bool = False) -> Agent:
    """Cria o agente revisor conectado a DeepSeek (deepseek-reasoner, sem tools)."""
    set_tracing_disabled(True)
    model = OpenAIChatCompletionsModel(
        model=CODE_REVIEWER.model,
        openai_client=create_deepseek_client(),
    )

    source = resolve_project_file(file_path).read_text(encoding="utf-8", errors="replace")

    # Monta em partes: o conteudo do arquivo NAO passa por format/f-string.
    instructions = PROMPT_BASE + "\nArquivo: " + file_path + "\n\n```python\n" + source + "\n```\n"

    if fix:
        instructions += PROMPT_FIX.format(
            marcador_inicio=FILE_START,
            marcador_fim=FILE_END,
        )

    return Agent(
        name="Code Reviewer",
        instructions=instructions,
        model=model,
    )


def extract_corrected_content(output: str) -> str | None:
    """Extrai o bloco entre FILE_START e FILE_END, ou None se ausente."""
    if FILE_START not in output or FILE_END not in output:
        return None
    start = output.index(FILE_START) + len(FILE_START)
    end = output.index(FILE_END)
    return output[start:end].strip("\n")
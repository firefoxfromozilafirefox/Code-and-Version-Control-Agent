"""Ferramentas seguras para leitura de arquivos no diretório de trabalho."""

from pathlib import Path

from agents import function_tool

PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
MAX_FILE_SIZE_BYTES = 200_000


def resolve_workspace_file(file_path: str) -> Path:
    """Resolve um arquivo dentro de workspace/, rejeitando acessos externos."""
    candidate = Path(file_path)
    if not candidate.is_absolute():
        candidate = WORKSPACE_DIR / candidate

    resolved_path = candidate.resolve()
    try:
        resolved_path.relative_to(WORKSPACE_DIR.resolve())
    except ValueError as error:
        raise ValueError("O arquivo deve estar dentro da pasta workspace/.") from error

    if not resolved_path.is_file():
        raise ValueError("Arquivo não encontrado ou não é um arquivo regular.")
    if resolved_path.stat().st_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"O arquivo excede o limite de {MAX_FILE_SIZE_BYTES} bytes para revisão."
        )

    return resolved_path


@function_tool
def read_file_tool(file_path: str) -> str:
    """Lê um arquivo de código dentro de workspace/ para revisão."""
    return resolve_workspace_file(file_path).read_text(encoding="utf-8")


def create_write_corrected_file_tool(file_path: str):
    """Cria uma ferramenta que só pode sobrescrever o arquivo solicitado."""
    target_file = resolve_workspace_file(file_path)
    backup_file = target_file.with_suffix(f"{target_file.suffix}.bak")

    @function_tool
    def write_corrected_file(content: str) -> str:
        """Salva o código corrigido completo no arquivo solicitado.

        Use esta ferramenta apenas após analisar o arquivo. O argumento content
        deve conter o arquivo completo corrigido, sem Markdown.
        """
        if not content.strip():
            raise ValueError("O conteúdo corrigido não pode estar vazio.")

        if not backup_file.exists():
            backup_file.write_text(target_file.read_text(encoding="utf-8"), encoding="utf-8")

        target_file.write_text(content, encoding="utf-8")
        return f"Arquivo corrigido salvo em {target_file.name}. Backup: {backup_file.name}."

    return write_corrected_file

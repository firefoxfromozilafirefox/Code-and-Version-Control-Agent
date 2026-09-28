"""Ferramentas seguras de leitura e escrita de arquivos dentro do projeto."""

from pathlib import Path

from agents import function_tool

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MAX_FILE_SIZE_BYTES = 200_000

BLOCKED_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules",
                ".mypy_cache", ".pytest_cache", ".ruff_cache"}
BLOCKED_FILES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
BLOCKED_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}

WRITE_BLOCKED_FILES = BLOCKED_FILES | {"pyproject.toml", "poetry.lock",
                                       "uv.lock", "package-lock.json"}
WRITE_BLOCKED_SUFFIXES = BLOCKED_SUFFIXES | {".exe", ".dll", ".so", ".dylib"}


def _is_blocked(path: Path) -> bool:
    if any(part in BLOCKED_DIRS for part in path.parts):
        return True
    if path.name in BLOCKED_FILES:
        return True
    if path.suffix.lower() in BLOCKED_SUFFIXES:
        return True
    return False


def resolve_project_file(file_path: str) -> Path:
    """Resolve um arquivo dentro de PROJECT_ROOT, rejeitando acessos externos e sensiveis."""
    candidate = Path(file_path)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate

    resolved = candidate.resolve()

    try:
        resolved.relative_to(PROJECT_ROOT.resolve())
    except ValueError as error:
        raise ValueError("O arquivo deve estar dentro do diretorio do projeto.") from error

    if _is_blocked(resolved):
        raise ValueError(f"Acesso negado ao caminho sensivel: {resolved.name}")

    if not resolved.is_file():
        raise ValueError("Arquivo nao encontrado ou nao e um arquivo regular.")
    if resolved.stat().st_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"O arquivo excede o limite de {MAX_FILE_SIZE_BYTES} bytes para revisao."
        )
    return resolved


@function_tool
def read_file_tool(file_path: str) -> str:
    """Le o conteudo de um arquivo de codigo do projeto."""
    return resolve_project_file(file_path).read_text(encoding="utf-8", errors="replace")


def write_corrected_file(file_path: str, new_content: str, *, dry_run: bool = False) -> str:
    """Grava conteudo corrigido com backup .bak. Determinista, sem LLM no meio."""
    path = resolve_project_file(file_path)

    if path.name in WRITE_BLOCKED_FILES:
        raise ValueError(f"Escrita bloqueada para arquivo protegido: {path.name}")
    if path.suffix.lower() in WRITE_BLOCKED_SUFFIXES:
        raise ValueError(f"Escrita bloqueada para tipo de arquivo: {path.suffix}")

    original = path.read_text(encoding="utf-8", errors="replace")
    if original == new_content:
        return f"Sem alteracoes em {file_path}."

    if dry_run:
        return f"[dry-run] {file_path} seria reescrito ({len(new_content)} chars)."

    backup = path.with_suffix(path.suffix + ".bak")
    backup.write_text(original, encoding="utf-8")
    path.write_text(new_content, encoding="utf-8")
    return f"Arquivo {file_path} atualizado (backup: {backup.name})."


def list_project_tree(subdir: str = ".", max_entries: int = 500) -> list[str]:
    """Lista arquivos do projeto (respeitando os bloqueios)."""
    base = (PROJECT_ROOT / subdir).resolve()
    try:
        base.relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        raise ValueError("O diretorio deve estar dentro do projeto.")
    if not base.is_dir():
        raise ValueError("Diretorio nao encontrado.")

    entries: list[str] = []
    for p in sorted(base.rglob("*")):
        if len(entries) >= max_entries:
            break
        if not p.is_file():
            continue
        rel = p.relative_to(PROJECT_ROOT)
        if _is_blocked(rel):
            continue
        entries.append(str(rel))
    return entries


@function_tool
def list_files(subdir: str = ".") -> str:
    """Lista arquivos do projeto para o agente explorar a estrutura."""
    return "\n".join(list_project_tree(subdir))


# ---- Compat com nomes antigos ---------------------------------------------

resolve_workspace_file = resolve_project_file
read_project_file = read_file_tool
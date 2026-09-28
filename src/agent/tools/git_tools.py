"""Ferramentas Git com escopo limitado a um único repositório validado."""

from agents import function_tool

from ..services.repository import GitRepository


def create_git_tools(repository: GitRepository, allow_write: bool = False):
    """Cria ferramentas Git; alterações exigem autorização explícita no CLI."""

    @function_tool
    def git_status() -> str:
        """Mostra a branch atual e os arquivos alterados."""
        return repository.status()

    @function_tool
    def git_diff() -> str:
        """Mostra as alterações ainda não preparadas para commit."""
        return repository.diff()

    @function_tool
    def git_log(limit: int = 10) -> str:
        """Mostra os commits mais recentes, com limite entre 1 e 50."""
        return repository.log(limit)

    @function_tool
    def git_branches() -> str:
        """Lista as branches locais e remotas."""
        return repository.branches()
        
    @function_tool
    def git_push(remote: str = "origin", branch: str = "main") -> str:
        """Envia commits para o repositório remoto."""
        return repository.push(remote, branch)

    tools = [git_status, git_diff, git_log, git_branches, git_push]
    if allow_write:
        @function_tool
        def git_stage(paths: list[str]) -> str:
            """Prepara arquivos específicos do repositório para commit."""
            return repository.stage(paths)

        @function_tool
        def git_commit(message: str) -> str:
            """Cria um commit somente com mudanças previamente preparadas."""
            return repository.commit(message)

        tools.extend([git_stage, git_commit])
    return tools

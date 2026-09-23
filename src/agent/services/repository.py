"""Validação e execução restrita de comandos Git."""

from pathlib import Path
import subprocess


class GitRepository:
    """Representa um repositório Git validado fora do projeto do agente."""

    def __init__(self, path: str) -> None:
        candidate = Path(path).expanduser().resolve()
        if not candidate.is_dir():
            raise ValueError("O caminho do repositório não existe ou não é um diretório.")

        self.path = candidate
        self._run("rev-parse", "--is-inside-work-tree")

    def _run(self, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.path,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        if completed.returncode:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise ValueError(f"Falha ao executar git {' '.join(args)}: {detail}")
        return completed.stdout.strip()

    def status(self) -> str:
        return self._run("status", "--short", "--branch") or "Repositório sem alterações."

    def diff(self) -> str:
        return self._run("diff", "--no-ext-diff") or "Não há alterações não preparadas."

    def log(self, limit: int = 10) -> str:
        safe_limit = max(1, min(limit, 50))
        return self._run("log", f"--max-count={safe_limit}", "--oneline") or "Ainda não há commits."

    def branches(self) -> str:
        return self._run("branch", "--all", "--no-color")

    def stage(self, paths: list[str]) -> str:
        if not paths:
            raise ValueError("Informe ao menos um arquivo para preparar.")
        for path in paths:
            candidate = (self.path / path).resolve()
            try:
                candidate.relative_to(self.path)
            except ValueError as error:
                raise ValueError("Os arquivos devem pertencer ao repositório informado.") from error
        self._run("add", "--", *paths)
        return "Arquivos preparados para commit."

    def commit(self, message: str) -> str:
        if not message.strip():
            raise ValueError("A mensagem de commit não pode estar vazia.")
        return self._run("commit", "-m", message)

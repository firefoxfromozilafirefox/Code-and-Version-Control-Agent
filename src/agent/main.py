"""Ponto de entrada dos agentes de revisão de código e Git."""

import argparse
import asyncio
import logging
import sys

from agents import Runner
from openai import APIConnectionError, APIStatusError, AuthenticationError

from .agents.code_reviewer import create_agent as create_code_reviewer
from .agents.git_agent import create_agent as create_git_agent
from .tools.file_tools import resolve_workspace_file


async def review_file(file_path: str, fix: bool = False) -> str:
    """Executa a revisão ou correção de um arquivo permitido."""
    resolve_workspace_file(file_path)
    agent = create_code_reviewer(file_path, fix=fix)
    task = f"Revise o arquivo de código '{file_path}'. O caminho é relativo a workspace/."
    if fix:
        task += " Corrija os problemas encontrados no próprio arquivo."
    result = await Runner.run(
        agent,
        task,
    )
    usage = result.context_wrapper.usage
    print("\n--- Consumo de tokens ---")
    print(f"Chamadas ao modelo: {usage.requests}")
    print(f"Tokens de entrada: {usage.input_tokens}")
    print(f"Tokens de saída: {usage.output_tokens}")
    print(f"Total de tokens: {usage.total_tokens}")
    return result.final_output


async def run_git_task(repository_path: str, task: str, allow_write: bool = False) -> str:
    """Executa uma solicitação Git dentro do repositório validado."""
    agent = create_git_agent(repository_path, allow_write=allow_write)
    result = await Runner.run(agent, task)
    return result.final_output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa agentes de revisão de código e Git.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    review_parser = subparsers.add_parser("review", help="Revisa um arquivo em workspace/.")
    review_parser.add_argument(
        "file_path",
        help="Caminho relativo ao diretório workspace/ do arquivo a revisar.",
    )
    review_parser.add_argument(
        "--corrigir",
        action="store_true",
        help="Permite que o agente corrija o arquivo e crie um backup .bak.",
    )

    git_parser = subparsers.add_parser("git", help="Executa uma tarefa Git em um repositório.")
    git_parser.add_argument("task", help="Solicitação em linguagem natural para o agente Git.")
    git_parser.add_argument("--repo", required=True, help="Caminho do repositório Git alvo.")
    git_parser.add_argument(
        "--permitir-escrita",
        action="store_true",
        help="Autoriza somente git add de arquivos específicos e git commit.",
    )

    arguments = sys.argv[1:]
    # Compatibilidade com a versão anterior: `code-reviewer arquivo.py`.
    if arguments and arguments[0] not in {"review", "git", "-h", "--help"}:
        arguments.insert(0, "review")
    return parser.parse_args(arguments)


def run() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    try:
        if args.command == "review":
            output = review_file(args.file_path, fix=args.corrigir)
        else:
            output = run_git_task(args.repo, args.task, allow_write=args.permitir_escrita)
        print(asyncio.run(output))
    except AuthenticationError:
        logging.error(
            "A DeepSeek recusou a autenticação. Verifique se DEEPSEEK_API_KEY no .env é uma chave ativa e válida."
        )
        raise SystemExit(1) from None
    except APIConnectionError:
        logging.error("Não foi possível conectar à API da DeepSeek. Tente novamente mais tarde.")
        raise SystemExit(1) from None
    except APIStatusError as error:
        logging.error("A API da DeepSeek retornou HTTP %s.", error.status_code)
        raise SystemExit(1) from None
    except (RuntimeError, ValueError) as error:
        logging.error("%s", error)
        raise SystemExit(1) from error

if __name__ == "__main__":
    run()

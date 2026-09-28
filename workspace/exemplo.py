"""Exemplos simples de funções utilitárias com tratamento de erros."""

from collections.abc import Iterable, Mapping
from typing import Any


def calculate_average(numbers: Iterable[float]) -> float:
    """Retorna a média aritmética dos valores informados.

    Args:
        numbers: Coleção de valores numéricos. Não pode estar vazia.

    Returns:
        A média aritmética dos valores.

    Raises:
        ValueError: Se ``numbers`` estiver vazia, pois a média seria indefinida.
        TypeError: Se algum dos valores não for numérico.
    """
    values = list(numbers)
    if not values:
        raise ValueError("Não é possível calcular a média de uma coleção vazia.")

    return sum(values) / len(values)


def format_users(users: Iterable[Mapping[str, Any]]) -> str:
    """Retorna os nomes dos usuários em maiúsculas, separados por vírgula.

    Usuários sem o campo ``"name"``, com nome ``None`` ou com nome vazio
    (ou apenas espaços) são ignorados. Itens que não forem mapeamentos
    também são ignorados, em vez de provocar erro.

    Args:
        users: Coleção de mapeamentos que podem conter a chave ``"name"``.

    Returns:
        String com os nomes em maiúsculas separados por ``", "``.
    """
    names: list[str] = []
    for user in users:
        if not isinstance(user, Mapping):
            continue

        raw_name = user.get("name")
        if raw_name is None:
            continue

        name = str(raw_name).strip()
        if name:
            names.append(name.upper())

    return ", ".join(names)


def main() -> None:
    """Executa uma demonstração das funções do módulo."""
    values = [10.0, 20.0, 30.0]
    print(calculate_average(values))

    users = [{"name": "ana"}, {"name": "bruno"}, {}, {"name": None}]
    print(format_users(users))


if __name__ == "__main__":
    main()

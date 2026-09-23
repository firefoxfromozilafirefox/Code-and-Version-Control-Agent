import pytest

from agent.tools.file_tools import (
    WORKSPACE_DIR,
    create_write_corrected_file_tool,
    resolve_workspace_file,
)


def test_resolve_workspace_file_rejects_paths_outside_workspace() -> None:
    with pytest.raises(ValueError, match="workspace"):
        resolve_workspace_file("../.env")


def test_resolve_workspace_file_rejects_missing_files() -> None:
    with pytest.raises(ValueError, match="não encontrado"):
        resolve_workspace_file("arquivo_inexistente.py")


def test_workspace_directory_is_project_local() -> None:
    assert WORKSPACE_DIR.name == "workspace"
    assert WORKSPACE_DIR.parent.name == "agent"


def test_write_tool_is_created_only_for_a_workspace_file() -> None:
    tool = create_write_corrected_file_tool("exemplo.py")
    assert tool.name == "write_corrected_file"

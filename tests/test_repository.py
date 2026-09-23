import subprocess

import pytest

from agent.services.repository import GitRepository


def make_repository(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    return GitRepository(str(tmp_path))


def test_repository_requires_a_git_work_tree(tmp_path) -> None:
    with pytest.raises(ValueError, match="rev-parse"):
        GitRepository(str(tmp_path))


def test_stage_rejects_paths_outside_repository(tmp_path) -> None:
    repository = make_repository(tmp_path)
    with pytest.raises(ValueError, match="pertencer"):
        repository.stage(["../outside.py"])


def test_status_reports_clean_repository(tmp_path) -> None:
    repository = make_repository(tmp_path)
    assert repository.status() == "Repositório sem alterações."

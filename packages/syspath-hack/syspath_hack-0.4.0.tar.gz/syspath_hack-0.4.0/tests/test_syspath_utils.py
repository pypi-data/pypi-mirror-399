"""Tests for the public helpers that manipulate sys.path."""

from __future__ import annotations

import sys
import typing as typ
from unittest import mock

import pytest

from syspath_hack import (
    DEFAULT_SIGIL,
    ProjectRootNotFoundError,
    SysPathMode,
    add_project_root,
    add_to_syspath,
    append_action_root,
    clear_from_syspath,
    ensure_module_dir,
    find_project_root,
    prepend_action_root,
    prepend_project_root,
    prepend_to_syspath,
    remove_from_syspath,
    temp_syspath,
)

if typ.TYPE_CHECKING:
    from pathlib import Path


def test_add_to_syspath_appends_resolved_path(tmp_path: Path) -> None:
    """It appends the resolved path and avoids duplicates."""
    target = tmp_path / "package"
    target.mkdir()
    starting_entries = ["/already-present"]

    with mock.patch.object(sys, "path", starting_entries.copy()):
        add_to_syspath(target)

        resolved = str(target.resolve())
        assert sys.path[-1] == resolved

        add_to_syspath(target)
        assert sys.path.count(resolved) == 1


def test_remove_from_syspath_removes_all_matches(tmp_path: Path) -> None:
    """It removes every occurrence of the resolved path."""
    target = tmp_path / "package"
    target.mkdir()
    resolved = str(target.resolve())
    other = str((tmp_path / "other").resolve())

    with mock.patch.object(sys, "path", [other, resolved, resolved]):
        remove_from_syspath(target)
        assert sys.path == [other]


def test_find_project_root_returns_first_match(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """It returns the first ancestor containing the marker file."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / DEFAULT_SIGIL).write_text("[project]\nname = 'demo'\n")

    nested = project_root / "src" / "demo"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)

    result = find_project_root()

    assert result == project_root.resolve()


def test_find_project_root_uses_start_parameter(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """It prefers the provided start directory over the CWD."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / DEFAULT_SIGIL).write_text("[project]\nname = 'demo'\n")

    start_dir = project_root / "src" / "demo"
    start_dir.mkdir(parents=True)

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    result = find_project_root(start=start_dir)

    assert result == project_root.resolve()


def test_find_project_root_start_uses_origin_in_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """It reports the explicit start directory in error messages."""
    fake_home = tmp_path / "home"
    start_dir = fake_home / "workspace" / "repo"
    start_dir.mkdir(parents=True)

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    with (
        mock.patch("pathlib.Path.home", return_value=fake_home),
        pytest.raises(ProjectRootNotFoundError) as excinfo,
    ):
        find_project_root("missing.sigil", start=start_dir)

    assert str(start_dir.resolve()) in str(excinfo.value)


def test_find_project_root_raises_when_reaching_home(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """It raises once the search reaches the home directory boundary."""
    fake_home = tmp_path / "home"
    nested = fake_home / "workspace" / "repo"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)

    with (
        mock.patch("pathlib.Path.home", return_value=fake_home),
        pytest.raises(ProjectRootNotFoundError),
    ):
        find_project_root("nonexistent.sigil")


def test_add_project_root_adds_directory_to_sys_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """It adds the located project root to sys.path."""
    project_root = tmp_path / "workspace"
    project_root.mkdir()
    (project_root / DEFAULT_SIGIL).write_text("[project]\nname = 'demo'\n")

    nested = project_root / "src"
    nested.mkdir()
    monkeypatch.chdir(nested)

    with mock.patch.object(sys, "path", []):
        add_project_root()

        resolved = str(project_root.resolve())
        assert sys.path == [resolved]


def test_add_project_root_uses_start_parameter(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """It searches from the provided start directory."""
    project_root = tmp_path / "workspace"
    project_root.mkdir()
    (project_root / DEFAULT_SIGIL).write_text("[project]\nname = 'demo'\n")

    start_dir = project_root / "src" / "pkg"
    start_dir.mkdir(parents=True)

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    with mock.patch.object(sys, "path", []):
        add_project_root(start=start_dir)

        resolved = str(project_root.resolve())
        assert sys.path == [resolved]


def test_prepend_project_root_uses_start_parameter(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """It prepends the project root found from the provided start directory."""
    project_root = tmp_path / "workspace"
    project_root.mkdir()
    (project_root / DEFAULT_SIGIL).write_text("[project]\nname = 'demo'\n")

    start_dir = project_root / "src" / "pkg"
    start_dir.mkdir(parents=True)

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)

    with mock.patch.object(sys, "path", ["sentinel"]):
        prepend_project_root(start=start_dir)

        resolved = str(project_root.resolve())
        assert sys.path == [resolved, "sentinel"]


def test_add_project_root_includes_existing_extra_paths(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """It appends the project root followed by existing extra paths."""
    project_root = tmp_path / "workspace"
    project_root.mkdir()
    (project_root / DEFAULT_SIGIL).write_text("[project]\nname = 'demo'\n")

    extra = project_root / "src" / "pkg"
    extra.mkdir(parents=True)
    missing = project_root / "missing"

    tests_dir = project_root / "tests"
    tests_dir.mkdir()
    monkeypatch.chdir(tests_dir)

    with mock.patch.object(sys, "path", []):
        add_project_root(extra_paths=["src/pkg", missing])

        assert sys.path == [
            str(project_root.resolve()),
            str(extra.resolve()),
        ]


def test_append_action_root_adds_default_extras(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """It appends action root and its scripts/src directories when present."""
    project_root = tmp_path / "action-repo"
    project_root.mkdir()
    (project_root / "action.yml").write_text("name: demo\n")
    scripts = project_root / "scripts"
    scripts.mkdir()
    src = project_root / "src"
    src.mkdir()

    runner_dir = project_root / "runner"
    runner_dir.mkdir()
    monkeypatch.chdir(runner_dir)

    with mock.patch.object(sys, "path", []):
        append_action_root()

        assert sys.path == [
            str(project_root.resolve()),
            str(scripts.resolve()),
            str(src.resolve()),
        ]


def test_prepend_to_syspath_inserts_resolved_path(tmp_path: Path) -> None:
    """It prepends the resolved path and avoids duplicates."""
    target = tmp_path / "package"
    target.mkdir()
    starting_entries = ["/already-present", "/other"]

    with mock.patch.object(sys, "path", starting_entries.copy()):
        prepend_to_syspath(target)

        resolved = str(target.resolve())
        assert sys.path[0] == resolved
        assert sys.path[1:] == starting_entries

        prepend_to_syspath(target)
        assert sys.path.count(resolved) == 1


def test_prepend_to_syspath_moves_existing_entry_to_front(tmp_path: Path) -> None:
    """It moves an existing equivalent entry to the front of sys.path."""
    target = tmp_path / "package"
    target.mkdir()
    resolved = str(target.resolve())

    with mock.patch.object(sys, "path", ["/other", resolved, "/later"]):
        prepend_to_syspath(target)

        assert sys.path[0] == resolved
        assert sys.path[1:] == ["/other", "/later"]


def test_prepend_to_syspath_preserves_blank_cwd_entry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """It keeps the CWD sentinel when prepending that same directory."""
    monkeypatch.chdir(tmp_path)
    starting_entries = ["", "/other"]

    with mock.patch.object(sys, "path", starting_entries.copy()):
        prepend_to_syspath(tmp_path)

        resolved = str(tmp_path.resolve())
        assert sys.path == [resolved, "", "/other"]


def test_prepend_project_root_places_root_first(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """It prepends the located project root so it wins import precedence."""
    project_root = tmp_path / "workspace"
    project_root.mkdir()
    (project_root / DEFAULT_SIGIL).write_text("[project]\nname = 'demo'\n")

    nested = project_root / "pkg"
    nested.mkdir()
    monkeypatch.chdir(nested)

    existing = ["/already-present"]

    with mock.patch.object(sys, "path", existing.copy()):
        prepend_project_root()

        resolved = str(project_root.resolve())
        assert sys.path[0] == resolved
        assert sys.path[1:] == existing


def test_prepend_project_root_adds_extras_after_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """It keeps the project root first and prepends extra paths afterwards."""
    project_root = tmp_path / "workspace"
    project_root.mkdir()
    (project_root / DEFAULT_SIGIL).write_text("[project]\nname = 'demo'\n")

    extra = project_root / "src" / "pkg"
    extra.mkdir(parents=True)

    monkeypatch.chdir(project_root)

    with mock.patch.object(sys, "path", ["/existing"]):
        prepend_project_root(extra_paths=["src/pkg", "does-not-exist"])

        assert sys.path[0] == str(project_root.resolve())
        assert sys.path[1] == str(extra.resolve())
        assert sys.path[2:] == ["/existing"]


def test_prepend_action_root_adds_defaults_with_precedence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """It keeps action root first then its scripts/src directories."""
    project_root = tmp_path / "action-repo"
    project_root.mkdir()
    (project_root / "action.yml").write_text("name: demo\n")
    scripts = project_root / "scripts"
    scripts.mkdir()
    src = project_root / "src"
    src.mkdir()

    monkeypatch.chdir(project_root)

    with mock.patch.object(sys, "path", ["/existing"]):
        prepend_action_root()

        assert sys.path[:3] == [
            str(project_root.resolve()),
            str(scripts.resolve()),
            str(src.resolve()),
        ]
        assert sys.path[3:] == ["/existing"]


def test_temp_syspath_prepend_restores_original_list(tmp_path: Path) -> None:
    """It prepends during the context and restores the previous sys.path."""
    target = tmp_path / "package"
    target.mkdir()

    starting = ["/already-present", "/other"]

    with mock.patch.object(sys, "path", starting.copy()):
        with temp_syspath([target], mode=SysPathMode.PREPEND):
            resolved = str(target.resolve())
            assert sys.path[0] == resolved
            assert sys.path[1:] == starting

        assert sys.path == starting


def test_temp_syspath_append_adds_once(tmp_path: Path) -> None:
    """It appends when requested and deduplicates inputs."""
    target = tmp_path / "package"
    target.mkdir()

    with mock.patch.object(sys, "path", ["/existing"]):
        with temp_syspath([target, str(target)], mode=SysPathMode.APPEND):
            resolved = str(target.resolve())
            assert sys.path[-1] == resolved
            assert sys.path.count(resolved) == 1

        assert sys.path == ["/existing"]


def test_ensure_module_dir_defaults_to_prepend(tmp_path: Path) -> None:
    """It adds the module directory at the front of sys.path."""
    module = tmp_path / "pkg" / "module.py"
    module.parent.mkdir()
    module.write_text("print('demo')\n")

    starting = ["/other"]

    with mock.patch.object(sys, "path", starting.copy()):
        module_dir = ensure_module_dir(module)

        resolved = str(module.parent.resolve())
        assert module_dir == module.parent.resolve()
        assert sys.path[0] == resolved
        assert sys.path[1:] == starting


def test_ensure_module_dir_supports_append_mode(tmp_path: Path) -> None:
    """It appends the module directory when requested."""
    module = tmp_path / "pkg" / "module.py"
    module.parent.mkdir()
    module.touch()

    with mock.patch.object(sys, "path", ["/existing"]):
        ensure_module_dir(module, mode=SysPathMode.APPEND)

        resolved = str(module.parent.resolve())
        assert sys.path[-1] == resolved
        assert sys.path[0] == "/existing"


def test_clear_from_syspath_removes_multiple_entries(tmp_path: Path) -> None:
    """It removes every occurrence of multiple paths."""
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()

    first_resolved = str(first.resolve())
    second_resolved = str(second.resolve())

    with mock.patch.object(
        sys, "path", [first_resolved, second_resolved, "/keep", first_resolved]
    ):
        clear_from_syspath([first, second])

        assert sys.path == ["/keep"]


def test_syspath_mode_allows_combining_flags() -> None:
    """It supports combining append and prepend preferences."""
    both = SysPathMode.APPEND | SysPathMode.PREPEND

    assert SysPathMode.APPEND in both
    assert SysPathMode.PREPEND in both
    assert list(both) == [SysPathMode.APPEND, SysPathMode.PREPEND]

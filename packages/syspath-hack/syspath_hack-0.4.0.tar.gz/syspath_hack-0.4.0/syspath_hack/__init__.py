"""syspath-hack package."""

from __future__ import annotations

from .pure import (
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

PACKAGE_NAME = "syspath_hack"

__all__ = [
    "DEFAULT_SIGIL",
    "ProjectRootNotFoundError",
    "SysPathMode",
    "add_project_root",
    "add_to_syspath",
    "append_action_root",
    "clear_from_syspath",
    "ensure_module_dir",
    "find_project_root",
    "prepend_action_root",
    "prepend_project_root",
    "prepend_to_syspath",
    "remove_from_syspath",
    "temp_syspath",
]

# syspath-hack

syspath-hack provides small helpers for keeping `sys.path` predictable in
scripts, notebooks, and tests. It resolves entries before adding them, avoids
duplicates, and can locate your project root with a marker file such as
`pyproject.toml`.

## Installation

Install from PyPI with your preferred tool:

- `pip install syspath-hack`
- `uv add syspath-hack`

## Quick start

Add the project root to `sys.path` so local imports work during ad-hoc scripts
or notebooks:

```python
from syspath_hack import add_project_root

add_project_root()  # finds the nearest pyproject.toml above the cwd
```

Prefer `prepend_project_root()` when you need imports to prioritise the working
tree over installed copies of the package.

Both project-root helpers accept `extra_paths` for common subdirectories. For
example, to prioritise the project and its `src` tree:

```python
from syspath_hack import prepend_project_root

prepend_project_root(extra_paths=["src"])
```

Working in a GitHub Action? Use `append_action_root()` or
`prepend_action_root()` to locate `action.yml` and automatically include
`scripts` and `src` when they exist.

## Working with temporary paths

When you need to add a directory only briefly, use `temp_syspath` to mutate
`sys.path` inside a context manager and restore it afterwards:

```python
from syspath_hack import SysPathMode, temp_syspath

with temp_syspath(["plugins"], mode=SysPathMode.PREPEND):
    import plugin_loader  # noqa: F401
```

For module-local imports, `ensure_module_dir(__file__)` adds the current file's
directory to `sys.path` in one call, replacing the boilerplate
`Path(__file__).resolve().parent` pattern.

## Custom project markers

You can search for a different marker file and handle failures explicitly:

```python
from syspath_hack import ProjectRootNotFoundError, find_project_root

try:
    repo_root = find_project_root("poetry.lock")
except ProjectRootNotFoundError as err:
    raise SystemExit(f"Could not locate the repository: {err}") from err
else:
    print(repo_root)
```

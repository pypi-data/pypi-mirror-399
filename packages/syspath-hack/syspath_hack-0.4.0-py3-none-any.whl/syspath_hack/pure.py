"""Pure Python helpers for managing sys.path state."""

from __future__ import annotations

import contextlib
import enum
import sys
import typing as typ
from pathlib import Path

Pathish = Path | str
ModeInput = typ.Union["SysPathMode", "_SysPathModes", typ.Iterable["SysPathMode"]]
DEFAULT_SIGIL = "pyproject.toml"


class StrEnum(str, enum.Enum):
    """Minimal string-valued Enum used for sys.path modes."""

    def __str__(self) -> str:  # pragma: no cover - trivial
        """Return the underlying string value for readability."""
        return str(self.value)


class SysPathMode(StrEnum):
    """Control how paths should be inserted into sys.path."""

    APPEND = "append"
    PREPEND = "prepend"

    def __or__(self, other: ModeInput) -> _SysPathModes:
        """Combine modes into an ordered, deduplicated collection."""
        if isinstance(other, SysPathMode):
            return _SysPathModes(self, other)
        if isinstance(other, _SysPathModes):
            return _SysPathModes(self, *other)
        if isinstance(other, typ.Iterable):
            return _SysPathModes(self, *_coerce_mode_iterable(other))
        return NotImplemented

    def __ror__(self, other: ModeInput) -> _SysPathModes:
        """Combine when the enum appears on the right-hand side of |."""
        if isinstance(other, SysPathMode):
            return _SysPathModes(other, self)
        if isinstance(other, _SysPathModes):
            return _SysPathModes(*other, self)
        if isinstance(other, typ.Iterable):
            return _SysPathModes(*_coerce_mode_iterable(other), self)
        return NotImplemented


class _SysPathModes(typ.Iterable[SysPathMode]):
    """Ordered, deduplicated collection of sys.path mutation modes."""

    def __init__(self, *modes: SysPathMode) -> None:
        unique: list[SysPathMode] = []

        for mode in modes:
            if not isinstance(mode, SysPathMode):
                msg = "modes must be SysPathMode instances"
                raise TypeError(msg)

            if mode not in unique:
                unique.append(mode)

        self._modes = tuple(unique)

    def __iter__(self) -> typ.Iterator[SysPathMode]:
        return iter(self._modes)

    def __contains__(self, item: object) -> bool:  # pragma: no cover - trivial
        return item in self._modes

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._modes)

    def __or__(self, other: ModeInput) -> _SysPathModes:
        """Combine two ordered collections of modes."""
        if isinstance(other, SysPathMode):
            return _SysPathModes(*self._modes, other)
        if isinstance(other, _SysPathModes):
            return _SysPathModes(*self._modes, *other._modes)
        if isinstance(other, typ.Iterable):
            return _SysPathModes(*self._modes, *_coerce_mode_iterable(other))
        return NotImplemented


def _coerce_mode_iterable(candidates: typ.Iterable[SysPathMode]) -> list[SysPathMode]:
    """Validate a collection of modes and maintain their order."""
    modes: list[SysPathMode] = []
    for candidate in candidates:
        if not isinstance(candidate, SysPathMode):
            msg = "mode entries must be SysPathMode instances"
            raise TypeError(msg)
        modes.append(candidate)
    return modes


def _coerce_modes(mode: ModeInput) -> _SysPathModes:
    """Normalise supplied modes to an ordered, deduplicated container."""
    if isinstance(mode, _SysPathModes):
        return mode

    if isinstance(mode, SysPathMode):
        return _SysPathModes(mode)

    if isinstance(mode, typ.Iterable):
        return _SysPathModes(*_coerce_mode_iterable(mode))

    msg = "mode must be SysPathMode or an iterable of SysPathMode values"
    raise TypeError(msg)


def _dedupe_resolved_paths(paths: typ.Iterable[Pathish]) -> tuple[Path, ...]:
    """Return resolved paths in the order seen without duplicates."""
    resolved_paths: list[Path] = []
    seen: set[Path] = set()

    for pth in paths:
        resolved = _to_resolved_path(pth)
        if resolved in seen:
            continue
        seen.add(resolved)
        resolved_paths.append(resolved)

    return tuple(resolved_paths)


def _apply_modes(resolved: Path, modes: _SysPathModes) -> None:
    """Apply the requested sys.path mutation modes in order."""
    for mode in modes:
        if mode is SysPathMode.PREPEND:
            prepend_to_syspath(resolved)
        elif mode is SysPathMode.APPEND:
            add_to_syspath(resolved)
        else:  # pragma: no cover - defensive
            msg = f"Unsupported SysPathMode value {mode!r}"
            raise ValueError(msg)


class ProjectRootNotFoundError(RuntimeError):
    """Raised when a project root marker cannot be located safely."""


def _to_resolved_path(pth: Pathish) -> Path:
    """Return an absolute, normalised Path for comparisons."""
    path = Path(pth).expanduser()
    return path.resolve(strict=False)


def _resolve_sys_path_entry(entry: object) -> Path | None:
    """Resolve a sys.path entry when it resembles a filesystem location."""
    if not isinstance(entry, str):
        return None

    candidate = Path.cwd() if entry == "" else Path(entry)

    try:
        return candidate.expanduser().resolve(strict=False)
    except (OSError, RuntimeError, ValueError):
        return None


def _iter_resolved_sys_path() -> typ.Iterator[tuple[int, Path]]:
    """Provide index and resolved path pairs for usable sys.path entries."""
    for index, entry in enumerate(sys.path):
        resolved = _resolve_sys_path_entry(entry)
        if resolved is None:
            continue
        yield index, resolved


def add_to_syspath(pth: Pathish) -> None:
    """Append the resolved path to sys.path when it is not yet present."""
    target = _to_resolved_path(pth)

    for _, existing in _iter_resolved_sys_path():
        if existing == target:
            return

    sys.path.append(str(target))


def prepend_to_syspath(pth: Pathish) -> None:
    """Place the resolved path at the front of sys.path exactly once."""
    target = _to_resolved_path(pth)

    # Keep the blank sentinel entry ("") that tracks the live CWD even when it
    # resolves to the same directory as the target.
    indexes_to_remove = [
        index
        for index, entry in _iter_resolved_sys_path()
        if entry == target and sys.path[index] != ""
    ]

    for index in reversed(indexes_to_remove):
        del sys.path[index]

    sys.path.insert(0, str(target))


def remove_from_syspath(pth: Pathish) -> None:
    """Remove all occurrences of the resolved path from sys.path."""
    target = _to_resolved_path(pth)
    indexes_to_remove = [
        index for index, entry in _iter_resolved_sys_path() if entry == target
    ]

    for index in reversed(indexes_to_remove):
        del sys.path[index]


def find_project_root(
    sigil: str | None = None, *, start: Pathish | None = None
) -> Path:
    """Find the nearest ancestor containing the marker file.

    The search stops before returning the user's home directory or any higher
    directory. A dedicated runtime error communicates when no marker is found.
    Use start to override the current working directory.
    """
    if sigil is None:
        sigil = DEFAULT_SIGIL
    if not sigil:
        msg = "sigil must be a non-empty string"
        raise ValueError(msg)

    current = Path.cwd().resolve() if start is None else _to_resolved_path(start)
    origin = current
    home = Path.home().resolve()

    while True:
        if current == home:
            break

        candidate = current / sigil
        if candidate.is_file():
            return current

        parent = current.parent
        if parent == current:
            break

        current = parent

    msg = (
        f"Unable to locate {sigil!r} when ascending from {origin} "
        f"before reaching the home directory {home}"
    )
    raise ProjectRootNotFoundError(msg)


def _iter_existing_extra_paths(
    project_root: Path, extra_paths: typ.Iterable[Pathish]
) -> typ.Iterator[Path]:
    """Yield resolved extra paths that exist, joining relatives to the root."""
    for extra in extra_paths:
        candidate = Path(extra)
        if not candidate.is_absolute():
            candidate = project_root / candidate
        resolved = candidate.expanduser().resolve(strict=False)
        if resolved.exists():
            yield resolved


def add_project_root(
    sigil: str | None = None,
    *,
    extra_paths: typ.Iterable[Pathish] | None = None,
    start: Pathish | None = None,
) -> None:
    """Locate the project root and place it, and optional extras, on sys.path.

    Provide start to search from a specific directory instead of the CWD.
    """
    project_root = find_project_root(sigil, start=start)
    add_to_syspath(project_root)

    if extra_paths is None:
        return

    for resolved in _iter_existing_extra_paths(project_root, extra_paths):
        add_to_syspath(resolved)


def prepend_project_root(
    sigil: str | None = None,
    *,
    extra_paths: typ.Iterable[Pathish] | None = None,
    start: Pathish | None = None,
) -> None:
    """Locate the project root and move it, and optional extras, to sys.path.

    Provide start to search from a specific directory instead of the CWD.
    """
    project_root = find_project_root(sigil, start=start)

    extras: tuple[Path, ...] = ()
    if extra_paths is not None:
        extras = tuple(_iter_existing_extra_paths(project_root, extra_paths))

    for resolved in reversed(extras):
        prepend_to_syspath(resolved)

    prepend_to_syspath(project_root)


def append_action_root(*, start: Pathish | None = None) -> None:
    """Append the GitHub Action root and common subdirs to sys.path.

    Provide start to search from a specific directory instead of the CWD.
    """
    add_project_root("action.yml", extra_paths=("scripts", "src"), start=start)


def prepend_action_root(*, start: Pathish | None = None) -> None:
    """Prepend the GitHub Action root and common subdirs to sys.path.

    Provide start to search from a specific directory instead of the CWD.
    """
    prepend_project_root("action.yml", extra_paths=("scripts", "src"), start=start)


@contextlib.contextmanager
def temp_syspath(
    paths: typ.Iterable[Pathish],
    *,
    mode: ModeInput = SysPathMode.APPEND | SysPathMode.PREPEND,
) -> typ.Iterator[None]:
    """Temporarily mutate sys.path and restore it afterwards."""
    baseline = list(sys.path)
    resolved_paths = _dedupe_resolved_paths(paths)
    modes = _coerce_modes(mode)

    try:
        for resolved in resolved_paths:
            _apply_modes(resolved, modes)
        yield
    finally:
        sys.path[:] = baseline


def ensure_module_dir(
    file_path: Pathish,
    *,
    mode: ModeInput = SysPathMode.APPEND | SysPathMode.PREPEND,
) -> Path:
    """Add the directory containing file_path to sys.path and return it."""
    module_dir = Path(file_path).expanduser().resolve(strict=False).parent
    resolved_dir = _to_resolved_path(module_dir)
    _apply_modes(resolved_dir, _coerce_modes(mode))
    return resolved_dir


def clear_from_syspath(paths: typ.Iterable[Pathish]) -> None:
    """Remove all provided paths from sys.path."""
    for resolved in _dedupe_resolved_paths(paths):
        remove_from_syspath(resolved)

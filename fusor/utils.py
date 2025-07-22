from __future__ import annotations

from pathlib import Path
from typing import Iterable, List


def expand_log_paths(project_path: str, paths: Iterable[str]) -> List[str]:
    """Expand directories in ``paths`` to the ``*.log`` files they contain."""
    result: List[str] = []
    base = Path(project_path)
    for p in paths:
        p_obj = Path(p)
        resolved = p_obj if p_obj.is_absolute() else base / p_obj
        if resolved.is_dir():
            for file in sorted(resolved.glob("*.log")):
                if p_obj.is_absolute():
                    result.append(str(file))
                else:
                    try:
                        result.append(str(file.relative_to(base)))
                    except ValueError:
                        result.append(str(file))
        else:
            result.append(p)
    return result


def is_git_repo(path: str) -> bool:
    """Return ``True`` if ``path`` is inside a Git repository."""
    if not path:
        return False

    p = Path(path).resolve()
    for parent in [p, *p.parents]:
        if (parent / ".git").exists():
            return True
    return False

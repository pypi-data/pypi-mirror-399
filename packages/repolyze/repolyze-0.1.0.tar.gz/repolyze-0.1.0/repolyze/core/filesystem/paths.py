from pathlib import Path


def depth(base: Path, target: Path) -> int:
    return len(target.relative_to(base).parts)

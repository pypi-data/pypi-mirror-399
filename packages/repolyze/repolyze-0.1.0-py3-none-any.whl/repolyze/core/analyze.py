import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
from statistics import median
from typing import Union

from repolyze.core.filesystem.scan import scan
from repolyze.core.filesystem.paths import depth
from repolyze.core.tree.build import build_tree
from repolyze.models import (
    RepoStats, FileStat, DirStat,
    StructureStats, SizeStats, FileTypeStats,
    LanguageStats, TimeStats, HygieneStats,
    MetadataStats, TreeNode,
)


CODE_EXTS = {".py", ".js", ".ts", ".java", ".c", ".cpp", ".rs", ".go"}
TEMP_EXTS = {".tmp", ".bak", "~"}


def analyze(path: Union[str, Path]) -> RepoStats:
    # Convert string to Path if needed
    if isinstance(path, str):
        path = Path(path)
    path = path.resolve()

    files = []
    dirs = []
    now = datetime.now()
    ages = []

    count_by_ext = defaultdict(int)
    size_by_ext = defaultdict(int)

    modified_24h = modified_7d = modified_30d = 0
    empty_files = hidden_files = temp_files = 0
    large_files = []
    
    # Track inodes to avoid double-counting hard links
    seen_inodes = set()

    for p in scan(path):
        if p.is_dir():
            dirs.append(p)
            continue

        # Use os.stat to get inode info, don't follow symlinks
        try:
            stat = os.stat(p, follow_symlinks=False)
        except (OSError, PermissionError):
            # Skip files we can't access
            continue
        
        # Skip symlinks entirely
        if os.path.islink(p):
            continue
        
        # Check if we've already counted this inode (hard link detection)
        inode = (stat.st_dev, stat.st_ino)
        if inode in seen_inodes:
            continue
        seen_inodes.add(inode)
        
        size = stat.st_size
        mtime = stat.st_mtime

        files.append(FileStat(p, size, mtime))
        ages.append((now - datetime.fromtimestamp(mtime)).days)

        ext = p.suffix.lower() or "<no-ext>"
        count_by_ext[ext] += 1
        size_by_ext[ext] += size

        if size == 0:
            empty_files += 1

        if p.name.startswith("."):
            hidden_files += 1

        if ext in TEMP_EXTS:
            temp_files += 1

        if size > 5 * 1024 * 1024:
            large_files.append(FileStat(p, size, mtime))

        delta = now - datetime.fromtimestamp(mtime)
        if delta <= timedelta(days=1):
            modified_24h += 1
        if delta <= timedelta(days=7):
            modified_7d += 1
        if delta <= timedelta(days=30):
            modified_30d += 1

    # ---------- Structure ----------
    max_depth = max((depth(path, d) for d in dirs), default=0)
    deepest = [
        DirStat(d, depth(path, d))
        for d in dirs if depth(path, d) == max_depth
    ]

    structure = StructureStats(
        total_files=len(files),
        total_dirs=len(dirs),
        max_depth=max_depth,
        deepest_paths=deepest,
    )

    # ---------- Size ----------
    total_size = sum(f.size for f in files)
    avg_size = total_size / len(files) if files else 0

    size_stats = SizeStats(
        total_size=total_size,
        average_file_size=avg_size,
        large_files=large_files,
        small_files=sorted(files, key=lambda f: f.size)[:5],
    )

    # ---------- File types ----------
    file_types = FileTypeStats(
        count_by_extension=dict(count_by_ext),
        size_by_extension=dict(size_by_ext),
    )

    # ---------- Language ----------
    code_files = sum(count_by_ext[e] for e in CODE_EXTS if e in count_by_ext)
    language = LanguageStats(
        primary_language=max(count_by_ext, key=count_by_ext.get, default=None),
        code_vs_non_code_ratio=(
            code_files / len(files) if files else None
        ),
    )

    # ---------- Time ----------
    time_stats = TimeStats(
        oldest_file=min(files, key=lambda f: f.mtime, default=None),
        newest_file=max(files, key=lambda f: f.mtime, default=None),
        modified_last_24h=modified_24h,
        modified_last_7d=modified_7d,
        modified_last_30d=modified_30d,
        median_file_age_days=median(ages) if ages else None,
    )

    # ---------- Hygiene ----------
    hygiene = HygieneStats(
        empty_files=empty_files,
        empty_dirs=0,
        large_files=large_files,
        temp_files=temp_files,
        hidden_files=hidden_files,
    )

    # ---------- Metadata ----------
    metadata = MetadataStats(
        readme_present=(path / "README.md").exists(),
        license_present=(path / "LICENSE").exists(),
        gitignore_present=(path / ".gitignore").exists(),
        ci_present=(path / ".github").exists(),
        config_files=[
            f.name for f in path.iterdir()
            if f.name in {"pyproject.toml", "package.json"}
        ],
    )

    # ---------- Tree ----------
    tree = build_tree(path)

    return RepoStats(
        path=path,
        structure=structure,
        size=size_stats,
        file_types=file_types,
        language=language,
        time=time_stats,
        hygiene=hygiene,
        metadata=metadata,
        tree=tree,
    )

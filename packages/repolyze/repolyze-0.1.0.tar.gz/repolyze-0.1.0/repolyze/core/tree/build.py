import os
from pathlib import Path
from typing import List, Optional
from fnmatch import fnmatch
from repolyze.models import TreeNode
from repolyze.core.filesystem.scan import SKIP_DIRS


def _load_gitignore(base_path: Path) -> Optional[List[str]]:
    """Load .gitignore patterns if file exists."""
    gitignore_path = base_path / ".gitignore"
    if not gitignore_path.exists():
        return None
    
    try:
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            patterns = []
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    patterns.append(line)
            return patterns if patterns else None
    except (OSError, UnicodeDecodeError):
        return None


def _matches_gitignore(rel_path: str, patterns: List[str], is_dir: bool = False) -> bool:
    """Check if a path matches any gitignore pattern."""
    if not patterns:
        return False
    
    # Normalize path separators to forward slashes
    rel_path = rel_path.replace('\\', '/')
    
    for pattern in patterns:
        # Handle negation patterns (starting with !)
        if pattern.startswith('!'):
            continue
        
        # Remove leading slash for proper matching
        pattern = pattern.lstrip('/')
        
        # Handle directory-only patterns (ending with /)
        if pattern.endswith('/'):
            pattern = pattern.rstrip('/')
            if is_dir and (fnmatch(rel_path, pattern) or fnmatch(rel_path, f"**/{pattern}")):
                return True
        else:
            # Match both files and directories
            if fnmatch(rel_path, pattern) or fnmatch(rel_path, f"**/{pattern}"):
                return True
            # Check if any parent directory matches
            parts = rel_path.split('/')
            for i in range(len(parts)):
                if fnmatch(parts[i], pattern):
                    return True
    
    return False


def build_tree(path: Path, root_path: Optional[Path] = None, gitignore_patterns: Optional[List[str]] = None) -> TreeNode:
    """Build tree structure respecting .gitignore patterns."""
    # On first call, load gitignore from root
    if root_path is None:
        root_path = path
        gitignore_patterns = _load_gitignore(root_path)
    
    node = TreeNode(path, 0, 0)

    try:
        items = sorted(path.iterdir())
    except (OSError, PermissionError):
        return node

    for p in items:
        # Skip symlinks
        if p.is_symlink():
            continue
        
        # Skip directories we're excluding
        if p.is_dir() and p.name in SKIP_DIRS:
            continue
        
        # Check gitignore patterns
        if gitignore_patterns:
            try:
                rel_path = str(p.relative_to(root_path)).replace('\\', '/')
                if _matches_gitignore(rel_path, gitignore_patterns, is_dir=p.is_dir()):
                    continue
            except ValueError:
                pass
        
        if p.is_dir():
            child = build_tree(p, root_path, gitignore_patterns)
            node.children.append(child)
        else:
            try:
                stat = os.stat(p, follow_symlinks=False)
                node.children.append(
                    TreeNode(p, 1, stat.st_size, [])
                )
            except (OSError, PermissionError):
                # Skip files we can't access
                continue

    return node

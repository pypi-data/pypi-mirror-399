import os
from pathlib import Path
from typing import Iterator, List, Optional
from fnmatch import fnmatch

# Directories to skip during scanning
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".tox",
    ".eggs",
    "dist",
    "build",
    ".cache",
}


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
            # Check exact match and wildcard match
            if fnmatch(rel_path, pattern) or fnmatch(rel_path, f"**/{pattern}"):
                return True
            # Check if any parent directory matches
            parts = rel_path.split('/')
            for i in range(len(parts)):
                if fnmatch(parts[i], pattern):
                    return True
    
    return False


def scan(path: Path) -> Iterator[Path]:
    """Scan directory tree, excluding common temporary/cache directories and .gitignore patterns.
    
    Walks the directory tree and yields paths while:
    - Skipping directories listed in SKIP_DIRS
    - Respecting .gitignore patterns if .gitignore exists
    - Not following symlinks to avoid counting external files
    """
    # Load gitignore patterns if available
    gitignore_patterns = _load_gitignore(path)
    
    for root, dirs, files in os.walk(path, followlinks=False):
        root_path = Path(root)
        
        # Get relative path for gitignore matching
        try:
            rel_root = root_path.relative_to(path)
        except ValueError:
            rel_root = Path('.')
        
        # Filter out directories to skip
        filtered_dirs = []
        for d in dirs:
            # Skip if in SKIP_DIRS
            if d in SKIP_DIRS:
                continue
            
            # Skip if matches .gitignore pattern
            if gitignore_patterns:
                if rel_root == Path('.'):
                    rel_path = d
                else:
                    rel_path = str(rel_root / d)
                
                if _matches_gitignore(rel_path, gitignore_patterns, is_dir=True):
                    continue
            
            filtered_dirs.append(d)
        
        # Update dirs in-place to affect os.walk
        dirs[:] = filtered_dirs
        
        # Yield directories
        for d in filtered_dirs:
            yield root_path / d
        
        # Yield files (also check against gitignore)
        for f in files:
            if gitignore_patterns:
                if rel_root == Path('.'):
                    rel_path = f
                else:
                    rel_path = str(rel_root / f)
                
                if _matches_gitignore(rel_path, gitignore_patterns, is_dir=False):
                    continue
            
            yield root_path / f

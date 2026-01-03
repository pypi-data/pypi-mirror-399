from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


# ---------- Low-level models ----------

@dataclass(frozen=True)
class FileStat:
    path: Path
    size: int  # bytes
    mtime: float  # modification time (timestamp)
    lines: Optional[int] = None  # line count if applicable


@dataclass(frozen=True)
class DirStat:
    path: Path
    depth: int


# ---------- Aggregated models ----------

@dataclass
class StructureStats:
    total_files: int = 0
    total_dirs: int = 0
    max_depth: int = 0
    deepest_paths: List[DirStat] = field(default_factory=list)


@dataclass
class SizeStats:
    total_size: int = 0  # bytes
    average_file_size: float = 0.0
    large_files: List[FileStat] = field(default_factory=list)
    small_files: List[FileStat] = field(default_factory=list)


@dataclass
class FileTypeStats:
    count_by_extension: Dict[str, int] = field(default_factory=dict)
    size_by_extension: Dict[str, int] = field(default_factory=dict)


@dataclass
class LanguageStats:
    primary_language: Optional[str] = None
    code_vs_non_code_ratio: Optional[float] = None
    total_lines_of_code: Optional[int] = None


@dataclass
class TimeStats:
    oldest_file: Optional[FileStat] = None
    newest_file: Optional[FileStat] = None
    modified_last_24h: int = 0
    modified_last_7d: int = 0
    modified_last_30d: int = 0
    median_file_age_days: Optional[float] = None


@dataclass
class HygieneStats:
    empty_files: int = 0
    empty_dirs: int = 0
    large_files: List[FileStat] = field(default_factory=list)
    temp_files: int = 0
    hidden_files: int = 0


@dataclass
class MetadataStats:
    readme_present: bool = False
    license_present: bool = False
    gitignore_present: bool = False
    ci_present: bool = False
    config_files: List[str] = field(default_factory=list)


@dataclass
class TreeNode:
    path: Path
    file_count: int
    total_size: int
    children: List["TreeNode"] = field(default_factory=list)


# ---------- Root model ----------

@dataclass
class RepoStats:
    path: Path

    structure: StructureStats
    size: SizeStats
    file_types: FileTypeStats
    language: LanguageStats
    time: TimeStats
    hygiene: HygieneStats
    metadata: MetadataStats
    tree: Optional[TreeNode] = None

    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        """
        Convert stats to a JSON-serializable dictionary.
        """
        return {
            "path": str(self.path),
            "structure": self._dataclass_to_dict(self.structure),
            "size": self._dataclass_to_dict(self.size),
            "file_types": self._dataclass_to_dict(self.file_types),
            "language": self._dataclass_to_dict(self.language),
            "time": self._dataclass_to_dict(self.time),
            "hygiene": self._dataclass_to_dict(self.hygiene),
            "metadata": self._dataclass_to_dict(self.metadata),
            "tree": self._tree_to_dict(self.tree),
            "created_at": self.created_at.isoformat(),
        }

    @staticmethod
    def _dataclass_to_dict(obj):
        if obj is None:
            return None
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, list):
            return [RepoStats._dataclass_to_dict(i) for i in obj]
        if hasattr(obj, "__dict__"):
            return {
                k: RepoStats._dataclass_to_dict(v)
                for k, v in obj.__dict__.items()
            }
        return obj

    @staticmethod
    def _tree_to_dict(node: Optional[TreeNode]) -> Optional[Dict]:
        if node is None:
            return None
        return {
            "path": str(node.path),
            "file_count": node.file_count,
            "total_size": node.total_size,
            "children": [
                RepoStats._tree_to_dict(child) for child in node.children
            ],
        }

from pathlib import Path
from typing import List
from repolyze.models import TreeNode


def render_tree(node: TreeNode, prefix: str = "") -> List[str]:
    lines = [f"{prefix}{node.path.name}/"]
    children = node.children

    for i, child in enumerate(children):
        is_last = i == len(children) - 1
        connector = "└─ " if is_last else "├─ "
        extension = "   " if is_last else "│  "

        if child.children:
            lines.append(f"{prefix}{connector}{child.path.name}/")
            lines.extend(
                render_tree(child, prefix + extension)[1:]
            )
        else:
            lines.append(f"{prefix}{connector}{child.path.name}")

    return lines

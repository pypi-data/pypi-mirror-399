import argparse
from pathlib import Path
import json

from repolyze.core.analyze import analyze


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="repolyze",
        description="Show quick statistics about a code repository",
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the repository (default: current directory)",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output statistics as JSON",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = Path(args.path)

    stats = analyze(path)

    if args.json:
        # Assumes stats can be converted to dict
        print(json.dumps(stats.to_dict(), indent=2))
        return

    # Human-readable output (keep this simple)
    print(f"Repository: {stats.path}")
    print("-" * 40)

    print(f"Files:        {stats.structure.total_files}")
    print(f"Directories:  {stats.structure.total_dirs}")
    print(f"Total size (bytes):   {stats.size.total_size} bytes")
    print(f"Total size (MB):   {stats.size.total_size / (1024 * 1024):.2f} MB")

    print("\nFile types by count:")
    for ext, count in stats.file_types.count_by_extension.items():
        print(f"{ext}: {count}")

    print("\nLarge files (> 5 MB):")
    for f in stats.size.large_files:
        rel_path = f.path.relative_to(stats.path)
        size_mb = f.size / (1024 * 1024)
        print(f"{rel_path} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()

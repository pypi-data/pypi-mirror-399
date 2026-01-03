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
        print(json.dumps(stats.to_dict(), indent=2))
        return

    print(f"Repository: {stats.path}")
    print("-" * 40)

    print(f"Files:        {stats.total_files}")
    print(f"Directories:  {stats.total_dirs}")
    print(f"Total size:   {stats.total_size_human}")

    print("\nExtensions:")
    for ext, count in stats.extensions.items():
        print(f"  {ext:>6}  {count}")

    print("\nLargest files:")
    for file in stats.largest_files:
        print(f"  {file.path} ({file.size_human})")


if __name__ == "__main__":
    main()

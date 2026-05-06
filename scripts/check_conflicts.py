"""Fail if unresolved Git merge-conflict markers are committed."""
from pathlib import Path
import sys

MARKERS = ("<" * 7, "=" * 7, ">" * 7)
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv"}
TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yml",
    ".yaml",
}


def iter_text_files(root):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix not in TEXT_SUFFIXES and path.name not in {"requirements.txt"}:
            continue
        yield path


def main():
    root = Path(__file__).resolve().parents[1]
    failures = []

    for path in iter_text_files(root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for lineno, line in enumerate(lines, start=1):
            if any(marker in line for marker in MARKERS):
                failures.append(f"{path.relative_to(root)}:{lineno}: {line.strip()}")

    if failures:
        print("Unresolved merge-conflict markers found:")
        print("\n".join(failures))
        return 1

    print("No merge-conflict markers found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

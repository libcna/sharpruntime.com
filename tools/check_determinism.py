#!/usr/bin/env python3
"""Build the static site twice and compare every generated artifact by hash."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED_DATA = (
    ROOT / "assets" / "search.js",
    ROOT / "search-index.json",
    ROOT / "sitemap.xml",
    ROOT / "robots.txt",
)


def build() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "build_site.py")],
        cwd=ROOT,
        check=True,
    )


def generated_files() -> list[Path]:
    html = [
        path
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts and "content" not in path.relative_to(ROOT).parts
    ]
    return sorted(html + [path for path in GENERATED_DATA if path.is_file()])


def hashes() -> dict[str, str]:
    return {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in generated_files()
    }


def main() -> int:
    build()
    first = hashes()
    build()
    second = hashes()
    missing = sorted(first.keys() - second.keys())
    added = sorted(second.keys() - first.keys())
    changed = sorted(
        path for path in first.keys() & second.keys() if first[path] != second[path]
    )
    print(f"Generated artifacts compared: {len(second)}")
    print(f"Missing after second generation: {len(missing)}")
    print(f"Added after second generation: {len(added)}")
    print(f"Content changes between generations: {len(changed)}")
    if missing or added or changed:
        for path in missing:
            print(f"missing: {path}", file=sys.stderr)
        for path in added:
            print(f"added: {path}", file=sys.stderr)
        for path in changed:
            print(f"changed: {path}", file=sys.stderr)
        return 1
    print("Deterministic generation: OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        print(f"generation failed with exit code {error.returncode}", file=sys.stderr)
        raise SystemExit(error.returncode)

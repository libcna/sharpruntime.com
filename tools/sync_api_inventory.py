#!/usr/bin/env python3
"""Generate the public-header API discovery inventory from an explicit runtime checkout."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "api-inventory.json"


def git(runtime: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(runtime), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def build_inventory(runtime: Path) -> dict:
    components = json.loads((ROOT / "data" / "components.json").read_text(encoding="utf-8"))
    source_sha = git(runtime, "rev-parse", "HEAD")
    if source_sha != components["source_sha"]:
        raise SystemExit(
            f"Runtime HEAD {source_sha} does not match pinned component SHA {components['source_sha']}"
        )

    entries = []
    for component in components["physical_components"]:
        owner = runtime / component["owner"]
        include = owner / "include"
        headers = []
        if include.exists():
            for header in sorted(include.rglob("*.hpp")):
                relative_header = header.relative_to(include).as_posix()
                parts = Path(relative_header).parts
                namespace = "::".join(parts[:-1]) or "(global)"
                headers.append({
                    "header": relative_header,
                    "namespace": namespace,
                    "entry_name": Path(relative_header).stem,
                })
        source_count = len(list((owner / "src").rglob("*.cpp"))) if (owner / "src").exists() else 0
        test_source_count = len(list((owner / "tests").rglob("*.cpp"))) if (owner / "tests").exists() else 0
        entries.append({
            "name": component["name"],
            "owner": component["owner"],
            "public_header_count": len(headers),
            "production_source_count": source_count,
            "test_source_count": test_source_count,
            "headers": headers,
        })

    namespaces: dict[str, dict] = {}
    for component in entries:
        for header in component["headers"]:
            record = namespaces.setdefault(header["namespace"], {"header_count": 0, "components": set(), "entries": []})
            record["header_count"] += 1
            record["components"].add(component["name"])
            record["entries"].append(header["entry_name"])

    namespace_rows = []
    for name, record in sorted(namespaces.items()):
        namespace_rows.append({
            "name": name,
            "header_count": record["header_count"],
            "components": sorted(record["components"]),
            "entries": sorted(set(record["entries"])),
        })

    return {
        "schema": 1,
        "source_repository": components["source_repository"],
        "source_sha": source_sha,
        "public_header_count": sum(item["public_header_count"] for item in entries),
        "production_source_count": sum(item["production_source_count"] for item in entries),
        "namespace_path_count": len(namespace_rows),
        "components": entries,
        "namespaces": namespace_rows,
        "methodology": "Header paths under each registered physical component's include directory; entry names are filenames, not inferred method or compatibility claims.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True, help="Explicit checkout at the pinned SHA")
    parser.add_argument("--check", action="store_true", help="Fail if committed inventory differs")
    arguments = parser.parse_args()
    inventory = build_inventory(arguments.runtime.resolve())
    rendered = json.dumps(inventory, indent=2, ensure_ascii=False) + "\n"
    if arguments.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("API inventory is stale; run sync_api_inventory.py without --check")
        print(f"API inventory matches {inventory['source_sha'][:12]} ({inventory['public_header_count']} headers)")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {inventory['public_header_count']} public headers")


if __name__ == "__main__":
    main()

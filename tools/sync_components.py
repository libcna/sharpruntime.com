#!/usr/bin/env python3
"""Synchronize the public component data from Sharp Runtime's generated catalogue.

The runtime repository remains the source of truth. This script intentionally consumes its
generated catalogue rather than maintaining another independent component list.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def clean(value: str) -> str:
    value = value.strip().replace("`", "")
    return "" if value == "—" else value


def split_values(value: str) -> list[str]:
    value = clean(value)
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_table(lines: list[str], heading: str) -> list[list[str]]:
    start = lines.index(heading)
    rows: list[list[str]] = []
    in_table = False
    for line in lines[start + 1 :]:
        if line.startswith("## ") and in_table:
            break
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not in_table:
            in_table = True
            continue
        if cells and all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append(cells)
    return rows


def git_sha(runtime: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=runtime, check=True, text=True, capture_output=True
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runtime",
        type=Path,
        default=(ROOT.parent / "sharp-runtime"),
        help="Path to the Sharp Runtime checkout",
    )
    parser.add_argument("--check", action="store_true", help="Fail if committed data differs")
    args = parser.parse_args()

    runtime = args.runtime.resolve()
    catalogue = runtime / "docs" / "ComponentCatalog.md"
    text = catalogue.read_text(encoding="utf-8")
    lines = text.splitlines()
    graph = re.search(r"\*\*(\d+) physical modules\*\* and \*\*(\d+) direct", text)
    if not graph:
        raise SystemExit("Could not read graph metrics from ComponentCatalog.md")

    physical = []
    for cells in parse_table(lines, "## Physical components"):
        if len(cells) != 8:
            raise SystemExit(f"Unexpected physical-component row: {cells!r}")
        physical.append(
            {
                "name": clean(cells[0]),
                "owner": clean(cells[1]),
                "kind": clean(cells[2]),
                "public_dependencies": split_values(cells[3]),
                "private_dependencies": split_values(cells[4]),
                "test_dependencies": split_values(cells[5]),
                "external_dependency": clean(cells[6]),
                "header": clean(cells[7]),
            }
        )

    compatibility = []
    for cells in parse_table(lines, "## Compatibility components"):
        if len(cells) != 5:
            raise SystemExit(f"Unexpected compatibility-component row: {cells!r}")
        compatibility.append(
            {
                "name": clean(cells[0]),
                "owner": clean(cells[1]),
                "kind": clean(cells[2]),
                "dependencies": split_values(cells[3]),
                "header": clean(cells[4]),
            }
        )

    data = {
        "schema": 1,
        "source_repository": "https://github.com/openeggbert/sharp-runtime",
        "source_sha": git_sha(runtime),
        "physical_count": int(graph.group(1)),
        "direct_production_edges": int(graph.group(2)),
        "physical_components": physical,
        "compatibility_components": compatibility,
    }
    if len(physical) != data["physical_count"]:
        raise SystemExit(
            f"Catalogue says {data['physical_count']} physical components; parsed {len(physical)}"
        )

    output = ROOT / "data" / "components.json"
    rendered = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("data/components.json is out of date; run tools/sync_components.py")
        print(
            f"Component data current: {data['physical_count']} physical, "
            f"{data['direct_production_edges']} direct production edges"
        )
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"Wrote {output} from {data['source_sha']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

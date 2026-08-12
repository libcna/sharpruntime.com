#!/usr/bin/env python3
"""Validate preservation decisions for the pre-redesign documentation.

The disposition ledger deliberately names the immutable Git baseline. This
script reads that baseline with ``git show`` and compares every historical
``h2``/``h3`` heading with the grouped entries in the CSV. It never checks out
or modifies the historical tree.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = "22d1d1f69de7bdc6a5096493e630c83acba92571"
DEFAULT_LEDGER = ROOT / "audit" / "content-disposition.csv"
GROUP_SEPARATOR = " || "
ALLOWED_ACTIONS = {
    "retain-adapt",
    "expand",
    "rewrite",
    "replace-generated",
    "move-cross-link",
    "intentional-remove",
}
NON_INDEXED_CANONICAL_PAGES = {"search.html"}


class HeadingParser(HTMLParser):
    """Collect normalized h2/h3 text in source order."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._tag: str | None = None
        self._parts: list[str] = []
        self.headings: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag in {"h2", "h3"}:
            self._tag = tag
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._tag is not None:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != self._tag:
            return
        heading = " ".join(" ".join(self._parts).split())
        if heading:
            self.headings.append(heading)
        self._tag = None
        self._parts = []


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def baseline_headings(revision: str) -> dict[str, list[str]]:
    paths = [
        path
        for path in git("ls-tree", "-r", "--name-only", revision).splitlines()
        if path.endswith(".html")
    ]
    result: dict[str, list[str]] = {}
    for path in paths:
        parser = HeadingParser()
        parser.feed(git("show", f"{revision}:{path}"))
        result[path] = parser.headings
    return result


def groups(value: str) -> list[str]:
    return [item.strip() for item in value.split(GROUP_SEPARATOR) if item.strip()]


def safe_destination(path: str) -> Path | None:
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (ROOT / candidate).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return resolved


def validate(revision: str, ledger: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    historical = baseline_headings(revision)
    expected = Counter(
        (page, heading)
        for page, headings in historical.items()
        for heading in headings
    )
    covered: Counter[tuple[str, str]] = Counter()
    destinations: set[str] = set()

    with ledger.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {
            "old_page",
            "old_sections",
            "current_validity",
            "destination",
            "action",
            "rationale",
        }
        missing_columns = required - set(reader.fieldnames or [])
        if missing_columns:
            errors.append(
                "ledger is missing columns: " + ", ".join(sorted(missing_columns))
            )
            rows: list[dict[str, str]] = []
        else:
            rows = list(reader)

    for number, row in enumerate(rows, start=2):
        page = row["old_page"].strip()
        action = row["action"].strip()
        sections = groups(row["old_sections"])
        destination_groups = groups(row["destination"])

        if page not in historical:
            errors.append(f"row {number}: unknown baseline page {page!r}")
        if not sections:
            errors.append(f"row {number}: no historical section is named")
        if not row["current_validity"].strip():
            errors.append(f"row {number}: current_validity is empty")
        if not row["rationale"].strip():
            errors.append(f"row {number}: rationale is empty")
        if action not in ALLOWED_ACTIONS:
            errors.append(f"row {number}: unsupported action {action!r}")

        for section in sections:
            key = (page, section)
            covered[key] += 1
            if key not in expected:
                errors.append(
                    f"row {number}: {section!r} is not an h2/h3 in {page} at {revision}"
                )

        if action == "intentional-remove":
            if destination_groups and destination_groups != ["-"]:
                warnings.append(
                    f"row {number}: intentional removal also names a destination"
                )
            continue
        if not destination_groups or destination_groups == ["-"]:
            errors.append(f"row {number}: {action} requires a destination page")
            continue
        for destination in destination_groups:
            target = safe_destination(destination)
            if target is None:
                errors.append(f"row {number}: unsafe destination {destination!r}")
                continue
            if target.suffix != ".html":
                errors.append(
                    f"row {number}: destination is not a generated HTML page: {destination}"
                )
            elif not target.is_file():
                errors.append(f"row {number}: destination does not exist: {destination}")
            else:
                destinations.add(destination)

    missing = expected - covered
    unexpected_duplicates = covered - expected
    for (page, heading), count in sorted(missing.items()):
        errors.append(f"uncovered baseline heading ({count}x): {page}: {heading}")
    for (page, heading), count in sorted(unexpected_duplicates.items()):
        errors.append(
            f"duplicate/extra coverage ({count}x): {page}: {heading}"
        )

    try:
        search_index = json.loads(
            (ROOT / "search-index.json").read_text(encoding="utf-8")
        )
        indexed_urls = {item["url"] for item in search_index}
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        errors.append(f"cannot validate destination search coverage: {error}")
        indexed_urls = set()

    for destination in sorted(destinations):
        target = ROOT / destination
        text = target.read_text(encoding="utf-8")
        expected_url = "/" if destination == "index.html" else "/" + destination
        expected_canonical = "https://sharpruntime.com" + expected_url
        canonicals = re.findall(
            r'<link\s+rel="canonical"\s+href="([^"]+)"', text, re.IGNORECASE
        )
        if canonicals != [expected_canonical]:
            errors.append(
                f"destination canonical mismatch: {destination}: {canonicals!r}"
            )
        if (
            destination not in NON_INDEXED_CANONICAL_PAGES
            and expected_url not in indexed_urls
        ):
            errors.append(f"destination is not in search-index.json: {destination}")

    print(f"Baseline revision: {revision}")
    print(f"Baseline HTML pages: {len(historical)}")
    print(f"Baseline h2/h3 headings: {sum(expected.values())}")
    print(f"Disposition rows: {len(rows)}")
    print(f"Validated canonical destination pages: {len(destinations)}")
    print(
        "Validated indexed documentation destinations: "
        f"{len(destinations - NON_INDEXED_CANONICAL_PAGES)}"
    )
    print(f"Warnings: {len(warnings)}")
    print(f"Errors: {len(errors)}")
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default=DEFAULT_BASELINE)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    args = parser.parse_args()
    ledger = args.ledger if args.ledger.is_absolute() else ROOT / args.ledger
    if not ledger.is_file():
        parser.error(f"ledger does not exist: {ledger}")
    try:
        return validate(args.baseline, ledger)
    except (OSError, RuntimeError, csv.Error) as exc:
        print(f"content audit failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

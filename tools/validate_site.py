#!/usr/bin/env python3
"""Validate generated sharpruntime.com structure, discovery data and local links."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = "https://sharpruntime.com/"
UTILITY = {"404.html", "search.html"}


class Document(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.links: list[str] = []
        self.scripts: list[str] = []
        self.styles: list[str] = []
        self.metas: list[dict[str, str]] = []
        self.canonicals: list[str] = []
        self.titles = 0
        self.mains = 0
        self.h1s = 0
        self.json_ld: list[str] = []
        self._json_depth = 0
        self._json_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if "id" in data:
            self.ids.append(data["id"])
        if tag == "a" and "href" in data:
            self.links.append(data["href"])
        if tag == "script":
            if data.get("src"):
                self.scripts.append(data["src"])
            if data.get("type") == "application/ld+json":
                self._json_depth += 1
                self._json_parts = []
        if tag == "link":
            if data.get("rel") == "stylesheet" and data.get("href"):
                self.styles.append(data["href"])
            if data.get("rel") == "canonical":
                self.canonicals.append(data.get("href", ""))
            if data.get("rel") == "icon" and data.get("href"):
                self.styles.append(data["href"])
        if tag == "meta":
            self.metas.append(data)
        if tag == "title":
            self.titles += 1
        if tag == "main":
            self.mains += 1
        if tag == "h1":
            self.h1s += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json_depth:
            self.json_ld.append("".join(self._json_parts))
            self._json_depth = 0

    def handle_data(self, data: str) -> None:
        if self._json_depth:
            self._json_parts.append(data)


def local_target(source: Path, href: str) -> tuple[Path, str] | None:
    parsed = urlparse(href)
    if parsed.scheme in {"http", "https", "mailto", "tel"} or href.startswith("//"):
        return None
    raw_path = unquote(parsed.path)
    if raw_path.startswith("/"):
        target = ROOT / raw_path.lstrip("/")
    elif raw_path:
        target = source.parent / raw_path
    else:
        target = source
    if raw_path.endswith("/"):
        target /= "index.html"
    return target.resolve(), unquote(parsed.fragment)


def expected_canonical(relative: str) -> str:
    return CANONICAL if relative == "index.html" else CANONICAL + relative


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, help="Also verify component data against this checkout")
    args = parser.parse_args()
    failures: list[str] = []

    html_files = sorted(ROOT.rglob("*.html"))
    documents: dict[Path, Document] = {}
    for path in html_files:
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        if re.search(r"\{\{[a-z_]+\}\}", text):
            failures.append(f"{relative}: unresolved generated placeholder")
        if not re.match(r"(?is)^\s*<!doctype html>", text):
            failures.append(f"{relative}: missing HTML5 doctype")
        document = Document()
        try:
            document.feed(text)
            document.close()
        except Exception as error:  # HTMLParser errors are rare but should be reported
            failures.append(f"{relative}: HTML parse failed: {error}")
        documents[path.resolve()] = document

        duplicates = [key for key, count in Counter(document.ids).items() if count > 1]
        if duplicates:
            failures.append(f"{relative}: duplicate IDs: {', '.join(duplicates)}")
        if document.titles != 1 or document.mains != 1 or document.h1s != 1:
            failures.append(
                f"{relative}: expected one title/main/h1, got "
                f"{document.titles}/{document.mains}/{document.h1s}"
            )
        descriptions = [m.get("content", "") for m in document.metas if m.get("name") == "description"]
        og_fields = {m.get("property") for m in document.metas if m.get("property", "").startswith("og:")}
        if len(descriptions) != 1 or not descriptions[0].strip():
            failures.append(f"{relative}: missing/duplicate description")
        required_og = {"og:type", "og:site_name", "og:title", "og:description", "og:url", "og:image", "og:image:alt"}
        if not required_og.issubset(og_fields):
            failures.append(f"{relative}: missing OpenGraph fields {sorted(required_og - og_fields)}")
        og_images = [m.get("content", "") for m in document.metas if m.get("property") == "og:image"]
        if og_images != [CANONICAL + "assets/og-card.png"] or not (ROOT / "assets" / "og-card.png").is_file():
            failures.append(f"{relative}: social preview image mismatch")
        if document.canonicals != [expected_canonical(relative)]:
            failures.append(f"{relative}: canonical mismatch {document.canonicals!r}")
        if not document.json_ld:
            failures.append(f"{relative}: missing JSON-LD")
        for block in document.json_ld:
            try:
                json.loads(block)
            except json.JSONDecodeError as error:
                failures.append(f"{relative}: JSON-LD parse failed: {error}")

    missing_files = 0
    missing_fragments = 0
    for source, document in documents.items():
        relative = source.relative_to(ROOT).as_posix()
        for href in document.links + document.scripts + document.styles:
            resolved = local_target(source, href)
            if resolved is None:
                continue
            target, fragment = resolved
            if not target.exists() or not target.is_file():
                failures.append(f"{relative}: missing local target {href}")
                missing_files += 1
                continue
            if fragment:
                target_document = documents.get(target)
                if target_document is None and target.suffix == ".html":
                    failures.append(f"{relative}: fragment target was not parsed {href}")
                    missing_fragments += 1
                elif target_document is not None and fragment not in target_document.ids:
                    failures.append(f"{relative}: missing local fragment {href}")
                    missing_fragments += 1

    # Parse every JSON artifact.
    for path in sorted(ROOT.rglob("*.json")):
        if ".git" in path.parts:
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            failures.append(f"{path.relative_to(ROOT)}: JSON parse failed: {error}")

    try:
        sitemap_root = ET.parse(ROOT / "sitemap.xml").getroot()
    except ET.ParseError as error:
        failures.append(f"sitemap.xml: XML parse failed: {error}")
        sitemap_root = None

    index = json.loads((ROOT / "search-index.json").read_text(encoding="utf-8"))
    index_urls = [item["url"] for item in index]
    expected_paths = {path.relative_to(ROOT).as_posix() for path in html_files} - UTILITY
    expected_urls = {"/" if path == "index.html" else "/" + path for path in expected_paths}
    if len(index_urls) != len(set(index_urls)):
        failures.append("search-index.json: duplicate URLs")
    if set(index_urls) != expected_urls:
        failures.append(
            "search-index.json coverage mismatch: "
            f"missing={sorted(expected_urls - set(index_urls))}, extra={sorted(set(index_urls) - expected_urls)}"
        )

    sitemap_urls: list[str] = []
    if sitemap_root is not None:
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap_urls = [node.text or "" for node in sitemap_root.findall("s:url/s:loc", namespace)]
        expected_sitemap = {expected_canonical(path) for path in expected_paths}
        if len(sitemap_urls) != len(set(sitemap_urls)):
            failures.append("sitemap.xml: duplicate URLs")
        if set(sitemap_urls) != expected_sitemap:
            failures.append("sitemap.xml coverage differs from canonical page set")

    components = json.loads((ROOT / "data" / "components.json").read_text(encoding="utf-8"))
    catalogue_text = (ROOT / "components" / "index.html").read_text(encoding="utf-8")
    search_tags = " ".join(" ".join(item.get("tags", [])) for item in index)
    missing_components = [
        item["name"] for item in components["physical_components"]
        if item["name"] not in catalogue_text or item["name"] not in search_tags
    ]
    if missing_components:
        failures.append(f"component coverage/search missing: {missing_components}")
    if len(components["physical_components"]) != components["physical_count"]:
        failures.append("data/components.json physical_count mismatch")

    # Whole-worktree sweeps, excluding Git internals and Python caches.
    legacy_hits: list[str] = []
    stale_hits: list[str] = []
    stale_patterns = [r"40 physical", r"983 public", r"369 test", r"C\+\+17", r"C\+\+20"]
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if ("sharpruntime." + "openeggbert.com") in text:
            legacy_hits.append(path.relative_to(ROOT).as_posix())
        if path.suffix == ".html":
            for pattern in stale_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    stale_hits.append(f"{path.relative_to(ROOT)}:{pattern}")
    if legacy_hits:
        failures.append(f"legacy-domain leaks: {legacy_hits}")
    if stale_hits:
        failures.append(f"stale-fact sweep hits: {stale_hits}")

    if (ROOT / "CNAME").read_text(encoding="utf-8").strip() != "sharpruntime.com":
        failures.append("CNAME is not sharpruntime.com")
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap: https://sharpruntime.com/sitemap.xml" not in robots:
        failures.append("robots.txt does not point to the canonical sitemap")

    if args.runtime:
        command = [sys.executable, str(ROOT / "tools" / "sync_components.py"), "--runtime", str(args.runtime), "--check"]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if result.returncode:
            failures.append("component synchronization failed: " + (result.stderr or result.stdout).strip())

    if failures:
        print("Site validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"HTML pages parsed: {len(html_files)}")
    print("Broken local files: 0")
    print("Broken local fragments: 0")
    print("Duplicate IDs: 0")
    print(f"Metadata + canonical + OpenGraph + JSON-LD: {len(html_files)}/{len(html_files)}")
    print(f"Search coverage: {len(index_urls)}/{len(expected_paths)} canonical pages, exactly once")
    print(f"Sitemap coverage: {len(sitemap_urls)}/{len(expected_paths)} canonical pages, exactly once")
    print(f"Component coverage: {components['physical_count']}/{components['physical_count']} physical components")
    print("JSON/XML parsing: OK")
    print("Legacy-domain leaks: 0")
    print("Stale global-fact sweep: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Report comparable visible documentation metrics across Git revisions.

The count is diagnostic rather than a quality gate.  It considers text inside
``main`` while excluding navigation, breadcrumbs, page metadata, search
placeholders, and previous/next controls.  Generated chrome therefore does not
make a deeper sidebar look like deeper documentation.
"""

from __future__ import annotations

import argparse
import statistics
import subprocess
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD_BASELINE = "22d1d1f69de7bdc6a5096493e630c83acba92571"
FIRST_PASS = "e76d045"
EXCLUDED_CLASSES = {
    "breadcrumb",
    "breadcrumbs",
    "docs-sidebar",
    "in-page-toc",
    "next-links",
    "page-meta",
    "page-nav",
}
EXCLUDED_IDS = {"search-results"}


class MainTextParser(HTMLParser):
    """Collect visible, substantive text from one document's main element."""

    def __init__(self, *, exclude_chrome: bool) -> None:
        super().__init__(convert_charrefs=True)
        self.exclude_chrome = exclude_chrome
        self.main_depth = 0
        self.excluded_depth = 0
        self.hidden_depth = 0
        self.parts: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "main":
            self.main_depth += 1
            return
        if not self.main_depth:
            return
        if self.excluded_depth:
            self.excluded_depth += 1
            return
        if self.hidden_depth:
            self.hidden_depth += 1
            return
        classes = set(data.get("class", "").split())
        if self.exclude_chrome and (
            classes & EXCLUDED_CLASSES or data.get("id") in EXCLUDED_IDS
        ):
            self.excluded_depth = 1
        elif tag in {"script", "style", "template"} or data.get("aria-hidden") == "true":
            self.hidden_depth = 1

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        del tag, attrs

    def handle_endtag(self, tag: str) -> None:
        if not self.main_depth:
            return
        if self.excluded_depth:
            self.excluded_depth -= 1
        elif self.hidden_depth:
            self.hidden_depth -= 1
        elif tag == "main":
            self.main_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.main_depth and not self.excluded_depth and not self.hidden_depth:
            self.parts.append(data)

    @property
    def words(self) -> int:
        return len(" ".join(self.parts).split())


@dataclass(frozen=True)
class Metrics:
    pages: int
    visible_main_words: int
    visible_main_median: float
    substantive_words: int
    substantive_median: float
    tutorials: int


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, check=False, capture_output=True, text=True
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def parse_words(text: str, *, exclude_chrome: bool) -> int:
    parser = MainTextParser(exclude_chrome=exclude_chrome)
    parser.feed(text)
    parser.close()
    return parser.words


def revision_metrics(revision: str) -> Metrics:
    paths = sorted(
        path
        for path in git("ls-tree", "-r", "--name-only", revision).splitlines()
        if path.endswith(".html")
    )
    raw_counts = [
        parse_words(git("show", f"{revision}:{path}"), exclude_chrome=False)
        for path in paths
    ]
    substantive_counts = [
        parse_words(git("show", f"{revision}:{path}"), exclude_chrome=True)
        for path in paths
    ]
    tutorials = sum(
        path.startswith("tutorials/") and path != "tutorials/index.html"
        for path in paths
    )
    return Metrics(
        len(paths),
        sum(raw_counts),
        statistics.median(raw_counts),
        sum(substantive_counts),
        statistics.median(substantive_counts),
        tutorials,
    )


def current_metrics() -> Metrics:
    paths = sorted(
        path
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts and "content" not in path.relative_to(ROOT).parts
    )
    raw_counts = [
        parse_words(path.read_text(encoding="utf-8"), exclude_chrome=False)
        for path in paths
    ]
    substantive_counts = [
        parse_words(path.read_text(encoding="utf-8"), exclude_chrome=True)
        for path in paths
    ]
    tutorials = sum(
        path.relative_to(ROOT).as_posix().startswith("tutorials/")
        and path.name != "index.html"
        for path in paths
    )
    return Metrics(
        len(paths),
        sum(raw_counts),
        statistics.median(raw_counts),
        sum(substantive_counts),
        statistics.median(substantive_counts),
        tutorials,
    )


def display(label: str, metrics: Metrics) -> None:
    print(
        f"{label}: {metrics.pages} HTML pages, "
        f"{metrics.visible_main_words:,} visible main words "
        f"(median {metrics.visible_main_median:g}), "
        f"{metrics.substantive_words:,} chrome-free substantive words "
        f"(median {metrics.substantive_median:g}), "
        f"{metrics.tutorials} tutorials"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old", default=OLD_BASELINE)
    parser.add_argument("--first-pass", default=FIRST_PASS)
    args = parser.parse_args()
    display("Old baseline", revision_metrics(args.old))
    display("First pass", revision_metrics(args.first_pass))
    display("Current generated site", current_metrics())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

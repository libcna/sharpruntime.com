#!/usr/bin/env python3
"""Run static presentation checks for generated long-form documentation.

This complements, but does not replace, screenshot review.  It catches the
structural regressions most likely to appear after a large content expansion:
missing TOCs or heading anchors, unscrollable tables/code, missing mobile
breakpoints, and absent dark/light theme rules.
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.dont_write_bytecode = True

from content_metrics import parse_words


ROOT = Path(__file__).resolve().parents[1]
LONG_PAGE_WORDS = 1_000


class PresentationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, set[str]]] = []
        self.headings = 0
        self.heading_ids = 0
        self.tables = 0
        self.wrapped_tables = 0
        self.pre_blocks = 0
        self.has_toc = False
        self.has_docs_shell = False
        self.has_nav_toggle = False
        self.has_theme_toggle = False

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        data = {key: value or "" for key, value in attrs}
        classes = set(data.get("class", "").split())
        in_docs_content = any(
            "docs-content" in ancestor for _, ancestor in self.stack
        )
        if tag in {"h2", "h3"} and in_docs_content:
            self.headings += 1
            self.heading_ids += bool(data.get("id"))
        if "in-page-toc" in classes:
            self.has_toc = True
        if "docs-shell" in classes:
            self.has_docs_shell = True
        if "nav-toggle" in classes:
            self.has_nav_toggle = True
        if "theme-toggle" in classes:
            self.has_theme_toggle = True
        if tag == "table":
            self.tables += 1
            if any("table-wrap" in ancestor for _, ancestor in self.stack):
                self.wrapped_tables += 1
        if tag == "pre":
            self.pre_blocks += 1
        self.stack.append((tag, classes))

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        del tag, attrs

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


def main() -> int:
    failures: list[str] = []
    html_files = sorted(
        path
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts and "content" not in path.relative_to(ROOT).parts
    )
    long_pages = 0
    toc_pages = 0
    headings = 0
    heading_ids = 0
    tables = 0
    wrapped_tables = 0
    pre_blocks = 0

    for path in html_files:
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        parser = PresentationParser()
        parser.feed(text)
        parser.close()
        words = parse_words(text, exclude_chrome=True)

        headings += parser.headings
        heading_ids += parser.heading_ids
        tables += parser.tables
        wrapped_tables += parser.wrapped_tables
        pre_blocks += parser.pre_blocks

        if parser.headings != parser.heading_ids:
            failures.append(f"{relative}: h2/h3 heading without an ID")
        if parser.tables != parser.wrapped_tables:
            failures.append(
                f"{relative}: {parser.wrapped_tables}/{parser.tables} tables are wrapped"
            )
        if not parser.has_nav_toggle or not parser.has_theme_toggle:
            failures.append(f"{relative}: missing navigation or theme control")

        if words >= LONG_PAGE_WORDS and parser.headings >= 4:
            long_pages += 1
            if parser.has_toc and parser.has_docs_shell:
                toc_pages += 1
            else:
                failures.append(f"{relative}: long page lacks documentation shell/TOC")

    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
    css_requirements = {
        "default dark theme": r":root\s*\{[^}]*color-scheme:\s*dark",
        "explicit light theme": r':root\[data-theme="light"\]',
        "system light theme": r"@media\s*\(prefers-color-scheme:\s*light\)",
        "desktop TOC collapse": r"@media\s*\(max-width:\s*1300px\)",
        "tablet navigation": r"@media\s*\(max-width:\s*840px\)",
        "mobile layout": r"@media\s*\(max-width:\s*620px\)",
        "narrow mobile layout": r"@media\s*\(max-width:\s*380px\)",
        "scrollable tables": r"\.table-wrap\s*\{[^}]*overflow-x:\s*auto",
        "scrollable code": r"pre\s*\{[^}]*overflow:\s*auto",
        "long heading wrapping": r"\.docs-content h1\s*\{[^}]*overflow-wrap:\s*anywhere",
        "stacked comparison blocks": r"\.code-compare\s*\{[^}]*grid-template-columns:\s*1fr",
    }
    for label, pattern in css_requirements.items():
        if not re.search(pattern, css, re.DOTALL):
            failures.append(f"assets/style.css: missing {label}")

    script = (ROOT / "assets" / "script.js").read_text(encoding="utf-8")
    for label, token in {
        "theme persistence": "sharp-runtime-theme",
        "mobile navigation state": "aria-expanded",
        "documentation navigation toggle": ".docs-toggle",
        "runtime heading anchors": ".docs-content h2[id]",
        "code copy controls": "copy-button",
    }.items():
        if token not in script:
            failures.append(f"assets/script.js: missing {label}")

    print(f"Generated HTML pages inspected structurally: {len(html_files)}")
    print(f"Long-form TOC coverage: {toc_pages}/{long_pages}")
    print(f"Anchored documentation headings: {heading_ids}/{headings}")
    print(f"Responsive table wrappers: {wrapped_tables}/{tables}")
    print(f"Scrollable code blocks represented: {pre_blocks}")
    print(f"Theme/responsive CSS requirements: {len(css_requirements)}/{len(css_requirements)}")
    print(f"Presentation audit errors: {len(failures)}")
    for failure in failures:
        print(f"error: {failure}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

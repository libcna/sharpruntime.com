# Long-form presentation QA — second pass

Date: 2026-08-12

The second pass preserved the first redesign's visual system and extended its
long-form reading behavior. Static presentation checks are reproducible with:

```bash
python3 tools/audit_presentation.py
```

The final generated output reports:

```text
Generated HTML pages inspected structurally: 128
Long-form TOC coverage: 19/19
Anchored documentation headings: 803/803
Responsive table wrappers: 154/154
Scrollable code blocks represented: 160
Theme/responsive CSS requirements: 11/11
Presentation audit errors: 0
```

The audit verifies the default dark palette, explicit and system-selected light
palette, desktop/tablet/mobile/narrow-mobile breakpoints, sticky desktop TOCs,
collapsed mobile documentation navigation, long-heading wrapping, horizontally
scrollable tables and code, stacked mobile comparison blocks, theme persistence,
navigation state, runtime heading links, and copy controls.

## Representative-page review set

The source/DOM review covered the homepage, architecture, API index, generated
IO and Net.Http component inventories, runtime overview, type system, String
class and internals, Array internals, I/O hub, streams, filesystem,
FileSystemWatcher, threading, the porting guide, contributor feature guide,
known limitations, array/span and networking tutorials, search, and mobile
navigation/theme code.

## Screenshot-rendering limitation

The in-app browser runtime exposed no available browser in this environment, so
desktop/tablet/mobile screenshots and manual dark/light rendered inspection
could not be performed. No alternate browser automation was substituted. This
is recorded explicitly rather than presenting static DOM/CSS inspection as
rendered visual evidence. The representative matrix still requiring a browser
is:

- homepage, architecture, API index, component catalogue, porting guide,
  FileSystemWatcher, table-heavy API inventory, long tutorial, and search;
- desktop, tablet, and mobile widths;
- dark and light themes.

All machine-verifiable layout prerequisites pass, but screenshot QA remains an
environmental follow-up.

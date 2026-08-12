# Maintaining sharpruntime.com

This repository publishes a dependency-light static site. The generated HTML is committed so
GitHub Pages can serve it directly; Python's standard library is the only build requirement.

## Update the site

1. Point the component synchronization step at the intended Sharp Runtime checkout:

   ```bash
   python3 tools/sync_components.py --runtime ../sharp-runtime
   ```

2. Update the pinned SHA and measured verification baseline in `data/site-facts.json`, then
   revise evidence-based prose in `tools/build_site.py` when the source-of-truth revision changes.
3. Regenerate and validate:

   ```bash
   python3 tools/build_site.py
   python3 tools/validate_site.py --runtime ../sharp-runtime
   ```

`data/components.json` is generated from Sharp Runtime's checked
`docs/ComponentCatalog.md`; do not hand-edit its component list. `tools/build_site.py` is the
canonical page registry and generates the shared shell, metadata, search index and sitemap.

## Invariants

- Every canonical content page is in `search-index.json` and `sitemap.xml` exactly once.
- `search.html` and `404.html` are useful utilities but are `noindex` and excluded from both.
- Every physical component appears in the catalogue and its canonical name is searchable.
- Internal links and fragments resolve without a server-side rewrite.
- Canonical/OG/structured-data/sitemap URLs use `https://sharpruntime.com/`.
- Human-facing prose uses “Sharp Runtime”; `sharp-runtime` is reserved for repository, path and
  command identities.

## Source discipline

Do not copy mutable facts from README summaries without corroboration. Prefer current
implementation, CMake registration, generated component metadata, tests and measured gate
results. If suite discovery and the most recent controlled outcome come from adjacent revisions,
publish them separately rather than inferring a result that was never measured.

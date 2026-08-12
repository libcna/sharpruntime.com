# Documentation content recovery audit

This audit prevents the generated website from becoming visually polished but
technically shallow. It records what happened to every substantive `h2` and
`h3` in the last pre-redesign website and requires an intentional disposition
for each topic.

The inventory is a preservation ledger, not a claim that the old prose was
correct. Every recovered technical statement must still be checked against the
newly selected Sharp Runtime source pin.

## Immutable comparison points

| State | Revision | Role |
|---|---|---|
| Pre-redesign website | `22d1d1f69de7bdc6a5096493e630c83acba92571` | Historical content-coverage baseline |
| First redesigned website | `e76d0450eaafaffda8c5c47c7ca13a56454703cd` | Presentation and generator baseline |
| Initial repository commit | `52f479721d2c5ca5e522582dd693f21cfb7d9531` | Contains only `CNAME`; not a documentation baseline |

The repository has no other pre-redesign content commit on its local branches.
The ledger therefore reads `22d1d1f` directly with `git show`; it does not rely
on memory, a mutable checkout, or the current generated pages as evidence of
what used to exist.

## Reproducible depth measurements

`python3 tools/content_metrics.py` reads the immutable revisions with
`git show`, parses visible text inside `main`, normalizes whitespace, and uses
the same whitespace-token count for all three editions. It reports two views:

- **visible main** preserves the historical review's approximate method. It
  includes anything visibly nested in `main`; after the redesign that includes
  repeated documentation navigation;
- **chrome-free substantive** additionally excludes documentation sidebars,
  in-page TOCs, breadcrumbs, page metadata, search placeholders, and
  previous/next controls. This is the more useful cross-layout content metric.

Both are diagnostics rather than quality thresholds:

| Measurement | Pre-redesign | First pass | Second pass |
|---|---:|---:|---:|
| Generated HTML pages | 51 | 72 | 128 |
| Visible-main words | 21,150 | 17,830 | 75,954 |
| Visible-main median | 415 | 228.5 | 351 |
| Chrome-free substantive words | 20,854 | 11,614 | 59,933 |
| Chrome-free median | 408 | 134.5 | 224 |
| Tutorial pages, excluding the index | 4 | 14 | 26 |

The first-pass visible-main figure therefore understated the collapse: its
repeated sidebar supplied roughly 6,200 of the words. On the 51 historical
URLs, chrome-free text fell from 20,854 to 7,373 words, a loss of 13,481 words
or 64.6%. The 21 newly added pages supplied 4,241 substantive words.

Among those 51 existing URLs under the chrome-free method:

- 48 became shorter and only three became longer;
- 40 fell to half their old size or less;
- 33 fell to one third or less;
- their median fell from 408 to 114 words;
- pages below 200 words rose from six to 40;
- baseline `h2`/`h3` headings totalled 473, while the first pass had only 228
  across all 72 pages.

The largest losses included array internals, String internals, the String and
EventHandler class pages, the porting guide, API discovery, runtime overview,
the Array and Nullable class pages, the contributor feature workflow,
component/module reference, I/O, type system, and architecture.

## Disposition ledger

[`content-disposition.csv`](content-disposition.csv) groups related historical
headings where they share the same validity assessment, destination, action,
and rationale. Every historical `h2` and `h3` is named exactly as it appeared
at the baseline revision.

The action vocabulary is intentionally small:

| Action | Meaning |
|---|---|
| `retain-adapt` | The topic remains useful; preserve it with current terminology and source verification. |
| `expand` | The topic is sound or necessary but the first pass became materially incomplete. |
| `rewrite` | Preserve the subject but replace stale, misleading, contradictory, or overbroad claims. |
| `replace-generated` | Preserve discovery value while deriving volatile names, types, paths, targets, or relationships from source metadata. |
| `move-cross-link` | Another current page is the better owner; keep a useful route from the historical URL. |
| `intentional-remove` | Remove the specific old claim or private mechanism for a documented reason. This does not authorize removal of the surrounding technical subject. |

Destinations are current generated HTML paths. Multiple destinations use
` || ` as a separator. Grouped old headings use the same separator. An
intentional removal uses `-` as its destination.

## Important recovery priorities

### Architecture and runtime model

Recover the namespace map, logical-versus-physical component model, dependency
closure, target naming, public/private/test edges, build and test topology,
platform abstraction, external dependency ownership, native object/value
distinction, exception model, and deliberate non-goals. Do not restore the old
40-component count, C++17 wording, universal `Object` inheritance, or the claim
that C++ exceptions equal .NET exceptions.

### API and class discovery

The old API page provided useful namespace and type discovery even though its
status badges drifted. Replace that hand-maintained inventory with generated
namespace, type, header, and physical-component mappings. Curated pages should
then explain purpose, compatibility, behavioral reductions, tutorials, and
important limitations. Generated declarations and curated explanation must
remain visibly distinct.

### Strings, arrays, and the type system

Restore representation, ownership, copying, mutation, lifetime, invalidation,
bounds, encoding units, conversion, equality, hashing, culture, nullable,
interfaces, casts, values, wrappers, and reflection boundaries. The old tables
are useful starting topic lists, but blanket null-to-empty mappings and claims
that string or array indexing is the same as C# must be rewritten.

### I/O and concurrency

Restore streams, concrete stream types, readers and writers, binary I/O,
filesystem helpers and metadata, buffers, RandomAccess, compression, hashing,
isolated storage, platform semantics, synchronization, cancellation, tasks,
timers, channels, and callback lifetime. FileSystemWatcher was absent from the
old page and requires new source-audited documentation because it became a
material remediation area after the first website source pin.

### Porting and contributor workflows

Recover real before-and-after C#/C++ transformations, ownership decisions,
properties, interfaces, events, collections, nullable values, exceptions,
tasks, strings, and filesystem behavior. Restore the contributor sequence from
contract selection through ownership, implementation, dependencies, tests,
negative consumers, boundary validation, catalogue regeneration, local gates,
examples, and documentation.

## Intentional removals

The ledger intentionally removes or replaces claims rather than silently
dropping their topics. Significant examples are:

- stale volatile values such as 40 components, 983 headers, and 369 test
  sources;
- hand-authored Todo, Stub, Partial, Implemented, Done, and Verified maturity
  labels used as if they were measured project status;
- the private `plan.sqlite3` and `prompt.md` workflow;
- binary platform badges and the assumption that macOS behavior is simply the
  same as Linux;
- universal `Object` inheritance;
- “C++ Exceptions = .NET Exceptions” and “exception handling works the same”;
- blanket null-string-to-empty and null-array-to-empty conventions;
- the stale C++17 statement;
- unsupported completeness claims such as Decimal having “full arithmetic” or
  URI providing “full URL parsing” without current behavioral evidence;
- isolated storage described as a security sandbox;
- unverified adoption or consumer-specific implementation lists;
- obsolete visual chrome, metadata, navigation, and hand-copied volatile
  catalogues.

These removals do not justify terse replacements. For example, removing an
unsafe null-to-empty rule requires a better explanation of `std::string`,
`std::optional`, pointer absence, and API-specific contracts.

## Automated audit

Run:

```bash
python3 tools/audit_content.py
```

The script is read-only with respect to Git history. It:

- enumerates all baseline HTML documents;
- extracts every historical `h2` and `h3`;
- requires exact coverage in the CSV, including grouped rows;
- rejects unknown or duplicate historical headings;
- validates the action vocabulary;
- requires non-removal rows to name existing generated HTML destinations;
- permits `-` only for intentional removals;
- rejects unsafe destination paths.

It deliberately does not require a raw word-count increase or a lexical match
between old and new headings. Those checks reward filler and punish legitimate
rewrites. The CSV supplies the human semantic decision; the script proves that
no historical section disappeared without one.

## Completion use

Before release, re-run the audit after generation and review every
`intentional-remove` row. Then perform a qualitative check of the high-risk
destinations: architecture, API discovery, runtime overview, type system,
String class and internals, Array class and internals, I/O, porting C# code,
adding runtime features, component families, and the practical tutorials.

Passing this audit means coverage decisions are complete. It does not by
itself prove that recovered prose is accurate, sufficiently deep, or pleasant
to read; source verification, example compilation, site validation, search
coverage, and visual QA remain separate release gates.

# Sharp Runtime website source audit — second pass, 2026-08-12

This ledger records the source-selection, ancestry, implementation, test and platform evidence
used by the second website remediation. It is maintainer evidence, not a public promise that every
API matches .NET. The Sharp Runtime user worktrees and libcna.com remained read-only. The selected
source was materialized only in an isolated temporary checkout for inspection.

The first website redesign pinned `develop` at `f827a6c5349234d5ac938886788ed8eca8fe1c10`.
That revision and its published 16,341-discovered / 16,310-measured facts are historical below;
they are not the current site status. The later 17,057 / 38 checkpoint is also historical: six
subsequent commits added 74 tests before the selected tip.

## Final Sharp Runtime source pin

| Field | Evidence |
|---|---|
| Selected SHA | `6d429559ce265daa21866f0d6e82c5642e2ba0ec` |
| Selected ref | `refs/heads/claude/core-audit-findings-triage-02tydm` |
| Commit timestamp | `2026-08-12T12:08:37Z` |
| Commit subject | `fix(io): a FileSystemWatcher handler could no longer stop its own watcher (#2347)` |
| Previous website SHA | `f827a6c5349234d5ac938886788ed8eca8fe1c10` |
| Main Sharp Runtime checkout HEAD | `f827a6c5349234d5ac938886788ed8eca8fe1c10` (`develop`) |
| Local `develop` | `f827a6c5349234d5ac938886788ed8eca8fe1c10` |
| Local and remote-tracking `origin/develop` | `f827a6c5349234d5ac938886788ed8eca8fe1c10` |
| Remote `develop` | `f827a6c5349234d5ac938886788ed8eca8fe1c10` |
| Second worktree HEAD / local `next` / `origin/next` | `6c7632657116fdbe64c91b0f2250f6b8ac755b48` |
| `master` | `a61468160a819cabe2d8d639f0ceed7b36fa2d34` |
| Merge base with previous website SHA | `a284b6e4d5f8d41e055fccf7a55feb47b0446f28` |
| Checkout state | Both user Sharp Runtime worktrees clean; `git status --short` emitted nothing |

`git ls-remote --heads origin` was checked at discovery and again after the delta audit. The remote
tip stayed at `6d429559...`. `NEXT.md` identifies
`claude/core-audit-findings-triage-02tydm` as the harness-designated branch. This is stronger
evidence of intended current work than assuming `develop` is automatically authoritative.

### Worktrees and ancestry

The user worktrees were:

- `/rv/data/development/github.com/openeggbert/sharp-runtime` — `develop` at `f827a6c...`;
- `/rv/data/development/github.com/openeggbert/sharp-runtimenext` — `next` at `6c763265...`.

The selected tip is a direct descendant of `next`:

```text
merge-base(next, selected) = 6c7632657116fdbe64c91b0f2250f6b8ac755b48
next...selected            = 0 next-only / 32 selected-only commits
```

The previous website SHA and selected tip have divergent integration topology:

```text
merge-base(f827a6c, selected) = a284b6e4d5f8d41e055fccf7a55feb47b0446f28
f827a6c...selected            = 2 old-only / 122 selected-only commits
```

Neither is an ancestor of the other. The two old-only commits are the `f827a6c...` merge and the
`bc5ddafe...` develop-side i686 stabilization lineage. The selected branch follows the merge's
`a284b6e4...` remediation parent and adds 122 selected-only commits. It is therefore the newest
intended remediation state, but it is not a strict integration superset of `develop`.

### Important integration caveat: i686

The selected tree does not contain the develop-only `FINAL-STAB-001` i686 integration that the
old website SHA carried. A tree comparison shows the selected pin lacks:

- `SHARP_RUNTIME_BUILD_I686_REGRESSION` and the native-`__int128` CMake capability probe;
- propagation of `SHARP_RUNTIME_HAS_NATIVE_INT128` through the shared headers target;
- conditional removal of `Decimal.cpp` on compilers without native 128-bit integers;
- `cmake/toolchains/mingw-w64-i686.cmake`;
- `tests/Platform/SharpRuntimeI686CompileBoundary.cpp`.

The website must not blend these two histories. It may describe older MinGW library-build evidence,
but it must not claim that the selected SHA includes or passed the develop-only i686 regression.

## Current canonical facts

| Topic | Current pinned fact | Source discipline |
|---|---:|---|
| Physical components | 41 | Current CMake registration and generated catalogue |
| Direct production dependency edges | 92 | Generated catalogue and boundary metadata |
| Compatibility surface | `Core`, `Collections`, `Xml.XPath`, plus `All` aggregate | Current component catalogue |
| Public module headers | 1,036 | Tracked-tree inventory at selected SHA |
| Production translation units | 218 | Tracked module-source inventory at selected SHA |
| Current discovered test cases | 17,131 | Selected source/test discovery; kept distinct from historical checkpoints |
| Test executables | 38 | 37 component executables plus one integration executable |
| Latest measured full gate | 17,131 run; 17,123 passed; 2 skipped; 6 failed | `CLAUDE.md` full-gate chain through #2347 |
| Language mode | C++23, extensions off | Root `CMakeLists.txt` |
| Minimum CMake | 3.20 | Root `CMakeLists.txt` |

The six measured failures were not hidden, disabled or recategorized:

- five `PingTests` associated with #1962 and raw-ICMP availability in the measurement environment;
- `SocketTests.Connect_ByHostname_NoMatchingAddressFamily_Throws`, which needs usable IPv6 in
  that environment.

The gate is not green and is not described as green.

### Local second-pass validation

The selected detached checkout configured successfully with CMake 3.31.6 and GNU C++ 14.2.0,
`SHARPRUNTIME_COMPONENTS=All`, and tests enabled. A full local build was stopped at approximately
20% after the user requested conservative RAM use; it is not represented as a completed gate.

The directly relevant I/O target was then built with exactly one compiler job:

```bash
cmake --build /tmp/sharp-runtime-site-gate-build \
  --target SharpRuntimeTests_IO --parallel 1
```

The following current-source test slice ran successfully:

```bash
SharpRuntimeTests_IO \
  --gtest_filter='WatcherReconfigurationFixture.*:FileSystemWatcherTests.*'
```

Result: **42 run / 42 passed / 0 skipped / 0 failed**. This covers the 26 current reconfiguration
and reentrancy cases plus 16 baseline FileSystemWatcher cases. It is targeted local evidence, not a
replacement for the separately recorded 17,131-case full gate.

### Test-count provenance

The previous website displayed 16,341 currently discovered cases and an older measured gate of
16,310 run / 16,303 passed / 1 skipped / 6 failed across 37 executables. Those numbers describe
the old `f827a6c...` audit and remain only as historical evidence.

The 17,057 / 38 checkpoint in the current `NEXT.md` header is also historical. The selected-tip
`CLAUDE.md` records the later complete gate, and the intervening test increments reconcile exactly:

| Change | Increment | Running total |
|---|---:|---:|
| Historical #2104 checkpoint | — | 17,057 |
| #2084 XML DOCTYPE validation | +11 | 17,068 |
| #2085 XML embedded-NUL rejection | +4 | 17,072 |
| #2200 XML.Linq DOCTYPE direct door | +18 | 17,090 |
| #2201 XML.Linq embedded-NUL rejection | +18 | 17,108 |
| #2350 XML.Linq name validation | +15 | 17,123 |
| #2347 FileSystemWatcher reentrancy | +8 | 17,131 |

The 38th executable is `SharpRuntimeTests_IO_IsolatedStorage`, introduced by the isolated-storage
remediation batch. Discovery and measured execution are separate concepts even when their totals
currently agree.

## Delta from the previous website source

The exact tree comparison is:

```text
git diff --stat f827a6c5349234d5ac938886788ed8eca8fe1c10..6d429559ce265daa21866f0d6e82c5642e2ba0ec
336 files changed, 41564 insertions(+), 1244 deletions(-)
```

Because the histories diverge, `git log f827a6c..selected` enumerates 122 selected-only commits;
it must not be described as a 122-commit fast-forward from `develop`. The detailed public-impact
classification is in [`source-delta-matrix.csv`](source-delta-matrix.csv).

Material groups include:

- TimeZone year-scoped standard-offset and identifier handling;
- Ping exception preservation, synchronous argument rejection and descriptor ownership;
- XML and XML.Linq namespace, lexical, NUL, DOCTYPE and name validation;
- isolated-storage confinement, disposed-state enforcement and exception mapping;
- Array, Span, Memory, Buffer and ArraySegment safety and overlap behavior;
- String search bounds, UTF-8 validation, Unicode whitespace and Base64 grammar;
- numeric special values, rounding, checked arithmetic and bounded parsing;
- Lazy, Environment, AppDomain, Activator, Delegate, Version and exception contracts;
- recursive `Monitor::Wait` and POSIX signal lifetime/descriptor fixes;
- FileStream closed-state enforcement and FileSystemWatcher reconfiguration/remediation.

No material production implementation change in this range justifies advertising new HTTP,
socket, task or collection capability. Several such test trees changed only to remove invalid
hash-collision assumptions or strengthen existing contracts.

## FileSystemWatcher disposition

The post-`f827a6c` self-join/termination warning is fixed at the selected tip; it is not a current
limitation.

Before #2347, all three reconfiguring members could reach an unconditional join from the watcher
thread. A handler that disabled or reconfigured its own watcher self-joined, threw
`std::system_error`, and could reach `std::terminate` because handler dispatch had no exception
boundary.

Current behavior at `6d429559...` is:

- `EnableRaisingEvents = false` from a handler is permitted with deferred teardown;
- the loop exits after the handler returns and an external operation or destructor reaps it;
- live `Path` or `NotifyFilter` changes from a handler throw `InvalidOperationException` and leave
  the watcher unchanged;
- reconfiguration from another thread continues to work;
- handler exceptions are delivered to `Error` handlers;
- an exception from an `Error` handler is swallowed to avoid recursion;
- watcher-thread identity uses a `thread_local` marker rather than racing on `std::thread` state;
- `enabled_` and `selfStopPending_` are atomic;
- the commit records unchanged size/alignment, five caught mutations and five clean TSan harness
  runs;
- eight deterministic tests cover self-disable, re-enable, rejected in-handler reconfiguration,
  external reconfiguration, error routing and destruction after self-stop.

Other post-pin watcher work is also current: changing `Path` retires and re-arms the inotify watch
without racing on the path string, and `NotifyFilter` now separates name-class events from
content-class events instead of admitting everything.

Current watcher limitations are narrower and evidence-based:

- the backend is Linux/inotify only; enabling events throws on other platforms;
- `IncludeSubdirectories` is stored but has no effect;
- mapping *within* each `NotifyFilters` class remains undecided (#2346);
- the already-running-handler lifecycle question remains explicitly deferred (#2105).

## Platform evidence at the selected pin

| Platform/toolchain | Evidence level | Honest website wording |
|---|---|---|
| Linux/GCC | Current native build/full-gate evidence; six known failures | Primary measured platform, non-green gate |
| Linux/Clang | Source portability paths exist; no selected-tip full-gate record inspected | Source/build support, not equivalent test evidence |
| Windows/MinGW | Earlier post-component `All` and selective `Text.Json` library cross-builds; no runtime gate | Cross-compile evidence only |
| Windows/MSVC | Build logic exists, but `Decimal`, `Int128` and `UInt128` require GCC/Clang native 128-bit extensions | Compiler-limited; not a first-class verified target |
| macOS/Apple Clang | Downstream Xcode 15.4 build evidence; no repository full standalone gate | Downstream-build evidence only |
| Emscripten | Earlier `All` and selective `Text.Json` library cross-builds; no browser/runtime gate | Cross-compile evidence plus explicit runtime limits |
| Android | `Storage` can privately use a parent-provided SDL3 target | Storage integration path only; no whole-project device claim |

Selected-source platform-limited areas include Linux-only `FileSystemWatcher` and network-interface
enumeration, POSIX-only process/signal operations, and Emscripten runtime rejection for sockets and
random-access operations. Compile support and runtime implementation must remain separate in the
website matrix.

## Current source-document contradictions

Implementation, CMake, generated metadata and measured test evidence take precedence over the
following prose:

1. `CLAUDE.md` records 17,131 / 38 at the selected tip; the top of `NEXT.md` still records the
   earlier 17,057 / 38 checkpoint.
2. The top of `NEXT.md` still presents #2347 as newly open and not implemented, although the
   selected commit is the #2347 fix.
3. `README.md` reports 16,406 / 37 near its introduction and 13,538 tests in its platform table.
4. `README.md` and `docs/CMakeComponents.md` say 41 modules / 91 edges; the generated catalogue
   says 41 / 92.
5. `README.md` says the full build/test gate passes, while current evidence records six failures
   and explicitly says the gate is not green.
6. `README.md` describes ten selective jobs; the tracked GitHub workflow contains nine matrix
   entries. The local script and hosted workflow are different scopes.
7. `FileSystemWatcher.hpp`'s class documentation says non-Linux enabling throws, matching the
   implementation; a later property comment says the flag is merely tracked on unsupported
   platforms. The implementation and class-level contract are authoritative.
8. The selected remediation branch omits `develop`'s i686 integration. Combining claims from the
   two trees would create a platform result no single pinned revision has.
9. `README.md` still contains the path typo `sharp-runtimervc`; the repository and CMake examples
   establish `sharp-runtime`.

## Current limitations retained from the delta audit

These are current implementation boundaries, not a dump of historical ticket text:

- text reader/writer wrappers can remain usable after `Close()` pending the object-layout decision;
- `BinaryData` invalid-UTF-8 and copy-versus-alias semantics remain explicitly deferred;
- isolated storage has a residual time-of-check/time-of-use race, and the separately constructed
  `IsolatedStorageFileStream` path remains outside the new confinement resolver;
- XML non-NUL control-character policy and an internal-subset serialization edge remain decision
  boundaries;
- `Lazy` retains its documented `PublicationOnly` recursion divergence;
- concrete delegate-type preservation/mismatch rejection remains a design decision;
- `CharUnicodeInfo` is now locale-stable for the repaired domain but does not claim a complete CLR
  Unicode database;
- the native runtime still has no CLR, JIT, garbage collector, full reflection, TLS stack or full
  managed scheduler semantics.

## Historical first-pass record

The first redesign's source pin was `f827a6c...` on `develop`. Its site audit established useful
infrastructure and several facts that remain valid: 41 physical components, 92 production edges,
CMake 3.20+, C++23, a generated component catalogue, explicit TLS/reflection boundaries and
evidence-tiered platform wording. It also compiled the following temporary consumers against that
historical pin:

| Historical example | Historical result at `f827a6c...` |
|---|---|
| Minimal console consumer | Configured, compiled and ran |
| Selective JSON + hashing closure | Configured and compiled |
| `vector<int>` JSON round trip | Compiled and ran |
| XML LINQ parse/navigation | Compiled and ran |
| CRC-32 check vector | Compiled and ran |
| Cooperative task cancellation | Compiled and ran |
| Synchronous plain-HTTP shape | Compiled and linked; not executed |

Those results are preserved as historical evidence only and were not silently promoted to the
selected `6d429559...` pin. The source-pin/delta investigation itself was read-only; the
coordinator subsequently performed the targeted local I/O validation recorded above and the
separate current example verification.

## Reproduction commands

The source decision was based on the following read-only evidence commands plus direct code/test
inspection:

```bash
git status --short
git branch -vv
git log --oneline --decorate --graph --all -n 100
git worktree list --porcelain
git for-each-ref --sort=-committerdate
git ls-remote --heads origin
git merge-base <left> <right>
git merge-base --is-ancestor <left> <right>
git rev-list --left-right --count <left>...<right>
git log f827a6c5349234d5ac938886788ed8eca8fe1c10..6d429559ce265daa21866f0d6e82c5642e2ba0ec
git diff --stat f827a6c5349234d5ac938886788ed8eca8fe1c10..6d429559ce265daa21866f0d6e82c5642e2ba0ec
git diff --name-status f827a6c5349234d5ac938886788ed8eca8fe1c10..6d429559ce265daa21866f0d6e82c5642e2ba0ec
```

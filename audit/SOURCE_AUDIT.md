# Sharp Runtime website source audit — 2026-08-12

This ledger records the evidence used to generate the current site. It is maintainer evidence,
not a public project-status promise. Sharp Runtime and libcna.com were read-only throughout.

## Pinned revisions

| Repository | Branch | Revision | Starting state |
|---|---|---|---|
| Sharp Runtime | `develop` | `f827a6c5349234d5ac938886788ed8eca8fe1c10` | clean; equals local and `origin/develop` |
| sharpruntime.com | `next` | `22d1d1f69de7bdc6a5096493e630c83acba92571` | clean |
| legacy site | `develop` | `b50e29b9cde40937dcadc5975988cb5b88a12ab5` | clean; content matched target except CNAME |
| libcna.com | `develop` | `af06b626b66062ab3e518dffb8156efbd1e94a12` | clean |

## Canonical fact ledger

| Topic | Old site claim | Verified pinned claim | Confidence / evidence | Website consequence |
|---|---|---|---|---|
| Physical modules | 40 | 41 | High: current CMake registration, boundary validator and generated catalogue | Generated complete catalogue; one canonical value |
| Production edges | not consistently stated | 92 (84 public, 8 private) | High: validator and current generated catalogue | Architecture and component data use 92 |
| Component kinds | incomplete | 30 static, 11 interface | High: CMake registration metadata | Kind shown for every component |
| Public headers | 983 | 1,032 current module public headers | High: tracked-tree inventory | Kept off the homepage; audit-only mutable fact |
| Production sources | incomplete | 217 module production translation units | High: tracked-tree inventory | Audit/development context only |
| Test sources | 369 | 477 component + 9 integration `.cpp` files | High: tracked-tree inventory | Old metric removed from landing pages |
| Test topology | old aggregate descriptions | 36 component executables + 1 integration executable | High: current executable/CMake enumeration | Testing page distinguishes target/executable/case |
| Current discovered cases | older counts | 16,341 | High: current built executables with `--gtest_list_tests` | Displayed as discovered, not “passing” |
| Latest controlled gate | implied green | 16,310 run; 16,303 passed; 1 skipped; 6 failed | High: newest pre-final-TimeZone full gate in `NEXT.md` | Exact qualified result, separate from current discovery |
| CMake / language | mixed old wording | CMake 3.20+, C++23 required, extensions off | High: root CMake | All build snippets use current requirements |
| GitHub CI | broad/incomplete prose | Ubuntu: 9 selective jobs, full local gate, Doxygen baseline | High: current workflow | No invented Windows/macOS/web CI |
| Linux | broad supported claim | primary native validation; qualified full-gate result | High | Evidence label rather than binary badge |
| MinGW | partial Windows | library-only All/Text.Json cross-compile evidence | Medium-high: recorded build evidence and source paths | “Cross-compile verified”; no test claim |
| MSVC | partial Windows | source/build logic exists; native-128 surface constrained; no current CI/runtime result | High for constraint | Compiler-limited label |
| macOS | same as Linux | downstream Xcode 15.4 build evidence; no standalone full gate | Medium-high | Downstream-build label |
| Emscripten | partial/compiles cleanly | library cross-build evidence; no browser tests; API limitations | High | Cross-compile + runtime-limit wording |
| Android | SDL-oriented broad implication | Storage-specific parent-SDL path; no whole-project device result | High | Storage integration path only |
| HTTP/TLS | vague networking support | plain buffered HTTP/1.1 over TCP; no HTTPS/TLS | High: implementation | Explicit security boundary |
| WebSockets | generic support | RFC6455 `ws://`; `wss://` throws | High: implementation/tests | Explicit in component/tutorial/limitations pages |
| Cryptography | broad label risk | digests, HMAC, HKDF, PBKDF2 and OS random; no encryption/certs/TLS | High: headers/implementations | Capability list separated from exclusions |
| Reflection | old reflection page | minimal type identity; no member metadata/dynamic invocation | High: `Type`, `Activator`, `Delegate` implementation | Rewritten concept page |
| Ownership | shallow RAII claim | native RAII plus smart ownership and non-owning views/raw-return exceptions | High: headers | Dedicated guide avoids “all automatic” claim |

## Meaningful source-document contradictions

1. `README.md` reports an old passing test baseline, while `NEXT.md` records a newer non-green
   controlled gate and the final TimeZone commits add another 31 passing cases. Current
   executables discover 16,341; no post-merge whole-gate pass total is inferred.
2. `README.md` and `docs/CMakeComponents.md` say 41 modules / 91 edges. The current generated
   catalogue and independent boundary validator say 41 / 92; the newer private edge is
   `Net.Http.Headers -> Net`.
3. `docs/CMakeComponents.md` gives an obsolete 12,681-test baseline and says the hosted workflow
   runs ten selective jobs. The current workflow has nine; the local default script has ten.
4. The README quick-start path contains `sharp-runtimervc`; CMake examples and the real repository
   prove `sharp-runtime`.
5. `NEXT.md` identifies the pre-merge remediation branch and 16,310-case gate. Pinned `develop`
   contains the final TimeZone fixes and merge, so `NEXT.md` is itself one unit behind HEAD.
6. The TimeZone header still describes a POSIX-only/current-offset surface even though current
   implementation has Windows and POSIX branches. It remains a reduced fixed-current-offset model,
   so the website documents both the newer platform path and the remaining semantic reduction.
7. The audit index still marks TimeZone findings 224–227 confirmed, but merged implementation,
   tests and commits fix their output clearing, factory validation, adjustment-rule validation and
   identity behavior. They are not published as current limitations.
8. Task prose describes a thread pool, while the implementation uses eager `std::async`; the
   ThreadPool compatibility type itself launches detached threads rather than enforcing its stored
   worker limits. Public wording avoids promising a managed scheduler.
9. Some Text/JSON/XML README comments describe older stubs or missing span types. Current headers
   and implementations provide more behavior, with explicit Unicode, serialization and XPath
   reductions documented instead.
10. The Doxygen job is not warning-free. It pins Doxygen 1.9.8 and enforces a ceiling of 1,942
    warnings; the website calls it warning-baseline drift protection.

## Public limitation curation

The public Known Limitations page includes high-impact behavior: managed-runtime non-goals,
Unicode/globalization reductions, fixed-offset time zones, TLS absence, async lifetime hazards,
isolated-storage non-confinement, Linux/POSIX-only APIs, Emscripten pthread constraints and the
native-128 compiler boundary. Internal ticket identifiers and fixed historical findings are not
dumped into user documentation.

## Consumer-example validation

Temporary CMake consumers were built against the pinned checkout with CMake 3.20, C++23,
tests disabled and at most two parallel build jobs.

| Published example | Target | Result |
|---|---|---|
| Minimal console consumer | `SharpRuntime::Console` | configured, compiled, ran; printed `Hello from native C++23.` |
| Selective JSON + hashing closure | `SharpRuntime::Text.Json`, `SharpRuntime::IO.Hashing` | configured and compiled |
| `vector<int>` JSON round trip | `SharpRuntime::Text.Json` | compiled, ran; printed `[3,7,11]` |
| XML LINQ parse/navigation | `SharpRuntime::Xml.Linq` | compiled, ran; printed `Sharp Runtime` |
| CRC-32 check vector | `SharpRuntime::IO.Hashing` | compiled, ran; printed `cbf43926` |
| Cooperative task cancellation | `SharpRuntime::Threading.Tasks` | compiled, ran; printed `canceled` |
| Synchronous plain-HTTP shape | `SharpRuntime::Net.Http` | compiled and linked; deliberately not executed |

The HTTP tutorial labels that distinction. No external endpoint result is inferred from a
compile/link check.

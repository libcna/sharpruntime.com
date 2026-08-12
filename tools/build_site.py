#!/usr/bin/env python3
"""Generate the maintainable shared shell and discovery files for sharpruntime.com."""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://sharpruntime.com/"
FACTS = json.loads((ROOT / "data" / "site-facts.json").read_text(encoding="utf-8"))
SOURCE_SHA = FACTS["source_sha"]
LASTMOD = FACTS["evidence_date"]


@dataclass
class Page:
    path: str
    title: str
    description: str
    category: str
    body: str
    tags: list[str] = field(default_factory=list)
    indexable: bool = True
    page_type: str = "TechArticle"


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def code(value: str, language: str = "cpp") -> str:
    return f'<pre><code class="language-{e(language)}">{html.escape(value)}</code></pre>'


def callout(title: str, content: str, kind: str = "note") -> str:
    cls = "callout" if kind == "note" else f"callout callout--{kind}"
    return f'<div class="{cls}"><div class="callout-title">{title}</div>{content}</div>'


def table(headers: list[str], rows: list[list[str]], cls: str = "") -> str:
    heads = "".join(f"<th scope=\"col\">{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<div class="table-wrap"><table class="{e(cls)}"><thead><tr>{heads}</tr></thead><tbody>{body}</tbody></table></div>'


def bullets(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def cards(items: list[tuple[str, str, str, str]]) -> str:
    return '<div class="cards">' + "".join(
        f'<a class="card" href="{href}"><span class="card-kicker">{kicker}</span><h3>{title}</h3><p>{desc}</p></a>'
        for kicker, title, desc, href in items
    ) + "</div>"


def page_index(items: list[tuple[str, str, str]]) -> str:
    return '<div class="page-index">' + "".join(
        f'<a href="{href}">{title}<small>{desc}</small></a>' for title, desc, href in items
    ) + "</div>"


GETTING_STARTED_CMAKE = """cmake_minimum_required(VERSION 3.20)
project(hello_sharp_runtime LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(SHARP_RUNTIME_COMPONENTS Console)
set(SHARP_RUNTIME_BUILD_TESTS OFF CACHE BOOL "" FORCE)
add_subdirectory(sharp-runtime)

add_executable(hello main.cpp)
target_link_libraries(hello PRIVATE SharpRuntime::Console)"""

GETTING_STARTED_CPP = """#include <System/Console.hpp>

int main()
{
    System::Console::WriteLine("Hello from native C++23.");
    return 0;
}"""


def intro(title: str, lead: str, labels: list[str] | None = None) -> str:
    meta = ""
    if labels:
        meta = '<div class="page-meta">' + "".join(f"<span>{e(label)}</span>" for label in labels) + "</div>"
    return f"<h1>{title}</h1><p class=\"lead\">{lead}</p>{meta}"


def home_body() -> str:
    return f"""
<section class="hero"><div class="container hero-grid">
  <div class="hero-copy">
    <div class="eyebrow">Familiar APIs. Native C++.</div>
    <h1>Bring practical <span>System.*</span> APIs to C++23.</h1>
    <p class="hero-lead">Sharp Runtime is a componentized native C++ implementation of a practical subset of .NET’s <code>System.*</code> surface—built for source ports that need familiar types and behavior without a managed runtime.</p>
    <div class="hero-actions">
      <a class="button button--primary" href="getting-started.html">Get started</a>
      <a class="button" href="components/index.html">Explore components</a>
      <a class="button" href="https://github.com/openeggbert/sharp-runtime">View on GitHub</a>
    </div>
    <p class="hero-note">MIT licensed · CMake 3.20+ · C++23 · source facts pinned to <code>{SOURCE_SHA[:8]}</code></p>
  </div>
  <div class="terminal" aria-label="Minimal Sharp Runtime consumer example">
    <div class="terminal-bar"><span class="terminal-dot"></span><span class="terminal-dot"></span><span class="terminal-dot"></span><span class="terminal-title">CMakeLists.txt + main.cpp</span></div>
    <pre><code><span class="code-comment"># Select only what this app needs</span>
<span class="code-key">set</span>(SHARP_RUNTIME_COMPONENTS Console)
<span class="code-key">add_subdirectory</span>(sharp-runtime)
<span class="code-key">target_link_libraries</span>(hello PRIVATE
  SharpRuntime::Console)

<span class="code-key">#include</span> &lt;System/Console.hpp&gt;

int main() {{
  System::Console::WriteLine(
    <span class="code-value">"Native. Familiar. Focused."</span>);
}}</code></pre>
  </div>
</div></section>
<section class="stat-strip"><div class="container stats">
  <div class="stat"><span class="stat-value">{{physical_components}}</span><span class="stat-label">physical CMake components</span></div>
  <div class="stat"><span class="stat-value">{{current_test_cases}}</span><span class="stat-label">current discovered test cases</span></div>
  <div class="stat"><span class="stat-value">C++23</span><span class="stat-label">required language standard</span></div>
  <div class="stat"><span class="stat-value">MIT</span><span class="stat-label">open-source license</span></div>
</div></section>
<section class="section"><div class="container">
  <div class="section-heading"><div class="eyebrow">Scope with boundaries</div><h2>A compatibility library—not a CLR.</h2><p>Sharp Runtime preserves useful API organization and porting patterns while remaining ordinary native C++. It does not execute managed assemblies and does not try to reproduce the managed execution environment.</p></div>
  <div class="split">
    <div>{callout("What it provides", bullets(["Native C++ types in familiar <code>System::*</code> namespaces", "Core types, collections, text, JSON, XML, I/O, networking, numerics, threading, tasks, channels and more", "Fine-grained CMake targets with transitive dependency closure", "A pragmatic base for C#/.NET-to-C++ ports and <a href=\"cna-integration.html\">CNA</a>"]), "success")}</div>
    <div>{callout("What it does not provide", bullets(["A CLR, JIT compiler, garbage collector, or managed assembly loader", "General metadata reflection, <code>DynamicInvoke</code>, P/Invoke, remoting, or BinaryFormatter-style serialization", "C# language <code>async</code>/<code>await</code> syntax in C++", "TLS, certificates, <code>SslStream</code>, or <code>wss://</code> transport"]), "warning")}</div>
  </div>
</div></section>
<section class="section section--tint"><div class="container">
  <div class="section-heading"><div class="eyebrow">Practical breadth</div><h2>Use one focused surface—or the complete runtime.</h2><p>Each physical component owns its public headers, implementation, tests and declared dependencies. Request direct needs; CMake enables the dependency closure.</p></div>
  {cards([
    ("Foundation", "Core & collections", "Object and Type, strings and wrappers, arrays and memory, delegates, exceptions, generic, concurrent and observable collections.", "components/core.html"),
    ("Data", "Text, JSON & XML", "Encoding and formatting, StringBuilder, regex, nlohmann-backed JSON, tinyxml2-backed XML and LINQ-style XML.", "components/text-data.html"),
    ("Systems", "I/O & storage", "Streams, files and directories, compression, ZIP, hashing, isolated storage and platform storage paths.", "components/io-storage.html"),
    ("Connectivity", "Networking", "DNS, addresses, sockets, HTTP, headers, HTTP JSON, MIME, network information and WebSockets—with explicit TLS boundaries.", "components/networking.html"),
    ("Concurrency", "Threading & tasks", "Threads, synchronization, cancellation, thread pool, tasks, continuations, channels and timers using native C++ machinery.", "components/concurrency.html"),
    ("Computation", "Numerics & globalization", "Vectors, matrices, quaternion, BigInteger, numeric wrappers, culture data, parsing and formatting—with compiler caveats documented.", "components/numerics-globalization.html"),
  ])}
  <div class="hero-actions"><a class="button button--primary" href="components/index.html">Browse all 41 components</a><a class="button" href="architecture.html">Understand the architecture</a></div>
</div></section>
<section class="section"><div class="container split">
  <div><div class="eyebrow">Verification</div><h2>Evidence, not a vanity counter.</h2><p>The pinned source registers {{test_executables}} test executables and currently exposes {{current_test_cases}} GoogleTest cases. The last controlled full-gate record before the final TimeZone additions ran {{gate_cases}}: {{gate_passed}} passed, {{gate_skipped_words}} and {{gate_failed_words}} for two known network-related causes.</p><p>The repository also validates component boundaries, selective consumers, negative include/link fixtures, catalogue drift, integration behavior and Doxygen warning regressions.</p><a class="button" href="running-tests.html">Read the verification model</a></div>
  <div class="status-list">
    <div class="status-row"><span class="badge badge--verified">Validated</span><span><strong>Component graph</strong><br>{{physical_components}} physical modules and {{production_edges}} declared direct production edges; no allow-list exceptions.</span></div>
    <div class="status-row"><span class="badge badge--verified">Measured</span><span><strong>Current suite shape</strong><br>{{component_test_executables}} component executables plus {{integration_test_executables_words}}.</span></div>
    <div class="status-row"><span class="badge badge--partial">Qualified</span><span><strong>Full gate</strong><br>Five host-triggered Ping failures expose a real fallback gap; one IPv6-interface failure is environmental. Neither is hidden.</span></div>
  </div>
</div></section>
<section class="section section--tint"><div class="container">
  <div class="section-heading"><div class="eyebrow">Portability</div><h2>Platform claims carry evidence labels.</h2><p>The current CI is Linux/Ubuntu. Other platforms have implementation and toolchain paths, but the website distinguishes source support, cross-compile evidence and runtime validation.</p></div>
  {table(["Platform", "Evidence label", "What that means"], [
    ["Linux / GCC", '<span class="badge badge--verified">Primary native validation</span>', "Push/PR jobs target Ubuntu; the last controlled full gate is qualified below rather than described as green."],
    ["Windows / MinGW", '<span class="badge badge--build">Cross-compile verified</span>', "Library-only All and Text.Json cross-build evidence exists; GoogleTest was not built or run."],
    ["Windows / MSVC", '<span class="badge badge--limited">Compiler-limited</span>', "Build logic exists, but native <code>__int128</code>-dependent numeric surfaces constrain current completeness."],
    ["macOS / Apple Clang", '<span class="badge badge--partial">Downstream build evidence</span>', "Xcode 15.4 downstream builds drove fixes; no standalone full-suite result or current macOS CI job exists."],
    ["Emscripten / Web", '<span class="badge badge--partial">Cross-compile verified</span>', "Library-only cross-build evidence exists; DNS and several native facilities are unavailable or reduced, and no browser suite ran."],
    ["Android", '<span class="badge badge--partial">Integration path</span>', "Storage can consume parent-provided SDL3; this audit did not run a device suite."],
  ])}
  <a class="button" href="platform-layer.html">Platform matrix and caveats</a>
</div></section>
<section class="section"><div class="container split">
  <div><div class="eyebrow">Ecosystem</div><h2>The System.* layer under CNA.</h2><p><a href="https://libcna.com/">CNA</a>, the sibling C++23 reimplementation of the XNA 4.0 API, builds on Sharp Runtime for familiar .NET base-library patterns. CNA owns the game framework; Sharp Runtime stays focused on the <code>System.*</code> compatibility layer.</p><a class="button" href="cna-integration.html">How CNA integrates it</a></div>
  <div><div class="eyebrow">Start a path</div><h2>From evaluation to contribution.</h2>{page_index([("Integrate the library", "Build a minimal component consumer.", "getting-started.html"), ("Port C# patterns", "Translate ownership, properties, delegates and errors.", "guides/porting-csharp.html"), ("Choose components", "Understand targets and dependency closure.", "components/index.html"), ("Extend the runtime", "Add APIs and components without breaking boundaries.", "development/adding-runtime-features.html")])}</div>
</div></section>
"""


def build_pages(components: dict) -> list[Page]:
    pages: list[Page] = [
        Page("index.html", "Sharp Runtime — Practical .NET System.* APIs for Native C++23", "Sharp Runtime is a componentized C++23 implementation of a practical subset of .NET System.* APIs for native source ports.", "Home", home_body(), ["c++23", ".net", "system", "native", "cmake"], page_type="SoftwareSourceCode"),
    ]

    pages.extend(core_pages())
    pages.extend(component_pages(components))
    pages.extend(tutorial_pages())
    pages.extend(reference_pages())
    replacements = {
        "{{current_test_cases}}": f"{FACTS['current_test_cases']:,}",
        "{{test_executables}}": str(FACTS["test_executables"]),
        "{{component_test_executables}}": str(FACTS["component_test_executables"]),
        "{{integration_test_executables_words}}": "one integration executable",
        "{{gate_cases}}": f"{FACTS['last_controlled_gate']['cases']:,}",
        "{{gate_passed}}": f"{FACTS['last_controlled_gate']['passed']:,}",
        "{{gate_skipped_words}}": "one skipped",
        "{{gate_failed_words}}": "six failed",
        "{{timezone_additions}}": str(FACTS["post_gate_timezone_additions"]),
        "{{physical_components}}": str(components["physical_count"]),
        "{{production_edges}}": str(components["direct_production_edges"]),
    }
    for page in pages:
        for placeholder, value in replacements.items():
            # Most page bodies are ordinary strings. The homepage is an f-string,
            # so its doubled braces are reduced once before this pass.
            page.body = page.body.replace(placeholder, value).replace(placeholder[1:-1], value)
    return pages


def core_pages() -> list[Page]:
    return [
        Page("overview.html", "What is Sharp Runtime?", "Goals, non-goals, audiences and verified scope of the Sharp Runtime C++23 compatibility library.", "Overview", intro("What is Sharp Runtime?", "A native C++23 library that implements a practical, porting-oriented subset of .NET’s System.* APIs.", ["Concept", "5 minute read", f"Source {SOURCE_SHA[:8]}"]) + """
<h2 id="purpose">Purpose</h2><p>Sharp Runtime exists to make C# and .NET source ports more direct. It provides recognizable namespace and type organization, useful behavioral compatibility and native implementations for areas commonly needed by framework and game ports. CNA is its principal verified consumer.</p>
<h2 id="audiences">Who it serves</h2>""" + bullets(["C++ developers evaluating a focused System.* compatibility layer", "Teams porting C# libraries, frameworks or games to native C++", "CNA contributors and direct Sharp Runtime consumers", "Contributors implementing APIs, component boundaries and portability behavior"]) + """
<h2 id="non-goals">Deliberate non-goals</h2>""" + bullets(["It is not a CLR, JIT, garbage collector or managed assembly loader.", "It does not execute arbitrary .NET binaries.", "It does not supply general reflection, DynamicInvoke, P/Invoke, remoting or BinaryFormatter infrastructure.", "It does not make C# language syntax—including async/await—available in C++."]) + callout("Compatibility is scoped", "<p>Matching a name does not guarantee every overload or every edge-case behavior. Use the component and limitation pages to distinguish implemented, partial, platform-limited and deliberately excluded surfaces.</p>", "warning") + """
<h2 id="verified-scope">Verified project shape</h2>""" + table(["Fact", "Pinned result", "Evidence"], [["Physical components", "{{physical_components}}", "CMake registrations and boundary validator"], ["Production dependency edges", "{{production_edges}}", "Generated catalogue and independent validator"], ["Test topology", "{{test_executables}} executables / {{current_test_cases}} discovered cases", "Current built GoogleTest executables"], ["Build baseline", "CMake 3.20+, C++23", "Root CMake configuration"]]) + """
<h2 id="next">Where to go next</h2>""" + page_index([("Getting started", "Build and link a minimal consumer.", "getting-started.html"), ("Compatibility philosophy", "Understand what “compatible” means here.", "compatibility.html"), ("All components", "Discover every current physical target.", "components/index.html"), ("Known limitations", "Evaluate real gaps and boundaries.", "development/known-limitations.html")])),
        Page("getting-started.html", "Getting Started", "Build a verified minimal Sharp Runtime C++23 consumer and select the CMake component you need.", "Getting Started", intro("Getting Started", "Build the runtime, select a narrow component and run a small native C++ program.", ["Beginner", "CMake", "Verified example"]) + """
<h2 id="requirements">Requirements</h2>""" + bullets(["CMake 3.20 or newer", "A compiler with the required C++23 features", "Git; initialize the GoogleTest submodule only if building Sharp Runtime’s tests", "ZLIB when selecting <code>IO.Compression</code> or <code>All</code>"]) + """
<h2 id="layout">Create the consumer</h2><p>Place the Sharp Runtime checkout at <code>sharp-runtime/</code> beside these two files. The component list must be set before <code>add_subdirectory</code>.</p>""" + code(GETTING_STARTED_CMAKE, "cmake") + code(GETTING_STARTED_CPP) + """
<h2 id="build">Configure and run</h2>""" + code("cmake -S . -B build\ncmake --build build --parallel 2\n./build/hello", "bash") + """
<h2 id="components">Select more components</h2><p>List direct needs using semicolons. Sharp Runtime resolves their transitive closure, so an application does not repeat dependencies.</p>""" + code("set(SHARP_RUNTIME_COMPONENTS\n    Text.Json\n    IO.Hashing\n)\n\ntarget_link_libraries(my_app PRIVATE\n    SharpRuntime::Text.Json\n    SharpRuntime::IO.Hashing\n)", "cmake") + callout("Embed explicitly", "<p>A standalone Sharp Runtime build defaults to <code>All</code>. An embedding application should always set <code>SHARP_RUNTIME_COMPONENTS</code> explicitly and normally disable the runtime’s own tests.</p>") + """
<h2 id="tests">Build the runtime tests</h2>""" + code("cmake -S sharp-runtime -B runtime-build \\\n  -DSHARP_RUNTIME_COMPONENTS=All \\\n  -DSHARP_RUNTIME_BUILD_TESTS=ON\ncmake --build runtime-build --target SharpRuntimeTests --parallel 2\nsharp-runtime/scripts/run_component_tests.sh runtime-build", "bash") + """
<h2 id="next">Next steps</h2>""" + page_index([("Component selection", "Targets, closures and compatibility umbrellas.", "components/index.html"), ("Build reference", "Options, dependencies and consumer modes.", "build.html"), ("First consumer tutorial", "A more detailed project walkthrough.", "tutorials/first-consumer.html"), ("Port C#", "Translate managed concepts deliberately.", "guides/porting-csharp.html")])),
        Page("build.html", "Build and Consumer Integration", "Verified CMake options, targets, dependencies and selective build patterns for Sharp Runtime.", "Getting Started", intro("Build and consumer integration", "Sharp Runtime’s CMake graph can build the complete compatibility surface or a dependency-closed subset.", ["Reference", "CMake 3.20+", "C++23"]) + """
<h2 id="options">Configuration options</h2>""" + table(["Option", "Default", "Purpose"], [["<code>SHARP_RUNTIME_COMPONENTS</code>", "<code>All</code> for standalone builds", "Semicolon-separated component names"], ["<code>SHARP_RUNTIME_BUILD_TESTS</code>", "<code>ON</code>", "Build requested component tests"], ["<code>SHARP_RUNTIME_BUILD_BENCHMARKS</code>", "<code>OFF</code>", "Build the standalone micro-benchmark"], ["<code>SHARP_RUNTIME_BUILD_I686_REGRESSION</code>", "<code>OFF</code>", "Build the special 32-bit MinGW boundary fixture"]]) + """
<h2 id="complete">Complete build</h2>""" + code("git submodule update --init --recursive\ncmake -S . -B build \\\n  -DSHARP_RUNTIME_COMPONENTS=All\ncmake --build build --target SharpRuntimeTests --parallel 2", "bash") + """
<h2 id="selective">Selective build</h2>""" + code("cmake -S . -B build-json \\\n  -DSHARP_RUNTIME_BUILD_TESTS=OFF \\\n  '-DSHARP_RUNTIME_COMPONENTS=Text.Json;Net.Http.Json'\ncmake --build build-json --parallel 2", "bash") + """
<h2 id="targets">Target rules</h2>""" + bullets(["Use <code>SharpRuntime::&lt;Component&gt;</code> targets for new code.", "<code>SharpRuntime::All</code> aggregates every physical component.", "<code>SharpRuntime::Core</code> and <code>SharpRuntime::Collections</code> preserve older broad surfaces.", "<code>SharpRuntime::Xml.XPath</code> aliases the physical <code>Xml</code> archive.", "The raw legacy <code>SHARP_RUNTIME</code> target exists only when <code>All</code> is enabled."]) + """
<h2 id="dependencies">External dependencies</h2>""" + table(["Selection", "Dependency", "Visibility"], [["<code>IO.Compression</code>", "ZLIB", "Private; found by CMake"], ["<code>IO.Compression.Zip</code>", "Vendored miniz", "Private"], ["<code>Xml</code>", "Vendored tinyxml2", "Public because public headers expose its types"], ["<code>Text.Json</code> / HTTP JSON", "Vendored nlohmann JSON headers", "Header surface"], ["<code>Storage</code> on Android", "Parent-provided SDL3 target", "Private"], ["Tests", "Vendored GoogleTest submodule", "Test-only"]]) + callout("Compiler capability", "<p>The build probes native <code>__int128</code> and publishes <code>SHARP_RUNTIME_HAS_NATIVE_INT128</code>. Some numeric surfaces are limited on compilers without it, notably current MSVC configurations.</p>", "warning")),
        Page("running-tests.html", "Testing and Verification", "How Sharp Runtime validates tests, components, boundaries, negative consumers, documentation and CI.", "Getting Started", intro("Testing and verification", "The project uses layered checks: behavior tests, component isolation, negative consumers, integration tests and documentation drift detection.", ["{{test_executables}} executables", "{{current_test_cases}} current cases", "Evidence-qualified"]) + """
<h2 id="topology">Test topology</h2><p>There are {{component_test_executables}} component test executables and {{integration_test_executables_words}}. <code>SharpRuntimeTests</code> is an aggregate build target, not one giant test binary. CTest discovers individual GoogleTest cases.</p>""" + table(["Layer", "What it proves"], [["Component executables", "Behavior owned by one physical component"], ["Integration executable", "Genuinely cross-component behavior in an <code>All</code> build"], ["Selective consumer fixtures", "Requested targets configure, build and expose only declared surfaces"], ["Negative fixtures", "Private or sibling headers do not leak to consumers"], ["Boundary validator", "Unique ownership, declared edges, correct visibility and an acyclic production graph"], ["Catalogue check", "Generated component documentation matches CMake registration"], ["Doxygen ceiling", "Documentation warnings do not exceed the pinned baseline"]]) + """
<h2 id="baseline">Current baseline, honestly stated</h2><p>At source SHA <code>""" + SOURCE_SHA + """</code>, current built executables discover <strong>{{current_test_cases}}</strong> test cases. The latest controlled full-gate record before {{timezone_additions}} final TimeZone additions ran {{gate_cases}} cases: {{gate_passed}} passed, {{gate_skipped_words}} and {{gate_failed_words}}. Five Ping failures were triggered by the host’s ping-group configuration but expose a real missing raw-ICMP receive fallback; one socket test depended on a missing IPv6 interface file.</p>""" + callout("Why the homepage does not say “16,000+ passing”", "<p>The current suite shape and the latest recorded full outcome refer to adjacent revisions. This site publishes them separately rather than inferring an unrecorded all-green result.</p>", "warning") + """
<h2 id="commands">Commands</h2>""" + code("# Build all test executables\ncmake -S . -B build -DSHARP_RUNTIME_COMPONENTS=All\ncmake --build build --target SharpRuntimeTests --parallel 2\n\n# Run the component-aware sequence\nscripts/run_component_tests.sh build\n\n# Full local integrity gate\nscripts/local_ci_check.sh build\n\n# Selective consumer matrix\nscripts/check_selective_components.sh", "bash") + """
<h2 id="ci">Current GitHub Actions</h2><p>The pinned workflow runs on pushes and pull requests. It has nine Ubuntu selective-component jobs, one Ubuntu full local gate and a Doxygen 1.9.8 warning-baseline job on Ubuntu 24.04. It does not currently run a Windows, macOS, Android or Emscripten matrix.</p>"""),
        Page("architecture.html", "Architecture", "Sharp Runtime architecture: component ownership, native types, compatibility boundaries and external dependency isolation.", "Overview", intro("Architecture", "A native C++ compatibility layer organized into independently selectable, boundary-validated CMake components.", ["{{physical_components}} physical components", "{{production_edges}} direct edges", "No dependency allow-list"]) + """
<h2 id="layers">Conceptual layers</h2>""" + table(["Layer", "Role"], [["Consumer code", "Native application or source port using familiar <code>System::*</code> names"], ["Curated compatibility API", "Headers and behavior for the practical implemented subset"], ["Physical components", "Ownership units for headers, implementation, tests and dependencies"], ["Native/platform layer", "C++ standard library, OS facilities and narrowly attached vendor dependencies"]]) + """
<h2 id="components">Component ownership</h2><p>Each module directory owns <code>include/</code>, optional <code>src/</code>, tests and one CMake registration. A component is either a static library or an interface/header-only target. Public, private and test dependencies are distinct.</p>""" + table(["Edge kind", "Meaning"], [["Public", "A public header uses the dependency; include/link requirements reach consumers"], ["Private", "Only implementation sources use the dependency; static-link needs remain correct without leaking include roots"], ["Test-only", "Available to the owning test binary, not production consumers"]]) + """
<h2 id="validation">Boundary enforcement</h2><p>The independent validator parses the registered graph and source includes. It rejects duplicate ownership, orphan production files, undeclared or stale edges, visibility mismatches and cycles. The current allow-list is empty.</p>
<h2 id="native-model">Native object model</h2><p>Sharp Runtime uses ordinary C++ objects, values, templates, RAII and smart pointers. There is no tracing collector. Compatibility wrappers and macros help port familiar shapes, but C++ lifetime, copy/move and aliasing rules remain in force.</p>
<h2 id="external">External dependency isolation</h2><p>ZLIB, miniz, tinyxml2, platform socket/crypto libraries and Android SDL integration attach to their narrow owners. This is what makes a <code>Text.Json</code>-only configuration meaningfully smaller than <code>All</code>.</p>""" + page_index([("Components", "Explore every target and dependency.", "components/index.html"), ("Memory and ownership", "Managed concepts in native C++.", "memory-management.html"), ("Internals", "Ownership and validation details.", "internals/index.html"), ("Adding a component", "Contributor workflow.", "tutorials/add-component.html")])),
        Page("compatibility.html", "Compatibility Philosophy", "What Sharp Runtime means by .NET compatibility, and the deliberate boundaries of its native C++ model.", "Guides", intro("Compatibility philosophy", "Familiar organization and useful behavior compatibility—without claiming to reproduce the managed execution environment.", ["Concept", "Evaluation guide"]) + """
<h2 id="intended">Intended compatibility</h2>""" + bullets(["Recognizable <code>System::*</code> namespaces, type names and porting patterns", "Useful behavior compatibility for the implemented subset", "Exception shapes and validation behavior where implementation and tests establish the contract", "A practical bridge for native ports, especially CNA and related framework/game work"]) + """
<h2 id="not-promised">What a matching name does not promise</h2><p>API completeness, every overload, identical representation, identical Unicode units, identical scheduling, or every edge-case result must be checked per subsystem. Native C++ constraints can make exact managed semantics undesirable or impossible.</p>
<h2 id="exclusions">Intentional exclusions</h2>""" + table(["Managed facility", "Sharp Runtime boundary"], [["CLR / JIT / assemblies", "No managed execution or arbitrary assembly loading"], ["Garbage collection", "RAII and explicit native ownership"], ["General reflection", "Basic type identity only; no metadata universe or member enumeration"], ["Dynamic invocation", "<code>Delegate::DynamicInvoke</code> is deliberately unsupported"], ["P/Invoke / remoting", "No general managed interop or AppDomain/remoting infrastructure"], ["Serialization infrastructure", "No BinaryFormatter-style general object serialization"], ["TLS / certificates", "No TLS transport, certificate stack or <code>SslStream</code>"], ["C# async syntax", "Task types do not add language-level <code>async</code>/<code>await</code> to C++"]]) + """
<h2 id="reductions">Important representation reductions</h2>""" + bullets(["Strings are UTF-8 <code>std::string</code>-based; some indices and lengths are storage bytes rather than .NET UTF-16 code units.", "Delegates use typed C++ callables; late-bound invocation is absent.", "Reflection is type-identification oriented rather than metadata driven.", "Task scheduling and continuation behavior are implemented with native synchronization and threads, not a CLR scheduler."]) + callout("Evaluate by surface", "<p>Use the component family pages and Known Limitations as the public contract. They separate implemented behavior, reductions, platform limits and non-goals.</p>")),
        Page("platform-layer.html", "Platforms and Portability", "Evidence-driven platform matrix for Linux, Windows, macOS, Emscripten and Android in Sharp Runtime.", "Guides", intro("Platforms and portability", "Platform status is reported as validation depth—not a binary supported/unsupported badge.", ["Pinned 2026-08-12", "CI inspected", "Conservative labels"]) + """
<h2 id="matrix">Evidence matrix</h2>""" + table(["Platform/toolchain", "Evidence", "Important limits"], [["Linux / GCC", '<span class="badge badge--verified">Primary native validation</span>', "Only full native build/runtime-test baseline. The last controlled gate has the qualified failures documented on the Testing page."], ["Linux / Clang", '<span class="badge badge--partial">Source-supported</span>', "Compiler branches exist; no pinned Clang CI job in the current workflow."], ["Windows / MinGW-w64", '<span class="badge badge--build">Cross-compile verified</span>', "Library-only All and Text.Json cross-builds; tests were not compiled or run."], ["Windows / i686 MinGW", '<span class="badge badge--build">Compile/link boundary</span>', "Dedicated target excludes native-128 surfaces and disables tests."], ["Windows / MSVC", '<span class="badge badge--limited">Compiler-limited</span>', "CMake warning policy and platform links exist; lack of native <code>__int128</code> limits numeric surface completeness; no current CI/runtime result."], ["macOS / Apple Clang", '<span class="badge badge--partial">Downstream build evidence</span>', "Xcode 15.4 downstream builds drove fixes; no standalone full gate or current hosted job."], ["Emscripten", '<span class="badge badge--partial">Cross-compile verified</span>', "Library-only All and Text.Json cross-builds; no browser tests. DNS and several native facilities are unavailable."], ["Android", '<span class="badge badge--partial">Storage integration path</span>', "Storage paths can use a parent-provided SDL3 target; no whole-project Android build or device-suite result was produced."]]) + """
<h2 id="meanings">Evidence labels</h2>""" + table(["Label", "Meaning"], [["Primary native validation", "The repository’s only full native build/runtime-test baseline; read its exact outcome"], ["Cross-compile verified", "Library compilation completed for a recorded toolchain; runtime tests did not run"], ["Downstream build evidence", "A consumer build drove fixes, without a standalone runtime gate"], ["Source-supported", "Implementation branches exist; this audit did not prove a complete gate"], ["Platform-limited", "Some APIs intentionally throw, reduce behavior or depend on unavailable host facilities"], ["Compiler-limited", "A compiler capability prevents part of the intended surface"]]) + """
<h2 id="api-caveats">Cross-platform caveats</h2>""" + bullets(["Console cursor/color behavior uses ANSI sequences and is not a uniform terminal abstraction.", "Ping and interface enumeration depend on host permissions and files; distinguish environment failures from library defects.", "Emscripten DNS methods explicitly throw <code>PlatformNotSupportedException</code>.", "Android storage’s SDL dependency must be provided by the parent build.", "Operating-system version helpers largely report compile-time platform identity; version comparison is reduced."]) + callout("No overclaim", "<p>A source path or a successful cross-compile is not described as full runtime support. Add platform CI before strengthening these labels.</p>", "warning")),
        Page("memory-management.html", "Memory and Ownership", "How Sharp Runtime maps managed object lifetime to C++ RAII, values, smart pointers and non-owning references.", "Guides", intro("Memory and ownership", "There is no garbage collector. Native lifetime is part of the program’s correctness model.", ["Core concept", "C# porting"]) + """
<h2 id="model">The native model</h2>""" + table(["C# intuition", "Sharp Runtime / C++ reality"], [["Managed reference", "Usually an explicitly chosen smart pointer or a reference with a proven lifetime"], ["Value type", "Ordinary stack/member value with C++ copy and move behavior"], ["GC lifetime", "Scope, owner destruction and RAII"], ["Shared graph", "<code>std::shared_ptr</code> only when ownership is genuinely shared; cycles must be avoided or broken"], ["Borrowed parameter", "Reference or pointer whose lifetime is not extended"]]) + """
<h2 id="rules">Porting rules</h2>""" + bullets(["Start with one clear owner; add shared ownership only when the domain requires it.", "Prefer stack values and direct members for value-like types.", "Treat callback captures as lifetime decisions; avoid capturing raw <code>this</code> past owner teardown.", "Do not assume collection insertion or event subscription copies a managed object graph.", "Read class-specific documentation for copy/move reductions and non-owning links."]) + """
<h2 id="raii">RAII and resources</h2><p>Streams, locks, sockets and other native resources should be scoped so destructors provide cleanup. Explicit <code>Dispose</code>-shaped APIs may exist for source compatibility, but C++ destruction remains the safety net.</p>
<h2 id="differences">Differences from .NET</h2>""" + bullets(["No tracing collector means reference cycles can leak.", "Destruction timing is normally deterministic rather than collection-dependent.", "Copy and move can duplicate or transfer state; check each type’s semantics.", "A reference can dangle if the owner ends; the runtime cannot repair ordinary C++ lifetime errors."]) + callout("Design ownership before transliteration", "<p>A mechanical replacement of every C# reference with <code>shared_ptr</code> obscures ownership and can create cycles. Port the lifetime model, not just the syntax.</p>", "warning") + page_index([("Porting guide", "A systematic C#-to-C++ workflow.", "guides/porting-csharp.html"), ("Object lifecycle", "Runtime internals and virtual behavior.", "internals/object-lifecycle.html"), ("Delegates and events", "Callback lifetime and composition.", "delegates.html"), ("Streams", "Resource ownership in I/O.", "io.html")])),
        Page("cna-integration.html", "CNA Integration", "How CNA uses Sharp Runtime and where Sharp Runtime documentation stops and libcna.com begins.", "Guides", intro("CNA integration", "CNA is the principal verified consumer: Sharp Runtime supplies the practical System.* layer beneath CNA’s XNA-facing API.", ["Ecosystem", "Consumer architecture"]) + """
<h2 id="boundary">Project boundary</h2>""" + table(["Project", "Owns"], [["Sharp Runtime", "Native <code>System::*</code> compatibility types and componentized base-library behavior"], ["CNA", "The <code>Microsoft::Xna::Framework</code>-facing game framework, rendering, audio, input and content behavior"]]) + """
<h2 id="integration">Integration pattern</h2><p>CNA configures Sharp Runtime as a sibling/subproject and links the surfaces its implementation needs. Direct consumers should select their own narrow components rather than copy CNA’s dependency set.</p>
<h2 id="docs">Documentation ownership</h2><p>This site explains the runtime layer: types, components, portability and porting semantics. For XNA APIs, renderer selection, game loops, content and CNA tutorials, use <a href="https://libcna.com/">libcna.com</a>.</p>""" + callout("Verified relationship, not adoption marketing", "<p>The source repositories establish CNA as a consumer. This site does not infer third-party adoption or popularity from that relationship.</p>") + """
<h2 id="next">Continue</h2>""" + page_index([("Visit libcna.com", "CNA’s definitive project and documentation site.", "https://libcna.com/"), ("Sharp Runtime components", "Select direct runtime surfaces.", "components/index.html"), ("Porting C#", "Native translations of familiar patterns.", "guides/porting-csharp.html"), ("Architecture", "Understand the boundary-validated graph.", "architecture.html")])),
    ]


def component_rows(components: dict) -> list[list[str]]:
    rows = []
    for item in components["physical_components"]:
        deps = item["public_dependencies"] + [f"{x} (private)" for x in item["private_dependencies"]]
        deps_html = "—" if not deps else '<span class="dependency-list">' + "".join(f"<code>{e(x)}</code>" for x in deps) + "</span>"
        external = e(item["external_dependency"] or "—")
        rows.append([
            f'<a class="component-anchor" id="component-{slug(item["name"])}" href="#component-{slug(item["name"])}"><code>{e(item["name"])}</code></a>',
            f'<span class="badge badge--kind">{e(item["kind"])}</span>',
            f'<code>{e(item["header"])}</code>',
            deps_html,
            external,
        ])
    return rows


def component_pages(components: dict) -> list[Page]:
    catalogue = intro("Components", "Every current physical component is listed here from the runtime’s generated CMake catalogue—not from a second hand-maintained inventory.", [f"{components['physical_count']} physical", f"{components['direct_production_edges']} direct edges", f"Source {components['source_sha'][:8]}"]) + """
<h2 id="select">Select direct needs</h2>""" + code("set(SHARP_RUNTIME_COMPONENTS\n    Net.Http.Json\n    IO.Hashing\n)\nset(SHARP_RUNTIME_BUILD_TESTS OFF CACHE BOOL \"\" FORCE)\nadd_subdirectory(sharp-runtime)\n\ntarget_link_libraries(app PRIVATE\n    SharpRuntime::Net.Http.Json\n    SharpRuntime::IO.Hashing\n)", "cmake") + """
<p>CMake recursively enables public and private production dependencies. Consumers link only their direct targets.</p>
<h2 id="families">Component families</h2>""" + page_index([("Core and collections", "Foundation, console, URI, time zones, buffers and collection families.", "core.html"), ("Text and data", "Text, regex, JSON, XML and XML LINQ.", "text-data.html"), ("I/O and storage", "Streams, compression, ZIP, hashing and storage.", "io-storage.html"), ("Networking", "Net, sockets, HTTP, MIME, network information, security and WebSockets.", "networking.html"), ("Concurrency", "Threading, tasks, channels and timers.", "concurrency.html"), ("Numerics and globalization", "Globalization, numerics, diagnostics and runtime helpers.", "numerics-globalization.html")]) + """
<h2 id="catalogue">Complete physical catalogue</h2>""" + table(["Component", "Kind", "Representative header", "Production dependencies", "External/platform"], component_rows(components), "component-table") + """
<h2 id="compatibility">Compatibility targets</h2>""" + table(["Target", "Role", "Direct contents"], [[f"<code>{e(item['name'])}</code>", e(item["kind"]), ", ".join(f"<code>{e(x)}</code>" for x in item["dependencies"])] for item in components["compatibility_components"]]) + """
<p><code>SharpRuntime::Headers</code> is an always-present support target rather than a selectable component. The raw legacy <code>SHARP_RUNTIME</code> target forwards to <code>All</code> only in a complete configuration.</p>
<h2 id="maintenance">Synchronization</h2><p><code>tools/sync_components.py</code> reads <code>docs/ComponentCatalog.md</code> from a pinned Sharp Runtime checkout and records the source SHA. <code>tools/validate_site.py</code> can compare the committed data against that checkout, preventing catalogue drift.</p>"""
    pages = [Page("components/index.html", "Sharp Runtime Components", "Complete generated catalogue of all Sharp Runtime physical CMake components, targets and dependency closures.", "Components", catalogue, ["components", "cmake", "targets", "catalogue"] + [item["name"] for item in components["physical_components"]])]
    groups = [
        ("components/core.html", "Core and Collections Components", "Foundation types, console, URI, time zones, buffers, collections and component model.", ["Core.Base", "Console", "Uri", "TimeZone", "Buffers", "Collections.Core", "Collections.Blocking", "Collections.Async", "Collections.ObjectModel", "ComponentModel"], """
<h2 id="foundation">Foundation</h2><p><code>Core.Base</code> owns the foundational object/type model, primitive wrappers, strings, arrays, spans and memory types, delegates and exceptions. <code>Console</code>, <code>Uri</code> and <code>TimeZone</code> are narrow optional physical targets; the older <code>Core</code> target aggregates them.</p>
<h2 id="collections">Collection split</h2>""" + table(["Component", "Purpose"], [["<code>Collections.Core</code>", "Synchronous generic/non-generic collection fundamentals"], ["<code>Collections.Blocking</code>", "BlockingCollection and its threading closure"], ["<code>Collections.Async</code>", "Asynchronous enumerable contracts"], ["<code>Collections.ObjectModel</code>", "Observable and object-model collection behavior"], ["<code>ComponentModel</code>", "Notifications, async completion shapes and component-model contracts"]]) + """
<h2 id="behavior">Behavior notes</h2>""" + bullets(["Enumerator versioning is enforced for mutable collection families; it follows native implementation details rather than a promise of universal .NET parity.", "Concurrent, blocking and async families have distinct scheduling and lifetime concerns.", "Floating-point comparer behavior has explicit compatibility decisions; do not assume host <code>operator==</code> is always the intended key policy.", "Object-model notifications are typed C++ callback behavior; callback lifetime remains native."])),
        ("components/text-data.html", "Text, JSON and XML Components", "Encoding, StringBuilder, regular expressions, JSON, XML and LINQ-style XML.", ["Text", "Text.Json", "Text.RegularExpressions", "Xml", "Xml.Linq"], """
<h2 id="text">Text</h2><p><code>Text</code> covers encodings, builders, formatting helpers and Base64-related surfaces. The string model is UTF-8 based; several index and length APIs therefore use bytes where .NET uses UTF-16 code units.</p>
<h2 id="regex">Regular expressions</h2><p><code>Text.RegularExpressions</code> is header-only and provides the project’s curated regex surface. Treat pattern, option and Unicode behavior as a practical subset rather than a guarantee of the entire .NET engine.</p>
<h2 id="json">JSON</h2><p><code>Text.Json</code> uses vendored nlohmann JSON machinery behind Sharp Runtime-compatible types. Serialization is curated; general .NET reflection-driven serialization infrastructure is not present.</p>
<h2 id="xml">XML</h2><p><code>Xml</code> uses vendored tinyxml2, exposed publicly where <code>XmlDocument</code> headers expose its types. <code>Xml.Linq</code> adds LINQ-style names, elements and documents. <code>Xml.XPath</code> is a compatibility alias of the physical <code>Xml</code> archive because their implementations have mutual binary dependencies.</p>""" + callout("Strictness matters", "<p>Recent remediation tightened XML lifecycle and strictness behavior. XPath covers the implemented subset; variables, custom functions and general extension contexts are not a full System.Xml.XPath engine.</p>", "warning")),
        ("components/io-storage.html", "I/O, Compression and Storage Components", "Streams, files, directories, compression, ZIP, hashing, storage and isolated storage.", ["IO", "IO.Compression", "IO.Compression.Zip", "IO.Hashing", "Storage", "IO.IsolatedStorage"], """
<h2 id="io">Streams and files</h2><p><code>IO</code> owns Stream, MemoryStream and file/directory/path surfaces plus readers, writers and filesystem-related helpers. Capability queries, disposal and argument validation have been heavily audited; use virtual capability members instead of assuming every stream supports read/write/seek.</p>
<h2 id="compression">Compression and ZIP</h2><p><code>IO.Compression</code> privately finds ZLIB and owns streaming compression behavior. <code>IO.Compression.Zip</code> privately embeds miniz for archive operations. These are separate physical components so selecting ZIP or compression is explicit.</p>
<h2 id="hashing">Hashing</h2><p><code>IO.Hashing</code> provides non-cryptographic hashing/checksum types including Adler32 and related algorithms. Do not treat this namespace as a replacement for cryptographic hashing or authentication.</p>
<h2 id="storage">Storage</h2><p><code>Storage</code> resolves platform storage paths and can consume a parent-provided SDL3 target on Android. <code>IO.IsolatedStorage</code> builds confinement semantics over I/O and storage paths; it is not a security sandbox against an adversarial process.</p>""" + callout("Lifecycle first", "<p>Use RAII and keep streams/resources scoped. Compatibility-shaped <code>Dispose</code> calls do not remove normal C++ ownership responsibilities.</p>")),
        ("components/networking.html", "Networking Components", "DNS, endpoints, sockets, HTTP, headers, HTTP JSON, MIME, network information, security markers and WebSockets.", ["Net", "Net.Sockets", "Net.Http", "Net.Http.Headers", "Net.Http.Json", "Net.Mime", "Net.NetworkInformation", "Net.Security", "Net.WebSockets"], """
<h2 id="net">Addresses, DNS and URI integration</h2><p><code>Net</code> provides address, endpoint, cookie, DNS and related foundations. Windows builds attach Winsock privately. Emscripten DNS host operations explicitly throw because the required native APIs are unavailable.</p>
<h2 id="sockets">Sockets</h2><p><code>Net.Sockets</code> covers socket, TCP/UDP and network stream patterns using platform socket APIs. Host permissions, interface availability and platform errno/WSA translation affect observable failures.</p>
<h2 id="http">HTTP and headers</h2><p><code>Net.Http</code> provides message, content, client and handler surfaces for the implemented transport. Headers are a distinct component, and <code>Net.Http.Json</code> combines HTTP, tasks and Text.Json for JSON helpers.</p>
<h2 id="websockets">WebSockets</h2><p>The client implements <code>ws://</code>. Secure <code>wss://</code> throws <code>PlatformNotSupportedException</code>; this is not hidden behind a vague “WebSockets supported” claim.</p>
<h2 id="network-info">Network information</h2><p>NetworkInterface is currently Linux-specific. Ping uses datagram ICMP; restrictive <code>ping_group_range</code> can require a raw receive fallback that the implementation does not yet provide. The separate missing-IPv6-proc test condition is environmental.</p>""" + callout("No TLS stack", "<p><code>Net.Security</code> is an interface/enum surface. Sharp Runtime does not currently supply certificates, <code>SslStream</code>, HTTPS or WSS transport.</p>", "warning")),
        ("components/concurrency.html", "Threading, Tasks, Channels and Timers", "Native threading, synchronization, cancellation, tasks, continuations, channels and timer behavior.", ["Threading", "Threading.Tasks", "Threading.Channels", "Timers"], """
<h2 id="threading">Threading</h2><p><code>Threading</code> covers threads, synchronization primitives, cancellation and thread-pool-oriented behavior using native C++ synchronization. Object lifetime and callback capture remain the caller’s responsibility.</p>
<h2 id="tasks">Tasks</h2><p><code>Threading.Tasks</code> provides Task, ValueTask-shaped and continuation APIs for porting familiar control flow. It does not add C# language <code>async</code>/<code>await</code> to C++ and is not a CLR task scheduler.</p>
<h2 id="channels">Channels</h2><p><code>Threading.Channels</code> is a header-only component layered over tasks for bounded/unbounded channel patterns. Cancellation, completion and blocking behavior should be designed explicitly in native code.</p>
<h2 id="timers">Timers</h2><p><code>Timers</code> owns elapsed-event timer behavior and privately depends on <code>Threading</code>. A timer callback can outlive the initiating scope unless ownership and shutdown are coordinated.</p>""" + callout("Callback lifetime", "<p>A continuation, event or timer that captures a raw object pointer can become unsafe after destruction. Prefer an explicit owner, cancellation and join/teardown protocol.</p>", "warning")),
        ("components/numerics-globalization.html", "Numerics, Globalization and Runtime Utilities", "Cultures, numeric types, vectors, matrices, diagnostics and runtime helper components.", ["Globalization", "Numerics", "Diagnostics", "Runtime", "Security", "Security.Cryptography", "Security.Cryptography.Random"], """
<h2 id="globalization">Globalization</h2><p>The component provides culture, calendar, Unicode category, number parsing and formatting surfaces. Locale data and collation/grapheme behavior are curated and platform-sensitive; broad culture parity is not implied.</p>
<h2 id="numerics">Numerics</h2><p>Vectors, matrices, quaternion, Complex, BigInteger, Decimal and wide numeric wrappers are available across the implemented subset. Current code probes native <code>__int128</code>; platforms without it have reduced wide-integer capability.</p>
<h2 id="diagnostics">Diagnostics and runtime</h2><p><code>Diagnostics</code> contains diagnostic/code-analysis and process-oriented surfaces. <code>Runtime</code> owns selected <code>System.Runtime</code> contracts—without CLR services, assembly metadata or managed interop.</p>
<h2 id="security">Security and cryptography</h2><p><code>Security</code> is a marker/exception surface. <code>Security.Cryptography</code> includes curated hashing, HMAC and PBKDF2-related behavior, while secure random is isolated in <code>Security.Cryptography.Random</code>. Windows random generation attaches bcrypt privately.</p>""" + callout("Cryptographic boundary", "<p>Hashing, HMAC, PBKDF2 and secure random do not amount to a complete crypto/TLS platform. Encryption algorithms, certificates, TLS and <code>SslStream</code> are outside the current public promise.</p>", "warning")),
    ]
    for path, title, desc, names, body in groups:
        rows = []
        by_name = {c["name"]: c for c in components["physical_components"]}
        for name in names:
            c = by_name[name]
            deps = c["public_dependencies"] + [f"{x} (private)" for x in c["private_dependencies"]]
            rows.append([f"<code>{e(name)}</code>", e(c["kind"]), ", ".join(f"<code>{e(x)}</code>" for x in deps) or "—", f"<code>{e(c['header'])}</code>"])
        body = intro(title, desc, [f"{len(names)} physical components", f"Source {SOURCE_SHA[:8]}"]) + "<h2 id=\"targets\">Targets in this family</h2>" + table(["Component", "Kind", "Production dependencies", "Representative header"], rows) + body + "<h2 id=\"catalogue\">Complete catalogue</h2><p>See <a href=\"index.html#catalogue\">all {{physical_components}} physical components</a> for external dependencies, ownership and direct graph details.</p>"
        pages.append(Page(path, title, desc, "Components", body, ["components", "cmake"] + [n.lower() for n in names]))
    return pages


def tutorial_pages() -> list[Page]:
    pages = [Page("tutorials/index.html", "Sharp Runtime Tutorials", "Practical Sharp Runtime learning paths for integration, C# porting, data, I/O, concurrency and component development.", "Tutorials", intro("Tutorials", "Focused, buildable paths from a first CMake consumer to contributor-level component work.", ["Beginner to advanced", "Practical examples"]) + """
<h2 id="start">Start here</h2>""" + page_index([("1. Build a first consumer", "Select Console and run a minimal C++23 app.", "first-consumer.html"), ("2. Select components", "Compose narrow targets and understand closure.", "select-components.html"), ("3. Port a C# class", "Translate properties, ownership and exceptions.", "port-csharp-class.html"), ("4. Port collections", "Use typed native collection surfaces deliberately.", "use-collections.html")]) + """
<h2 id="data">Text and data</h2>""" + page_index([("Strings and StringBuilder", "Understand UTF-8 storage semantics.", "strings-and-builder.html"), ("JSON", "Use the curated Text.Json surface.", "json.html"), ("XML LINQ", "Parse and navigate names/elements.", "xml-linq.html")]) + """
<h2 id="systems">Systems programming</h2>""" + page_index([("Files and streams", "Scope streams and handle failures.", "work-with-files.html"), ("Compression and hashing", "Choose distinct components for distinct jobs.", "compression-hashing.html"), ("HTTP boundaries", "Build requests without assuming TLS.", "http.html"), ("Tasks and cancellation", "Translate async-shaped control flow to native lifetimes.", "tasks-cancellation.html")]) + """
<h2 id="contribute">Contributor path</h2>""" + page_index([("Events and delegates", "Typed callables and subscription lifetime.", "use-events.html"), ("Add a component", "Registration, ownership, fixtures and catalogue.", "add-component.html"), ("Debug component selection", "Diagnose missing targets and leaked headers.", "debug-components.html")]), ["tutorials", "learning path"])]

    specs = [
        ("tutorials/first-consumer.html", "Build a First Consumer", "Create a minimal CMake application that links only SharpRuntime::Console.", "Beginner", """
<h2 id="goal">Goal</h2><p>Build a tiny native executable using one physical component. This keeps the dependency graph visible and avoids pulling the complete runtime into an embedding project.</p>
<h2 id="files">1. Create the files</h2>""" + code(GETTING_STARTED_CMAKE, "cmake") + code(GETTING_STARTED_CPP) + """
<h2 id="source">2. Add the source checkout</h2><p>Clone Sharp Runtime as <code>sharp-runtime/</code> beneath the sample project. GoogleTest is unnecessary because this consumer forces runtime tests off.</p>""" + code("git clone https://github.com/openeggbert/sharp-runtime.git sharp-runtime", "bash") + """
<h2 id="run">3. Configure, build and run</h2>""" + code("cmake -S . -B build\ncmake --build build --parallel 2\n./build/hello", "bash") + """
<h2 id="understand">What happened</h2>""" + bullets(["<code>SHARP_RUNTIME_COMPONENTS</code> was set before adding the subdirectory.", "The app linked the namespaced physical target <code>SharpRuntime::Console</code>.", "CMake automatically enabled <code>Core.Base</code>, Console’s public dependency.", "The executable is native C++; no CLR or managed assembly is involved."]) + callout("Verified shape", "<p>The include, namespace, method, CMake option and target names are present at the pinned source SHA.</p>", "success")),
        ("tutorials/select-components.html", "Select CMake Components", "Combine multiple Sharp Runtime targets and inspect dependency closure.", "Beginner", """
<h2 id="scenario">Scenario</h2><p>An application needs JSON and non-cryptographic hashing. Request exactly those direct surfaces:</p>""" + code("set(SHARP_RUNTIME_COMPONENTS\n    Text.Json\n    IO.Hashing\n)\nset(SHARP_RUNTIME_BUILD_TESTS OFF CACHE BOOL \"\" FORCE)\nadd_subdirectory(sharp-runtime)\n\ntarget_link_libraries(app PRIVATE\n    SharpRuntime::Text.Json\n    SharpRuntime::IO.Hashing\n)", "cmake") + """
<h2 id="closure">Understand the closure</h2><p><code>Text.Json</code> enables Core.Base, Buffers and Text publicly plus Collections.Core privately. <code>IO.Hashing</code> enables Core.Base and IO; IO in turn brings Uri publicly and TimeZone privately. The application does not repeat any of those transitive targets.</p>
<h2 id="test">Test one component</h2>""" + code("cmake -S sharp-runtime -B build-json-tests \\\n+  -DSHARP_RUNTIME_COMPONENTS=Text.Json \\\n+  -DSHARP_RUNTIME_BUILD_TESTS=ON\ncmake --build build-json-tests --target SharpRuntimeTests --parallel 2\nsharp-runtime/scripts/run_component_tests.sh build-json-tests", "bash") + """
<h2 id="mistakes">Common mistakes</h2>""" + bullets(["Setting the component list after <code>add_subdirectory</code>", "Linking <code>SHARP_RUNTIME</code> in a selective build—the legacy target only exists with All", "Listing private/transitive dependencies in consumer CMake", "Assuming that a component’s test dependencies become production dependencies"])),
        ("tutorials/port-csharp-class.html", "Port a C# Class", "Translate a small C# class to native C++ with explicit ownership, properties and exceptions.", "Intermediate", """
<h2 id="before">Start from semantics</h2><p>Record whether the C# type is value-like, who owns it, whether callbacks outlive it, and which exceptions callers depend on. Then translate the shape.</p>
<h2 id="property">Properties become explicit accessors</h2>""" + code("""class Counter final {
public:
    int getValueProperty() const noexcept { return value_; }

    void Increment()
    {
        if (value_ == INT_MAX) {
            throw System::OverflowException("Counter overflow.");
        }
        ++value_;
    }

private:
    int value_ = 0;
};""") + """
<h2 id="ownership">Choose ownership</h2>""" + bullets(["Use a direct member for a required value with the same lifetime.", "Use <code>std::unique_ptr</code> for exclusive heap ownership.", "Use <code>std::shared_ptr</code> only for real shared ownership; identify cycles.", "Use references/pointers only when a longer-lived owner is already established."]) + """
<h2 id="errors">Preserve observable errors</h2><p>Use the specific implemented Sharp Runtime exception when callers rely on it. Do not replace every validation error with a generic <code>std::runtime_error</code>, and do not invent .NET behavior that the runtime does not implement.</p>
<h2 id="verify">Verify the port</h2>""" + bullets(["Compile warnings as errors.", "Test normal, boundary and invalid inputs.", "Test copy/move behavior if the type owns resources.", "Test callback shutdown and destruction order."])),
        ("tutorials/use-collections.html", "Use Collections Safely", "Choose Sharp Runtime collection components and preserve iterator/versioning semantics.", "Intermediate", """
<h2 id="choose">Choose the family first</h2>""" + table(["Need", "Component"], [["Synchronous lists, dictionaries, sets, queues", "<code>Collections.Core</code>"], ["Blocking producer/consumer queue", "<code>Collections.Blocking</code>"], ["Async enumeration contracts", "<code>Collections.Async</code>"], ["Observable/object-model collections", "<code>Collections.ObjectModel</code>"]]) + """
<h2 id="cmake">Select it</h2>""" + code("""set(SHARP_RUNTIME_COMPONENTS Collections.Core)
target_link_libraries(app PRIVATE SharpRuntime::Collections.Core)""", "cmake") + """
<h2 id="rules">Native rules still apply</h2>""" + bullets(["Mutation invalidates version-sensitive enumerators; do not keep them across changes.", "Container element ownership follows the chosen C++ value/pointer type.", "Concurrent collections do not make the objects stored inside them thread-safe.", "Floating keys need an intentional comparer policy, particularly for NaN and signed zero."]) + callout("Avoid transliteration by type name alone", "<p>A C# collection of managed objects and a C++ collection of values have different copy, identity and lifetime behavior. Decide the element model before selecting the container.</p>", "warning")),
        ("tutorials/use-events.html", "Use Delegates and Events", "Compose typed callbacks while controlling capture and subscription lifetime.", "Intermediate", """
<h2 id="model">Typed callables</h2><p>Action, Func, Predicate and EventHandler-shaped APIs provide compile-time typed callback patterns. They are not late-bound managed delegates.</p>
<h2 id="lifetime">Design lifetime explicitly</h2>""" + bullets(["Prefer value captures for immutable data.", "Use weak ownership when a callback can outlive its target.", "Unsubscribe or cancel before destroying an object referenced by the callback.", "Treat async callbacks and timer handlers as concurrency boundaries."]) + """
<h2 id="composition">Composition</h2><p>Delegate composition can model multicast behavior for the implemented subset, but exception propagation, removal identity and concurrent modification deserve tests in the consumer’s use case.</p>""" + callout("No DynamicInvoke", "<p>Late-bound <code>DynamicInvoke</code> is deliberately unsupported and throws <code>NotImplementedException</code>. Use typed invocation.</p>", "warning")),
        ("tutorials/work-with-files.html", "Work with Files and Streams", "Use Sharp Runtime I/O with RAII, capability checks and explicit platform error handling.", "Intermediate", """
<h2 id="select">Select I/O</h2>""" + code("""set(SHARP_RUNTIME_COMPONENTS IO)
target_link_libraries(app PRIVATE SharpRuntime::IO)""", "cmake") + """
<h2 id="lifetime">Scope resources</h2><p>Keep streams and readers/writers in the narrowest practical scope. Destruction is the native cleanup backstop; explicit Dispose-shaped calls may still matter for source-compatible control flow.</p>
<h2 id="capabilities">Ask before operating</h2>""" + bullets(["Use stream capability properties rather than assuming read/write/seek.", "Treat short reads and end-of-stream as normal control flow.", "Distinguish path validation from filesystem failures.", "Do not hold a callback or span beyond the buffer/resource lifetime it borrows."]) + """
<h2 id="platform">Handle platform variation</h2><p>Paths, watchers, sharing, symlinks and permission errors are platform-dependent. Catch the narrow Sharp Runtime I/O exception only when the application can recover; otherwise preserve the diagnostic.</p>"""),
        ("tutorials/strings-and-builder.html", "Strings and StringBuilder", "Use UTF-8 Sharp Runtime text APIs without assuming .NET UTF-16 indexing.", "Intermediate", """
<h2 id="representation">Know the representation</h2><p>Sharp Runtime’s common string surface is based on UTF-8 <code>std::string</code>. That is excellent for native interoperability but differs from .NET’s UTF-16 <code>System.String</code>.</p>
<h2 id="builder">StringBuilder byte positions</h2><p>Current <code>StringBuilder</code> length, index and count operations use UTF-8 storage bytes. For example, <code>éA</code> occupies three bytes even though a user sees two characters. An index-taking mutation can split a multi-byte scalar.</p>
<h2 id="safe">Practical guidance</h2>""" + bullets(["Use append and whole-string operations when byte indexing is irrelevant.", "Use rune/scalar-aware iteration for Unicode code points.", "Do not use byte length as a display-column or grapheme count.", "Test malformed input and culture-sensitive formatting separately."]) + callout("Not UTF-16 parity", "<p>Code ported from C# that stores string indices or slices arbitrary text needs a deliberate unit conversion; a mechanical method rename is insufficient.</p>", "warning")),
        ("tutorials/json.html", "Work with JSON", "Select Text.Json and use its curated native serialization surface.", "Intermediate", """
<h2 id="select">Select the component</h2>""" + code("""set(SHARP_RUNTIME_COMPONENTS Text.Json)
target_link_libraries(app PRIVATE SharpRuntime::Text.Json)""", "cmake") + """
<h2 id="scope">Understand the scope</h2><p>The component supplies Sharp Runtime-compatible JSON reader/writer/document and curated serialization behavior over vendored nlohmann JSON machinery. It is not a general reflection-driven clone of every <code>System.Text.Json</code> feature.</p>
<h2 id="round-trip">Round-trip an explicit native shape</h2>""" + code("""#include <iostream>
#include <string>
#include <vector>

#include "System/Text/Json/JsonSerializer.hpp"

using System::Text::Json::JsonSerializer;

int main()
{
    const std::vector<int> ids{3, 7, 11};
    const std::string json = JsonSerializer::Serialize(ids);
    const auto restored =
        JsonSerializer::Deserialize<std::vector<int>>(json);

    std::cout << json << '\\n';
    return restored == ids ? 0 : 1;
}""") + callout("Built and run", "<p>Against the pinned source, this prints <code>[3,7,11]</code> and exits successfully. Conversion is compile-time nlohmann/ADL behavior—not reflection.</p>", "success") + """
<h2 id="workflow">A safe workflow</h2>""" + bullets(["Choose explicit native data shapes.", "Validate required fields and types at the boundary.", "Keep parse/document lifetimes clear when values reference backing storage.", "Test comments, trailing commas, numbers, Unicode and invalid input according to the exact APIs used."]) + """
<h2 id="numeric-boundary">Numeric boundary</h2><p>Validate aggregate member types before conversion. A current nested conversion such as a fractional JSON number inside <code>vector&lt;int&gt;</code> can truncate even though the top-level integral conversion rejects that input.</p>
<h2 id="http">HTTP JSON</h2><p>For task-shaped HTTP JSON helpers, select <code>Net.Http.Json</code>. It brings HTTP, Text.Json and Threading.Tasks—but it does not add HTTPS/TLS.</p>"""),
        ("tutorials/xml-linq.html", "Parse XML with XML LINQ", "Select Xml.Linq and work with names, elements and documents within the implemented subset.", "Intermediate", """
<h2 id="select">Select XML LINQ</h2>""" + code("""set(SHARP_RUNTIME_COMPONENTS Xml.Linq)
target_link_libraries(app PRIVATE SharpRuntime::Xml.Linq)""", "cmake") + """
<h2 id="model">Model</h2><p><code>Xml.Linq</code> provides LINQ-style XML names, nodes, elements and documents over the project’s XML implementation. <code>Xml</code> and <code>Xml.Linq</code> have mutual binary needs, which is why XPath remains an alias rather than another physical archive.</p>
<h2 id="parse">Parse and navigate</h2>""" + code("""#include <iostream>

#include "System/Xml/Linq/XElement.hpp"

using System::Xml::Linq::XElement;

int main()
{
    auto catalog = XElement::Parse(
        "<catalog><book id=\\\"sr\\\">Sharp Runtime</book></catalog>");
    auto book = catalog->Element("book");
    if (!book) return 1;

    const auto id = book->getAttributeValue("id");
    if (!id || *id != "sr") return 2;

    std::cout << book->getValueProperty() << '\\n';
    return 0;
}""") + callout("Built and run", "<p>Against the pinned source, this prints <code>Sharp Runtime</code> and exits successfully.</p>", "success") + """
<h2 id="guidance">Guidance</h2>""" + bullets(["Treat namespace-qualified names explicitly; current parse/serialization is not a full namespace-URI parity surface.", "Keep parent/child ownership and document lifetime in mind; do not retain borrowed views across owner destruction.", "Prefer owning <code>Attributes()</code> results when data must outlive the element.", "Do not assume a full XPath extension engine; variables and custom functions are outside the current subset."]) + callout("External type exposure", "<p>The Xml target publicly exposes vendored tinyxml2 because a public header uses its types. This is an intentional component-visibility decision.</p>")),
        ("tutorials/compression-hashing.html", "Compression, ZIP and Hashing", "Choose the right Sharp Runtime I/O component for compression, archives or checksums.", "Intermediate", """
<h2 id="choose">Separate concerns</h2>""" + table(["Job", "Component", "Dependency"], [["Streaming compression", "<code>IO.Compression</code>", "ZLIB"], ["ZIP archives", "<code>IO.Compression.Zip</code>", "Vendored miniz"], ["Checksums/non-crypto hashes", "<code>IO.Hashing</code>", "No external library"]]) + """
<h2 id="cmake">Select only the jobs you use</h2>""" + code("""set(SHARP_RUNTIME_COMPONENTS
    IO.Compression
    IO.Hashing
)
target_link_libraries(app PRIVATE
    SharpRuntime::IO.Compression
    SharpRuntime::IO.Hashing
)""", "cmake") + """
<h2 id="crc">Compute a CRC-32 checksum</h2>""" + code("""#include <iostream>
#include <string>

#include "System/IO/Hashing/Crc32.hpp"

using System::IO::Hashing::Crc32;

int main()
{
    const std::string payload = "123456789";
    const auto crc = Crc32::HashToUInt32(
        reinterpret_cast<const SharpRuntime::bytecs*>(payload.data()),
        static_cast<SharpRuntime::intcs>(payload.size()));

    std::cout << std::hex << crc << '\\n';
    return crc == 0xCBF43926u ? 0 : 1;
}""") + callout("Built and run", "<p>The standard check vector produces <code>cbf43926</code> at the pinned source. The pointer remains valid for the call and the length conversion is explicit.</p>", "success") + """
<h2 id="rules">Rules</h2>""" + bullets(["Finish/flush compression streams before consuming final output.", "Treat archive entry names as untrusted paths; enforce an extraction root.", "Do not use Adler32/CRC-style hashes for authentication or password storage.", "Use Security.Cryptography for the implemented crypto hashes/HMAC/PBKDF2 surface, and document its boundaries."])),
        ("tutorials/http.html", "Use HTTP Within Its Transport Boundaries", "Select Sharp Runtime HTTP components and avoid assuming TLS or browser networking parity.", "Advanced", """
<h2 id="targets">Choose targets</h2>""" + code("""set(SHARP_RUNTIME_COMPONENTS
    Net.Http
    Net.Http.Headers
)
target_link_libraries(app PRIVATE
    SharpRuntime::Net.Http
    SharpRuntime::Net.Http.Headers
)""", "cmake") + """
<h2 id="request">Make a synchronous plain-HTTP request</h2>""" + code("""#include <iostream>

#include "System/Net/Http/HttpClient.hpp"

using System::Net::Http::HttpClient;

int main()
{
    HttpClient client;
    client.setDefaultHeader("Accept", "text/plain");

    auto response = client.Get("http://example.com/");
    response->EnsureSuccessStatusCode();

    auto content = response->getContentProperty();
    if (!content) return 1;
    std::cout << content->ReadAsString() << '\\n';
    return 0;
}""") + callout("Compile-verified, intentionally not run", "<p>This exact shape compiles and links against the pinned source. The audit made no external network request and claims no endpoint result.</p>", "success") + """
<h2 id="boundary">Transport boundary</h2><p>Document and test against plain <code>http://</code> behavior. Sharp Runtime does not currently provide TLS, certificates, <code>SslStream</code> or HTTPS. WebSockets similarly support <code>ws://</code>, not <code>wss://</code>.</p>
<h2 id="errors">Error handling</h2>""" + bullets(["Distinguish DNS resolution, connect and protocol failures; the current API has no general request cancellation-token/timeout overload.", "Validate headers; names are currently case-sensitive and default/request fields can duplicate semantically.", "Responses are fully buffered and have no current hard size limit; avoid untrusted or large endpoints.", "No automatic redirect following is provided.", "Prefer the synchronous public pattern: async helpers capture the HttpClient owner, which must outlive completion.", "Treat environment network restrictions as a distinct diagnostic category."]) + callout("Security", "<p>Do not send credentials or sensitive data over the plain HTTP/WebSocket transport offered by the current runtime. Use a separately audited secure transport layer if the application requires it.</p>", "danger")),
        ("tutorials/tasks-cancellation.html", "Tasks, Continuations and Cancellation", "Port async-shaped code to Sharp Runtime with explicit native scheduling and lifetime.", "Advanced", """
<h2 id="translate">Translate the control flow</h2><p>A Task is a compatibility abstraction, not C# language syntax. Express creation, continuation, waiting and cancellation through the implemented C++ API and make the scheduling boundary visible in code review.</p>
<h2 id="example">Observe cooperative cancellation</h2>""" + code("""#include <iostream>

#include "System/Threading/CancellationToken.hpp"
#include "System/Threading/CancellationTokenSource.hpp"
#include "System/Threading/Tasks/Task.hpp"
#include "System/Threading/Tasks/TaskCanceledException.hpp"

using System::Threading::CancellationToken;
using System::Threading::CancellationTokenSource;
using System::Threading::Tasks::TaskCanceledException;
using System::Threading::Tasks::TaskT;

int main()
{
    CancellationTokenSource source;
    const CancellationToken token = source.getTokenProperty();
    source.Cancel();

    auto task = TaskT<int>::Run([token] {
        token.ThrowIfCancellationRequested();
        return 42;
    }, token);

    try {
        (void)task.Wait();
    } catch (const TaskCanceledException&) {
        std::cout << "canceled\\n";
        return 0;
    }
    return 1;
}""") + callout("Built and run", "<p>Against the pinned source, the task reports <code>canceled</code> and exits successfully. Passing a token does not interrupt arbitrary work: running code must poll it or call <code>ThrowIfCancellationRequested()</code>.</p>", "success") + """
<h2 id="lifetime">Lifetime checklist</h2>""" + bullets(["Who owns the work state until completion?", "Can a continuation run after its UI/game/component owner is destroyed?", "Which cancellation source controls shutdown?", "Does teardown wait/join, or deliberately detach?", "How are exceptions observed and propagated?"]) + """
<h2 id="execution">Execution differences</h2><p>Tasks start eagerly through native <code>std::async</code>; <code>Wait()</code> returns or rethrows directly rather than wrapping faults in a managed <code>AggregateException</code>. Single-thread Emscripten cannot provide this surface without pthreads.</p>
<h2 id="channels">Channels</h2><p>Use <code>Threading.Channels</code> for producer/consumer flow when it matches the port. Decide bounded capacity, full behavior, completion and cancellation instead of inheriting implicit assumptions from the C# scheduler.</p>""" + callout("No magic await", "<p>Sharp Runtime cannot add the C# <code>async</code>/<code>await</code> grammar or CLR synchronization-context semantics to C++.</p>", "warning")),
        ("tutorials/add-component.html", "Add a New Component", "Contributor workflow for Sharp Runtime module ownership, CMake registration, tests and validation.", "Advanced", """
<h2 id="layout">1. Create one owner</h2><p>Place public headers, sources and component tests under one <code>modules/&lt;module&gt;/{include,src,tests}</code> tree with its CMakeLists.</p>
<h2 id="register">2. Register metadata</h2><p>Add the directory once in <code>cmake/SharpRuntimeModules.cmake</code>. Register the target as STATIC or INTERFACE and declare public, private and test-only component edges at the narrowest correct visibility.</p>
<h2 id="validate">3. Validate boundaries</h2>""" + code("""python3 scripts/validate_module_boundaries.py
python3 test/validate_module_boundaries_test.py
python3 scripts/generate_component_catalog.py --check""", "bash") + """
<h2 id="consumer">4. Add consumer evidence</h2><p>Add or update a positive selective fixture for meaningful public use. Add negative fixtures when private or sibling headers must stay inaccessible.</p>
<h2 id="gate">5. Run gates</h2>""" + code("""scripts/check_selective_components.sh
scripts/local_ci_check.sh build""", "bash") + callout("Do not solve cycles with umbrellas", "<p>Internal production targets should not depend on <code>Core</code>, <code>Collections</code> or <code>All</code> compatibility umbrellas. Revisit ownership or isolate the optional behavior.</p>", "warning")),
        ("tutorials/debug-components.html", "Debug Component Selection", "Diagnose unknown targets, transitive closure, leaked headers and selective test behavior.", "Advanced", """
<h2 id="unknown">Unknown target</h2>""" + bullets(["Confirm the canonical spelling in the generated catalogue.", "Set <code>SHARP_RUNTIME_COMPONENTS</code> before <code>add_subdirectory</code>.", "Do not use the legacy raw <code>SHARP_RUNTIME</code> target in a selective configuration."]) + """
<h2 id="include">Header not found</h2>""" + bullets(["Identify which physical component owns the header.", "Link that direct component; do not add a module include directory manually.", "If a public header needs another component’s header, the owning module likely needs a PUBLIC edge."]) + """
<h2 id="leak">Private header unexpectedly visible</h2><p>Run the negative consumer fixtures and the module boundary validator. Do not “fix” the consumer by adding broad vendor or module include roots.</p>
<h2 id="tests">Unexpected test set</h2><p>Selective testing builds only the requested component’s test executable plus declared production test dependencies. Requesting an alias delegates to its physical component; requesting All adds integration tests.</p>"""),
    ]
    for path, title, desc, level, body in specs:
        pages.append(Page(path, title, desc, "Tutorials", intro(title, desc, [level, "Tutorial"]) + body + "<div class=\"next-links\"><a href=\"index.html\"><span class=\"next-label\">Tutorial hub</span>All tutorials</a><a href=\"../components/index.html\"><span class=\"next-label\">Reference</span>Component catalogue</a></div>", ["tutorial", level.lower()] + title.lower().split()))
    return pages


def reference_pages() -> list[Page]:
    # Existing public URLs are retained and rewritten into a smaller set of authoritative topics.
    specs = [
        ("runtime-overview.html", "Runtime Model", "Native type, object, string, array, delegate and exception architecture.", "Overview", """
<h2 id="native">Native first</h2><p>Sharp Runtime types are ordinary C++ values and objects. Names and behavior aid porting, but ABI, ownership, copy/move and scheduling follow native rules.</p>
<h2 id="foundations">Foundation surfaces</h2>""" + page_index([("Type system", "Object, Type, wrappers and conversion.", "type-system.html"), ("Strings", "UTF-8 representation and formatting.", "strings.html"), ("Arrays and memory", "Containers, Span and Memory concepts.", "arrays.html"), ("Exceptions", "Hierarchy, HResult and causes.", "exceptions.html"), ("Delegates", "Typed callbacks and events.", "delegates.html"), ("Reflection", "Basic type identity only.", "reflection.html")]) + """
<h2 id="boundaries">Managed-runtime boundaries</h2><p>No CLR service exists behind these types: no GC, JIT, managed metadata universe, assembly loader or general interop layer. Read <a href="compatibility.html">Compatibility Philosophy</a> before assuming managed-only behavior.</p>"""),
        ("type-system.html", "Type System and Core Values", "Primitive aliases, wrappers, Object, Type, nullable, enums, date/time and conversions.", "Concepts", """
<h2 id="categories">Type categories</h2>""" + table(["Category", "Examples", "Native consideration"], [["Primitive aliases", "<code>intcs</code>, <code>longcs</code>, byte/unsigned aliases", "Fixed intent, but C++ overload/formatting rules apply"], ["Wrappers", "Numeric and value wrappers", "Copyable native values with curated .NET-shaped APIs"], ["Object / Type", "Base identity and runtime type naming", "Not a CLR metadata graph"], ["Array / Span / Memory", "Owned sequences and borrowed views", "View lifetime must not exceed backing storage"], ["Nullable / enums", "Optional/value and enum compatibility helpers", "Template and C++ enum semantics remain visible"], ["Date/time", "DateTime, DateOnly, TimeOnly, TimeSpan, TimeZoneInfo", "Local-zone and platform data matter"]]) + """
<h2 id="conversion">Conversion and validation</h2><p>Conversions and parsers are implemented per type. Edge behavior—including overflow, separators, culture and Try-output rules—has been an active compatibility-audit area; consult tests when contributing rather than copying an old overview count.</p>"""),
        ("strings.html", "Strings and Text", "Sharp Runtime UTF-8 strings, formatting, StringBuilder, encodings and Base64 behavior.", "Concepts", """
<h2 id="representation">Representation</h2><p>The common surface uses <code>std::string</code> and UTF-8-oriented helpers rather than a managed UTF-16 object representation. This affects indexing, length and slicing.</p>
<h2 id="builder">StringBuilder</h2><p>Current StringBuilder indices and counts are UTF-8 byte positions. Rune iteration exists for scalar-wise work; grapheme segmentation is not a general promise.</p>
<h2 id="formatting">Formatting</h2><p>Composite formatting and numeric conversion cover the implemented subset. Culture and floating-point boundaries need targeted tests in ports.</p>
<h2 id="components">Components</h2>""" + bullets(["<code>Text</code>: encoding, builders and text utilities", "<code>Text.RegularExpressions</code>: curated regex surface", "<code>Text.Json</code>: JSON document/reader/writer and serialization subset", "<code>Globalization</code>: culture and formatting data"]) + page_index([("StringBuilder tutorial", "Avoid UTF-16 indexing assumptions.", "tutorials/strings-and-builder.html"), ("Text components", "Complete family overview.", "components/text-data.html")])) ,
        ("arrays.html", "Arrays, Spans and Memory", "Owned arrays, borrowed spans, memory views and lifetime rules in Sharp Runtime.", "Concepts", """
<h2 id="owned">Owned sequences</h2><p>Array/vector-shaped types own or contain native values according to their declared C++ element type. Copy and move are native operations, not managed-reference assignments.</p>
<h2 id="views">Borrowed views</h2><p>Span- and memory-shaped APIs can reference existing storage. A span must not outlive or be invalidated by its owner; resizing a backing container is a common invalidation boundary.</p>
<h2 id="bounds">Bounds and units</h2><p>Use the API’s documented unit. For text-backed memory, bytes, Unicode scalar values and user-perceived characters are not interchangeable.</p>""" + callout("Lifetime cannot be checked by a GC", "<p>Returning a span into a temporary or retaining it after owner destruction is an ordinary C++ lifetime bug.</p>", "warning")),
        ("delegates.html", "Delegates, Events and Callables", "Typed Action, Func, Predicate and EventHandler behavior in native C++.", "Concepts", """
<h2 id="surface">Surface</h2><p>Action, Func, Predicate and EventHandler-shaped types support familiar typed callback patterns and composition for the implemented subset.</p>
<h2 id="differences">Differences from managed delegates</h2>""" + bullets(["No late-bound DynamicInvoke; calls are typed at compile time.", "Capture ownership is ordinary C++.", "Subscription does not make the target immortal.", "Async callbacks can cross teardown and synchronization boundaries."]) + """
<h2 id="practice">Safe practice</h2><p>Document who owns each callable, how it is unsubscribed or cancelled, and whether invocation is serialized. Prefer weak ownership when a publisher can outlive a subscriber.</p>"""),
        ("exceptions.html", "Exceptions and Error Semantics", "Sharp Runtime exception hierarchy, HResult values, causal exceptions and native translation differences.", "Concepts", """
<h2 id="hierarchy">Hierarchy</h2><p>The project provides a broad curated System exception hierarchy, including argument, I/O, networking, platform and implementation exceptions.</p>
<h2 id="hresult">HResult and causes</h2><p>Many specialized exceptions populate .NET-compatible HResult constants, and causal/inner errors use native exception pointers where supported. Recent remediation corrected derived exception values and network propagation.</p>
<h2 id="translation">Translation guidance</h2>""" + bullets(["Catch the narrow exception only when recovery differs.", "Preserve a causal exception when translating an OS/vendor failure.", "Do not infer an exception type from prose if tests/code define a different contract.", "NotImplemented and PlatformNotSupported are meaningful public boundaries, not generic failure buckets."]) + """
<h2 id="native">Native difference</h2><p>There is no CLR stack or managed exception filter machinery. C++ destruction/RAII runs during unwinding, and exception-safety of owned resources remains essential.</p>"""),
        ("reflection.html", "Reflection and Runtime Type Identity", "What Sharp Runtime Type and type-name helpers provide—and what full CLR reflection it omits.", "Concepts", """
<h2 id="provided">Provided</h2>""" + bullets(["Basic runtime type identity and names", "<code>Object</code>/<code>Type</code>-shaped compatibility", "Macros/helpers used by the project’s native object model", "Selected runtime attributes and marker types"]) + """
<h2 id="not-provided">Not provided</h2>""" + bullets(["A CLR metadata universe", "Assembly discovery/loading", "General member enumeration", "Late-bound construction or method invocation", "DynamicInvoke", "Reflection-driven BinaryFormatter or universal JSON serialization"]) + callout("Porting implication", "<p>Replace reflection-heavy C# designs with explicit registries, templates, variants or typed factories. Do not build new code around marker APIs as if full reflection will appear behind them.</p>", "warning")),
        ("io.html", "I/O, Files and Streams", "Sharp Runtime streams, files, directories, readers/writers and filesystem portability.", "Concepts", """
<h2 id="surface">Surface</h2>""" + bullets(["Stream and MemoryStream", "FileStream plus File, Directory and Path helpers", "Text and binary readers/writers", "Filesystem watcher-related surfaces", "Compression, ZIP and isolated storage through separate components"]) + """
<h2 id="contracts">Contracts</h2><p>Capability queries, lifecycle behavior, argument validation and partial reads/writes are part of the public contract. Recent audits found and corrected many assumptions in this area; old summaries are not authoritative.</p>
<h2 id="portability">Portability</h2><p>Filesystem naming, permissions, links, sharing and watchers differ by platform. Handle errors at the operation boundary and avoid assuming POSIX-only behavior where Windows paths now exist.</p>""" + page_index([("I/O component family", "Dependencies and boundaries.", "components/io-storage.html"), ("File tutorial", "Practical lifecycle guidance.", "tutorials/work-with-files.html"), ("Compression tutorial", "Compression, ZIP and hashing.", "tutorials/compression-hashing.html")])) ,
        ("threading.html", "Threading, Tasks and Timers", "Native threads, synchronization, cancellation, tasks, channels and timer behavior.", "Concepts", """
<h2 id="threading">Threading</h2><p>Thread, mutex, semaphore, monitor and cancellation-shaped surfaces use native synchronization. Thread safety is per type; a namespace name does not make global state safe.</p>
<h2 id="tasks">Tasks</h2><p>Task and continuation APIs support porting patterns, but C++ syntax and native scheduling remain explicit. There is no synchronization context supplied by a CLR.</p>
<h2 id="channels">Channels and timers</h2><p>Channels provide producer/consumer flow; timers schedule callbacks. Both require explicit cancellation, completion and lifetime protocols.</p>""" + callout("Shutdown is a design", "<p>Destroying an owner while work, continuations or timer callbacks can still touch it is unsafe. Build teardown into the API.</p>", "warning") + page_index([("Concurrency components", "Component boundaries.", "components/concurrency.html"), ("Tasks tutorial", "Cancellation and lifetime.", "tutorials/tasks-cancellation.html")])) ,
        ("csharp-compatibility.html", "Porting C# Patterns", "Quick mapping from C# managed concepts to deliberate native C++ Sharp Runtime patterns.", "Guides", """
<h2 id="values">Common value mappings</h2>""" + table(["C#", "Sharp Runtime / C++ direction", "Important difference"], [["<code>string</code>", "<code>System::String</code> helpers over <code>std::string</code>", "UTF-8 bytes, not a managed UTF-16 object"], ["<code>bool</code>, integer aliases", "<code>boolcs</code>, <code>intcs</code>, <code>longcs</code> and related aliases", "C++ overload and promotion rules remain visible"], ["<code>char</code>", "<code>charcs</code> / <code>char16_t</code>", "Do not confuse a UTF-16 code unit with a UTF-8 byte"], ["<code>T?</code>", "<code>Nullable&lt;T&gt;</code> / optional-value pattern", "Contained values use native construction and copying"], ["reference type", "Value, <code>unique_ptr</code>, <code>shared_ptr</code>, <code>weak_ptr</code>, reference or pointer", "The port must choose ownership explicitly"]]) + """
<h2 id="map">Pattern map</h2>""" + table(["C# concept", "Native porting direction", "Compatibility boundary"], [["Managed class reference", "Explicit owner: value, unique/shared pointer, or borrowed reference", "No GC or universal object identity"], ["Property", "Named getter/setter or the project’s property helper where established", "A helper is compile-time C++; it creates no runtime metadata"], ["<code>Action</code>/<code>Func</code>/<code>Predicate</code>", "Typed callable, principally <code>std::function</code>-shaped", "Captures have ordinary C++ lifetime"], ["Event", "Typed callback collection plus explicit subscription protocol", "Publisher/subscriber lifetime is not managed"], ["Exception", "Specific Sharp Runtime exception when the contract exists", "C++ RAII runs during unwinding; no CLR stack services"], ["List/Dictionary", "Select Collections.Core and decide value/identity ownership", "Mutation, iterator and comparer rules must be verified"], ["<code>async</code>/<code>await</code>", "Explicit Task/continuation/cancellation flow—or idiomatic native concurrency", "No C# language syntax or ambient synchronization context"], ["Reflection", "Explicit registry, templates, variants or typed factories", "<code>Type</code> is basic RTTI, not a metadata universe"], ["<code>Activator.CreateInstance&lt;T&gt;</code>", "Compile-time templated activation where supported", "No general <code>Type</code>-driven construction"], ["<code>IDisposable</code>", "RAII plus compatibility-shaped Dispose where needed", "Destructors remain the safety net"], ["P/Invoke / COM", "Write an explicit native boundary outside the compatibility facade", "No CLR marshaller or DLL-binding service"]]) + """
<h2 id="workflow">Workflow</h2>""" + bullets(["Inventory observable behavior and managed-only dependencies.", "Design ownership and concurrency before translating syntax.", "Select the narrow Sharp Runtime components.", "Port one behavior slice with tests.", "Record reductions explicitly where exact parity is impossible or intentionally omitted."]) + page_index([("Deep porting guide", "End-to-end process.", "guides/porting-csharp.html"), ("Memory and ownership", "Native lifetime model.", "memory-management.html"), ("Compatibility philosophy", "Scope and exclusions.", "compatibility.html")])) ,
        ("guides/porting-csharp.html", "Porting C# to Native C++", "A systematic workflow for porting C# code with Sharp Runtime while respecting native ownership and compatibility boundaries.", "Guides", """
<h2 id="inventory">1. Inventory managed assumptions</h2>""" + bullets(["Reference identity and object graph ownership", "GC-dependent lifetime or finalization", "Reflection, serialization, DynamicInvoke or AppDomain use", "async/await, synchronization context and cancellation", "UTF-16 indexing and culture-sensitive text", "TLS, certificates, P/Invoke or platform services"]) + """
<h2 id="select">2. Select compatibility surfaces</h2><p>Map the required APIs to physical components. Keep deliberate rewrites—such as reflection registries or secure transport—outside a false compatibility layer.</p>
<h2 id="ownership">3. Design native ownership</h2><p>Choose values, unique owners, shared owners and borrows. Sketch callback and async lifetime before implementation.</p>
<h2 id="translate">4. Translate behavior slices</h2><p>Port one cohesive class or subsystem with its boundary tests. Preserve observable validation and exception behavior only where the implemented Sharp Runtime contract supports it.</p>
<h2 id="verify">5. Verify reductions</h2>""" + table(["Risk", "Verification"], [["String indices", "Non-ASCII and malformed UTF-8 cases"], ["Numeric behavior", "Overflow, NaN, infinity, signed zero and compiler capabilities"], ["Collections", "Mutation/enumerator invalidation and comparer policy"], ["I/O", "Short operations, lifecycle, permissions and platform paths"], ["Concurrency", "Cancellation, teardown, exception observation and races"], ["Networking", "DNS/connect/protocol distinctions and TLS boundary"]]) + """
<h2 id="choose-native">6. Prefer idiomatic C++ when compatibility adds no value</h2><p>Sharp Runtime is a tool for practical ports, not a requirement to preserve every managed design. A native value, standard range or explicit factory is often clearer than emulating a managed-only mechanism.</p>"""),
        ("project-structure.html", "Project Structure", "Current Sharp Runtime module layout, CMake registration, tests, vendor dependencies and audit material.", "Development", """
<h2 id="layout">Repository map</h2>""" + table(["Path", "Purpose"], [["<code>modules/&lt;module&gt;/include</code>", "Public header ownership"], ["<code>modules/&lt;module&gt;/src</code>", "Compiled implementation for static components"], ["<code>modules/&lt;module&gt;/tests</code>", "Owning component’s GoogleTest sources"], ["<code>cmake/SharpRuntimeModules.cmake</code>", "Physical module enumeration"], ["<code>cmake/SharpRuntimeComponents.cmake</code>", "Registration and enablement engine"], ["<code>tests/integration</code>", "Cross-component test scenarios"], ["<code>test/consumers</code>", "Positive and negative consumer fixtures"], ["<code>scripts/</code>", "Catalogue, boundary and local-CI tooling"], ["<code>docs/</code>", "Generated catalogue plus engineering decisions/reviews"], ["<code>audit/</code>", "Historical/current audit evidence—not automatically public truth"], ["<code>vendor/</code>", "Vendored libraries and the GoogleTest submodule"]]) + """
<h2 id="inventory">Pinned tracked inventory</h2><p>The current tree has 1,032 public module headers, 217 production translation units, 477 component test sources and nine integration test sources. These are audit facts, not a promise to keep mutable counts in every page.</p>"""),
        ("api/index.html", "API Discovery", "Curated Sharp Runtime API navigation by concepts, components and low-level source reference.", "API", """
<h2 id="strategy">Layered reference strategy</h2>""" + table(["Layer", "Use it for"], [["Concept guides", "Ownership, compatibility and subsystem behavior"], ["Component family pages", "Targets, dependencies and capability boundaries"], ["Class pages", "High-value foundational types"], ["Source/Doxygen", "Exact signatures and member-level details at the pinned revision"]]) + """
<h2 id="browse">Browse curated reference</h2>""" + page_index([("Components", "All {{physical_components}} physical targets.", "../components/index.html"), ("Core classes", "Object, String, Array, Nullable and exceptions.", "../classes/index.html"), ("Type system", "Values and runtime identity.", "../type-system.html"), ("I/O", "Streams and filesystem.", "../io.html"), ("Networking", "HTTP, sockets and transport limits.", "../components/networking.html"), ("Concurrency", "Threads, tasks, channels and timers.", "../threading.html")]) + """
<h2 id="doxygen">Low-level source reference</h2><p>The runtime has a reproducible Doxygen configuration and a CI warning ceiling, but its current warning baseline remains large. This site therefore does not publish a noisy generated dump as if it were curated reference. For exact declarations, follow the representative header in the component catalogue to the pinned source.</p>""" + callout("Reference freshness", "<p>Curated pages state concepts and boundaries. Exact overload lists belong to generated/source-level documentation and tests, reducing hand-maintained API drift.</p>")),
        ("modules/index.html", "Module Reference (Compatibility URL)", "Compatibility entry point for the complete current Sharp Runtime component catalogue.", "Components", """
<h2 id="moved">The module catalogue has expanded</h2><p>The old page described a small subset. The definitive catalogue now covers every current physical CMake component, its kind, representative public header, direct dependencies and external/platform attachment.</p>""" + page_index([("Complete component catalogue", "All {{physical_components}} physical components.", "../components/index.html"), ("Core and collections", "Foundation family.", "../components/core.html"), ("Text and data", "Text, JSON and XML.", "../components/text-data.html"), ("I/O and storage", "Streams, archives and storage.", "../components/io-storage.html"), ("Networking", "Sockets through WebSockets.", "../components/networking.html"), ("Concurrency", "Threads, tasks and timers.", "../components/concurrency.html")]) + callout("URL preserved", "<p>This public URL remains useful for existing inbound links; canonical discovery continues through the complete catalogue.</p>")),
        ("modules/collections.html", "Collections Module Family", "Compatibility URL for current Sharp Runtime collection components and semantics.", "Components", "<p>The older broad Collections page now maps to the four physical collection components: Core, Blocking, Async and ObjectModel.</p>" + page_index([("Current family page", "Targets, closures and behavior.", "../components/core.html"), ("Collections tutorial", "Native ownership and versioning.", "../tutorials/use-collections.html")])) ,
        ("modules/text.html", "Text Module Family", "Compatibility URL for Text, Regex, JSON and XML documentation.", "Components", "<p>Text, regular expressions and JSON are distinct current components; XML is documented alongside them as a data/text family.</p>" + page_index([("Current text/data page", "Targets and boundaries.", "../components/text-data.html"), ("Strings", "UTF-8 semantics.", "../strings.html"), ("JSON tutorial", "Curated serialization scope.", "../tutorials/json.html")])) ,
        ("modules/net.html", "Networking Module Family", "Compatibility URL for current Net, sockets, HTTP, MIME, network information and WebSockets components.", "Components", "<p>The current architecture has nine networking components rather than one blanket Net module.</p>" + page_index([("Current networking page", "All networking targets and caveats.", "../components/networking.html"), ("HTTP tutorial", "Transport boundaries.", "../tutorials/http.html"), ("Platforms", "Evidence labels.", "../platform-layer.html")])) ,
        ("modules/globalization.html", "Globalization Module", "Culture, parsing, formatting and portability boundaries in Sharp Runtime.", "Components", "<p>Globalization provides a curated culture/calendar/Unicode/number surface. Locale data, collation and grapheme behavior must be evaluated per API and platform.</p>" + page_index([("Numerics/globalization family", "Targets and current boundaries.", "../components/numerics-globalization.html"), ("Platforms", "Platform validation depth.", "../platform-layer.html")])) ,
        ("modules/numerics.html", "Numerics Module", "Vectors, matrices, quaternion, BigInteger, Decimal and compiler capability boundaries.", "Components", "<p>Numerics includes vector/matrix/quaternion types plus BigInteger, Decimal and wide wrappers. Native <code>__int128</code> is probed at configure time; compiler limits are public behavior.</p>" + page_index([("Current family page", "Numerics, globalization and crypto.", "../components/numerics-globalization.html"), ("Known limitations", "Current numeric/compiler caveats.", "../development/known-limitations.html")])) ,
        ("modules/diagnostics.html", "Diagnostics Module", "Sharp Runtime diagnostic/code-analysis and process-oriented surfaces.", "Components", "<p>Diagnostics contains diagnostic and code-analysis-related types plus selected process behavior. Platform facilities vary; the namespace is not a managed diagnostics runtime.</p>" + page_index([("Current family page", "Diagnostics and Runtime targets.", "../components/numerics-globalization.html"), ("Platforms", "Evidence matrix.", "../platform-layer.html")])) ,
        ("classes/index.html", "Core Class Reference", "Curated reference for important foundational Sharp Runtime types.", "API", page_index([("Object", "Native base identity.", "object.html"), ("String", "UTF-8 helpers.", "string.html"), ("Array", "Owned sequence helpers.", "array.html"), ("Nullable", "Optional value patterns.", "nullable.html"), ("Exception", "Error hierarchy.", "exception.html"), ("EventHandler", "Typed events.", "eventhandler.html")]) + "<h2 id=\"more\">More APIs</h2><p>Use the <a href=\"../components/index.html\">component catalogue</a> to locate a representative public header, then consult the pinned source for exact overloads.</p>"),
        ("classes/object.html", "System::Object", "Native base identity and object-model boundaries.", "API", "<p><code>System::Object</code> anchors familiar identity/type behavior for the implemented subset. It is not backed by a CLR object header, garbage collector or universal reflection metadata.</p><h2 id=\"lifetime\">Lifetime</h2><p>Derived instances follow ordinary C++ construction, virtual destruction, copy/move and ownership rules.</p>"),
        ("classes/string.html", "System::String Helpers", "UTF-8 string helpers, formatting and compatibility differences.", "API", "<p>The common string representation is native <code>std::string</code>/UTF-8. Helpers provide familiar operations; indices and Unicode behavior must be checked rather than assumed from .NET UTF-16 semantics.</p>" + page_index([("Strings concept", "Representation and components.", "../strings.html"), ("StringBuilder tutorial", "Byte-index caveats.", "../tutorials/strings-and-builder.html")])) ,
        ("classes/array.html", "System::Array Helpers", "Curated array operations and native ownership considerations.", "API", "<p>Array-shaped helpers operate over native owned sequences for the implemented subset. Element copy, identity and lifetime follow the C++ element type.</p>" + page_index([("Arrays and memory", "Owned and borrowed sequences.", "../arrays.html"), ("Type system", "Value categories.", "../type-system.html")])) ,
        ("classes/nullable.html", "Nullable Values", "Optional value compatibility patterns in Sharp Runtime.", "API", "<p>Nullable-shaped templates model the presence or absence of a native value. Construction, copying and the contained type’s lifetime follow ordinary C++ semantics.</p>"),
        ("classes/exception.html", "System::Exception", "Base exception behavior, messages, HResult and causal exceptions.", "API", "<p>The base exception anchors the implemented hierarchy. Specialized types carry contract-specific defaults and, where implemented, .NET-compatible HResult values and causal exception pointers.</p>" + page_index([("Exception guide", "Hierarchy and translation.", "../exceptions.html"), ("Known limitations", "NotImplemented and platform boundaries.", "../development/known-limitations.html")])) ,
        ("classes/eventhandler.html", "EventHandler", "Typed event callback behavior and native capture lifetime.", "API", "<p>EventHandler-shaped APIs provide familiar typed event patterns. Publisher/subscriber ownership and capture lifetime are not managed by a garbage collector.</p>" + page_index([("Delegate guide", "Composition and limits.", "../delegates.html"), ("Events tutorial", "Safe callback lifetime.", "../tutorials/use-events.html")])) ,
        ("development/index.html", "Development Guide", "Contribute APIs and components while preserving Sharp Runtime behavior, boundaries and portability.", "Development", page_index([("Adding runtime features", "Implementation workflow.", "adding-runtime-features.html"), ("Known limitations", "Current public gaps.", "known-limitations.html"), ("Testing", "Layered validation.", "../running-tests.html"), ("Project structure", "Ownership map.", "../project-structure.html"), ("Debugging", "Failures and selective builds.", "debugging.html"), ("Coding style", "Conventions and evidence.", "coding-style.html")]) + "<h2 id=\"principle\">Contribution principle</h2><p>Implement the smallest correct behavioral slice, own it in one physical component, declare its real edges and prove it with positive, negative and boundary tests.</p>"),
        ("development/known-limitations.html", "Known Limitations", "Current non-goals, partial APIs, platform limits and known verification gaps at the pinned Sharp Runtime revision.", "Development", """
<h2 id="non-goals">Deliberate non-goals</h2>""" + bullets(["CLR/JIT/GC and arbitrary managed assembly execution", "General reflection/member enumeration and DynamicInvoke", "P/Invoke, remoting and AppDomain assembly infrastructure", "BinaryFormatter-style general serialization", "C# language async/await in C++"]) + """
<h2 id="partial">Important partial or reduced surfaces</h2>""" + table(["Area", "Current boundary"], [["Text", "UTF-8 storage means some indices/lengths differ from .NET UTF-16; StringInfo lacks general grapheme segmentation"], ["Reflection", "Basic type identity, not member metadata or dynamic invocation"], ["OperatingSystem", "Platform identity is available; real OS version detection/comparison is reduced"], ["TimeZoneInfo", "Serialized-string round trip is not implemented"], ["Networking", "Some base virtuals intentionally throw; Emscripten DNS unavailable; WebProxy default lookup follows platform-limited behavior"], ["WebSockets", "<code>ws://</code> only; <code>wss://</code> throws"], ["XML/XPath", "Curated XPath subset; variables/custom functions/extension context absent"], ["LocalDataStoreSlot", "Thread-local per-slot semantics remain a stub"], ["Guid", "Rare X/Open and Microsoft variant normalization is not implemented"]]) + """
<h2 id="security">Security boundary</h2><p>Implemented hashing, HMAC, PBKDF2 and secure random are not a complete cryptographic platform. Encryption algorithms, certificates, TLS, HTTPS, WSS and <code>SslStream</code> are not part of the current public promise.</p>
<h2 id="platform">Platform/compiler limits</h2>""" + bullets(["Current hosted CI validates Ubuntu only.", "MSVC lacks the native <code>__int128</code> capability used by some numeric surfaces.", "Emscripten cannot provide several native DNS/network/process/filesystem facilities.", "Android storage expects SDL3 from the parent build.", "Console cursor/color behavior is ANSI-terminal oriented."]) + """
<h2 id="high-impact">High-impact current limitations</h2>""" + bullets(["<strong>Network transport:</strong> HTTP is buffered plain HTTP/1.1 over TCP; no redirects or TLS. WebSockets support <code>ws://</code>, not <code>wss://</code>.", "<strong>Async lifetime:</strong> several socket, HTTP and WebSocket task wrappers capture raw owners or caller buffers; keep them alive until completion.", "<strong>Text/globalization:</strong> Unicode normalization is effectively ASCII/no-op beyond the reduced surface; several encoding indices count UTF-8 bytes; culture, collation, casing and grapheme behavior are limited.", "<strong>Time zones:</strong> Windows/POSIX paths exist, but the model largely uses fixed current offsets with no transition rules, ambiguity/invalid-time model or serialized form.", "<strong>Storage:</strong> isolated storage is organizational, not a security sandbox. Use trusted relative paths; absolute paths, <code>..</code> and symlink confinement are not comprehensively contained.", "<strong>Platform APIs:</strong> FileSystemWatcher and NetworkInterface are Linux-specific; Process is POSIX-only; Emscripten threading requires pthreads and whole-program/browser configuration.", "<strong>Compiler boundary:</strong> Decimal/Int128/UInt128 surfaces require native <code>__int128</code>, limiting current MSVC/i686 coverage."]) + """
<h2 id="known-tests">Known full-gate conditions</h2><p>The latest controlled recorded full gate had {{gate_failed_words}}: five Ping cases were triggered by <code>ping_group_range</code> and expose a real missing raw-ICMP receive fallback; one socket/interface case depended on a missing <code>/proc/net/if_inet6</code>. The current pinned source adds {{timezone_additions}} passing TimeZone cases after that record; no post-merge controlled full-gate result is claimed.</p>""" + callout("A limitation page, not an audit-ticket dump", "<p>Internal audit findings are translated into user-facing behavior here. Fixed findings and project-management identifiers are not published as if they were current defects.</p>")),
        ("development/adding-runtime-features.html", "Adding Runtime Features", "Implement a Sharp Runtime API with evidence, ownership, tests and component boundaries.", "Development", """
<h2 id="evidence">1. Establish the contract</h2><p>Read the current implementation, headers, upstream reference source where applicable and existing tests. Treat project prose and audit tickets as evidence to corroborate—not automatic truth.</p>
<h2 id="owner">2. Choose the owner</h2><p>Place the header/source/test under one physical module. Declare PUBLIC edges for headers, PRIVATE edges for implementation and TEST edges only for the test binary.</p>
<h2 id="slice">3. Implement a bounded slice</h2>""" + bullets(["Validate parameters before mutation.", "Preserve exception type and causal error where established.", "Define ownership, copy/move and disposal behavior.", "Document intentional reductions and platform guards."]) + """
<h2 id="test">4. Test behavior and boundaries</h2><p>Add normal, invalid, boundary and lifetime tests. For public includes or target behavior, add selective/negative consumer fixtures.</p>
<h2 id="validate">5. Validate</h2>""" + code("""python3 scripts/validate_module_boundaries.py
python3 scripts/generate_component_catalog.py --check
scripts/check_selective_components.sh
scripts/local_ci_check.sh build""", "bash")),
        ("development/debugging.html", "Debugging Sharp Runtime", "Diagnose component selection, exceptions, platform failures, concurrency and native memory errors.", "Development", """
<h2 id="classify">Classify first</h2>""" + table(["Symptom", "First question"], [["Configure failure", "Unknown component, missing external dependency or Android parent target?"], ["Header missing", "Is the owning component linked, or is a private header leaking?"], ["Link failure", "Is an implementation dependency declared with correct visibility?"], ["Test failure", "Behavior defect or unavailable host facility?"], ["Crash/use-after-free", "Which native owner or callback outlived its target?"], ["Race/deadlock", "What cancellation/join/lock order is documented?"]]) + """
<h2 id="tools">Useful tools</h2>""" + bullets(["Component boundary validator and selective fixtures", "GoogleTest filters on the owning executable", "ASan/UBSan for native memory and undefined behavior", "TSan for shared state where the toolchain supports it", "Debugger breakpoints on specific Sharp Runtime exception construction", "CMake target/property inspection rather than global include hacks"]) + """
<h2 id="network">Network tests</h2><p>Record permissions, namespace/container restrictions, DNS state, <code>ping_group_range</code> and interface files. An environment-limited result and an implementation defect require different fixes.</p>"""),
        ("development/coding-style.html", "Coding and Documentation Style", "Sharp Runtime naming, component boundaries, portability and evidence conventions.", "Development", """
<h2 id="principles">Principles</h2>""" + bullets(["Use human-facing “Sharp Runtime”; reserve <code>sharp-runtime</code> for repository/path/command identities.", "Match the existing System namespace/type spelling where implementing a compatibility API.", "Keep C++ ownership and const/copy/move behavior explicit.", "Place APIs under the narrow physical owner and declare real edge visibility.", "Compile with the project’s warnings-as-errors policy.", "Document reductions and platform limits next to the behavior."]) + """
<h2 id="evidence">Documentation evidence</h2><p>Do not copy a mutable count or platform claim from an older summary. Prefer implementation, CMake registration, generated current metadata, tests and measured gate output.</p>"""),
        ("development/porting-csharp-code.html", "Porting C# Code (Compatibility URL)", "Compatibility entry point for the current Sharp Runtime C# porting guide.", "Guides", "<p>The porting guide now separates managed assumptions, native ownership, component selection and behavioral verification.</p>" + page_index([("Current porting guide", "End-to-end workflow.", "../guides/porting-csharp.html"), ("Pattern map", "Quick compatibility mapping.", "../csharp-compatibility.html"), ("Port a class tutorial", "A bounded practical exercise.", "../tutorials/port-csharp-class.html")])) ,
        ("internals/index.html", "Sharp Runtime Internals", "Component boundaries, object lifecycle, strings, arrays and property helper internals.", "Internals", page_index([("Component architecture", "Registration and edge visibility.", "../architecture.html"), ("Object lifecycle", "Construction, destruction and virtual behavior.", "object-lifecycle.html"), ("Array internals", "Owned sequence and view boundaries.", "array-internals.html"), ("String internals", "UTF-8 representation.", "string-internals.html"), ("Property helpers", "Compatibility macros and accessors.", "property-macros.html"), ("Testing", "Boundary and negative fixtures.", "../running-tests.html")]) + "<h2 id=\"audience\">Audience</h2><p>These pages are for contributors and advanced consumers. Public API contracts still live in headers/tests; internals may change without preserving implementation detail.</p>"),
        ("internals/object-lifecycle.html", "Object Lifecycle Internals", "Construction, virtual destruction, native ownership and compatibility-shaped disposal.", "Internals", """
<h2 id="model">Native object model</h2><p><code>System::Object</code> is an abstract base for participating Sharp Runtime class hierarchies, not a hidden header attached to every C++ value. Construction, destruction, copying and moving remain ordinary C++. Its virtual destructor makes deletion through an Object base safe; it does not imply garbage collection.</p>
<p><code>System::GC</code> is a compatibility no-op. It cannot find unreachable objects, break reference cycles, move allocations or extend a borrowed lifetime.</p>
<h2 id="ownership">Ownership vocabulary</h2>""" + table(["Form", "Use", "Porting consequence"], [["Stack/value member", "Small values with clear containing lifetime", "Copy/move follows the value type"], ["<code>std::unique_ptr&lt;T&gt;</code>", "One transferable owner", "Closest expression of exclusive ownership"], ["<code>std::shared_ptr&lt;T&gt;</code>", "Genuinely shared lifetime", "Cycles still leak unless a back edge is weak"], ["<code>std::weak_ptr&lt;T&gt;</code>", "Observation without keeping the target alive", "Lock and handle expiry at every use"], ["Reference/raw pointer", "Short, documented borrow or interop boundary", "Owner must outlive every access"], ["Span/Memory/ArraySegment", "Borrowed view into existing storage", "Reallocation or owner destruction invalidates the view"]]) + """
<h2 id="dispose">Dispose-shaped APIs</h2><p>Where present, <code>Dispose</code> aids source compatibility and deterministic release. The C++ destructor must still leave the type safe under scope exit and exception unwinding. A port should make repeated disposal and post-disposal behavior explicit rather than assuming the CLR contract.</p>
<h2 id="exceptions">Surfaces that need extra care</h2>""" + bullets(["Some collection enumerator and Keys/Values APIs return owning raw heap pointers; the caller must delete them.", "<code>MemoryHandle</code> has an explicit Dispose contract.", "Reference-taking BlockingCollection constructors keep a no-delete shared wrapper; the referenced collection must outlive the wrapper.", "Several asynchronous socket, HTTP and WebSocket operations capture a raw owner or caller buffer; both must survive task completion.", "Delegates and event subscriptions keep the ownership expressed by their C++ captures—not a managed target root."]) + """
<h2 id="copy-move">Copy, move and shutdown</h2><p>For each resource-owning type, decide whether copying duplicates a value, shares a handle, or must be disabled. Moving must leave a destructible source. For asynchronous owners, shutdown normally means: prevent new work, request cancellation, wait or join, detach subscriptions, then release state.</p>""" + callout("Audit lifetime at boundaries", "<p>The most dangerous compatibility bugs live where an API looks managed but stores a native borrow. Record the owner, invalidation events, and thread that may perform the last access.</p>", "warning")),
        ("internals/array-internals.html", "Array and Memory Internals", "Owned buffers, spans, bounds and invalidation behavior.", "Internals", "<p>Owned containers and borrowed views are deliberately distinct. Bounds use the declared native units, and mutation/reallocation can invalidate pointers, iterators and spans.</p>"),
        ("internals/string-internals.html", "String Internals", "UTF-8 representation, byte indexing and Unicode-aware iteration boundaries.", "Internals", "<p>The runtime reduces managed UTF-16 strings to UTF-8 native storage. This is a central compatibility tradeoff: interoperability and compact storage improve, while some indices and lengths change units.</p>"),
        ("internals/property-macros.html", "Property Helpers and Macros", "How Sharp Runtime expresses C#-shaped properties in native C++.", "Internals", """
<h2 id="purpose">Compile-time convenience only</h2><p>The helpers in <code>SharpRuntime/Prop.hpp</code> produce ordinary members and functions with predictable names. They do not create CLR properties, metadata, dynamic dispatch or automatic validation.</p>
<h2 id="declarations">Declaration helpers</h2>""" + table(["Macro", "Generated shape"], [["<code>DDATA(type, name)</code>", "Private <code>type name_</code>, a const-reference getter, and const-reference plus rvalue setters"], ["<code>DGETTER(type, name)</code>", "Private backing member and const-reference getter only"], ["<code>DGETTERSTATIC(type, name)</code>", "Static backing member and static const-reference getter"]]) + code("""class Settings {
    DDATA(std::string, Label)
    DGETTER(int, Generation)
public:
    Settings(std::string label, int generation)
        : Label_(std::move(label)), Generation_(generation) {}
};

// Generated names include:
// const std::string& getLabelProperty() const;
// void setLabelProperty(const std::string& value);
// void setLabelProperty(std::string&& value);
// const int& getGenerationProperty() const;""", "cpp") + """
<h2 id="definitions">Out-of-class definitions</h2><p><code>IDATA(type, name, clazz)</code>, <code>IGETTER(type, name, clazz)</code> and <code>IGETTERSTATIC(type, name, clazz, init)</code> emit the corresponding definitions and, for the static form, initialization. Parameter order matters; older prose used incompatible signatures.</p>
<h2 id="type-names">Type-name helpers</h2><p><code>GETTYPENAME_HPP</code> declares the virtual type-name accessor, while <code>GETTYPENAME_CPP(Class, "Name")</code> defines it using a stable static string. This is native identity plumbing, not full reflection.</p>
<h2 id="guidance">Contributor guidance</h2>""" + bullets(["Follow the established pattern in the owning module rather than introducing a new property dialect.", "Keep validation and invariants visible in a method when a generated setter would be too permissive.", "Do not hide ownership transfer, allocation, blocking I/O or expensive computation behind property syntax.", "Prefer explicit accessors where a debugger, caller or generated documentation benefits from seeing the contract."]) + callout("Generated names are part of source compatibility", "<p>Before changing a macro, search its declarations and out-of-class definition helpers together. A harmless-looking signature change can affect many headers.</p>", "warning")),
    ]
    pages = []
    for path, title, desc, category, body in specs:
        pages.append(Page(path, title, desc, category, intro(title, desc, [category, f"Source {SOURCE_SHA[:8]}"]) + body, title.lower().split() + [category.lower()]))
    return pages


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def relative(from_path: str, to_path: str) -> str:
    from_dir = Path(from_path).parent
    result = Path(to_path)
    try:
        return str(result.relative_to(from_dir)) if from_dir != Path(".") else str(result)
    except ValueError:
        depth = len(from_dir.parts)
        return "../" * depth + str(result)


NAV = [
    ("Home", "index.html"), ("Start", "getting-started.html"), ("Guides", "guides/porting-csharp.html"),
    ("Components", "components/index.html"), ("API", "api/index.html"), ("Tutorials", "tutorials/index.html"),
]

SIDEBAR = [
    ("Overview", [("What is Sharp Runtime?", "overview.html"), ("Architecture", "architecture.html"), ("Runtime model", "runtime-overview.html"), ("Compatibility", "compatibility.html"), ("Platforms", "platform-layer.html")]),
    ("Get started", [("Getting Started", "getting-started.html"), ("Build & integration", "build.html"), ("Testing & verification", "running-tests.html")]),
    ("Guides", [("Port C# to C++", "guides/porting-csharp.html"), ("Memory & ownership", "memory-management.html"), ("Exceptions", "exceptions.html"), ("CNA integration", "cna-integration.html"), ("Known limitations", "development/known-limitations.html")]),
    ("Components", [("Complete catalogue", "components/index.html"), ("Core & collections", "components/core.html"), ("Text, JSON & XML", "components/text-data.html"), ("I/O & storage", "components/io-storage.html"), ("Networking", "components/networking.html"), ("Concurrency", "components/concurrency.html"), ("Numerics & globalization", "components/numerics-globalization.html")]),
    ("Concepts", [("Type system", "type-system.html"), ("Strings", "strings.html"), ("Arrays & memory", "arrays.html"), ("Delegates & events", "delegates.html"), ("Reflection", "reflection.html"), ("I/O", "io.html"), ("Threading & tasks", "threading.html")]),
    ("Develop", [("Development guide", "development/index.html"), ("Project structure", "project-structure.html"), ("Adding features", "development/adding-runtime-features.html"), ("Debugging", "development/debugging.html"), ("Internals", "internals/index.html")]),
]


def head(page: Page) -> str:
    canonical = BASE if page.path == "index.html" else urljoin(BASE, page.path)
    social_image = BASE + "assets/og-card.png"
    title = page.title if page.path == "index.html" else f"{page.title} | Sharp Runtime"
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": page.page_type, "headline" if page.page_type == "TechArticle" else "name": page.title, "description": page.description, "url": canonical, "image": social_image, "isPartOf": {"@id": BASE + "#website"}},
            {"@type": "WebSite", "@id": BASE + "#website", "name": "Sharp Runtime", "url": BASE, "potentialAction": {"@type": "SearchAction", "target": BASE + "search.html?q={search_term_string}", "query-input": "required name=search_term_string"}},
        ],
    }
    if page.path != "index.html":
        breadcrumb_items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE}]
        if page.category != page.title:
            breadcrumb_items.append({"@type": "ListItem", "position": len(breadcrumb_items) + 1, "name": page.category})
        breadcrumb_items.append({"@type": "ListItem", "position": len(breadcrumb_items) + 1, "name": page.title, "item": canonical})
        data["@graph"].append({"@type": "BreadcrumbList", "itemListElement": breadcrumb_items})
    root = relative(page.path, "")
    assets = relative(page.path, "assets/style.css")
    favicon = relative(page.path, "favicon.svg")
    robots = '  <meta name="robots" content="noindex, follow">\n' if not page.indexable else ""
    return f"""<!doctype html>
<html lang="en" data-search-url="{e(relative(page.path, 'search.html'))}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(page.description)}">
{robots}  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="{'website' if page.path == 'index.html' else 'article'}">
  <meta property="og:site_name" content="Sharp Runtime">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(page.description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{social_image}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Sharp Runtime component architecture illustration">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{e(title)}">
  <meta name="twitter:description" content="{e(page.description)}">
  <meta name="twitter:image" content="{social_image}">
  <meta name="twitter:image:alt" content="Sharp Runtime component architecture illustration">
  <link rel="icon" href="{favicon}" type="image/svg+xml">
  <link rel="stylesheet" href="{assets}">
  <script>(function(){{try{{var t=localStorage.getItem('sharp-runtime-theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}}catch(_){{}}}})();</script>
  <script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>
</head>"""


def nav(page: Page) -> str:
    navlinks = []
    for label, target in NAV:
        current = page.path == target or (target.startswith("components/") and page.path.startswith("components/")) or (target.startswith("tutorials/") and page.path.startswith("tutorials/")) or (target.startswith("guides/") and page.path.startswith("guides/"))
        aria = ' aria-current="page"' if current else ""
        navlinks.append(f'<a class="nav-link" href="{relative(page.path, target)}"{aria}>{label}</a>')
    return f"""<a class="skip-link" href="#main-content">Skip to content</a>
<nav class="site-nav" aria-label="Primary"><div class="nav-inner">
  <a class="brand" href="{relative(page.path, 'index.html')}"><span class="brand-mark" aria-hidden="true">SR</span><span class="brand-word">Sharp Runtime</span></a>
  <div class="nav-links" id="primary-navigation">{''.join(navlinks)}<a class="nav-link" href="{relative(page.path, 'search.html')}">Search</a><a class="nav-link nav-link--github" href="https://github.com/openeggbert/sharp-runtime">GitHub</a></div>
  <button class="nav-toggle" type="button" aria-label="Open navigation" aria-controls="primary-navigation" aria-expanded="false"><span></span><span></span><span></span></button>
  <div class="nav-actions"><button class="icon-button theme-toggle" type="button" aria-label="Switch theme"><svg class="theme-icon-light" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 17a5 5 0 1 1 0-10 5 5 0 0 1 0 10zm0-2a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM11 1h2v3h-2V1zm0 19h2v3h-2v-3zM3.5 4.9l1.4-1.4 2.1 2.1-1.4 1.4-2.1-2.1zm13.5 13.5 1.4-1.4 2.1 2.1-1.4 1.4-2.1-2.1zM19.1 3.5l1.4 1.4-2.1 2.1-1.4-1.4 2.1-2.1zM5.6 17 7 18.4l-2.1 2.1-1.4-1.4L5.6 17zM23 11v2h-3v-2h3zM4 11v2H1v-2h3z"/></svg><svg class="theme-icon-dark" viewBox="0 0 24 24" aria-hidden="true"><path d="M12.3 22a10 10 0 0 1-1.6-19.9c.6-.1 1 .5.8 1a7.9 7.9 0 0 0 9.7 10.6c.5-.2 1 .3.9.8A10 10 0 0 1 12.3 22z"/></svg></button></div>
</div></nav>"""


def sidebar(page: Page) -> str:
    groups = []
    for title, links in SIDEBAR:
        rendered = []
        for label, target in links:
            current = ' aria-current="page"' if page.path == target else ""
            rendered.append(f'<a href="{relative(page.path, target)}"{current}>{label}</a>')
        groups.append(f'<div class="docs-nav-group">{title}</div>{"".join(rendered)}')
    return f'<aside class="docs-sidebar"><button class="docs-toggle" type="button" aria-controls="documentation-navigation" aria-expanded="false">Browse documentation</button><div class="docs-sidebar-title">Documentation</div><nav class="docs-nav" id="documentation-navigation" aria-label="Documentation">{"".join(groups)}</nav></aside>'


def footer(page: Page) -> str:
    def links(items: list[tuple[str, str]]) -> str:
        return '<ul class="footer-links">' + "".join(f'<li><a href="{relative(page.path, target) if not target.startswith("http") else target}">{label}</a></li>' for label, target in items) + "</ul>"
    return f"""<footer class="site-footer"><div class="container footer-grid">
<div class="footer-brand"><a class="brand" href="{relative(page.path, 'index.html')}"><span class="brand-mark" aria-hidden="true">SR</span><span>Sharp Runtime</span></a><p>A practical, componentized subset of .NET System.* APIs implemented in native C++23.</p></div>
<div><h2 class="footer-title">Documentation</h2>{links([('Getting Started','getting-started.html'),('Components','components/index.html'),('API discovery','api/index.html'),('Tutorials','tutorials/index.html')])}</div>
<div><h2 class="footer-title">Project</h2>{links([('Architecture','architecture.html'),('Platforms','platform-layer.html'),('Testing','running-tests.html'),('Known limitations','development/known-limitations.html')])}</div>
<div><h2 class="footer-title">Ecosystem</h2>{links([('GitHub','https://github.com/openeggbert/sharp-runtime'),('CNA','https://libcna.com/'),('OpenEggbert','https://github.com/openeggbert')])}</div>
</div><div class="container footer-bottom">Sharp Runtime is MIT licensed. Technical claims on this edition are pinned to runtime source <code>{SOURCE_SHA[:12]}</code>.</div></footer>"""


def render(page: Page) -> str:
    if page.path == "index.html":
        main = f'<main id="main-content">{page.body}</main>'
    else:
        category = f'<span>/</span><span>{e(page.category)}</span>' if page.category != page.title else ""
        trail = f'<a href="{relative(page.path, "index.html")}">Home</a>{category}<span>/</span><span aria-current="page">{e(page.title)}</span>'
        main = f'<main id="main-content"><div class="docs-shell">{sidebar(page)}<article class="docs-content"><nav class="breadcrumbs" aria-label="Breadcrumb">{trail}</nav>{page.body}</article></div></main>'
    return head(page) + f"\n<body>\n{nav(page)}\n{main}\n{footer(page)}\n<script src=\"{relative(page.path, 'assets/script.js')}\"></script>\n</body>\n</html>\n"


def search_page() -> Page:
    body = """<section><div class="container"><div class="search-hero"><div class="eyebrow">Site-wide discovery</div><h1>Search Sharp Runtime</h1><p>Find concepts, components, APIs, tutorials and contributor guidance.</p><form class="search-form" action="search.html" method="get" role="search"><input class="search-input" id="search-input" name="q" type="search" autocomplete="off" placeholder="Try “WebSockets”, “ownership” or “Text.Json”" aria-label="Search documentation"><button class="button button--primary" type="submit">Search</button></form><p>Press <span class="search-shortcut">/</span> from any page to open search.</p></div><div class="search-results" id="search-results" aria-live="polite"><p>Type at least two characters to search.</p></div></div></section>"""
    return Page("search.html", "Search", "Search Sharp Runtime documentation, components, tutorials and contributor guides.", "Search", body, indexable=False, page_type="WebPage")


def render_search(page: Page) -> str:
    return head(page) + f'\n<body>\n{nav(page)}\n<main id="main-content">{page.body}</main>\n{footer(page)}\n<script src="assets/script.js"></script>\n<script src="assets/search.js"></script>\n</body>\n</html>\n'


def render_404() -> str:
    page = Page("404.html", "Page not found", "The requested Sharp Runtime page could not be found.", "Utility", "", indexable=False, page_type="WebPage")
    body = """<main id="main-content"><div class="page-404"><div class="page-404-inner"><div class="error-code" aria-hidden="true">404</div><h1>This page is outside the runtime.</h1><p>The address may be old or mistyped. Search the current documentation or return to a known entry point.</p><form class="search-form" action="search.html" method="get" role="search"><input class="search-input" name="q" type="search" placeholder="Search Sharp Runtime" aria-label="Search documentation"><button class="button button--primary" type="submit">Search</button></form><div class="quick-links"><a class="button" href="index.html">Home</a><a class="button" href="getting-started.html">Getting Started</a><a class="button" href="components/index.html">Components</a><a class="button" href="tutorials/index.html">Tutorials</a></div></div></div></main>"""
    return head(page) + f"\n<body>\n{nav(page)}\n{body}\n{footer(page)}\n<script src=\"assets/script.js\"></script>\n</body>\n</html>\n"


def write_search_js() -> None:
    content = r"""(function () {
  'use strict';
  var input = document.getElementById('search-input');
  var results = document.getElementById('search-results');
  if (!input || !results) return;
  var index = [];

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (character) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[character];
    });
  }
  function score(page, terms) {
    var title = page.title.toLowerCase();
    var tags = page.tags.join(' ').toLowerCase();
    var description = page.description.toLowerCase();
    var total = 0;
    for (var i = 0; i < terms.length; i += 1) {
      if (title.indexOf(terms[i]) !== -1) total += 8;
      if (tags.indexOf(terms[i]) !== -1) total += 4;
      if (description.indexOf(terms[i]) !== -1) total += 2;
      if (!title.includes(terms[i]) && !tags.includes(terms[i]) && !description.includes(terms[i])) return -1;
    }
    return total;
  }
  function run() {
    var query = input.value.trim().toLowerCase();
    var params = new URLSearchParams(window.location.search);
    if (query) { params.set('q', query); history.replaceState(null, '', '?' + params.toString()); }
    else { history.replaceState(null, '', window.location.pathname); }
    if (query.length < 2) { results.innerHTML = '<p>Type at least two characters to search.</p>'; return; }
    var terms = query.split(/\s+/).filter(Boolean);
    var matches = index.map(function (page) { return {page: page, score: score(page, terms)}; })
      .filter(function (item) { return item.score >= 0; })
      .sort(function (a, b) { return b.score - a.score || a.page.title.localeCompare(b.page.title); });
    if (!matches.length) {
      results.innerHTML = '<p>No results for <strong>' + escapeHtml(query) + '</strong>. Try a component name or a broader concept.</p>';
      return;
    }
    results.innerHTML = '<p class="search-count">' + matches.length + ' result' + (matches.length === 1 ? '' : 's') + '</p>' + matches.map(function (item) {
      var page = item.page;
      return '<a class="search-result" href="' + encodeURI(page.url) + '"><h2>' + escapeHtml(page.title) + '</h2><p>' + escapeHtml(page.description) + '</p><span class="search-result-meta">' + escapeHtml(page.category) + ' · ' + escapeHtml(page.url) + '</span></a>';
    }).join('');
  }
  fetch('search-index.json').then(function (response) { if (!response.ok) throw new Error('index'); return response.json(); })
    .then(function (data) { index = data; run(); })
    .catch(function () { results.innerHTML = '<p>Search index is unavailable. Use the documentation navigation above.</p>'; });
  input.addEventListener('input', run);
  var initial = new URLSearchParams(window.location.search).get('q') || '';
  input.value = initial;
  if (initial) input.focus();
})();
"""
    (ROOT / "assets" / "search.js").write_text(content, encoding="utf-8")


def write_site_files(pages: list[Page]) -> None:
    # The page set is generated deterministically, so old public files are overwritten in place.
    for page in pages:
        destination = ROOT / page.path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(render(page), encoding="utf-8")

    search = search_page()
    (ROOT / search.path).write_text(render_search(search), encoding="utf-8")
    (ROOT / "404.html").write_text(render_404(), encoding="utf-8")
    write_search_js()

    search_index = [
        {"title": page.title, "url": "/" if page.path == "index.html" else "/" + page.path, "description": page.description, "tags": sorted(set(page.tags + [page.category.lower()])), "category": page.category}
        for page in pages if page.indexable
    ]
    (ROOT / "search-index.json").write_text(json.dumps(search_index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for page in sorted((p for p in pages if p.indexable), key=lambda p: p.path):
        url = BASE if page.path == "index.html" else urljoin(BASE, page.path)
        priority = "1.0" if page.path == "index.html" else ("0.8" if "/" not in page.path or page.path.endswith("/index.html") else "0.6")
        sitemap.extend(["  <url>", f"    <loc>{url}</loc>", f"    <lastmod>{LASTMOD}</lastmod>", f"    <priority>{priority}</priority>", "  </url>"])
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: https://sharpruntime.com/sitemap.xml\n", encoding="utf-8")


def main() -> None:
    components = json.loads((ROOT / "data" / "components.json").read_text(encoding="utf-8"))
    if components["source_sha"] != SOURCE_SHA:
        raise SystemExit("Pinned component source SHA does not match build-site source SHA")
    pages = build_pages(components)
    paths = [page.path for page in pages]
    if len(paths) != len(set(paths)):
        raise SystemExit("Duplicate page paths")
    write_site_files(pages)
    print(f"Generated {len(pages)} indexable pages, search, sitemap and 404")


if __name__ == "__main__":
    main()

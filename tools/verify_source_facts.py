#!/usr/bin/env python3
"""Verify website facts against one explicitly selected Sharp Runtime checkout.

This checker never selects a branch, changes the runtime checkout, configures CMake, builds, or
runs tests. The caller must provide the exact checkout to inspect with ``--runtime``.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Keep a read-only drift check from leaving interpreter cache artifacts behind.
sys.dont_write_bytecode = True

import sync_api_inventory
import sync_components


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class VerificationError(RuntimeError):
    """A foundational input could not be inspected safely."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise VerificationError(f"cannot read {path.relative_to(ROOT)}: {error}") from error
    if not isinstance(value, dict):
        raise VerificationError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def git(runtime: Path, *arguments: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(runtime), *arguments],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", "") or str(error)
        raise VerificationError(f"git {' '.join(arguments)} failed: {detail.strip()}") from error


def expected_component_data(runtime: Path, source_sha: str) -> dict[str, Any]:
    """Use sync_components' catalogue parsing rules without writing its output file."""

    catalogue = runtime / "docs" / "ComponentCatalog.md"
    try:
        text = catalogue.read_text(encoding="utf-8")
    except OSError as error:
        raise VerificationError(f"cannot read {catalogue}: {error}") from error
    lines = text.splitlines()
    graph = re.search(r"\*\*(\d+) physical modules\*\* and \*\*(\d+) direct", text)
    if not graph:
        raise VerificationError("cannot read graph metrics from docs/ComponentCatalog.md")

    physical: list[dict[str, Any]] = []
    try:
        physical_rows = sync_components.parse_table(lines, "## Physical components")
        compatibility_rows = sync_components.parse_table(lines, "## Compatibility components")
    except ValueError as error:
        raise VerificationError(f"cannot find a component catalogue table: {error}") from error

    for cells in physical_rows:
        if len(cells) != 8:
            raise VerificationError(f"unexpected physical-component row: {cells!r}")
        physical.append(
            {
                "name": sync_components.clean(cells[0]),
                "owner": sync_components.clean(cells[1]),
                "kind": sync_components.clean(cells[2]),
                "public_dependencies": sync_components.split_values(cells[3]),
                "private_dependencies": sync_components.split_values(cells[4]),
                "test_dependencies": sync_components.split_values(cells[5]),
                "external_dependency": sync_components.clean(cells[6]),
                "header": sync_components.clean(cells[7]),
            }
        )

    compatibility: list[dict[str, Any]] = []
    for cells in compatibility_rows:
        if len(cells) != 5:
            raise VerificationError(f"unexpected compatibility-component row: {cells!r}")
        compatibility.append(
            {
                "name": sync_components.clean(cells[0]),
                "owner": sync_components.clean(cells[1]),
                "kind": sync_components.clean(cells[2]),
                "dependencies": sync_components.split_values(cells[3]),
                "header": sync_components.clean(cells[4]),
            }
        )

    physical_count = int(graph.group(1))
    if len(physical) != physical_count:
        raise VerificationError(
            f"catalogue reports {physical_count} physical components but its table has "
            f"{len(physical)} rows"
        )
    return {
        "schema": 1,
        "source_repository": "https://github.com/openeggbert/sharp-runtime",
        "source_sha": source_sha,
        "physical_count": physical_count,
        "direct_production_edges": int(graph.group(2)),
        "physical_components": physical,
        "compatibility_components": compatibility,
    }


def check_generated_catalogue(runtime: Path) -> str:
    """Ask the runtime's generator to compare CMake metadata with its catalogue."""

    script = runtime / "scripts" / "generate_component_catalog.py"
    if not script.is_file():
        raise VerificationError(f"missing catalogue checker: {script}")
    try:
        result = subprocess.run(
            [sys.executable, "-B", str(script), "--root", str(runtime), "--check"],
            cwd=runtime,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise VerificationError(f"cannot run the catalogue checker: {error}") from error
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise VerificationError(f"runtime component catalogue is stale: {detail}")
    return result.stdout.strip()


def has_cpp(path: Path) -> bool:
    return path.is_dir() and next(path.rglob("*.cpp"), None) is not None


def test_topology(runtime: Path, components: dict[str, Any]) -> tuple[int, int]:
    """Mirror the current CMake one-executable-per-tested-module topology."""

    component_logic = (runtime / "cmake" / "SharpRuntimeComponents.cmake").read_text(
        encoding="utf-8"
    )
    root_cmake = (runtime / "CMakeLists.txt").read_text(encoding="utf-8")
    required_component_markers = (
        'file(GLOB_RECURSE module_test_sources CONFIGURE_DEPENDS',
        '"${CMAKE_CURRENT_SOURCE_DIR}/tests/*.cpp"',
        'function(sharp_runtime_add_component_tests component)',
        'add_executable("${test_target}" ${test_sources})',
    )
    missing = [marker for marker in required_component_markers if marker not in component_logic]
    if missing:
        raise VerificationError(
            "cannot derive component test topology from current CMake; missing marker(s): "
            + ", ".join(missing)
        )
    required_integration_markers = (
        'file(GLOB_RECURSE SHARP_RUNTIME_INTEGRATION_TEST_SOURCES CONFIGURE_DEPENDS',
        'add_executable(',
        'SharpRuntimeIntegrationTests',
    )
    missing = [marker for marker in required_integration_markers if marker not in root_cmake]
    if missing:
        raise VerificationError(
            "cannot derive integration test topology from current CMake; missing marker(s): "
            + ", ".join(missing)
        )

    component_executables = sum(
        has_cpp(runtime / item["owner"] / "tests")
        for item in components["physical_components"]
    )
    integration_executables = int(has_cpp(runtime / "tests" / "integration"))
    return component_executables, integration_executables


def cmake_baseline(runtime: Path) -> tuple[str, int, bool, bool]:
    text = (runtime / "CMakeLists.txt").read_text(encoding="utf-8")
    minimum = re.search(
        r"cmake_minimum_required\s*\(\s*VERSION\s+([0-9]+(?:\.[0-9]+)*)", text
    )
    standard = re.search(r"set\s*\(\s*CMAKE_CXX_STANDARD\s+([0-9]+)\s*\)", text)
    if not minimum or not standard:
        raise VerificationError("cannot parse CMake minimum or C++ standard from CMakeLists.txt")
    required = bool(re.search(r"set\s*\(\s*CMAKE_CXX_STANDARD_REQUIRED\s+ON\s*\)", text))
    extensions_off = bool(re.search(r"set\s*\(\s*CMAKE_CXX_EXTENSIONS\s+OFF\s*\)", text))
    return minimum.group(1), int(standard.group(1)), required, extensions_off


def gate_evidence_failures(
    runtime: Path, facts: dict[str, Any], test_executables: int
) -> list[str]:
    failures: list[str] = []
    gate = facts.get("latest_measured_gate")
    if not isinstance(gate, dict):
        return ["site-facts latest_measured_gate must be an object"]
    evidence = gate.get("evidence")
    if not isinstance(evidence, str) or not evidence.strip():
        return ["latest measured gate has no evidence string"]

    source_name = evidence.split(maxsplit=1)[0]
    source_path = Path(source_name)
    if source_path.is_absolute() or ".." in source_path.parts:
        return [f"gate evidence names an unsafe source path: {source_name}"]
    evidence_path = runtime / source_path
    try:
        text = evidence_path.read_text(encoding="utf-8")
    except OSError as error:
        return [f"cannot read gate evidence {source_name}: {error}"]

    expected_phrases = (
        f"{gate.get('cases'):,} tests across {test_executables} executables",
        f"{gate.get('passed'):,} passed, {gate.get('failed')} failed, "
        f"{gate.get('skipped')} skipped",
        f"measured on {gate.get('measured_at')}",
    )
    for phrase in expected_phrases:
        if phrase not in text:
            failures.append(f"gate evidence {source_name} does not contain {phrase!r}")
    ticket = re.search(r"#\d+", evidence)
    if ticket and ticket.group(0) not in text:
        failures.append(
            f"gate evidence {source_name} does not contain ticket {ticket.group(0)}"
        )
    return failures


def verify(runtime: Path) -> tuple[list[str], dict[str, Any]]:
    facts = load_json(DATA / "site-facts.json")
    components = load_json(DATA / "components.json")
    api_inventory = load_json(DATA / "api-inventory.json")
    component_docs = load_json(DATA / "component-docs.json")

    top_level = Path(git(runtime, "rev-parse", "--show-toplevel")).resolve()
    if top_level != runtime:
        raise VerificationError(
            f"--runtime must name the repository root exactly ({top_level}), not {runtime}"
        )
    source_sha = git(runtime, "rev-parse", "HEAD")
    status_before = git(runtime, "status", "--short", "--ignore-submodules=all")
    if status_before:
        raise VerificationError(
            "explicit runtime checkout has working-tree changes; facts cannot be tied solely to "
            f"HEAD:\n{status_before}"
        )

    catalogue_check = check_generated_catalogue(runtime)
    expected_components = expected_component_data(runtime, source_sha)
    try:
        expected_inventory = sync_api_inventory.build_inventory(runtime)
    except (OSError, subprocess.CalledProcessError, SystemExit) as error:
        raise VerificationError(f"cannot derive API inventory: {error}") from error
    component_tests, integration_tests = test_topology(runtime, expected_components)
    test_executables = component_tests + integration_tests
    minimum_cmake, cxx_standard, cxx_required, extensions_off = cmake_baseline(runtime)

    failures: list[str] = []

    def equal(label: str, actual: Any, expected: Any) -> None:
        if actual != expected:
            failures.append(f"{label}: website has {actual!r}, source requires {expected!r}")

    equal("site-facts source SHA", facts.get("source_sha"), source_sha)
    equal("component data source SHA", components.get("source_sha"), source_sha)
    equal("API inventory source SHA", api_inventory.get("source_sha"), source_sha)
    equal(
        "measured gate source SHA",
        facts.get("latest_measured_gate", {}).get("source_sha"),
        source_sha,
    )
    equal(
        "site-facts source commit time",
        facts.get("source_commit_time"),
        git(runtime, "show", "-s", "--format=%cI", "HEAD"),
    )

    if components != expected_components:
        failures.append(
            "data/components.json differs from the explicit runtime catalogue; "
            "run tools/sync_components.py with the same --runtime path"
        )
    physical_names = [item["name"] for item in expected_components["physical_components"]]
    website_names = [item.get("name") for item in components.get("physical_components", [])]
    if len(set(physical_names)) != len(physical_names):
        failures.append("runtime component catalogue contains duplicate physical names")
    if len(set(website_names)) != len(website_names):
        failures.append("data/components.json contains duplicate physical names")
    equal("physical component name set", set(website_names), set(physical_names))
    equal("components.json physical count", components.get("physical_count"), len(physical_names))
    equal("site-facts physical count", facts.get("physical_components"), len(physical_names))
    equal(
        "site-facts production-edge count",
        facts.get("direct_production_edges"),
        expected_components["direct_production_edges"],
    )
    equal(
        "components.json production-edge count",
        components.get("direct_production_edges"),
        expected_components["direct_production_edges"],
    )

    if api_inventory != expected_inventory:
        failures.append(
            "data/api-inventory.json differs from the explicit runtime tree; "
            "run tools/sync_api_inventory.py with the same --runtime path"
        )
    api_component_names = [item.get("name") for item in api_inventory.get("components", [])]
    equal("API inventory component name set", set(api_component_names), set(physical_names))
    equal(
        "API inventory public-header rollup",
        api_inventory.get("public_header_count"),
        sum(item.get("public_header_count", 0) for item in api_inventory.get("components", [])),
    )
    equal(
        "API inventory production-source rollup",
        api_inventory.get("production_source_count"),
        sum(item.get("production_source_count", 0) for item in api_inventory.get("components", [])),
    )
    equal(
        "site-facts public-header count",
        facts.get("public_headers"),
        expected_inventory["public_header_count"],
    )
    equal(
        "site-facts production-source count",
        facts.get("production_sources"),
        expected_inventory["production_source_count"],
    )
    equal("component documentation name set", set(component_docs), set(physical_names))

    equal(
        "component test-executable count",
        facts.get("component_test_executables"),
        component_tests,
    )
    equal(
        "integration test-executable count",
        facts.get("integration_test_executables"),
        integration_tests,
    )
    equal("total test-executable count", facts.get("test_executables"), test_executables)
    equal(
        "test-executable internal sum",
        facts.get("test_executables"),
        facts.get("component_test_executables", 0)
        + facts.get("integration_test_executables", 0),
    )

    gate = facts.get("latest_measured_gate", {})
    equal("measured gate case count", gate.get("cases"), facts.get("current_test_cases"))
    equal(
        "measured gate arithmetic",
        gate.get("cases"),
        gate.get("passed", 0) + gate.get("skipped", 0) + gate.get("failed", 0),
    )
    equal("gate evidence date", gate.get("measured_at"), facts.get("evidence_date"))
    failures.extend(gate_evidence_failures(runtime, facts, test_executables))

    equal("minimum CMake version", minimum_cmake, "3.20")
    equal("C++ standard", cxx_standard, 23)
    equal("C++ standard required", cxx_required, True)
    equal("C++ extensions disabled", extensions_off, True)

    repositories = {
        facts.get("source_repository"),
        components.get("source_repository"),
        api_inventory.get("source_repository"),
    }
    if repositories != {"https://github.com/openeggbert/sharp-runtime"}:
        failures.append(f"website source_repository values disagree: {repositories!r}")

    status_after = git(runtime, "status", "--short", "--ignore-submodules=all")
    if status_after != status_before:
        failures.append("runtime checkout changed while source facts were being verified")

    summary = {
        "source_sha": source_sha,
        "catalogue_check": catalogue_check,
        "physical_components": len(physical_names),
        "production_edges": expected_components["direct_production_edges"],
        "public_headers": expected_inventory["public_header_count"],
        "production_sources": expected_inventory["production_source_count"],
        "component_test_executables": component_tests,
        "integration_test_executables": integration_tests,
        "test_executables": test_executables,
        "minimum_cmake": minimum_cmake,
        "cxx_standard": cxx_standard,
        "gate": gate,
    }
    return failures, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runtime",
        type=Path,
        required=True,
        help="Explicit Sharp Runtime repository root at the pinned HEAD",
    )
    args = parser.parse_args()
    try:
        runtime = args.runtime.expanduser().resolve(strict=True)
        if not runtime.is_dir():
            raise VerificationError(f"--runtime is not a directory: {runtime}")
        failures, summary = verify(runtime)
    except (OSError, VerificationError) as error:
        print(f"Source fact verification failed:\n- {error}", file=sys.stderr)
        return 1

    if failures:
        print("Source fact verification failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    gate = summary["gate"]
    print(f"Explicit runtime: {runtime}")
    print(f"Source HEAD: {summary['source_sha']}")
    print(f"Generated catalogue: {summary['catalogue_check']}")
    print(
        "Components: "
        f"{summary['physical_components']} physical, "
        f"{summary['production_edges']} direct production edges; names exact"
    )
    print(
        "API inventory: "
        f"{summary['public_headers']:,} public headers, "
        f"{summary['production_sources']:,} production sources"
    )
    print(
        "Test topology: "
        f"{summary['component_test_executables']} component + "
        f"{summary['integration_test_executables']} integration = "
        f"{summary['test_executables']} executables"
    )
    print(
        f"Build baseline: CMake {summary['minimum_cmake']}, "
        f"C++{summary['cxx_standard']} required, extensions off"
    )
    print(
        f"Measured gate evidence: {gate['evidence']} — {gate['cases']:,} run, "
        f"{gate['passed']:,} passed, {gate['skipped']} skipped, {gate['failed']} failed"
    )
    print("Internal website consistency: OK")
    print("Runtime checkout remained unchanged: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Configure, build serially, and run the website's deterministic C++ examples."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUILD = Path("/tmp/sharpruntime-site-examples")
RUNNABLE = (
    "example_hello_console",
    "example_ported_class",
    "example_arrays_spans",
    "example_collections",
    "example_memory_stream",
    "example_filesystem",
    "example_json",
    "example_tasks",
    "example_channels",
    "example_network_types",
    "example_http_configuration",
    "example_websocket_shape",
)


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--build", type=Path, default=DEFAULT_BUILD)
    parser.add_argument("--configure-only", action="store_true")
    args = parser.parse_args()

    runtime = args.runtime.resolve()
    build = args.build.resolve()
    if not (runtime / "CMakeLists.txt").is_file():
        parser.error("--runtime must name a Sharp Runtime checkout")

    run([
        "cmake", "-S", str(ROOT / "examples" / "verified"), "-B", str(build),
        "-G", "Ninja", "-DCMAKE_BUILD_TYPE=Debug",
        f"-DSHARP_RUNTIME_SOURCE_DIR={runtime}",
    ])
    if args.configure_only:
        print("Example configuration: OK")
        return 0

    run(["cmake", "--build", str(build), "--target", "website_examples", "--parallel", "1"])
    for executable in RUNNABLE:
        run([str(build / executable)])
    print(f"Examples built and run: {len(RUNNABLE)}/{len(RUNNABLE)} (serial build)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        print(f"Example verification failed with exit code {error.returncode}", file=sys.stderr)
        raise SystemExit(error.returncode)

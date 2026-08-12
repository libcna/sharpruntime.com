# Website Example Verification

Date: 2026-08-12

Sharp Runtime source: `6d429559ce265daa21866f0d6e82c5642e2ba0ec`

Compiler: GNU C++ 14.2.0

Configuration: Debug, C++23, tests off

Build policy: exactly one compiler job (`--parallel 1`)

## Method

`examples/verified/CMakeLists.txt` requires an explicit `SHARP_RUNTIME_SOURCE_DIR`, selects the
smallest union needed by the examples, and links each executable to its direct namespaced physical
target. The configured dependency closure contained 17 physical components:

```text
Core.Base, Console, Collections.Core, Uri, TimeZone, IO, Buffers, Text,
Text.Json, Threading, Threading.Tasks, Threading.Channels, ComponentModel,
Net, Net.Http, Net.Sockets, Net.WebSockets
```

The exact command was:

```bash
python3 tools/verify_examples.py \
  --runtime /tmp/sharp-runtime-source-audit.m7gUgr \
  --build /tmp/sharpruntime-site-examples
```

The script configures, builds `website_examples` serially, then runs every deterministic
executable. Network examples validate native construction, parsing, configuration, state, and
linking only; they make no external connection.

## Results

| Executable | Direct component | Result | Public documentation exercised |
| --- | --- | --- | --- |
| `example_hello_console` | Console | Built and ran | Getting Started / first consumer |
| `example_ported_class` | Core.Base | Built and ran | Porting, Nullable, EventHandler |
| `example_arrays_spans` | Core.Base | Built and ran | Array helpers, Span, overlapping copy |
| `example_collections` | Collections.Core | Built and ran | List and Dictionary |
| `example_memory_stream` | IO | Built and ran | MemoryStream, BinaryReader/Writer, leave-open |
| `example_filesystem` | IO | Built and ran | File text round trip in an isolated temporary directory |
| `example_json` | Text.Json | Built and ran | `vector<int>` JSON round trip; printed `[3,7,11]` |
| `example_tasks` | Threading.Tasks | Built and ran | Cooperative cancellation and fault observation |
| `example_channels` | Threading.Channels | Built and ran | Bounded capacity, FIFO reads, completion |
| `example_network_types` | Net | Built and ran | IP parsing, endpoint, address family; no DNS/network request |
| `example_http_configuration` | Net.Http | Built and ran | HttpClient construction, base address, headers; no request |
| `example_websocket_shape` | Net.WebSockets | Built and ran | Client construction and initial state; no connection |

Final result: **12/12 built, linked, and exited successfully**.

## Warning-profile note

An initial example compile used `-Wpedantic -Werror`. It rejected the intentional
`unsigned __int128` spelling exposed by `Decimal.hpp`, even though the example itself was valid.
The verifier now matches Sharp Runtime's consumer warning profile, `-Wall -Wextra -Werror`, so
the example gate does not manufacture an unsupported portability rule.

# Tutorial gap analysis — second pass

Date: 2026-08-12

The first redesigned site contained 14 task-oriented tutorial pages. The
second-pass audit compared those tutorials with the selected source's physical
component families, the old site's practical examples, the porting guide, and
the current limitations. Page count was not used as a target.

## Coverage retained from the first pass

The site retains first consumer setup, component selection, strings and
StringBuilder, collections, events, files, JSON, XML LINQ, tasks/cancellation,
HTTP, compression/hashing, adding a component, debugging components, and
porting a small C# class.

## Gaps filled

Twelve new tutorials now cover:

| Gap | New tutorial | Verification boundary |
|---|---|---|
| Optional values | Use Nullable Values | Source-checked; paired ported-class executable built and ran |
| Owned arrays and borrowed views | Work with Arrays and Spans | Example built and ran |
| In-memory binary protocols | Round-trip Data with MemoryStream | Example built and ran |
| Reader/writer selection | Use Readers and Writers | Source-checked; binary path exercised by MemoryStream example |
| Watcher callbacks and reconfiguration | Watch a Directory | 42 focused watcher tests ran locally; Linux/inotify only |
| DNS and socket families | Use DNS, TCP, and UDP | Types built/ran without network; live operations require a controlled peer |
| WebSocket lifetime | Use WebSockets | Client/state built/ran without connection; live example requires a controlled `ws://` peer |
| Locks and queued work | Use Locks and ThreadPool | Source-checked; detached-thread and capture caveats explicit |
| Backpressure and completion | Build a Channel Pipeline | Example built and ran |
| Callback teardown | Use Timers Safely | Source-checked; no claim that disposal joins every in-flight callback |
| Owning behavior tests | Write a Component Test | Current CMake/test topology and serial commands |
| Proving forbidden boundaries | Add a Negative Consumer Fixture | Current consumer-fixture workflow |

The final tutorial count is 26, excluding the tutorial index.

## Topics deliberately consolidated

- Properties, interfaces, constructors, exceptions, delegates, events,
  ownership, JSON/HTTP composition, and XML porting have substantial sections
  in the flagship porting guide and link to focused existing tutorials. A thin
  page for each syntax transformation would duplicate that guide.
- File, Directory, FileStream, readers/writers, and MemoryStream are layered
  across the filesystem tutorial, two new I/O tutorials, and the deep I/O
  conceptual pages.
- Task continuations, cancellation, ThreadPool, locks, channels, and timers are
  split by materially different execution/lifetime models rather than by every
  type name.

## Tutorials intentionally not published

- HTTPS, `wss://`, certificate, and TLS tutorials would imply a transport the
  selected runtime does not provide.
- Recursive FileSystemWatcher guidance would teach unsupported behavior because
  `IncludeSubdirectories` is currently inert.
- Async stream tutorials were not invented: the current Stream family is
  synchronous and does not expose a general async I/O contract.
- A live public-network integration tutorial was not used as build evidence.
  DNS, TCP, UDP, HTTP, Ping, and WebSocket runtime behavior depends on peers,
  privileges, IPv6, and host policy; deterministic examples stop before network
  contact unless a controlled peer is explicitly required.
- Reflection-driven serializer, dynamic invocation, managed assembly loading,
  and GC tutorials would contradict deliberate native-runtime non-goals.

This disposition leaves room for future platform-fixture tutorials when the
runtime gains the corresponding implementation and repeatable test evidence.

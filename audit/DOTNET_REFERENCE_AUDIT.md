# Official .NET Concept Reference Audit

Checked: 2026-08-12

Sharp Runtime behavior in the website is derived from the pinned Sharp Runtime implementation,
CMake graph, tests, and measured evidence. Official .NET documentation is used only to describe
the comparison side of a porting table; matching names do not establish compatibility.

| .NET concept | Official reference checked | Comparison conclusion used by the website |
| --- | --- | --- |
| `String` | [String class](https://learn.microsoft.com/en-us/dotnet/api/system.string?view=net-10.0) and [C# strings](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/strings/) | .NET strings are immutable UTF-16-code-unit sequences. Sharp Runtime's common value is mutable, byte-indexed `std::string`, so the site never calls indexing/casing full parity. |
| `Span<T>` | [Span&lt;T&gt;](https://learn.microsoft.com/en-us/dotnet/api/system.span-1?view=net-10.0) and [memory/span guidance](https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/) | .NET Span is a stack-constrained ref struct and cannot cross await/yield. Sharp Runtime Span is a pointer/length C++ view; its safety comes from documented owner lifetime rather than CLR ref-safety rules. |
| `Nullable<T>` | [GetValueOrDefault](https://learn.microsoft.com/en-us/dotnet/api/system.nullable-1.getvalueordefault?view=net-10.0) and [Value](https://learn.microsoft.com/en-us/dotnet/api/system.nullable-1.value?view=net-9.0) | Present/default/throw behavior is a valid conceptual reference. Sharp Runtime's `std::optional`-backed construction, copies, moves, equality, and hashing remain native and are documented separately. |
| `EventHandler<TEventArgs>` | [EventHandler&lt;TEventArgs&gt;](https://learn.microsoft.com/en-us/dotnet/api/system.eventhandler-1?view=net-9.0) and [events guidance](https://learn.microsoft.com/en-us/dotnet/standard/events/) | In .NET EventHandler is a delegate signature used by a separate language event. Sharp Runtime deliberately combines signature, subscription storage, tokens, and dispatch in one C++ template. |
| `Task` faults | [Task.Exception](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.exception?view=netframework-4.8.1) and [Task.Wait](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.wait?view=net-10.0) | .NET blocking observation uses AggregateException semantics. Sharp Runtime Wait rethrows the stored native exception directly; the site calls this out instead of promising CLR task behavior. |
| Channels | [System.Threading.Channels](https://learn.microsoft.com/en-us/dotnet/api/system.threading.channels?view=net-10.0) | Producer/consumer, bounded full-mode, reader/writer, and completion concepts are comparable. Sharp Runtime uses mutex/condition-variable state and task-backed waits without C# async-enumerable syntax. |
| Readers/writers | [BinaryReader](https://learn.microsoft.com/en-us/dotnet/api/system.io.binaryreader?view=net-10.0) and [StreamReader](https://learn.microsoft.com/en-us/dotnet/api/system.io.streamreader?view=net-10.0) | .NET readers expose encoding-aware character behavior and optional leave-open ownership. Sharp Runtime binary UTF-8 behavior is specific, while its current StreamReader byte-to-character behavior is reduced and documented as such. |
| `FileSystemWatcher` | [FileSystemWatcher](https://learn.microsoft.com/en-us/dotnet/api/system.io.filesystemwatcher?view=net-10.0) | .NET documents filtering, subdirectories, internal-buffer overflow, remote paths, and platform-specific duplicate/missed events. The selected Sharp Runtime backend is narrower: Linux inotify, one directory, no effective recursion, and no explicit overflow translation. |

No external page was used to infer a Sharp Runtime API, signature, platform backend, or test result.

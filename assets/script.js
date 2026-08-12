/* sharp-runtime documentation — shared JavaScript */

// ---- Theme toggle ----
(function () {
  const KEY = 'sr-theme';
  const saved = localStorage.getItem(KEY);
  if (saved === 'dark') document.body.classList.add('dark');
  else if (saved === 'light') document.body.classList.add('light');

  document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;
    function updateLabel() {
      const isDark = document.body.classList.contains('dark') ||
        (!document.body.classList.contains('light') &&
          window.matchMedia('(prefers-color-scheme: dark)').matches);
      btn.textContent = isDark ? '☀ Light' : '☾ Dark';
    }
    updateLabel();
    btn.addEventListener('click', function () {
      if (document.body.classList.contains('dark')) {
        document.body.classList.remove('dark');
        document.body.classList.add('light');
        localStorage.setItem(KEY, 'light');
      } else {
        document.body.classList.remove('light');
        document.body.classList.add('dark');
        localStorage.setItem(KEY, 'dark');
      }
      updateLabel();
    });
  });
})();

// ---- Active sidebar link ----
document.addEventListener('DOMContentLoaded', function () {
  const links = document.querySelectorAll('.sidebar nav a');
  const current = window.location.pathname.split('/').pop() || 'index.html';
  links.forEach(function (link) {
    const href = link.getAttribute('href');
    if (!href) return;
    const target = href.split('/').pop();
    if (target === current) link.classList.add('active');
  });
});

// ---- Search ----
document.addEventListener('DOMContentLoaded', function () {
  const input = document.getElementById('search-input');
  const resultsDiv = document.getElementById('search-results');
  if (!input || !resultsDiv) return;

  const pages = [
    { title: 'Project Overview', url: '../overview.html', desc: 'What sharp-runtime is, main purpose, goals, status' },
    { title: 'Getting Started', url: '../getting-started.html', desc: 'Quick start guide for using sharp-runtime' },
    { title: 'Build System', url: '../build.html', desc: 'CMake build commands, options, dependencies' },
    { title: 'Running Tests', url: '../running-tests.html', desc: 'GoogleTest, test commands, test structure' },
    { title: 'Architecture', url: '../architecture.html', desc: 'Runtime layers, design decisions, namespace structure' },
    { title: 'Project Structure', url: '../project-structure.html', desc: 'Directories, files, include layout, vendor' },
    { title: 'Runtime Overview', url: '../runtime-overview.html', desc: 'Object model, types, primitives, design' },
    { title: 'Type System', url: '../type-system.html', desc: 'Object, primitives, SharpRuntimeHelper, intcs, bytecs' },
    { title: 'Memory Management', url: '../memory-management.html', desc: 'RAII, smart pointers, no GC, ownership rules' },
    { title: 'Exceptions', url: '../exceptions.html', desc: 'Exception hierarchy, throwing, handling, C# mapping' },
    { title: 'Strings', url: '../strings.html', desc: 'std::string, System::String utilities, StringBuilder' },
    { title: 'Arrays', url: '../arrays.html', desc: 'std::vector, System::Array static helpers, usage' },
    { title: 'Delegates and Events', url: '../delegates.html', desc: 'Action, Func, Predicate, EventHandler, operator+=' },
    { title: 'Reflection', url: '../reflection.html', desc: 'Type, GetTypeName, limited runtime type info' },
    { title: 'I/O Subsystem', url: '../io.html', desc: 'Stream, File, Directory, BinaryReader, Compression, IsolatedStorage' },
    { title: 'Threading', url: '../threading.html', desc: 'Thread, Task, Mutex, CancellationToken, Timer' },
    { title: 'Platform Layer', url: '../platform-layer.html', desc: 'Platform guards, POSIX-only subsystems, Android/Emscripten' },
    { title: 'C# Compatibility', url: '../csharp-compatibility.html', desc: 'C# to C++ mapping table, porting patterns' },
    { title: 'CNA Integration', url: '../cna-integration.html', desc: 'How CNA uses sharp-runtime, XNA port, include/link' },
    { title: 'Modules Index', url: '../modules/index.html', desc: 'All subsystem documentation pages' },
    { title: 'Classes Index', url: '../classes/index.html', desc: 'All important class documentation pages' },
    { title: 'API Reference Index', url: '../api/index.html', desc: 'API reference grouped by namespace' },
    { title: 'Internals Index', url: '../internals/index.html', desc: 'Deep internal documentation' },
    { title: 'Tutorials Index', url: '../tutorials/index.html', desc: 'Step-by-step tutorials' },
    { title: 'Development Index', url: '../development/index.html', desc: 'Developer guide, adding features, coding style' },
    { title: 'Coding Style', url: '../development/coding-style.html', desc: 'Naming conventions, property macros, SPDX headers' },
    { title: 'Debugging', url: '../development/debugging.html', desc: 'Debugging runtime issues, GDB, sanitizers' },
    { title: 'Porting C# Code', url: '../development/porting-csharp-code.html', desc: 'How to port C# classes to C++ with sharp-runtime' },
    { title: 'Adding Runtime Features', url: '../development/adding-runtime-features.html', desc: 'How to add new runtime classes and methods' },
    { title: 'Known Limitations', url: '../development/known-limitations.html', desc: 'What is not implemented, known bugs, POSIX-only items' },
    { title: 'Collections Module', url: '../modules/collections.html', desc: 'List, Dictionary, HashSet, Queue, Stack, immutable' },
    { title: 'Numerics Module', url: '../modules/numerics.html', desc: 'Vector2/3/4, Matrix4x4, Quaternion, BigInteger' },
    { title: 'Text Module', url: '../modules/text.html', desc: 'Encoding, StringBuilder, Regex, Json, Xml' },
    { title: 'Property Macros', url: '../internals/property-macros.html', desc: 'DDATA, DGETTER, Prop.hpp macro system' },
    { title: 'Object Lifecycle', url: '../internals/object-lifecycle.html', desc: 'Object creation, destruction, virtual dispatch' },
  ];

  function search(query) {
    query = query.toLowerCase().trim();
    if (query.length < 2) { resultsDiv.innerHTML = ''; return; }
    const results = pages.filter(p =>
      p.title.toLowerCase().includes(query) ||
      p.desc.toLowerCase().includes(query)
    );
    if (results.length === 0) {
      resultsDiv.innerHTML = '<p style="color:var(--text-muted)">No results found.</p>';
      return;
    }
    resultsDiv.innerHTML = results.map(r =>
      `<div class="search-result-item"><a href="${r.url}">${r.title}</a><p>${r.desc}</p></div>`
    ).join('');
  }

  input.addEventListener('input', function () { search(this.value); });
});

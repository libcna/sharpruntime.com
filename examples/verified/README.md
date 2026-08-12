# Verified website examples

These translation units are the executable counterparts of important website snippets. They are
configured against an explicitly supplied Sharp Runtime checkout so no ambient branch can change
the source under test.

```bash
cmake -S examples/verified -B /tmp/sharpruntime-site-examples \
  -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DSHARP_RUNTIME_SOURCE_DIR=/path/to/pinned/sharp-runtime

cmake --build /tmp/sharpruntime-site-examples \
  --target website_examples \
  --parallel 1
```

Run the local, deterministic executables with `tools/verify_examples.py`. Network examples verify
construction and configuration only; they intentionally do not contact an external host.

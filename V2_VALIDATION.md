# V2 validation

Checks performed in the build environment:

- Compiled C++20 to the bundled Wasm binary with Zig, SIMD and fixed 128 MiB memory.
- Loaded the actual binary in Node WebAssembly; inspected exports/imports. No host imports in this bundled binary.
- Verified valid mesh setup, vertex-normal calculation, localized deformation, BVH ray-near-vertex picking, undo and vertex-capacity rejection.
- Ran the engine worker script against a stub WebGL2 API: verified initialization, settings, input batching, buffer recycling, deformation and mesh export. This checks protocol behavior, not real GPU rendering or shader compilation.
- Compiled the persistent-thread C++ path with GCC and pthreads; verified its deformation against a brute-force reference across 20 strokes on 30,000 vertices.
- JavaScript syntax checks for new modules and the editor's inline scripts.

Not verified: real WebGPU/WebGL rendering, Safari/iPadOS, stylus hardware, actual presented 60/120 Hz frames, mobile memory/thermal behavior, full editor regression, PWA update/install, and Emscripten pthread glue in browsers. Browser automation installation failed because the browser download was incomplete. No screenshots or browser FPS results are claimed.

Re-run from the package directory:

```sh
node tests/wasm.cjs
node tests/worker.cjs
g++ -std=c++20 -O3 -pthread tests/threaded.cpp -o /tmp/p3-thread-test
/tmp/p3-thread-test
```

The two Node scripts accept package-directory paths. Tests intentionally do not assert throughput. Historical TEST_RESULTS files shipped with the original upload were not revalidated.

## V2.0.1 storage isolation

`node tests/isolation.cjs` passed: V2 ignores legacy V1 keys; V2 writes/removals preserve V1 data; subsequent V1 color changes do not alter V2 values; service-worker activation deletes only obsolete caches for the same V2 scope and all reads target its own cache. These are programmatic tests, not live browser deployment verification.

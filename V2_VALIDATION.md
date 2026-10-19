# V2.0.3 validation

## Executed checks

- Parsed all 19 executable inline scripts in index.html plus the service worker, anatomy asset script and both engine modules.
- Rebuilt the delivered C++20 Wasm binary with Zig, SIMD and fixed 128 MiB memory. Inspected its exports and loaded the actual binary in Node.
- `tests/wasm.cjs`: mesh setup, normals, local deformation, BVH ray-near-vertex picking, undo and capacity rejection.
- `tests/grab.cjs`: frozen Grab baseline, mirror motion, centered symmetry seam, zero drift on returning to the origin, undo and BVH picking after bounds refit.
- `tests/worker.cjs`: actual worker script/Wasm initialization and message protocol with a stub WebGL API. This check alone does not validate graphics.
- Native pthread C++ test: 20 deformation strokes over 30,000 vertices matched a brute-force reference.
- `tests/isolation.cjs`: separate V1/V2 theme/color/layout keys; V1 data preserved; V1 color changes do not alter V2 values; cache reads/deletion scoped to V2.

## Real browser execution

Chromium 134 headless, software WebGL2/ANGLE/SwiftShader, at **1440 × 1000** and **390 × 844** viewport sizes. These tests used desktop mouse input at both widths, not physical touchscreen hardware. CDN module requests were supplied unchanged through a local test request handler because direct browser networking was restricted. A test-only module hook exposes state to assertions; the shipped index.html has no such hook.

Passed at both sizes:

- Full editor initialization with no page errors or console errors.
- Selecting Grab after Paint and Move disables painting/transforms and selects sculpt mode.
- Main Grab deforms vertices, continues beyond the original surface, returns without accumulated drift, and undoes correctly.
- Actual canvas strokes for Inflate, Carve, Clay, Smooth, Flatten and Pinch change mesh vertices and remain finite.
- Worker workspace loads through real WebGL2/VAO, accepts Grab strokes and applies changed geometry back to the editor.
- Scene snapshot/restore completes.
- All **23 built-in shape factories**, including the anatomy assets, produce finite positions and indices within the vertex range.

## Reproduce

From this extracted package directory:

```sh
node tests/wasm.cjs
node tests/grab.cjs
node tests/worker.cjs
node tests/isolation.cjs
g++ -std=c++20 -O3 -pthread tests/threaded.cpp -o /tmp/p3-thread-test
/tmp/p3-thread-test
pip install playwright==1.51.0
python -m playwright install chromium
python tests/browser.py
P3_PHONE_VIEWPORT=1 python tests/browser.py
```

The browser harness serves the app itself on a temporary loopback port and needs network access to retrieve Three.js modules if they are not already in its temporary cache. It hides floating panels during canvas-drag assertions so controls cannot cover the test coordinates. It validates engine behavior, not every layout permutation.

## Remaining limits

These checks do not certify every application feature as bug-free. Real WebGPU rendering, Apple Pencil/touch pressure and cancellation, iPhone/iPad Safari, thermal/memory behavior, actual 60/120 Hz presentation, PWA installation/update on devices, and the Emscripten pthread browser build are unverified. Exports, rigging, movie editing and all possible imported files were not exhaustively exercised. Existing historical TEST_RESULTS files came from the original upload and are not new test results.

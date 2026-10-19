# V2.2.0 — Alpha Stamp brush

Added a separate Alpha Stamp sculpt brush with a cached radial alpha texture, distance-based spacing, pressure interpolation, Dot/Drag strokes, per-stroke capped height or accumulating volume, symmetry and undo. Existing sculpt brushes remain available. Choose Alpha Stamp in Sculpt and adjust its dedicated settings in the right panel. The optional performance worker retains its existing eleven brushes.

The reusable module also renders to 2D canvases. See `STAMP_ENGINE.md` for API hooks, settings, math and limitations. Tests cover the new brush on desktop/phone viewports plus reusable 2D capped/accumulating behavior; general app regressions and simulated touch/browser fallbacks are checked separately. Physical device limitations documented below still apply.

Upload the complete extracted package, including `engine/stamps.js`, `vendor/` and all other files, to V2. V1 code/settings remain separate.

# V2.1.0 validation

Tested in Chromium 134 with software graphics. Desktop regression covers eleven brushes, worker deformation/apply, 23 shapes, undo, scene edits, painting, native save/reopen, malformed-project rejection, rig creation, GLB/STL/OBJ/PNG export, voxel remesh and video export. Test-only hooks are injected by the local test server, never shipped in app code.

Additional tests cover phone viewport, actual browser-emulated touch events, forced WebGL1, simulated context loss/restoration with scene preservation, missing Worker/ResizeObserver, failed worker construction, and absent WebGL. Startup is tested with external HTTPS requests blocked. WebAssembly brush/BVH/undo tests, worker protocol and V1/V2 isolation checks also run.

Physical iOS/Safari, Android hardware, Apple Pencil pressure/tilt and native WebGPU are not verified. Compatibility requires WebGL, ES modules and a modern browser; the optional performance workspace requires Wasm SIMD, Worker and OffscreenCanvas plus WebGL2 or WebGPU. Unsupported graphics devices receive an explanation rather than a usable 3D viewport. No universal device or fixed frame-rate guarantee is made.

Current logs: `TEST_RUN_V2_1_0*.log`. Earlier records below describe earlier builds.

# V2.0.5 symmetry indicator checks

Targeted browser tests cover X/Y/Z local-coordinate reflection, axis labels, immediate symmetry-off hiding, the brush-indicator checkbox, and the worker's projected Mirror X preview. The prior V2.0.4 broader test record follows below. Actual Safari/Apple Pencil/WebGPU hardware remains unverified.

# V2.0.4 validation

## Environment

Real Chromium 134 headless, ANGLE/SwiftShader software WebGL2, served over loopback HTTP. Core tests ran at 1440 × 1000 and 390 × 844 viewport sizes using mouse input. Phone-sized tests are not physical iPhone or touch/Apple Pencil tests. Public Three.js modules were served unchanged through a test request handler because direct browser networking was restricted. A test-only state hook is injected by the harness; it is absent from the delivered app.

## Verified

- Complete initialization and JavaScript parsing: all 19 executable inline scripts, engine modules, service worker and anatomy asset script.
- Eleven distinct main brushes: Inflate, Carve, Clay, Smooth, Flatten, Pinch, original Grab, new Drag, Crease, Scrape and Polish. Real canvas drags changed finite vertex data.
- Drag continues beyond the original surface, returns without cumulative drift, and undoes. It is separate from Grab.
- Switching from Paint/Move to Drag selects sculpt mode and disables competing handlers. The brush contact ring becomes visible on the model.
- Real worker WebGL2/VAO initialization, Drag input and Apply back to the editor.
- All 23 built-in shape factories produce finite vertex positions and valid indices.
- Scene snapshot/restore, duplicate/remove, theme, background, material color/Matcap, perspective/orthographic projection, move snapping and five light types.
- Vertex painting, OBJ export, native .p3sculpt save/reopen and basic rig create/close.
- Neighbor-cache rebuild when geometry/topology changes.
- C++20 Wasm rebuilt with SIMD and fixed 128 MiB memory. Native Wasm fixtures verify all ten dab tools, finite geometry, undo and capacity checks. Drag has a separate mirrored movement/center seam/zero-drift/BVH refit test.
- Native persistent-pthread deformation matches brute force across 20 strokes / 30,000 vertices.
- V1/V2 storage isolation and scope-only offline cache ownership remain tested.

The core desktop and phone-sized browser runs completed without page or console errors. Additional desktop checks passed for PNG output (valid PNG signature), STL output, resolution-16 voxel remeshing, and a two-second 640 × 360 WebM turntable video. The final extended desktop suite also completed without page or console errors, including malformed-project rejection without scene changes. The video returned a nonempty download; software rendering skipped frame intervals, so this is not a frame-rate guarantee.

A preliminary 0.3-second video test returned an empty-video error, which the app reported. Two-second WebM recording passed. Very short clips and other encoder combinations remain device/codec-dependent.

## Limits

These tests do not prove every feature is bug-free or that every device sustains 60/120 FPS. Real WebGPU, Safari/iPadOS, physical touch/Apple Pencil, mobile thermal/memory behavior, PWA installation/update and Emscripten pthread glue in browsers remain unverified. Complex rigging/animation, arbitrary imported files and every layout combination are not exhaustive tests.

GLB export verification was blocked by a timed-out download of the Three.js GLTFExporter dependency in the test environment. The export code remains present; successful GLB output is not claimed for this run. Set `P3_TEST_GLB=1` when that dependency is reachable to include it in the browser suite.

## Reproduce

From the extracted package directory:

```sh
node tests/wasm.cjs
node tests/brushes.cjs
node tests/drag.cjs
node tests/worker.cjs
node tests/isolation.cjs
g++ -std=c++20 -O3 -pthread tests/threaded.cpp -o /tmp/p3-thread-test
/tmp/p3-thread-test
pip install playwright==1.51.0
python -m playwright install chromium
python tests/browser.py
P3_PHONE_VIEWPORT=1 python tests/browser.py
```

The browser harness serves the app on a temporary loopback port, retrieves public modules when its temporary cache lacks them, and hides floating panels for canvas-drag assertions. Existing historical TEST_RESULTS files came with the original upload and are not new validation evidence.

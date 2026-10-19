# V2.0.3 — Grab and smoother sculpting

- Main brush list: **Grab · Sculpt** selects an actual deformation brush and automatically exits painting/object transforms.
- Grab fixes a region at stroke start, follows a camera-facing plane, respects local transforms and mirror settings, continues outside the initial surface, and returns without cumulative drift. Applied in the main editor and worker workspace.
- Main/worker brush paths use closer, evenly spaced dabs and interpolate pressure. Main input uses coalesced pointer samples and bounded per-frame batches. Normals/bounds update once per batch; per-vertex vector allocations and repeated position-array allocation are removed from the main deformation loop.
- Switching from Paint or Move/Rotate/Scale to a sculpt brush no longer leaves those tools intercepting a sculpt gesture. Two-finger navigation flushes/records the pending stroke before switching gestures.
- V1/V2 settings isolation is retained.

Upload the extracted contents to **Project3StudiosV.2** only. Save your open project first, then reload V2 with **Ctrl+Shift+R** after deployment.

See `V2_VALIDATION.md` for the browser and engine checks and their limits.

# V2.0.2 — V2 app branding

The app title, header, home caption, version label, diagnostics and export filenames now identify V2. The project JSON schema version remains 1 for compatibility. Independent V2 settings are preserved.

# V2.0.1 — Separate settings from V1

V2 now has its own browser storage namespace for every persisted setting, including layout, light/dark theme, panel/accent colors, background, swatches, shortcuts, symmetry and quality options. It never imports old shared settings. First launch starts with V2 defaults; previously shared preferences are not carried over. V1 data is left intact.

V2 also uses separate, scope-specific offline caches and reads/deletes only its own cache versions. Keep V1 and V2 in separate repository URLs. Upload this package to **Project3StudiosV.2** only. Save any open work first, then reload V2 after deployment (Ctrl+Shift+R on desktop). Existing V1 code is untouched.

# Project3Studios V2 Sculpt

Built from `Project3Studios_SEPARATE_STYLE_MENU.zip`. The original editor, assets, separate style menu, materials, scene saving and other tools remain in this package. Historical 1.0.1 feature/test files describe the supplied editor, not validation of this V2 engine.

## Open and use

Upload the extracted contents to your existing HTTPS website, including the new `engine` folder. Do not open index.html directly from the iPhone Files app: worker/module/Wasm loading needs HTTP(S). For local desktop use run `python3 -m http.server 8000` in this directory and open http://localhost:8000.

1. Select a mesh in the editor.
2. Press **V2 Performance Sculpt**, at the top of the left panel.
3. Use Inflate, Carve, Flatten, Pinch or Grab. Pressure is used for deformation. Tilt and timestamp are carried in the input protocol for future brush extensions; they do not currently alter the brush.
4. Turn Orbit on to rotate; turn it off to sculpt. Zoom adjusts orthographic framing. Mirror X mirrors the brush in local mesh coordinates.
5. **Undo / redo stroke** swaps the most recent stroke snapshot. **Apply & return** updates that selected mesh, preserving its object transform/material and recording the change in the editor history. **Discard & return** leaves the original untouched.

The performance workspace intentionally shows one mesh with its own clay renderer. Scene lights, textures, rig playback and the full original tool set are available in the original editor. Smooth/Clay brushes remain there. This is an integrated optional engine, not a migration of every original editor subsystem.

## What is delivered

- Bundled, executable C++20 WebAssembly (`engine/sculpt.wasm`), with sources and rebuild scripts. No compilation needed to use the included single-worker build.
- Worker-owned positions, normals, indices, point BVH and deformation math; fixed 128 MiB Wasm memory with no growth during a stroke.
- OffscreenCanvas rendering with WebGPU adapter detection and WebGL2/VAO fallback. Unsupported workers/rendering show an error and allow return to the editor.
- Coalesced pointer events, four reusable transferable input buffers, bounded sample batches, pressure, tilt and timestamps. Sample drops under backpressure are counted; terminal stroke events are retained.
- Dynamic refit of changed BVH paths, Inflate/Carve/Flatten/Pinch/Grab, mirror X, one-stroke undo/redo, transfer back to the original scene.
- A generated matcap lookup texture with a more detailed lit-clay variant. Large meshes or slow work trigger the cheaper shader branch. This is not the original editor's full PBR material system.
- Optional persistent two-way C++ deformation pool source, Emscripten build script and loader path. The second worker owns one subtree and the coordinator owns the other. Normal recomputation stays serial.

## Boundaries and performance claims

This is a runnable V2 implementation plus an engineering template, **not a certified production release or a verified 60/120 Hz lock**. Desktop Chromium browser tests passed using software WebGL2 at desktop and phone-sized viewport widths; iPad/Safari hardware tests have not been run. Refresh rate, thermal throttling, mesh complexity and browser scheduling control the achievable rate.

The bundled build uses one Wasm worker and unshared linear memory. It works without cross-origin isolation. It isolates deformation and rendering from the main DOM thread; it does not eliminate the browser's JavaScript GC. No per-vertex JS objects are created in the hot loop. WebGPU command encoders, render passes, textures' current views and command buffers still involve browser-managed wrappers. Transfer/message handling and fallback timers can allocate. The implementation does not claim an entirely allocation-free JS loop.

`GPUQueue.writeBuffer` and `bufferSubData` upload/copy bytes. They cannot alias GPU VRAM with arbitrary Wasm memory. The implementation avoids JSON mesh serialization and uses typed views into Wasm, but **does not provide literal zero-copy GPU uploads**.

The BVH indexes vertices, with sphere queries and incremental bounds refitting. Expected local query cost is output-sensitive; worst case is linear, not a guaranteed O(log N). Picking chooses the nearest vertex near the view ray, not an exact triangle intersection. Sparse meshes can miss; dense sculpt meshes work best. Grab now uses a frozen stroke anchor and influence weights and continues pulling after the pointer leaves the original surface.

Capacity is 300,000 vertices and 600,000 triangles. Positions/normals are uploaded in full after an edited input batch. Normal recomputation scans all triangles. These are known throughput limits; dirty-range uploads and adjacency-based normal updates are necessary before claiming high-density production performance. There is no automatic reduction of mesh resolution. Deformation may produce self-intersections; there is no topology/remesh guarantee.

The displayed statistic is worker animation callback frequency while a pointer is held, not a GPU profiler or proof of presented frames. Treat 60 Hz (16.67 ms) and 120 Hz (8.33 ms) as measurement budgets. Benchmark on target hardware before making a frame-rate commitment.

See `V2_ARCHITECTURE.md` for the blueprint, compiler flags and threading deployment notes. See `V2_VALIDATION.md` for exact checks and untested paths.

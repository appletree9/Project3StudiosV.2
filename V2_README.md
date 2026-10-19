# V2.2.3 — Stone interface defaults

Dark: charcoal / warm gray / sandstone. Light: limestone / taupe / dark stone text. Both the main interface and worker workspace use neutral defaults. Custom appearance values are retained; the exact previous factory blue appearance is migrated to stone. Interface Style reset and the header accent reset return to the new defaults. Scene background, paint, and model material colors are unchanged. V1 settings and the V2.2.2 backup remain separate.

Palette browser checks cover fresh defaults, previous default migration, a custom saved palette, dark/light mode, reset and unchanged scene background. No sculpt math changes are included. Use Interface Style > Reset if you have a custom palette and want the stone defaults.

# V2.2.2 — deployment package

Start with `START_HERE.txt`. Includes `.github/workflows/deploy.yml`, required-file checks, and local static deployment without a Jekyll build. Set Pages Source to GitHub Actions and disable duplicate publishing workflows in your repository. Local checks cannot validate your account runner availability or clear already queued runs. App behavior retains the V2.2.1 strength fixes.

# V2.2.1 — Brush strength response

Fixed Alpha Stamp ignoring the main Strength slider. Strength now multiplies its capped/accumulating height, while Intensity still controls alpha coverage. The sculpt strength curve preserves a gentle low range and increases the upper deformation range; the standard and worker editors both use it. Grab/Drag remain anchored to pointer movement with a continuous bounded pull response, without a flat upper slider range. Worker smoothing/flattening gains are bounded for stability.

The main Strength slider now supports zero, half-percent increments and a percentage readout; the performance workspace also shows its percentage. Stamp and anchored Drag freeze strength at stroke start, so changed settings apply to the next stroke.

Validation compares identical strokes at 0%, 10% and 100% across all twelve standard brushes, plus worker low/high strength. Alpha Stamp cap, accumulation, dot, symmetry and undo regression checks remain included. Physical Safari/Pencil hardware remains unverified.

# V2.2.0 — Alpha Stamp brush

Added a separate Alpha Stamp sculpt brush with a cached radial alpha texture, distance-based spacing, pressure interpolation, Dot/Drag strokes, per-stroke capped height or accumulating volume, symmetry and undo. Existing sculpt brushes remain available. Choose Alpha Stamp in Sculpt and adjust its dedicated settings in the right panel. The optional performance worker retains its existing eleven brushes.

The reusable module also renders to 2D canvases. See `STAMP_ENGINE.md` for API hooks, settings, math and limitations. Tests cover the new brush on desktop/phone viewports plus reusable 2D capped/accumulating behavior; general app regressions and simulated touch/browser fallbacks are checked separately. Physical device limitations documented below still apply.

Upload the complete extracted package, including `engine/stamps.js`, `vendor/` and all other files, to V2. V1 code/settings remain separate.

# Project3Studios V2.1.0 — Stability update

Upload the **entire extracted ZIP contents**, including `vendor/` and `engine/`, to your V2 repository. Refresh after deployment. V1 code and settings remain separate.

This update bundles Three.js and its import/export modules locally, removing the CDN dependency for startup and GLB export. It adds clear startup failures, graphics-context recovery, worker startup timeouts and failure cleanup, and standard-editor fallback when offscreen workers are unavailable. Lower initial pixel density and antialiasing settings reduce GPU load on touch and low-memory devices.

Undo restores the selected object, checked transform selections, original reset geometry and independent rig metadata. Imports now record their final geometry and reset baseline; oversized files are rejected before parsing. Interrupted input is ended on tab changes or lost focus. Editor shortcuts no longer modify the main scene while the performance workspace is open. Older browsers without ResizeObserver retain resize support.

All eleven brushes and symmetry indicators remain available. See `V2_VALIDATION.md` for checks and device limitations. This is a source/deployment package, not an installed update to your live GitHub site.

# V2.0.5 — Symmetry brush indicator

When Sculpt symmetry is on, a gold brush outline shows the mirrored brush position across the selected object's X, Y or Z axis. The brush readout adds **Mirror X/Y/Z**. It follows the brush radius, hides when symmetry/brush indicators are disabled, and is excluded from PNG exports.

The performance workspace has a matching gold **Mirror X** outline. Its position is projected from the actual mirrored mesh point, so orbiting the view updates its location. During Drag, the mirror follows the stroke plane beyond the original surface. The label reports Mirror X when enabled.

Upload the extracted contents to **Project3StudiosV.2** and refresh after deployment. V1 settings remain separate.

# Project3Studios V2.0.4 Sculpt

This update restores the earlier **Grab** behavior and adds **Drag as a separate brush**, plus Crease, Scrape and Polish. It retains independent V2 settings and the optional Wasm performance workspace.

## Install

Save any open project. Extract the ZIP and upload its contents—including `engine/`—to the root of **Project3StudiosV.2**, replacing the previous V2 files. Do not upload it into the V1 repository. After deployment, reload V2 with Ctrl+Shift+R. Existing V2 layout/color settings remain separate from V1.

Use HTTPS hosting, or run `python3 -m http.server 8000` in the extracted directory for desktop testing at http://localhost:8000. Opening the HTML directly from Files does not support the worker/module loading path.

## Sculpt brushes

| Brush | Action |
| --- | --- |
| Inflate | Builds up the surface |
| Carve | Cuts into the surface |
| Clay | Adds clay along the stroke normal |
| Smooth | Softens bumps using neighboring vertices |
| Flatten | Levels the surface toward the starting plane |
| Pinch | Pulls points toward the stroke |
| Grab | Keeps the earlier incremental pull behavior |
| **Drag** | Pulls a fixed region with the pointer, including beyond the original surface |
| **Crease** | Cuts a groove and pinches its edges |
| **Scrape** | Shaves raised areas toward the brush plane |
| **Polish** | Smooths detail with reduced normal shrinkage |

All eleven are available in the main editor and performance workspace. Brush selection exits painting and object transforms. Radius, strength, plus/minus and symmetry remain available in the main editor; the performance workspace has its own radius, strength and Mirror X controls.

## Brush indicators

The main canvas displays a surface-aligned radius ring, center dot, pressure ring and tool/radius readout. **Brush indicators** turns them on/off and saves that choice in V2. The performance workspace has a screen-space brush-size preview: dashed while previewing, solid when the worker reports contact. Its checkbox hides the preview. Hover previews are available with a mouse; touch/stylus indicators appear on contact.

## Smoother strokes and fixes

- Evenly spaced brush dabs and interpolated pressure; coalesced pointer samples are accepted where supported.
- Main sculpt samples are bounded and processed in frame batches, with one normals/bounds refresh per batch.
- Position snapshots are reused for neighborhood brushes; other brushes avoid unnecessary whole-mesh copies. Squared-distance rejection avoids square roots for unaffected vertices.
- Measurement labels stop rebuilding during an active sculpt stroke.
- Raycasting reuses its target arrays and updates mesh/camera transforms before picking.
- Surface normals use correct transforms on scaled objects.
- Neighbor caches rebuild when topology or position/index attributes change.
- Repeated Matcap activation no longer accumulates preview materials; replaced previews are disposed.
- Worker Undo/settings wait for earlier queued input, and malformed native project geometry is rejected.
- Movie export disables its Export button while recording and restores it afterward.

## Performance workspace

Select a mesh and choose **V2 Performance Sculpt**. This opens a dedicated single-mesh worker canvas. **Apply & return** copies the edited geometry into the selected editor object and records history. **Discard & return** preserves the original geometry. The earlier editor still owns full scenes, materials, lights, rigging, projects and exports.

The bundled C++20 Wasm engine uses fixed 128 MiB memory, a refittable vertex BVH and CSR neighbor lists. It supports up to 300,000 vertices / 600,000 triangles. It attempts worker WebGPU and falls back to WebGL2/VAO. Emscripten and Zig rebuild scripts and optional persistent-pthread source are included.

This does not guarantee 60/120 FPS or literal zero-copy GPU uploads. Normals and GPU position/normal uploads still scan/stream the full mesh per changed worker batch. The BVH uses approximate ray-near-vertex picking. Browser-managed objects can allocate. Large meshes and actual device capabilities determine responsiveness.

See `V2_ARCHITECTURE.md` and `V2_VALIDATION.md`. Browser checks cover representative workflows, not every possible file, device or application state. Safari, physical touch/Apple Pencil and real WebGPU remain hardware-testing items. Historical feature/test files from the original upload are included for context and are not new V2 test results.

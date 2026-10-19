# V2.2.0 Alpha Stamp

Choose **Sculpt → Alpha Stamp**. Its settings are in **Alpha Stamp Brush** in the right panel. Existing Grab/Drag tools and the performance worker retain their original behavior. The new brush currently runs in the standard editor.

- Radius: screen pixels, integer. UI 1–512; reusable engine 1–2048.
- Intensity: 0–1, multiplied by PointerEvent pressure. Mouse uses full pressure.
- Spacing: fraction of radius. UI displays percentages; 5% is `.05`. Validated to 1–200% with a quarter-pixel minimum distance.
- Accumulate off: each vertex's maximum alpha coverage is measured against stroke-start geometry and normals, yielding one capped height layer. A new stroke may add another layer.
- Accumulate on: every moving stamp adds displacement; repeated overlaps build volume. Static pointer events do not repeatedly stamp.
- Dot: one imprint on pointer down. Drag: regular distance-spaced stamps, including LERP of pressure and coalesced event samples.

The normalized 128×128 radial alpha texture is rendered once into OffscreenCanvas (detached HTML canvas fallback). The 2D backend draws that cached texture. The 3D adapter samples the same cached alpha data in a camera-facing brush plane, limits influence to a local surface neighborhood, and deforms vertices. It does not draw a flat image over the viewport. Mesh resolution limits sculpt detail. Stroke height is proportional to world brush radius. Symmetry uses the existing local X/Y/Z plane and reflects the alpha basis.

The distance engine carries unconsumed arc length between pointer segments. With `step = max(.25, radius * spacing)` and segment length `d = hypot(dx,dy)`, stamps occur at distances `step - carry`, then one `step` apart. Each stamp position uses `start + delta * t`, where `t = distance / d`. Zero-length/nonfinite distances exit before division. The remainder is retained for the next segment. Captured pointer coordinates are bounded to the canvas plus one brush radius to avoid processing enormous off-canvas spans. Resizing the main viewport ends its active stamp stroke before changing projection. Settings are validated and frozen for the stroke.

## Reuse on a 2D canvas

```js
import {createStampEngine} from './engine/stamps.js';
const brush = createStampEngine({settings:{
  radius:40, intensity:.5, spacing:.05, accumulate:false, strokeType:'drag'
}});
canvas.style.touchAction = 'none';
canvas.addEventListener('pointerdown', e => {
  if (brush.handleStrokeStart(canvas,e)) canvas.setPointerCapture(e.pointerId);
});
canvas.addEventListener('pointermove', e => brush.handleStrokeMove(canvas,e));
for (const name of ['pointerup','pointercancel','lostpointercapture'])
  canvas.addEventListener(name, e => brush.handleStrokeEnd(canvas,e));
window.addEventListener('blur', () => brush.cancel());
```

The default backend paints white alpha into the 2D canvas (optional RGB `color`). For custom renderers supply `onStamp(x,y,pressure,settings,sampleAlpha)`; the adapter owns accumulation/cap behavior. `sampleAlpha(u,v)` accepts normalized brush coordinates [-1,1]. Public configuration in the app: `window.P3StampBrush.settings`. Type declarations: `engine/stamps.d.ts`.

2D capped rendering keeps a stroke-start pixel copy and maximum-coverage buffer. 3D keeps stroke-start positions, normals and per-vertex maximum coverage; these are released at stroke end/cancel, focus loss or tool change. Geometry updates use the existing bounded sample queue and batched normals/bounds refresh. Small spacing and dense meshes cost more work; this feature does not promise a fixed frame rate.

## Validation

`python tests/stamps.py` checks fast vs segmented paths, exact spacing, zero movement, dot, coalesced endpoint samples, pointer ownership/cancel, 2D cap/accumulation, 3D deformation/undo, dot, cap vs accumulation and mirrored layers. `P3_PHONE_VIEWPORT=1 python tests/stamps.py` uses a phone-sized viewport. General browser and compatibility tests remain in `tests/`. Physical Apple Pencil and Safari/WebGPU hardware remain unverified.

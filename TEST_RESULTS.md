# Verification — Header Slider r8 / Armature Studio r7

18 October 2026. Final local app tested in headless Chrome with WebGL software rendering and a touch-enabled phone-sized context. All inline JavaScript and service-worker syntax checks passed. No application JavaScript errors were recorded in the final runs.

## Armature posing and presets

- Created Simple (3 joints), Full Human (82), Humanoid (22), and Custom Chain (2) through the actual UI. All opened in Pose with enabled controls.
- Checked all vertex influences for finite normalized weights, valid bone indices and successful skin deformation. Sample maximum displacements in the preset tests were approximately 0.756, 0.859, 0.859 and 0.301 model units, respectively.
- Actual mouse range input and degree fields changed bone rotations and deformed the skinned mesh. Pose Undo/Redo passed.
- Edit joints reset preview rotations to neutral while preserving the separate pose. Rest coordinate editing and return to the preserved pose passed.
- Custom child addition and branch deletion passed. A mouse drag on a local rotation ring changed the selected joint.
- Actual emulated touch slider dragging and touch viewport-joint posing passed.
- A saved rig containing a deliberately invalid/null weight was reopened; invalid weights were recalculated and all resulting weights were finite and normalized.

## Animation and export

- On a detailed Female Body, saved whole-pose keys at 0 and 1 seconds, with a 60° lower-arm rotation in the second key.
- At 0.5 seconds the sampled rotation was 30°, matching quaternion interpolation.
- Play advanced the clock and the joint pose; Pause stopped progression; Start returned to 0. Key Undo/Redo passed.
- Save Project through the actual button and reopening through the real project file input preserved the 82-joint rig and both keys. Closing/reopening Armature retained the animation.
- Export produced valid GLB bytes containing an 82-joint skin and 82 rotation channels. Reimported those exact bytes with GLTFLoader, played the imported clip with AnimationMixer, and verified the 30° midpoint rotation.

## Existing features retained

- Inspector Move/Rotate/Scale buttons were visible and clicked; each transformed an object correctly with mouse and touch, without changing mesh vertices or camera position. Undo/Redo passed.
- Viewport object Move/Rotate/Scale handles passed mouse/touch drags on an already transformed object. Move grid snapping, selected-object tracking, Undo/Redo and project save/reopen passed. Chrome-emulated pen dragging passed; physical pen hardware was not tested.
- Bottom `p3AxisDock` toolbar remained absent.
- Blend/Merge regression: two overlapping transformed solids became a connected 3,032-triangle indexed surface. All boundary edges were shared by exactly two triangles. Existing sculpting, Undo/Redo and snapshot restoration passed; disconnected input was rejected and source objects remained. Earlier actual merged-project Save/Open checks are retained in development/test-results.json.
- Detailed anatomy assets, icons, manifest and PWA structure were retained. Service worker uses a fresh r7 cache. Frozen 1.0.0 app hashes were checked against its saved inventory during packaging. ZIP entries were compared to their source files with SHA-256.

## Limits

These are representative tests, not exhaustive checks of every browser/model/tool. Physical iPhone speed/memory, physical pen behavior, every external GLB application, complex/open/nonmanifold merge inputs and production-quality shoulder/finger weighting remain unverified. The animation system keys local rotations; it has no IK, root-motion/position keys, joint limits or multiple clips per rig. Automatic weights are starting weights, and generic skeleton placement needs fitting.

Tests captured the exact generated Blob bytes instead of relying on the OS/browser Downloads flow, which was canceled in this environment. Test-only hooks were inserted by a local server and are absent from the shipped app. Full physical-device offline/PWA installation behavior was not rerun. The published site was not changed by this chat.


## Header slider r8

Tested the revised app in desktop (1440px, then resized to 900px) and phone (390px) Chrome contexts. Every main header action (Sculpt, Camera, Undo, Redo, Focus, Save, Open, Export OBJ, theme and Armature) was visible and could be scrolled fully into view. Native slider Home/End reached both ends with synchronized disabled arrow buttons. Arrow scrolling worked. The actual Armature button opened its panel and Close worked after reparenting. Phone native swipe and touch slider dragging worked. Desktop header dragging and window resizing retained the slider behavior. The bottom object bar was absent. No application JavaScript errors were recorded. Existing r7 armature/animation checks above were run before this header-only revision; its Armature action was rechecked in r8.

Header text cleanup: removed ARMATURE STUDIO · HEADER SLIDER r8 from the visible build label. All functionality retained. Cache suffix r8-clean. Static source check passed.

Face scaling: all six sides of a rotated cube tested using mouse drags; opposite face fixed, other scale dimensions unchanged, undo restores position and scale. Render quality: Standard/High/Ultra each exported decoded 1600x900 PNGs, restored viewport size, pixel ratio, grid and object handles, with no browser errors.

Organized settings: checked 24 representative controls in correct categories; no duplicate element IDs; actual clicks verified Move, add Cube, painting on/off and brush selection, add light, Armature open/close, Render workspace and quality setting. Desktop and 390px mobile inspected. No browser errors.

Home cleanup: removed the requested description paragraph and verified both home buttons and copyright notice remain in the upload archive.

Transform snapping: all six face handles tested with 25 percent snapping on a rotated cube; opposite faces stay fixed and undo restores position/scale. Rotation ring drags for X/Y/Z produced 75/60/45 degree changes, all multiples of selected 15 degree increment. No browser errors.

Three-option snapping layout: browser verified all three cards share a row in the Inspector. Six directional scale and three rotation snapping checks passed again with no browser errors.

Closed presets: audited all 23 presets; zero open boundary edges, zero edges with more than two adjacent faces, no duplicate seam vertices and no degenerate triangles after welding. See solid-shapes-results.json.
Face Editor: real viewport click selected one face; Grow selected four; Delete removed exactly four triangles without changing vertex positions. Undo/redo and snapshot restore preserved triangle indices; Clear and overlay visibility verified. See face-editor-results.json.
Scene groups: grouped two of three cubes; movement affected only group members; shared-center scale and rotation preserved group spacing; hide/show and undo/redo worked. Actual project save and reopen retained names, group membership, hidden state and transforms. All-scene target affected all three. See scene-groups-results.json.
Regression: all six snapped directional scale handles and three rotation handles passed; Standard/High/Ultra PNG export and editor state restoration passed. No browser errors.

Scene Groups removal: source checked for no remaining scene group UI, visibility filtering or layer metadata handlers. Face Editor selection/delete/undo checks and all 23 closed-shape topology checks rerun.

Checkbox transforms: real mouse drags verified Move/Rotate/Scale affect two checked objects and leave a third unchanged. Undo/redo restored both objects together. Numeric movement affected checked objects equally. Actual project save/reopen retained the two checks. Existing six scale and three rotation snap checks also passed. No browser errors.

Optimization: merged two detailed heads totaling 277,134 source triangles at Detail 32. Scan conversion tested 10,026 candidate triangle/sample pairs versus the previous estimated 282,676,680 ray/triangle checks. Local run completed in 178 ms and produced 9,148 triangles with every surface edge shared by two triangles; the UI timer fired 18 times during the operation. Timing is local test evidence, not a device-independent guarantee. Cancellation preserved both original geometries. Existing connected-sphere merge, sculptability, undo/redo, restore and separated-object rejection passed. Actual Voxel Remesh button completed on a detailed head at resolution 24.
Keyboard: default and custom Move/Rotate, conflict rejection, Escape cancellation, typing-field protection, enable/disable and saved binding after reload passed. Checked-object transform and snapping regressions passed. No browser errors. Details: work/optimization-results.json.

Adaptive runtime/debugger: local browser idle test observed zero scene draws over a 500 ms idle interval and resumed drawing on wheel input. Thirty forced measurement updates/renders kept renderer geometry count at 6 before/after. Snapshot tests confirmed unchanged geometry arrays are shared, position-version changes invalidate the cache, and earlier snapshots remain unchanged. Smooth and Sharp pixel-density profiles applied independently of export settings. Debugger diagnostics, repeated errors, filters/search, JSON download, clipboard copy/fallback, log bounds, clear, close and 390px phone layout passed. No browser errors.
Regression: four armature presets (3/82/22/2 joints), actual mesh deformation, pose slider/ring, undo/redo, rest separation, keyframes/playback, saved animation project, legacy-weight repair, 82-channel animated GLB export/reimport/playback and touch posing passed. Face deletion/grow/undo, checked-object transforms, all six snapped scale handles and three rotation rings passed. Standard/High/Ultra exports decoded as 1600x900 PNG and restored editor state. Dense worker merge and custom-shortcut tests passed after scheduler changes.

Movie Editor tests: encoded a real 640x360, 15 fps WebM from an animated colored scene rig. Decoded frames showed thousands of changing pixels, retained red model color, and retained the chosen blue background within lossy-codec tolerance. Export did not modify source geometry/rig data, viewport size or pixel ratio. Cancel preserved source data and the previous video. Animated GLB import and subsequent video export passed. A saved full-human scene with 82 joints exported a decoded 640x360 MP4 successfully. No browser errors.
Very Low/Phone export tests: PNG decoded as 640x360; binary STL had 15,552 triangles and exactly 84+50*triangleCount bytes; OBJ retained 7,778 vertices, 15,552 faces and its material reference; static GLB retained material data; animated GLB retained 3 joints and one animation. Android phone emulation defaulted to 360p image/video and 15 fps. Its recorded MP4 decoded as 640x360. Desktop WebM and MP4 encoders both produced playable files. Phone emulation is not a substitute for testing physical hardware.
Regression tests after integration: four rig presets, real skin deformation, pose controls and rings, keyframes/playback, undo/redo, project save/open, legacy-weight repair, 82-channel GLB export/reimport/playback and touch posing passed. Checkbox transforms, face selection/deletion/undo, three snap controls, Standard/High/Ultra PNG export and viewport restoration passed. Debugger/idle rendering/memory tests and optimized dense-merge/custom-shortcut tests passed. See movie-test-results.json, movie-full-rig-results.json and phone-exports-results.json.

Quick tools r27: browser verified all four button routes and active states, actual mouse dragging, reload persistence, phone viewport clamping and keyboard movement; zero page errors. Touch/pen use the same pointer-capture drag path.

## Movie download feedback (r28)
Completed movies now start the video download automatically and show a prominent fallback download link. Export errors, invalid ranges and busy processing messages are visible above the editor instead of appearing only below the controls. Browser-tested actual WebM download, decoded animated/color frames, imported animation and cancellation preserving the prior movie. Live pre-fix site also generated a 640x360 MP4 in testing; the user's exact no-response cause remains unconfirmed.


## 3D Print / Flashforge (r29)
Dedicated quick binary STL export for Flashforge and other slicers. Selected/all scene, target longest dimension in mm or keep measurement scale, automatic centering and bed placement with Z up. Corrects mirrored winding, skips zero-area triangles, validates coordinates and yields during large exports. Exports rest sculpt geometry, not animation; separate overlapping objects remain separate. Use slicer repair/preview, supports and printer/filament profiles. Browser test verified 12,096 triangles, a 100 x 100 x 100 mm model, floor at Z=0, centered XY, keep-size path, invalid-size rejection and no page errors. Download request verified; test inspected generated STL blob because automated Chrome canceled filesystem persistence. Physical printing and slicer import have not been tested.


## Separate Style menu (r30)
Interface Style now opens its own floating Appearance menu rather than navigating to Interface/layout settings. Removed drag/minimize controls from the launcher button and spaced it away from Debug. Existing panel drag/minimize, color/transparency and reset controls remain. Verified actual clicks, open/close/toggle and color/Glass controls on desktop and 390px phone viewport with no page errors.


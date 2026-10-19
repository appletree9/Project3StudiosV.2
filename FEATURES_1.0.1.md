# Project3Studios V1 Sculpt 1.0.1 — Header Slider r8

This release repairs armature posing and adds simpler rig choices and real rotation-keyframe animation. The detailed anatomy meshes, sculpting, painting, object transforms, Blend/Merge and PWA assets remain. The frozen 1.0.0 baseline was not edited. This chat has not published changes to GitHub.

## GitHub Pages

Extract `Project3Studios_HEADER_SLIDER_R8.zip`. Its website files are at the ZIP root: upload those files directly to your repository root, replacing the existing `index.html`, `sw.js` and other app files. There is no enclosing `app/` folder in this upload ZIP. Do not upload the ZIP itself as the website.

Keep anatomy-assets.js, manifest.webmanifest and the icons alongside index.html. Pages should deploy your source branch's `/ (root)` directory. No build step is needed. After deployment, the header shows **FULL HUMAN ARMATURE · VERSION 1.0.1**. Save your project before accepting an in-app update/reload notification. Three.js and GLB import/export modules require internet on first use. The service-worker cache ends in `r8`.

## Header slider

Use the slider below the header to reveal every option. The arrow buttons move through the header a page at a time. You can also swipe the options row on touchscreens, scroll with a mouse wheel/trackpad, or focus the slider and use the arrow/Home/End keys. Slider position follows direct scrolling and updates when the window resizes. Undo, Redo, Focus and Export remain available on small screens instead of being hidden. Existing header actions and its draggable grip remain functional. The bottom object toolbar remains removed.

## Start a rig

Select your sculpt and open **Armature**. Open **Rig presets · Simple / Human / Custom**, choose a preset, and choose **Create selected rig**. Creating a replacement asks before replacing an existing rig and its animation. Main Undo can restore the previous rig.

| Preset | Joints | Use |
| --- | ---: | --- |
| Simple (original) | 3 | Root → Spine → Head; bend a simple sculpt |
| Full Human | 82 | Pelvis/root, spine/chest, neck/head, shoulders/clavicles, limbs, hands/fingers, feet/toes |
| Humanoid | 22 | A simpler body skeleton without individual fingers or toes |
| Custom chain | 2 initially | Start with root + child, then add your own branches |

New rigs open in **Pose**, with usable rotation controls. The preset is a starting fit: edit joint placement for your particular sculpt, especially fingers. Old project rigs are retained. Saved non-finite, zero-sum or invalid weights are recalculated automatically on reopen.

## Edit joints

Choose **1 · Edit joints**. Search for a joint or select it from the visible hierarchy; the selected viewport joint is gold. Drag a joint in the screen plane or restrict movement to X/Y/Z. Children follow their parent. Local coordinate fields allow precise placement. Choose **Whole skeleton** to move all roots together. **Resize selected branch** changes descendant offsets by the entered percentage; it does not resize the sculpt.

Add a child joint or delete a branch. At least one root must remain. Animation keys are extended/remapped when joints are added/deleted. Rest edits rebind the mesh and recalculate weights; pose rotations and rotation keyframes are kept separately. Use **Undo rig / Redo rig** or the main Undo/Redo.

## Pose

Choose **2 · Pose**, select a joint, and use the X/Y/Z sliders or degree fields. Drag a colored ring for rotation around a local axis: red X, green Y, blue Z. Drag the gold joint for quick X/Z rotation, or choose a single joint-drag axis. The actual skinned mesh and child joints follow the rotation.

Reset one joint or the whole pose. **Mirror pose** copies a selected Left/Right branch to its counterpart in a human preset. **Parent** moves selection up the hierarchy; **Focus joint** recenters the view.

Opening Armature temporarily suspends sculpt/paint/object-drag interaction so joint gestures do not accidentally edit the sculpt or move the entire object. Closing restores the previous interaction mode and shows the rest sculpt. Reopen Armature to resume the saved rig/pose. On phones, background tool panels hide while Armature is open and return when it closes. The Armature panel remains draggable.

## Animate

1. Choose **3 · Animate** to open the timeline. At 0 seconds, set a pose and choose **Save pose key**.
2. Move the playhead to another time. Change the pose using the joint controls, then choose **Save pose key** again.
3. Choose **Play**, **Pause** or **Start**. Scrub the playhead or tap a saved key to inspect it. Toggle Loop as needed.
4. Edit an existing key by visiting its time, changing the pose and saving again. Delete a key with **Delete key**. Undo/Redo includes keys.

Keys store the whole skeleton's local rotations. Interpolation uses quaternion slerp. Edits are not auto-keyed: save a pose key after changing a pose. For a smooth loop, use matching poses at the beginning and end. Set clip name, length (0.1–60 seconds) and frames/second (1–60). Key times snap to the frame interval; a clip supports up to 300 pose keys. Deleting later keys is required before shortening a clip past them.

**Save Project / Open Project** keeps the hierarchy, rest placement, current pose, weights and all animation keys. **Export rig + animation GLB** exports a real skinned GLB, with animation tracks when there are at least two keys. The final key is held to the clip's duration if needed. The exported GLB was reimported and replayed in Three.js during testing.

This is rotation-keyframe animation. It does not add IK, joint limits, root-motion/position keys, or multiple clips per rig. Automatic weights are functional starting weights; production shoulder/finger deformation may need refinement in dedicated rigging software. Physical iPhone/pen hardware and every external GLB application remain untested. One rig preview is active at a time; each object can retain its own saved rig.

## Object movement and blending

The Inspector retains **Move / Rotate / Scale / Sculpt**. Object Move has labeled world-axis arrows and Scale has labeled local-axis cubes (red X, green Y, blue Z); rotation rings are available too. Object axis handles are hidden while Armature is open. Mouse/touch/pen capture, move constraints, grid snapping, undo/redo and saved transforms remain. The floating bottom Move / Scale / Sculpt bar stays removed.

For **Blend/Merge**, check two to twelve closed objects in the Inspector, position them in contact/overlap, choose Detail and Blend smoothness, then Blend checked objects. This performs an actual voxel union and smooths the shared-vertex geometry. It rejects disconnected solids rather than silently creating separate pieces. There is no automatic bridge; overlap the objects or increase Detail for unresolved thin contacts. Sources remain until creation succeeds; Undo restores them.

World transforms are baked into the result. The first checked object in scene-list order supplies its material. Paint and rigs are not transferred to the fused result; reapply them afterward. Save/Open preserves the fused sculpt. Detail is resolution-dependent; thin features can disappear and smoothing can shrink details. Phone limits are stricter, and high-complexity inputs can be blocked by workload estimates. Accepted remeshing can briefly pause the page.

## Saved source and verification

`Project3Studios_V1_Sculpt_1.0.1_COMPLETE.zip` contains app/, development sources, browser test harnesses, generated test projects/GLB and continuation notes. `app/index.html` is authoritative; there is no build pipeline. `development/armature-studio-r7.js` is a readable extraction of the final rig implementation, not a separately loaded app file. Historical patch scripts are intermediate work and must not all be rerun against the final app.

See TEST_RESULTS.md for final checks and limits. Ordinary OBJ/mesh exports use the rest sculpt; use the Armature GLB exporter for the skin and animation.

Home page updated with current sculpting, blending, armature, posing, animation and export features, plus an application ownership and creator-content notice. Cache: r9-home.

Latest additions: Scale shows six colored face nodes; stretching one dimension keeps the opposite face fixed. Move retains its axis arrows. Render quality offers Standard, High and Ultra supersampling with lossless PNG output and device limits. Cache r11-render-quality.

Organized settings: expandable categories for Objects & transforms; Add & import models; Mesh editing & blending; Materials & painting; Armatures & animation; Lighting; Camera & lens; Render & image quality; Viewport & measurements; Projects & exports; Interface & layout. Find settings dropdown jumps to a category. Sculpt brushes and symmetry are together on the left. Project/export and interface controls moved from the header into their categories. Existing control nodes and handlers retained. Mobile shortcuts open the corresponding category. Cache r12-organized-settings.

Rotate and Scale snapping: Objects & transforms > Rotate & Scale Snap. Independent toggles; rotation steps 1/5/15/30/45/90 degrees; size steps 1/5/10/25/50 percent relative to drag-start size. Works with viewport handles and free object dragging. Preferences retained locally. Precision sliders retain separate snap controls. Cache r15-transform-snap.

Latest features (r19-scene-groups):
- All 23 built-in sculpt shapes start as closed, welded surfaces. Cylinder and Cone now have end caps; Plane is a thicker closed slab. Torus/Knot retain their intended through-openings. Existing saved sculpts are not automatically rebuilt.
- Mesh editing & blending > Face Editor: tap to select/deselect triangles, grow across shared edges, invert, clear, delete selected faces and undo. Deleting faces intentionally creates openings. Face edits preserve vertex positions/colors and saved rig weight arrays.
- Objects & transforms > Scene Groups / Layers: check objects, assign/rename groups, ungroup, target the active object, checked objects, a named group or all scene objects. Batch move, rotate and uniformly scale around a shared center; hide/show and focus. Group controls are separate from single-object viewport handles. Group membership and hidden state persist in projects and undo. Hidden objects are excluded from whole-scene OBJ/GLB/STL exports.
- The requested previous backup remains unchanged.

Current version: Scene Groups / Layers removed. Scene Objects uses the standard object list. Face Editor and all 23 closed welded presets remain.

Simple checked-object transforms: each Scene Object now has a checkbox. Check multiple objects and use Move, Rotate or Scale normally; the active checked object drives the other checked objects. Unchecked objects edit separately. Applies to viewport handles, object drags and precision sliders; snap settings remain available. Check selections persist in projects and undo. No layer system or separate group panel.

Performance and keyboard update (r22-optimized-hotkeys):
- Merge and Voxel Remesh now use projected-triangle scan conversion in a cancellable background Web Worker. Detailed heads are no longer rejected by the old triangles-times-rays estimate. Source-data memory, voxel-grid, overlap, processing-time and output-triangle limits remain. Cancel, failed processing and disconnected inputs keep source objects. Voxel edge contacts are regularized before surface extraction to keep closed surfaces.
- Rendering pauses while the document is hidden; measurement updates are throttled to 10 Hz and mesh-stat polling skips hidden settings.
- Interface & layout > Keyboard shortcuts: enable/disable, Set a custom combination, Clear, Restore defaults, conflict detection and browser-key protection. Saved locally. Letter keys follow the active keyboard layout. Keyboard shortcuts pause in typing fields, the welcome screen and mesh-processing dialogs.
- Defaults: G Move, R Rotate, S Scale, B Sculpt, C Camera, F Focus, P Paint, Ctrl+Z Undo, Ctrl+Shift+Z Redo, Ctrl+S Save, Ctrl+O Open, Shift+F Face selection, Delete selected faces (only in Face Editor), Alt+R Render PNG, Shift+G Grid, Alt+A Uncheck objects, 1–7 Sculpt brushes. Ctrl also accepts Command on Mac.

Adaptive performance and debugger update (r24-adaptive-performance):
- Interface & layout > Viewport performance: Auto, Smooth, Balanced and Sharp profiles. Auto adapts pixel density after sustained slow interaction; Smooth caps active rendering at 30 fps. Profile selection is saved locally. Viewport quality is separate from PNG export quality.
- One scene/rig/helper render scheduler replaces several independent animation loops. Rendering stops when idle and pauses for hidden tabs. Rig animation continues drawing while playing.
- Cached local bounds avoid rescanning detailed meshes each frame for scale handles. Sculpt normals/bounds update once after a complete dab rather than after every interpolation/symmetry step. Painting no longer rebuilds the object list for each dab on the active mesh.
- Measurement-line geometries/materials are disposed on replacement. Undo snapshots share unchanged geometry data, invalidate changed attributes, and trim history against a device-sensitive geometry-memory budget (at least current and previous steps are kept).
- Debug button: graphics health, object/triangle/mesh-memory counts, undo-memory estimates, draw calls, viewport profile and rendered FPS, worker activity, missing controls/assets and last voxel statistics. Search/filter events; repeated-message counts; bounded 500-event log. Copy or download a JSON report. Clipboard fallback supports manual copying. Reports contain diagnostics, not model vertex data or project contents. No automatic report transmission. Performance monitoring runs only with the debugger open.

Movie Editor and phone export update (r26-movie-phone-exports):
- New Movie Editor category: export silent animation videos with model/material/vertex colors and scene or custom background. Supports saved scene rigs and self-contained animated GLB files, clip choice, start/end trimming, half/normal/double speed, turntable or animation+turntable, automatic framing, 360p/480p/720p/1080p, 15/24/30 fps, quality and supported video formats. Armature Studio now has Make animation video, which saves/closes the rig editor and opens Movie Editor.
- Recording uses the browser's available MP4 or WebM encoder and runs in real time. Keep the tab visible. A progress dialog has Cancel. Previous successful video, sculpt geometry, rig data and viewport are retained if cancelled or if recording fails. Preview and download the finished video. Movie-source GLBs are separate from the sculpt and must be loaded again after restarting. Movie settings are retained locally and included in project saves.
- Projects & exports > Export device preset: Auto, Very Low / Phone, Low, Standard, High. Auto chooses Very Low on phones/low-memory devices. Very Low defaults to 640x360 PNG, standard image sampling, 640x360 video at 15 fps and a smaller bitrate, 256px GLB/movie textures, compact OBJ coordinate strings, and binary STL. Individual image/movie settings can be adjusted afterward. 3D mesh topology, skeleton weights and animation keys are retained; this preset does not decimate rigged models.
- Movie optimizations: pause scene rendering during recording, use one temporary recorder renderer, compile/warm the scene before timing, lower Auto recording size/rate for slow rendering, limit source/file/output memory and recording duration, bound texture size, and release encoder tracks/rendering resources on success, cancellation or failure. Phone output is capped at 720p; desktop recording at 1080p. Maximum clip video length is 30s on phone and 60s on desktop. Extremely detailed scenes can still exceed device limits.
- OBJ generation now uses chunks and yields between batches. Binary STL avoids very large ASCII strings and exports from stable geometry/transform copies. Project JSON is serialized per mesh into Blob parts using cached mesh arrays. GLB export bounds texture sizes and releases temporary geometry/material copies. PNG output excludes editor guides/helpers and restores them afterward.
- Browser format checks: https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder/isTypeSupported_static . A supported format can still fail if device encoding resources are unavailable. This version was tested in Chrome desktop and Android phone emulation; physical-device performance and codec availability vary.

## Draggable quick tools (r27)
Added a compact floating Move / Rotate / Scale / Sculpt toolbar. Drag its grip with mouse, touch or pen; position is saved and clamped to the screen. Existing sidebar tools, axis handles and snapping remain connected. Arrow keys move the focused grip; Shift moves faster.


## Movie download feedback (r28)
Completed movies now start the video download automatically and show a prominent fallback download link. Export errors, invalid ranges and busy processing messages are visible above the editor instead of appearing only below the controls. Browser-tested actual WebM download, decoded animated/color frames, imported animation and cancellation preserving the prior movie. Live pre-fix site also generated a 640x360 MP4 in testing; the user's exact no-response cause remains unconfirmed.


## 3D Print / Flashforge (r29)
Dedicated quick binary STL export for Flashforge and other slicers. Selected/all scene, target longest dimension in mm or keep measurement scale, automatic centering and bed placement with Z up. Corrects mirrored winding, skips zero-area triangles, validates coordinates and yields during large exports. Exports rest sculpt geometry, not animation; separate overlapping objects remain separate. Use slicer repair/preview, supports and printer/filament profiles. Browser test verified 12,096 triangles, a 100 x 100 x 100 mm model, floor at Z=0, centered XY, keep-size path, invalid-size rejection and no page errors. Download request verified; test inspected generated STL blob because automated Chrome canceled filesystem persistence. Physical printing and slicer import have not been tested.


## Separate Style menu (r30)
Interface Style now opens its own floating Appearance menu rather than navigating to Interface/layout settings. Removed drag/minimize controls from the launcher button and spaced it away from Debug. Existing panel drag/minimize, color/transparency and reset controls remain. Verified actual clicks, open/close/toggle and color/Glass controls on desktop and 390px phone viewport with no page errors.


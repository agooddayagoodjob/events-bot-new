# CherryFlash / Popular Video Afisha Design Brief

> **Status:** Concept pack for approval  
> **Goal:** define the visual system for a separate daily popularity-driven video product with a `Мобильная лента` 3D intro and `VideoAfisha`-style 2D scene flow.

## Product naming and boundary

- marketing / product name: `CherryFlash`
- product description: `Popular Video Afisha`
- internal mode key: `popular_review`
- planned canonical Kaggle runtime path:
  - `kaggle/CherryFlash/`
- runtime boundary:
  - this product is operationally separate from `CrumpleVideo`;
  - `CrumpleVideo` must keep its own render contract and daily reliability untouched;
  - this brief may still borrow approved intro aesthetics from older references, but that does not make the runtime part of `CrumpleVideo`.

## Canonical visual inputs

- Base asset to reinterpret: `video_announce/crumple_references/Final.png`
- Supporting references:
  - `video_announce/crumple_references/intro ref (day).png`
  - `video_announce/crumple_references/intro ref (weekend).png`
  - `video_announce/crumple_references/intro ref (1).png`
  - `video_announce/crumple_references/intro ref (2).png`
- Current active shot reference for the next concept round:
  - `/workspaces/events-bot-new/docs/reference/09bc959616262101b9cd310629f08b84.jpg`
  - this reference should be followed strictly for shot language and object relationship.
- Canonical frame size: `1080 x 1920`
- Draft preview renders may use a lower resolution, but they must keep the same `9:16` aspect and handoff geometry as the canonical frame.

## Active concept shift: `Мобильная лента`

- Product working name:
  - internal: `MobileFeed Intro`
  - concept label for review: `Мобильная лента`
- Status:
  - active intro direction for the next approval round;
  - previous slab-card stills remain archived as exploratory work, not as the current concept target.
- Strict reference lock:
  - the provided phone+ribbon composition is the canonical shot grammar;
  - allowed deviations are intentionally narrow:
    - the starting camera may be slightly closer/larger;
    - the phone tilt may be slightly calmer;
    - other composition changes should be treated as deviations requiring explicit re-approval.

## Visual thesis for `Мобильная лента`

- Visual thesis:
  - a premium product-shot phone with a continuous glossy poster ribbon passing through it, like a luxury magazine strip pulled through the device and turning into the first full-screen afisha.
- Content plan:
  - hero: phone + ribbon + strong CTA;
  - support: real dates/cities outside the phone in restrained editorial typography;
  - detail: visible neighboring posters in the ribbon prove variety inside the video;
  - final CTA: the second poster becomes the first full-screen afisha.
- Interaction thesis:
  - start from a readable static hero;
  - use one combined premium move over `~1.7-1.9s`, where camera straightening and push-in happen together rather than as two separate mechanical phases;
  - cut during the continuing zoom or at the end of the zoom phase, then let `video_afisha` continue into the upward move.

## Design intent

- Keep visual kinship with the approved editorial paper/poster references used earlier in the project:
  - bold editorial typography;
  - paper / poster / print energy;
  - strong date-led hierarchy.
- Shift the mood away from a generic "daily afisha" card toward a popularity-led format:
  - more "signal", "picked by audience", "what people are saving/watching";
  - still city-cultural, not entertainment-clickbait.
- The intro should feel intentionally designed, not like a generic AI gradient or a template slideshow.

## Non-goals

- No photorealistic city backgrounds.
- No soft purple gradients or generic neon tech look.
- No tiny metadata blocks that will disappear in motion.
- No overloaded collage that competes with the event posters themselves.

## Core visual system

- Palette baseline:
  - base: warm yellow / paper / cream;
  - text: near-black;
  - optional accent: deep red, traffic orange, or muted cobalt.
- Texture:
  - tactile paper wrinkles, torn edges, offset-print noise, folded poster feel.
- Typography mood:
  - compressed headline for the main phrase;
  - hard numeric/date block;
  - narrow supporting type for city stack / secondary line.
- Motion principle:
  - 2-3 decisive beats maximum;
  - strong reveal of date/title first;
  - no micro-animation clutter.

## Layout invariants

- The first frame must read instantly on mobile without pausing.
- For `Мобильная лента`, the dominant visual anchor is the phone+ribbon object, not an abstract date plate.
- The title / CTA system must stay short enough to survive motion and later reuse in stories.
- Dates/cities may live outside the phone as secondary editorial support, but they must not overpower the phone+ribbon hero.
- The composition must leave a clean path into the first poster transition.

## Story-safe contract

- The intro is designed for vertical story surfaces first.
- Critical content must stay inside a conservative story-safe area:
  - primary CTA;
  - time signal / date signal;
  - city support when shown;
  - the poster area that matters for the handoff read.
- Avoid placing key copy where story UI commonly appears:
  - top status / account bars;
  - bottom reply / action areas;
  - side edges that can be cropped or obscured by service chrome in Telegram, Instagram, and similar surfaces.
- Large decorative text may approach the safe boundary only if the readable core remains fully safe.

## MobileFeed scene contract

- One stylized 3D phone object is mandatory.
- One continuous poster ribbon is mandatory:
  - it runs left-to-right through the phone;
  - it is stitched from real event posters;
  - it behaves like glossy magazine sheets joined into one strip.
- Ribbon length contract:
  - number of visible poster panels is derived from the actual number of scenes/posters in the video announce;
  - the intro should not fake a longer or shorter editorial payload than the actual release.
- Poster order contract:
  - the second poster in the ribbon is the poster framed inside the phone at start;
  - that same poster must become the handoff poster for the first `video_afisha` scene.
- Physical behavior contract:
  - the ribbon must meet the phone and desk surfaces credibly;
  - it should not appear to hover or clip through the screen edge;
  - it should behave like glossy magazine paper with soft folds, mild spring, and gravity-led sag off the phone body.
  - ribbon text and poster artwork must stay non-mirrored and readable from the viewer-facing camera;
  - the strip must not penetrate the phone shell or sink through the desk plane;
  - the strip should read as dense coated magazine stock: it keeps its width, does not stretch, and mainly bends as a developable sheet with limited twist rather than as an elastic ribbon.
  - inside the phone, the ribbon must stay sufficiently planar across the master poster; strong curvature begins at or just beyond the phone edge, not across the central poster face.
  - the exit from the phone must match the strict reference: a broad magazine-like bend with readable neighboring posters, not a sharp collapse into the phone body and not a sudden drop that makes adjacent panels look pinched.
- Alignment contract:
  - posters inside the ribbon must be height-aligned and edge-stitched with no visible gaps;
  - stitching must feel intentional and premium, not like a rough collage seam.
- Poster-fit contract:
  - each poster keeps its full artwork area inside the ribbon;
  - the ribbon must not crop posters to a decorative band or partial slice;
  - no visible borders, gutters, or extra frames may appear around individual posters inside the ribbon;
  - all posters are scaled to one shared height while preserving their native width ratio;
  - poster panels touch edge-to-edge, flush joint to flush joint.
  - the second poster is the master panel for ribbon scaling and must fill the visible phone width in the hero frame language;
  - ribbon height must be solved from that master panel after matching its width to the phone width in the shot grammar;
  - neighboring posters may remain visible as the ribbon exits the device, but not so much that the center poster stops reading as the phone-width anchor.
  - several neighboring posters may remain visible in the hero frame exactly as allowed by the strict reference, but this visibility must come from camera/framing and paper bends, never from per-panel stretch, squeeze, or artificial collapse.
  - ribbon tail geometry must preserve the strip's panel-width distribution; broad paper bends are allowed, but adjacent posters must not be remapped into compressed shoulder zones that read as rubber instead of paper.
- Framing contract:
  - the second poster should sit inside the phone in the same center-led framing family used by `video_afisha` scene `1`;
  - the intro is allowed to stylize the phone environment, but not the handoff geometry;
  - ribbon scale must be solved from the second poster, with that poster width matching the phone screen width at the zoom target / handoff state.
  - in the hero frame, the ribbon sits in front of the phone screen content; the phone-screen typography/UI remains visible above and below the strip, as in the strict reference.
  - the ribbon must continue beyond the camera frame on both left and right sides in the hero frame; visible ribbon endpoints are a defect.
- Material / lighting contract:
  - the approved local phone asset is considered visually sufficient; if the phone reads wrong in render, the defect is in material, light, shading, or render setup rather than in the underlying model choice.
  - the environment should stay warm-milky, while the phone screen itself should read cooler, cleaner, and more luminous than the surrounding background.
  - the phone body must keep strong product-shot edge definition with readable highlights, clear contour separation, and contact shadows; a washed-out or noisy/blotchy silhouette is a defect.
  - the local phone model should keep its own screen construction; do not invent an extra black screen border if the asset does not have one.
  - the screen may begin bright and cool or directly in a darker app-like state, but by the late 3D phase it may move into a controlled near-black treatment while the sensor-island / camera block remains close to black and the upper phone contour stays readable against the environment.
  - ribbon posters must keep print density and color richness; chalky, dusty, or low-contrast poster reproduction is a defect even in approval renders.
  - saturated dark poster tones, especially reds, must not collapse into muddy near-black fields because of render lighting or tone mapping.
  - the hero shot should keep clear cast shadows from both phone and ribbon, close to the strict reference; weak or overly washed shadows flatten the scene and are a defect.
  - the three defects called out by the latest consultation — washed-out contact shadow, gray-lifted sensor island, and too-plastic phone shell with insufficient upper rim separation — have been addressed in the deep lookdev pass (2026-04-08); remaining polish targets are HDRI-driven environment reflections and final render-budget uplift.
  - the render should clearly separate three surfaces: milky environment, cooler phone screen, and darker premium phone shell.
  - the strict reference uses one dominant soft key from upper-left, a much weaker fill, a thin cool rim/spec edge on the phone shell, and a clear contact-core shadow with a softer tail falling down-right; the local light rig should follow that hierarchy rather than flattening the scene with ambient fill.

## Clean-frame contract

- Approval covers and the final intro hero-frame should show only **viewer-facing** copy.
- Remove from the visible cover:
  - concept labels;
  - debug/source notes like `/popular_posts`, `prod snapshot`, internal windows, or pipeline references;
  - explanatory support sentences that exist only for operator review.
- Preferred visible copy budget:
  - `1` main external CTA/title;
  - `1-2` CTA/support lines inside the phone;
  - optional outside dates/cities block when it materially improves the promise;
  - avoid extra explanatory copy beyond that.
- The cover should read as a cultural poster, not as an annotated design board.
- Inside-phone depth cue contract:
  - at least one CTA/support line should live inside the phone above and/or below the handoff poster;
  - this internal typography should help reveal depth and layering, not flatten the screen into a single pasted image.
- Current draft screen-layer routing:
  - upper on-screen label: count-driven product signal plus a compact real type cluster, for example `6 событий` + `кино • лекции • встречи • экскурсии`;
  - lower on-screen label: compact city cluster from the real payload, for example `КАЛИНИНГРАД • ЧЕРНЯХОВСК`;
  - exact sparse dates may stay outside the phone in the large editorial date block;
  - the phone-screen CTA should read like an interface layer rather than a poster headline: mixed case / UI casing is preferred over all-caps poster typography;
  - phone-screen CTA size and placement must be solved from the world-space phone screen after import and scale, not from an unscaled local mesh bbox, so the labels stay visibly above/below the ribbon at reference-like size;
  - the top phone CTA must keep a sensor/island safe area and may not run through the camera block;
  - the supplied `Cygre` pack should be used in its wider UI-appropriate weights rather than drifting into a narrower fallback appearance;
  - the lower phone label and the quiet bottom city treatment should also stay in `Cygre`, not fall back to the poster font stack;
  - for this shot family, the preferred top placement is an asymmetrical left-column lockup below the sensor area rather than a centered banner fighting the island;
  - the screen-layer typography should now be art-directed as if it belongs to a premium mobile app surface, with restrained UI hierarchy, sparse copy, and no print-caption feel;
  - both labels should read as real screen-surface layers attached to the moving phone screen, not as free-floating overlays;
  - the upper label should stay readable deeper into the push-in than the lower support line;
  - labels must remain screen-locked while visible and must not jump to a new layout system after the cut;
  - current approval path fades the labels on the phone surface just before the cut, so the first 2D frame starts without cross-cut CTA repositioning.
  - if useful for product value, the second line of the upper label may change to another real type cluster during the intro, but this is optional and must remain subtle, screen-locked, and non-distracting.
  - a dark app-like phone screen is now an approved treatment for this intro family; in that state the on-screen CTA should invert to light UI typography rather than preserving dark-on-light poster habits.
- Text collision rule:
  - text-over-text overlap is a defect, not a style;
  - if two viewer-facing text layers compete or intersect, the layout is not approved.

## Visual lineage and motion boundary

- Current repo references split into two visual families:
  - `kaggle/CrumpleVideo/crumple_video.ipynb` — current paper-unfold / paper-fold render language with Blender XPBD.
  - `kaggle/VideoAfisha/video_afisha.ipynb` — legacy overlay-first language with moving sticker strips, bento collage, and direct scene handoff.
- Confirmed boundary for `popular_review`:
  - **scene generation stays on** `kaggle/VideoAfisha/video_afisha.ipynb`;
  - **intro concept language** comes from `CrumpleVideo` references and their strong poster typography;
  - **intro implementation target** is now a short `1.0-1.5s` 3D sequence on a fresh Blender branch;
  - **decorative handoff to the first scene** uses the more energetic overlay/dispersal behavior from the legacy `VideoAfisha` family;
  - the mode should not switch to full paper-physics scene generation just because the intro styling borrows from Crumple refs.
  - this boundary is product-separating, not product-merging: `CherryFlash` is not the same runtime as `CrumpleVideo`.

## 3D intro boundary

- This mode no longer aims for a flat 2D-only intro as the final target.
- Final intro target:
  - start from a highly readable hero composition;
  - render that hero in 3D with visible depth/material/light;
  - transform it over `~3.2-3.4s`, because this concept now absorbs a slower premium opening move before the synced late-tail handoff instead of cutting back to the small centered legacy start frame;
  - end on a frame that can smoothly reveal or hand off into scene `1` of `video_afisha.ipynb`.
- Current implementation boundary for this pass:
  - only the intro block through the first 2D-ready poster frame is in scope;
  - later `video_afisha` scene redesign is out of scope until this handoff is approved.
- Approval artifact expansion:
  - for handoff validation the repo may render an approval clip that includes the full intro plus the first legacy `video_afisha` scene and the canonical music cue;
  - this does not change the production boundary, where Blender still owns only the intro.
- Blender scope:
  - Blender renders only the intro block;
  - `video_afisha.ipynb` still handles the main event-scene portion;
  - this keeps the 3D part expressive without slowing the full video pipeline unnecessarily.
- Approval flow before animation:
  - static 3D still pack first;
  - narrow to winners;
  - only then design the `1.0-1.5s` transform/handoff.
- Approval pack constraint after review feedback:
  - pseudo-3D paintovers are not enough;
  - the approval stills should be rendered by a real Blender scene, even if they use a lighter preview-sample profile than the future production intro.

## Handoff contract to `video_afisha`

- The second ribbon poster is the canonical bridge object.
- The intro camera move should not reset to the exact small centered `scene1-start` state if that creates a visible backward step.
- The preferred handoff is now:
  - during the continuing zoom with matched apparent speed, with sync anchored primarily to the legacy `0.9 -> 1.0` tail rather than to the earlier `0.4 -> 0.9` entry beat;
  - or at the end of the zoom phase, immediately before the upward move begins.
- Current measured audio anchor for the active cue:
  - using the current `Pulsarium.mp3` offset path from `video_afisha`, the strongest early accent lands at roughly `3.58s`;
  - therefore the clean intro should be paced so that this accent lands when the late `0.9 -> 1.0` tail completes and the first 2D scene starts its upward move.
  - the current handoff retune keeps scene `1` near local `~1.80s`, so the cut lands just after the start of `move_up`; swallowing the upward motion or cutting from an oversized 3D poster state into a smaller 2D state is a defect.
  - the validation clip should use a less delayed cubic in/out curve for the first upward move; a quintic curve starts too invisibly at the beat and then makes the move look sudden.
  - the 3D camera progress curve should retain a small non-zero tail velocity into the cut; if the close-in push fully eases to a stop before the 2D scene starts moving, the handoff reads as a stutter rather than a premium continuation.
  - the preview path no longer uses optical-flow interpolation or sparse-frame image blending for in-between intro frames; motion review now requires real per-frame 3D renders even in the cheap preview path.
  - the white-background push-in should be driven by one continuous global curve with a noticeable premium ease in and ease out; any mid-clip micro-stop, plateau, or near-linear mechanical push on white is treated as a motion defect, not as acceptable preview behavior.
  - the late close-in phase must use one coordinated progress solve across camera location, target, up vector, and lens; if those elements advance on mismatched progress curves and create visible flutter or micro-pauses, the move is rejected even if the frame cadence is real.
  - preview and clean final approval should avoid visible whole-frame hybrid phone/poster dissolves; softness now comes from tonal continuity in the early 2D frames rather than from blended dual-scene composites.
  - any dense rerender of the late intro tail must preserve the original absolute camera-keyframe timeline; if the dense tail is treated as a fresh short animation, the preview can jump back to an earlier wide shot and create a visible deja-vu/jitter defect.
- Motion quality rule:
  - the push-in must use premium easing and settle, not a linear or mechanical zoom;
  - even in draft approval quality, the timing should feel expensive, deliberate, and smooth;
  - in the clean final pass the opening should feel calmer and more graceful than the old short draft, while the ending remains tightly matched to the 2D continuation.
- First-gesture rule:
  - the opening motion should not be a blunt straight push-in;
  - it should feel like an expensive combined move that becomes more frontal to the phone screen while already moving inward.
- The end frame of the Blender intro should be close enough to the first `video_afisha` scene that the cut/handoff reads as one continuous move rather than a concept reset.
- Canonical behavioral note from the current legacy scene:
  - the first `video_afisha` poster starts as a centered `0.4x` poster on the `1080 x 1920` canvas, waits `1.3s`, then scales up before moving upward into the split layout;
  - therefore `Мобильная лента` should use the tail of that legacy zoom profile as the strict sync anchor, but may keep a freer first-half rhythm as long as the overall movement stays visually related and never cuts back to the tiny centered state after pushing further in.
- Draft animation preview rule:
  - fast low-sample preview renders are acceptable while tuning the handoff;
  - preview timing should still honor the target motion cadence rather than using a placeholder tempo.
- Current motion-preview note:
  - the draft handoff path now uses explicit camera roll control so the poster finishes upright rather than flipping during the push-in;
  - the current preview/approval path keeps the on-screen labels screen-locked and finishes their fade before the cut, instead of rebuilding them in the 2D tail;
  - the current preview now uses a matched cut on the late `0.9 -> 1.0` zoom tail rather than a dissolve back to the tiny centered poster state;
  - the previous draft moved the tonal fade into the early 2D continuation;
  - the active correction moves that tonal shift into the late 3D phase so the cut lands closer to the final darker state already in progress;
  - the old `~1.9s` draft timing is obsolete for the clean final pass;
  - the clean intro target now runs `~3.2-3.4s` and carries into the late 2D zoom / first upward-move beat;
  - the active motion-approval artifact is now intentionally cheaper than the clean pass: a `360 x 640` preview clip is acceptable as long as it preserves the same `9:16` handoff geometry and beat timing.
  - the same renderer may also emit a clean `--final` approval clip in full `1080 x 1920` once the preview timing and handoff are accepted; this full-HD path should keep the same motion grammar and music sync while raising the Blender render budget.
  - in clean `--final`, the intro must render every frame at full cadence; synthetic in-between intro frames from image blending or similar shortcuts are a defect because they create staircase motion, unreadable CTA, and fake smoothness.
  - motion polish, premium feel, and render cleanliness are the main active final-pass tasks.
  - the final pass should not rely on motion blur to fake smoothness; if blur makes the phone UI or screen typography look shadowed/smeared, keep the cadence and improve render cleanliness instead.
  - screen CTA should read as bonded to the phone glass/UI layer with no shadow-like separation from the screen plane.

## Current approval render path

- Preproduction execution path:
  - clean approval renders for CherryFlash should migrate onto Kaggle, because that is the intended real render environment for the product;
  - the current narrow preproduction deliverable is `intro + first 2D scene + music`, not yet the full `2..6` scene daily release.
- The active `Мобильная лента` approval path now has its own Blender still tooling:
  - `kaggle/CherryFlash/mobilefeed_intro_still.py`
  - `kaggle/CherryFlash/assets/`
  - orchestrated by `scripts/render_mobilefeed_intro_still.py`
  - draft motion preview:
    - `scripts/render_mobilefeed_intro_preview.py`
    - outputs low-sample storyboard / gif / handoff frame under `artifacts/codex/mobilefeed_intro_anim_preview/`
  - high-resolution approval clip:
    - `scripts/render_mobilefeed_intro_scene1_approval.py`
    - outputs the current `intro + scene1 + music` preview/final mp4 and frame pack under `artifacts/codex/mobilefeed_intro_scene1_preview/` and `artifacts/codex/mobilefeed_intro_scene1_final/`
    - current defect status: any final export that still inherits preview-style sparse-frame assembly is considered rejected until re-rendered with full-cadence Blender frames.
  - Kaggle preproduction runner:
    - `kaggle/CherryFlash/cherryflash.ipynb`
    - `kaggle/execute_cherryflash_intro_scene1.py`
    - this path is the intended preproduction render route for the clean `intro + first 2D scene + music` artifact.
    - the target long-term contract still mirrors the working project notebooks: mounted CherryFlash render bundle under `/kaggle/input`;
    - current preproduction bootstrap stays input-first: the notebook should try the mounted CherryFlash bundle under `/kaggle/input` first and only then fall back to the already-pushed CherryFlash branch head when dataset propagation is missing.
    - the current preproduction runtime must also stay compatible with Kaggle's bundled `moviepy` package layout, because the approval clip is assembled remotely rather than only on the local workstation.
  - current preview renders use the local `iPhone 16 Pro Max` glb:
    - `/workspaces/events-bot-new/docs/reference/iphone_16_pro_max.glb`
  - scene split for previews:
    - phone + ribbon + surface light/shadow are rendered in Blender;
    - the large external editorial CTA layer is composited after render for precise approval typography without flattening the 3D phone/ribbon shot.
- Current focused refinement path for the strongest single-scene approval round:
  - previous slab-card tooling remains useful as Blender infrastructure, but it is not the active composition target;
  - the next approval round should build a phone+ribbon scene that matches the strict reference shot;
  - the immediate defect-fix pass is specifically responsible for enlarging the phone-screen CTA, restoring a true phone-width master poster, and removing false horizontal pinching from neighboring ribbon panels before another clean animation/render round.
  - the active still pack must prove:
    - premium phone object quality;
    - believable continuous ribbon geometry;
    - correct second-poster framing for the future handoff;
    - readable CTA hierarchy without clutter.
- Font stack policy for the real 3D approval pass:
  - the external editorial layer may stay close to the current repo visual language:
    - `DrukCyr`
    - `Akrobat`
    - `BebasNeue`
  - the inside-phone CTA should move to a modern UI-oriented family from:
    - `/workspaces/events-bot-new/docs/reference/шрифт РО Знание.zip`
  - the phone-screen typography should read like a premium interface layer rather than a print-poster caption.
- Preview-sample policy for approval stills:
  - the static concept pack may use a faster sample budget than the future final intro render;
  - this is acceptable only for approval images, not as the final production-quality intro target.
  - current single-scene refinement stills use low-sample `Cycles CPU` because it is stable in the repo's headless environment and fast enough for one-frame approval passes.
- Clean-render policy for the current final pass:
  - the final `intro + scene1` validation clip must use a materially higher render budget than the approval preview;
  - visible draft-like grain on the phone shell, screen frame, and ribbon is not acceptable;
  - denoising, higher samples, stronger contact shadows, and more deliberate lighting are all allowed if they improve the premium product-shot read without breaking the handoff match.
  - phone-screen CTA slabs should not use drop-shadow treatment that visually detaches them from the screen plane.
  - if the screen goes dark in late 3D, the first 2D frames should not reintroduce a separate bright-to-dark background shift; the darker tonal state should already feel established by the cut.
  - once this artifact is accepted, the same production-minded Kaggle path should be extended from `intro + scene1` to the real CherryFlash release with `2..6` posters/scenes.

## Phone asset sourcing policy

- Asset priority for `Мобильная лента`:
  - confirmed local `iPhone 16 Pro Max` asset from the workspace:
    - `/workspaces/events-bot-new/docs/reference/iphone-16-pro-max.zip`
    - archive currently contains `source/iPhone 16 Pro Max_upload.fbx` plus texture files;
  - otherwise: mockup-ready Blender asset with editable screen and existing light/camera setup;
  - otherwise a high-quality realistic phone mesh with Blender-native or Blender-compatible materials;
  - otherwise a strong free phone mesh with local shading/lookdev.
- User-provided preferred asset pool for the next pass:
  - `CGTrader iPhone 16 Pro Max Mockup + Animations`
  - `Superhive MOCKUPZ`
  - `Sketchfab / Superhive iPhone 16 Pro / Pro Max` variants
  - free fallbacks such as `CGTrader iPhone 15 Pro 2023 free`, `Sketchfab iPhone 16 Free`, `BlenderKit` phone assets, `Fab` generic smartphone
  - optional lighting support: `Poly Haven Phone Shop HDRI`
- Governance rule:
  - asset choice must not silently change the concept;
  - the current implementation path should start from the provided local `iPhone 16 Pro Max` asset rather than continuing the generic asset hunt;
  - if a premium/mockup asset is unavailable, document the fallback used and continue with the same shot grammar rather than redesigning the scene around a weaker prop;
  - this fallback is non-blocking by default and should not pause concept development unless the user explicitly asks to wait for a specific asset.

## Data-backed mockup policy

- Approval mockups for this mode should be based on a **fresh prod snapshot**, not on a stale local copy.
- Candidate events for mockups should come from the same pool as `/popular_posts`, anchored to the freshest available metrics timestamp in the snapshot.
- When comparing **concept variants**, prefer keeping the same real data payload across all variants so the decision is about the visual system rather than about different event/date choices.
- The static approval pack should cover at least these editorial date cases:
  - sparse same-month dates;
  - true range within one month;
  - true range across months;
  - scattered multi-month dates including at least one clearly farther-future pick.
- Every mockup pack should ship with a compact manifest listing the selected event ids/titles/dates so date-topology decisions are reviewable without guessing.

## Date topology rules

- The intro must react differently to the actual structure of selected dates, not only to `min_date` and `max_date`.
- One cover must use **one coherent date notation system**.
  - Do not mix slash-separated anchors with a hyphenated continuation on the same frame if it can be read as a false range.
  - For sparse sets prefer either:
    - one exact anchor list, for example `6 • 7 • 8 • 9 • 10 • 12`;
    - or month-led notation with anchors, for example `АПРЕЛЬ` plus `9 • 10 • 12 • 17 +2`.
- Canonical display rules:
  - `single_day`
    - Example: `10 АПРЕЛЯ`
    - Large numeral + month + optional weekday/title line.
  - `continuous_range_same_month`
    - Example: `10-12 АПРЕЛЯ`
    - Large compact range is the primary graphic.
  - `continuous_range_cross_month`
    - Example: `30 АПРЕЛЯ — 2 МАЯ`
    - Split across two stacked month blocks or asymmetric left/right blocks.
  - `sparse_dates_same_month` for `2-3` anchor dates
    - Example: `10 / 14 / 21 АПРЕЛЯ`
    - Use explicit anchor dates rather than a fake range.
  - `sparse_dates_same_month` for `4+` anchors
    - Primary: month-led block, for example `АПРЕЛЬ`
    - Secondary: up to `4` anchor dates plus `+N`, for example `10 • 14 • 21 • 27 +2`.
  - `sparse_dates_multi_month`
    - Primary: month pair or cluster, for example `АПРЕЛЬ / МАЙ`
    - Secondary: up to `4` anchor dates, for example `10.04 • 21.04 • 02.05 • 11.05`.
- Strong typography rule:
  - even when dates are sparse, the intro should still look like a designed cover, not like a calendar widget or tiny metadata list.
- Fallback label allowed only when needed for readability:
  - `РАЗНЫЕ ДАТЫ`
  - `НЕСКОЛЬКО ДАТ`
  - but only as a support line, not as a replacement for the actual anchor dates.

## Ribbon geometry guardrails

- The ribbon must behave like glossy magazine paper:
  - dense stock;
  - readable stiffness;
  - soft drape and recognizable magazine bends.
- Each poster keeps its own image proportion on the paper surface.
- Width changes are acceptable only when caused by perspective, camera angle, or the sheet curvature itself.
- Local geometry or UV distortion that makes a neighbouring poster look implausibly pinched, squeezed, or wrinkled is a defect and should be corrected.

## Controlled diversity system

- Goal: each release should remain recognizably part of the same concept family, but differ enough that small Telegram previews do not look cloned.
- Diversity must be **controlled**, not random. Use a deterministic seed based on concept key + release date + selected date topology.
- At least `3` visible tokens should change between releases inside one concept:
  - one **silhouette token**
  - one **color token**
  - one **texture/support token**

### Shared variation tokens

- `date topology token`
  - single day, range, sparse dates; this already changes the headline silhouette.
- `accent color token`
  - rotate within a restrained family such as deep red / orange / cobalt / off-black.
- `texture token`
  - wrinkle map, tear pattern, print noise density, fold traces.
- `angle token`
  - one of a few preset angle families, for example `-7/-3/0/+4/+8`.
- `support-line token`
  - subline phrasing or issue-chip treatment, for example `БЫСТРЫЙ ОБЗОР`, `ПОПУЛЯРНОЕ`, `ВЫБОР ЗРИТЕЛЕЙ`.
- `city block token`
  - right stack / lower-right stack / vertical column.
- `accent placement token`
  - bar left/right, tape order, ticket overlap order, tear window position.

### Concept-specific variation knobs

- `V2 Ticket Stack`
  - vary ticket count (`2` or `3`);
  - vary overlap order;
  - vary dominant ticket color;
  - vary the angle family.
- `V4 Ripped Poster Wall`
  - vary tear direction;
  - vary which strip carries the strongest accent color;
  - vary negative-space reveal placement.
- `V5 Signal Strip`
  - vary accent bar side or tilt;
  - vary the relative scale of date block vs title block;
  - vary kicker placement.
- `V8 Future Tape`
  - vary tape order;
  - vary tape widths and slants;
  - vary whether the month/date sits on a separate top strip or is fused with the headline.

### Identity guardrails

- What stays fixed inside one concept:
  - font family hierarchy;
  - overall palette envelope;
  - headline-to-support scale contrast;
  - core motion grammar.
- What must not happen:
  - full-layout roulette;
  - switching into a different concept by accident;
  - losing the strong typographic read just to manufacture variety.

## CTA strategy

- The CTA is not a UI button. It should behave like an editorial sticker / tape / strip embedded into the poster composition.
- Its job is to answer the viewer's implicit question:
  - why should I open this video;
  - what is inside;
  - can I quickly decide **куда пойти / что посмотреть**.
- Working conclusion after review feedback:
  - `НАЙДИ СВОЮ ДАТУ` is strong linguistically, but semantically weaker for this mode because the viewer is usually choosing an event or outing, not a calendar date by itself.
- Separate the **headline promise** from the **CTA chip**:
  - headline families:
    - `КУДА ПОЙТИ`
    - `ЧТО ПОСМОТРЕТЬ`
    - `ПОПУЛЯРНОЕ`
  - CTA chip families:
    - `ВЫБЕРИ СОБЫТИЕ`
    - `КОРОТКИЕ АНОНСЫ`
    - `СМОТРИ ПОДБОРКУ`
    - `N КОРОТКИХ АНОНСОВ`
- Recommended routing by topology:
  - `single_day` / `true range`
    - prefer headline `ЧТО ПОСМОТРЕТЬ` or `ПОПУЛЯРНОЕ`;
    - CTA chip `СМОТРИ ПОДБОРКУ` or `N КОРОТКИХ АНОНСОВ`.
  - `sparse_dates_same_month`
    - prefer headline `КУДА ПОЙТИ`;
    - CTA chip `ВЫБЕРИ СОБЫТИЕ` or `КОРОТКИЕ АНОНСЫ`.
  - `sparse_dates_multi_month`
    - prefer headline `КУДА ПОЙТИ`;
    - CTA chip `ВЫБЕРИ СОБЫТИЕ`.
- Avoid CTA copy that sounds internal, statistical, or operator-oriented:
  - `/popular_posts`
  - `реальная выборка`
  - `prod snapshot`
  - window names like `7 суток`, `3 суток`, `24 часа`
- Strong recommendation for the next pass:
  - compare CTA wording with the same layout and the same real date set, so the decision is about copy rather than about a different composition.
  - treat `ВЫБЕРИ СОБЫТИЕ` as the primary CTA candidate;
  - keep `КОРОТКИЕ АНОНСЫ` and `СМОТРИ ПОДБОРКУ` as secondary candidates.
- Daily-mode CTA rule:
  - the default CTA family must stay evergreen across daily scheduled releases;
  - month-locked headlines like `КУДА ПОЙТИ / В АПРЕЛЕ` are not acceptable as the default outer message;
  - the temporal signal should change per payload, while the main promise can stay stable.

## CTA architecture for `Мобильная лента`

- CTA level `1`:
  - large external message, visible from preview distance;
  - role: answer why to open/watch the video.
- CTA level `2`:
  - inside-phone support line above the ribbon and/or inside-phone lower support line below the ribbon;
  - role: explain that several short afishas/announces are inside.
- Temporal CTA rule:
  - at least one CTA layer must include the actual temporal signal of the selected payload;
  - depending on the real example this may be:
    - exact date;
    - compact range;
    - month cluster;
    - another honest period marker that matches the selected set better than a fake continuous range.
- Recommended copy routing for the next approval round:
  - default external CTA:
    - `ВЫБЕРИ СОБЫТИЕ`
  - default inside-phone upper CTA:
    - `ПОПУЛЯРНОЕ`
  - default inside-phone lower CTA:
    - `N АНОНСОВ`
  - secondary alternates for later comparison:
    - external: `ЧТО НЕ ПРОПУСТИТЬ`, `КУДА ПОЙТИ`
    - inside-phone lower: `КОРОТКИЕ АНОНСЫ`, `СМОТРИ ОБЗОР`
- Dates and cities outside the phone are support copy, not CTA, unless one of them is intentionally promoted to satisfy the temporal CTA rule.

## Transition contract: fixed start + decorative dispersal

- The intro must begin from a **fixed readable hero frame**.
- After the fixed opening, the first `1.0-2.0s` should perform a decorative dispersal that transitions into scene `1`.
- Recommended timing:
  - `0.00-0.35s`: full static hold, thumbnail-safe.
  - `0.35-1.40s`: decorative spread/dispersal begins.
  - `1.40-1.90s`: first scene becomes dominant.
- This dispersal is not a hard cut and not a generic fade.
- The motion should feel like graphic parts are released from the cover:
  - strips peel away;
  - tickets flick to edges;
  - torn layers split;
  - accent bars wipe out;
  - tape pieces release and travel off-axis.

### Motion rules

- Max `3-5` animated pieces in the intro dispersal.
- Stagger piece timing with short offsets (`40-90ms`) so the handoff feels designed rather than explosive.
- Large pieces move first; smaller secondary chips lag behind.
- Exit vectors should be seeded and slightly varied between releases, but inside a narrow family per concept.
- The first scene may be revealed beneath the departing intro pieces, rather than appearing only after they fully disappear.
- Motion must preserve legibility of frame `0`; decorative spread begins only after the short hold.

### Recommended concept-to-scene handoff styles

- `V2 Ticket Stack`
  - tickets separate into different quadrants and expose the first poster below.
- `V4 Ripped Poster Wall`
  - strips tear apart sideways/upwards and reveal the first scene through the openings.
- `V5 Signal Strip`
  - accent bar wipes off first, then the title plate breaks into `2-3` rigid slabs.
- `V8 Future Tape`
  - tape strips release in sequence and whip out on diagonals, leaving the first scene underneath.

## Concept variants

### V1. Crumpled Banner

- Essence: one huge skewed headline strip across a wrinkled yellow paper field.
- Mood: closest to the current system, but tighter and more fashion-editorial.
- Motion: headline strip slams in; date locks a beat later.
- Fit: safest evolution path.

### V2. Ticket Stack

- Essence: intro built as overlapping ticket stubs with date, title, and city split across layers.
- Mood: event admission / collectible stub / city culture.
- Motion: tickets slide and slightly over-rotate into alignment.
- Fit: strong for "audience picked this" framing.
- Current approval status:
  - deprioritized / rejected for the current round because the composition tends to visually escape the frame and becomes harder to parse in small preview.

### V3. Folded Calendar

- Essence: the date block behaves like a folded printed calendar page, title set under the fold.
- Mood: future plans, saved dates, upcoming picks.
- Motion: fold opens downward, then title appears underneath.
- Fit: best if the mode should still feel scheduling-oriented.

### V4. Ripped Poster Wall

- Essence: layered torn-paper poster fragments, with the winning phrase revealed through ripped openings.
- Mood: urban poster culture, tactile, a bit bolder than current Crumple.
- Motion: paper tears/reveals in two steps.
- Fit: strongest visual identity candidate for a differentiated sub-mode.

### V5. Signal Strip

- Essence: one thick vertical or diagonal accent bar carries the date while the main title sits in oversized black type.
- Mood: alert / picked / noteworthy without becoming tabloid.
- Motion: accent bar wipes in first; headline snaps onto it.
- Fit: efficient, clean, easy to animate.

### V6. City Column

- Essence: tall right-side city stack becomes a key graphic element rather than a footnote, with a huge left headline.
- Mood: local media / cultural issue cover.
- Motion: city column scrolls up slightly while headline lands.
- Fit: best for reinforcing locality and channel identity.

### V7. Stamp Sheet

- Essence: intro looks like a sheet of oversized editorial stamps/marks, including the popularity cue.
- Mood: curated, selected, limited-edition.
- Motion: one or two stamp hits with subtle texture shake.
- Fit: good if we want a visible "popular pick" signal without using literal social icons.

### V8. Future Tape

- Essence: typographic tape strips crossing each other with date fragments and a bold short phrase.
- Mood: energetic, contemporary, slightly experimental.
- Motion: tape strips pull into place from opposite sides.
- Fit: strongest option for short, punchy intros with minimal clutter.

### V9. Black Plate

- Essence: deep black rectangle plate over warm paper, with cut-out type and one colored accent.
- Mood: more premium, more dramatic, less playful.
- Motion: black plate rises first, then type is revealed as if printed on top.
- Fit: best for a more serious editorial brand.

### V10. Offset Noise Grid

- Essence: modular grid with offset print misregistration, large date numerals, and small noisy crop marks.
- Mood: print studio / poster lab / cultured but raw.
- Motion: grid builds in pieces; numerals finish the composition.
- Fit: strongest if we want a visibly redesigned system, not just a theme variation.

## Recommended shortlist for first image generation round

- `V4 Ripped Poster Wall`
  - Strongest distinct identity if we want this mode to feel like a separate series.
- `V5 Signal Strip`
  - Most production-friendly and easiest to keep readable in motion.
- `V8 Future Tape`
  - Most contemporary option without losing the print/poster feel.

## Variants to deprioritize unless specifically requested

- `V2 Ticket Stack`
  - currently not recommended for the next approval round after user feedback about edge escape and unclear preview read.
- `V1 Crumpled Banner`
  - Safe, but may feel too close to the current Crumple system.
- `V9 Black Plate`
  - Strong, but risks feeling too heavy for a morning quick-review release.

## Prompt-ready direction notes

### Shared prompt ingredients

- format: editorial print poster intro, `1080 x 1572`
- palette: warm yellow paper, near-black typography, one restrained accent
- texture: crumpled paper, torn edges, offset print noise, poster wall tactility
- style: premium cultural city-media poster, not ad-banner, not glossy tech promo
- composition: giant date block, short title phrase, compact city stack, clean transition space
- avoid: photoreal background, generic gradient, purple bias, tiny text, meme energy

### Shared title language

- Base phrase family for this mode:
  - `БЫСТРЫЙ ОБЗОР`
  - `ПОПУЛЯРНЫЕ СОБЫТИЯ`
  - `ЧТО СМОТРЯТ СЕЙЧАС`
  - `ВЫБОР ПО РЕАКЦИИ`
- Exact final copy should be approved together with the selected concept.

## Motion guidance for the final intro

- intro duration target for the current `Мобильная лента` final pass: roughly `3.2-3.4s`
- date must appear before or together with the main phrase
- one main motion idea per concept is enough
- paper/tape/stamp motion should feel tactile, not "particle FX"
- the scene should read as an infinite white product-shot space with shadow falloff, not a gray tabletop whose edge becomes visible
- the phone motion path must stay continuous and expensive-looking:
  - no move where the phone first escapes upward/outward and then returns
  - no rollback feeling before the handoff
- approval sequencing for the next pass:
  - first prove the corrected motion path and beat-locked cut in a lower-cost motion preview
  - only then spend the higher clean-render budget on the final `intro + scene1`

## Confirmed 3D pre-roll direction

- Confirmed next phase after concept approval:
  - build a short `1.0-1.5s` 3D typographic intro beat using a fresh Blender branch rather than the older `3.6` path currently used by `CrumpleVideo`;
  - keep the 3D section limited to the opening hero object / typography / depth reveal;
  - then hand off into the improved legacy `VideoAfisha` flow for the actual event scenes.
- Practical constraints:
  - the 3D beat should not own poster generation;
  - the 3D beat should render as one compact intro scene, not per-event geometry;
  - if the 3D intro is disabled or fails, the static clean-frame intro remains a valid fallback.
- Visual target:
  - strong typography with real depth;
  - one memorable material cue, for example paper slabs, plates, extruded strips, or folded boards;
  - a short release/dispersal into the first 2D scene rather than a long standalone 3D showcase.
- Blender baseline for planning:
  - official latest stable on blender.org is `v4.4.3` (April 29, 2025);
  - current active LTS on blender.org is `Blender 4.5 LTS`, supported until July 2027;
  - working recommendation for this feature: target the fresh LTS branch first unless a specific add-on/runtime constraint forces the latest stable instead.

## Approval workflow for the next pass

1. Pick `2-4` concepts from the shortlist.
2. Confirm the preferred title phrase family.
3. Generate up to `10` static intro/cover variants grouped by chosen concepts.
4. Narrow to `1-2` winners before moving to motion and notebook integration.

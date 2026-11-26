# dino-series: notes for Claude Code

An illustrated dinosaur series of seven species (T. rex, Triceratops, Stegosaurus, Dreadnoughtus, Ankylosaurus, Spinosaurus, Pachycephalosaurus) as animated SVG, GSAP pages, poster and rig-sheet boards, and Three.js models. See README.md for the file map and rebuild commands.

## Decisions that must hold

- T. rex: `src/sp_trex.py` (dinokit pattern) is the definitive build since 2026-11-24; the boxy-head pipeline (`trex_drawing.py`, `trex_svg.py`, `trex_gsap.py`, `trex_poster.py`, `trex_rig.py`) and its baseline are removed. Head per `RESEARCH_GUIDE.md`: skull about 13% of length, lips over the teeth.
- Rework in progress (user, 2026-11-24): every species is redrawn from a hidden skeleton layer per `RESEARCH_GUIDE.md`, keeping group ids, classes and GSAP selectors. This round covers `svg/` and `gsap/` only; posters, rig sheets, styles, sprites and 3D follow later and are stale until then. Order: Dreadnoughtus, Spinosaurus, Stegosaurus, T. rex, Pachycephalosaurus, Ankylosaurus, Triceratops. Each species: research, preview PNG, user approval, build.
- Keep the existing group ids, classes and GSAP selectors unless asked (proportions and pivot positions change in the rework). Each `svg/*-animated.svg` and its `gsap/*-gsap.html` must carry the identical drawing; rebuild both together.
- All drawings are original. Do not trace or reproduce reference artwork the user shares; use references only for general anatomy.
- `RESEARCH_GUIDE.md` is the science reference for all seven species: chosen species and specimens, size and proportion targets, rig rules, debates and what to avoid. Read the species' section before drawing, rigging or scripting a claim about it. Its series rules hold: never invent a measurement, never present reconstructed soft tissue or colour as fossil fact, never drop a distinctive feature to simplify a rig, and label the seven together as a size comparison, not one ecosystem.
- The titanosaur is *Dreadnoughtus schrani* (decided 2026-11-24, replacing *Patagotitan*). Its skull and most of its neck are reconstructed; say so wherever it appears.
- Research before drawing. Before drawing or redrawing any species (2D or 3D), check its anatomy and size against published sources (the describing papers where reachable, the Natural History Museum Dino Directory, Wikipedia's description sections) and look at photos of mounted skeletons or skeletal diagrams for overall proportions. For 3D work, also look at published 3D models of the species (for example Sketchfab searches, museum scans such as the Smithsonian's, and well-regarded life restorations) and check the model from the side, front and three-quarter views, not only the default camera. Note open debates (posture, sail or plate shape) and pick the current mainstream view. Record the choices and sources in the README's "Scientific accuracy" section. Show the user a preview before building the full set.
- Lengths drive the group poster: use checked adult lengths for the species actually drawn, and cite them.

## How the drawings work

- Every moving part is a group inside a pivot wrapper: `translate(x y)` > group with id/class > `translate(-x -y)`. Rotate with `transform-origin: 0 0` (GSAP: `svgOrigin: "0 0"`).
- Layout: outputs in `svg/`, `gsap/`, `3d/` and `boards/`; builders in `src/`; screenshots in `shots/` (untracked). Run builders as `python3 src/<builder>.py`.
- `src/dinokit.py` is the shared toolkit (series style, motion CSS, poster and rig builders). Species modules `src/sp_<name>.py` (all seven, T. rex included) build a `SPEC` dict on import with no side effects; running them writes the outputs.
- Class prefixes: `tr-` (T. rex), `tri-`, `stg-`, `tit-`. Root classes: `<prefix>anim` (idle), `<prefix>acting` (click move), `<prefix>loop` (standalone SVG repeats the move).
- New species: add `src/sp_<name>.py` following the existing three, reuse `dinokit.Look`, `skin_part`, `piv`, `eye`, and give each moving part an id and a pivot.

## Character model rules (rework, user 2026-11-24)

Every reworked `svg/<species>-animated.svg` is an anatomical character asset for editing, rigging and animation, not a poster or scene.

- **Look:** cel-shaded vector; bold dark outlines of one consistent weight; clean smooth Béziers; flat base colours with a few controlled gradient shadows; clearly defined anatomical forms; subtle, simplified skin texture; a strong, research-based silhouette; polished educational finish.
- **Construction:** built from distinct anatomical parts; every independently moving part is its own group with a pivot at its joint; closed paths where possible; each part's outline lives in the same group as its fill; no tangled or needlessly intersecting paths; overlaps designed so a part can move or be separated without showing a gap.
- **Required groups** (nested inside the existing ids so GSAP selectors keep working): head/skull; upper and lower jaw where the anatomy has them; neck; chest/torso; pelvis/hips; tail in segments where it bends; left and right upper and lower forelimbs, hands and digits; left and right upper and lower hindlimbs, feet and digits; each species-specific structure (plates, spikes, horns, frill, sail, club, dome, osteoderm groups) as its own group.
- **Composition:** full body, three-quarter side view facing right, neutral standing pose, every structure visible, head, tail and feet inside the canvas, orthographic character presentation, transparent background, no ground plane, no ground shadow, no scenery.
- **Restrictions:** SVG geometry only; no raster textures, photographic effects, particle effects or background objects; no text, labels, watermark or frame; no tiny decorative paths.
- **Priority:** anatomical accuracy, then clean vector construction and animation-friendly separation, then visual complexity.

## Style

Dark outlines only on outer edges, dark stripes over the back and tail, a pale belly, gradient shading, scale texture and a warm rim light. Posters share one layout: Big Shoulders Display title, Public Sans text, a scene with depth, and an umber info band with three facts. Facts on posters must come from checked sources.

## Style variants (svg/styles/)

Eleven 2D design styles of one species, built by `src/styles.py` on `src/stylekit.py`. The big-head explainer style is the episode look (sprites come from it); the paleontologist host `src/char_paleontologist.py` is drawn in the same style. Emotions (face kit in `dinokit.face_eye`/`EMOTIONS`, body language in `sprites.BODY`) are sprite poses. Style choice and sources: `reports/Dinosaur SVG illustration styles.md` (local, untracked). They are separate files; the definitive drawings and the boxy-head baseline stay untouched.

All rules below must hold. Several come from `ANIMATION_GUIDE.md`: the variants are meant to become cutout sprites in its 2D-in-3D pipeline.

- **Distinct at a glance:** each style differs in shape language and technique (silhouette, line, how tone is made), never only in colour or filters; all must be told apart as thumbnails.
- **Rig intact:** keep every group id, class, pivot wrapper and the motion CSS; generate geometry inside each part's own group in original coordinates so texture moves with the part (no "shower door" patterns fixed to the page). Proportion changes (bigger head, shorter tail) go through the pivot wrappers, and a scaled head carries its jaw.
- **Sprite-ready:** transparent background in the SVG (backgrounds live in the preview page), crisp alpha silhouette with nothing soft or glowing outside it (the guide cuts sprites at `alphaTest: 0.5`), and readable at phone size, exported at 2x (1600 px wide).
- **No pure black:** ink is lifted charcoal (`#2A1C22` series outline or `#1d1e30` guide ink), never `#000000`.
- **Deterministic:** seed every random choice by species and part id, so rebuilds and the SVG/GSAP copies stay identical (the guide's Remotion renders need pure functions of the frame).
- **Survive the ink pass:** the guide's Sobel luma outline pass adds lines on contrast edges, so keep texture marks (dots, hatching, pixels) at 3 px or more at export size; avoid sub-pixel speckle that would flicker.
- **Geometry, not filters:** build marks as real shapes in Python; avoid `feTurbulence`/`feDisplacementMap` on animated parts (repaints every frame, slow on mobile).

## One-page design philosophy

Follow the principles from Stone Librande's GDC talk [One-Page Designs](https://www.youtube.com/watch?v=E9_wLks1kAg) when designing boards, posters, rig sheets and documentation:

- **One complete page, nothing hidden:** Fit each system, sheet or design concept onto a single self-contained page/board instead of sprawling multi-page docs that go unread and stale.
- **Visuals over walls of text:** Prefer diagrams, spatial layouts, flowcharts and annotated visuals over long prose.
- **Layered hierarchy like a poster:** Lead with an immediate visual hook for the big picture, with finer details and data readable on closer inspection.
- **Use the constraint to design:** Treat the page limit as a filter to cut fluff, clarify relationships and catch structural problems early.

## Episodes (video)

Remotion 2D-in-3D shorts in `src/video/`, one folder per episode in `episodes/`. `ANIMATION_GUIDE.md` holds the pipeline; these preferences override it where they differ.

- **Length 60–75 s** (1800–2250 frames at 30 fps). At least 60 s; cap 75 s.
- **Unrushed pacing:** voice at 1.0x, natural pauses kept (`prep:voice --max-pause 0.5 --keep-gap 0.3`), about 2.5–3 words per second, about 1 s of picture before the first word.
- **Show what you say:** every line has its speaker or the thing it names at the focal point, and every claim gets a visual (bite marks shown, a head pop popped). Nothing important off-frame or behind a caption.
- **Camera:** glides within and between stations; cut only when changing location.
- **Per episode:** lighting moods (Ep01: daylight to late afternoon, no night) and host format (two hosts, Skeptic = Puck and Paleontologist = Charon, or a single narrator).
- **Science on screen:** say only what the sources say, with their hedges ("likely"); show post-mortem evidence as feeding, not as a fight result. Cite in the README.
- **Voice:** Gemini TTS via `npm run gen:voice` (key in the repo-root `.env`, git-excluded; never print, commit or copy it). Whisper drops or mishears words; fix captions in `public/audio/transcript.json` by hand after every `prep:voice`.
- **Approval flow:** stills of every new shot, then a half-res draft for the user, then the 1080x1920 master only after approval. Renders go to `out/` (git-ignored).

## Git (this repo)

Markdown is committed here (README, guides, `CLAUDE.md`, episode scripts), an exception to the global rule. `HANDOVER.md`, `.env` and `out/` stay local.

## Checking work

Render to PNG with headless Chrome or Playwright and look at the result before calling something done. The 3D pages need a local server for module imports when testing offline.

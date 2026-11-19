# dino-series: notes for Claude Code

An illustrated dinosaur series (T. rex, Triceratops, Stegosaurus, titanosaur) as animated SVG, GSAP pages, poster and rig-sheet boards, and Three.js models. See README.md for the file map and rebuild commands.

## Decisions that must hold

- The T. rex head is the big, boxy skull with the rounded, blunt snout, drawn at 1.4x. It is the definitive version. Do not redesign it or swap in a wedge-shaped skull. `build5.py` checks the head's shapes, ids, classes and pivots against `versions/boxy-head-definitive/baseline.json` and stops if they change.
- Keep the existing body proportions, group ids, classes, pivots and GSAP selectors unless asked. Each `*-animated.svg` and its `*-gsap.html` must carry the identical drawing; rebuild both together.
- All drawings are original. Do not trace or reproduce reference artwork the user shares; use references only for general anatomy.

## How the drawings work

- Every moving part is a group inside a pivot wrapper: `translate(x y)` > group with id/class > `translate(-x -y)`. Rotate with `transform-origin: 0 0` (GSAP: `svgOrigin: "0 0"`).
- `dinokit.py` is the shared toolkit (series style, motion CSS, poster and rig builders). Species modules `sp_<name>.py` build a `SPEC` dict on import with no side effects; running them writes the outputs.
- Class prefixes: `tr-` (T. rex), `tri-`, `stg-`, `tit-`. Root classes: `<prefix>anim` (idle), `<prefix>acting` (click move), `<prefix>loop` (standalone SVG repeats the move).
- New species: add `sp_<name>.py` following the existing three, reuse `dinokit.Look`, `skin_part`, `piv`, `eye`, and give each moving part an id and a pivot.

## Style

Dark outlines only on outer edges, dark stripes over the back and tail, a pale belly, gradient shading, scale texture and a warm rim light. Posters share one layout: Big Shoulders Display title, Public Sans text, a scene with depth, and an umber info band with three facts. Facts on posters must come from checked sources.

## Checking work

Render to PNG with headless Chrome or Playwright and look at the result before calling something done. The 3D pages need a local server for module imports when testing offline.

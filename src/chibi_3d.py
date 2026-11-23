import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Chibi 3D models: soft clay, toy-proportioned versions of every species, sculpted from blended spheres (marching
cubes) under studio light. Writes 3d/<slug>-chibi.html for each. Each species keeps its real defining features
(horns and frill, plates and spikes, club, sail, long neck, boxy head) in toy proportions.
Every page shares the same clay, lights and controls; a species supplies its sculpt and its move."""
import pathlib

TOP = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chibi __NAME__</title>
<meta name="description" content="A soft, clay-style chibi __NAME__ in 3D. Drag to orbit, scroll or pinch to zoom, click it to __VERB__.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@800&family=Public+Sans:wght@400;600&display=swap">
<link rel="modulepreload" href="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.min.js" crossorigin>
<style>
  :root { --bg0: #2B3140; --bg1: #151922; --ink: #EEF0F4; --muted: #A9B0BE; --btn: #EEF0F4; --btn-ink: #151922; }
  html, body { margin: 0; height: 100%; }
  body { background: radial-gradient(120% 90% at 50% 38%, var(--bg0) 0%, var(--bg1) 70%); color: var(--ink); font-family: 'Public Sans', system-ui, sans-serif; overflow: hidden; }
  canvas { display: block; width: 100%; height: 100%; touch-action: none; }
  .panel { position: absolute; top: 20px; left: max(20px, env(safe-area-inset-left, 0px)); max-width: 340px; pointer-events: none; }
  h1 { margin: 0; font-family: 'Big Shoulders Display', 'Arial Narrow', sans-serif; font-weight: 800; font-size: 46px; line-height: 0.9; }
  p { margin: 8px 0 0; font-size: 14px; line-height: 1.45; color: var(--muted); }
  .bar { position: absolute; bottom: max(20px, env(safe-area-inset-bottom, 0px)); left: max(20px, env(safe-area-inset-left, 0px)); display: flex; gap: 8px; flex-wrap: wrap; }
  button { font: 600 14px/1 'Public Sans', system-ui, sans-serif; border-radius: 999px; padding: 11px 16px; cursor: pointer; border: 1px solid rgba(255,255,255,0.25); background: transparent; color: var(--ink); }
  button.primary, button[aria-pressed="true"] { background: var(--btn); color: var(--btn-ink); border-color: var(--btn); }
  button:focus-visible { outline: 3px solid #F2A7C3; outline-offset: 2px; }
  #status { position: absolute; inset: 0; display: grid; place-items: center; color: var(--muted); font-size: 15px; pointer-events: none; }
</style>
</head>
<body>
<canvas id="c" aria-label="3D chibi Triceratops. Drag to orbit, scroll to zoom."></canvas>
<div class="panel">
  <h1>Chibi __NAME__</h1>
  <p>Drag to turn it all the way around, scroll or pinch to zoom, and tap it to __VERB__.</p>
</div>
<div class="bar">
  <button type="button" class="primary" id="roar">__BUTTON__</button>
  <button type="button" id="spin" aria-pressed="false">Spin 360°</button>
  <button type="button" id="reset">Reset view</button>
</div>
<div id="status">Sculpting the model…</div>
<script type="importmap">
{ "imports": {
  "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.min.js",
  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
} }
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { MarchingCubes } from 'three/addons/objects/MarchingCubes.js';

// ---------------------------------------------------------------- look: soft clay under studio light
// __ABOUT__
const C = {
  clay: '__CLAY__', accent: '__ACCENT__',
  horn: '#F3E7D2', nail: '#E9DBC2', eye: '#1B1720', blush: '#F2A7C3',
  hemiSky: '#D8E2FF', hemiGround: '#7A2A55', rim: '#FFC2DA'
};
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 100);
const HOME = { pos: new THREE.Vector3(__CAMPOS__), target: new THREE.Vector3(__CAMTARGET__) };
camera.position.copy(HOME.pos);
const controls = new OrbitControls(camera, canvas);
controls.target.copy(HOME.target); controls.enableDamping = true; controls.minDistance = 3.5; controls.maxDistance = 24;
controls.maxPolarAngle = Math.PI * 0.49; controls.autoRotateSpeed = 2.0;

// lights: cool key from above-front, magenta bounce from below, warm-pink rim from behind
scene.add(new THREE.HemisphereLight(C.hemiSky, C.hemiGround, 1.35));
const key = new THREE.DirectionalLight('#FFFFFF', 2.4); key.position.set(4, 8, 5); key.castShadow = true;
key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 8; key.shadow.bias = -0.0004;
Object.assign(key.shadow.camera, { left: -5, right: 5, top: 5, bottom: -5, near: 1, far: 30 }); scene.add(key);
const rim = new THREE.DirectionalLight(C.rim, 1.6); rim.position.set(-5, 3, -4); scene.add(rim);
const fill = new THREE.DirectionalLight('#BFD0FF', 0.5); fill.position.set(-3, 2, 6); scene.add(fill);

// floor: only the shadow shows, plus a soft contact shadow under the animal
const floor = new THREE.Mesh(new THREE.PlaneGeometry(40, 40).rotateX(-Math.PI / 2), new THREE.ShadowMaterial({ opacity: 0.42 }));
floor.receiveShadow = true; scene.add(floor);
{
  const cv = document.createElement('canvas'); cv.width = cv.height = 128; const g = cv.getContext('2d');
  const grd = g.createRadialGradient(64, 64, 0, 64, 64, 64); grd.addColorStop(0, 'rgba(0,0,0,0.55)'); grd.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = grd; g.fillRect(0, 0, 128, 128);
  const blob = new THREE.Mesh(new THREE.PlaneGeometry(__BLOB__).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(cv), transparent: true, depthWrite: false }));
  blob.position.set(0.2, 0.005, 0); scene.add(blob);
}

// clay material: soft, slightly sheeny, with a faint hand-worked surface from 3D noise on the normal
function clay(color, rough = 0.62) {
  const m = new THREE.MeshPhysicalMaterial({ color, roughness: rough, sheen: 0.35, sheenColor: new THREE.Color('#FFE3EF'), sheenRoughness: 0.8 });
  m.onBeforeCompile = s => {
    s.vertexShader = s.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vWP;')
      .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvWP = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    s.fragmentShader = s.fragmentShader.replace('#include <common>', `#include <common>
varying vec3 vWP;
float h3(vec3 p){ p = fract(p * 0.3183099 + 0.1); p *= 17.0; return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }
float vn(vec3 x){ vec3 i = floor(x), f = fract(x); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(mix(h3(i), h3(i + vec3(1,0,0)), f.x), mix(h3(i + vec3(0,1,0)), h3(i + vec3(1,1,0)), f.x), f.y),
             mix(mix(h3(i + vec3(0,0,1)), h3(i + vec3(1,0,1)), f.x), mix(h3(i + vec3(0,1,1)), h3(i + vec3(1,1,1)), f.x), f.y), f.z); }`)
      .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
{ vec3 q = vWP * 7.0; vec3 d = vec3(vn(q) - 0.5, vn(q + 11.3) - 0.5, vn(q + 23.7) - 0.5) + 0.5 * vec3(vn(q * 2.7) - 0.5, vn(q * 2.7 + 5.1) - 0.5, vn(q * 2.7 + 9.4) - 0.5);
  normal = normalize(normal + 0.16 * d); }`);
  };
  return m;
}
const clayMat = clay(C.clay, 0.82), hornMat = clay(C.horn, 0.7), nailMat = clay(C.nail, 0.7);

// ---------------------------------------------------------------- sculpting with blended spheres (metaballs)
// Each sculpt is a MarchingCubes field inside a cube of side SIZE centred on CENTRE; spheres added with ball() melt together.
const ISO = 40, SUB = 80;   // a tight falloff: parts keep their size and melt together only where they meet
function sculpt(centre, size, res) {
  const mc = new MarchingCubes(res, clayMat, false, false, 200000);
  mc.isolation = ISO; mc.position.copy(centre); mc.scale.setScalar(size / 2); mc.castShadow = true; mc.receiveShadow = true;
  mc.reset();
  const U = (v, c) => (v - c) / size + 0.5;
  mc.ball = (x, y, z, r, carve = false) => mc.addBall(U(x, centre.x), U(y, centre.y), U(z, centre.z), (carve ? -1 : 1) * (ISO + SUB) * (r / size) ** 2, SUB);
  mc.capsule = (a, b, ra, rb, n = 5) => { for (let i = 0; i <= n; i++) { const t = i / n; mc.ball(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t, ra + (rb - ra) * t); } };
  return mc;
}
const UP = new THREE.Vector3(0, 1, 0);
function cone(parent, base, dir, r, len, mat, seg = 20) {
  const g = new THREE.ConeGeometry(r, len, seg, 4).translate(0, len / 2, 0);
  const p = g.attributes.position;                       // soft, slightly rounded horn tips
  for (let k = 0; k < p.count; k++) { const y = p.getY(k) / len; const s = 1 - 0.35 * y * y; p.setX(k, p.getX(k) * (0.75 + 0.25 * s)); p.setZ(k, p.getZ(k) * (0.75 + 0.25 * s)); }
  g.computeVertexNormals();
  const m = new THREE.Mesh(g, mat); m.castShadow = true;
  m.position.copy(base); m.quaternion.setFromUnitVectors(UP, dir.clone().normalize()); parent.add(m); return m;
}
"""

HELPERS = r"""
const dino = new THREE.Group(); scene.add(dino);           // the whole animal (hops on its move)
const squash = new THREE.Group(); dino.add(squash);         // squash and stretch
const accentMat = clay(C.accent, 0.7);
const eyes = [];
// glossy eye with a catchlight, looking out to the side and a little forward; optional blush below it
function addEye(parent, p, r = 0.13, s = 1, blush = true, fwd = 0.9) {
  const eye = new THREE.Group(); eye.position.set(p[0], p[1], s * p[2]); parent.add(eye);
  eye.add(new THREE.Mesh(new THREE.SphereGeometry(r, 24, 16).scale(0.85, 1.15, 0.6), new THREE.MeshPhysicalMaterial({ color: C.eye, roughness: 0.15, clearcoat: 1 })));
  const glint = new THREE.Mesh(new THREE.SphereGeometry(r * 0.22, 12, 8), new THREE.MeshBasicMaterial({ color: '#FFFFFF' })); glint.position.set(r * 0.3, r * 0.45, s * r * 0.45); eye.add(glint);
  parent.updateMatrixWorld(true);
  eye.lookAt(eye.getWorldPosition(new THREE.Vector3()).add(new THREE.Vector3(fwd, 0, s)));
  eyes.push(eye);
  if (blush) {
    const b = new THREE.Mesh(new THREE.CircleGeometry(r * 0.8, 24), new THREE.MeshBasicMaterial({ color: C.blush, transparent: true, opacity: 0.45, depthWrite: false }));
    b.position.set(p[0] + r * 0.4, p[1] - r * 2.0, s * (p[2] + r * 0.6)); b.lookAt(b.position.clone().add(new THREE.Vector3(0.5, -0.1, s))); parent.add(b);
  }
}
const mouthMat = new THREE.MeshStandardMaterial({ color: '#4A2E35', roughness: 0.8 });
function smile(parent, pts, r = 0.016) {          // mirrored smile line lying on the face
  for (const s of [1, -1]) parent.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts.map(([x, y, z]) => new THREE.Vector3(x, y, s * z))), 24, r, 8, false), mouthMat));
}
function nails(parent, x, z, n, r = 0.075, reach = 0.2, y = 0.07) {   // a fan of toenails at the front of a foot
  for (let i = 0; i < n; i++) {
    const a = (i - (n - 1) / 2) * 0.5, m = new THREE.Mesh(new THREE.SphereGeometry(r, 16, 10).scale(1, 0.75, 0.9), nailMat);
    m.position.set(x + reach * Math.cos(a), y, z + reach * Math.sin(a)); m.castShadow = true; parent.add(m);
  }
}
// a soft, rounded flat plate (rounded top, bevelled edges) standing on its base
function plateGeo(w, h, t = 0.08) {
  const s = new THREE.Shape(); s.moveTo(-w / 2, 0);
  s.bezierCurveTo(-w * 0.62, h * 0.45, -w * 0.32, h, 0, h); s.bezierCurveTo(w * 0.32, h, w * 0.62, h * 0.45, w / 2, 0); s.lineTo(-w / 2, 0);
  return new THREE.ExtrudeGeometry(s, { depth: t, bevelEnabled: true, bevelThickness: t * 0.5, bevelSize: t * 0.5, bevelSegments: 4, curveSegments: 18 }).translate(0, 0, -t / 2);
}
function pivot(parent, x, y, z = 0) {             // a joint at (x, y, z) whose children keep world coordinates
  const p = new THREE.Group(); p.position.set(x, y, z); parent.add(p);
  const inner = new THREE.Group(); inner.position.set(-x, -y, -z); p.add(inner);
  return [p, inner];
}
"""

MOTION = r"""
// ---------------------------------------------------------------- motion
const clock = new THREE.Clock();
let start = -10, nextBlink = 1.5;
const ease = t => t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2;
const bump = (t, a, b) => t < a || t > b ? 0 : Math.sin(Math.PI * (t - a) / (b - a));      // 0 -> 1 -> 0 between a and b
const ramp = (t, a, b, c, d) => t < a || t > d ? 0 : t < b ? ease((t - a) / (b - a)) : t < c ? 1 : 1 - ease((t - c) / (d - c));   // rise, hold, fall
const go = () => { start = clock.getElapsedTime(); };
document.getElementById('roar').addEventListener('click', go);
const spinBtn = document.getElementById('spin');
spinBtn.addEventListener('click', () => { controls.autoRotate = !controls.autoRotate && !reduceMotion; spinBtn.setAttribute('aria-pressed', controls.autoRotate); });
document.getElementById('reset').addEventListener('click', () => { camera.position.copy(HOME.pos); controls.target.copy(HOME.target); controls.update(); });
const ray = new THREE.Raycaster(), ptr = new THREE.Vector2(); let down = null;
canvas.addEventListener('pointerdown', e => { down = { x: e.clientX, y: e.clientY }; });
canvas.addEventListener('pointerup', e => {
  if (!down || Math.hypot(e.clientX - down.x, e.clientY - down.y) > 6) return;
  const r = canvas.getBoundingClientRect(); ptr.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ptr, camera); if (ray.intersectObject(dino, true).length) go();
});
addEventListener('message', e => { const d = e.data || {}; if ('spin' in d) { controls.autoRotate = !!d.spin && !reduceMotion; spinBtn.setAttribute('aria-pressed', controls.autoRotate); } if (d.reset) document.getElementById('reset').click(); });

function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / h;
  camera.position.copy(HOME.pos).sub(HOME.target).multiplyScalar(Math.max(1, 1.3 / (w / h))).add(HOME.target);
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize); resize();

function loop() {
  const t = clock.getElapsedTime(), k = t - start, idle = reduceMotion ? 0 : 1;
  const m = move(k, t, idle) || {};
  const breathe = 0.015 * idle * Math.sin(t * 2.2), sq = m.sq || 0;
  squash.scale.set(1 + 0.12 * sq, 1 - 0.14 * sq + breathe, 1 + 0.1 * sq);
  dino.position.set(m.fwd || 0, m.hop || 0, 0);
  if (t > nextBlink) { const b = t - nextBlink, s = b < 0.07 ? 1 - b / 0.07 : b < 0.16 ? (b - 0.07) / 0.09 : 1; eyes.forEach(e => e.scale.y = Math.max(0.08, s)); if (b > 0.16) nextBlink = t + 2.5 + Math.random() * 3; }
  controls.update();
  renderer.render(scene, camera);
}
renderer.setAnimationLoop(loop);
document.getElementById('status').remove();
</script>
</body>
</html>
"""

HELPERS += r"""
const beakMat = clay('#8E7B70', 0.6);
function addPlate(parent, x, y, h, w, row, mat = accentMat, lean = -0.12, t = 0.08) {
  const m = new THREE.Mesh(plateGeo(w, h, t), mat); m.position.set(x, y, row * 0.07); m.rotation.z = lean; m.castShadow = true; parent.add(m); return m;
}
function limb(parent, a, b, r, mat = clayMat) {   // a soft capsule from a to b
  const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b), d = B.clone().sub(A);
  const m = new THREE.Mesh(new THREE.CapsuleGeometry(r, d.length(), 8, 16), mat); m.position.copy(A).addScaledVector(d, 0.5);
  m.quaternion.setFromUnitVectors(UP, d.normalize()); m.castShadow = true; parent.add(m); return m;
}
const ball = (parent, p, r, mat = clayMat, sc = [1, 1, 1]) => { const m = new THREE.Mesh(new THREE.SphereGeometry(r, 24, 16).scale(...sc), mat); m.position.set(...p); m.castShadow = true; parent.add(m); return m; };
const V = (x, y, z) => new THREE.Vector3(x, y, z);
"""

SPECIES = {}

# ------------------------------------------------------------------ Triceratops
SPECIES["triceratops"] = dict(
    name="Triceratops", verb="make it charge", button="Charge", clay="#B3CDA8", accent="#D9C8B2",
    campos="5.6, 2.9, 6.4", camtarget="0.3, 1.15, 0", blob="4.6, 2.6",
    about="Triceratops horridus, chibi: the big head, solid frill, two long brow horns, short nose horn, beak and cheek points, with hoofed toes.",
    js=r"""
// body: a round barrel, stubby legs, a short upturned tail
const body = sculpt(V(-0.15, 1.15, 0), 3.4, 72);
body.ball(-0.15, 1.05, 0, 0.66); body.ball(0.25, 1.0, 0, 0.6); body.ball(-0.55, 1.12, 0, 0.55); body.ball(0.05, 0.82, 0, 0.55);
body.ball(0.62, 1.12, 0, 0.42);                              // neck, hidden under the frill
body.capsule([-0.95, 1.08, 0], [-1.48, 1.34, 0], 0.32, 0.12, 6);
for (const [x, z] of [[0.42, 0.36], [0.42, -0.36], [-0.52, 0.38], [-0.52, -0.38]]) body.capsule([x, 0.62, z], [x + 0.02, 0.24, z * 1.04], 0.26, 0.24, 4);
body.update(); squash.add(body);
cone(squash, V(-1.52, 1.36, 0), V(-1, 0.55, 0), 0.1, 0.26, clayMat);
for (const [x, z] of [[0.42, 0.36], [0.42, -0.36], [-0.52, 0.38], [-0.52, -0.38]]) nails(squash, x, z * 1.04, 3);   // three hooves show on each foot

const [headPivot, head] = pivot(squash, 0.7, 1.2);
const skull = sculpt(V(1.1, 1.45, 0), 3.0, 84);
skull.ball(1.2, 1.32, 0, 0.6); skull.ball(1.12, 1.12, 0.3, 0.42); skull.ball(1.12, 1.12, -0.3, 0.42);
skull.ball(1.62, 1.14, 0, 0.42); skull.ball(1.9, 1.06, 0, 0.3); skull.ball(1.84, 1.26, 0, 0.2);
skull.ball(1.86, 0.84, 0, 0.24); skull.ball(1.55, 0.86, 0, 0.32);
// frill: a solid shield behind the head, tilted back over the neck, with a gently waved rim
const FC = V(0.62, 1.66, 0), tilt = -0.62;
for (let k = 0; k <= 22; k++) {
  const a = -Math.PI * 0.6 + (k / 22) * Math.PI * 1.2, R = 0.86 + 0.035 * Math.cos(k * Math.PI * 0.5), y = Math.cos(a) * R, z = Math.sin(a) * R * 1.1;
  skull.ball(FC.x - y * Math.sin(tilt), FC.y + y * Math.cos(tilt), z, 0.18);
}
for (const [R, rr, n] of [[0.58, 0.23, 12], [0.3, 0.27, 7]]) for (let k = 0; k <= n; k++) {
  const a = -Math.PI * 0.6 + (k / n) * Math.PI * 1.2, y = Math.cos(a) * R, z = Math.sin(a) * R * 1.1;
  skull.ball(FC.x - y * Math.sin(tilt) - 0.04, FC.y + y * Math.cos(tilt), z, rr);
}
skull.ball(FC.x - 0.04, FC.y, 0, 0.32);
skull.update(); head.add(skull);
for (const s of [1, -1]) {
  cone(head, V(1.36, 1.74, s * 0.26), V(0.6, 1, s * 0.14), 0.11, 0.6, hornMat);        // brow horns
  cone(head, V(1.05, 0.98, s * 0.56), V(-0.2, -0.55, s), 0.07, 0.2, hornMat);          // cheek points
}
cone(head, V(1.88, 1.38, 0), V(0.45, 1, 0), 0.1, 0.32, hornMat);                         // nose horn
const bill = ball(head, [2.13, 1.02, 0], 0.17, beakMat, [1.0, 1.05, 0.8]); bill.rotation.z = -0.5;
const hook = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.16, 16).rotateZ(Math.PI), beakMat); hook.position.set(2.22, 0.9, 0); hook.rotation.z = 0.35; head.add(hook);
ball(head, [2.0, 0.84, 0], 0.12, beakMat, [1.0, 0.8, 0.75]);
smile(head, [[2.03, 0.93, 0.17], [1.9, 0.9, 0.27], [1.74, 0.91, 0.34], [1.58, 0.97, 0.4]]);
for (const s of [1, -1]) addEye(head, [1.56, 1.38, 0.42], 0.13, s);

function move(k, t, idle) {        // anticipation squash, hop forward with the head down, land, settle
  let c = { sq: 0, hop: 0, fwd: 0, nod: 0 };
  if (k >= 0 && k <= 1.5) {
    if (k < 0.25) { const u = ease(k / 0.25); c = { sq: u, hop: 0, fwd: -0.15 * u, nod: -0.3 * u }; }
    else if (k < 0.65) { const u = (k - 0.25) / 0.4; c = { sq: -0.6 * Math.sin(u * Math.PI), hop: 0.55 * Math.sin(u * Math.PI), fwd: -0.15 + 0.85 * ease(u), nod: -0.3 + 0.75 * ease(u) }; }
    else if (k < 0.8) { const u = (k - 0.65) / 0.15; c = { sq: 0.7 * Math.sin(u * Math.PI), hop: 0, fwd: 0.7, nod: 0.45 }; }
    else { const u = ease((k - 0.8) / 0.7); c = { sq: 0, hop: 0, fwd: 0.7 * (1 - u), nod: 0.45 * (1 - u) }; }
  }
  headPivot.rotation.z = -c.nod * 0.6 + 0.03 * idle * Math.sin(t * 1.1);
  headPivot.rotation.y = 0.08 * idle * Math.sin(t * 0.45);
  return c;
}
""")

# ------------------------------------------------------------------ T. rex
SPECIES["trex"] = dict(
    name="T. rex", verb="make it roar", button="Roar", clay="#D7A7B4", accent="#C88C9C",
    campos="6.2, 3.2, 7.2", camtarget="0.1, 1.45, 0", blob="4.4, 2.4",
    about="Tyrannosaurus rex, chibi: a big, boxy head with a rounded, blunt snout (the series' T. rex head), tiny two-fingered arms, strong legs and a balancing tail.",
    js=r"""
const body = sculpt(V(-0.2, 1.25, 0), 3.8, 76);
body.ball(0, 1.35, 0, 0.6); body.ball(0.35, 1.3, 0, 0.5); body.ball(-0.4, 1.42, 0, 0.55); body.ball(0.05, 1.08, 0, 0.46);
body.ball(0.55, 1.62, 0, 0.38);                                                          // neck
body.capsule([-0.8, 1.48, 0], [-1.75, 1.8, 0], 0.4, 0.12, 9);                           // tail, held level
for (const s of [1, -1]) {
  body.capsule([-0.25, 1.18, s * 0.36], [-0.15, 0.62, s * 0.42], 0.34, 0.22, 4);        // thigh
  body.capsule([-0.15, 0.62, s * 0.42], [-0.06, 0.24, s * 0.42], 0.2, 0.19, 3);         // shin
  body.ball(0.1, 0.17, s * 0.42, 0.19); body.ball(0.26, 0.15, s * 0.42, 0.15);           // foot
}
body.update(); squash.add(body);
cone(squash, V(-1.82, 1.82, 0), V(-1, 0.32, 0), 0.1, 0.24, clayMat);
for (const s of [1, -1]) nails(squash, 0.28, s * 0.42, 3, 0.06, 0.12, 0.07);           // three forward toes
// tiny arms with two fingers
const arms = [];
for (const s of [1, -1]) {
  const [ap, arm] = pivot(squash, 0.55, 1.28, s * 0.42); arms.push(ap);
  limb(arm, [0.55, 1.28, s * 0.42], [0.78, 1.08, s * 0.46], 0.08);
  for (const dz of [0.04, -0.04]) cone(arm, V(0.84, 1.05, s * 0.46 + dz), V(0.6, -0.8, 0), 0.025, 0.1, nailMat);
}
// head: big and boxy with a rounded, blunt snout
const [headPivot, head] = pivot(squash, 0.6, 1.75);
const skull = sculpt(V(1.3, 2.05, 0), 2.6, 80);
skull.ball(1.05, 2.15, 0, 0.55); skull.ball(1.0, 1.98, 0.28, 0.4); skull.ball(1.0, 1.98, -0.28, 0.4);
skull.ball(1.45, 2.05, 0, 0.47); skull.ball(1.78, 2.0, 0.13, 0.36); skull.ball(1.78, 2.0, -0.13, 0.36);   // broad, blunt snout
skull.ball(1.25, 2.5, 0.22, 0.13); skull.ball(1.25, 2.5, -0.22, 0.13);                                    // little brow bumps
skull.update(); head.add(skull);
const [jawPivot, jaw] = pivot(head, 0.95, 1.82);
const jawS = sculpt(V(1.45, 1.72, 0), 2.0, 64);
jawS.ball(1.05, 1.78, 0, 0.38); jawS.capsule([1.2, 1.7, 0], [1.82, 1.7, 0], 0.32, 0.27, 5);
jawS.update(); jaw.add(jawS);
ball(jaw, [1.55, 1.86, 0], 0.26, new THREE.MeshStandardMaterial({ color: '#8E3A4E', roughness: 0.7 }), [1.6, 0.35, 0.8]);     // mouth
for (const s of [1, -1]) {
  cone(head, V(1.96, 1.68, s * 0.17), V(0.1, -1, 0), 0.035, 0.11, hornMat);              // two little front teeth
  cone(head, V(1.72, 1.66, s * 0.3), V(0, -1, 0), 0.03, 0.09, hornMat);
}
smile(head, [[2.08, 1.76, 0.2], [1.85, 1.71, 0.34], [1.55, 1.73, 0.42], [1.28, 1.84, 0.46]]);
for (const s of [1, -1]) addEye(head, [1.32, 2.28, 0.53], 0.12, s);

function move(k, t, idle) {         // roar: dip, then throw the head up with the jaw wide
  const pre = bump(k, 0, 0.3), up = ramp(k, 0.25, 0.45, 1.1, 1.5);
  const shake = k > 0.45 && k < 1.1 ? 0.06 * Math.sin(k * 40) : 0;
  headPivot.rotation.z = 0.32 * up - 0.16 * pre + 0.03 * idle * Math.sin(t * 1.1);
  headPivot.rotation.y = 0.08 * idle * Math.sin(t * 0.45) * (1 - up);
  jawPivot.rotation.z = -0.55 * up * (1 - shake);
  arms.forEach((a, i) => a.rotation.z = 0.5 * up * Math.sin(k * 18 + i) + 0.05 * idle * Math.sin(t * 2 + i));
  return { sq: 0.55 * pre - 0.25 * bump(k, 0.3, 0.6) };
}
""")

# ------------------------------------------------------------------ Stegosaurus
SPECIES["stegosaurus"] = dict(
    name="Stegosaurus", verb="make it swing its tail", button="Swing", clay="#A8CAC4", accent="#EBA27F",
    campos="6.2, 3.3, 7.2", camtarget="-0.1, 1.2, 0", blob="5.0, 2.6",
    about="Stegosaurus stenops, chibi: broad, round-topped plates in two staggered rows, tallest over the hips, a small low head, longer hind legs and four tail spikes pointing out to the sides.",
    js=r"""
const body = sculpt(V(-0.1, 1.0, 0), 3.4, 72);
body.ball(-0.35, 1.15, 0, 0.64); body.ball(0.15, 1.0, 0, 0.6); body.ball(0.55, 0.9, 0, 0.48); body.ball(0, 0.8, 0, 0.5);
body.capsule([0.75, 0.95, 0], [1.05, 0.86, 0], 0.32, 0.26, 3);                          // short neck
for (const s of [1, -1]) {
  body.capsule([-0.4, 0.78, s * 0.38], [-0.38, 0.24, s * 0.4], 0.27, 0.23, 4);          // longer hind legs
  body.capsule([0.5, 0.62, s * 0.34], [0.52, 0.22, s * 0.36], 0.22, 0.21, 4);           // short forelegs
}
body.update(); squash.add(body);
for (const s of [1, -1]) { nails(squash, -0.38, s * 0.4, 3); nails(squash, 0.52, s * 0.36, 2, 0.065, 0.17); }
// plates: two staggered rows, tallest over the hips
for (const [x, y, h, w, row] of [[0.86, 1.12, 0.26, 0.24, 1], [0.64, 1.28, 0.36, 0.32, -1], [0.4, 1.44, 0.48, 0.4, 1], [0.14, 1.56, 0.58, 0.48, -1],
                                  [-0.13, 1.66, 0.64, 0.52, 1], [-0.4, 1.7, 0.62, 0.5, -1], [-0.68, 1.6, 0.5, 0.42, 1], [-0.92, 1.44, 0.36, 0.32, -1]]) addPlate(squash, x, y, h, w, row);
// head: small and low, with a beak
const [headPivot, head] = pivot(squash, 1.0, 0.88);
const hs = sculpt(V(1.4, 0.86, 0), 1.8, 60);
hs.ball(1.3, 0.92, 0, 0.36); hs.capsule([1.4, 0.86, 0], [1.72, 0.76, 0], 0.28, 0.2, 4);
hs.update(); head.add(hs);
ball(head, [1.86, 0.74, 0], 0.1, beakMat, [1.2, 0.9, 0.9]);
smile(head, [[1.84, 0.69, 0.12], [1.7, 0.67, 0.2], [1.55, 0.71, 0.27]], 0.013);
for (const s of [1, -1]) addEye(head, [1.42, 1.0, 0.29], 0.11, s);
// tail with two plates and four spikes that stick out sideways and back
const [tailPivot, tail] = pivot(squash, -0.8, 1.2);
const ts = sculpt(V(-1.3, 1.26, 0), 2.0, 56);
ts.capsule([-0.75, 1.2, 0], [-1.75, 1.36, 0], 0.34, 0.1, 8);
ts.update(); tail.add(ts);
addPlate(tail, -1.08, 1.4, 0.3, 0.28, 1); addPlate(tail, -1.32, 1.4, 0.22, 0.22, -1);
for (const s of [1, -1]) {
  cone(tail, V(-1.52, 1.38, s * 0.06), V(-0.55, 0.35, s), 0.06, 0.34, hornMat);
  cone(tail, V(-1.7, 1.4, s * 0.05), V(-0.8, 0.3, s * 0.8), 0.05, 0.3, hornMat);
}

function move(k, t, idle) {         // wind the tail away, whip it across, damped settle
  let w = 0;
  if (k >= 0 && k < 0.35) w = 0.45 * ease(k / 0.35);
  else if (k >= 0.35 && k < 0.6) w = 0.45 - 1.2 * ease((k - 0.35) / 0.25);
  else if (k >= 0.6 && k < 1.8) w = -0.75 * Math.exp(-3 * (k - 0.6)) * Math.cos((k - 0.6) * 8);
  tailPivot.rotation.y = w + 0.1 * idle * Math.sin(t * 1.3);
  headPivot.rotation.z = 0.04 * idle * Math.sin(t * 1.1) + 0.12 * bump(k, 0, 0.6);
  headPivot.rotation.y = 0.1 * idle * Math.sin(t * 0.45) - 0.25 * w;
  return { sq: 0.3 * bump(k, 0.5, 0.75) };
}
""")

# ------------------------------------------------------------------ Ankylosaurus
SPECIES["ankylosaurus"] = dict(
    name="Ankylosaurus", verb="make it swing its club", button="Swing", clay="#D7BE96", accent="#F0DFC0",
    campos="5.2, 4.0, 6.4", camtarget="-0.2, 0.75, 0", blob="5.0, 3.2",
    about="Ankylosaurus magniventris, chibi: a broad, low body with rows of short, keeled bony plates, a wide head with little horns at the back corners and cheeks, and a two-lobed tail club.",
    js=r"""
const body = sculpt(V(-0.1, 0.85, 0), 3.2, 72);
body.ball(-0.3, 0.9, 0.28, 0.55); body.ball(-0.3, 0.9, -0.28, 0.55); body.ball(0.25, 0.88, 0.26, 0.52); body.ball(0.25, 0.88, -0.26, 0.52);
body.ball(0, 0.96, 0, 0.6); body.ball(0, 0.7, 0, 0.5); body.ball(0.7, 0.88, 0, 0.38);
for (const s of [1, -1]) {
  body.capsule([-0.45, 0.6, s * 0.55], [-0.45, 0.22, s * 0.58], 0.22, 0.21, 3);
  body.capsule([0.45, 0.58, s * 0.52], [0.47, 0.21, s * 0.55], 0.2, 0.2, 3);
}
body.update(); squash.add(body);
for (const s of [1, -1]) { nails(squash, -0.45, s * 0.58, 3, 0.06, 0.16); nails(squash, 0.47, s * 0.55, 3, 0.06, 0.16); }
// osteoderms: short keeled domes in rows, spaced apart
const E = { cx: -0.02, cy: 0.9, rx: 0.95, ry: 0.64, rz: 0.88 };
for (const z of [0, 0.3, -0.3, 0.56, -0.56]) for (let x = -0.72; x <= 0.62; x += 0.27) {
  const xx = x + (Math.abs(z) > 0.4 ? 0.13 : 0), q = 1 - ((xx - E.cx) / E.rx) ** 2 - (z / E.rz) ** 2; if (q < 0.08) continue;
  const y = E.cy + E.ry * Math.sqrt(q), n = V((xx - E.cx) / E.rx ** 2, (y - E.cy) / E.ry ** 2, z / E.rz ** 2).normalize();
  const d = new THREE.Mesh(new THREE.SphereGeometry(0.075, 16, 10).scale(1, 0.55, 0.85), accentMat); d.position.set(xx, y - 0.01, z); d.quaternion.setFromUnitVectors(UP, n); d.castShadow = true; squash.add(d);
  cone(squash, V(xx, y + 0.02, z), n, 0.035, 0.07, accentMat, 10);
}
// head: broad, with little horns at the back corners and on the cheeks
const [headPivot, head] = pivot(squash, 0.85, 0.88);
const hs = sculpt(V(1.2, 0.9, 0), 1.9, 64);
hs.ball(1.15, 0.95, 0, 0.42); hs.ball(1.1, 0.92, 0.2, 0.36); hs.ball(1.1, 0.92, -0.2, 0.36); hs.ball(1.45, 0.85, 0, 0.32);
hs.update(); head.add(hs);
ball(head, [1.72, 0.8, 0], 0.13, beakMat, [0.9, 0.85, 1.4]);
for (const s of [1, -1]) {
  cone(head, V(0.95, 1.12, s * 0.38), V(-0.6, 0.35, s * 0.7), 0.08, 0.22, hornMat);
  cone(head, V(1.02, 0.72, s * 0.38), V(-0.4, -0.6, s * 0.6), 0.07, 0.18, hornMat);
}
smile(head, [[1.72, 0.72, 0.18], [1.58, 0.7, 0.28], [1.42, 0.74, 0.36]], 0.014);
for (const s of [1, -1]) addEye(head, [1.33, 1.04, 0.48], 0.11, s);
// tail: stiff, ending in a wide, two-lobed club of bone
const [tailPivot, tail] = pivot(squash, -0.85, 0.85);
const ts = sculpt(V(-1.35, 0.88, 0), 1.9, 56);
ts.capsule([-0.8, 0.86, 0], [-1.75, 0.92, 0], 0.3, 0.12, 8);
ts.update(); tail.add(ts);
for (const s of [1, -1]) ball(tail, [-1.9, 0.92, s * 0.13], 0.17, accentMat, [1.15, 0.8, 1]);
ball(tail, [-2.02, 0.92, 0], 0.13, accentMat, [1, 0.8, 1]);

function move(k, t, idle) {         // the club swung side to side: wind away, whip across, damped settle
  let w = 0;
  if (k >= 0 && k < 0.4) w = 0.55 * ease(k / 0.4);
  else if (k >= 0.4 && k < 0.62) w = 0.55 - 1.4 * ease((k - 0.4) / 0.22);
  else if (k >= 0.62 && k < 1.9) w = -0.85 * Math.exp(-3 * (k - 0.62)) * Math.cos((k - 0.62) * 8);
  tailPivot.rotation.y = w + 0.08 * idle * Math.sin(t * 1.2);
  dino.rotation.y = -0.08 * w;
  headPivot.rotation.z = 0.03 * idle * Math.sin(t * 1.1);
  headPivot.rotation.y = 0.08 * idle * Math.sin(t * 0.45) + 0.2 * w;
  return { sq: 0.3 * bump(k, 0.55, 0.8) };
}
""")

# ------------------------------------------------------------------ Spinosaurus
SPECIES["spinosaurus"] = dict(
    name="Spinosaurus", verb="make it strike at a fish", button="Strike", clay="#E2B394", accent="#F0B96E",
    campos="6.6, 3.2, 7.6", camtarget="0.1, 1.55, 0", blob="5.0, 2.4",
    about="Spinosaurus aegyptiacus, chibi: a scalloped sail over the back, a long, low, crocodile-like snout with conical teeth, an S-curved neck, strong arms with a big thumb claw, short legs and a deep, paddle-like tail.",
    js=r"""
const body = sculpt(V(-0.3, 1.3, 0), 3.8, 76);
body.ball(0, 1.35, 0, 0.52); body.ball(0.4, 1.3, 0, 0.44); body.ball(-0.4, 1.4, 0, 0.5); body.ball(0.05, 1.12, 0, 0.42);
body.capsule([-0.8, 1.45, 0], [-1.85, 1.62, 0], 0.38, 0.1, 9);                          // tail
for (const s of [1, -1]) {
  body.capsule([-0.3, 1.15, s * 0.34], [-0.2, 0.55, s * 0.38], 0.3, 0.2, 4);
  body.capsule([-0.2, 0.55, s * 0.38], [-0.1, 0.22, s * 0.38], 0.17, 0.16, 3);
  body.ball(0.08, 0.15, s * 0.38, 0.17); body.ball(0.26, 0.13, s * 0.38, 0.13);        // flat feet with long toes
}
body.update(); squash.add(body);
for (const s of [1, -1]) nails(squash, 0.22, s * 0.38, 3, 0.055, 0.15, 0.06);
// sail: skin stretched over a row of spines, scalloped between the tips, tallest toward the rear of the back
{
  const tips = [[0.45, 2.1], [0.26, 2.42], [0.04, 2.64], [-0.2, 2.76], [-0.44, 2.72], [-0.64, 2.46], [-0.8, 2.02]];
  const sh = new THREE.Shape(); sh.moveTo(0.62, 1.72); let p = [0.62, 1.72];
  for (const q of tips) { sh.quadraticCurveTo((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 - 0.07, q[0], q[1]); p = q; }
  sh.quadraticCurveTo(-0.84, 1.86, -0.86, 1.74); sh.bezierCurveTo(-0.4, 1.86, 0.2, 1.86, 0.62, 1.72);
  const g = new THREE.ExtrudeGeometry(sh, { depth: 0.08, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.04, bevelSegments: 4, curveSegments: 16 }).translate(0, 0, -0.04);
  const sail = new THREE.Mesh(g, accentMat); sail.castShadow = true; squash.add(sail);
  // a paddle fin along the top and bottom of the tail
  const f = new THREE.Shape(); f.moveTo(-0.85, 1.75); f.quadraticCurveTo(-1.35, 2.02, -1.92, 1.66); f.quadraticCurveTo(-1.4, 1.2, -0.95, 1.18); f.lineTo(-0.85, 1.75);
  const fin = new THREE.Mesh(new THREE.ExtrudeGeometry(f, { depth: 0.05, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 3, curveSegments: 14 }).translate(0, 0, -0.025), clayMat);
  fin.castShadow = true; squash.add(fin);
}
// arms: strong, with a big thumb claw
for (const s of [1, -1]) {
  limb(squash, [0.5, 1.2, s * 0.36], [0.8, 0.95, s * 0.4], 0.1);
  ball(squash, [0.84, 0.92, s * 0.4], 0.1);
  cone(squash, V(0.9, 0.9, s * 0.45), V(0.7, -0.6, s * 0.3), 0.04, 0.17, nailMat);
  cone(squash, V(0.93, 0.9, s * 0.38), V(0.8, -0.6, 0), 0.025, 0.1, nailMat);
}
// S-curved neck carrying the head
const [neckPivot, neck] = pivot(squash, 0.55, 1.55);
const ns = sculpt(V(0.85, 1.85, 0), 1.6, 52);
ns.capsule([0.55, 1.55, 0], [0.8, 2.0, 0], 0.32, 0.26, 4); ns.capsule([0.8, 2.0, 0], [1.1, 2.12, 0], 0.26, 0.25, 3);
ns.update(); neck.add(ns);
const [headPivot, head] = pivot(neck, 1.1, 2.12);
const hs = sculpt(V(1.65, 2.08, 0), 2.2, 72);
hs.ball(1.25, 2.2, 0, 0.36); hs.capsule([1.4, 2.14, 0], [2.05, 2.02, 0], 0.26, 0.17, 7); hs.ball(2.12, 2.0, 0, 0.18);
hs.ball(1.44, 2.42, 0, 0.1);                                                               // small crest before the eyes
hs.update(); head.add(hs);
const [jawPivot, jaw] = pivot(head, 1.2, 2.02);
const js_ = sculpt(V(1.6, 1.94, 0), 1.8, 56);
js_.capsule([1.2, 2.0, 0], [2.05, 1.88, 0], 0.22, 0.12, 7);
js_.update(); jaw.add(js_);
for (let x = 1.55; x <= 2.1; x += 0.11) {                                                // straight conical teeth
  const u = (x - 1.4) / 0.65, cy = 2.14 - 0.12 * u, r = 0.26 - 0.09 * u;
  for (const s of [1, -1]) cone(head, V(x, cy - r * 0.8, s * r * 0.55), V(0, -1, 0), 0.022, 0.08, hornMat, 10);
}
for (const s of [1, -1]) addEye(head, [1.32, 2.33, 0.28], 0.1, s);

function move(k, t, idle) {         // raise the head with the jaws open, lunge down, snap shut, recover
  const pre = ramp(k, 0, 0.3, 0.35, 0.5), strike = ramp(k, 0.35, 0.55, 1.0, 1.5), open = ramp(k, 0, 0.3, 0.55, 0.62);
  neckPivot.rotation.z = 0.15 * pre - 0.5 * strike + 0.03 * idle * Math.sin(t * 1.1);
  headPivot.rotation.z = 0.1 * pre - 0.2 * strike;
  headPivot.rotation.y = 0.08 * idle * Math.sin(t * 0.45) * (1 - strike);
  jawPivot.rotation.z = -0.45 * open;
  return { sq: 0.4 * bump(k, 0, 0.35), fwd: 0.3 * strike };
}
""")

# ------------------------------------------------------------------ Titanosaur
SPECIES["titanosaur"] = dict(
    name="Titanosaur", verb="make it call", button="Call", clay="#AFBDD8", accent="#C7D2E8",
    campos="9.5, 4.8, 11", camtarget="0.1, 1.9, 0", blob="6.4, 3.4",
    about="Patagotitan mayorum, chibi: a deep, round body on pillar legs, a long neck raised at a slant, a small head and a long tapering tail. The front feet have no claws, as in titanosaurs.",
    js=r"""
const body = sculpt(V(-0.1, 1.75, 0), 3.6, 76);
body.ball(0, 1.85, 0, 0.78); body.ball(0.45, 1.8, 0, 0.6); body.ball(-0.5, 1.85, 0, 0.65); body.ball(0, 1.5, 0, 0.6);
for (const s of [1, -1]) {
  body.capsule([-0.5, 1.3, s * 0.5], [-0.5, 0.26, s * 0.52], 0.3, 0.28, 5);
  body.capsule([0.5, 1.3, s * 0.46], [0.52, 0.26, s * 0.48], 0.28, 0.27, 5);
}
body.update(); squash.add(body);
for (const s of [1, -1]) nails(squash, -0.5, s * 0.52, 3, 0.075, 0.24);                // claws on the hind feet only
const [tailPivot, tail] = pivot(squash, -0.9, 1.9);
const ts = sculpt(V(-1.8, 1.65, 0), 2.6, 60);
ts.capsule([-0.85, 1.95, 0], [-2.6, 1.3, 0], 0.42, 0.08, 10);
ts.update(); tail.add(ts);
const [neckPivot, neck] = pivot(squash, 0.75, 2.1);
const ns = sculpt(V(1.15, 2.95, 0), 2.6, 64);
ns.capsule([0.7, 2.1, 0], [1.2, 3.0, 0], 0.42, 0.3, 6); ns.capsule([1.2, 3.0, 0], [1.55, 3.7, 0], 0.3, 0.24, 5);
ns.update(); neck.add(ns);
const [headPivot, head] = pivot(neck, 1.55, 3.75);
const hs = sculpt(V(1.85, 3.88, 0), 1.6, 56);
hs.ball(1.72, 3.92, 0, 0.34); hs.ball(2.02, 3.84, 0, 0.27);
hs.update(); head.add(hs);
smile(head, [[2.26, 3.76, 0.1], [2.12, 3.72, 0.19], [1.96, 3.75, 0.25]], 0.014);
for (const s of [1, -1]) addEye(head, [1.84, 4.02, 0.27], 0.1, s);

function move(k, t, idle) {         // raise the neck, tip the head up and call
  const up = ramp(k, 0.1, 0.6, 1.5, 2.1), pre = bump(k, 0, 0.25);
  neckPivot.rotation.z = 0.2 * up - 0.06 * pre + 0.025 * idle * Math.sin(t * 0.9);
  headPivot.rotation.z = 0.35 * up * (1 + 0.1 * Math.sin(k * 14) * (k > 0.6 && k < 1.5)) + 0.04 * idle * Math.sin(t * 1.3);
  headPivot.rotation.y = 0.1 * idle * Math.sin(t * 0.45) * (1 - up);
  tailPivot.rotation.y = 0.12 * idle * Math.sin(t * 0.8);
  tailPivot.rotation.z = 0.08 * up;
  return { sq: 0.35 * pre };
}
""")


def page(slug):
    s = SPECIES[slug]
    t = TOP
    for k, v in [("__NAME__", s["name"]), ("__VERB__", s["verb"]), ("__BUTTON__", s["button"]), ("__ABOUT__", s["about"]),
                 ("__CLAY__", s["clay"]), ("__ACCENT__", s["accent"]), ("__CAMPOS__", s["campos"]), ("__CAMTARGET__", s["camtarget"]), ("__BLOB__", s["blob"])]:
        t = t.replace(k, v)
    assert "__" not in t.replace("__dbg", ""), slug
    return t + "\n" + HELPERS + "\n" + s["js"] + MOTION


if __name__ == "__main__":
    for slug in SPECIES:
        pathlib.Path(ROOT, "3d", f"{slug}-chibi.html").write_text(page(slug))
    print("ok", ", ".join(SPECIES))

import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Generate triceratops-3d.html from the T. rex 3D engine: same renderer, shaders, paint, merge and loading code;
new animal build, scenery and motion."""
import pathlib, re, sys
sys.path.insert(0, HERE)
import sp_triceratops as T

src = pathlib.Path(ROOT + "/3d/trex-3d.html").read_text()
lines = src.split("\n")
def find(prefix):
    return next(i for i, l in enumerate(lines) if l.startswith(prefix))
a_animal = find("// ---------------------------------------------------------------- the animal")
a_paint = find("// ---------------------------------------------------------------- paint")
a_merge_calls = find("legGroups.forEach(g => mergeSkin(g));")
a_scenery = find("// ---------------------------------------------------------------- scenery")
a_motion = find("// ---------------------------------------------------------------- motion")
head_part = "\n".join(lines[:a_animal])
paint_part = "\n".join(lines[a_paint:a_merge_calls])

# ---- header / palette / UI text
head_part = (head_part
    .replace("<title>T. rex 3D model</title>", "<title>Triceratops 3D model</title>")
    .replace("background: #C9D6DA;", "background: #CBD9D0;")
    .replace("Interactive 3D model of a Tyrannosaurus rex. Drag to orbit, scroll or pinch to zoom, click the dinosaur to make it roar.",
             "Interactive 3D model of a Triceratops. Drag to orbit, scroll or pinch to zoom, click the dinosaur to make it charge.")
    .replace("<h1>T. rex</h1>", "<h1>Triceratops</h1>")
    .replace("and click the dinosaur to make it roar.", "and click the dinosaur to make it charge.")
    .replace('<button type="button" id="roar">Roar</button>', '<button type="button" id="roar">Charge</button>'))
head_part = re.sub(r"const C = \{.*?\};", """const C = {
  skin: new THREE.Color('#7A8450'), belly: new THREE.Color('#DCCFA6'), outline: '#2A1C22',
  frill: '#C27A48', horn: '#E6D9BC', beak: '#4A3A30', claw: '#3A2A2C', eye: '#E0B04A',
  sky: '#CBD9D0', ground: '#9AA864', hill: '#A9B596', hill2: '#93A27A', river: '#9DBFC6'
};""", head_part, flags=re.S)
head_part = head_part.replace("const HOME = { pos: new THREE.Vector3(3.5, 4.2, 19), target: new THREE.Vector3(-0.4, 2.7, 0) };",
                              "const HOME = { pos: new THREE.Vector3(3.4, 3.1, 16), target: new THREE.Vector3(0, 1.6, 0) };")
head_part = head_part.replace("controls.minDistance = 7; controls.maxDistance = 40;", "controls.minDistance = 5; controls.maxDistance = 32;")
head_part = head_part.replace("Object.assign(sun.shadow.camera, { left: -9, right: 9, top: 7, bottom: -4, near: 4, far: 30 });",
                              "Object.assign(sun.shadow.camera, { left: -8, right: 8, top: 6, bottom: -3, near: 4, far: 30 });")
assert "Triceratops" in head_part and "#7A8450" in head_part

ANIMAL = r"""// ---------------------------------------------------------------- the animal
const rex = new THREE.Group(); scene.add(rex);                    // whole animal (lunges on the charge)
const hips = new THREE.Group(); hips.position.set(0, 2.5, 0); rex.add(hips);   // long, columnar hind legs
const trunk = new THREE.Group(); hips.add(trunk);                 // breathes

// barrel body
const hipMass = mesh(ellipsoid(1.5, 1.3, 0.95), skinMat, { stripes: true }); hipMass.position.set(-0.55, 0.16, 0); trunk.add(hipMass);   // back highest over the hips
const belly = mesh(ellipsoid(2.3, 1.22, 1.06), skinMat, { stripes: true }); belly.position.set(0.45, -0.2, 0); trunk.add(belly);
const chest = mesh(ellipsoid(1.15, 1.02, 0.94), skinMat, { stripes: true }); chest.position.set(1.85, -0.44, 0); chest.rotation.z = 0.2; trunk.add(chest);
const neck = mesh(ellipsoid(0.8, 0.8, 0.74), skinMat, { stripes: true }); neck.position.set(2.5, -0.42, 0); trunk.add(neck);

// head: skull, jaw and beak extruded from the same outlines as the 2D drawing
const headPivot = new THREE.Group(); headPivot.position.set(2.5, -0.16, 0); trunk.add(headPivot);   // head carried low
const head = new THREE.Group(); headPivot.add(head);
const HS = { s: 0.0094, ox: 700, oy: 300, x0: 0, x1: 2.5 };
const SKULL = '__SKULL__', JAWP = '__JAW__', BEAK = '__BEAK__', LBEAK = '__LBEAK__';
const toothMat = toon(C.horn), clawMat = toon(C.claw), hornMat = toon(C.horn), beakMat = toon(C.beak), frillMat = toon(C.frill);
head.add(mesh(profile(SKULL, 1.05, 0.55, HS), skinMat, { kind: 'head' }));
head.add(mesh(profile(JAWP, 0.84, 0.55, HS), skinMat, { kind: 'head' }));
head.add(mesh(profile(BEAK, 0.34, 0.3, HS), beakMat, {}));
head.add(mesh(profile(LBEAK, 0.3, 0.3, HS), beakMat, {}));
const headX = x => (x - HS.ox) * HS.s, headY = y => -(y - HS.oy) * HS.s;
const halfW = (X, depth) => (depth / 2) * (1 - 0.55 * Math.min(Math.max(X / 2.5, 0), 1) ** 2) + 0.08;

function batcher(mat) {
  const parts = [];
  return { add(m) { m.updateMatrix(); parts.push(m.geometry.clone().applyMatrix4(m.matrix)); },
           flush(parent, opts) { if (parts.length) { const m = mesh(mergeGeometries(parts), mat, opts || { outline: false, shadow: false }); parent.add(m); return m; } } };
}
// a cone pointing from `base` along `dir`
function cone(base, dir, r, len, mat, opts) {
  const g = new THREE.ConeGeometry(r, len, 14).translate(0, len / 2, 0);
  const m = mesh(g, mat, opts || {}); m.position.copy(base); m.quaternion.setFromUnitVectors(UP, dir.clone().normalize()); return m;
}

// frill: a broad, slightly cupped shield tilted back, with a skin-coloured rim and bumps
const frillG = new THREE.CylinderGeometry(1.0, 1.0, 0.09, 48, 1).rotateZ(Math.PI / 2).scale(1, 0.95, 1.12);
{ const p = frillG.attributes.position; for (let k = 0; k < p.count; k++) { const y = p.getY(k), z = p.getZ(k); p.setX(k, p.getX(k) + 0.12 * y * y + 0.62 * z * z); } frillG.computeVertexNormals(); }
const frill = new THREE.Group(); frill.position.set(-0.06, 0.34, 0); frill.rotation.z = 1.05; frill.scale.setScalar(1.02); head.add(frill);   // swept back over the neck
frill.add(mesh(frillG, frillMat, {}));
const rimG = new THREE.TorusGeometry(1.0, 0.07, 10, 64).rotateY(Math.PI / 2).scale(1, 0.95, 1.12);
{ const p = rimG.attributes.position; for (let k = 0; k < p.count; k++) { const y = p.getY(k), z = p.getZ(k); p.setX(k, p.getX(k) + 0.12 * y * y + 0.62 * z * z); } rimG.computeVertexNormals(); }
frill.add(mesh(rimG, skinMat, { kind: 'head' }));
const bumps = batcher(skinMat);
for (let k = 0; k < 22; k++) {                                       // adult edge bones: low and worn down
  const a = (k / 22) * Math.PI * 2; if (Math.sin(a) < -0.55) continue;     // none where the frill meets the neck
  const y = Math.sin(a) * 0.95 * 1.04, z = Math.cos(a) * 1.12 * 1.04, x = 0.12 * y * y + 0.62 * z * z;
  const b = new THREE.Mesh(new THREE.ConeGeometry(0.08, 0.08, 8).translate(0, 0.04, 0), skinMat);
  b.position.set(x, y, z); b.quaternion.setFromUnitVectors(UP, new THREE.Vector3(0, Math.sin(a), Math.cos(a))); bumps.add(b);
}
bumps.flush(frill, { kind: 'head' });

// horns, eyes, cheek points
const BROW = new THREE.Vector3(0.62, 0.42, 0);
for (const side of [1, -1]) {
  head.add(cone(new THREE.Vector3(headX(824), headY(292), side * 0.26), new THREE.Vector3(0.66, 0.74, side * 0.08), 0.13, 1.35, hornMat));   // brow horns about a metre, angled forward
  const ex = headX(818), ey = headY(316), ez = side * (halfW(ex, 1.05) - 0.03);
  const eye = new THREE.Group(); eye.position.set(ex, ey, ez); head.add(eye); eye.userData.isEye = true;
  eye.add(new THREE.Mesh(new THREE.SphereGeometry(0.075, 14, 10), toon(C.eye)));
  const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.033, 10, 8), toon('#15110D')); pupil.position.z = side * 0.04; eye.add(pupil);
  const brow = mesh(ellipsoid(0.18, 0.06, 0.08, 14, 8), skinMat, { kind: 'head', shadow: false }); brow.position.set(ex + 0.01, ey + 0.08, ez * 0.95); head.add(brow);
  head.add(cone(new THREE.Vector3(headX(772), headY(392), side * 0.44), new THREE.Vector3(-0.3, -0.8, side * 0.5), 0.08, 0.26, skinMat, { kind: 'head' }));
}
head.add(cone(new THREE.Vector3(headX(886), headY(300), 0), new THREE.Vector3(0.35, 1, 0), 0.1, 0.38, hornMat));
const eyes = []; head.traverse(o => { if (o.userData.isEye) eyes.push(o); });

// legs: thick hind pillars, shorter front legs; hoof-like nails
const legGroups = [];
function hoofs(g, at, side) {
  const nails = batcher(clawMat);
  for (const dz of [-0.16, 0, 0.16]) { const n = new THREE.Mesh(new THREE.SphereGeometry(0.09, 10, 8).scale(1.1, 0.7, 0.9), clawMat); n.position.set(at.x + 0.3, at.y - 0.06, dz); nails.add(n); }
  nails.flush(g);
}
function hindLeg(side, dx) {
  const g = new THREE.Group(); legGroups.push(g); g.position.set(dx, 0, side * 0.72); hips.add(g);
  const P = (x, y) => new THREE.Vector3(x, y, 0);
  const thigh = mesh(ellipsoid(0.66, 1.0, 0.52), skinMat, { kind: 'leg' }); thigh.position.set(-0.5, -0.8, 0); thigh.rotation.z = -0.1; g.add(thigh);
  const knee = P(-0.4, -1.56), ankle = P(-0.5, -2.24), foot = P(-0.42, -2.36);
  g.add(limb(knee, ankle, 0.34, 0.27, { kind: 'leg' }), ball(knee, 0.34, { kind: 'leg' }));
  const f = mesh(ellipsoid(0.42, 0.13, 0.34, 20, 12), skinMat, { kind: 'leg' }); f.position.copy(foot); g.add(f);
  hoofs(g, foot, side);
}
function frontLeg(side, dx) {
  const g = new THREE.Group(); legGroups.push(g); g.position.set(dx, 0, side * 0.74); hips.add(g);
  const P = (x, y, z = 0) => new THREE.Vector3(x, y, z);
  const shoulder = P(1.95, -0.6), elbow = P(1.74, -1.42, side * 0.16), wrist = P(1.92, -2.22, side * 0.06), foot = P(1.98, -2.36);   // elbows flexed back and slightly out
  const upper = mesh(ellipsoid(0.42, 0.62, 0.4), skinMat, { kind: 'leg' }); upper.position.set(1.88, -0.96, side * 0.06); upper.rotation.z = 0.2; g.add(upper);
  g.add(limb(elbow, wrist, 0.25, 0.2, { kind: 'leg' }), ball(elbow, 0.26, { kind: 'leg' }));
  const f = mesh(ellipsoid(0.36, 0.12, 0.3, 20, 12), skinMat, { kind: 'leg' }); f.position.copy(foot); g.add(f);
  hoofs(g, foot, side);
}
hindLeg(1, 0.1); hindLeg(-1, -0.3); frontLeg(1, 0.05); frontLeg(-1, -0.25);

// tail: one continuous tapered mesh, bent each frame along a swaying centreline
const TL = 2.6, RINGS = 48, RAD = 24;                                // a fairly short, thick tail, as in other big horned dinosaurs
const tailR = u => 0.62 * Math.pow(1 - u, 0.85) + 0.07;
const tailGeo = new THREE.BufferGeometry();
const tPos = [], tOff = [], tRing = [], tIdx = [];
for (let i = 0; i <= RINGS; i++) {
  const u = i / RINGS, r = tailR(u);
  for (let k = 0; k < RAD; k++) {
    const a = (k / RAD) * Math.PI * 2, oy = Math.cos(a) * r * 1.1, oz = Math.sin(a) * r * 0.85;
    tPos.push(-u * TL, oy, oz); tOff.push(0, oy, oz); tRing.push(i);
  }
}
const tipIndex = tPos.length / 3; tPos.push(-TL - 0.05, 0, 0); tOff.push(0, 0, 0); tRing.push(RINGS + 1);
for (let i = 0; i < RINGS; i++) for (let k = 0; k < RAD; k++) {
  const a = i * RAD + k, b = i * RAD + (k + 1) % RAD, c = a + RAD, d = b + RAD;
  tIdx.push(a, c, b, b, c, d);
}
for (let k = 0; k < RAD; k++) tIdx.push(RINGS * RAD + k, tipIndex, RINGS * RAD + (k + 1) % RAD);
tailGeo.setIndex(tIdx);
tailGeo.setAttribute('position', new THREE.Float32BufferAttribute(tPos, 3));
tailGeo.computeVertexNormals();
const tailRestN = tailGeo.attributes.normal.array.slice();
const tail = mesh(tailGeo, skinMat, { stripes: true, kind: 'tail' });
tail.position.set(-1.3, -0.12, 0); tail.frustumCulled = false; tail.children[0].frustumCulled = false; trunk.add(tail);
const ringM = Array.from({ length: RINGS + 2 }, () => new THREE.Matrix4()), ringC = Array.from({ length: RINGS + 2 }, () => new THREE.Vector3());
const mz = new THREE.Matrix4(), my = new THREE.Matrix4(), tv = new THREE.Vector3(), tn = new THREE.Vector3();
const tailC = new THREE.Vector3();
function bendTail(t) {
  const step = TL / RINGS; const c = tailC.set(0, 0, 0);
  for (let i = 0; i <= RINGS + 1; i++) {
    const u = Math.min(i / RINGS, 1);
    const pitch = 0.05 + 0.12 * u * u + (reduceMotion ? 0 : 0.03 * Math.sin(t * 0.9 - u * 2.5) * u);
    const yaw = reduceMotion ? 0 : 0.26 * Math.sin(t * 1.1 - u * 2.6) * u * u;
    ringM[i].multiplyMatrices(my.makeRotationY(yaw), mz.makeRotationZ(pitch));
    ringC[i].copy(c);
    if (i <= RINGS) c.add(tv.set(-step, 0, 0).applyMatrix4(ringM[i]));
  }
  const P = tailGeo.attributes.position.array, N = tailGeo.attributes.normal.array;
  for (let v = 0; v < tRing.length; v++) {
    const i = tRing[v];
    if (i > RINGS) { tv.set(-0.05, 0, 0).applyMatrix4(ringM[RINGS]).add(ringC[RINGS + 1]); }
    else tv.set(tOff[v * 3], tOff[v * 3 + 1], tOff[v * 3 + 2]).applyMatrix4(ringM[i]).add(ringC[i]);
    P[v * 3] = tv.x; P[v * 3 + 1] = tv.y; P[v * 3 + 2] = tv.z;
    tn.set(tailRestN[v * 3], tailRestN[v * 3 + 1], tailRestN[v * 3 + 2]).applyMatrix4(ringM[Math.min(i, RINGS)]);
    N[v * 3] = tn.x; N[v * 3 + 1] = tn.y; N[v * 3 + 2] = tn.z;
  }
  tailGeo.attributes.position.needsUpdate = true; tailGeo.attributes.normal.needsUpdate = true;
}
bendTail(0);
"""
ANIMAL = (ANIMAL.replace("__SKULL__", T.SKULL_D).replace("__JAW__", T.JAW_D)
                .replace("__BEAK__", T.BEAK_D).replace("__LBEAK__", T.LBEAK_D))

MERGE_CALLS = """legGroups.forEach(g => mergeSkin(g));
mergeSkin(trunk, [tail]);
mergeSkin(head);
"""

SCENERY = """// ---------------------------------------------------------------- scenery: Hell Creek floodplain
const ground = new THREE.Mesh(new THREE.CircleGeometry(70, 64).rotateX(-Math.PI / 2), toon(C.ground)); ground.receiveShadow = true; scene.add(ground);
for (const [r, w, h, c] of [[11, 1.2, 0.04, '#8C9A58'], [15, 1.6, 0.03, '#A7B26E'], [20, 1.4, 0.02, '#7F8D4E']]) {
  const ring = new THREE.Mesh(new THREE.RingGeometry(r, r + w, 64).rotateX(-Math.PI / 2), toon(c)); ring.position.y = h; ring.receiveShadow = true; scene.add(ring);
}
const river = new THREE.Mesh(new THREE.PlaneGeometry(140, 3.2).rotateX(-Math.PI / 2), toon(C.river)); river.position.set(0, 0.05, -24); scene.add(river);
for (const [x, z, rx, ry, c] of [[-34, -46, 22, 6, C.hill], [4, -54, 26, 8, C.hill], [36, -44, 18, 5, C.hill], [-14, -38, 14, 4, C.hill2], [22, -36, 12, 3.5, C.hill2]]) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2).scale(rx, ry, 8), toon(c)); m.position.set(x, 0, z); scene.add(m);
}
"""

MOTION = r"""// ---------------------------------------------------------------- motion
const clock = new THREE.Clock();
let roarStart = -10, nextBlink = 2.5;
const ease = t => t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2;
const backOut = t => { const c = 1.9; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2; };
function chargeCurve(t) {          // lunge in metres, dip 0..1 (negative = lift before the charge)
  if (t < 0 || t > 1.6) return { lunge: 0, dip: 0 };
  if (t < 0.28) { const u = ease(t / 0.28); return { lunge: -0.25 * u, dip: -0.5 * u }; }
  if (t < 0.68) { const u = backOut((t - 0.28) / 0.4); return { lunge: -0.25 + 0.85 * u, dip: -0.5 + 1.5 * u }; }
  if (t < 1.1) return { lunge: 0.6, dip: 1 - 0.04 * Math.abs(Math.sin((t - 0.68) * 30)) };
  const u = ease((t - 1.1) / 0.5); return { lunge: 0.6 * (1 - u), dip: 1 - u };
}
function roar() { roarStart = clock.getElapsedTime(); }
document.getElementById('roar').addEventListener('click', roar);
document.getElementById('reset').addEventListener('click', () => { camera.position.copy(HOME.pos); controls.target.copy(HOME.target); controls.update(); });

const ray = new THREE.Raycaster(), ptr = new THREE.Vector2(); let down = null;
canvas.addEventListener('pointerdown', e => { down = { x: e.clientX, y: e.clientY }; });
canvas.addEventListener('pointerup', e => {
  if (!down || Math.hypot(e.clientX - down.x, e.clientY - down.y) > 6) return;
  const r = canvas.getBoundingClientRect();
  ptr.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ptr, camera);
  if (ray.intersectObject(rex, true).length) roar();
});

function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  renderer.setSize(w, h, false); camera.aspect = w / h;
  camera.position.z = HOME.pos.z * Math.max(1, 1.35 / (w / h)); // keep the whole animal in frame on tall screens
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize); resize();

const headBase = headPivot.rotation.z;
let frame = 0, acc = 0, lastNow = performance.now();
function adapt() {                       // keep frames near 60 fps by trading resolution
  const now = performance.now(), dt = now - lastNow; lastNow = now; acc += dt;
  if (++frame % 60) return;
  const avg = acc / 60; acc = 0;
  const next = avg > 22 ? Math.max(0.75, pixelRatio - 0.25) : avg < 14 ? Math.min(MAX_PR, pixelRatio + 0.25) : pixelRatio;
  if (next !== pixelRatio) { pixelRatio = next; renderer.setPixelRatio(pixelRatio); resize(); }
}
function loop() {
  if (document.hidden) return;
  adapt();
  renderer.shadowMap.needsUpdate = frame % 2 === 0;
  const t = clock.getElapsedTime();
  if (!reduceMotion) {
    trunk.scale.set(1, 1 + 0.012 * Math.sin(t * 2.0), 1 + 0.008 * Math.sin(t * 2.0));
    bendTail(t);
    headPivot.rotation.y = 0.06 * Math.sin(t * 0.35);
    if (t > nextBlink) { const k = t - nextBlink; const s = k < 0.07 ? 1 - k / 0.07 : k < 0.16 ? (k - 0.07) / 0.09 : 1; eyes.forEach(e => e.scale.y = Math.max(0.08, s)); if (k > 0.16) nextBlink = t + 3 + Math.random() * 3; }
  }
  const { lunge, dip } = chargeCurve(t - roarStart);
  rex.position.x = lunge;
  headPivot.rotation.z = headBase - 0.22 * dip;
  controls.update();
  renderer.render(scene, camera);
}
// compile every shader before the first frame, off the main thread where the browser supports it
function start() { renderer.setAnimationLoop(loop); document.getElementById('status').remove(); }
renderer.shadowMap.needsUpdate = true;
(renderer.compileAsync ? renderer.compileAsync(scene, camera) : Promise.resolve()).catch(() => {}).then(start);
</script>
</body>
</html>
"""

merge_def = "\n".join(lines[a_merge_calls - 10:a_merge_calls])   # mergeSkin() definition lines live just before the calls
assert "function mergeSkin" in paint_part or "function mergeSkin" in merge_def
out = head_part + "\n" + ANIMAL + "\n" + paint_part + "\n" + MERGE_CALLS + "\n" + SCENERY + "\n" + MOTION
pathlib.Path(ROOT + "/3d/triceratops-3d.html").write_text(out)
print("ok", len(out))

import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Generate ankylosaurus-3d.html from the T. rex 3D engine (renderer, shaders, paint, merge and loading code), with the
Hell Creek ground and page motion of the Triceratops page, a new animal build and a tail-club swing.
Anatomy as in sp_ankylosaurus.py (Arbour and Mallon 2017): broad, low body with short, keeled osteoderms in rows,
two half-rings over the neck, a broad head with pyramid-shaped horns at the back corners and cheeks, and a stiff tail
ending in a wide, flat club (AMNH 5214: about 60 cm long, 49 cm wide, 19 cm tall). About 7 m long."""
import pathlib, re

src = pathlib.Path(ROOT + "/3d/trex-3d.html").read_text()
lines = src.split("\n")
def find(prefix):
    return next(i for i, l in enumerate(lines) if l.startswith(prefix))
a_animal = find("// ---------------------------------------------------------------- the animal")
a_paint = find("// ---------------------------------------------------------------- paint")
a_merge_calls = find("legGroups.forEach(g => mergeSkin(g));")
head_part = "\n".join(lines[:a_animal])
paint_part = "\n".join(lines[a_paint:a_merge_calls])

tri = pathlib.Path(HERE + "/triceratops_3d.py").read_text()
SCENERY = re.search(r'SCENERY = """(.*?)"""', tri, re.S).group(1)
MOTION = re.search(r'MOTION = r"""(.*?)"""', tri, re.S).group(1)

# ---- header / palette / UI text
head_part = (head_part
    .replace("<title>T. rex 3D model</title>", "<title>Ankylosaurus 3D model</title>")
    .replace("background: #C9D6DA;", "background: #D9D3C2;")
    .replace("Interactive 3D model of a Tyrannosaurus rex. Drag to orbit, scroll or pinch to zoom, click the dinosaur to make it roar.",
             "Interactive 3D model of an Ankylosaurus. Drag to orbit, scroll or pinch to zoom, click the dinosaur to make it swing its tail club.")
    .replace("<h1>T. rex</h1>", "<h1>Ankylosaurus</h1>")
    .replace("and click the dinosaur to make it roar.", "and click the dinosaur to make it swing its tail club.")
    .replace('<button type="button" id="roar">Roar</button>', '<button type="button" id="roar">Swing</button>'))
head_part = re.sub(r"const C = \{.*?\};", """const C = {
  skin: new THREE.Color('#8C6F48'), belly: new THREE.Color('#DED0AA'), outline: '#2A1C22',
  bone: '#BFA674', beak: '#4A3A30', claw: '#3A2A2C', eye: '#E0B04A',
  sky: '#D9D3C2', ground: '#A69A62', hill: '#A9A57E', hill2: '#93884F', river: '#9FB2AE'
};""", head_part, flags=re.S)
head_part = head_part.replace("const HOME = { pos: new THREE.Vector3(3.5, 4.2, 19), target: new THREE.Vector3(-0.4, 2.7, 0) };",
                              "const HOME = { pos: new THREE.Vector3(4.5, 5.2, 11.5), target: new THREE.Vector3(-0.3, 0.8, 0) };")   # looks down a little, so the sideways club swing reads
head_part = head_part.replace("controls.minDistance = 7; controls.maxDistance = 40;", "controls.minDistance = 4; controls.maxDistance = 28;")
head_part = head_part.replace("Object.assign(sun.shadow.camera, { left: -9, right: 9, top: 7, bottom: -4, near: 4, far: 30 });",
                              "Object.assign(sun.shadow.camera, { left: -7, right: 7, top: 5, bottom: -3, near: 4, far: 30 });")
assert "Ankylosaurus" in head_part and "#8C6F48" in head_part

ANIMAL = r"""// ---------------------------------------------------------------- the animal
const rex = new THREE.Group(); scene.add(rex);                    // whole animal (braces on the swing)
const hips = new THREE.Group(); hips.position.set(0, 1.55, 0); rex.add(hips);
const trunk = new THREE.Group(); hips.add(trunk);                 // breathes
const boneMat = toon(C.bone), clawMat = toon(C.claw), beakMat = toon(C.beak);

function batcher(mat) {
  const parts = [];
  return { add(m) { m.updateMatrix(); parts.push(m.geometry.clone().applyMatrix4(m.matrix)); },
           flush(parent, opts) { if (parts.length) { const m = mesh(mergeGeometries(parts), mat, opts || { outline: false, shadow: false }); parent.add(m); return m; } } };
}
function cone(base, dir, r, len, mat, opts) {
  const g = new THREE.ConeGeometry(r, len, 14).translate(0, len / 2, 0);
  const m = mesh(g, mat, opts || {}); m.position.copy(base); m.quaternion.setFromUnitVectors(UP, dir.clone().normalize()); return m;
}
// a short, keeled osteoderm lying on a surface with normal n
function osteoderm(b, p, n, size) {
  const plate = new THREE.Mesh(new THREE.SphereGeometry(1, 14, 8).scale(size, size * 0.38, size * 0.8), boneMat);
  plate.position.copy(p); plate.quaternion.setFromUnitVectors(UP, n); b.add(plate);
  const keel = new THREE.Mesh(new THREE.ConeGeometry(size * 0.35, size * 0.5, 8).translate(0, size * 0.25, 0), boneMat);
  keel.position.copy(p).addScaledVector(n, size * 0.2); keel.quaternion.setFromUnitVectors(UP, n); b.add(keel);
}
// point and normal on an ellipsoid (centre c, radii a b z) at long-axis position s (-1..1) and angle al from the top
function onEllipsoid(c, a, bb, z, s, al) {
  const k = Math.sqrt(Math.max(0, 1 - s * s));
  const p = new THREE.Vector3(c.x + a * s, c.y + bb * k * Math.cos(al), c.z + z * k * Math.sin(al));
  const n = new THREE.Vector3(s / a, k * Math.cos(al) / bb, k * Math.sin(al) / z).normalize();
  return [p, n];
}

// broad, low body
const BODY = { c: new THREE.Vector3(0.25, 0.05, 0), a: 2.1, b: 0.82, z: 1.3 };
const body = mesh(ellipsoid(BODY.a, BODY.b, BODY.z), skinMat, { stripes: true }); body.position.copy(BODY.c); trunk.add(body);
const hipMass = mesh(ellipsoid(1.1, 0.78, 1.2), skinMat, { stripes: true }); hipMass.position.set(-1.05, 0.02, 0); trunk.add(hipMass);
const chest = mesh(ellipsoid(0.9, 0.72, 1.05), skinMat, { stripes: true }); chest.position.set(1.65, -0.1, 0); trunk.add(chest);
// armour: rows of short, keeled osteoderms, spaced apart
const armour = batcher(boneMat);
for (const [al, n, size] of [[0, 8, 0.13], [0.42, 8, 0.12], [-0.42, 8, 0.12], [0.85, 7, 0.11], [-0.85, 7, 0.11], [1.25, 6, 0.09], [-1.25, 6, 0.09]]) {
  for (let i = 0; i < n; i++) {
    const s = -0.78 + 1.56 * (i + (Math.abs(al) > 0.6 ? 0.5 : 0)) / n;
    const [p, nn] = onEllipsoid(BODY.c, BODY.a, BODY.b, BODY.z, s, al); osteoderm(armour, p, nn, size);
  }
}
armour.flush(trunk, { outline: true, shadow: true });

// neck with two half-rings of keeled osteoderms
const neckJoint = new THREE.Group(); neckJoint.position.set(2.15, -0.05, 0); trunk.add(neckJoint);
const neck = mesh(ellipsoid(0.6, 0.52, 0.66), skinMat, { stripes: true }); neck.position.set(0.12, 0, 0); neckJoint.add(neck);
const rings = batcher(boneMat);
for (const x of [-0.12, 0.26]) for (const al of [-1.15, -0.58, 0, 0.58, 1.15]) {
  const [p, nn] = onEllipsoid(new THREE.Vector3(0.12, 0, 0), 0.6, 0.52, 0.66, x / 0.6, al); osteoderm(rings, p, nn, 0.1);
}
rings.flush(neckJoint, { outline: true, shadow: true });

// head: broad and low, wider than long, with pyramid-shaped horns at the back corners and cheeks
const headPivot = new THREE.Group(); headPivot.position.set(0.55, 0.02, 0); neckJoint.add(headPivot);
const head = new THREE.Group(); headPivot.add(head);
const skull = mesh(ellipsoid(0.52, 0.32, 0.52), skinMat, { kind: 'head' }); skull.position.set(0.32, 0.02, 0); head.add(skull);
const snout = mesh(ellipsoid(0.36, 0.25, 0.38), skinMat, { kind: 'head' }); snout.position.set(0.66, -0.04, 0); head.add(snout);
const beak = mesh(ellipsoid(0.13, 0.17, 0.3), beakMat, {}); beak.position.set(0.95, -0.1, 0); head.add(beak);
const tiles = batcher(boneMat);
for (const [x, z] of [[0.12, 0.2], [0.12, -0.2], [0.36, 0.26], [0.36, -0.26], [0.34, 0], [0.56, 0.14], [0.56, -0.14]]) {
  const t = new THREE.Mesh(new THREE.SphereGeometry(1, 10, 6).scale(0.1, 0.03, 0.09), boneMat); t.position.set(x, 0.32, z); tiles.add(t);
}
tiles.flush(head, { outline: true, shadow: false });
const eyes = [];
for (const side of [1, -1]) {
  head.add(cone(new THREE.Vector3(0.0, 0.18, side * 0.42), new THREE.Vector3(-0.7, 0.3, side * 0.6), 0.11, 0.3, boneMat));   // squamosal horn
  head.add(cone(new THREE.Vector3(0.14, -0.2, side * 0.44), new THREE.Vector3(-0.5, -0.75, side * 0.4), 0.09, 0.24, boneMat)); // jugal horn
  const nostril = new THREE.Mesh(new THREE.SphereGeometry(0.045, 10, 8).scale(1.4, 0.8, 0.6), toon('#1E1416')); nostril.position.set(0.86, -0.03, side * 0.27); head.add(nostril);
  const eye = new THREE.Group(); eye.position.set(0.46, 0.1, side * 0.4); head.add(eye); eyes.push(eye);
  eye.add(new THREE.Mesh(new THREE.SphereGeometry(0.06, 14, 10), toon(C.eye)));
  const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.028, 10, 8), toon('#15110D')); pupil.position.z = side * 0.034; eye.add(pupil);
  const brow = mesh(ellipsoid(0.13, 0.05, 0.07, 14, 8), boneMat, { shadow: false }); brow.position.set(0.47, 0.17, side * 0.39); head.add(brow);
}

// legs: short and sturdy; hind legs longer than forelegs
const legGroups = [];
function leg(x, side, front) {
  const g = new THREE.Group(); legGroups.push(g); g.position.set(x, 0, side * 0.95); hips.add(g);
  const P = (px, py, pz = 0) => new THREE.Vector3(px, py, pz);
  const top = front ? P(0, -0.3) : P(0, -0.15), knee = front ? P(-0.06, -0.95, side * 0.08) : P(0.08, -0.9), ankle = P(0.02, -1.42);
  const upper = mesh(ellipsoid(front ? 0.36 : 0.46, front ? 0.5 : 0.62, 0.38), skinMat, { kind: 'leg' }); upper.position.set(0, front ? -0.55 : -0.45, 0); g.add(upper);
  g.add(limb(top, knee, front ? 0.28 : 0.33, 0.24, { kind: 'leg' }), ball(knee, 0.24, { kind: 'leg' }), limb(knee, ankle, 0.24, 0.2, { kind: 'leg' }));
  const f = mesh(ellipsoid(0.3, 0.1, 0.26, 20, 12), skinMat, { kind: 'leg' }); f.position.set(0.08, -1.5, 0); g.add(f);
  const nails = batcher(clawMat);
  for (const dz of [-0.14, 0, 0.14]) { const n = new THREE.Mesh(new THREE.SphereGeometry(0.075, 10, 8).scale(1.1, 0.7, 0.9), clawMat); n.position.set(0.34, -1.54, dz); nails.add(n); }
  nails.flush(g);
}
leg(-1.0, 1, false); leg(-1.2, -1, false); leg(1.6, 1, true); leg(1.4, -1, true);

// tail: broad at the base, stiff toward the end, and finished with a wide, flat club
const TL = 3.0, RINGS = 40, RAD = 22;
const tailR = u => 0.55 * Math.pow(1 - u, 0.9) + 0.09;
const tailGeo = new THREE.BufferGeometry();
const tPos = [], tOff = [], tRing = [], tIdx = [];
for (let i = 0; i <= RINGS; i++) {
  const u = i / RINGS, r = tailR(u);
  for (let k = 0; k < RAD; k++) {
    const a = (k / RAD) * Math.PI * 2, oy = Math.cos(a) * r * 0.8, oz = Math.sin(a) * r * 1.05;
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
tail.position.set(-1.95, -0.05, 0); tail.frustumCulled = false; tail.children[0].frustumCulled = false; trunk.add(tail);
const club = new THREE.Group(); trunk.add(club);
club.add(mesh(ellipsoid(0.34, 0.13, 0.27, 28, 16), boneMat, {}));
for (const side of [1, -1]) { const lobe = mesh(ellipsoid(0.2, 0.12, 0.13, 20, 12), boneMat, {}); lobe.position.set(0.02, 0, side * 0.15); club.add(lobe); }
const ringM = Array.from({ length: RINGS + 2 }, () => new THREE.Matrix4()), ringC = Array.from({ length: RINGS + 2 }, () => new THREE.Vector3());
const mz = new THREE.Matrix4(), my = new THREE.Matrix4(), tv = new THREE.Vector3(), tn = new THREE.Vector3(), clubQ = new THREE.Quaternion();
const tailC = new THREE.Vector3();
function bendTail(t, swing = 0) {
  const step = TL / RINGS; const c = tailC.set(0, 0, 0);
  for (let i = 0; i <= RINGS + 1; i++) {
    const u = Math.min(i / RINGS, 1);
    const pitch = 0.02 + 0.04 * u + (reduceMotion ? 0 : 0.015 * Math.sin(t * 0.9 - u * 2.5) * u);
    // the swing bends the tail near its base; the last part stays stiff, like the bony-tendon handle of the club
    const yaw = (reduceMotion ? 0 : 0.08 * Math.sin(t * 0.8 - u * 2) * u) + swing * Math.min(1, u / 0.4);
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
  club.position.copy(ringC[RINGS - 2]).add(tail.position); club.quaternion.setFromRotationMatrix(ringM[RINGS]);
  club.position.add(tv.set(-0.12, 0, 0).applyQuaternion(club.quaternion));
}
bendTail(0);
"""

MERGE_CALLS = """legGroups.forEach(g => mergeSkin(g));
mergeSkin(trunk, [tail]);
mergeSkin(head);
"""

SCENERY = SCENERY.replace("scenery: Hell Creek floodplain", "scenery: Hell Creek floodplain (shared with the Triceratops page)")

# ---- motion: wind up (tail swings away), whip across, settle; the body braces and the head turns a little
MOTION = re.sub(r"function chargeCurve\(t\) \{.*?\n\}\n", r"""function swingCurve(t) {           // tail yaw in radians: wind up, whip across, damped settle
  if (t < 0 || t > 1.8) return 0;
  if (t < 0.4) return 0.75 * ease(t / 0.4);
  if (t < 0.55) return 0.75;
  if (t < 0.78) { const u = (t - 0.55) / 0.23; return 0.75 - 1.75 * u * u; }
  const u = (t - 0.78) / 1.02; return -1.0 * Math.exp(-3.2 * u) * Math.cos(u * 9);
}
""", MOTION, flags=re.S)
for a, b in [("    bendTail(t);\n", "    bendTail(t, swingCurve(t - roarStart));\n"),
             ("  const { lunge, dip } = chargeCurve(t - roarStart);\n  rex.position.x = lunge;\n  headPivot.rotation.z = headBase - 0.22 * dip;\n",
              "  const sw = swingCurve(t - roarStart);\n  if (reduceMotion) bendTail(0, sw);\n  rex.rotation.y = -0.07 * sw;\n  headPivot.rotation.y += 0.14 * sw;\n")]:
    assert a in MOTION, a[:40]; MOTION = MOTION.replace(a, b)

out = head_part + "\n" + ANIMAL + "\n" + paint_part + "\n" + MERGE_CALLS + "\n" + SCENERY + "\n" + MOTION
pathlib.Path(ROOT + "/3d/ankylosaurus-3d.html").write_text(out)
print("ok", len(out))

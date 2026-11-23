import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Generate spinosaurus-3d.html from the T. rex 3D page: same engine, paint, merge and page code; new animal build,
river-margin ground and a strike-at-a-fish move. Anatomy as in sp_spinosaurus.py: a 14 m biped with its weight over
the hips (Sereno et al. 2022), short hind legs with long toes, robust three-fingered arms with a big thumb claw, a long
low skull with straight conical teeth and set-back nostrils, an S-curved neck, a thin sail of spines up to about
1.65 m peaking over the rear of the back, and a deep, narrow, paddle-like tail (Ibrahim et al. 2020)."""
import pathlib, re, sys
sys.path.insert(0, HERE)
import sp_spinosaurus as S

src = pathlib.Path(ROOT + "/3d/trex-3d.html").read_text()
lines = src.split("\n")
def find(prefix):
    return next(i for i, l in enumerate(lines) if l.startswith(prefix))
a_animal = find("// ---------------------------------------------------------------- the animal")
a_paint = find("// ---------------------------------------------------------------- paint")
a_scenery = find("// ---------------------------------------------------------------- scenery")
a_motion = find("// ---------------------------------------------------------------- motion")
head_part = "\n".join(lines[:a_animal])
paint_merge = "\n".join(lines[a_paint:a_scenery])
motion = "\n".join(lines[a_motion:])

head_part = (head_part
    .replace("<title>T. rex 3D model</title>", "<title>Spinosaurus 3D model</title>")
    .replace("background: #C9D6DA;", "background: #DCD6C4;")
    .replace("Interactive 3D model of a Tyrannosaurus rex. Drag to orbit, scroll or pinch to zoom, click the dinosaur to make it roar.",
             "Interactive 3D model of a Spinosaurus. Drag to orbit, scroll or pinch to zoom, click the dinosaur to make it strike at a fish.")
    .replace("<h1>T. rex</h1>", "<h1>Spinosaurus</h1>")
    .replace("and click the dinosaur to make it roar.", "and click the dinosaur to make it strike at a fish.")
    .replace('<button type="button" id="roar">Roar</button>', '<button type="button" id="roar">Strike</button>'))
head_part = re.sub(r"const C = \{.*?\};", """const C = {
  skin: new THREE.Color('#A0694A'), belly: new THREE.Color('#E2D3B4'), outline: '#2A1C22',
  tooth: '#EFE6D0', claw: '#3A2A2C', eye: '#E0B04A', mouth: '#5A2A26', tongue: '#8E3A3E',
  sail: '#C98E48', spine: '#7A4A30', sky: '#DCD6C4', ground: '#C3A877', water: '#9FB3AE', dune: '#D2BE94'
};""", head_part, flags=re.S)
head_part = re.sub(r"const HOME = \{.*?\};", "const HOME = { pos: new THREE.Vector3(4.5, 4.4, 21), target: new THREE.Vector3(0.8, 2.6, 0) };", head_part)
head_part = re.sub(r"Object\.assign\(sun\.shadow\.camera, \{.*?\}\);", "Object.assign(sun.shadow.camera, { left: -10, right: 10, top: 8, bottom: -4, near: 4, far: 34 });", head_part)
assert "Spinosaurus" in head_part and "#A0694A" in head_part and "4.5, 4.4, 21" in head_part

# 2D outlines reused for the skull and jaw (drawing units; jaw hinge near 806, 252)
ANIMAL = r"""// ---------------------------------------------------------------- the animal
const rex = new THREE.Group(); scene.add(rex);
const hips = new THREE.Group(); hips.position.set(0, 2.55, 0); rex.add(hips);   // short hind legs: hips about 2.5 m up
const trunk = new THREE.Group(); hips.add(trunk);                 // breathes

// trunk masses: long and fairly narrow
const hipMass = mesh(ellipsoid(1.1, 0.78, 0.66), skinMat, { stripes: true }); hipMass.position.set(0, 0.2, 0); trunk.add(hipMass);
const belly = mesh(ellipsoid(2.0, 0.9, 0.76), skinMat, { stripes: true }); belly.position.set(1.6, -0.02, 0); trunk.add(belly);
const chest = mesh(ellipsoid(0.98, 0.88, 0.7), skinMat, { stripes: true }); chest.position.set(3.1, -0.12, 0); chest.rotation.z = 0.15; trunk.add(chest);

// sail: thin skin over tall neural spines, tallest over the rear of the back; scalloped between spine tips
const SAIL_TIPS = [[3.8, 1.0], [3.45, 1.32], [3.1, 1.62], [2.75, 1.9], [2.4, 2.12], [2.05, 2.3], [1.7, 2.42], [1.35, 2.5], [1.0, 2.5], [0.7, 2.38], [0.45, 2.1], [0.25, 1.6], [0.1, 1.0]];
const sailShape = new THREE.Shape(); sailShape.moveTo(4.05, 0.55);
let prev = [4.05, 0.55];
for (const [x, y] of SAIL_TIPS) { const mx = (prev[0] + x) / 2, my = (prev[1] + y) / 2 - 0.08; sailShape.quadraticCurveTo(mx, my, x, y); prev = [x, y]; }
sailShape.lineTo(-0.05, 0.62); sailShape.bezierCurveTo(1.2, 0.78, 2.8, 0.78, 4.05, 0.55);
const sailGeo = new THREE.ExtrudeGeometry(sailShape, { depth: 0.07, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02, bevelSegments: 1, curveSegments: 6 }).translate(0, 0, -0.035);
const sail = mesh(sailGeo, toon(C.sail), { outline: true, shadow: true }); trunk.add(sail);
const spineMat = toon(C.spine);
function batcher(mat) {
  const parts = [];
  return { add(m) { m.updateMatrix(); parts.push(m.geometry.clone().applyMatrix4(m.matrix)); },
           flush(parent) { if (parts.length) parent.add(new THREE.Mesh(mergeGeometries(parts), mat)); } };
}
const spines = batcher(spineMat);
for (const [x, y] of SAIL_TIPS) for (const z of [0.05, -0.05]) {
  const h = y - 0.62, sp = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.03, h, 6), spineMat); sp.position.set(x, 0.62 + h / 2 - 0.02, z); spines.add(sp);
}
spines.flush(trunk);

// S-curved neck: rises steeply from the shoulders, then bends forward to the head
const neckJoint = new THREE.Group(); neckJoint.position.set(3.7, 0.35, 0); neckJoint.rotation.z = 0.95; trunk.add(neckJoint);
const neck = mesh(new THREE.CylinderGeometry(0.34, 0.56, 1.9, 26, 4).rotateZ(-Math.PI / 2).translate(0.95, 0, 0).scale(1, 1, 0.82), skinMat, { stripes: true }); neckJoint.add(neck);
const neckEnd = ball(new THREE.Vector3(1.9, 0, 0), 0.36, { stripes: true }); neckJoint.add(neckEnd);
const headPivot = new THREE.Group(); headPivot.position.set(1.95, 0.0, 0); headPivot.rotation.z = -1.1; neckJoint.add(headPivot);
const head = new THREE.Group(); head.position.set(-0.05, -0.1, 0); headPivot.add(head);

// long, low, crocodile-like skull from the 2D outlines
const HS = { s: 0.0098, ox: 806, oy: 250, x0: 0, x1: 1.6 };
const SKULL = '__SKULL__', JAWP = '__JAW__';
const MOUTH = 'M812 252 C850 260 900 266 940 270 L936 276 C900 274 850 270 812 262 Z';
const skull = mesh(profile(SKULL, 0.42, 0.55, HS), skinMat, { kind: 'head' }); head.add(skull);
const jaw = new THREE.Group(); head.add(jaw);                     // hinge at origin
jaw.add(mesh(profile(JAWP, 0.36, 0.55, HS), skinMat, { kind: 'head' }));
jaw.add(mesh(profile(MOUTH, 0.26, 0.5, HS), toon(C.mouth), { outline: false }));
const headX = x => (x - HS.ox) * HS.s, headY = y => -(y - HS.oy) * HS.s;
const halfW = (X, depth) => (depth / 2) * (1 - 0.55 * Math.min(Math.max(X / 1.6, 0), 1) ** 2) + 0.05;
const toothMat = toon(C.tooth), clawMat = toon(C.claw);
const upperTeeth = batcher(toothMat), lowerTeeth = batcher(toothMat);
for (const side of [1, -1]) {
  for (let x = 820; x <= 946; x += 9) {                           // straight conical teeth; bigger at the front
    const y = 252 + (x - 800) * 0.09 - (x > 918 && x < 934 ? 5 : 0), X = headX(x), big = x > 920 ? 1.5 : 1;
    const t = new THREE.Mesh(new THREE.ConeGeometry(0.018 * big, 0.08 * big, 8), toothMat);
    t.rotation.x = Math.PI; t.position.set(X, headY(y) - 0.03, side * (halfW(X, 0.42) - 0.04)); upperTeeth.add(t);
  }
  for (let x = 826; x <= 944; x += 10) {
    const y = 260 + (x - 800) * 0.085, X = headX(x);
    const t = new THREE.Mesh(new THREE.ConeGeometry(0.015, 0.06, 8), toothMat);
    t.position.set(X, headY(y) + 0.03, side * (halfW(X, 0.36) - 0.05)); lowerTeeth.add(t);
  }
  const eyeX = headX(828), eyeY = headY(222), ez = side * (halfW(eyeX, 0.42) - 0.02);
  const eye = new THREE.Group(); eye.position.set(eyeX, eyeY, ez); head.add(eye); eye.userData.isEye = true;
  eye.add(new THREE.Mesh(new THREE.SphereGeometry(0.055, 14, 10), toon(C.eye)));
  const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.028, 10, 8), toon('#15110D')); pupil.position.z = side * 0.035; eye.add(pupil);
  const brow = mesh(ellipsoid(0.12, 0.04, 0.05, 12, 8), skinMat, { kind: 'head', shadow: false }); brow.position.set(eyeX + 0.01, eyeY + 0.06, ez * 0.95); head.add(brow);
  const nostril = new THREE.Mesh(new THREE.SphereGeometry(0.03, 10, 8).scale(1.6, 0.7, 0.8), toon('#2A1C22'));   // set well back on the snout
  nostril.position.set(headX(880), headY(224), side * (halfW(headX(880), 0.42) - 0.03)); head.add(nostril);
}
const crest = mesh(ellipsoid(0.1, 0.06, 0.06, 12, 8), skinMat, { kind: 'head', shadow: false }); crest.position.set(headX(850), headY(204), 0); head.add(crest);   // small crest before the eyes
upperTeeth.flush(head); lowerTeeth.flush(jaw);
const eyes = []; head.traverse(o => { if (o.userData.isEye) eyes.push(o); });

// arms: robust, three fingers, the first with an enlarged claw
const arms = [];
for (const side of [1, -1]) {
  const shoulder = new THREE.Group(); shoulder.position.set(3.25, -0.55, side * 0.5); trunk.add(shoulder);
  const s0 = new THREE.Vector3(0, 0, 0), e = new THREE.Vector3(0.3, -0.55, side * 0.06), w = new THREE.Vector3(0.78, -0.62, side * 0.08);
  shoulder.add(limb(s0, e, 0.17, 0.13), limb(e, w, 0.13, 0.09), ball(e, 0.13));
  const claws = batcher(clawMat);
  for (const [dz, len, big] of [[0.07, 0.22, 2.0], [0, 0.26, 1.0], [-0.07, 0.22, 1.0]]) {
    const tip = w.clone().add(new THREE.Vector3(len, -0.14, side * dz));
    shoulder.add(limb(w, tip, 0.05, 0.03, { outline: false, shadow: false }));
    const claw = new THREE.Mesh(new THREE.ConeGeometry(0.03 * big, 0.11 * big, 6), clawMat); claw.position.copy(tip); claw.rotation.z = Math.PI * 0.8; claws.add(claw);
  }
  claws.flush(shoulder);
  arms.push(shoulder);
}

// legs: short, with long toes and flat-bottomed claws
const legGroups = [];
function leg(side, dx) {
  const g = new THREE.Group(); legGroups.push(g); g.position.set(dx, 0, side * 0.5); hips.add(g);
  const P = (x, y) => new THREE.Vector3(x, y, 0);
  const knee = P(0.5, -1.15), ankle = P(0.05, -2.05), ballP = P(0.38, -2.42);
  const thigh = mesh(ellipsoid(0.62, 0.9, 0.5), skinMat, { kind: 'leg' }); thigh.position.set(0.25, -0.55, 0); thigh.rotation.z = 0.25; g.add(thigh);
  const calf = mesh(ellipsoid(0.32, 0.6, 0.32), skinMat, { kind: 'leg' }); calf.position.set(0.32, -1.55, 0); calf.rotation.z = -0.5; g.add(calf);
  g.add(limb(knee, ankle, 0.28, 0.16, { kind: 'leg' }), limb(ankle, ballP, 0.15, 0.12, { kind: 'leg' }), ball(ankle, 0.16, { kind: 'leg' }), ball(ballP, 0.13, { kind: 'leg' }));
  const claws = batcher(clawMat);
  for (const [ang, len] of [[0.3, 0.6], [0, 0.72], [-0.3, 0.6]]) {
    const tip = ballP.clone().add(new THREE.Vector3(Math.cos(ang) * len, -0.08, Math.sin(ang) * len));
    g.add(limb(ballP, tip, 0.09, 0.06, { kind: 'leg' }));
    const claw = new THREE.Mesh(new THREE.SphereGeometry(0.06, 8, 6).scale(1.6, 0.5, 0.9), clawMat);   // flat-bottomed
    claw.position.copy(tip).add(new THREE.Vector3(Math.cos(ang) * 0.06, -0.03, Math.sin(ang) * 0.06)); claw.rotation.y = -ang; claws.add(claw);
  }
  claws.flush(g);
}
leg(1, 0.15); leg(-1, -0.35);

// tail: deep and narrow, a paddle built from tall neural spines and long chevrons
const TL = 5.6, RINGS = 56, RAD = 26;
const tailH = u => 0.7 * Math.pow(1 - u, 0.55) + 0.08;     // half-height: stays deep far down the tail
const tailW = u => 0.55 * Math.pow(1 - u, 1.2) + 0.03;     // half-width: thin
const tailGeo = new THREE.BufferGeometry();
const tPos = [], tOff = [], tRing = [], tIdx = [];
for (let i = 0; i <= RINGS; i++) {
  const u = i / RINGS;
  for (let k = 0; k < RAD; k++) {
    const a = (k / RAD) * Math.PI * 2, oy = Math.cos(a) * tailH(u), oz = Math.sin(a) * tailW(u);
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
tail.position.set(-0.75, 0.22, 0); tail.frustumCulled = false; tail.children[0].frustumCulled = false; trunk.add(tail);
const ringM = Array.from({ length: RINGS + 2 }, () => new THREE.Matrix4()), ringC = Array.from({ length: RINGS + 2 }, () => new THREE.Vector3());
const mz = new THREE.Matrix4(), my = new THREE.Matrix4(), tv = new THREE.Vector3(), tn = new THREE.Vector3();
const tailC = new THREE.Vector3();
function bendTail(t) {
  const step = TL / RINGS; const c = tailC.set(0, 0, 0);
  for (let i = 0; i <= RINGS + 1; i++) {
    const u = Math.min(i / RINGS, 1);
    const pitch = -0.02 + 0.06 * u + (reduceMotion ? 0 : 0.02 * Math.sin(t * 0.9 - u * 2.5) * u);
    const yaw = reduceMotion ? 0 : 0.3 * Math.sin(t * 1.0 - u * 2.6) * u * u;
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
const tailRestPose = tailGeo.attributes.position.array.slice();   // painted from the rest pose
const tailRestNormals = tailGeo.attributes.normal.array.slice();
""".replace("__SKULL__", S.SKULL_D).replace("__JAW__", S.JAW_D)

SCENERY = """// ---------------------------------------------------------------- scenery: Bahariya river margin and tidal flats
const ground = new THREE.Mesh(new THREE.CircleGeometry(70, 64).rotateX(-Math.PI / 2), toon(C.ground)); ground.receiveShadow = true; scene.add(ground);
for (const [r, w, h, c] of [[13, 1.2, 0.04, '#B09461'], [17, 1.6, 0.03, '#D2BE94'], [22, 1.4, 0.02, '#A3885A']]) {
  const ring = new THREE.Mesh(new THREE.RingGeometry(r, r + w, 64).rotateX(-Math.PI / 2), toon(c)); ring.position.y = h; ring.receiveShadow = true; scene.add(ring);
}
const water = new THREE.Mesh(new THREE.PlaneGeometry(160, 30).rotateX(-Math.PI / 2), toon(C.water)); water.position.set(0, 0.05, -26); scene.add(water);
for (const [x, z, rx, ry] of [[-30, -48, 24, 4], [6, -56, 28, 5], [38, -46, 20, 3.5]]) {
  const m = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2).scale(rx, ry, 8), toon(C.dune)); m.position.set(x, 0, z); scene.add(m);
}
"""

# ---- motion: wind up (head rises, jaws open), lunge down at the water, snap shut, recover
motion = re.sub(r"function roarCurve\(t\) \{.*?\n\}\n", r"""function roarCurve(t) {            // strike: lift < 0 raises the head, lift > 0 drives it down; open 0..1
  if (t < 0 || t > 1.7) return { lift: 0, open: 0, lunge: 0 };
  if (t < 0.3) { const u = ease(t / 0.3); return { lift: -0.4 * u, open: 0.8 * u, lunge: -0.15 * u }; }
  if (t < 0.6) { const u = backOut((t - 0.3) / 0.3); return { lift: -0.4 + 1.4 * u, open: 0.8 + 0.2 * u, lunge: -0.15 + 0.6 * u }; }
  if (t < 0.68) { const u = (t - 0.6) / 0.08; return { lift: 1, open: 1 - u, lunge: 0.45 }; }
  if (t < 1.1) return { lift: 1, open: 0, lunge: 0.45 };
  const u = ease((t - 1.1) / 0.6); return { lift: 1 - u, open: 0, lunge: 0.45 * (1 - u) };
}
""", motion, flags=re.S)
for a, b in [("  const { lift, open } = roarCurve(t - roarStart);\n  neckJoint.rotation.z = neckBase + 0.12 * lift;\n  headPivot.rotation.z = headBase + 0.22 * lift;\n  jaw.rotation.z = -0.5 * open;\n  arms.forEach(a => a.rotation.z = -0.35 * open);",
              "  const { lift, open, lunge } = roarCurve(t - roarStart);\n  neckJoint.rotation.z = neckBase - 0.45 * lift;\n  headPivot.rotation.z = headBase - 0.25 * lift;\n  jaw.rotation.z = -0.45 * open;\n  rex.position.x = lunge;\n  arms.forEach(a => a.rotation.z = -0.25 * Math.max(0, lift));")]:
    assert a in motion, "motion application lines changed in trex-3d.html"
    motion = motion.replace(a, b)

out = head_part + "\n" + ANIMAL + "\n" + paint_merge + "\n" + SCENERY + "\n" + motion
pathlib.Path(ROOT + "/3d/spinosaurus-3d.html").write_text(out)
print("ok", len(out))

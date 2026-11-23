import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Generate triceratops-3d.html from the T. rex 3D engine: same renderer, shaders, paint, merge and loading code;
sculpted continuous-loft Triceratops horridus anatomy (torso, saddle frill, wedge skull, curved horns,
flexed-elbow forelimbs, columnar hind limbs, sloping tail) and grounded weighted charge motion."""
import pathlib, re

src = pathlib.Path(ROOT + "/3d/trex-3d.html").read_text(encoding="utf-8")
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

# ---- header / palette / shadow quality / belly wrap / UI text
head_part = (head_part
    .replace("<title>T. rex 3D model</title>", "<title>Triceratops 3D model</title>")
    .replace("background: #C9D6DA;", "background: #CBD9D0;")
    .replace("Interactive 3D model of a Tyrannosaurus rex. Drag to orbit, scroll or pinch to zoom, click the dinosaur to make it roar.",
             "Interactive 3D model of a Triceratops. Drag to orbit, scroll or pinch to zoom, click the dinosaur to make it charge.")
    .replace("<h1>T. rex</h1>", "<h1>Triceratops</h1>")
    .replace("and click the dinosaur to make it roar.", "and click the dinosaur to make it charge.")
    .replace('<button type="button" id="roar">Roar</button>', '<button type="button" id="roar">Charge</button>')
    .replace("sun.shadow.mapSize.set(1024, 1024);", "sun.shadow.mapSize.set(2048, 2048);")
    .replace("sun.shadow.bias = -0.0008;", "sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.045;")
    .replace("float bellyAmt = smoothstep(-0.02, -0.38, ny) * vPaint.y;",
             "float bellyAmt = smoothstep(-0.18, -0.52, ny) * vPaint.y;"))
head_part = re.sub(r"const C = \{.*?\};", """const C = {
  skin: new THREE.Color('#7A8450'), belly: new THREE.Color('#DCCFA6'), outline: '#2A1C22',
  frill: '#C27A48', horn: '#E6D9BC', beak: '#4A3A30', claw: '#3A2A2C', eye: '#E0B04A',
  sky: '#CBD9D0', ground: '#9AA864', hill: '#A9B596', hill2: '#93A27A', river: '#9DBFC6'
};""", head_part, flags=re.S)
head_part = head_part.replace("const HOME = { pos: new THREE.Vector3(3.5, 4.2, 19), target: new THREE.Vector3(-0.4, 2.7, 0) };",
                              "const HOME = { pos: new THREE.Vector3(4.2, 3.0, 15.5), target: new THREE.Vector3(0.4, 1.8, 0) };")
head_part = head_part.replace("controls.minDistance = 7; controls.maxDistance = 40;", "controls.minDistance = 5; controls.maxDistance = 32;")
head_part = head_part.replace("Object.assign(sun.shadow.camera, { left: -9, right: 9, top: 7, bottom: -4, near: 4, far: 30 });",
                              "Object.assign(sun.shadow.camera, { left: -8, right: 8, top: 6, bottom: -3, near: 4, far: 30 });")
# keep olive skin on the back of the frill (no downward-normal belly bleach)
paint_part = paint_part.replace("kind === 'leg' ? 0.35 : 1", "kind === 'frill' ? 0 : kind === 'leg' ? 0.35 : 1")
assert "Triceratops" in head_part and "#7A8450" in head_part and "normalBias = 0.045" in head_part and "kind === 'frill'" in paint_part

ANIMAL = r"""// ---------------------------------------------------------------- the animal
const rex = new THREE.Group(); scene.add(rex);                    // whole animal (lunges on the charge)
const BASE_HIP_Y = 2.585;                                         // raises soles by outline thickness so foot ink rests flush on y=0
const hips = new THREE.Group(); hips.position.set(0, BASE_HIP_Y, 0); rex.add(hips);
const trunk = new THREE.Group(); hips.add(trunk);                 // breathes and pitches on charge

const hornMat = toon(C.horn), beakMat = toon(C.beak), frillMat = toon(C.frill), clawMat = toon(C.claw);

// ---- sculpting helpers (parallel-transport frames with guaranteed outward normals: U x V = +T)
function catmull(stations, u) {
  const n = stations.length - 1, f = THREE.MathUtils.clamp(u, 0, 1) * n;
  const i = Math.min(Math.floor(f), n - 1), t = f - i;
  const p0 = stations[Math.max(0, i - 1)], p1 = stations[i], p2 = stations[i + 1], p3 = stations[Math.min(n, i + 2)];
  const t2 = t * t, t3 = t2 * t;
  const out = {};
  for (const k of Object.keys(p1)) {
    const v0 = p0[k], v1 = p1[k], v2 = p2[k], v3 = p3[k];
    out[k] = 0.5 * ((2 * v1) + (-v0 + v2) * t + (2 * v0 - 5 * v1 + 4 * v2 - v3) * t2 + (-v0 + 3 * v1 - 3 * v2 + v3) * t3);
  }
  return out;
}

// Loft a smooth closed organic mesh along a 3D spine using parallel transport (zero frame-flip twists on hooked curves)
function loftMesh(stations, { segs = 32, rad = 28, upHint = new THREE.Vector3(0, 1, 0), capStart = true, capEnd = true } = {}) {
  const pts = [], sts = [];
  for (let i = 0; i <= segs; i++) {
    const s = catmull(stations, i / segs);
    sts.push(s); pts.push(new THREE.Vector3(s.x, s.y, s.z || 0));
  }
  const pos = [], idx = [];
  const T = new THREE.Vector3(), prevT = new THREE.Vector3(), U = new THREE.Vector3(), V = new THREE.Vector3();
  const qStep = new THREE.Quaternion();
  for (let i = 0; i <= segs; i++) {
    const pPrev = pts[Math.max(0, i - 1)], pNext = pts[Math.min(segs, i + 1)];
    T.subVectors(pNext, pPrev).normalize();
    if (i === 0) {
      const ref = Math.abs(T.dot(upHint)) > 0.94 ? new THREE.Vector3(0, 0, 1) : upHint;
      V.crossVectors(T, ref).normalize();
      U.crossVectors(V, T).normalize();
    } else {
      qStep.setFromUnitVectors(prevT, T);
      U.applyQuaternion(qStep).normalize();
      V.crossVectors(T, U).normalize();
      U.crossVectors(V, T).normalize();
    }
    prevT.copy(T);
    const s = sts[i], P = pts[i];
    for (let k = 0; k < rad; k++) {
      const a = (k / rad) * Math.PI * 2;
      const ca = Math.cos(a), sa = Math.sin(a);
      const ry = ca >= 0 ? s.ryTop : s.ryBot;
      const flank = 1 + (s.bellyWide || 0) * Math.max(0, -ca) - (s.pinchTop || 0) * Math.max(0, ca) * Math.max(0, ca);
      const lu = ca * ry, lv = sa * s.rz * flank;
      pos.push(P.x + U.x * lu + V.x * lv, P.y + U.y * lu + V.y * lv, P.z + U.z * lu + V.z * lv);
    }
  }
  for (let i = 0; i < segs; i++) for (let k = 0; k < rad; k++) {
    const a = i * rad + k, b = i * rad + (k + 1) % rad, c = a + rad, d = b + rad;
    idx.push(a, b, c, b, d, c);
  }
  if (capStart) {
    const cIdx = pos.length / 3, p0 = pts[0]; pos.push(p0.x, p0.y, p0.z);
    for (let k = 0; k < rad; k++) idx.push(cIdx, (k + 1) % rad, k);
  }
  if (capEnd) {
    const cIdx = pos.length / 3, p1 = pts[segs]; pos.push(p1.x, p1.y, p1.z);
    for (let k = 0; k < rad; k++) idx.push(cIdx, segs * rad + k, segs * rad + (k + 1) % rad);
  }
  const g = new THREE.BufferGeometry();
  g.setIndex(idx); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.computeVertexNormals();
  return g;
}

function batcher(mat) {
  const parts = [];
  return { add(m) { m.updateMatrix(); parts.push(m.geometry.clone().applyMatrix4(m.matrix)); },
           flush(parent, opts) { if (parts.length) { const m = mesh(mergeGeometries(parts), mat, opts || { outline: false, shadow: false }); parent.add(m); return m; } } };
}

// ---- 1. CONTINUOUS SCULPTED TORSO + SYNCERVICAL NECK
// Smooth sacral arch (-0.62) flowing seamlessly into heavy caudofemoral pelvis (-1.36..-2.04),
// broad barrel ribcage (+0.20), sloping shoulders (+1.72), thick muscular neck (+2.76).
const torsoGeo = loftMesh([
  { x: -2.04, y: -0.18, ryTop: 0.56, ryBot: 0.48, rz: 0.52, pinchTop: 0.08, bellyWide: 0.04 }, // broad tail bridge
  { x: -1.36, y:  0.00, ryTop: 0.92, ryBot: 0.74, rz: 0.84, pinchTop: 0.14, bellyWide: 0.08 }, // muscular rear pelvis
  { x: -0.62, y:  0.12, ryTop: 1.10, ryBot: 0.94, rz: 1.08, pinchTop: 0.16, bellyWide: 0.12 }, // high sacral/hip arch
  { x:  0.20, y:  0.04, ryTop: 1.10, ryBot: 1.16, rz: 1.24, pinchTop: 0.16, bellyWide: 0.16 }, // wide deep barrel ribcage
  { x:  1.00, y: -0.08, ryTop: 1.03, ryBot: 1.12, rz: 1.16, pinchTop: 0.16, bellyWide: 0.14 }, // anterior ribcage
  { x:  1.72, y: -0.22, ryTop: 0.92, ryBot: 0.96, rz: 1.00, pinchTop: 0.14, bellyWide: 0.10 }, // muscular shoulders
  { x:  2.28, y: -0.34, ryTop: 0.72, ryBot: 0.72, rz: 0.74, pinchTop: 0.10, bellyWide: 0.04 }, // neck base
  { x:  2.76, y: -0.34, ryTop: 0.58, ryBot: 0.56, rz: 0.60, pinchTop: 0.08, bellyWide: 0.02 }, // skull attachment
], { segs: 38, rad: 30 });
trunk.add(mesh(torsoGeo, skinMat, { stripes: true }));

// ---- 2. HEAD, SADDLE FRILL, WEDGE SKULL, PARROT BEAK & HORNS
const headPivot = new THREE.Group(); headPivot.position.set(2.68, -0.24, 0); trunk.add(headPivot);
const head = new THREE.Group(); headPivot.add(head);
const excludeHead = []; // meshes keeping custom outline/shadow flags outside mergeSkin(head)

// Upper cranium + deep integrated jugal cheeks + laterally compressed snout (tapers cleanly inside beak socket)
const skullGeo = loftMesh([
  { x: -0.08, y:  0.10, ryTop: 0.54, ryBot: 0.56, rz: 0.66, pinchTop: 0.14, bellyWide: 0.20 }, // rear cranium / throat blend
  { x:  0.38, y:  0.02, ryTop: 0.66, ryBot: 0.56, rz: 0.80, pinchTop: 0.22, bellyWide: 0.26 }, // broad muscular jugal cheeks
  { x:  0.76, y:  0.00, ryTop: 0.66, ryBot: 0.48, rz: 0.66, pinchTop: 0.26, bellyWide: 0.20 }, // orbits / brow horn base
  { x:  1.20, y: -0.04, ryTop: 0.54, ryBot: 0.42, rz: 0.44, pinchTop: 0.30, bellyWide: 0.12 }, // preorbital face
  { x:  1.66, y: -0.07, ryTop: 0.49, ryBot: 0.36, rz: 0.28, pinchTop: 0.34, bellyWide: 0.06 }, // deep narrow nasal arch
  { x:  2.02, y: -0.16, ryTop: 0.29, ryBot: 0.19, rz: 0.16, pinchTop: 0.32, bellyWide: 0.00 }, // smooth taper into beak collar
  { x:  2.18, y: -0.25, ryTop: 0.14, ryBot: 0.10, rz: 0.08, pinchTop: 0.24, bellyWide: 0.00 },
], { segs: 30, rad: 30 });
head.add(mesh(skullGeo, skinMat, { kind: 'head' }));

// Heavy pyramidal epijugal cheek bosses blended cleanly into the lower jugal flare (no skinny thorn)
for (const side of [1, -1]) {
  const ejGeo = loftMesh([
    { x: 0.38, y: -0.22, z: side * 0.66, ryTop: 0.17, ryBot: 0.17, rz: 0.16 },
    { x: 0.28, y: -0.32, z: side * 0.77, ryTop: 0.095, ryBot: 0.095, rz: 0.09 },
    { x: 0.22, y: -0.38, z: side * 0.82, ryTop: 0.04, ryBot: 0.04, rz: 0.038 },
  ], { segs: 8, rad: 12 });
  head.add(mesh(ejGeo, skinMat, { kind: 'head' }));
}

// Sleek keratin upper beak (rhamphotheca) flush with dorsal snout slope and crisp parrot-hook tip
const upperBeakGeo = loftMesh([
  { x: 1.98, y: -0.15, ryTop: 0.315, ryBot: 0.20, rz: 0.18,  pinchTop: 0.34, bellyWide: 0.00 },
  { x: 2.16, y: -0.21, ryTop: 0.22,  ryBot: 0.15, rz: 0.115, pinchTop: 0.34, bellyWide: 0.00 },
  { x: 2.30, y: -0.30, ryTop: 0.11,  ryBot: 0.09, rz: 0.060, pinchTop: 0.28, bellyWide: 0.00 },
  { x: 2.35, y: -0.39, ryTop: 0.032, ryBot: 0.028, rz: 0.022, pinchTop: 0.18, bellyWide: 0.00 },
  { x: 2.34, y: -0.43, ryTop: 0.004, ryBot: 0.004, rz: 0.004, pinchTop: 0.05, bellyWide: 0.00 },
], { segs: 18, rad: 20 });
head.add(mesh(upperBeakGeo, beakMat, {}));

// Pivoted lower jaw (mandible + predentary lower beak) raised cleanly into the muscular cheek line
const jawPivot = new THREE.Group(); jawPivot.position.set(0.56, -0.34, 0); head.add(jawPivot);
const jawInner = new THREE.Group(); jawInner.position.set(-0.56, 0.34, 0); jawPivot.add(jawInner);
const jawGeo = loftMesh([
  { x: 0.38, y: -0.35, ryTop: 0.18, ryBot: 0.17, rz: 0.50, pinchTop: 0.10, bellyWide: 0.04 }, // nested inside deep cheek
  { x: 0.94, y: -0.38, ryTop: 0.18, ryBot: 0.16, rz: 0.38, pinchTop: 0.10, bellyWide: 0.02 },
  { x: 1.50, y: -0.39, ryTop: 0.15, ryBot: 0.14, rz: 0.23, pinchTop: 0.12, bellyWide: 0.00 },
  { x: 2.02, y: -0.38, ryTop: 0.10, ryBot: 0.10, rz: 0.105, pinchTop: 0.10, bellyWide: 0.00 },
], { segs: 16, rad: 20 });
jawInner.add(mesh(jawGeo, skinMat, { kind: 'head' }));
const lowerBeakGeo = loftMesh([
  { x: 1.94, y: -0.38, ryTop: 0.115, ryBot: 0.11, rz: 0.12 },
  { x: 2.12, y: -0.37, ryTop: 0.095, ryBot: 0.09, rz: 0.082 },
  { x: 2.24, y: -0.34, ryTop: 0.055, ryBot: 0.05, rz: 0.042 },
  { x: 2.28, y: -0.31, ryTop: 0.012, ryBot: 0.012, rz: 0.010 },
], { segs: 10, rad: 16 });
jawInner.add(mesh(lowerBeakGeo, beakMat, { outline: false }));

// Large iconic external nares (nostrils) seated cleanly on the lateral snout wall behind the beak
const nostrilMat = toon('#2A1C22');
for (const side of [1, -1]) {
  const n = new THREE.Mesh(ellipsoid(0.135, 0.074, 0.036, 16, 10), nostrilMat);
  n.position.set(1.74, -0.02, side * 0.252); n.rotation.set(0, side * 0.30, -0.22);
  head.add(n);
}

// ---- 3. SCULPTED SADDLE-SHAPED FRILL (olive back + broad adult scalloped epoccipital rim + terracotta front face)
function buildFrillShield({ rScale = 1.0, thick = 0.15, xShift = 0, epocAmp = 0.062, radialRings = 14, segs = 76 }) {
  function rimR(a) {
    const ca = Math.cos(a), sa = Math.sin(a);
    const baseW = 1.44 * rScale, baseH = 1.24 * rScale;
    const saddleDip = 1 - 0.04 * Math.pow(Math.max(0, ca), 4);
    const squamosalFlare = 1 + 0.09 * Math.pow(Math.abs(sa), 2.2);
    const neckTuck = 1 - 0.34 * Math.pow(Math.max(0, -ca), 2.4);
    const epocMask = THREE.MathUtils.smoothstep(ca, -0.46, -0.14);
    const wave = epocAmp * epocMask * Math.pow(0.5 + 0.5 * Math.cos(a * 15), 1.15); // broader adult lobes
    const y = ca * baseH * saddleDip * neckTuck + wave * ca;
    const z = sa * baseW * squamosalFlare * (0.76 + 0.24 * Math.max(-0.3, ca)) + wave * sa;
    return [y, z];
  }
  function surfX(y, z) {
    return xShift + 0.15 * z * z - 0.04 * y * y + 0.07 * Math.max(0, -y) * z * z;
  }
  const pos = [], idx = [];
  const ringPts = (radialRings + 1) * segs;
  for (const face of [1, -1]) {
    for (let r = 0; r <= radialRings; r++) {
      const u = r / radialRings;
      const halfT = (thick * 0.5) * (0.58 + 0.42 * Math.sqrt(Math.max(0, 1 - u * u * 0.85)));
      for (let k = 0; k < segs; k++) {
        const a = (k / segs) * Math.PI * 2;
        const [ry, rz] = rimR(a);
        const y = ry * u, z = rz * u;
        const x = surfX(y, z) + face * halfT;
        pos.push(x, y, z);
      }
    }
  }
  for (let r = 0; r < radialRings; r++) for (let k = 0; k < segs; k++) {
    const a = r * segs + k, b = r * segs + (k + 1) % segs, c = a + segs, d = b + segs;
    idx.push(a, c, b, b, c, d);
  }
  const off = ringPts;
  for (let r = 0; r < radialRings; r++) for (let k = 0; k < segs; k++) {
    const a = off + r * segs + k, b = off + r * segs + (k + 1) % segs, c = a + segs, d = b + segs;
    idx.push(a, b, c, b, d, c);
  }
  const fRim = radialRings * segs, bRim = off + radialRings * segs;
  for (let k = 0; k < segs; k++) {
    const kn = (k + 1) % segs;
    const a = fRim + k, b = fRim + kn, c = bRim + k, d = bRim + kn;
    idx.push(a, c, b, b, c, d);
  }
  const g = new THREE.BufferGeometry();
  g.setIndex(idx); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.computeVertexNormals();
  return g;
}

const frill = new THREE.Group();
frill.position.set(0.02, 0.64, 0);
frill.rotation.z = 0.62;
head.add(frill);
// Olive skin main structural frill (kind:'frill' prevents belly-bleach on rear downward-facing normals)
frill.add(mesh(buildFrillShield({ rScale: 1.12, thick: 0.16, xShift: 0, epocAmp: 0.062 }), skinMat, { kind: 'frill' }));
// Terracotta front display inlay cleanly offset proud of the olive shield (zero edge stipple)
frill.add(mesh(buildFrillShield({ rScale: 0.95, thick: 0.03, xShift: 0.076, epocAmp: 0.0 }), frillMat, { outline: false, shadow: false }));

// ---- 4. ADULT T. HORRIDUS S-RECURVED BROW HORNS (pointed tips) + FORWARD NASAL HORN + EYES
function browHorn(side) {
  const b = new THREE.Vector3(0.70, 0.46, side * 0.34);
  const curve = new THREE.CubicBezierCurve3(
    b.clone(),
    b.clone().add(new THREE.Vector3(0.48, 0.30, side * 0.24)),
    b.clone().add(new THREE.Vector3(1.14, 0.26, side * 0.28)),
    b.clone().add(new THREE.Vector3(1.72, 0.62, side * 0.14))
  );
  const SEGS = 24, RAD = 16, r0 = 0.20;
  const pts = curve.getPoints(SEGS);
  const pos = [], idx = [];
  const T = new THREE.Vector3(), prevT = new THREE.Vector3(), U = new THREE.Vector3(), V = new THREE.Vector3();
  const qStep = new THREE.Quaternion(), upHint = new THREE.Vector3(0, 1, 0);
  for (let i = 0; i <= SEGS; i++) {
    const u = i / SEGS;
    const r = Math.max(0.004, r0 * (1 + 0.16 * Math.pow(1 - u, 4)) * Math.pow(1 - u, 0.84));
    const pPrev = pts[Math.max(0, i - 1)], pNext = pts[Math.min(SEGS, i + 1)];
    T.subVectors(pNext, pPrev).normalize();
    if (i === 0) { V.crossVectors(T, upHint).normalize(); U.crossVectors(V, T).normalize(); }
    else { qStep.setFromUnitVectors(prevT, T); U.applyQuaternion(qStep).normalize(); V.crossVectors(T, U).normalize(); U.crossVectors(V, T).normalize(); }
    prevT.copy(T);
    const P = pts[i];
    for (let k = 0; k < RAD; k++) {
      const a = (k / RAD) * Math.PI * 2, c = Math.cos(a) * r, s = Math.sin(a) * r;
      pos.push(P.x + U.x * c + V.x * s, P.y + U.y * c + V.y * s, P.z + U.z * c + V.z * s);
    }
  }
  // project pointed apex along final tangent so outlineMat tapers to a crisp sharp point
  const tipIdx = pos.length / 3, tipP = pts[SEGS].clone().addScaledVector(T, 0.055);
  pos.push(tipP.x, tipP.y, tipP.z);
  for (let i = 0; i < SEGS; i++) for (let k = 0; k < RAD; k++) {
    const a = i * RAD + k, b2 = i * RAD + (k + 1) % RAD, c = a + RAD, d = b2 + RAD;
    idx.push(a, b2, c, b2, d, c);
  }
  for (let k = 0; k < RAD; k++) idx.push(tipIdx, SEGS * RAD + k, SEGS * RAD + (k + 1) % RAD);
  const g = new THREE.BufferGeometry();
  g.setIndex(idx); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.computeVertexNormals();
  return mesh(g, hornMat, {});
}

// Stout forward-canted nasal horn positioned over the anterior nasal arch
const nasalHornGeo = loftMesh([
  { x: 1.70, y: 0.32, ryTop: 0.165, ryBot: 0.165, rz: 0.11 },
  { x: 1.82, y: 0.54, ryTop: 0.105, ryBot: 0.105, rz: 0.075 },
  { x: 1.93, y: 0.72, ryTop: 0.036, ryBot: 0.036, rz: 0.028 },
  { x: 1.98, y: 0.80, ryTop: 0.004, ryBot: 0.004, rz: 0.004 },
], { segs: 12, rad: 14, upHint: new THREE.Vector3(1, 0, 0) });
head.add(mesh(nasalHornGeo, hornMat, {}));

for (const side of [1, -1]) {
  // fleshy brow-horn boss excluded from mergeSkin so outline:false stays clean
  const boss = mesh(ellipsoid(0.25, 0.18, 0.18, 16, 12), skinMat, { kind: 'head', outline: false });
  boss.position.set(0.70, 0.42, side * 0.34); head.add(boss); excludeHead.push(boss);
  head.add(browHorn(side));

  // eye tucked under clean supraorbital brow ridge (excluded from mergeSkin so shadow:false stays clean)
  const eye = new THREE.Group(); eye.position.set(0.74, 0.16, side * 0.58); head.add(eye); eye.userData.isEye = true;
  eye.add(new THREE.Mesh(new THREE.SphereGeometry(0.082, 16, 12), toon(C.eye)));
  const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.038, 12, 10), toon('#15110D'));
  pupil.position.set(0.02, 0, side * 0.054); eye.add(pupil);
  const brow = mesh(ellipsoid(0.21, 0.062, 0.08, 14, 8), skinMat, { kind: 'head', outline: false, shadow: false });
  brow.position.set(0.75, 0.24, side * 0.52); brow.rotation.z = -0.1; head.add(brow); excludeHead.push(brow);
}
const eyes = []; head.traverse(o => { if (o.userData.isEye) eyes.push(o); });

// ---- 5. SCULPTED CONTINUOUS LOFTED LIMBS & BROAD PADDED HOOFED FEET
const legGroups = [];
const legSockets = { hindNear: null, hindFar: null, frontNear: null, frontFar: null };

function footHoofs(g, fx, fy, fz, count, spread, yawBias = 0) {
  const nails = batcher(clawMat);
  for (let i = 0; i < count; i++) {
    const frac = count === 1 ? 0 : (i / (count - 1) - 0.5);
    const ang = frac * spread + yawBias;
    const n = new THREE.Mesh(new THREE.SphereGeometry(0.115, 12, 8).scale(1.18, 0.56, 1.04), clawMat);
    n.position.set(fx + Math.cos(ang) * 0.31, fy + 0.06, fz + Math.sin(ang) * 0.31);
    n.rotation.y = -ang;
    nails.add(n);
  }
  nails.flush(g, { outline: false, shadow: true });
}

// Columnar muscular hind leg: broad thigh tucked deeply inside pelvis -> flexed knee -> angled calf -> ankle -> broad padded foot (4 hooves)
function hindLeg(side, dx) {
  const sx = dx - 0.62, sy = -0.25, sz = side * 0.80;
  const g = new THREE.Group(); legGroups.push(g); g.position.set(sx, sy, sz); hips.add(g);
  const legGeo = loftMesh([
    { x:  0.02, y:  0.26, z: -side * 0.44, ryTop: 0.46, ryBot: 0.46, rz: 0.30 }, // tucked deeply inside hip
    { x:  0.08, y: -0.32, z: -side * 0.06, ryTop: 0.70, ryBot: 0.70, rz: 0.46 }, // broad muscular thigh
    { x:  0.18, y: -0.96, z:  side * 0.02, ryTop: 0.48, ryBot: 0.48, rz: 0.37 }, // knee
    { x: -0.04, y: -1.48, z:  0.00,        ryTop: 0.38, ryBot: 0.38, rz: 0.31 }, // muscular calf
    { x: -0.10, y: -1.96, z:  0.00,        ryTop: 0.28, ryBot: 0.28, rz: 0.27 }, // defined ankle / metatarsus
    { x:  0.03, y: -2.20, z:  0.00,        ryTop: 0.41, ryBot: 0.41, rz: 0.37 }, // padded foot flare
    { x:  0.05, y: -2.30, z:  0.00,        ryTop: 0.37, ryBot: 0.37, rz: 0.34 }, // sole (world y = +0.035 so ink outline hits y=0)
  ], { segs: 22, rad: 20, upHint: new THREE.Vector3(1, 0, 0) });
  g.add(mesh(legGeo, skinMat, { kind: 'leg' }));
  footHoofs(g, 0.05, -2.30, 0, 4, 1.15);
  return g;
}

// Broad semi-sprawled flexed-elbow foreleg: massive shoulder -> outward-bowed elbow -> beefy forearm -> anterolaterally splayed 3-hoofed forefoot
function frontLeg(side, dx) {
  const sx = dx + 1.64, sy = -0.56, sz = side * 0.86;
  const g = new THREE.Group(); legGroups.push(g); g.position.set(sx, sy, sz); hips.add(g);
  const legGeo = loftMesh([
    { x:  0.04, y:  0.24, z: -side * 0.44, ryTop: 0.34, ryBot: 0.34, rz: 0.26 }, // tucked deeply inside shoulder
    { x: -0.06, y: -0.32, z:  side * 0.04, ryTop: 0.47, ryBot: 0.47, rz: 0.37 }, // heavy upper arm
    { x: -0.28, y: -0.82, z:  side * 0.32, ryTop: 0.38, ryBot: 0.38, rz: 0.32 }, // broad flexed & outward-bowed elbow
    { x: -0.06, y: -1.34, z:  side * 0.20, ryTop: 0.31, ryBot: 0.31, rz: 0.28 }, // stout forearm
    { x:  0.04, y: -1.72, z:  side * 0.14, ryTop: 0.25, ryBot: 0.25, rz: 0.25 }, // wrist
    { x:  0.08, y: -1.91, z:  side * 0.12, ryTop: 0.36, ryBot: 0.36, rz: 0.33 }, // broad forefoot
    { x:  0.08, y: -1.99, z:  side * 0.12, ryTop: 0.33, ryBot: 0.33, rz: 0.30 }, // sole (world y = +0.035)
  ], { segs: 22, rad: 20, upHint: new THREE.Vector3(1, 0, 0) });
  g.add(mesh(legGeo, skinMat, { kind: 'leg' }));
  footHoofs(g, 0.08, -1.99, side * 0.12, 3, 0.9, side * 0.24);
  return g;
}

legSockets.hindNear = hindLeg(1, 0.12);
legSockets.hindFar = hindLeg(-1, -0.26);
legSockets.frontNear = frontLeg(1, 0.06);
legSockets.frontFar = frontLeg(-1, -0.22);

// ---- 6. CONTINUOUS TAPERED TAIL (seamless caudofemoral bridge, longer natural S-curve)
const TL = 4.05, RINGS = 56, RAD = 24;
const tailR = u => 0.78 * Math.pow(1 - u, 1.12) + 0.035;
const tailGeo = new THREE.BufferGeometry();
const tPos = [], tOff = [], tRing = [], tIdx = [];
for (let i = 0; i <= RINGS; i++) {
  const u = i / RINGS, r = tailR(u);
  for (let k = 0; k < RAD; k++) {
    const a = (k / RAD) * Math.PI * 2, oy = Math.cos(a) * r * 1.12, oz = Math.sin(a) * r * 0.86;
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
tail.position.set(-1.32, -0.05, 0); tail.frustumCulled = false; tail.children[0].frustumCulled = false; trunk.add(tail);
const ringM = Array.from({ length: RINGS + 2 }, () => new THREE.Matrix4()), ringC = Array.from({ length: RINGS + 2 }, () => new THREE.Vector3());
const mz = new THREE.Matrix4(), my = new THREE.Matrix4(), tv = new THREE.Vector3(), tn = new THREE.Vector3();
const tailC = new THREE.Vector3();
function bendTail(t, lift = 0) {
  const step = TL / RINGS; const c = tailC.set(0, 0, 0);
  for (let i = 0; i <= RINGS + 1; i++) {
    const u = Math.min(i / RINGS, 1);
    // tangent transition from rear pelvis, sloping smoothly and leveling near tip clear of ground
    const pitch = 0.18 + 0.25 * Math.sin(u * Math.PI * 0.74) - 0.18 * lift * u + (reduceMotion ? 0 : 0.03 * Math.sin(t * 0.9 - u * 2.5) * u);
    const yaw = reduceMotion ? 0 : 0.22 * Math.sin(t * 1.1 - u * 2.6) * u * u;
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

MERGE_CALLS = """legGroups.forEach(g => mergeSkin(g));
mergeSkin(trunk, [tail]);
mergeSkin(head, [jawPivot, ...excludeHead]);
mergeSkin(jawInner);
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
function chargeCurve(t) {          // lunge in metres, dip 0..1, snort 0..1
  if (t < 0 || t > 1.6) return { lunge: 0, dip: 0, snort: 0 };
  if (t < 0.30) { const u = ease(t / 0.30); return { lunge: -0.22 * u, dip: -0.45 * u, snort: Math.sin(u * Math.PI) }; }
  if (t < 0.70) { const u = backOut((t - 0.30) / 0.40); return { lunge: -0.22 + 0.82 * u, dip: -0.45 + 1.45 * u, snort: 0 }; }
  if (t < 1.12) return { lunge: 0.60, dip: 1 - 0.04 * Math.abs(Math.sin((t - 0.70) * 28)), snort: 0 };
  const u = ease((t - 1.12) / 0.48); return { lunge: 0.60 * (1 - u), dip: 1 - u, snort: 0 };
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
  camera.position.z = HOME.pos.z * Math.max(1, 1.35 / (w / h));
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize); resize();

const headBase = headPivot.rotation.z;
let frame = 0, acc = 0, lastNow = performance.now();
function adapt() {
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
  const { lunge, dip, snort } = chargeCurve(t - roarStart);
  if (!reduceMotion) {
    trunk.scale.set(1, 1 + 0.012 * Math.sin(t * 2.0), 1 + 0.008 * Math.sin(t * 2.0));
    bendTail(t, Math.max(0, dip));
    headPivot.rotation.y = 0.06 * Math.sin(t * 0.35);
    if (t > nextBlink) { const k = t - nextBlink; const s = k < 0.07 ? 1 - k / 0.07 : k < 0.16 ? (k - 0.07) / 0.09 : 1; eyes.forEach(e => e.scale.y = Math.max(0.08, s)); if (k > 0.16) nextBlink = t + 3 + Math.random() * 3; }
  }
  rex.position.x = lunge;
  hips.position.y = BASE_HIP_Y - 0.045 * Math.max(0, dip);         // weighted crouch into charge
  trunk.rotation.z = -0.075 * dip;
  headPivot.rotation.z = headBase - 0.28 * dip;
  jawPivot.rotation.z = -0.18 * snort;
  // subtle braced limb angles keep all four soles planted cleanly on the ground
  legSockets.frontNear.rotation.z = 0.075 * dip;
  legSockets.frontFar.rotation.z = -0.06 * dip;
  legSockets.hindNear.rotation.z = -0.065 * dip;
  legSockets.hindFar.rotation.z = 0.055 * dip;
  controls.update();
  renderer.render(scene, camera);
}
function start() { renderer.setAnimationLoop(loop); document.getElementById('status').remove(); }
renderer.shadowMap.needsUpdate = true;
(renderer.compileAsync ? renderer.compileAsync(scene, camera) : Promise.resolve()).catch(() => {}).then(start);
</script>
</body>
</html>
"""

merge_def = "\n".join(lines[a_merge_calls - 10:a_merge_calls])
assert "function mergeSkin" in paint_part or "function mergeSkin" in merge_def
out = head_part + "\n" + ANIMAL + "\n" + paint_part + "\n" + MERGE_CALLS + "\n" + SCENERY + "\n" + MOTION
pathlib.Path(ROOT + "/3d/triceratops-3d.html").write_text(out, encoding="utf-8")
print("ok", len(out))

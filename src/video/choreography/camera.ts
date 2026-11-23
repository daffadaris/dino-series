import * as THREE from 'three';
import { interpolate } from 'remotion';

type V3 = [number, number, number];
export type CameraKey = {
  f: number;
  pos: V3;
  target: V3;
  fov: number;
  ease?: (t: number) => number;
  /** Optional quadratic Bezier control-point offset [dx, dy, dz] added to segment midpoint so glides arc smoothly around actors. */
  arc?: V3;
  /** Rick's Clips rapid-cut flag: hold previous angle until `f - 1`, then snap cleanly to this shot on frame `f`. */
  cut?: boolean;
};
export type CameraShake = { at: number; strength: number; dur?: number };

function quadBezier(a: V3, b: V3, arc: V3 | undefined, t: number): THREE.Vector3 {
  const va = new THREE.Vector3(...a);
  const vb = new THREE.Vector3(...b);
  if (!arc) return va.lerp(vb, t);
  const mid = va.clone().add(vb).multiplyScalar(0.5).add(new THREE.Vector3(...arc));
  const u = 1 - t;
  return va.multiplyScalar(u * u).add(mid.multiplyScalar(2 * u * t)).add(vb.multiplyScalar(t * t));
}

/** Pure function of the frame: supports both Rick's Clips snap cuts and curved 3D glides/orbits + handheld float + impact shake. */
export function evaluateCamera(keys: CameraKey[], frame: number, fps: number, shakes: CameraShake[] = []) {
  const i = keys.findIndex((k) => k.f > frame);
  const [a, b] = i === -1 ? [keys[keys.length - 1], keys[keys.length - 1]] : [keys[i - 1], keys[i]];
  // If the upcoming key is marked `cut`, hold `a` cleanly until frame `b.f` (where `b` becomes `a` and snaps instantly!).
  const t = a === b || b.cut
    ? 0
    : interpolate(frame, [a.f, b.f], [0, 1], { easing: b.ease, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const s = frame / fps;
  const driftX = Math.sin(s * 0.95) * 0.085 + Math.sin(s * 2.1 + 1.1) * 0.028;
  const driftY = Math.cos(s * 0.72) * 0.075 + Math.sin(s * 1.55 + 0.4) * 0.022;

  let shakeX = 0, shakeY = 0;
  for (const sh of shakes) {
    const local = frame - sh.at;
    const dur = sh.dur ?? 12;
    if (local >= 0 && local < dur) {
      const decay = Math.exp(-(local / dur) * 3.8);
      shakeX += Math.sin(local * 2.9 + sh.at) * sh.strength * decay;
      shakeY += Math.cos(local * 3.7 + sh.at * 1.3) * sh.strength * 0.85 * decay;
    }
  }

  const position = quadBezier(a.pos, b.pos, b.cut ? undefined : b.arc, t).add(new THREE.Vector3(driftX + shakeX, driftY + shakeY, 0));
  const target = new THREE.Vector3(...a.target)
    .lerp(new THREE.Vector3(...b.target), t)
    .add(new THREE.Vector3(shakeX * 0.35, shakeY * 0.35, 0));

  return { position, target, fov: a.fov + (b.fov - a.fov) * t, focusDist: position.distanceTo(target) };
}

/** A camera matching evaluateCamera, for projecting 3D anchors onto the 2D overlay. */
export function makeCamera(cam: ReturnType<typeof evaluateCamera>, aspect: number) {
  const c = new THREE.PerspectiveCamera(cam.fov, aspect, 0.1, 400);
  c.position.copy(cam.position);
  c.lookAt(cam.target);
  c.updateMatrixWorld();
  return c;
}

// TikTok safe zone (ANIMATION_GUIDE.md:966): keep overlays inside x 48..860, y 230..1520.
export function projectToScreen(world: V3, camera: THREE.Camera, width = 1080, height = 1920) {
  const p = new THREE.Vector3(...world).project(camera);
  return {
    x: THREE.MathUtils.clamp((p.x * 0.5 + 0.5) * width, 72, 840),
    y: THREE.MathUtils.clamp((-p.y * 0.5 + 0.5) * height, 240, 1480),
    visible: p.z < 1,
  };
}

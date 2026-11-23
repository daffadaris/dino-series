import React, { useMemo } from 'react';
import * as THREE from 'three';
import { useLoader } from '@react-three/fiber';
import { Easing, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';

// Sprites from src/sprites.py: 1600x896 transparent PNGs of the 1000x560 big-head explainer SVGs.
// Dinosaurs scale by horizontal length (`span`); human stickmen scale by standing height (`top..ground`).
type SpeciesCfg = {
  length?: number;
  span?: readonly [number, number];
  height?: number;
  top?: number;
  cx?: number;
  ground: number;
  stride: number;
  poses: readonly string[];
};

const SPECIES: Record<'trex' | 'triceratops' | 'paleontologist' | 'skeptic', SpeciesCfg> = {
  trex: {
    length: 12, span: [31.5, 916.3], ground: 514, stride: 1.9,
    poses: ['default', 'blink', 'mouth', 'happy', 'angry', 'sad', 'surprised', 'scared', 'smug', 'walk', 'roaring'],
  },
  triceratops: {
    length: 8.5, span: [142.1, 955.8], ground: 514, stride: 1.4,
    poses: ['default', 'blink', 'mouth', 'happy', 'angry', 'sad', 'surprised', 'scared', 'smug', 'walk', 'charging'],
  },
  paleontologist: {
    height: 2.25, top: 142, cx: 504, ground: 514, stride: 0.72,
    poses: ['default', 'blink', 'mouth', 'happy', 'angry', 'sad', 'surprised', 'scared', 'smug', 'walk', 'eureka'],
  },
  skeptic: {
    height: 2.2, top: 140, cx: 504, ground: 514, stride: 0.72,
    poses: ['default', 'blink', 'mouth', 'happy', 'angry', 'sad', 'surprised', 'scared', 'smug', 'walk', 'point'],
  },
};
const SVG_W = 1000, SVG_H = 560;

export type Species = keyof typeof SPECIES;
export type MoveKey = { f: number; pos: [number, number, number]; ease?: (t: number) => number };
export type ActionCue = {
  at: number;
  kind: 'roar' | 'lunge' | 'stomp' | 'recoil' | 'hop' | 'pivot';
  dur?: number;
};

export type ActorSpec = {
  id: string;
  species: Species;
  position: [number, number, number];
  /** Optional world-space motion keyframes; overrides static `position` when provided. */
  moves?: MoveKey[];
  /** Auto-drive stride-locked walk/default sprite toggle + bounce whenever moving along `moves`. */
  autoWalk?: boolean;
  poses: [number, string][]; // [fromFrame, pose], ascending
  /** Frame ranges [start, end] where this character is actively speaking (triggers crisp mouth-flapping & talk bounce). */
  speakRanges?: [number, number][];
  /** Short physical acting beats (squash/stretch, tilt, lunge, recoil, hop). */
  actions?: ActionCue[];
  visible: [number, number];
  /** Frame windows [start, end] inside `visible` where the actor is off-stage (keeps it out of other shots). */
  hidden?: [number, number][];
  flipX?: boolean;
  phase?: number;
};

function evalPosition(base: [number, number, number], moves: MoveKey[] | undefined, frame: number) {
  if (!moves || moves.length === 0) return { pos: base, speed: 0, distTraveled: 0 };

  const sample = (fr: number): [number, number, number] => {
    if (fr <= moves[0].f) return moves[0].pos;
    const i = moves.findIndex((m) => m.f > fr);
    if (i === -1) return moves[moves.length - 1].pos;
    const a = moves[i - 1], b = moves[i];
    const t = interpolate(fr, [a.f, b.f], [0, 1], {
      easing: b.ease ?? Easing.inOut(Easing.cubic),
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
    return [
      a.pos[0] + (b.pos[0] - a.pos[0]) * t,
      a.pos[1] + (b.pos[1] - a.pos[1]) * t,
      a.pos[2] + (b.pos[2] - a.pos[2]) * t,
    ];
  };

  const pos = sample(frame);
  const prev = sample(Math.max(0, frame - 1));
  const speed = Math.hypot(pos[0] - prev[0], pos[2] - prev[2]);

  let distTraveled = 0;
  for (let idx = 1; idx < moves.length; idx++) {
    const a = moves[idx - 1], b = moves[idx];
    if (frame <= a.f) break;
    const segLen = Math.hypot(b.pos[0] - a.pos[0], b.pos[2] - a.pos[2]);
    if (frame >= b.f) {
      distTraveled += segLen;
    } else {
      const t = interpolate(frame, [a.f, b.f], [0, 1], {
        easing: b.ease ?? Easing.inOut(Easing.cubic),
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      });
      distTraveled += segLen * t;
      break;
    }
  }
  return { pos, speed, distTraveled };
}

function evalActions(actions: ActionCue[] | undefined, frame: number, fps: number, facing: number, scaleFactor: number) {
  let dx = 0, dy = 0, rotZ = 0, sx = 0, sy = 0;
  if (!actions) return { dx, dy, rotZ, sx, sy };

  for (const act of actions) {
    const dur = act.dur ?? 20;
    const local = frame - act.at;
    if (local < 0 || local > dur) continue;
    const u = local / dur;
    const env = Math.sin(u * Math.PI);
    const snap = Math.sin(Math.min(1, u * 2.2) * Math.PI) * Math.exp(-u * 2.4);

    if (act.kind === 'roar') {
      const rear = u < 0.25 ? Math.sin((u / 0.25) * Math.PI) : 0;
      const thrust = u >= 0.2 ? Math.sin(((u - 0.2) / 0.8) * Math.PI) : 0;
      const tremor = u > 0.25 && u < 0.85 ? Math.sin(local * 1.9) * 0.015 : 0;
      dx += facing * (thrust * 0.55 - rear * 0.25) * scaleFactor;
      dy += (thrust * 0.18 + Math.abs(tremor) * 3) * scaleFactor;
      rotZ += facing * (-thrust * 0.07 + rear * 0.05) + tremor;
      sy += thrust * 0.06 - rear * 0.03;
      sx += -thrust * 0.04 + rear * 0.025;
    } else if (act.kind === 'lunge') {
      dx += facing * snap * 0.95 * scaleFactor;
      dy += env * 0.16 * scaleFactor;
      rotZ += facing * (-snap * 0.085);
      sx += snap * 0.055;
      sy += -snap * 0.04;
    } else if (act.kind === 'stomp') {
      const lift = u < 0.35 ? Math.sin((u / 0.35) * Math.PI) : 0;
      const impact = u >= 0.35 ? Math.sin(((u - 0.35) / 0.65) * Math.PI) * Math.exp(-(u - 0.35) * 4) : 0;
      dy += lift * 0.38 * scaleFactor;
      rotZ += facing * (-lift * 0.05 + impact * 0.035);
      sy += lift * 0.055 - impact * 0.095;
      sx += -lift * 0.035 + impact * 0.08;
    } else if (act.kind === 'recoil') {
      const pop = spring({ frame: local, fps, config: { damping: 10, stiffness: 220, mass: 0.7 } });
      const fade = 1 - u;
      dx += -facing * Math.sin(u * Math.PI) * 0.85 * scaleFactor;
      dy += Math.sin(Math.min(1, u * 1.8) * Math.PI) * 0.34 * scaleFactor;
      rotZ += facing * (pop * fade * 0.095);
      sy += snap * 0.075;
      sx += -snap * 0.05;
    } else if (act.kind === 'hop') {
      dy += Math.sin(u * Math.PI) * 0.44 * scaleFactor;
      sy += (u < 0.2 || u > 0.8 ? -0.055 : 0.06) * env;
      sx += (u < 0.2 || u > 0.8 ? 0.05 : -0.04) * env;
      rotZ += facing * Math.sin(u * Math.PI * 2) * 0.045;
    } else if (act.kind === 'pivot') {
      dx += facing * Math.sin(u * Math.PI) * 0.65 * scaleFactor;
      dy += Math.sin(Math.min(1, u * 2) * Math.PI) * 0.22 * scaleFactor;
      rotZ += facing * (-Math.sin(u * Math.PI) * 0.08);
      sx += snap * 0.065;
      sy += -snap * 0.045;
    }
  }
  return { dx, dy, rotZ, sx, sy };
}

export const CutoutActor: React.FC<ActorSpec & { camPos: THREE.Vector3 }> = ({
  id, species, position, moves, autoWalk = true, poses, speakRanges, actions, visible, hidden, flipX, phase = 0, camPos,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sp = SPECIES[species];
  const textures = useLoader(THREE.TextureLoader, sp.poses.map((p) => staticFile(`sprites/${species}/${p}.png`)));
  useMemo(() => textures.forEach((t) => { t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; }), [textures]);

  const { pos: basePos, speed, distTraveled } = evalPosition(position, moves, frame);
  const isWalking = autoWalk && speed > 0.01;
  const isSpeaking = Boolean(speakRanges?.some(([a, b]) => frame >= a && frame <= b));

  const [swapAt, rawBase] = [...poses].reverse().find(([f]) => frame >= f) ?? poses[0];

  const stridePhase = (distTraveled / sp.stride) * Math.PI * 2;
  const walkSpriteOn = isWalking && Math.sin(stridePhase) > 0;

  // Seeded blink every 2.2-3.8 s while holding a neutral pose.
  let blink = false;
  for (let t = 0, k = 0; t <= frame; t += Math.round((2.2 + 1.6 * random(`${id}-blink-${k}`)) * fps), k++) {
    if (frame - t < 4 && t > 0) blink = true;
  }

  const heroPose = rawBase === 'roaring' || rawBase === 'charging' || rawBase === 'eureka' || rawBase === 'point';
  let pose = rawBase;
  if (isWalking && (rawBase === 'default' || rawBase === 'walk')) {
    pose = walkSpriteOn ? 'walk' : 'default';
  } else if (isSpeaking && !heroPose && Math.floor(frame / 4) % 2 === 0) {
    pose = 'mouth';
  } else if ((rawBase === 'default' || rawBase === 'smug') && blink) {
    pose = 'blink';
  }

  const idx = sp.poses.indexOf(pose);
  const tex = textures[idx >= 0 ? idx : 0];
  const depthMaterial = useMemo(
    () => new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: tex, alphaTest: 0.5 }),
    [tex]
  );

  // Meters-per-SVG-unit: horizontal length for dinosaurs, vertical height for human stickmen.
  const isHuman = Boolean(sp.height);
  const mpu = sp.height
    ? sp.height / (sp.ground - (sp.top ?? 140))
    : (sp.length ?? 10) / ((sp.span?.[1] ?? 900) - (sp.span?.[0] ?? 100));
  const w = SVG_W * mpu, h = SVG_H * mpu;
  const cx = sp.cx ?? ((sp.span?.[0] ?? 0) + (sp.span?.[1] ?? SVG_W)) / 2;
  const actionScale = isHuman ? 0.52 : 1.0;

  const elapsed = frame / fps;
  const breath = Math.sin(elapsed * 2.8 + phase) * 0.025;
  const idleSway = Math.sin(elapsed * 1.25 + phase * 1.7) * 0.02;

  // Snappy Rick's Clips talk-bounce when speaking!
  const talkBounce = isSpeaking ? Math.abs(Math.sin(elapsed * 11 + phase)) * 0.045 : 0;
  const talkTilt = isSpeaking ? Math.sin(elapsed * 6.5 + phase) * 0.028 : 0;

  // Elastic spring squash/stretch on pose swaps.
  const since = frame - swapAt;
  let swapSy = 0, swapSx = 0, swapRot = 0;
  if (swapAt > 0 && since >= 0 && since < 12) {
    const s = spring({ frame: since, fps, config: { damping: 9, stiffness: 280, mass: 0.5 } });
    const decay = 1 - since / 12;
    const punch = (1 - Math.abs(1 - s)) * decay;
    swapSy = punch * 0.085;
    swapSx = -punch * 0.06;
    swapRot = (flipX ? 1 : -1) * Math.sin((since / 12) * Math.PI) * 0.038;
  }

  const walkAmp = Math.min(1, speed / (isHuman ? 0.035 : 0.06));
  const walkBobY = isWalking ? Math.abs(Math.sin(stridePhase)) * (isHuman ? 0.14 : 0.24) * walkAmp : 0;
  const walkRockZ = isWalking ? Math.cos(stridePhase) * 0.05 * walkAmp : 0;
  const walkSquash = isWalking ? (Math.abs(Math.sin(stridePhase)) - 0.5) * 0.05 * walkAmp : 0;

  const facing = flipX ? -1 : 1;
  const act = evalActions(actions, frame, fps, facing, actionScale);

  const sy = 1 + breath + talkBounce + swapSy + walkSquash + act.sy;
  const sx = 1 - breath * 0.45 - talkBounce * 0.5 + swapSx - walkSquash * 0.5 + act.sx;
  const rotZ = idleSway + talkTilt + swapRot + walkRockZ + act.rotZ;

  if (frame < visible[0] || frame > visible[1]) return null;
  if (hidden?.some(([a, b]) => frame >= a && frame <= b)) return null;

  const worldX = basePos[0] + act.dx;
  const worldY = basePos[1] + walkBobY + act.dy;
  const worldZ = basePos[2];
  const rotY = Math.atan2(camPos.x - worldX, camPos.z - worldZ);

  return (
    <group position={[worldX, worldY, worldZ]} rotation={[0, rotY, 0]}>
      <group rotation={[0, 0, rotZ]} scale={[flipX ? -sx : sx, sy, 1]}>
        <mesh position={[(SVG_W / 2 - cx) * mpu, (sp.ground - SVG_H / 2) * mpu, 0]} castShadow receiveShadow customDepthMaterial={depthMaterial}>
          <planeGeometry args={[w, h]} />
          <meshStandardMaterial map={tex} alphaTest={0.5} side={THREE.DoubleSide} roughness={0.72} metalness={0.04} />
        </mesh>
      </group>
    </group>
  );
};

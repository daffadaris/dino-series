import React, { useMemo } from 'react';
import * as THREE from 'three';
import { useLoader } from '@react-three/fiber';
import { Easing, interpolate, staticFile, useCurrentFrame } from 'remotion';

// Fossil props from src/props.py: transparent PNGs drawn at 2x their SVG size (w x h SVG px).
export type PropKey = { f: number; pos: [number, number, number]; rot?: number; ease?: (t: number) => number };
export type PropSpec = {
  id: string;
  file: string;
  size: [number, number];
  /** metres per SVG px */
  mpp: number;
  /** SVG px placed at `pos` and used as the spin pivot (skull and neck share one, so they stay joined) */
  anchor: [number, number];
  keys: PropKey[];
  visible: [number, number];
  /** pulsing callout rings at SVG px, drawn on top of the prop */
  rings?: { px: [number, number]; r: number; at: number; until: number }[];
};

function sample(keys: PropKey[], frame: number) {
  const i = keys.findIndex((k) => k.f > frame);
  if (i === 0) return { pos: keys[0].pos, rot: keys[0].rot ?? 0 };
  if (i === -1) { const k = keys[keys.length - 1]; return { pos: k.pos, rot: k.rot ?? 0 }; }
  const a = keys[i - 1], b = keys[i];
  const t = interpolate(frame, [a.f, b.f], [0, 1], { easing: b.ease ?? Easing.inOut(Easing.cubic) });
  return {
    pos: a.pos.map((v, k) => v + (b.pos[k] - v) * t) as [number, number, number],
    rot: (a.rot ?? 0) + ((b.rot ?? 0) - (a.rot ?? 0)) * t,
  };
}

const RING = '#ffad5c';

export const Prop: React.FC<PropSpec & { camPos: THREE.Vector3 }> = ({ file, size, mpp, anchor, keys, visible, rings, camPos }) => {
  const frame = useCurrentFrame();
  const tex = useLoader(THREE.TextureLoader, staticFile(`sprites/props/${file}.png`));
  useMemo(() => { tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; }, [tex]);
  const depth = useMemo(() => new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: tex, alphaTest: 0.5 }), [tex]);
  if (frame < visible[0] || frame > visible[1]) return null;

  const { pos, rot } = sample(keys, frame);
  const [w, h] = [size[0] * mpp, size[1] * mpp];
  const local = (px: [number, number]): [number, number, number] => [(px[0] - anchor[0]) * mpp, (anchor[1] - px[1]) * mpp, 0];
  const centre = local([size[0] / 2, size[1] / 2]);

  return (
    <group position={pos} rotation={[0, Math.atan2(camPos.x - pos[0], camPos.z - pos[2]), 0]}>
      <group rotation={[0, 0, rot]}>
        <mesh position={centre} castShadow receiveShadow customDepthMaterial={depth}>
          <planeGeometry args={[w, h]} />
          <meshStandardMaterial map={tex} alphaTest={0.5} side={THREE.DoubleSide} roughness={0.8} />
        </mesh>
        {rings?.filter((r) => frame >= r.at && frame <= r.until).map((r, i) => {
          const pulse = 1 + 0.12 * Math.sin((frame - r.at) * 0.35);
          const grow = interpolate(frame - r.at, [0, 6], [0.3, 1], { extrapolateRight: 'clamp', easing: Easing.out(Easing.back(2)) });
          const fade = interpolate(frame, [r.until - 5, r.until], [1, 0], { extrapolateLeft: 'clamp' });
          const [x, y] = local(r.px);
          return (
            <mesh key={i} position={[x, y, 0.01]} scale={r.r * mpp * pulse * grow} renderOrder={10}>
              <ringGeometry args={[1, 1.22, 48]} />
              <meshBasicMaterial color={RING} transparent opacity={fade} depthTest={false} toneMapped={false} />
            </mesh>
          );
        })}
      </group>
    </group>
  );
};

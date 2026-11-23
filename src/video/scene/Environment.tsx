import React, { useMemo } from 'react';
import * as THREE from 'three';
import { useLoader } from '@react-three/fiber';
import { random, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import type { Lighting } from './LightingRig';

// Seeded painterly canvas textures (ANIMATION_GUIDE.md:311): brush dabs + lifted-charcoal cracks, never #000.
function painterly(seed: string, base: string, tones: string[], dabs: number, cracks: number) {
  const size = 512;
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  let k = 0;
  const r = () => random(`${seed}-${k++}`);
  ctx.fillStyle = base;
  ctx.fillRect(0, 0, size, size);
  for (let i = 0; i < dabs; i++) {
    ctx.fillStyle = tones[Math.floor(r() * tones.length)];
    ctx.globalAlpha = 0.18 + r() * 0.22;
    ctx.beginPath();
    ctx.ellipse(r() * size, r() * size, 10 + r() * 34, 5 + r() * 14, r() * Math.PI, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalAlpha = 0.4;
  ctx.strokeStyle = '#1d1e30';
  ctx.lineWidth = 2.2;
  for (let i = 0; i < cracks; i++) {
    let x = r() * size, y = r() * size;
    ctx.beginPath();
    ctx.moveTo(x, y);
    for (let s = 0; s < 4; s++) ctx.lineTo((x += (r() - 0.5) * 44), (y += (r() - 0.5) * 28));
    ctx.stroke();
  }
  const tex = new THREE.CanvasTexture(canvas);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

// Hell Creek cards from src/sprites.py (900x1200 PNGs). [drawn height in metres, content top px, ground px], measured
// from each PNG's alpha, so the plane is sized by what is drawn and its ground line sits on y = 0.
const CARD_H = {
  'hell-creek-ferns': [1.4, 946, 1153], 'hell-creek-fan-palm': [6, 479, 1142], 'hell-creek-broadleaf-tree': [11, 543, 1142],
  'hell-creek-dawn-redwood': [14, 571, 1141], 'any-habitat-boulder': [1.8, 952, 1142],
} as const;
type Card = keyof typeof CARD_H;
type Placed = [Card, number, number]; // card, x, z

// Hand-placed set dressing around the face-off clearing (x ~0) and the fossil spot (x 12-17), plus foreground ferns on the camera glide paths for DoF parallax.
const SET: Placed[] = [
  ['hell-creek-dawn-redwood', -22, -14], ['hell-creek-broadleaf-tree', -12, -12], ['hell-creek-fan-palm', -18, -6],
  ['hell-creek-ferns', -12.5, 1.8], ['hell-creek-ferns', -7.2, 2.2], ['any-habitat-boulder', -9, -4],
  ['hell-creek-ferns', -6, 9.5], ['hell-creek-ferns', -3.6, 8.6], ['hell-creek-fan-palm', -7, 11],
  ['hell-creek-broadleaf-tree', -2, -15], ['hell-creek-dawn-redwood', 8, -16], ['hell-creek-fan-palm', 11, -8],
  ['hell-creek-ferns', 3.6, 3.2], ['hell-creek-ferns', 9.5, 2.4], ['any-habitat-boulder', -13, -8],
  ['hell-creek-dawn-redwood', 27, -12], ['hell-creek-fan-palm', 15.5, -10], ['hell-creek-ferns', 18.4, 4.6], ['hell-creek-ferns', 25, 1.5],
  ['any-habitat-boulder', 29, -3], ['hell-creek-broadleaf-tree', 34, -6],
  ['hell-creek-broadleaf-tree', -16, 15], ['hell-creek-fan-palm', 13, 12], ['hell-creek-ferns', 1, 13], ['hell-creek-ferns', 6.5, 14.5],
];
const RIVER_Z = -9;

const FoliageCard: React.FC<{ tex: THREE.Texture; card: Card; x: number; z: number; camPos: THREE.Vector3; t: number }> = ({ tex, card, x, z, camPos, t }) => {
  const [m, top, ground] = CARD_H[card];
  const h = (m * 1200) / (ground - top), w = h * 0.75;
  const depth = useMemo(() => new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: tex, alphaTest: 0.5 }), [tex]);
  const sway = card === 'any-habitat-boulder' ? 0 : Math.sin(t * 1.9 + x * 0.7) * 0.045;
  return (
    <group position={[x, 0, z]} rotation={[0, Math.atan2(camPos.x - x, camPos.z - z), 0]}>
      <mesh rotation={[0, 0, sway]}>
        <mesh position={[0, h / 2 - ((1200 - ground) / 1200) * h, 0]} castShadow receiveShadow customDepthMaterial={depth}>
          <planeGeometry args={[w, h]} />
          <meshStandardMaterial map={tex} alphaTest={0.5} side={THREE.DoubleSide} roughness={0.85} />
        </mesh>
      </mesh>
    </group>
  );
};

export const Environment: React.FC<{ camPos: THREE.Vector3; focus: THREE.Vector3; light: Lighting }> = ({ camPos, focus, light }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const cards = Object.keys(CARD_H) as Card[];
  const cardTex = useLoader(THREE.TextureLoader, cards.map((c) => staticFile(`sprites/scenery/${c}.png`)));
  useMemo(() => cardTex.forEach((x) => { x.colorSpace = THREE.SRGBColorSpace; x.anisotropy = 8; }), [cardTex]);

  const ground = useMemo(() => {
    const tex = painterly('ground', '#7d7a52', ['#6a6b45', '#8f845c', '#5f6e48', '#9a8d68'], 520, 10);
    tex.repeat.set(24, 24);
    return tex;
  }, []);
  const water = useMemo(() => {
    const tex = painterly('water', '#4d7f95', ['#5f95a8', '#3f6f86', '#7fb1bd', '#4a7a8c'], 380, 0);
    tex.repeat.set(16, 2);
    return tex;
  }, []);
  const rock = useMemo(() => painterly('rock', '#8c7e74', ['#7a6d64', '#9e8f82', '#6a7459', '#b2a392'], 420, 28), []);
  water.offset.x = (t * 0.08) % 1;

  // Dust motes near the focus point, a little brighter in the late-afternoon light.
  const motes = useMemo(() => Array.from({ length: 48 }, (_, i) => [random(`mote-x-${i}`), random(`mote-y-${i}`), random(`mote-z-${i}`), random(`mote-p-${i}`)]), []);
  const moteGeo = useMemo(() => new THREE.BufferGeometry().setAttribute('position', new THREE.BufferAttribute(new Float32Array(48 * 3), 3)), []);
  const pos = moteGeo.attributes.position as THREE.BufferAttribute;
  motes.forEach(([mx, my, mz, p], i) =>
    pos.setXYZ(i, focus.x + (mx - 0.5) * 16 + Math.sin(t * 0.3 + p * 6) * 0.6, 0.4 + my * 5 + Math.sin(t * 0.5 + p * 9) * 0.3, focus.z + (mz - 0.5) * 10));
  pos.needsUpdate = true;
  const moteGlow = THREE.MathUtils.clamp((light.fogD - 0.011) / 0.001, 0.3, 0.7); // fog density: day 0.011, late afternoon 0.0115

  return (
    <>
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[240, 240]} />
        <meshStandardMaterial map={ground} roughness={0.95} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.03, RIVER_Z]} receiveShadow>
        <planeGeometry args={[240, 5]} />
        <meshStandardMaterial map={water} roughness={0.25} metalness={0.1} />
      </mesh>
      {[[-6.5, -6.5, 1.1], [14, -5.5, 1.4], [21, 4.5, 0.8], [-5.5, 3.2, 0.7]].map(([x, z, s], i) => (
        <mesh key={i} position={[x, s * 0.45, z]} rotation={[0.3 * i, 0.7 * i, 0]} scale={[s * 1.3, s * 0.8, s]} castShadow receiveShadow>
          <dodecahedronGeometry args={[1, 0]} />
          <meshStandardMaterial map={rock} roughness={0.9} flatShading />
        </mesh>
      ))}
      {SET.map(([card, x, z], i) => (
        <FoliageCard key={i} tex={cardTex[cards.indexOf(card)]} card={card} x={x} z={z} camPos={camPos} t={t} />
      ))}
      <points geometry={moteGeo}>
        <pointsMaterial color="#ffd98a" size={0.07} transparent opacity={moteGlow} depthWrite={false} />
      </points>
    </>
  );
};

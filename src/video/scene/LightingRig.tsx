import React, { useMemo } from 'react';
import * as THREE from 'three';
import { Easing, interpolate } from 'remotion';

// Daylight -> warm late afternoon (Ep01 payoff). Values are display-space (the ink pass applies ACES + sRGB).
const MOODS = {
  daylight: { key: '#ffe2a8', keyI: 2.15, sky: '#a8d5ff', ground: '#475c96', hemiI: 0.95, rim: '#ffd394', rimI: 0.65,
    fog: '#d8e5ea', fogD: 0.011, ink: '#1d1e30', skyTop: '#5ea8e6', skyHorizon: '#f5dfb8' },
  lateAfternoon: { key: '#ffd9a6', keyI: 2.15, sky: '#ffe6c8', ground: '#56587a', hemiI: 0.95, rim: '#ffdca0', rimI: 0.9,
    fog: '#e6dccd', fogD: 0.0115, ink: '#221c2a', skyTop: '#76a8dc', skyHorizon: '#ffdcae' },
};
type Mood = typeof MOODS.daylight;
export type Lighting = { [K in keyof Mood]: Mood[K] extends string ? THREE.Color : number };

export function evaluateLighting(frame: number, late: [number, number]): Lighting {
  const t = interpolate(frame, late, [0, 1], { easing: Easing.inOut(Easing.cubic), extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const from = MOODS.daylight, to = MOODS.lateAfternoon;
  return Object.fromEntries(Object.keys(from).map((k) => {
    const a = from[k as keyof Mood], b = to[k as keyof Mood];
    return [k, typeof a === 'number' ? a + ((b as number) - a) * t : new THREE.Color(a).lerp(new THREE.Color(b as string), t)];
  })) as Lighting;
}

const SKY_FRAG = /* glsl */ `
  uniform vec3 uTop; uniform vec3 uHorizon; varying vec3 vDir;
  void main() { gl_FragColor = vec4(mix(uHorizon, uTop, smoothstep(-0.05, 0.55, normalize(vDir).y)), 1.0); }`;
const SKY_VERT = /* glsl */ `
  varying vec3 vDir;
  void main() { vDir = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;

/** Lights, fog and sky for one frame. The key light and its shadow box follow the camera target. */
export const LightingRig: React.FC<{ light: Lighting; focus: THREE.Vector3 }> = ({ light, focus }) => {
  const sky = useMemo(() => new THREE.ShaderMaterial({
    uniforms: { uTop: { value: new THREE.Color() }, uHorizon: { value: new THREE.Color() } },
    vertexShader: SKY_VERT, fragmentShader: SKY_FRAG, side: THREE.BackSide, depthWrite: false, fog: false,
  }), []);
  sky.uniforms.uTop.value.copy(light.skyTop);
  sky.uniforms.uHorizon.value.copy(light.skyHorizon);
  const keyTarget = useMemo(() => new THREE.Object3D(), []);
  keyTarget.position.copy(focus);
  keyTarget.updateMatrixWorld();

  return (
    <>
      <fogExp2 attach="fog" args={['#d8e5ea', 0.011]} color={light.fog} density={light.fogD} />
      <mesh material={sky} renderOrder={-1}>
        <sphereGeometry args={[300, 32, 16]} />
      </mesh>
      <hemisphereLight color={light.sky} groundColor={light.ground} intensity={light.hemiI} />
      <directionalLight
        position={[focus.x - 8, focus.y + 14, focus.z + 9]} target={keyTarget}
        color={light.key} intensity={light.keyI}
        castShadow shadow-mapSize={[2048, 2048]} shadow-bias={-0.0004}
        shadow-camera-left={-18} shadow-camera-right={18} shadow-camera-top={18} shadow-camera-bottom={-18}
        shadow-camera-near={1} shadow-camera-far={60}
      />
      {/* Rim from the side and slightly behind: flat cutouts face the camera, so a light straight from behind would miss them. */}
      <directionalLight position={[focus.x + 12, focus.y + 5, focus.z - 4]} color={light.rim} intensity={light.rimI} />
    </>
  );
};

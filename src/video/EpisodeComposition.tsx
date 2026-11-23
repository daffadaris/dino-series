import React, { useMemo } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { ThreeCanvas } from '@remotion/three';
import { AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { evaluateCamera, makeCamera } from './choreography/camera';
import { ACTORS, BADGES, BED, CAMERA, CAMERA_SHAKES, GLINT, LIGHTING, PROPS, SFX, VO_END, VO_START, WORDS } from './choreography/ep01';
import { CutoutActor } from './scene/CutoutActor';
import { Environment } from './scene/Environment';
import { Prop } from './scene/Prop';
import { LightingRig, evaluateLighting } from './scene/LightingRig';
import { PostPipeline } from './post/PostPipeline';
import { Captions, Glint, SafeZoneGuide, StatBadges, chunkWords, useSeriesFonts } from './ui/Overlay';

type Cam = ReturnType<typeof evaluateCamera>;

// Runs before the post pipeline (priority 0 < 1), so every pass sees this frame's camera.
const CameraRig: React.FC<{ cam: Cam }> = ({ cam }) => {
  useFrame(({ camera }) => {
    const c = camera as THREE.PerspectiveCamera;
    c.position.copy(cam.position);
    c.fov = cam.fov;
    c.near = 0.1;
    c.far = 400;
    c.lookAt(cam.target);
    c.updateProjectionMatrix();
  });
  return null;
};

const DUCK = 10 ** (-4 / 20); // bed sits 4 dB lower while the VO speaks (ANIMATION_GUIDE.md:150)

export const EpisodeComposition: React.FC<{ showSafeZones: boolean }> = ({ showSafeZones }) => {
  useSeriesFonts();
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const cam = evaluateCamera(CAMERA, frame, fps, CAMERA_SHAKES);
  const light = evaluateLighting(frame, LIGHTING.late);
  const overlayCam = makeCamera(cam, width / height);
  const chunks = useMemo(() => chunkWords(WORDS), []);

  return (
    <AbsoluteFill style={{ backgroundColor: '#1d1e30' }}>
      {/* No own <Suspense>: ThreeCanvas's built-in one holds the frame until textures load. */}
      <ThreeCanvas width={width} height={height} shadows camera={{ fov: cam.fov, near: 0.1, far: 400 }}>
          <CameraRig cam={cam} />
          <LightingRig light={light} focus={cam.target} />
          <Environment camPos={cam.position} focus={cam.target} light={light} />
          {ACTORS.map((a) => <CutoutActor key={a.id} {...a} camPos={cam.position} />)}
          {PROPS.map((p) => <Prop key={p.id} {...p} camPos={cam.position} />)}
          <PostPipeline focusDist={cam.focusDist} inkColor={light.ink} />
      </ThreeCanvas>

      <StatBadges badges={BADGES} camera={overlayCam} />
      <Glint at={GLINT.at} anchor={GLINT.anchor} camera={overlayCam} />
      <Captions chunks={chunks} />
      <SafeZoneGuide visible={showSafeZones} />

      <Sequence from={VO_START}>
        <Audio src={staticFile('audio/voiceover.wav')} />
      </Sequence>
      {BED.map((b, i) => (
        <Sequence key={i} from={b.from} durationInFrames={b.to - b.from + 15}>
          {/* 15-frame overlap and fades so texture swaps crossfade instead of cutting */}
          <Audio loop src={staticFile(`audio/${b.file}.wav`)}
            volume={(f) => interpolate(f, [0, 15, b.to - b.from, b.to - b.from + 15], [b.from === 0 ? 1 : 0, 1, 1, 0], { extrapolateRight: 'clamp' })
              * (b.from + f >= VO_START && b.from + f < VO_END ? DUCK : 1)} />
        </Sequence>
      ))}
      {SFX.map((s, i) => (
        <Sequence key={i} from={s.at} durationInFrames={fps * 2}>
          <Audio src={staticFile(`audio/sfx/${s.file}.wav`)} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

import React from 'react';
import { Composition } from 'remotion';
import { EpisodeComposition } from './EpisodeComposition';
import { DURATION, FPS } from './choreography/ep01';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Ep01TrexVsTriceratops"
    component={EpisodeComposition}
    durationInFrames={DURATION}
    fps={FPS}
    width={1080}
    height={1920}
    defaultProps={{ showSafeZones: false }}
  />
);

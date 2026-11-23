import React, { useEffect, useState } from 'react';
import type * as THREE from 'three';
import { AbsoluteFill, continueRender, delayRender, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { projectToScreen } from '../choreography/camera';
import type { Badge } from '../choreography/ep01';

const INK = '#1d1e30';
const FONTS = 'https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@800&family=Public+Sans:wght@700&display=block';

/** Series fonts (Big Shoulders Display titles, Public Sans text); holds frame 0 until both are ready. */
export function useSeriesFonts() {
  const [handle] = useState(() => delayRender('Loading series fonts'));
  useEffect(() => {
    const link = Object.assign(document.createElement('link'), { rel: 'stylesheet', href: FONTS });
    document.head.appendChild(link);
    link.onload = () => Promise.all([document.fonts.load('800 64px "Big Shoulders Display"'), document.fonts.load('700 64px "Public Sans"')])
      .then(() => continueRender(handle));
    link.onerror = () => continueRender(handle); // offline: fall back to system fonts rather than hang the render
  }, [handle]);
}

type Word = { word: string; startFrame: number; endFrame: number };
/** 2-4 word kinetic chunks, breaking on punctuation; the spoken word turns gold (ANIMATION_GUIDE.md:1011). */
export function chunkWords(words: Word[], max = 3) {
  const chunks: Word[][] = [[]];
  for (const w of words) {
    const cur = chunks[chunks.length - 1];
    cur.push(w);
    if (cur.length >= max || /[.,!?;]$/.test(w.word)) chunks.push([]);
  }
  return chunks.filter((c) => c.length);
}

export const Captions: React.FC<{ chunks: Word[][] }> = ({ chunks }) => {
  const frame = useCurrentFrame();
  const i = chunks.findIndex((c, k) => frame >= c[0].startFrame && frame < (chunks[k + 1]?.[0].startFrame ?? c[c.length - 1].endFrame + 12));
  if (i < 0) return null;
  const pop = interpolate(frame - chunks[i][0].startFrame, [0, 4], [0.9, 1], { extrapolateRight: 'clamp' });
  return (
    <div style={{ position: 'absolute', left: 64, top: 1260, width: 780, transform: `translateY(-50%) scale(${pop})`, textAlign: 'center',
      font: '700 70px/1.1 "Public Sans", sans-serif', color: '#FFF6E8', WebkitTextStroke: `10px ${INK}`, paintOrder: 'stroke fill',
      textShadow: `0 6px 0 ${INK}` }}>
      {chunks[i].map((w, k) => (
        <span key={k} style={{ color: frame >= w.startFrame && frame < w.endFrame ? '#FFD369' : undefined }}>{w.word} </span>
      ))}
    </div>
  );
};

export const StatBadges: React.FC<{ badges: Badge[]; camera: THREE.Camera }> = ({ badges, camera }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <>
      {badges.filter((b) => frame >= b.at && frame <= b.until).map((b) => {
        const p = projectToScreen(b.anchor, camera);
        const half = (b.text.length * 36 + 64) / 2; // approx. card half-width: keep the whole card inside x 48..860
        const x = Math.min(Math.max(p.x, 48 + half), 860 - half);
        const s = spring({ frame: frame - b.at, fps, config: { damping: 11, stiffness: 180 } });
        const out = interpolate(frame, [b.until - 6, b.until], [1, 0], { extrapolateLeft: 'clamp' });
        return (
          <div key={b.text} style={{ position: 'absolute', left: x, top: p.y, transform: `translate(-50%, -100%) scale(${s * out})`,
            transformOrigin: '50% 100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div style={{ font: '800 74px/0.92 "Big Shoulders Display", sans-serif', whiteSpace: 'nowrap',
              padding: '14px 26px 10px', color: INK, background: b.hot ? '#ffad5c' : '#FFF6E8', border: `6px solid ${INK}`,
              borderRadius: 14, boxShadow: `0 8px 0 ${INK}` }}>{b.text}</div>
            <div style={{ width: 6, height: 46, background: INK }} />
            <div style={{ width: 20, height: 20, borderRadius: 10, background: b.hot ? '#ffad5c' : '#FFF6E8', border: `5px solid ${INK}` }} />
          </div>
        );
      })}
    </>
  );
};

/** Deadpan comic glint: a four-point star that flares and spins for 14 frames. */
export const Glint: React.FC<{ at: number; anchor: [number, number, number]; camera: THREE.Camera }> = ({ at, anchor, camera }) => {
  const frame = useCurrentFrame();
  if (frame < at || frame > at + 14) return null;
  const p = projectToScreen(anchor, camera);
  const s = interpolate(frame - at, [0, 4, 14], [0, 1.15, 0]);
  return (
    <svg width={160} height={160} viewBox="-80 -80 160 160" style={{ position: 'absolute', left: p.x - 80, top: p.y - 80,
      transform: `rotate(${(frame - at) * 4}deg) scale(${s})` }}>
      <path d="M0 -76 L12 -12 L76 0 L12 12 L0 76 L-12 12 L-76 0 L-12 -12 Z" fill="#FFF6E8" stroke={INK} strokeWidth={5} />
    </svg>
  );
};

/** TikTok HUD danger zones (ANIMATION_GUIDE.md:966) for preview only. */
export const SafeZoneGuide: React.FC<{ visible?: boolean }> = ({ visible }) => {
  if (!visible) return null;
  const danger = 'rgba(255, 59, 92, 0.28)';
  return (
    <AbsoluteFill style={{ pointerEvents: 'none' }}>
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '11%', background: danger }} />
      <div style={{ position: 'absolute', top: '42%', right: 0, width: '18%', height: '39%', background: danger }} />
      <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: '19%', background: danger }} />
    </AbsoluteFill>
  );
};

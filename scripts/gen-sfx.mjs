#!/usr/bin/env node
/**
 * Step 3: seeded procedural SFX + ambient beds (48 kHz mono 16-bit WAV, no dependencies).
 * Same seed -> byte-identical files. Levels follow ANIMATION_GUIDE.md:149-150:
 * Foley peaks -10..-6 dBFS (not ducked); beds ~-24 dBFS RMS, ducked under VO in Remotion.
 *
 *   npm run gen:sfx            -> public/audio/sfx/*.wav, public/audio/bed-{day,night}.wav
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT = path.join(ROOT, 'public', 'audio');
const SR = 48000;
const TAU = Math.PI * 2;

function rng(name) {
  let h = 2166136261;
  for (const c of name) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
  return () => {
    h = (h + 0x6d2b79f5) | 0;
    let t = Math.imul(h ^ (h >>> 15), 1 | h);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const buf = (sec) => new Float32Array(Math.round(sec * SR));
const noise = (sec, r) => buf(sec).map(() => r() * 2 - 1);
const env = (t, attack, decay) => (t < attack ? t / attack : Math.exp(-(t - attack) / decay));

// RBJ biquad; f0 may be a function of sample index for sweeps.
function biquad(x, type, f0, q = 0.707) {
  const y = new Float32Array(x.length);
  let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
  for (let i = 0; i < x.length; i++) {
    const w = (TAU * (typeof f0 === 'function' ? f0(i) : f0)) / SR;
    const a = Math.sin(w) / (2 * q), c = Math.cos(w);
    const [b0, b1, b2] = type === 'lp' ? [(1 - c) / 2, 1 - c, (1 - c) / 2]
      : type === 'hp' ? [(1 + c) / 2, -(1 + c), (1 + c) / 2]
      : [a, 0, -a];
    const a0 = 1 + a;
    y[i] = (b0 * x[i] + b1 * x1 + b2 * x2 + 2 * c * y1 - (1 - a) * y2) / a0;
    x2 = x1; x1 = x[i]; y2 = y1; y1 = y[i];
  }
  return y;
}

const mix = (...parts) => {
  const out = buf(Math.max(...parts.map((p) => p.length)) / SR);
  for (const p of parts) p.forEach((v, i) => { out[i] += v; });
  return out;
};
const shape = (x, fn) => x.map((v, i) => v * fn(i / SR));
const dbToLin = (db) => 10 ** (db / 20);
const peak = (x) => x.reduce((m, v) => Math.max(m, Math.abs(v)), 0);
const rms = (x) => Math.sqrt(x.reduce((s, v) => s + v * v, 0) / x.length);
const scaleTo = (x, cur, db) => x.map((v) => (v * dbToLin(db)) / cur);

function tone(sec, freq, phase = 0) {
  let p = phase;
  return buf(sec).map((_, i) => {
    p += (TAU * (typeof freq === 'function' ? freq(i / SR) : freq)) / SR;
    return Math.sin(p);
  });
}

// --- Foley (peak dBFS from episodes/ep01-trex-vs-triceratops/script.md) ---
const SFX = {
  'paper-snap': [-8, (r) => mix(
    shape(biquad(noise(0.09, r), 'hp', 2500), (t) => env(t, 0.001, 0.012)),
    shape(biquad(noise(0.09, r), 'bp', 1200, 2), (t) => 0.5 * env(t, 0.002, 0.025)),
  )],
  'jaw-crunch': [-6, (r) => {
    const crackles = buf(0.32);
    for (let k = 0; k < 14; k++) {
      const at = Math.floor((0.01 + r() * 0.22) * SR), len = Math.floor((0.008 + r() * 0.02) * SR);
      const amp = 0.4 + r() * 0.6;
      for (let i = 0; i < len && at + i < crackles.length; i++) crackles[at + i] += (r() * 2 - 1) * amp * Math.exp(-i / (len / 3));
    }
    return mix(
      biquad(biquad(crackles, 'bp', 900, 0.8), 'hp', 200),
      shape(tone(0.32, (t) => 140 - 200 * t), (t) => 0.6 * env(t, 0.003, 0.05)),
    );
  }],
  'stomp-thud': [-7, (r) => mix(
    shape(tone(0.6, (t) => 42 + 48 * Math.exp(-t / 0.05)), (t) => env(t, 0.004, 0.16)),
    shape(biquad(noise(0.6, r), 'lp', 400), (t) => 0.5 * env(t, 0.002, 0.04)),
  )],
  shing: [-9, (r) => {
    const partials = [2100, 3380, 5230, 7890].map((f, k) =>
      shape(tone(0.9, (t) => f * (1 + 0.002 * Math.sin(TAU * 6 * t)), r() * TAU), (t) => env(t, 0.004, 0.25 - k * 0.04) / (k + 1)));
    const scrape = shape(biquad(noise(0.9, r), 'bp', (i) => 3000 + 5000 * Math.min(1, i / SR / 0.12), 3), (t) => (t < 0.12 ? 0.4 * Math.sin((Math.PI * t) / 0.12) : 0));
    return mix(scrape, ...partials);
  }],
  whoosh: [-10, (r) => {
    const dur = 0.5;
    const sweep = (i) => { const t = i / SR / dur; return 400 + 2200 * Math.sin(Math.PI * Math.min(1, t)) ** 2; };
    return shape(biquad(noise(dur, r), 'bp', sweep, 1.2), (t) => Math.sin(Math.PI * Math.min(1, t / dur)) ** 2);
  }],
  pop: [-8, (r) => mix(
    shape(tone(0.15, (t) => 200 + 700 * Math.exp(-t / 0.012)), (t) => env(t, 0.001, 0.035)),
    shape(biquad(noise(0.15, r), 'hp', 3000), (t) => 0.3 * env(t, 0.0005, 0.003)),
  )],
};

// --- Ambient beds: seamless 16 s loops (every tone has a whole number of cycles in LOOP). ---
const LOOP = 16, XFADE = 2;
function bed(r, drones, noiseLp, lfoHz) {
  const sec = LOOP + XFADE;
  const lfo = (t) => 0.75 + 0.25 * Math.sin(TAU * lfoHz * t);
  const air = shape(biquad(biquad(noise(sec, r), 'lp', noiseLp), 'hp', 40), lfo);
  const body = mix(...drones.map(([f, a]) => shape(tone(sec, f, r() * TAU), (t) => a * lfo(t + 2))));
  const raw = mix(air, body);
  const n = LOOP * SR, x = XFADE * SR;
  // Equal-power crossfade of the overhang into the head so the loop point is seamless.
  return raw.subarray(0, n).map((v, i) => (i < x ? v * Math.sin((Math.PI / 2) * (i / x)) + raw[n + i] * Math.cos((Math.PI / 2) * (i / x)) : v));
}
const BEDS = {
  // Warm daylight: open fifth on A, brighter air.
  'bed-day': (r) => bed(r, [[55, 0.5], [82.5, 0.3], [110, 0.15]], 700, 0.125),
  // Night Blue pivot: lower, darker air, beating 220/223 Hz tension pair.
  'bed-night': (r) => bed(r, [[41.25, 0.55], [61.875, 0.3], [220, 0.05], [223, 0.05]], 320, 0.0625),
};
const BED_RMS_DB = -24;

function writeWav(file, samples) {
  const data = Buffer.alloc(samples.length * 2);
  samples.forEach((v, i) => data.writeInt16LE(Math.round(Math.max(-1, Math.min(1, v)) * 32767), i * 2));
  const h = Buffer.alloc(44);
  h.write('RIFF', 0); h.writeUInt32LE(36 + data.length, 4); h.write('WAVEfmt ', 8);
  h.writeUInt32LE(16, 16); h.writeUInt16LE(1, 20); h.writeUInt16LE(1, 22);
  h.writeUInt32LE(SR, 24); h.writeUInt32LE(SR * 2, 28); h.writeUInt16LE(2, 32); h.writeUInt16LE(16, 34);
  h.write('data', 36); h.writeUInt32LE(data.length, 40);
  fs.writeFileSync(file, Buffer.concat([h, data]));
}

const fadeOut = (x) => { const n = Math.min(x.length, SR * 0.005); for (let i = 0; i < n; i++) x[x.length - 1 - i] *= i / n; return x; };

fs.mkdirSync(path.join(OUT, 'sfx'), { recursive: true });
for (const [name, [db, make]] of Object.entries(SFX)) {
  const x = fadeOut(make(rng(name)));
  const out = scaleTo(x, peak(x), db);
  const got = 20 * Math.log10(peak(out));
  assert(got >= -10.05 && got <= -5.95, `${name} peak ${got} outside -10..-6 dBFS`);
  writeWav(path.join(OUT, 'sfx', `${name}.wav`), out);
  console.log(`sfx/${name}.wav  ${(out.length / SR).toFixed(2)} s  peak ${got.toFixed(1)} dBFS`);
}
for (const [name, make] of Object.entries(BEDS)) {
  const x = make(rng(name));
  const out = scaleTo(x, rms(x), BED_RMS_DB);
  const seam = Math.abs(out[out.length - 1] - out[0]);
  assert(peak(out) < 1 && seam < 0.01, `${name} clips or has a loop click (seam ${seam})`);
  writeWav(path.join(OUT, `${name}.wav`), out);
  console.log(`${name}.wav  ${LOOP} s loop  rms ${BED_RMS_DB} dBFS  peak ${(20 * Math.log10(peak(out))).toFixed(1)} dBFS`);
}

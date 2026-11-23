#!/usr/bin/env node
/**
 * Step 2 Audio Prep Pipeline for dino-series
 *
 * Works out-of-the-box with Remotion's bundled FFmpeg (no system FFmpeg install required)
 * as well as full system FFmpeg.
 *
 * 1. Decodes any input audio (.mp3, .wav, .m4a, .flac, .ogg) to 48 kHz mono 16-bit PCM
 * 2. Detects every pause > 150 ms (configurable --max-pause 0.15 @ --silence-threshold -38dB)
 *    via FFmpeg `silencedetect` and splices them out with 5 ms cosine fades (click-free,
 *    preserving consonant attacks & strictly zero gaps > 150 ms per ANIMATION_GUIDE.md:140)
 * 3. Applies an 80 Hz high-pass filter + FFmpeg `loudnorm=I=-14:TP=-1.5:LRA=7` (-14 LUFS)
 * 4. Writes uncompressed 48 kHz WAV + CBR 192k MP3 to public/audio/ (zero VBR seeking drift)
 * 5. Produces word-level timestamps in public/audio/transcript.json:
 *    - Uses local whisper.cpp (.whisper-cpp/) or `whisper` CLI when available
 *    - Falls back to syllable-weighted alignment against --script (flagged as estimated)
 *
 * Usage:
 *   npm run prep:voice -- \
 *     --input episodes/ep01-trex-vs-triceratops/raw-vo.mp3 \
 *     --script episodes/ep01-trex-vs-triceratops/voiceover.txt
 */

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execFileSync, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

function parseArgs(argv) {
  const args = {
    input: null,
    script: null,
    outDir: path.join(ROOT, 'public', 'audio'),
    fps: 30,
    maxPause: 0.15,          // Strip every pause longer than 150 ms (ANIMATION_GUIDE.md:140)
    keepGap: 0.06,           // Leave 60 ms breath cushion at cut boundaries (0.06s < 0.15s)
    tempo: 1.0,              // Optional pitch-preserving FFmpeg atempo multiplier (e.g. 1.18 for ~3.7 wps)
    silenceThreshold: '-38dB',
    align: 'auto',           // auto | whisper-cpp | whisper | estimate
    whisperModel: 'base.en',
    keepTemp: false,
    noHighpass: false,
    help: false,
  };

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '-h' || a === '--help') args.help = true;
    else if (a === '-i' || a === '--input') args.input = argv[++i];
    else if (a === '-s' || a === '--script') args.script = argv[++i];
    else if (a === '-o' || a === '--out-dir') args.outDir = path.resolve(argv[++i]);
    else if (a === '--fps') args.fps = Number(argv[++i]);
    else if (a === '--max-pause') args.maxPause = Number(argv[++i]);
    else if (a === '--keep-gap') args.keepGap = Number(argv[++i]);
    else if (a === '--tempo') args.tempo = Number(argv[++i]);
    else if (a === '--silence-threshold') args.silenceThreshold = argv[++i];
    else if (a === '--align') args.align = argv[++i];
    else if (a === '--whisper-model') args.whisperModel = argv[++i];
    else if (a === '--keep-temp') args.keepTemp = true;
    else if (a === '--no-highpass') args.noHighpass = true;
    else if (!a.startsWith('-') && !args.input) args.input = a;
  }
  return args;
}

function printHelp() {
  console.log(`
dino-series Step 2: Voiceover Trim, Loudness Master & Word Alignment

Usage:
  npm run prep:voice -- --input <raw-vo.mp3|wav> [--script <voiceover.txt>]

Options:
  -i, --input <file>            Raw voiceover audio file (required)
  -s, --script <file>           Plain-text VO script for beat mapping & fallback alignment
  -o, --out-dir <dir>           Output directory (default: public/audio)
      --fps <n>                 Video framerate for frame indices (default: 30)
      --max-pause <sec>         Strip any pause longer than this (default: 0.15 = 150ms)
      --keep-gap <sec>          Cushion kept when splicing a long pause (default: 0.06s)
      --silence-threshold <dB>  Silence detector threshold (default: -38dB)
      --align <mode>            auto | whisper-cpp | whisper | estimate (default: auto)
      --whisper-model <name>    Whisper model name (default: base.en)
      --no-highpass             Disable 80 Hz high-pass filter
      --keep-temp               Keep 16kHz mono Whisper scratch WAV
`);
}

function findBinary(name) {
  const exe = process.platform === 'win32' ? `${name}.exe` : name;
  // 1. Prefer Remotion's bundled compositor binaries (guaranteed present after npm install)
  const remotionScope = path.join(ROOT, 'node_modules', '@remotion');
  if (fs.existsSync(remotionScope)) {
    for (const entry of fs.readdirSync(remotionScope)) {
      if (entry.startsWith('compositor-')) {
        const candidate = path.join(remotionScope, entry, exe);
        if (fs.existsSync(candidate)) return candidate;
      }
    }
  }
  // 2. Fallback to system PATH
  const whichCmd = process.platform === 'win32' ? 'where' : 'which';
  const res = spawnSync(whichCmd, [name], { encoding: 'utf8' });
  if (res.status === 0 && res.stdout.trim()) {
    return res.stdout.trim().split(/\r?\n/)[0];
  }
  return null;
}

function getDurationSec(ffprobe, filePath) {
  const out = execFileSync(
    ffprobe,
    [
      '-v', 'error',
      '-show_entries', 'format=duration',
      '-of', 'default=noprint_wrappers=1:nokey=1',
      filePath,
    ],
    { encoding: 'utf8' }
  ).trim();
  const val = parseFloat(out);
  if (!Number.isFinite(val) || val <= 0) {
    throw new Error(`Could not read valid audio duration for ${filePath} (got "${out}")`);
  }
  return val;
}

function detectSilences(ffmpeg, wavPath, threshold, minDuration) {
  const res = spawnSync(
    ffmpeg,
    ['-i', wavPath, '-af', `silencedetect=n=${threshold}:d=${minDuration}`, '-f', 'null', '-'],
    { encoding: 'utf8' }
  );
  const stderr = res.stderr ?? '';
  const silences = [];
  let currentStart = null;
  for (const line of stderr.split(/\r?\n/)) {
    const startMatch = line.match(/silence_start:\s*([0-9.]+)/);
    if (startMatch) {
      currentStart = parseFloat(startMatch[1]);
    }
    const endMatch = line.match(/silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)/);
    if (endMatch) {
      const end = parseFloat(endMatch[1]);
      const dur = parseFloat(endMatch[2]);
      const start = currentStart !== null ? currentStart : Math.max(0, end - dur);
      silences.push({ start, end, duration: dur });
      currentStart = null;
    }
  }
  if (currentStart !== null) {
    silences.push({ start: currentStart, end: Infinity, duration: Infinity });
  }
  return silences;
}

function readMonoPcmWav(wavPath) {
  const buf = fs.readFileSync(wavPath);
  if (buf.toString('ascii', 0, 4) !== 'RIFF' || buf.toString('ascii', 8, 12) !== 'WAVE') {
    throw new Error(`Not a valid RIFF/WAVE file: ${wavPath}`);
  }
  let offset = 12;
  let sampleRate = 48000;
  let dataOffset = -1;
  let dataSize = 0;

  while (offset + 8 <= buf.length) {
    const id = buf.toString('ascii', offset, offset + 4);
    const size = buf.readUInt32LE(offset + 4);
    if (id === 'fmt ') {
      sampleRate = buf.readUInt32LE(offset + 12);
    } else if (id === 'data') {
      dataOffset = offset + 8;
      dataSize = size;
      break;
    }
    offset += 8 + size + (size % 2);
  }
  if (dataOffset < 0) throw new Error(`Missing data chunk in WAV: ${wavPath}`);

  const numSamples = Math.floor(dataSize / 2);
  const samples = new Float32Array(numSamples);
  for (let i = 0; i < numSamples; i++) {
    samples[i] = buf.readInt16LE(dataOffset + i * 2) / 32768;
  }
  return { sampleRate, samples };
}

function writeMonoPcmWav(wavPath, sampleRate, samples) {
  const dataSize = samples.length * 2;
  const buf = Buffer.alloc(44 + dataSize);
  buf.write('RIFF', 0, 4, 'ascii');
  buf.writeUInt32LE(36 + dataSize, 4);
  buf.write('WAVE', 8, 4, 'ascii');
  buf.write('fmt ', 12, 4, 'ascii');
  buf.writeUInt32LE(16, 16);        // PCM chunk size
  buf.writeUInt16LE(1, 20);         // PCM format
  buf.writeUInt16LE(1, 22);         // Mono
  buf.writeUInt32LE(sampleRate, 24);
  buf.writeUInt32LE(sampleRate * 2, 28);
  buf.writeUInt16LE(2, 32);         // Block align
  buf.writeUInt16LE(16, 34);        // Bits per sample
  buf.write('data', 36, 4, 'ascii');
  buf.writeUInt32LE(dataSize, 40);

  for (let i = 0; i < samples.length; i++) {
    const clamped = Math.max(-1, Math.min(1, samples[i]));
    buf.writeInt16LE(Math.round(clamped * 32767), 44 + i * 2);
  }
  fs.writeFileSync(wavPath, buf);
}

/**
 * First-order 80 Hz high-pass filter (removes low-end mic rumble per ANIMATION_GUIDE.md:148)
 */
function applyHighPass80Hz(samples, sampleRate) {
  const rc = 1 / (2 * Math.PI * 80);
  const dt = 1 / sampleRate;
  const alpha = rc / (rc + dt);
  const out = new Float32Array(samples.length);
  let prevX = 0;
  let prevY = 0;
  for (let i = 0; i < samples.length; i++) {
    const x = samples[i];
    const y = alpha * (prevY + x - prevX);
    out[i] = y;
    prevX = x;
    prevY = y;
  }
  return out;
}

/**
 * Splices out every silence longer than maxPause, leaving at most keepGap (default 60 ms)
 * on internal gaps and 20 ms on leading/trailing edges, with 5 ms cosine fades to avoid clicks.
 */
function spliceSilences(samples, sampleRate, silences, maxPause, keepGap) {
  const totalSec = samples.length / sampleRate;
  const halfCushion = Math.min(keepGap / 2, maxPause * 0.4);
  const edgeCushion = 0.02;

  // Build removal intervals [cutStart, cutEnd]
  const cuts = [];
  for (const s of silences) {
    const sStart = Math.max(0, s.start);
    const sEnd = Math.min(totalSec, s.end);
    const dur = sEnd - sStart;
    if (dur < maxPause) continue;

    const isLeading = sStart <= 0.02;
    const isTrailing = sEnd >= totalSec - 0.02;

    const cutStart = isLeading ? 0 : sStart + halfCushion;
    const cutEnd = isTrailing ? totalSec : sEnd - halfCushion;
    if (cutEnd > cutStart + 0.005) {
      cuts.push([cutStart, cutEnd]);
    }
  }

  // Invert cuts into kept ranges
  const keeps = [];
  let cursor = 0;
  for (const [cStart, cEnd] of cuts) {
    if (cStart > cursor) keeps.push([cursor, cStart]);
    cursor = Math.max(cursor, cEnd);
  }
  if (cursor < totalSec) {
    // Allow small trailing edge cushion if not fully cut
    keeps.push([cursor, Math.min(totalSec, totalSec + edgeCushion)]);
  }

  if (keeps.length === 0) return samples;

  const fadeSamples = Math.round(0.005 * sampleRate); // 5 ms click-free cosine fade
  const segments = keeps.map(([a, b]) => {
    const i0 = Math.max(0, Math.round(a * sampleRate));
    const i1 = Math.min(samples.length, Math.round(b * sampleRate));
    const seg = samples.slice(i0, i1);
    const f = Math.min(fadeSamples, Math.floor(seg.length / 4));
    for (let k = 0; k < f; k++) {
      const gain = 0.5 * (1 - Math.cos((Math.PI * k) / f));
      seg[k] *= gain;
      seg[seg.length - 1 - k] *= gain;
    }
    return seg;
  });

  const totalLen = segments.reduce((sum, seg) => sum + seg.length, 0);
  const stitched = new Float32Array(totalLen);
  let pos = 0;
  for (const seg of segments) {
    stitched.set(seg, pos);
    pos += seg.length;
  }
  return stitched;
}

function tokenizeScript(text) {
  return text
    .replace(/^(?:Skeptic|Paleontologist|Speaker\s*\d+):\s*/gim, '') // Strip multi-speaker labels
    .replace(/\[[^\]]+\]/g, ' ') // Strip ElevenLabs v3 audio tags like [chuckling], [deadpan]
    .replace(/<[^>]+>/g, ' ')    // Strip Gemini 3.8 TTS inline vocal tags like <chuckle>, <short pause>
    .replace(/\r?\n+/g, ' ')
    .replace(/—/g, ' — ')
    .split(/\s+/)
    .map((w) => w.trim())
    .filter((w) => w && w !== '—');
}

function estimateSyllables(word) {
  const clean = word.toLowerCase().replace(/[^a-z0-9]/g, '');
  if (!clean) return 1;
  if (/^\d+$/.test(clean)) return Math.max(1, clean.length);
  const groups = clean.replace(/(?:[^laeiouy]es|ed|[^laeiouy]e)$/, '').match(/[aeiouy]{1,2}/g);
  return Math.max(1, groups ? groups.length : 1);
}

function alignWithWhisperCpp(wav16k, fps, modelName) {
  const dir = path.join(ROOT, '.whisper-cpp');
  const binNames = process.platform === 'win32'
    ? ['whisper-cli.exe', 'main.exe']
    : ['whisper-cli', 'main'];
  const bin = binNames.map((n) => path.join(dir, n)).find((p) => fs.existsSync(p));
  const model = path.join(dir, `ggml-${modelName}.bin`);
  if (!bin || !fs.existsSync(model)) return null;

  const outPrefix = path.join(os.tmpdir(), `dino-whisper-${Date.now()}`);
  const res = spawnSync(
    bin,
    ['-m', model, '-f', wav16k, '-ojf', '-of', outPrefix, '--max-len', '1', '--split-on-word'],
    { encoding: 'utf8' }
  );
  if (res.status !== 0) {
    console.warn(`[warn] whisper.cpp exited with ${res.status}: ${res.stderr}`);
    return null;
  }

  const jsonPath = `${outPrefix}.json`;
  if (!fs.existsSync(jsonPath)) return null;
  const raw = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
  fs.rmSync(jsonPath, { force: true });

  const words = [];
  for (const seg of raw.transcription ?? []) {
    const tokens = seg.tokens ?? [];
    if (tokens.length > 0) {
      let current = null;
      for (const tok of tokens) {
        const txt = String(tok.text ?? '');
        if (txt.startsWith('[') && txt.endsWith(']')) continue;
        const start = (tok.offsets?.from ?? 0) / 1000;
        const end = (tok.offsets?.to ?? 0) / 1000;
        if (!txt.trim()) continue;
        if (txt.startsWith(' ') || !current) {
          if (current) words.push(current);
          current = { word: txt.trim(), start, end };
        } else {
          current.word += txt;
          current.end = Math.max(current.end, end);
        }
      }
      if (current) words.push(current);
    } else if (seg.text?.trim()) {
      words.push({
        word: seg.text.trim(),
        start: (seg.offsets?.from ?? 0) / 1000,
        end: (seg.offsets?.to ?? 0) / 1000,
      });
    }
  }

  if (!words.length) return null;
  const cleaned = words.filter((w) => /[a-z0-9]/i.test(w.word));
  return {
    method: `whisper.cpp (${modelName})`,
    words: cleaned.map((w) => ({
      word: w.word,
      start: Number(w.start.toFixed(3)),
      end: Number(w.end.toFixed(3)),
      startFrame: Math.round(w.start * fps),
      endFrame: Math.round(w.end * fps),
    })),
  };
}

function alignWithWhisperCli(wav16k, fps, modelName) {
  const whichCmd = process.platform === 'win32' ? 'where' : 'which';
  const check = spawnSync(whichCmd, ['whisper'], { encoding: 'utf8' });
  if (check.status !== 0) return null;

  const outDir = fs.mkdtempSync(path.join(os.tmpdir(), 'dino-whisper-cli-'));
  const res = spawnSync(
    'whisper',
    [
      wav16k,
      '--model', modelName,
      '--language', 'en',
      '--word_timestamps', 'True',
      '--output_format', 'json',
      '--output_dir', outDir,
    ],
    { encoding: 'utf8', stdio: 'inherit' }
  );
  if (res.status !== 0) return null;

  const base = path.basename(wav16k, path.extname(wav16k));
  const jsonPath = path.join(outDir, `${base}.json`);
  if (!fs.existsSync(jsonPath)) return null;
  const raw = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
  fs.rmSync(outDir, { recursive: true, force: true });

  const words = [];
  for (const seg of raw.segments ?? []) {
    for (const w of seg.words ?? []) {
      const start = Number(w.start);
      const end = Number(w.end);
      words.push({
        word: String(w.word ?? '').trim(),
        start: Number(start.toFixed(3)),
        end: Number(end.toFixed(3)),
        startFrame: Math.round(start * fps),
        endFrame: Math.round(end * fps),
      });
    }
  }
  if (!words.length) return null;
  return { method: `openai-whisper (${modelName})`, words };
}

function alignEstimated(scriptText, durationSec, fps) {
  const tokens = tokenizeScript(scriptText);
  if (!tokens.length) {
    throw new Error('Cannot estimate alignment: script text is empty.');
  }

  const weights = tokens.map((w) => {
    let weight = estimateSyllables(w);
    if (/[.!?]$/.test(w)) weight += 0.9;
    else if (/[,;:—]$/.test(w)) weight += 0.45;
    return weight;
  });
  const totalWeight = weights.reduce((a, b) => a + b, 0);

  let cursor = 0;
  const words = tokens.map((word, idx) => {
    const span = (weights[idx] / totalWeight) * durationSec;
    const start = cursor;
    const end = idx === tokens.length - 1 ? durationSec : cursor + span;
    cursor = end;
    return {
      word,
      start: Number(start.toFixed(3)),
      end: Number(end.toFixed(3)),
      startFrame: Math.round(start * fps),
      endFrame: Math.round(end * fps),
    };
  });

  return { method: 'estimated-syllable-proportional', words };
}

function detectBeats(words, durationInFrames) {
  const findPhrase = (phrase) => {
    const needles = phrase.toLowerCase().replace(/[^a-z0-9\s]/g, '').split(/\s+/).filter(Boolean);
    for (let i = 0; i <= words.length - needles.length; i++) {
      let ok = true;
      for (let j = 0; j < needles.length; j++) {
        const w = words[i + j].word.toLowerCase().replace(/[^a-z0-9]/g, '');
        if (w !== needles[j]) {
          ok = false;
          break;
        }
      }
      if (ok) return words[i];
    }
    return null;
  };

  const b2a = findPhrase('wait what') ?? findPhrase('12meter') ?? findPhrase('sixty six') ?? findPhrase('sixtysix') ?? findPhrase('66') ?? findPhrase('hell creek');
  const b2b = findPhrase('problem is');
  const b3 = findPhrase('you see');
  const b4 = findPhrase('unhealed') ?? findPhrase('so what happened');

  const points = [
    { id: 'hook', label: '1. Paradox Hook (Daylight)', mood: 'daylight', word: words[0] ?? null },
    { id: 'escalation', label: '2a. Escalation (Daylight)', mood: 'daylight', word: b2a },
    { id: 'counter_gag', label: '2b. Counter-Stats + Gag (Daylight)', mood: 'daylight', word: b2b },
    { id: 'pivot', label: '3. "You see..." Pivot (Night Blue)', mood: 'nightBlue', word: b3 },
    { id: 'payoff', label: '4. Ironic Payoff (Sunset)', mood: 'sunset', word: b4 },
  ].filter((p) => p.word);

  return points.map((p, idx) => {
    const next = points[idx + 1];
    return {
      id: p.id,
      label: p.label,
      mood: p.mood,
      startSec: p.word.start,
      startFrame: p.word.startFrame,
      endFrame: next ? next.word.startFrame : durationInFrames,
      anchorWord: p.word.word,
    };
  });
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help || !args.input) {
    printHelp();
    process.exit(args.help ? 0 : 1);
  }

  const inputPath = path.resolve(args.input);
  if (!fs.existsSync(inputPath)) {
    console.error(`Error: input audio file not found: ${inputPath}`);
    process.exit(1);
  }

  const ffmpeg = findBinary('ffmpeg');
  const ffprobe = findBinary('ffprobe');
  if (!ffmpeg || !ffprobe) {
    console.error('Error: ffmpeg/ffprobe not found in node_modules/@remotion/compositor-* or PATH.');
    process.exit(1);
  }

  fs.mkdirSync(args.outDir, { recursive: true });
  const rawWav = path.join(args.outDir, '_raw-48k.wav');
  const splicedWav = path.join(args.outDir, '_spliced-48k.wav');
  const wavOut = path.join(args.outDir, 'voiceover.wav');
  const mp3Out = path.join(args.outDir, 'voiceover.mp3');
  const wav16k = path.join(args.outDir, '_voiceover-16k.wav');
  const transcriptOut = path.join(args.outDir, 'transcript.json');

  const rawDuration = getDurationSec(ffprobe, inputPath);

  console.log(`[1/4] Decoding & stripping pauses > ${Math.round(args.maxPause * 1000)} ms (threshold ${args.silenceThreshold})...`);
  execFileSync(
    ffmpeg,
    ['-y', '-i', inputPath, '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', rawWav],
    { stdio: 'pipe' }
  );

  const silences = detectSilences(ffmpeg, rawWav, args.silenceThreshold, args.maxPause);
  const { sampleRate, samples: rawSamples } = readMonoPcmWav(rawWav);
  const filtered = args.noHighpass ? rawSamples : applyHighPass80Hz(rawSamples, sampleRate);
  const trimmedSamples = spliceSilences(filtered, sampleRate, silences, args.maxPause, args.keepGap);
  writeMonoPcmWav(splicedWav, sampleRate, trimmedSamples);

  const afMaster = args.tempo && Math.abs(args.tempo - 1.0) > 0.005
    ? `atempo=${args.tempo},loudnorm=I=-14:TP=-1.5:LRA=7`
    : 'loudnorm=I=-14:TP=-1.5:LRA=7';

  console.log(`[2/4] Mastering to -14 LUFS / -1.5 dBTP${args.tempo !== 1 ? ` (tempo ${args.tempo}x)` : ''} & encoding CBR 192k MP3...`);
  execFileSync(
    ffmpeg,
    [
      '-y', '-i', splicedWav,
      '-af', afMaster,
      '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le',
      wavOut,
    ],
    { stdio: 'pipe' }
  );

  execFileSync(
    ffmpeg,
    ['-y', '-i', wavOut, '-c:a', 'libmp3lame', '-b:a', '192k', '-write_xing', '0', mp3Out],
    { stdio: 'pipe' }
  );

  execFileSync(
    ffmpeg,
    ['-y', '-i', wavOut, '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', wav16k],
    { stdio: 'pipe' }
  );

  fs.rmSync(rawWav, { force: true });
  fs.rmSync(splicedWav, { force: true });

  const trimmedDuration = getDurationSec(ffprobe, wavOut);
  const durationInFrames = Math.ceil(trimmedDuration * args.fps);
  const savedSec = Math.max(0, rawDuration - trimmedDuration);

  console.log(
    `      Raw: ${rawDuration.toFixed(2)}s -> Trimmed: ${trimmedDuration.toFixed(2)}s ` +
    `(removed ${savedSec.toFixed(2)}s dead air across ${silences.length} pause(s), ${durationInFrames} frames @ ${args.fps} fps)`
  );

  const scriptText = args.script && fs.existsSync(path.resolve(args.script))
    ? fs.readFileSync(path.resolve(args.script), 'utf8').trim()
    : '';

  console.log(`[3/4] Generating word-level timestamps (mode: ${args.align})...`);
  let aligned = null;
  if (args.align === 'auto' || args.align === 'whisper-cpp') {
    aligned = alignWithWhisperCpp(wav16k, args.fps, args.whisperModel);
  }
  if (!aligned && (args.align === 'auto' || args.align === 'whisper')) {
    aligned = alignWithWhisperCli(wav16k, args.fps, args.whisperModel);
  }
  if (!aligned && (args.align === 'auto' || args.align === 'estimate')) {
    if (!scriptText) {
      console.error(
        'Error: No Whisper engine found (.whisper-cpp/ or `whisper` CLI) and no --script file provided for fallback estimation.'
      );
      process.exit(1);
    }
    aligned = alignEstimated(scriptText, trimmedDuration, args.fps);
    console.warn(
      '      [!] Whisper not found locally; wrote syllable-estimated timestamps so you can prototype immediately.\n' +
      '          For frame-exact ASR timestamps, place whisper.cpp + ggml-base.en.bin in `.whisper-cpp/` or install `whisper` CLI and re-run.'
    );
  }

  if (!aligned) {
    console.error(`Error: Requested alignment engine "${args.align}" is not available.`);
    process.exit(1);
  }

  if (!args.keepTemp && fs.existsSync(wav16k)) {
    fs.rmSync(wav16k, { force: true });
  }

  const wps = Number((aligned.words.length / trimmedDuration).toFixed(2));
  const beats = detectBeats(aligned.words, durationInFrames);

  const payload = {
    sourceFile: path.basename(inputPath),
    audioWav: 'audio/voiceover.wav',
    audioMp3: 'audio/voiceover.mp3',
    fps: args.fps,
    rawDurationSec: Number(rawDuration.toFixed(3)),
    durationSec: Number(trimmedDuration.toFixed(3)),
    durationInFrames,
    silencesRemovedCount: silences.length,
    wordCount: aligned.words.length,
    wordsPerSecond: wps,
    alignmentMethod: aligned.method,
    isEstimated: aligned.method.startsWith('estimated'),
    trimConfig: {
      maxPauseSec: args.maxPause,
      keepGapSec: args.keepGap,
      silenceThreshold: args.silenceThreshold,
      highPassHz: args.noHighpass ? null : 80,
      loudnormTargetLufs: -14,
      truePeakDb: -1.5,
    },
    beats,
    words: aligned.words,
  };

  fs.writeFileSync(transcriptOut, JSON.stringify(payload, null, 2) + '\n', 'utf8');
  console.log('[4/4] Done! Wrote:');
  console.log(`      - ${path.relative(ROOT, wavOut)}`);
  console.log(`      - ${path.relative(ROOT, mp3Out)}`);
  console.log(`      - ${path.relative(ROOT, transcriptOut)} (${aligned.words.length} words, ${wps} wps, method: ${aligned.method})`);
  if (beats.length) {
    console.log('      Detected beat frames:');
    for (const b of beats) {
      console.log(`        * ${b.label}: frame ${b.startFrame} (${b.startSec.toFixed(2)}s)`);
    }
  }
}

main();

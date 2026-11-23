#!/usr/bin/env node
/**
 * Windows-safe one-bundle batch still dumper + contact sheet builder for dino-series
 * (adopts video-KrD2pcBrzII-guide.md §6.2 without Linux `/opt/pw-browsers` hardcodes).
 *
 * Usage:
 *   npm run stills -- [--scale 0.4] [--safe-zones] [--frames 0,180,264,...]
 */

import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { bundle } from '@remotion/bundler';
import { renderStill, selectComposition } from '@remotion/renderer';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

function findFfmpeg() {
  const exe = process.platform === 'win32' ? 'ffmpeg.exe' : 'ffmpeg';
  const remotionScope = path.join(ROOT, 'node_modules', '@remotion');
  if (fs.existsSync(remotionScope)) {
    for (const entry of fs.readdirSync(remotionScope)) {
      if (entry.startsWith('compositor-')) {
        const p = path.join(remotionScope, entry, exe);
        if (fs.existsSync(p)) return p;
      }
    }
  }
  return 'ffmpeg';
}

function parseArgs(argv) {
  const args = {
    composition: 'Ep01TrexVsTriceratops',
    scale: 0.4,
    safeZones: false,
    frames: null,
    outDir: path.join(ROOT, 'shots', 'ep01-stills'),
    sheet: path.join(ROOT, 'shots', 'ep01-contact-sheet.png'),
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--scale') args.scale = Number(argv[++i]);
    else if (a === '--safe-zones') args.safeZones = true;
    else if (a === '--composition') args.composition = argv[++i];
    else if (a === '--frames') args.frames = argv[++i].split(',').map((s) => Number(s.trim())).filter(Number.isFinite);
    else if (a === '--out-dir') args.outDir = path.resolve(argv[++i]);
    else if (a === '--sheet') args.sheet = path.resolve(argv[++i]);
  }
  return args;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const transcriptPath = path.join(ROOT, 'public', 'audio', 'transcript.json');
  const transcript = JSON.parse(fs.readFileSync(transcriptPath, 'utf8'));
  const beatMap = Object.fromEntries((transcript.beats ?? []).map((b) => [b.id, b.startFrame]));
  const maxF = (transcript.durationInFrames ?? 1800) + 44;

  // Default 10 key QA frames covering both stickmen, all 3 lighting moods, and Rick's Clips rapid cuts
  const defaultFrames = [
    25,                                                  // T1: Skeptic hook + towering dinos
    185,                                                 // T2: Paleontologist eureka + HEALED BITE
    250,                                                 // T3a: Skeptic snap reaction WAIT WHAT?!
    355,                                                 // T3b: Low worm's-eye T. rex roar + 35,000 N
    600,                                                 // T4b: Triceratops charging stomp
    870,                                                 // T6b: Triceratops frill + Paleontologist scale
    1140,                                                // T8a: Night Blue 2008 FOSSIL + Paleontologist
    1360,                                                // T8b: Night Blue Triceratops pivot + T. rex recoil
    1815,                                                // T10b: Sunset T. rex popped jar lid
    1865,                                                // T11: Horrified Skeptic JAR LID?!
  ];

  const frames = (args.frames ?? defaultFrames).map((f) => Math.max(0, Math.min(maxF, Math.round(f))));
  fs.mkdirSync(args.outDir, { recursive: true });

  console.log(`[1/3] Bundling Remotion entry once (src/video/index.ts)...`);
  const serveUrl = await bundle({
    entryPoint: path.join(ROOT, 'src', 'video', 'index.ts'),
    publicDir: path.join(ROOT, 'public'),
  });

  const inputProps = { showSafeZones: args.safeZones };
  const composition = await selectComposition({
    serveUrl,
    id: args.composition,
    inputProps,
    chromiumOptions: { gl: 'angle' },
  });

  console.log(`[2/3] Rendering ${frames.length} stills at scale=${args.scale} (${Math.round(composition.width * args.scale)}x${Math.round(composition.height * args.scale)})...`);
  const written = [];
  for (let i = 0; i < frames.length; i++) {
    const f = frames[i];
    const outPath = path.join(args.outDir, `still-${String(i).padStart(2, '0')}-f${String(f).padStart(4, '0')}.png`);
    await renderStill({
      composition,
      serveUrl,
      output: outPath,
      frame: f,
      scale: args.scale,
      imageFormat: 'png',
      inputProps,
      chromiumOptions: { gl: 'angle' },
    });
    written.push({ f, outPath });
    console.log(`      [${i + 1}/${frames.length}] frame ${f} -> ${path.relative(ROOT, outPath)}`);
  }

  // Stitch into a single 5x2 contact sheet using Remotion's bundled FFmpeg (hstack + vstack, supported without libfreetype)
  const ffmpeg = findFfmpeg();
  const cols = Math.min(5, written.length);
  const rows = Math.ceil(written.length / cols);
  if (written.length >= 2) {
    console.log(`[3/3] Stitching ${cols}x${rows} contact sheet -> ${path.relative(ROOT, args.sheet)}...`);
    // Build a simple HTML grid rendered OR check if ffmpeg supports tile/hstack. Let's use pure Node PNG stitch?
    // Wait: Remotion's FFmpeg has `scale` + `nullsrc` + `copy` but may omit `hstack`/`tile`!
    // Use Python Pillow/matplotlib OR pure PNG buffer composition so it NEVER fails on slim FFmpeg!
    const pyScript = `
import sys, pathlib
from PIL import Image, ImageDraw
paths = sys.argv[2:]
imgs = [Image.open(p).convert('RGB') for p in paths]
w, h = imgs[0].size
cols = min(5, len(imgs))
rows = (len(imgs) + cols - 1) // cols
pad = 12
sheet = Image.new('RGB', (cols * w + (cols + 1) * pad, rows * h + (rows + 1) * pad), (29, 30, 48))
draw = ImageDraw.Draw(sheet)
for idx, (im, p) in enumerate(zip(imgs, paths)):
    r, c = divmod(idx, cols)
    x = pad + c * (w + pad)
    y = pad + r * (h + pad)
    sheet.paste(im, (x, y))
    label = pathlib.Path(p).stem.split('-')[-1]
    draw.rectangle([x + 6, y + 6, x + 96, y + 32], fill=(29, 30, 48))
    draw.text((x + 14, y + 12), label, fill=(255, 211, 105))
sheet.save(sys.argv[1])
print('Saved contact sheet:', sys.argv[1], sheet.size)
`;
    try {
      execFileSync('python', ['-m', 'uv', 'run', '--with', 'pillow', 'python', '-c', pyScript, args.sheet, ...written.map((w) => w.outPath)], { stdio: 'inherit' });
    } catch {
      console.warn('      [!] Could not stitch contact sheet (individual stills are in ' + path.relative(ROOT, args.outDir) + ')');
    }
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

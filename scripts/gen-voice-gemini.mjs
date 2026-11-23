#!/usr/bin/env node
/**
 * Generate expressive single- or two-speaker voiceover via Gemini 3.8 Flash TTS (Interactions API)
 * using structured per-beat `speech_metadata.style` + official `<...>` inline vocal tags.
 *
 * Requires GEMINI_API_KEY in the environment or in the repo's `.env` (git-excluded; `npm run gen:voice` loads it).
 *
 * Usage:
 *   $env:GEMINI_API_KEY="your-key"
 *   npm run gen:voice -- --input episodes/ep01-trex-vs-triceratops/voiceover-gemini.json --prep
 */

import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

function parseArgs(argv) {
  const args = {
    input: path.join(ROOT, 'episodes', 'ep01-trex-vs-triceratops', 'voiceover-gemini.json'),
    out: null,
    voice: null,
    model: null,
    prep: false,
    dryRun: false,
    help: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '-h' || a === '--help') args.help = true;
    else if (a === '-i' || a === '--input') args.input = path.resolve(argv[++i]);
    else if (a === '-o' || a === '--out') args.out = path.resolve(argv[++i]);
    else if (a === '-v' || a === '--voice') args.voice = argv[++i];
    else if (a === '-m' || a === '--model') args.model = argv[++i];
    else if (a === '--prep') args.prep = true;
    else if (a === '--tempo') args.tempo = argv[++i];
    else if (a === '--dry-run') args.dryRun = true;
  }
  return args;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(`
Generate voiceover with Gemini 3.8 Flash TTS (Interactions API)

Usage:
  npm run gen:voice -- [--input <voiceover-gemini.json>] [--voice Charon|Puck|Fenrir|Kore] [--prep] [--dry-run]

Flags:
  -i, --input <file>   Structured turns JSON (default: episodes/ep01-trex-vs-triceratops/voiceover-gemini.json)
  -o, --out <file>     Output WAV path (default: <input-dir>/raw-vo.wav)
  -v, --voice <name>   Override prebuilt voice (e.g. Charon, Puck, Fenrir, Orus, Kore)
  -m, --model <id>     Override model (default: gemini-3.8-flash-tts)
      --tempo <x>      Pass a pitch-preserving tempo to prep-voice (e.g. 1.05)
      --prep           Automatically run Step 2 (scripts/prep-voice.mjs) after generating WAV
      --dry-run        Validate JSON and print the Interactions API request payload without calling the API
`);
    process.exit(0);
  }

  if (!fs.existsSync(args.input)) {
    console.error(`Error: input JSON not found: ${args.input}`);
    process.exit(1);
  }

  const spec = JSON.parse(fs.readFileSync(args.input, 'utf8'));
  const model = args.model ?? spec.model ?? 'gemini-3.8-flash-tts';
  const voice = args.voice ?? spec.voice ?? 'Charon';
  const outPath = args.out ?? path.join(path.dirname(args.input), 'raw-vo.wav');

  if (!Array.isArray(spec.turns) || spec.turns.length === 0) {
    console.error('Error: input JSON must contain a non-empty "turns" array.');
    process.exit(1);
  }

  const payload = {
    model,
    input: [
      {
        type: 'user_input',
        content: spec.turns.map((t) => ({
          type: 'text',
          text: t.text,
          annotations: [
            {
              type: 'speech_metadata',
              ...(t.speaker && { speaker: t.speaker }),
              style: t.style,
            },
          ],
        })),
      },
    ],
    response_format: { type: 'audio' },
    generation_config: {
      // Multi-speaker takes an object of named speakers; single-speaker an array.
      speech_config: spec.speakers ? { speakers: spec.speakers } : [{ voice }],
    },
  };

  if (args.dryRun) {
    console.log(`[dry-run] Model: ${model} | Voice: ${spec.speakers ? spec.speakers.map((x) => `${x.speaker}=${x.voice}`).join(', ') : voice} | Turns: ${spec.turns.length} | Out: ${outPath}`);
    console.log(JSON.stringify(payload, null, 2));
    return;
  }

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    console.error(
      'Error: GEMINI_API_KEY is not set.\n' +
      'Get a key at https://aistudio.google.com/apikey and run:\n' +
      '  $env:GEMINI_API_KEY="YOUR_KEY"\n' +
      '  npm run gen:voice -- --prep'
    );
    process.exit(3);
  }

  console.log(`[1/2] Synthesizing ${spec.turns.length} styled turns via ${model} (voice: ${voice})...`);
  const res = await fetch('https://generativelanguage.googleapis.com/v1beta/interactions', {
    method: 'POST',
    headers: {
      'x-goog-api-key': apiKey,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errText = await res.text();
    console.error(`Gemini API error (${res.status} ${res.statusText}):\n${errText}`);
    process.exit(1);
  }

  const data = await res.json();
  const base64Audio =
    data?.output_audio?.data ??
    data?.outputs?.find((o) => o?.type === 'audio')?.data ??
    data?.steps?.flatMap((s) => s?.content ?? []).find((c) => c?.type === 'audio')?.data;

  if (!base64Audio) {
    console.error('Error: response did not contain output audio data:\n', JSON.stringify(data, null, 2).slice(0, 1000));
    process.exit(1);
  }

  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  const wavBuf = Buffer.from(base64Audio, 'base64');
  fs.writeFileSync(outPath, wavBuf);
  console.log(`[2/2] Saved ${(wavBuf.length / 1024).toFixed(1)} KB WAV -> ${path.relative(ROOT, outPath)}`);

  if (args.prep) {
    const scriptTxt = path.join(path.dirname(args.input), 'voiceover.txt');
    const prepArgs = [path.join(ROOT, 'scripts', 'prep-voice.mjs'), '--input', outPath];
    if (fs.existsSync(scriptTxt)) {
      prepArgs.push('--script', scriptTxt);
    }
    if (args.tempo) prepArgs.push('--tempo', args.tempo);
    console.log('\nRunning Step 2 audio prep (150ms trim + -14 LUFS + transcript.json)...');
    execFileSync(process.execPath, prepArgs, { stdio: 'inherit' });
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

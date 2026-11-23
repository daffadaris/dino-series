#!/usr/bin/env node
// Installs whisper.cpp and the base.en model into .whisper-cpp/ (where prep-voice.mjs looks for them).
//   npm run setup:whisper [-- <model>]   e.g. medium.en for better word timings
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { downloadWhisperModel, installWhisperCpp } from '@remotion/install-whisper-cpp';

const to = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '.whisper-cpp');
const model = process.argv[2] ?? 'base.en';
await installWhisperCpp({ to, version: '1.5.5' });
await downloadWhisperModel({ model, folder: to });
console.log(`whisper.cpp 1.5.5 + ggml-${model}.bin ready in ${to}`);

import { Config } from '@remotion/cli/config';

// src/ holds the Python builders, so the video code lives in src/video/.
Config.setEntryPoint('src/video/index.ts');
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(92);
Config.setOverwriteOutput(true);
// 'angle' uses the native GPU (D3D11 on Windows); use 'swangle' on GPU-less machines (much slower).
Config.setChromiumOpenGlRenderer('angle');
// Heavy WebGL post passes: modest concurrency avoids GPU context loss.
Config.setConcurrency(4);

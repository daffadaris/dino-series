import * as THREE from 'three';

// Full-screen quad: positions are already in clip space.
const VERT = /* glsl */ `
  varying vec2 vUv;
  void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;

const DEPTH = /* glsl */ `
  #include <packing>
  uniform sampler2D tDepth; uniform float uCameraNear; uniform float uCameraFar;
  float viewDist(vec2 uv) { return -perspectiveDepthToViewZ(texture2D(tDepth, uv).x, uCameraNear, uCameraFar); }`;

const common = () => ({
  tDiffuse: { value: null as THREE.Texture | null },
  tDepth: { value: null as THREE.Texture | null },
  uResolution: { value: new THREE.Vector2(1080, 1920) },
  uCameraNear: { value: 0.1 },
  uCameraFar: { value: 400 },
});

/**
 * Pass 1 (ANIMATION_GUIDE.md:425): depth edges + light Sobel on luma, distance fade, saturation boost,
 * lifted blacks. The scene target is linear HDR, so this pass tone-maps (ACES) and encodes sRGB first; everything
 * after it, including the DoF pass and the canvas, works in display sRGB.
 */
export const InkOutlineShader = () => ({
  uniforms: {
    ...common(),
    uInkColor: { value: new THREE.Color('#1d1e30') },
    uBlackLift: { value: new THREE.Vector3(0.075, 0.082, 0.135) },
    uDepthThreshold: { value: 0.012 },
    uLumaThreshold: { value: 0.22 },
    uEdgeFadeStart: { value: 24 },
    uEdgeFadeEnd: { value: 68 },
    uSaturation: { value: 1.15 },
    uLineThickness: { value: 1.15 },
  },
  vertexShader: VERT,
  fragmentShader: /* glsl */ `
    ${DEPTH}
    uniform sampler2D tDiffuse; uniform vec2 uResolution; uniform vec3 uInkColor; uniform vec3 uBlackLift;
    uniform float uDepthThreshold, uLumaThreshold, uEdgeFadeStart, uEdgeFadeEnd, uSaturation, uLineThickness;
    varying vec2 vUv;

    vec3 toSRGB(vec3 c) { return mix(1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, 12.92 * c, step(c, vec3(0.0031308))); }
    vec3 display(vec2 uv) {
      vec3 c = texture2D(tDiffuse, uv).rgb;
      c = clamp((c * (2.51 * c + 0.03)) / (c * (2.43 * c + 0.59) + 0.14), 0.0, 1.0); // ACES (Narkowicz)
      return toSRGB(c);
    }
    float luma(vec2 uv) { return dot(display(uv), vec3(0.299, 0.587, 0.114)); }

    void main() {
      vec2 tx = uLineThickness / uResolution;
      float cd = viewDist(vUv);
      float d[9]; float l[9];
      for (int j = 0; j < 9; j++) {
        vec2 o = vec2(float(j - (j / 3) * 3) - 1.0, 1.0 - float(j / 3)) * tx;
        d[j] = cd / viewDist(vUv + o); // reciprocal depth is linear across a plane in screen space
        l[j] = luma(vUv + o);
      }
      // indices: 0 TL 1 TC 2 TR / 3 ML 4 MC 5 MR / 6 BL 7 BC 8 BR
      // Second difference instead of the guide's first-order Sobel: flat ground at grazing angles has a steep but
      // linear depth gradient, which Sobel inks as a dark band along the horizon; silhouettes still break linearity.
      float dd = max(max(abs(d[3] + d[5] - 2.0), abs(d[1] + d[7] - 2.0)), max(abs(d[0] + d[8] - 2.0), abs(d[2] + d[6] - 2.0)));
      float gxL = -l[0] - 2.0 * l[3] - l[6] + l[2] + 2.0 * l[5] + l[8];
      float gyL = -l[0] - 2.0 * l[1] - l[2] + l[6] + 2.0 * l[7] + l[8];
      float depthEdge = smoothstep(uDepthThreshold, uDepthThreshold * 2.5, dd);
      float lumaEdge = smoothstep(uLumaThreshold, uLumaThreshold * 2.2, length(vec2(gxL, gyL))) * 0.42;
      float fade = 1.0 - smoothstep(uEdgeFadeStart, uEdgeFadeEnd, cd);
      float inkMask = clamp(max(depthEdge, lumaEdge) * fade, 0.0, 0.92);

      vec3 c = display(vUv);
      c = mix(vec3(dot(c, vec3(0.299, 0.587, 0.114))), c, uSaturation);
      c = max(c, uBlackLift);
      gl_FragColor = vec4(mix(c, max(toSRGB(uInkColor), uBlackLift), inkMask), 1.0);
    }`,
});

/** Pass 2 (ANIMATION_GUIDE.md:540): 24-tap golden-angle bokeh on the inked image, using the original sharp depth. */
export const DepthOfFieldShader = () => ({
  uniforms: {
    ...common(),
    uFocusDist: { value: 12 },
    uFocusRange: { value: 5.5 },
    uMaxBlur: { value: 7.5 },
  },
  vertexShader: VERT,
  fragmentShader: /* glsl */ `
    ${DEPTH}
    uniform sampler2D tDiffuse; uniform vec2 uResolution; uniform float uFocusDist, uFocusRange, uMaxBlur;
    varying vec2 vUv;
    float coc(float dist) { return smoothstep(uFocusRange * 0.35, uFocusRange * 1.8, abs(dist - uFocusDist)); }
    void main() {
      float cd = viewDist(vUv);
      float cc = coc(cd);
      vec3 acc = texture2D(tDiffuse, vUv).rgb;
      if (cc < 0.02) { gl_FragColor = vec4(acc, 1.0); return; }
      float total = 1.0;
      // uMaxBlur is in pixels at 1080 px wide; scale with the actual target width.
      float radius = uMaxBlur * cc * uResolution.x / 1080.0;
      for (int i = 1; i <= 24; i++) {
        float fi = float(i);
        float r = sqrt(fi / 24.0) * radius;
        vec2 uv = clamp(vUv + vec2(cos(fi * 2.39996323), sin(fi * 2.39996323)) * r / uResolution, vec2(0.001), vec2(0.999));
        float sd = viewDist(uv);
        float wgt = sd < cd - 0.5 ? coc(sd) : 1.0; // sharp foreground must not bleed into the blurred background
        acc += texture2D(tDiffuse, uv).rgb * wgt;
        total += wgt;
      }
      gl_FragColor = vec4(acc / total, 1.0);
    }`,
});

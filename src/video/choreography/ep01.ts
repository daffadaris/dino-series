// Episode 01: T. rex vs. Triceratops (Skeptic + Paleontologist, 13 turns). Every shot shows what its line says.
// Two places: the face-off clearing (x ~0) and the fossil spot (x 12-17). All cues come from public/audio/transcript.json.
import { Easing } from 'remotion';
import transcript from '../../../public/audio/transcript.json';
import type { CameraKey, CameraShake } from './camera';
import type { ActorSpec } from '../scene/CutoutActor';
import type { PropSpec } from '../scene/Prop';

export const FPS = transcript.fps;
/** Establishing beat before the first line, so the opening is not rushed. */
export const VO_START = 30;
export const VO_END = VO_START + transcript.durationInFrames;
/** Tail: a closing beat (Triceratops stomps, T. rex backs off) on the pull-back. */
export const END_BEAT = VO_END + 18;
export const DURATION = VO_END + 90;
export const WORDS = transcript.words.map((w) => ({ ...w, startFrame: w.startFrame + VO_START, endFrame: w.endFrame + VO_START }));

const norm = (w: string) => w.toLowerCase().replace(/[^a-z0-9]/g, '');
/** First frame of `word` (or any alias) at or after composition frame `after`. */
export function cue(word: string | string[], after = 0): number {
  const targets = (Array.isArray(word) ? word : [word]).map(norm);
  const hit = WORDS.find((w) => w.startFrame >= after && targets.includes(norm(w.word)));
  if (!hit) throw new Error(`cue word "${targets.join('|')}" not found after frame ${after}`);
  return hit.startFrame;
}

// --- Turn starts (L1..L11, plus the horn-lock exchange L6b/L6c) and word cues, chained so each lookup starts after the previous one ---
const L1 = VO_START;
const easy = cue('easy', L1);
const L2 = cue('is', easy);
const look = cue('look', L2);
const horn1 = cue('horn', look);
const tooth = cue('tooth', horn1);
const healed = cue('healed', tooth);
const thisTri = cue('this', healed);
const L3 = cue('survived', cue('survived', thisTri) + 1);
const meters12 = cue(['12', 'twelve'], L3);
const strongest = cue('strongest', meters12);
const bite1 = cue('bite', strongest);
const L4 = cue('true', bite1);
const triL4 = cue('triceratops', L4);
const nine = cue(['9', 'nine'], triL4);
const tons = cue('tons', nine);
const skull25 = cue(['25', 'twoandahalf', 'two'], tons);
const horns = cue('horns', skull25);
const meterHorn = cue('meter', horns);
const L5 = cue('so', horns);
const sneak = cue('sneak', L5);
const L6 = cue('the', cue('neck', sneak));
const hornL6 = cue('horn', L6);
const thisL6 = cue('this', hornL6);
const face = cue(['face', 'facetoface'], thisL6);
const that = cue('that', face);
const swiveled = cue(['swiveled', 'swivelled'], that);
const ball = cue(['ball', 'ballandsocket'], swiveled);
const L6b = cue('wait', ball);
const fighting = cue('fighting', L6b);
const L6c = cue('and', fighting);
const healedL6c = cue('healed', L6c);
const locking = cue('locking', healedL6c);
const L7 = cue('okay', locking);
const did = cue('did', L7);
const L8 = cue('oh', did);
const other = cue('other', L8);
const bites = cue('bites', other);
const never = cue('never', bites);
const neckJoint = cue('neck', never);
const L9 = cue('trex', neckJoint);
const gripped = cue('gripped', L9);
const pulled = cue('pulled', gripped);
const popped = cue('popped', pulled);
const jar = cue('jar', popped);
const L10 = cue('it', jar);
const L11 = cue('only', L10);
const inHC = cue('in', L11);
const fought = cue('fought', inHC);

export const LIGHTING = { late: [L8 - 10, L8 + 20] as [number, number] };

const SKEPTIC_SPEAK: [number, number][] = [[L1, L2 - 4], [L3, L4 - 4], [L5, L6 - 4], [L6b, L6c - 4], [L7, L8 - 4], [L10, L11 - 4]];
const PALEO_SPEAK: [number, number][] = [[L2, L3 - 4], [L4, L5 - 4], [L6, L6b - 4], [L6c, L7 - 4], [L8, L10 - 4], [L11, VO_END]];

const walkEase = Easing.inOut(Easing.sin);

// Clearing: T. rex faces right, Triceratops faces left; heads meet near x 0. Hosts stand in front (z 5).
const TREX_A: [number, number, number] = [-6.5, 0, -3];
const SKP: [number, number, number] = [-2.0, 0, 5.0];
const PAL_A: [number, number, number] = [1.2, 0, 5.0];
// Fossil spot: horn on the ground, skull (facing left) on its neck bones; the condyle is the shared anchor.
const HORN: [number, number, number] = [12.2, 0, 3.6];
const SK: [number, number, number] = [14.6, 0.183, 2.6];

export const ACTORS: ActorSpec[] = [
  {
    id: 'skp-a', species: 'skeptic', position: SKP, visible: [0, DURATION],
    hidden: [[meters12, L4 - 1], [thisL6, that - 1], [L6c, L7 - 1]], // out of the hero shot and the two head-to-head shots
    speakRanges: SKEPTIC_SPEAK,
    poses: [[0, 'point'], [easy, 'smug'], [L3, 'surprised'], [L5, 'point'], [L6b, 'surprised'], [fighting, 'point'], [L7, 'sad'], [did, 'surprised'], [L10, 'scared'], [inHC, 'happy']],
    actions: [{ at: 10, kind: 'hop', dur: 16 }, { at: easy, kind: 'hop', dur: 16 }, { at: L3, kind: 'recoil', dur: 18 },
      { at: L5, kind: 'hop', dur: 14 }, { at: L6b, kind: 'hop', dur: 14 }, { at: L10, kind: 'recoil', dur: 22 }, { at: END_BEAT + 27, kind: 'hop', dur: 16 }],
    phase: 0.3,
  },
  {
    id: 'pal-a', species: 'paleontologist', position: PAL_A, flipX: true, visible: [L4, DURATION], hidden: [[triL4, inHC - 1]],
    speakRanges: PALEO_SPEAK,
    poses: [[L4, 'smug'], [inHC, 'happy']],
    actions: [{ at: L4, kind: 'hop', dur: 14 }, { at: END_BEAT + 32, kind: 'hop', dur: 16 }],
    phase: 1.1,
  },
  {
    // Stands beside the Triceratops for scale while its size is listed.
    id: 'pal-scale', species: 'paleontologist', position: [7.4, 0, -0.6], flipX: true, visible: [triL4, L5 - 1],
    speakRanges: PALEO_SPEAK,
    poses: [[triL4, 'default'], [skull25, 'eureka']],
    actions: [{ at: skull25, kind: 'hop', dur: 16 }],
    phase: 0.6,
  },
  {
    id: 'trex-a', species: 'trex', position: TREX_A, visible: [0, DURATION], hidden: [[L6c, L7 - 1]],
    moves: [
      { f: 0, pos: TREX_A }, { f: sneak, pos: TREX_A },
      { f: sneak + 40, pos: [-4.2, 0, -6.6], ease: walkEase },   // sneaks round the back
      { f: hornL6 + 2, pos: [-4.2, 0, -6.6] },
      { f: thisL6 - 1, pos: [-6.0, 0, -3], ease: walkEase },     // off screen during the horn insert
    ],
    poses: [[0, 'smug'], [meters12, 'angry'], [strongest, 'roaring'], [L4, 'default'], [thisL6, 'angry'], [face, 'scared'],
      [L7, 'default'], [inHC, 'default'], [fought, 'surprised'], [END_BEAT, 'scared']],
    actions: [{ at: strongest, kind: 'roar', dur: 36 }, { at: bite1, kind: 'stomp', dur: 18 }, { at: thisL6 + 4, kind: 'lunge', dur: 18 },
      { at: face + 4, kind: 'recoil', dur: 22 }, { at: fought + 4, kind: 'recoil', dur: 22 }, { at: END_BEAT + 3, kind: 'recoil', dur: 26 }],
  },
  {
    id: 'tri-a', species: 'triceratops', position: [4.5, 0, -3], flipX: true, visible: [0, DURATION],
    poses: [[0, 'default'], [thisTri, 'happy'], [L4, 'smug'], [horns, 'angry'], [face, 'charging'], [that, 'angry'], [L6c, 'smug'], [locking, 'charging'], [L7, 'default'],
      [fought, 'charging'], [END_BEAT + 30, 'smug']],
    actions: [{ at: thisTri, kind: 'hop', dur: 18 }, { at: face, kind: 'stomp', dur: 20 }, { at: swiveled, kind: 'pivot', dur: 24 }, { at: locking, kind: 'lunge', dur: 18 },
      { at: fought, kind: 'stomp', dur: 22 }, { at: END_BEAT, kind: 'stomp', dur: 22 }],
    phase: 1.3,
  },
  {
    // "Locking horns with rivals": a second Triceratops takes the T. rex's place, brow horns meeting near x 1.
    id: 'tri-b', species: 'triceratops', position: [-2.6, 0, -3.1], visible: [L6c, L7 - 1],
    poses: [[L6c, 'angry'], [locking, 'charging']],
    actions: [{ at: L6c, kind: 'stomp', dur: 18 }, { at: locking, kind: 'lunge', dur: 18 }],
    phase: 0.4,
  },
  {
    // "Look at this": faces the horn on the ground.
    id: 'pal-horn', species: 'paleontologist', position: [13.4, 0, 3.4], flipX: true, visible: [L2, L3 - 1],
    speakRanges: PALEO_SPEAK,
    poses: [[L2, 'smug'], [look, 'happy'], [healed, 'eureka']],
    actions: [{ at: look, kind: 'hop', dur: 14 }, { at: healed, kind: 'hop', dur: 18 }],
    phase: 0.9,
  },
  {
    // Beside the fossil skull; steps out of the head-pop shot.
    id: 'pal-skull', species: 'paleontologist', position: [12.4, 0, 3.8], visible: [L8, inHC - 1], hidden: [[L9, L11 - 1]],
    speakRanges: PALEO_SPEAK,
    poses: [[L8, 'smug'], [other, 'default'], [L11, 'smug']],
    actions: [{ at: L8, kind: 'hop', dur: 14 }, { at: L11, kind: 'hop', dur: 14 }],
    phase: 0.5,
  },
  {
    // Looms over the fossil skull, grips the frill, pulls, and the head pops off.
    id: 'trex-pop', species: 'trex', position: [20.4, 0, 0.6], flipX: true, visible: [L9, L10 - 1],
    moves: [{ f: L9, pos: [23.0, 0, 0.6] }, { f: gripped - 2, pos: [20.4, 0, 0.6], ease: walkEase }],
    poses: [[L9, 'angry'], [gripped, 'roaring'], [popped, 'happy'], [jar, 'smug']],
    actions: [{ at: gripped, kind: 'lunge', dur: 18 }, { at: pulled, kind: 'recoil', dur: 18 }, { at: popped, kind: 'hop', dur: 20 }],
  },
];

const HORN_MPP = 0.9 / 594;   // horn core ~0.9 m, drawn 594 px base to tip
const SKULL_MPP = 2.3 / 842;  // skull 2.3 m beak to frill, under the 2.5 m maximum
export const PROPS: PropSpec[] = [
  {
    id: 'horn', file: 'horn-healed', size: [800, 360], mpp: HORN_MPP, anchor: [400, 306], keys: [{ f: 0, pos: HORN }], visible: [0, L8 - 1],
    rings: [
      { px: [398, 180], r: 34, at: tooth, until: thisTri - 1 }, { px: [470, 160], r: 30, at: tooth + 4, until: thisTri - 1 },
      { px: [398, 180], r: 34, at: hornL6, until: thisL6 - 1 }, { px: [470, 160], r: 30, at: hornL6 + 4, until: thisL6 - 1 },
    ],
  },
  { id: 'neck', file: 'neck-bones', size: [760, 300], mpp: SKULL_MPP, anchor: [64, 206], keys: [{ f: 0, pos: SK }], visible: [0, DURATION] },
  {
    id: 'skull', file: 'trike-skull', size: [1000, 620], mpp: SKULL_MPP, anchor: [626, 420], visible: [0, DURATION],
    keys: [
      { f: 0, pos: SK }, { f: pulled, pos: SK },
      { f: pulled + 5, pos: [SK[0] + 0.08, SK[1] + 0.03, SK[2]], rot: -0.05 }, { f: pulled + 10, pos: SK },
      { f: popped - 4, pos: SK }, { f: popped, pos: [SK[0] + 0.1, SK[1] + 0.04, SK[2]], rot: -0.08 },
      // pops up, flips once, lands upright in front of the host
      { f: popped + 10, pos: [SK[0] - 0.6, 2.6, SK[2] + 1.1], rot: Math.PI, ease: Easing.out(Easing.quad) },
      { f: popped + 21, pos: [SK[0] - 1.2, SK[1], SK[2] + 2.2], rot: 2 * Math.PI, ease: Easing.in(Easing.quad) },
      { f: popped + 26, pos: [SK[0] - 1.3, SK[1] + 0.25, SK[2] + 2.25], rot: 2 * Math.PI + 0.06, ease: Easing.out(Easing.quad) },
      { f: popped + 31, pos: [SK[0] - 1.35, SK[1], SK[2] + 2.3], rot: 2 * Math.PI, ease: Easing.in(Easing.quad) },
    ],
    rings: [{ px: [770, 210], r: 80, at: bites, until: neckJoint - 2 }, { px: [626, 422], r: 34, at: neckJoint, until: L9 - 1 }],
  },
];
const SK_LANDED: [number, number, number] = [SK[0] - 1.35, SK[1], SK[2] + 2.3];

// --- Camera: 21 shots, each framed on the speaker or on what the line names ---
const glide = Easing.inOut(Easing.cubic);
const drift = Easing.inOut(Easing.sin);
export const CAMERA: CameraKey[] = [
  // L1 "T. rex versus Triceratops?": wide face-off, Skeptic in front, slow push
  { f: 0, pos: [0.0, 3.0, 15.0], target: [-0.4, 2.4, -2], fov: 42 },
  { f: easy - 1, pos: [-0.2, 2.8, 13.6], target: [-0.6, 2.3, -2], fov: 41, ease: drift },
  // "Easy. That's just lunch.": Skeptic medium
  { f: easy, pos: [-2.0, 1.6, 9.2], target: [-2.0, 1.45, 5.0], fov: 34, cut: true },
  { f: L2 - 1, pos: [-2.0, 1.6, 8.6], target: [-2.0, 1.45, 5.0], fov: 33, ease: drift },
  // L2 "Is it? Look at this.": host at the fossil spot, then down to the horn
  { f: L2, pos: [13.0, 1.5, 8.6], target: [13.0, 1.15, 3.4], fov: 36, cut: true },
  { f: look, pos: [13.0, 1.5, 8.4], target: [13.0, 1.15, 3.4], fov: 36, ease: drift },
  { f: horn1 - 1, pos: [12.4, 1.0, 7.0], target: [12.3, 0.5, HORN[2]], fov: 36, ease: glide },
  // "A Triceratops horn with T. rex tooth marks... It healed.": horn insert, pushing in on the pits
  { f: horn1, pos: [12.25, 0.6, 7.0], target: [12.25, 0.3, HORN[2]], fov: 40, cut: true },
  { f: healed, pos: [12.3, 0.42, 4.9], target: [12.3, 0.33, HORN[2]], fov: 38, ease: glide },
  { f: thisTri - 1, pos: [12.3, 0.42, 4.7], target: [12.3, 0.33, HORN[2]], fov: 38, ease: drift },
  // "This Triceratops survived.": the survivor, close
  { f: thisTri, pos: [2.4, 2.2, 3.6], target: [2.0, 1.8, -3], fov: 36, cut: true },
  { f: L3 - 1, pos: [2.3, 2.1, 3.0], target: [2.0, 1.8, -3], fov: 35, ease: drift },
  // L3 "Survived a T. rex?!": Skeptic snap close-up
  { f: L3, pos: [-2.0, 1.7, 7.6], target: [-2.0, 1.6, 5.0], fov: 30, cut: true },
  { f: meters12 - 1, pos: [-2.0, 1.7, 7.3], target: [-2.0, 1.6, 5.0], fov: 30, ease: drift },
  // "Twelve meters, and the strongest bite...": low hero shot on the T. rex
  { f: meters12, pos: [0.6, 0.8, 6.0], target: [-2.6, 3.5, -3], fov: 44, cut: true },
  { f: L4 - 1, pos: [0.3, 1.0, 5.2], target: [-2.4, 3.7, -3], fov: 42, ease: drift },
  // L4 "True. But...": host medium
  { f: L4, pos: [1.2, 1.6, 9.2], target: [1.2, 1.45, 5.0], fov: 34, cut: true },
  { f: triL4 - 1, pos: [1.2, 1.6, 8.8], target: [1.2, 1.45, 5.0], fov: 33, ease: drift },
  // "Triceratops was no snack. Nine meters... skull... horns": host for scale, then along to the head and horns
  { f: triL4, pos: [7.4, 1.9, 7.0], target: [6.6, 1.7, -2], fov: 42, cut: true },
  { f: skull25, pos: [3.4, 2.0, 4.6], target: [2.2, 1.9, -3], fov: 38, ease: glide },
  { f: L5 - 1, pos: [2.6, 2.1, 3.0], target: [1.6, 2.1, -3], fov: 34, ease: drift },
  // L5 "So? Sneak around and bite the neck.": Skeptic in front, T. rex creeping round behind
  { f: L5, pos: [-1.2, 2.8, 13.4], target: [-2.0, 2.2, -3], fov: 42, cut: true },
  { f: L6 - 1, pos: [-1.0, 2.9, 12.8], target: [-2.0, 2.2, -3], fov: 42, ease: drift },
  // L6 "The bite's on the horn.": horn insert callback
  { f: L6, pos: [12.3, 0.45, 5.4], target: [12.3, 0.33, HORN[2]], fov: 38, cut: true },
  { f: thisL6 - 1, pos: [12.3, 0.45, 5.2], target: [12.3, 0.33, HORN[2]], fov: 38, ease: drift },
  // "This fight was face to face.": side-on two-shot of the heads
  { f: thisL6, pos: [0.0, 3.0, 9.5], target: [0.0, 3.0, -3], fov: 40, cut: true },
  { f: that - 1, pos: [0.0, 3.0, 8.8], target: [0.0, 3.0, -3], fov: 40, ease: drift },
  // "That huge head swivelled on a ball-and-socket joint.": Triceratops head close
  { f: that, pos: [2.6, 2.0, 3.4], target: [1.8, 1.9, -3], fov: 34, cut: true },
  { f: L6b - 1, pos: [2.5, 2.0, 3.0], target: [1.8, 1.9, -3], fov: 33, ease: drift },
  // L6b "Wait, so those horns were for fighting T. rex?": Skeptic in front, Triceratops behind
  { f: L6b, pos: [-2.8, 1.9, 10.6], target: [0.8, 1.7, -2], fov: 40, cut: true },
  { f: L6c - 1, pos: [-2.6, 1.9, 10.0], target: [0.8, 1.7, -2], fov: 40, ease: drift },
  // L6c "And each other... locking horns with rivals.": two Triceratops head to head, low three-quarter
  { f: L6c, pos: [1.8, 1.3, 7.4], target: [0.8, 1.9, -3], fov: 42, cut: true },
  { f: L7 - 1, pos: [1.6, 1.3, 6.6], target: [0.8, 1.9, -3], fov: 40, ease: drift },
  // L7 "Okay... so did T. rex ever win?": Skeptic close
  { f: L7, pos: [-1.8, 1.65, 7.4], target: [-2.0, 1.6, 5.0], fov: 30, cut: true },
  { f: L8 - 1, pos: [-1.8, 1.65, 7.1], target: [-2.0, 1.6, 5.0], fov: 30, ease: drift },
  // L8 "Oh, it ate plenty. Other skulls...": host and the fossil skull, pushing in to the bite marks and the neck joint
  { f: L8, pos: [13.3, 1.8, 11.0], target: [13.3, 1.0, 3.0], fov: 44, cut: true },
  { f: bites, pos: [14.9, 0.95, 6.6], target: [14.8, 0.4, SK[2]], fov: 40, ease: glide },
  { f: L9 - 1, pos: [14.7, 0.75, 6.2], target: [14.6, 0.15, SK[2]], fov: 38, ease: drift },
  // L9 "T. rex gripped the frill, pulled... popped the head off. Like a jar lid.": T. rex looms over the skull
  { f: L9, pos: [12.4, 1.3, 10.4], target: [14.6, 2.2, 1.8], fov: 46, cut: true },
  { f: popped, pos: [12.6, 1.3, 9.8], target: [14.4, 2.0, 2.0], fov: 45, ease: drift },
  { f: L10 - 1, pos: [12.6, 1.2, 9.6], target: [13.8, 1.3, 3.2], fov: 44, ease: glide },
  // L10 "It popped... the head... OFF?!": Skeptic, low and close
  { f: L10, pos: [-1.5, 1.25, 7.3], target: [-2.0, 1.75, 5.0], fov: 32, cut: true },
  { f: L11 - 1, pos: [-1.5, 1.25, 7.0], target: [-2.0, 1.75, 5.0], fov: 32, ease: drift },
  // L11 "Only after the fight.": host beside the popped skull
  { f: L11, pos: [12.8, 1.5, 9.8], target: [12.8, 1.2, 4.2], fov: 38, cut: true },
  { f: inHC - 1, pos: [12.8, 1.5, 9.4], target: [12.8, 1.2, 4.2], fov: 38, ease: drift },
  // "In Hell Creek, dinner fought back.": all four in the clearing, pulling back
  { f: inHC, pos: [0.2, 3.0, 15.0], target: [0.0, 2.4, -2], fov: 44, cut: true },
  { f: DURATION, pos: [0.2, 4.0, 18.0], target: [0.0, 2.2, -2], fov: 44, ease: drift },
];

export const CAMERA_SHAKES: CameraShake[] = [
  { at: bite1, strength: 0.15, dur: 14 },
  { at: face, strength: 0.12, dur: 12 },
  { at: locking, strength: 0.12, dur: 12 },
  { at: popped, strength: 0.17, dur: 14 },
  { at: popped + 21, strength: 0.1, dur: 10 },
  { at: fought, strength: 0.14, dur: 12 },
  { at: END_BEAT, strength: 0.12, dur: 12 },
];

export type Badge = { text: string; at: number; until: number; anchor: [number, number, number]; hot?: boolean };
export const BADGES: Badge[] = [
  { text: 'TOOTH MARKS', at: tooth, until: healed - 3, anchor: [12.25, 0.62, HORN[2]] },
  { text: 'HEALED', at: healed, until: thisTri - 3, anchor: [12.3, 0.62, HORN[2]], hot: true },
  { text: '12 m', at: meters12, until: L4 - 4, anchor: [-4.5, 5.6, -3] },
  { text: '~35,000 N', at: bite1, until: L4 - 4, anchor: [-1.8, 4.9, -3], hot: true },
  { text: '9 m', at: nine, until: tons - 2, anchor: [6.5, 3.0, -3] },
  { text: 'UP TO 12 t', at: tons, until: skull25 - 2, anchor: [6.0, 3.0, -3] },
  { text: '2.5 m SKULL', at: skull25, until: horns - 2, anchor: [1.6, 3.0, -3] },
  { text: '1 m HORNS', at: horns, until: L5 - 4, anchor: [0.9, 2.9, -3] },
  { text: 'FACE TO FACE', at: face, until: that - 2, anchor: [0.0, 4.9, -3], hot: true },
  { text: 'BALL-AND-SOCKET', at: ball, until: L6b - 4, anchor: [2.9, 2.6, -3] },
  { text: 'HEALED FRILLS', at: healedL6c, until: locking - 2, anchor: [1.0, 3.4, -3] },
  { text: 'HORN LOCK', at: locking, until: L7 - 4, anchor: [1.0, 3.6, -3], hot: true },
  { text: 'NEVER HEALED', at: never, until: L9 - 3, anchor: [SK[0] + 0.3, 1.15, SK[2]], hot: true },
  { text: 'JAR LID?!', at: jar, until: L10 - 2, anchor: [SK_LANDED[0], 1.5, SK_LANDED[2]], hot: true },
];

/** Comic glint on the brow-horn tip ("horns a meter long"). */
export const GLINT = { at: meterHorn, anchor: [0.6, 2.4, -3] as [number, number, number] };

// SFX at -10..-6 dB peak, unducked, 2 frames early (ANIMATION_GUIDE.md:149).
export const SFX: { file: string; at: number }[] = [
  { file: 'whoosh', at: 4 }, { file: 'pop', at: easy },
  { file: 'whoosh', at: L2 }, { file: 'paper-snap', at: horn1 }, { file: 'pop', at: tooth }, { file: 'shing', at: healed },
  { file: 'whoosh', at: thisTri },
  { file: 'pop', at: L3 }, { file: 'stomp-thud', at: meters12 }, { file: 'jaw-crunch', at: bite1 },
  { file: 'whoosh', at: L4 }, { file: 'whoosh', at: triL4 }, { file: 'paper-snap', at: nine }, { file: 'paper-snap', at: tons },
  { file: 'paper-snap', at: skull25 }, { file: 'shing', at: GLINT.at },
  { file: 'pop', at: L5 }, { file: 'whoosh', at: sneak },
  { file: 'whoosh', at: L6 }, { file: 'stomp-thud', at: face }, { file: 'whoosh', at: swiveled }, { file: 'paper-snap', at: ball },
  { file: 'pop', at: L6b }, { file: 'whoosh', at: L6c }, { file: 'paper-snap', at: healedL6c }, { file: 'stomp-thud', at: locking },
  { file: 'pop', at: L7 },
  { file: 'whoosh', at: L8 }, { file: 'paper-snap', at: never },
  { file: 'stomp-thud', at: L9 }, { file: 'jaw-crunch', at: gripped }, { file: 'pop', at: popped }, { file: 'stomp-thud', at: popped + 21 },
  { file: 'paper-snap', at: jar },
  { file: 'pop', at: L10 }, { file: 'whoosh', at: inHC }, { file: 'stomp-thud', at: fought },
  { file: 'stomp-thud', at: END_BEAT }, { file: 'pop', at: END_BEAT + 27 },
].map((s) => ({ ...s, at: Math.max(0, s.at - 2) }));

/** Ambient bed: one day loop for the whole episode. */
export const BED: { file: string; from: number; to: number }[] = [{ file: 'bed-day', from: 0, to: DURATION }];

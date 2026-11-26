import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Dreadnoughtus schrani, the series titanosaur (RESEARCH_GUIDE.md). Import has no side effects; run as a script to
write the SVG and GSAP page.

Built skeleton first, in metres, from the describing team's figures (Lacovara et al. 2014, via Drexel's FAQ):
26 m long = head about 0.9 m + neck 11.3 m + torso and hips 5.1 m + tail 8.7 m. The neck is held low, closer to
horizontal than in Brachiosaurus, as Lacovara et al. reconstructed it; forelimbs long but not much longer than the
hind limbs; wide-gauge columnar stance. RECONSTRUCTED from other titanosaurs: the skull (only a maxilla fragment
and a tooth are known), most of the neck (one cervical per specimen), the hand (not preserved; titanosaur hands were
columns of metacarpals without fingers or claws) and most of the foot (metatarsals I-II and the digit I claw are
known). Hip height is about 4.2 m to the top of the pelvis (UNVERIFIED: the guide's working ~3.9 m; Wikipedia's 6 m
shoulder height is unexplained). No osteoderms: none are reported for this animal."""
import sys
sys.path.insert(0, HERE)
import dinokit as K
from dinokit import OL, CLAW, path, line, piv, dots

C = "tit"
LOOK = K.Look(C, skin="#A08672", belly="#DCCDB6", accent="#8A5A4A")   # dusty clay, artistic interpretation
S = 36                                   # drawing units per metre
F = K.Frame(386, 362, S)                 # x 0 = hip socket, y 0 = ground
FAR = (0.5, 0.2)                         # three-quarter view: far-side limbs sit forward and higher

def part(pts, **kw): return K.rig_part(LOOK, pts, **kw)

def m(ps, off=(0, 0)): return F.pts([(x + off[0], y + off[1]) for x, y in ps])

# ------------------------------------------------------------------ skeleton (metres): joint centres
HIP, KNEE, ANKLE = (0, 3.35), (0.1, 1.6), (0.05, 0.48)
SHOULDER, ELBOW, WRIST = (3.5, 3.45), (3.52, 1.8), (3.53, 0.62)

# ------------------------------------------------------------------ hind limbs: thigh > shin > foot > toes (digits I-III clawed)
THIGH = [(0.75, 3.95), (0.88, 3.0), (0.62, 2.1), (0.45, 1.6), (0.1, 1.42), (-0.25, 1.55), (-0.5, 2.4), (-0.75, 3.4), (-0.6, 3.95), (0.1, 4.12)]
SHIN = [(0.42, 1.75), (0.4, 1.1), (0.36, 0.55), (0.05, 0.42), (-0.27, 0.55), (-0.3, 1.1), (-0.28, 1.72), (0.07, 1.9)]
FOOT = [(-0.33, 0.62), (0.38, 0.62), (0.62, 0.4), (0.84, 0.13), (0.8, 0.0), (-0.48, 0.0), (-0.58, 0.16), (-0.5, 0.42)]
TOES = [((0.66, 0.36), 0.3, 0.13), ((0.76, 0.22), 0.24, 0.11), ((0.82, 0.1), 0.17, 0.09)]   # (base, length, height)

def hind_leg(side):
    far = side == "far"; o = FAR if far else (0, 0)
    toes = "".join(piv(f"toe-{side}-{i + 1}", f"{C}-toe", *F(b[0] + o[0], b[1] + o[1]),
                       path(K.smooth(m(K.claw(b, ln, h), o))[0], CLAW, 0.85 if far else None))
                   for i, (b, ln, h) in enumerate(TOES))
    foot = piv(f"foot-{side}", f"{C}-foot", *F(ANKLE[0] + o[0], ANKLE[1] + o[1]), toes + part(m(FOOT, o), far=far, tex=False))
    shin = piv(f"shin-{side}", f"{C}-shin", *F(KNEE[0] + o[0], KNEE[1] + o[1]), part(m(SHIN, o), far=far) + foot)
    return piv(f"leg-{side}", f"{C}-leg", *F(HIP[0] + o[0], HIP[1] + o[1]), shin + part(m(THIGH, o), skip=(8, 9), seam=(0, 1, 2, 6, 7), far=far, seam_op=0.22))

# ------------------------------------------------------------------ forelimbs: upper arm > forearm > hand (metacarpal column, no fingers)
UPPER_ARM = [(3.0, 4.3), (3.95, 4.25), (4.1, 3.4), (3.95, 2.4), (3.82, 1.75), (3.5, 1.62), (3.22, 1.8), (3.12, 2.5), (2.95, 3.4), (2.8, 4.0)]
FOREARM = [(3.82, 1.95), (3.83, 1.2), (3.8, 0.62), (3.5, 0.55), (3.27, 0.62), (3.25, 1.2), (3.24, 1.92), (3.52, 2.05)]
HAND = [(3.25, 0.72), (3.82, 0.72), (3.9, 0.35), (3.93, 0.0), (3.16, 0.0), (3.18, 0.35)]
DIGITS = "M{} L{} M{} L{} M{} L{}"     # grooves between the metacarpal pads at the front of the hand

def foreleg(side):
    far = side == "far"; o = FAR if far else (0, 0)
    g = [F(x + o[0], y + o[1]) for x, y in [(3.5, 0.0), (3.52, 0.2), (3.66, 0.0), (3.68, 0.22), (3.8, 0.0), (3.82, 0.2)]]
    digits = f'<g id="digits-{side}" class="{C}-digits">{line(DIGITS.format(*(K._f(p) for p in g)), 0.4, 2)}</g>'
    hand = piv(f"hand-{side}", f"{C}-hand", *F(WRIST[0] + o[0], WRIST[1] + o[1]), part(m(HAND, o), far=far, tex=False) + digits)
    forearm = piv(f"forearm-{side}", f"{C}-forearm", *F(ELBOW[0] + o[0], ELBOW[1] + o[1]), part(m(FOREARM, o), far=far) + hand)
    return piv(f"foreleg-{side}", f"{C}-foreleg", *F(SHOULDER[0] + o[0], SHOULDER[1] + o[1]), forearm + part(m(UPPER_ARM, o), skip=(9, 0), seam=(1, 6, 7, 8), far=far, seam_op=0.22))

# ------------------------------------------------------------------ tail: five nested segments on one centreline
TAIL_SPINE = K.Spine([(*F(x, y), d * S) for x, y, d in
                      [(0.2, 3.5, 1.25), (-1.0, 3.5, 1.1), (-2.6, 3.27, 0.9), (-4.2, 2.88, 0.68), (-5.8, 2.38, 0.48), (-7.6, 1.78, 0.3), (-9.6, 1.15, 0.08)]])
TAIL_CUTS = [0, 0.22, 0.42, 0.6, 0.8, 1.0]

TAIL = K.segmented(LOOK, TAIL_SPINE, TAIL_CUTS, ["tail", "tail-2", "tail-3", "tail-4", "tail-5"], 0.4 * S, [3, 3, 3, 3, 2], tip_cap=0.5)

# ------------------------------------------------------------------ head: skull with upper jaw, lower jaw on its own hinge (RECONSTRUCTED)
# local frame in metres from the back of the skull, x along the skull; titanosaur comparison: long, low skull,
# narrow snout, nostrils retracted above the eyes, slender lower jaw
HF = K.Frame(0, 0, S)
SKULL = [(-0.08, 0.12), (0.04, 0.3), (0.22, 0.37), (0.38, 0.34), (0.5, 0.35), (0.62, 0.27), (0.8, 0.16), (0.93, 0.08),
         (0.97, 0.0), (0.93, -0.07), (0.7, -0.08), (0.4, -0.09), (0.15, -0.13), (0.0, -0.15), (-0.1, -0.04)]
UPPER_JAW = [(0.3, -0.03), (0.6, -0.01), (0.86, 0.02), (0.96, 0.0), (0.93, -0.07), (0.7, -0.08), (0.4, -0.09), (0.28, -0.08)]
TEETH = [(0.5, -0.08), (0.92, -0.06), (0.92, -0.11), (0.5, -0.12)]
LOWER_JAW = [(0.02, -0.06), (0.3, -0.085), (0.6, -0.075), (0.88, -0.065), (0.95, -0.1), (0.9, -0.16), (0.6, -0.19), (0.3, -0.2), (0.05, -0.17), (-0.04, -0.11)]
JAW_HINGE = (0.08, -0.1)

def hp(ps): return HF.pts(ps)
JAW = piv("jaw", f"{C}-jaw", *HF(*JAW_HINGE), part(hp(LOWER_JAW), tex=False, belly=K.smooth(hp([(0.1, -0.15), (0.6, -0.165), (0.9, -0.14), (0.86, -0.165), (0.6, -0.185), (0.3, -0.195), (0.08, -0.17)]))[0]))
UPPER = (f'<g id="upper-jaw" class="{C}-upper-jaw">' + path(K.smooth(hp(TEETH))[0], K.IVORY)
         + part(hp(UPPER_JAW), skip=(0, 1, 2, 7), tex=False) + "</g>")
ex, ey = HF(0.3, 0.19); nx_, ny_ = HF(0.5, 0.27)
SKULL_G = (f'<g id="skull" class="{C}-skull">' + part(hp(SKULL), light=True, tex=False)
           + f'<ellipse cx="{nx_}" cy="{ny_}" rx="2.2" ry="1.4" fill="{OL}" opacity="0.7"></ellipse>'
           + K.eye(ex, ey, f"{C}-eyelid", r=2.2) + "</g>")
HEAD_ANGLE = 16                          # degrees, snout tipped down at rest

# ------------------------------------------------------------------ neck: four nested segments, head at the end (most of it RECONSTRUCTED)
NECK_SPINE = K.Spine([(*F(x, y), d * S) for x, y, d in
                      [(3.9, 3.65, 2.4), (6.0, 4.88, 1.8), (8.6, 6.25, 1.35), (11.4, 7.08, 1.02), (14.5, 7.55, 0.68)]])
hx, hy, htx, hty, _ = NECK_SPINE.at(NECK_SPINE.length)
HEAD = (f'<g transform="translate({hx:.1f} {hy:.1f}) rotate({HEAD_ANGLE})">'
        + piv("head", f"{C}-head", 0, 0, SKULL_G + UPPER + JAW) + "</g>")
NECK = K.segmented(LOOK, NECK_SPINE, [0, 0.3, 0.53, 0.76, 1.0], ["neck", "neck-2", "neck-3", "neck-4"], 0.35 * S, [3, 3, 3, 2], tip_cap=0.1, end=HEAD)
# ------------------------------------------------------------------ torso: abdomen (whole barrel) under chest and pelvis
BARREL = [(-1.45, 3.85), (-0.7, 4.1), (0.3, 4.2), (1.5, 4.26), (2.6, 4.45), (3.5, 4.78), (4.3, 5.06), (4.95, 4.95), (5.05, 3.9),
          (4.5, 2.85), (3.7, 1.95), (2.8, 1.58), (1.8, 1.5), (0.8, 1.62), (-0.2, 2.05), (-0.9, 2.55), (-1.4, 2.95), (-1.65, 3.45)]
BELLY = [(4.5, 2.85), (3.7, 1.95), (2.8, 1.58), (1.8, 1.5), (0.8, 1.62), (-0.2, 2.05), (-0.2, 2.5), (0.8, 2.1), (1.8, 1.98), (2.8, 2.05), (3.6, 2.38), (4.3, 3.15)]
CHEST = [(1.9, 4.33), (2.6, 4.45), (3.5, 4.78), (4.3, 5.06), (4.95, 4.95), (5.05, 3.9), (4.5, 2.85), (3.7, 1.95), (2.8, 1.58), (2.2, 1.52), (1.9, 2.4), (1.75, 3.5)]
CHEST_BELLY = [(4.5, 2.85), (3.7, 1.95), (2.8, 1.58), (2.2, 1.52), (2.2, 1.98), (2.8, 2.05), (3.6, 2.38), (4.3, 3.15)]
PELVIS = [(-1.45, 3.85), (-0.7, 4.1), (0.3, 4.2), (1.2, 4.24), (1.35, 3.6), (1.1, 2.4), (0.5, 1.8), (-0.2, 2.05), (-0.9, 2.55), (-1.4, 2.95), (-1.65, 3.45)]
BACK = K.Spine([(*F(x, y + 0.0), 0.9 * S) for x, y in [(-1.2, 3.55), (0.3, 3.75), (1.9, 3.85), (3.4, 4.25), (4.6, 4.5)]])
body_poly = m([(-1.2, 3.8), (1.5, 4.1), (4.4, 4.7), (4.3, 2.4), (2.0, 1.9), (-0.8, 2.7)])
BODY = piv("body", f"{C}-body", *F(1.6, 2.0), (
    f'<g id="abdomen" class="{C}-abdomen">' + part(m(BARREL), skip=(6, 7), seam=(8,), seam_op=0.18, belly=K.smooth(m(BELLY))[0], layers=dots(body_poly, 60, 1.2, 2.0, 0.08, seed=11)) + "</g>"
    + f'<g id="pelvis" class="{C}-pelvis">' + part(m(PELVIS), seam=(3, 4, 5), seam_op=0.1, layers=K.spine_stripes(BACK, 0, BACK.length * 0.42, 3)) + "</g>"
    + f'<g id="chest" class="{C}-chest">' + part(m(CHEST), skip=(3, 4), seam=(5, 9, 10, 11), seam_op=0.1, belly=K.smooth(m(CHEST_BELLY))[0],
                                                  layers=K.spine_stripes(BACK, BACK.length * 0.5, BACK.length, 3)) + "</g>"))

# ------------------------------------------------------------------ hidden skeletal guide (joint centres and spines, for editing)
def _guide():
    j = [HIP, KNEE, ANKLE, SHOULDER, ELBOW, WRIST]
    bones = f"M{K._f(F(*HIP))} L{K._f(F(*KNEE))} L{K._f(F(*ANKLE))} M{K._f(F(*SHOULDER))} L{K._f(F(*ELBOW))} L{K._f(F(*WRIST))}"
    spines = "".join(f'<path d="M' + " L".join(K._f(sp.at(sp.length * k / 20)[:2]) for k in range(21)) + '" fill="none" stroke="#3A7BD5" stroke-width="2"></path>'
                     for sp in (TAIL_SPINE, NECK_SPINE))
    dots_ = "".join(f'<circle cx="{F(*p)[0]}" cy="{F(*p)[1]}" r="4" fill="#E5484D"></circle>' for p in j)
    return (f'<g id="skeleton-guide" class="{C}-guide" display="none" pointer-events="none">'
            f'<path d="{bones}" fill="none" stroke="#3A7BD5" stroke-width="3"></path>{spines}{dots_}</g>')

FRAG = piv("act", f"{C}-act", *F(1.6, 0), hind_leg("far") + foreleg("far") + TAIL + NECK + BODY + hind_leg("near") + foreleg("near") + _guide())

# snout-to-tail midline in drawing units (the group poster measures length along it)
_ht = (hx + htx * 0.97 * S, hy + hty * 0.97 * S)
MIDLINE = ([TAIL_SPINE.at(TAIL_SPINE.length * (1 - k / 10))[:2] for k in range(11)] + [F(1.6, 3.3)]
           + [NECK_SPINE.at(NECK_SPINE.length * k / 10)[:2] for k in range(11)] + [_ht])

# ------------------------------------------------------------------ move: neck raise and call
ACTION = {
    "neck": [(0, "rotate(0)"), (0.3, "rotate(-6deg)"), (0.75, "rotate(-6deg)"), (1, "rotate(0)")],
    "neck-2": [(0, "rotate(0)"), (0.3, "rotate(-4deg)"), (0.75, "rotate(-4deg)"), (1, "rotate(0)")],
    "neck-3": [(0, "rotate(0)"), (0.3, "rotate(-3deg)"), (0.75, "rotate(-3deg)"), (1, "rotate(0)")],
    "head": [(0, "rotate(0)"), (0.3, "rotate(4deg)"), (0.75, "rotate(4deg)"), (1, "rotate(0)")],
    "jaw": [(0, "rotate(0)"), (0.32, "rotate(0)"), (0.45, "rotate(16deg)"), (0.52, "rotate(12deg)"), (0.6, "rotate(16deg)"), (0.7, "rotate(15deg)"), (0.82, "rotate(0)"), (1, "rotate(0)")],
    "tail": [(0, "rotate(0)"), (0.3, "rotate(2deg)"), (0.75, "rotate(2deg)"), (1, "rotate(0)")],
}
GSAP = """      .to(parts.neck, { rotation: -6, duration: 0.65, ease: 'power2.out' }, 0)
      .to(parts.neck_2, { rotation: -4, duration: 0.65, ease: 'power2.out' }, 0.05)
      .to(parts.neck_3, { rotation: -3, duration: 0.65, ease: 'power2.out' }, 0.1)
      .to(parts.head, { rotation: 4, duration: 0.65, ease: 'power2.out' }, 0.1)
      .to(parts.tail, { rotation: 2, duration: 0.65, ease: 'sine.out' }, 0)
      .to(parts.jaw, { rotation: 16, duration: 0.25, ease: 'power2.out' }, 0.7)
      .to(parts.jaw, { rotation: 12, duration: 0.12, yoyo: true, repeat: 3, ease: 'none' }, 0.95)
      .to(parts.jaw, { rotation: 0, duration: 0.25, ease: 'power2.in' }, 1.55)
      .to([parts.neck, parts.neck_2, parts.neck_3, parts.head, parts.tail], { rotation: 0, duration: 0.6, ease: 'power2.inOut' }, 1.6)"""

IDS = ["act", "body", "chest", "abdomen", "pelvis", "tail", "tail-2", "tail-3", "tail-4", "tail-5",
       "neck", "neck-2", "neck-3", "neck-4", "head", "skull", "upper-jaw", "jaw",
       "leg-near", "leg-far", "foreleg-near", "foreleg-far"]

SPEC = dict(
    code=C, slug="titanosaur", board="Titanosaur", name="Dreadnoughtus", short="titanosaur", look=LOOK,
    viewbox=(1000, 380), frag=FRAG, ids=IDS, action=ACTION, dur=2.2, gsap=GSAP,
    action_label="Make the titanosaur call", action_verb="make it call", page_bg="#D3DBDF",
    title="Dreadnoughtus", title_px=150, binomial="Dreadnoughtus schrani", subtitle="the titan from southern Patagonia",
    paragraph="One of the most complete giant titanosaurs: about 70% of its bone types (skull aside) were found. Its mass is debated, from about 22 to 59 tonnes depending on the method.",
    facts=[("26 m", "estimated length"), ("70%", "of bone types found, skull aside"), ("22–59 t", "mass, by method")],
    footer="Found in the Cerro Fortaleza Formation of Santa Cruz Province, Argentina; the type individual was still growing.",
    hint="Tap the titanosaur to make it call", skin_swatches=["#A08672", "#7C8AA0", "#9A8F7E", "#8A5A4A"],
    dino_top=60, midline=MIDLINE, ground=F.g,
)

if __name__ == "__main__":
    K.write_all(SPEC)          # this rework round: svg/ and gsap/ only; poster and rig board follow later
    print("ok")

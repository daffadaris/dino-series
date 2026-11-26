import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Tyrannosaurus rex for the dinosaur series (RESEARCH_GUIDE.md), the definitive build (it replaced the removed
boxy-head pipeline). Building SPEC has no side effects; run as a script to write the SVG and GSAP page.

Built skeleton first, in metres, as a 12 m adult (NHM; the most complete skeleton is 12.3-12.4 m), guide targets
checked: skull 1.45 m (12%), tail 5.5 m (45%), top of the hips 4.05 m (34%), forelimb about a quarter of the hind
limb. Horizontal, balanced posture. Deep skull, broad at the back, with a deep, robust snout; eyes placed high and
far back so they face partly forward; deep lower jaw. Lips cover the teeth when the mouth is closed (Cullen et al.
2023): the tooth rows are layered behind the jaws and show only when the jaw opens. Thick, recurved, serrated teeth of
varied size. Short, robust arms with two clawed fingers, palms facing inward (not mammal-like). Three weight-bearing
toes per foot with a small raised first toe. Small irregular scales, no feathers (Bell et al. 2017). Colour artistic."""
import sys, math
sys.path.insert(0, HERE)
import dinokit as K
from dinokit import SKIN, OL, D, CLAW, IVORY, path, stroke, line, piv, dots

C = "tr"
LOOK = K.Look(C, skin="#7A5C4C", belly="#DCC8A8", accent="#9C5B3F")   # earthy brown, rust accent: artistic
S = 72                                   # drawing units per metre
F = K.Frame(576, 514, S)                 # x 0 = hip socket, y 0 = ground
FAR = (0.22, 0.08)                       # three-quarter view: far-side limbs sit forward and higher

def part(pts, **kw): return K.rig_part(LOOK, pts, **kw)
def m(ps, off=(0, 0)): return F.pts([(x + off[0], y + off[1]) for x, y in ps])
def rot(ps, deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return [(x * c - y * s, x * s + y * c) for x, y in ps]
def shift(ps, o): return [(x + o[0], y + o[1]) for x, y in ps]
def margin(x, pts):
    pts = sorted(pts)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[0][1] if x < pts[0][0] else pts[-1][1]

# ------------------------------------------------------------------ skeleton (metres): joint centres
HIP, KNEE, ANKLE = (0, 3.1), (0.45, 1.82), (0.05, 0.72)
ARM_SHIFT = (-0.35, -0.2)                 # arm set low on the front of the chest
SHOULDER, ELBOW, WRIST = [(x + ARM_SHIFT[0], y + ARM_SHIFT[1]) for x, y in [(2.75, 2.85), (2.86, 2.5), (3.1, 2.34)]]

# ------------------------------------------------------------------ hind limbs: thigh > shin > foot > toes
THIGH = [(0.85, 3.4), (1.0, 2.75), (0.85, 2.1), (0.62, 1.7), (0.2, 1.62), (-0.4, 2.05), (-0.75, 2.75), (-0.85, 3.3), (-0.05, 3.6)]
SHIN = [(0.85, 2.05), (0.6, 1.2), (0.3, 0.78), (0.0, 0.62), (-0.25, 0.8), (0.05, 1.4), (0.2, 2.1)]
FOOT = [(-0.14, 0.86), (0.2, 0.84), (0.5, 0.3), (0.62, 0.12), (0.5, 0.0), (0.2, 0.0), (-0.18, 0.62)]
TOES = [((0.36, 0.1), 0.42, 0.11), ((0.44, 0.05), 0.5, 0.12), ((0.5, 0.0), 0.56, 0.13)]   # back to front: (base, length, depth)
HALLUX = [(-0.12, 0.55), (-0.26, 0.5), (-0.32, 0.42), (-0.2, 0.44)]                       # small first toe, raised off the ground

def toes(side, far, o):
    out = ""
    for i, ((bx, by), ln, h) in enumerate(TOES):
        toe = [(bx, by + h), (bx + ln * 0.7, by + h * 0.9), (bx + ln * 0.92, by + h * 0.5), (bx + ln * 0.9, by), (bx, by)]
        cl = shift(K.claw((0, 0), 0.16, h * 0.9), (bx + ln * 0.86, by + h * 0.45))
        out += piv(f"toe-{side}-{len(TOES) - i}", f"{C}-toe", *F(bx + o[0], by + o[1]),
                   part(m(toe, o), skip=(4,), far=far, tex=False) + path(K.smooth(m(rot_about(cl, (bx + ln * 0.86, by + h * 0.45), -18), o))[0], CLAW, 0.85 if far else None))
    return out

def rot_about(ps, c, deg): return shift(rot(shift(ps, (-c[0], -c[1])), deg), c)

def hind_leg(side):
    far = side == "far"; o = FAR if far else (0, 0)
    hallux = piv(f"toe-{side}-0", f"{C}-toe", *F(-0.12 + o[0], 0.55 + o[1]), path(K.smooth(m(HALLUX, o))[0], CLAW, 0.85 if far else None))
    foot = piv(f"foot-{side}", f"{C}-foot", *F(ANKLE[0] + o[0], ANKLE[1] + o[1]), hallux + part(m(FOOT, o), far=far, tex=False) + toes(side, far, o))
    shin = piv(f"shin-{side}", f"{C}-shin", *F(KNEE[0] + o[0], KNEE[1] + o[1]), foot + part(m(SHIN, o), far=far))
    thigh = f'<g id="thigh-{side}" class="{C}-thigh">' + part(m(THIGH, o), skip=(7, 8), seam=(0, 6), far=far, seam_op=0.3) + "</g>"
    return piv(f"leg-{side}", f"{C}-leg{'' if not far else '-far'}", *F(HIP[0] + o[0], HIP[1] + o[1]), shin + thigh)

# ------------------------------------------------------------------ arms: upper arm > forearm > two-fingered hand, palm facing in
UPPER_ARM = [(2.58, 3.08), (2.97, 3.06), (3.02, 2.75), (2.96, 2.5), (2.8, 2.42), (2.62, 2.58)]
FOREARM = [(2.76, 2.6), (2.96, 2.62), (3.14, 2.44), (3.1, 2.3), (2.96, 2.3), (2.76, 2.44)]
PALM = [(3.04, 2.42), (3.18, 2.42), (3.22, 2.32), (3.1, 2.26), (3.02, 2.32)]
FINGERS = [((3.18, 2.36), -35, 0.12, 0.11, 0.05), ((3.14, 2.3), -55, 0.14, 0.12, 0.05)]   # digits I and II: base, angle, length, claw, claw depth
UPPER_ARM, FOREARM, PALM = (shift(a, ARM_SHIFT) for a in (UPPER_ARM, FOREARM, PALM))
FINGERS = [(shift([b], ARM_SHIFT)[0], *rest) for b, *rest in FINGERS]

def finger(base, ang, flen, clen, ch):
    body = rot([(0, 0.028), (flen, 0.024), (flen + 0.015, 0), (flen, -0.024), (0, -0.028), (-0.015, 0)], ang)
    tip = rot([(flen, 0)], ang)[0]
    return shift(body, base), shift(rot(K.claw((0, 0), clen, ch), ang - 15), (base[0] + tip[0], base[1] + tip[1]))

def arm(side):
    far = side == "far"; o = FAR if far else (0, 0)
    fingers = ""
    for i, spec in enumerate(FINGERS):
        fb, cl = finger(*spec)
        fingers += piv(f"finger-{side}-{i + 1}", f"{C}-finger", *F(spec[0][0] + o[0], spec[0][1] + o[1]),
                       part(m(fb, o), far=far, tex=False) + path(K.smooth(m(cl, o))[0], CLAW, 0.85 if far else None))
    hand = piv(f"hand-{side}", f"{C}-hand", *F(WRIST[0] + o[0], WRIST[1] + o[1]), fingers + part(m(PALM, o), far=far, tex=False))
    forearm = piv(f"forearm-{side}", f"{C}-forearm", *F(ELBOW[0] + o[0], ELBOW[1] + o[1]), part(m(FOREARM, o), far=far) + hand)
    upper = f'<g id="upper-arm-{side}" class="{C}-upper-arm">' + part(m(UPPER_ARM, o), skip=(0,), seam=(5,), far=far, seam_op=0.3) + "</g>"
    return piv(f"arm-{side}", f"{C}-arm{'' if not far else '-far'}", *F(SHOULDER[0] + o[0], SHOULDER[1] + o[1]), forearm + upper)

# ------------------------------------------------------------------ tail: base, middle, tip (thick, muscular counterweight)
TAIL_SPINE = K.Spine([(*F(x, y), d * S) for x, y, d in
                      [(0.0, 3.1, 1.35), (-1.3, 3.1, 1.3), (-2.8, 2.9, 0.95), (-4.3, 2.62, 0.62), (-5.8, 2.38, 0.34), (-7.3, 2.28, 0.06)]])
TAIL = K.segmented(LOOK, TAIL_SPINE, [0, 0.33, 0.66, 1.0], ["tail", "tail-2", "tail-3"], 0.35 * S, [4, 4, 3], tip_cap=0.4, joint_cap=0.5, tight_joints=True)

# ------------------------------------------------------------------ head: skull (with upper lip) over the lower jaw; tooth rows behind both
HEAD_SCALE = 1.1                          # skull about 1.6 m (13% of length)
HF = K.Frame(0, 0, S * HEAD_SCALE)
SKULL = [(-0.08, 0.08), (-0.2, 0.45), (-0.12, 0.86), (0.06, 1.02), (0.28, 1.05), (0.48, 0.98), (0.58, 0.9), (0.75, 0.8), (1.0, 0.7),
         (1.22, 0.6), (1.4, 0.5), (1.5, 0.34), (1.51, 0.15), (1.44, 0.03), (1.0, 0.02), (0.6, 0.01), (0.3, 0.0), (0.12, -0.03)]
LOWER_JAW = [(-0.17, 0.02), (0.3, 0.0), (0.7, 0.01), (1.1, 0.025), (1.4, 0.04), (1.46, -0.04), (1.38, -0.15), (1.05, -0.25),
             (0.7, -0.36), (0.3, -0.45), (0.0, -0.4), (-0.2, -0.14)]
JAW_HINGE = (0.0, 0.0)
UPPER_TEETH = [(0.42, 0.09), (0.56, 0.13), (0.71, 0.16), (0.86, 0.15), (1.0, 0.13), (1.13, 0.12), (1.25, 0.1), (1.35, 0.08)]
LOWER_TEETH = [(0.5, 0.08), (0.64, 0.11), (0.79, 0.13), (0.93, 0.12), (1.06, 0.11), (1.18, 0.09), (1.27, 0.07)]

def tooth_row(gid, spec, y0, down):
    """thick, recurved teeth (curving back toward the throat) on a margin at y0"""
    out = ""
    for x, ln in spec:
        w = ln * 0.48; tip = (x - ln * 0.3, y0 - ln if down else y0 + ln)          # thick, banana-shaped
        pts = [(x - w, y0), (x - w * 0.6, y0 + (-ln * 0.55 if down else ln * 0.55)), tip, (x + w * 0.35, y0 + (-ln * 0.5 if down else ln * 0.5)), (x + w, y0)]
        fill, out_d = K.smooth(HF.pts(pts), skip=(4,))
        out += path(fill, IVORY) + stroke(out_d, 1.3)
    return f'<g id="{gid}" class="{C}-teeth">{out}</g>'

EYE_NEAR, EYE_FAR = (0.38, 0.72), (0.44, 0.52)
ex, ey = HF(*EYE_NEAR)
RIDGE_COLOUR = "#B5562E"                 # burnt-orange brow and nasal ridge: artistic, like the reference's display colour
RIDGE = [(0.26, 0.9), (0.36, 0.97), (0.46, 0.95), (0.56, 0.93), (0.66, 0.86), (0.8, 0.8), (0.95, 0.73), (1.08, 0.67), (1.15, 0.62),
         (1.06, 0.6), (0.9, 0.66), (0.72, 0.73), (0.56, 0.8), (0.42, 0.82), (0.3, 0.8)]
SKULL_G = (f'<g id="skull" class="{C}-skull">'
           + f'<g id="eye-far" class="{C}-eye-far">{K.eye(*HF(*EYE_FAR), f"{C}-eyelid", r=3.2)}</g>'    # far eye, behind the skull (forward-facing pair)
           + part(HF.pts(SKULL), light=True, skip=(0, 17), seam=(1,), seam_op=0.3)   # back of the skull flows from the neck; cheek tucks over the jaw joint
           + f'<g id="upper-jaw" class="{C}-upper-jaw">'
           + f'<ellipse cx="{HF(0.88, 0.44)[0]}" cy="{HF(0.88, 0.44)[1]}" rx="{0.26 * S * HEAD_SCALE:.1f}" ry="{0.12 * S * HEAD_SCALE:.1f}" fill="{D}" opacity="0.1"></ellipse>'   # skin over the antorbital opening
           + f'<ellipse cx="{HF(1.4, 0.42)[0]}" cy="{HF(1.4, 0.42)[1]}" rx="4" ry="2.4" fill="{OL}" opacity="0.55"></ellipse>'
           + line(f"M{K._f(HF(1.02, 0.36))} L{K._f(HF(1.2, 0.27))} M{K._f(HF(0.9, 0.24))} L{K._f(HF(1.04, 0.2))}", 0.0, 1.6).replace('stroke="#000000"', 'stroke="#E9DCC4"').replace('opacity="0.0"', 'opacity="0.55"')   # old scars
           + line(f"M{K._f(HF(0.2, 0.36))} Q{K._f(HF(0.3, 0.26))} {K._f(HF(0.26, 0.1))}", 0.16, 1.8)   # crease over the jaw muscles
           + "</g>"
           + path(K.smooth(HF.pts(RIDGE))[0], RIDGE_COLOUR) + path(K.smooth(HF.pts(RIDGE))[0], LOOK.url("shade"))
           + stroke(K.smooth(HF.pts(RIDGE))[0], 1.6, OL, 0.6)
           + "".join(f'<circle cx="{HF(x, y)[0]}" cy="{HF(x, y)[1]}" r="{r}" fill="{D}" opacity="0.18"></circle>' for x, y, r in
                     [(0.34, 0.9, 1.6), (0.47, 0.9, 1.8), (0.6, 0.86, 1.5), (0.74, 0.79, 1.4), (0.88, 0.73, 1.3), (1.0, 0.67, 1.2)])    # rugose texture
           + f'<g id="eye-near" class="{C}-eye">{K.eye(ex, ey, f"{C}-eyelid", r=3.4)}'
           + path(K.smooth(HF.pts([(0.28, 0.82), (0.52, 0.8), (0.48, 0.705), (0.38, 0.73), (0.29, 0.765)]))[0], SKIN)    # heavy lid slanting down toward the snout: a glare
           + stroke(f"M{K._f(HF(0.29, 0.765))} Q{K._f(HF(0.38, 0.735))} {K._f(HF(0.49, 0.7))}", 2.2) + "</g>" + "</g>")
JAW = piv("jaw", f"{C}-jaw", *HF(*JAW_HINGE),
          path(K.smooth(HF.pts([(0.2, 0.02), (0.6, 0.16), (0.95, 0.28), (1.2, 0.36), (1.28, 0.2), (1.24, 0.04), (0.8, 0.025), (0.45, 0.02)]))[0], "#4A2226")   # mouth lining that opens with the jaw; the skull hides it when closed
          + path(K.smooth(HF.pts([(0.05, 0.04), (0.6, 0.06), (1.0, 0.08), (0.95, 0.13), (0.5, 0.12), (0.1, 0.09)]))[0], "#8E4A4E")   # tongue
          + tooth_row("teeth-lower", LOWER_TEETH, 0.03, down=False)
          + part(HF.pts(LOWER_JAW), skip=(0, 10, 11), belly=K.smooth(HF.pts([(0.1, -0.34), (0.6, -0.3), (1.1, -0.17), (1.3, -0.14), (1.0, -0.23), (0.6, -0.34), (0.3, -0.43), (0.05, -0.38)]))[0]))
HEAD_ANGLE = 10
MOUTH = path(K.smooth(HF.pts([(0.0, 0.035), (0.7, 0.035), (1.3, 0.035), (1.3, -0.08), (0.7, -0.11), (0.05, -0.08)]))[0], "#4A2226")   # gum strip under the upper teeth; the closed jaw hides it

# ------------------------------------------------------------------ neck: short, thick, slight S-curve
NECK_SPINE = K.Spine([(*F(x, y), d * S) for x, y, d in [(1.6, 3.05, 1.15), (2.25, 3.5, 1.15), (2.75, 3.88, 1.05), (3.15, 4.0, 0.95)]])   # S-curve, muscle hump above the skull
HEAD_AT = F(2.92, 3.55)                     # jaw hinge: skull top continues the neck's top line, jaw underside the throat
hx, hy, *_ = NECK_SPINE.at(NECK_SPINE.length)
HEAD = (f'<g transform="translate({HEAD_AT[0]:.1f} {HEAD_AT[1]:.1f}) rotate({HEAD_ANGLE})">'
        + piv("head", f"{C}-head", 0, 0, MOUTH + tooth_row("teeth-upper", UPPER_TEETH, 0.03, down=True) + JAW + SKULL_G) + "</g>")
NECK = K.segmented(LOOK, NECK_SPINE, [0, 1.0], ["neck"], 0, [2], tip_cap=0.1, end=HEAD)

# ------------------------------------------------------------------ torso: deep chest and belly, broad pelvis
BACK = [(-1.45, 3.5), (-1.3, 3.6), (-0.6, 3.75), (0.3, 3.78), (0.9, 3.72), (1.35, 3.64)]
def neck_top(xm):
    """point on the neck's top edge (metres) nearest to x = xm"""
    tops = []
    for q in range(0, int(NECK_SPINE.length), 2):
        x, y, tx, ty, d = NECK_SPINE.at(q); nx, ny = -ty, tx
        if ny > 0: nx, ny = -nx, -ny
        tops.append(((x + nx * d / 2 - F.x0) / S, (F.g - (y + ny * d / 2)) / S))
    return min(tops, key=lambda p: abs(p[0] - xm))
FRONT_TOP = [neck_top(x) for x in (1.65, 2.0)]
FRONT_CAP = [(2.42, 4.05)]                         # just under the neck top, so the body's edge never bulges over it
def inset(ps, c=(1.0, 2.6), d=0.03):
    """pull a piece a hair inside the body outline so it never pokes past it"""
    return [(x + (c[0] - x) * d / max(math.dist((x, y), c), 1e-6), y + (c[1] - y) * d / max(math.dist((x, y), c), 1e-6)) for x, y in ps]             # inside the neck: no outline there                     # back line runs on into the neck top
BARREL = BACK[1:] + FRONT_TOP + FRONT_CAP + [(2.55, 2.95), (2.5, 2.45), (2.0, 2.1), (1.3, 1.8), (0.6, 1.45), (0.0, 1.62), (-0.5, 2.1), (-1.0, 2.45), (-1.4, 2.8), (-1.6, 3.2)]
nb = len(BACK) - 1 + len(FRONT_TOP)                                # index of the first front-cap point
BELLY = [(2.5, 2.45), (2.0, 2.1), (1.3, 1.8), (0.6, 1.45), (0.2, 1.55), (0.3, 1.95), (1.3, 2.2), (2.0, 2.5), (2.45, 2.8)]
CHEST = [(1.0, 3.7), (1.35, 3.64)] + FRONT_TOP + FRONT_CAP + [(2.55, 2.95), (2.5, 2.45), (2.0, 2.1), (1.3, 1.8), (1.1, 2.4), (1.05, 3.2)]
PELVIS = [(-1.3, 3.6), (-0.6, 3.75), (0.3, 3.78), (0.85, 3.72), (1.0, 3.0), (0.85, 1.5), (0.6, 1.45), (0.0, 1.62), (-0.5, 2.1), (-1.0, 2.45), (-1.4, 2.8), (-1.6, 3.2)]
BACK_SPINE = K.Spine([(*F(x, y - 0.52), 0.9 * S) for x, y in BACK[1:]])   # stripes start just under the back edge
body_poly = m([(-1.0, 3.5), (1.0, 3.55), (2.3, 3.3), (2.3, 2.3), (1.0, 1.9), (-0.6, 2.4)])
BODY = piv("body", f"{C}-body", *F(1.0, 2.0), (
    f'<g id="abdomen" class="{C}-abdomen">' + part(m(BARREL), skip=(nb - 1,), seam=(nb,), seam_op=0.18, belly=K.smooth(m(BELLY))[0],
                                                   layers=K.spine_stripes(BACK_SPINE, 0, BACK_SPINE.length, 6) + dots(body_poly, 80, 1.2, 2.2, 0.08, seed=19)) + "</g>"
    + f'<g id="pelvis" class="{C}-pelvis">' + part(m(inset(PELVIS)), skip=(0, 1, 2, 5, 6, 7, 8, 9, 10, 11), seam=(3, 4), seam_op=0.14) + "</g>"
    + f'<g id="chest" class="{C}-chest">' + part(m(inset(CHEST)), skip=(0, 1, 2, 3, 4, 5, 6, 7), seam=(8, 9, 10), seam_op=0.14,
                                                  belly=K.smooth(m([(2.5, 2.45), (2.0, 2.1), (1.3, 1.8), (1.25, 2.18), (2.0, 2.5), (2.45, 2.8)]))[0]) + "</g>"))

# ------------------------------------------------------------------ hidden skeletal guide
def _guide():
    bones = f"M{K._f(F(*HIP))} L{K._f(F(*KNEE))} L{K._f(F(*ANKLE))} M{K._f(F(*SHOULDER))} L{K._f(F(*ELBOW))} L{K._f(F(*WRIST))}"
    spines = "".join('<path d="M' + " L".join(K._f(sp.at(sp.length * k / 20)[:2]) for k in range(21)) + '" fill="none" stroke="#3A7BD5" stroke-width="2"></path>'
                     for sp in (TAIL_SPINE, NECK_SPINE))
    joints = "".join(f'<circle cx="{F(*p)[0]}" cy="{F(*p)[1]}" r="4" fill="#E5484D"></circle>' for p in (HIP, KNEE, ANKLE, SHOULDER, ELBOW, WRIST))
    return (f'<g id="skeleton-guide" class="{C}-guide" display="none" pointer-events="none">'
            f'<path d="{bones}" fill="none" stroke="#3A7BD5" stroke-width="3"></path>{spines}{joints}</g>')

FRAG = piv("act", f"{C}-act", *F(0.6, 0), hind_leg("far") + arm("far") + TAIL + NECK + BODY + hind_leg("near") + arm("near") + _guide())

# ------------------------------------------------------------------ move: roar (wind-up, head up with jaws wide, arms flex, close)
ACTION = {
    "head": [(0, "rotate(0)"), (0.15, "rotate(4deg)"), (0.35, "rotate(-8deg)"), (0.8, "rotate(-8deg)"), (1, "rotate(0)")],
    "jaw": [(0, "rotate(0)"), (0.15, "rotate(0)"), (0.33, "rotate(18deg)"), (0.45, "rotate(15deg)"), (0.55, "rotate(18deg)"), (0.65, "rotate(15deg)"), (0.82, "rotate(0)"), (1, "rotate(0)")],
    "neck": [(0, "rotate(0)"), (0.15, "rotate(2deg)"), (0.35, "rotate(-4deg)"), (0.8, "rotate(-4deg)"), (1, "rotate(0)")],
    "arm": [(0, "rotate(0)"), (0.35, "rotate(14deg)"), (0.8, "rotate(14deg)"), (1, "rotate(0)")],
    "arm-far": [(0, "rotate(0)"), (0.37, "rotate(14deg)"), (0.8, "rotate(14deg)"), (1, "rotate(0)")],
}
GSAP = """      .to(parts.head, { rotation: 4, duration: 0.25, ease: 'power2.out' }, 0)
      .to(parts.neck, { rotation: 2, duration: 0.25, ease: 'power2.out' }, 0)
      .to(parts.head, { rotation: -8, duration: 0.35, ease: 'back.out(2)' }, 0.25)
      .to(parts.neck, { rotation: -4, duration: 0.35, ease: 'power2.out' }, 0.25)
      .to(parts.jaw, { rotation: 18, duration: 0.3, ease: 'power3.out' }, 0.25)
      .to([parts.arm_near, parts.arm_far], { rotation: 14, duration: 0.3, ease: 'power2.out', stagger: 0.05 }, 0.25)
      .to(parts.jaw, { rotation: 15, duration: 0.08, yoyo: true, repeat: 5, ease: 'none' }, 0.55)
      .to([parts.head, parts.neck, parts.jaw, parts.arm_near, parts.arm_far], { rotation: 0, duration: 0.5, ease: 'power2.inOut' }, 1.15)"""

IDS = ["act", "body", "chest", "abdomen", "pelvis", "tail", "tail-2", "tail-3", "neck", "head", "skull", "upper-jaw", "jaw",
       "teeth-upper", "teeth-lower", "eye-near", "eye-far", "leg-near", "leg-far", "arm-near", "arm-far"]
_tip = (HEAD_AT[0] + math.cos(math.radians(HEAD_ANGLE)) * 1.5 * HEAD_SCALE * S, HEAD_AT[1] + math.sin(math.radians(HEAD_ANGLE)) * 1.5 * HEAD_SCALE * S)
MIDLINE = ([TAIL_SPINE.at(TAIL_SPINE.length * (1 - k / 10))[:2] for k in range(11)] + [F(1.0, 2.8)]
           + [NECK_SPINE.at(NECK_SPINE.length * k / 4)[:2] for k in range(5)] + [_tip])

SPEC = dict(
    code=C, slug="trex", board="T. rex", name="T. rex", short="T. rex", look=LOOK,
    viewbox=(1000, 560), frag=FRAG, ids=IDS, action=ACTION, dur=2.0, gsap=GSAP,
    action_label="Make the T. rex roar", action_verb="make it roar", page_bg="#C9D6DA",
    title="T. rex", title_px=200, binomial="Tyrannosaurus rex", subtitle="the tyrant lizard king",
    paragraph="A 12 m predator with a deep skull, a bite stronger than any other known land animal's, tiny two-fingered arms and a long, heavy tail for balance.",
    facts=[("12 m", "adult length"), ("68–66", "million years ago"), ("~35,000 N", "bite force")],
    footer="Fossils come from the Hell Creek and Lance formations and other latest Cretaceous rocks of western North America.",
    hint="Tap the T. rex to make it roar", skin_swatches=["#7A5C4C", "#9E6B7B", "#5E7E7A", "#8A6A3E"],
    dino_top=170, midline=MIDLINE, ground=F.g,
)

if __name__ == "__main__":
    K.write_all(SPEC)          # this rework round: svg/ and gsap/ only; poster and rig board follow later
    print("ok")

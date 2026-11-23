import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Paleontologist, the series' human host, in the big-head explainer style: oversized round head with dot eyes that
blink and emote (dinokit face kit), blush and a fringe under a bush hat, a filled field shirt, thin outlined tube limbs,
a femur in the near hand and a rock hammer in the far hand. Building SPEC has no side effects; run as a script to write outputs.
Signature move: "eureka", a hop with the bone raised up and forward."""
import sys
sys.path.insert(0, HERE)
import dinokit as K
from dinokit import SKIN, OL, path, stroke, piv
C = "pal"
LOOK = K.Look(C, skin="#F3DEC4", belly="#F3DEC4")
HAT, BAND, HAIR, SHIRT, POCKET, PANTS, SCARF, BOOT = "#B8955A", "#6E4F2E", "#4A3326", "#8C9A5B", "#76834A", "#6B5A48", "#C0462F", "#5A3E2E"
BONE, WOOD, STEEL = "#EFE6D0", "#8A5A36", "#7C8490"
OW = 3.5  # outline width; 5.6 px at the 1600 px sprite export


def tube(color, w, *pts):
    """outlined limb: charcoal under, colour on top"""
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    return stroke(d, w + 2 * OW) + stroke(d, w, color)


def shaded(d, fill, w=OW):
    return path(d, fill) + path(d, LOOK.url("shade")) + stroke(d, w)


def hand(x, y):
    return f'<circle cx="{x}" cy="{y}" r="7.5" fill="{SKIN}" stroke="{OL}" stroke-width="{OW}"></circle>'


def boot(x, y=514):
    return shaded(f"M{x-11} {y-14} C{x-11} {y-20} {x+5} {y-20} {x+7} {y-14} C{x+19} {y-12} {x+27} {y-8} {x+27} {y-2} "
                  f"C{x+27} {y+1} {x+23} {y} {x+18} {y} L{x-9} {y} C{x-13} {y} {x-13} {y-4} {x-11} {y-14} Z", BOOT, 3)


def femur(x, cy, ln):
    t, b = cy - ln / 2, cy + ln / 2
    return (f"M{x-5} {t+8} C{x-14} {t+2} {x-8} {t-8} {x} {t-2} C{x+8} {t-8} {x+14} {t+2} {x+5} {t+8} "
            f"L{x+5} {b-8} C{x+14} {b-2} {x+8} {b+8} {x} {b+2} C{x-8} {b+8} {x-14} {b-2} {x-5} {b-8} Z")


# ---------------- geometry (1000 x 560, ground at 514, facing right); hip 504 394, shoulders y 292, neck 504 276
LEG_FAR = piv("leg-far", f"{C}-leg-far", 496, 392, tube(PANTS, 9, (496, 392), (490, 450), (488, 498)) + boot(488))
LEG_NEAR = piv("leg-near", f"{C}-leg-near", 512, 392, tube(PANTS, 9, (512, 392), (518, 450), (514, 498)) + boot(514))

hammer = (tube(WOOD, 5, (456, 382), (464, 426))
          + shaded("M444 424 L482 418 L494 424 L482 430 L446 434 C440 434 438 426 444 424 Z", STEEL, 2.6))
ARM_FAR = piv("arm-far", f"{C}-arm-far", 478, 292,
              tube(SKIN, 6, (478, 292), (458, 338), (456, 378)) + tube(SHIRT, 15, (478, 292), (470, 310)) + hammer + hand(456, 378))

FOREARM = piv("forearm-near", f"{C}-forearm-near", 546, 340,
              tube(SKIN, 6, (546, 340), (582, 330)) + shaded(femur(584, 330, 70), BONE, 3) + hand(582, 330))
ARM_NEAR = piv("arm-near", f"{C}-arm-near", 526, 292,
               tube(SKIN, 6, (526, 292), (546, 340)) + tube(SHIRT, 15, (526, 292), (533, 311)) + FOREARM)

TORSO_D = "M474 292 C474 280 486 276 504 276 C522 276 534 280 534 292 L540 384 C540 392 534 398 526 398 L482 398 C474 398 468 392 468 384 Z"
BODY = piv("body", f"{C}-body", 504, 396,
           shaded(TORSO_D, SHIRT)
           + shaded("M512 306 L530 306 L530 322 C530 326 512 326 512 322 Z", POCKET, 2.4)          # chest pocket
           + stroke("M504 296 L504 396", 2.2, OL, 0.35)                                            # button line
           + stroke("M470 372 L538 372", 6, BAND) + stroke("M470 372 L538 372", 1.6, OL, 0.6)    # belt
           + shaded("M484 278 C494 288 514 288 524 278 L514 298 C510 302 498 302 494 298 Z", SCARF, 3))  # neckerchief knot
TAIL = piv("tail", f"{C}-tail", 490, 282, shaded("M492 278 C476 282 462 294 454 310 C470 306 482 300 496 288 Z", SCARF, 3))

hair = "M449 210 A56 56 0 0 1 559 206 C548 200 536 205 528 198 C518 207 502 203 494 196 C484 205 466 203 449 210 Z"
MOUTH_IN = "#7A2E2E"
mouths = {"smile": stroke("M518 240 Q526 248 535 239", 3.4),
          "grin": path("M516 238 Q526 256 538 237 Z", MOUTH_IN) + stroke("M516 238 Q526 256 538 237 Z", 3),
          "open": f'<ellipse cx="527" cy="245" rx="5.5" ry="7" fill="{MOUTH_IN}" stroke="{OL}" stroke-width="3"></ellipse>',
          "frown": stroke("M518 247 Q526 239 535 248", 3.4),
          "flat": stroke("M519 243 L534 242", 3.4)}
face = (f'<g class="{C}-blush" opacity="0.45">'
        + "".join(f'<ellipse cx="{x}" cy="235" rx="7" ry="4.5" fill="{K.BLUSH}"></ellipse>' for x in (502, 550)) + "</g>"
        + K.face_eye(C, 512, 220, 5.5, SKIN) + K.face_eye(C, 538, 220, 5.5, SKIN, mirror=True)
        + "".join(f'<g class="{C}-mouth-{k}">{v}</g>' for k, v in mouths.items())
        + K.drop(558, 198, 1.1, f"{C}-sweat"))
hat = (f'<g transform="rotate(-5 504 184)">'
       + shaded("M460 186 C456 160 474 144 504 142 C536 142 552 160 548 184 Z", HAT)
       + shaded("M459 174 C486 168 522 168 549 172 L548 184 C522 180 486 180 460 186 Z", BAND, 2.6)
       + shaded("M424 190 C452 176 556 174 586 186 C594 190 586 196 572 195 C536 191 470 191 436 196 C422 197 418 193 424 190 Z", HAT)
       + "</g>")
HEAD = piv("head", f"{C}-head", 504, 276,
           f'<circle cx="504" cy="218" r="56" fill="{SKIN}"></circle>'
           + path(hair, HAIR)
           + f'<circle cx="504" cy="218" r="56" fill="none" stroke="{OL}" stroke-width="{OW}"></circle>'
           + face + hat)

SHADOW = f'<ellipse cx="502" cy="514" rx="62" ry="7" fill="{OL}" opacity="0.3"></ellipse>'
FRAG = K.face_css(C) + SHADOW + piv("act", f"{C}-act", 504, 514, LEG_FAR + LEG_NEAR + ARM_FAR + TAIL + BODY + HEAD + ARM_NEAR)

# ------------------------------------------------------------------ motion: eureka hop, bone raised up and forward
ACTION = {
    "act": [(0, "translateY(0)"), (0.12, "translateY(8px)"), (0.3, "translateY(-44px)"), (0.42, "translateY(-44px)"),
            (0.55, "translateY(0)"), (0.6, "translateY(5px)"), (0.66, "translateY(0)"), (1, "translateY(0)")],
    "arm-near": [(0, "rotate(0)"), (0.12, "rotate(8deg)"), (0.32, "rotate(-87deg)"), (0.75, "rotate(-87deg)"), (1, "rotate(0)")],
    "forearm-near": [(0, "rotate(0)"), (0.32, "rotate(52deg)"), (0.75, "rotate(52deg)"), (1, "rotate(0)")],
    "head": [(0, "rotate(0)"), (0.32, "rotate(-8deg)"), (0.75, "rotate(-8deg)"), (1, "rotate(0)")],
    "leg-near": [(0, "rotate(0)"), (0.14, "rotate(0)"), (0.3, "rotate(-18deg)"), (0.5, "rotate(0)"), (1, "rotate(0)")],
    "leg-far": [(0, "rotate(0)"), (0.14, "rotate(0)"), (0.3, "rotate(14deg)"), (0.5, "rotate(0)"), (1, "rotate(0)")],
    "tail": [(0, "rotate(0)"), (0.3, "rotate(-14deg)"), (0.55, "rotate(6deg)"), (1, "rotate(0)")],
}
GSAP = """      .to(parts.act, { y: 8, duration: 0.2, ease: 'power2.out' }, 0)
      .to(parts.act, { y: -44, duration: 0.28, ease: 'power2.out' }, 0.2)
      .to(parts.arm_near, { rotation: -87, duration: 0.3, ease: 'back.out(1.6)' }, 0.2)
      .to(parts.forearm_near, { rotation: 52, duration: 0.3, ease: 'back.out(1.6)' }, 0.2)
      .to(parts.head, { rotation: -8, duration: 0.3 }, 0.2)
      .to(parts.leg_near, { rotation: -18, duration: 0.2 }, 0.22)
      .to(parts.leg_far, { rotation: 14, duration: 0.2 }, 0.22)
      .to(parts.tail, { rotation: -14, duration: 0.25 }, 0.2)
      .to(parts.act, { y: 0, duration: 0.25, ease: 'power2.in' }, 0.62)
      .to([parts.leg_near, parts.leg_far], { rotation: 0, duration: 0.2 }, 0.62)
      .to(parts.tail, { rotation: 6, duration: 0.25 }, 0.62)
      .to(parts.act, { y: 5, duration: 0.08, yoyo: true, repeat: 1 }, 0.87)
      .to([parts.arm_near, parts.forearm_near, parts.head, parts.tail], { rotation: 0, duration: 0.5, ease: 'power2.inOut' }, 1.15)"""

SPEC = dict(
    code=C, slug="paleontologist", name="Paleontologist", short="paleontologist", look=LOOK,
    viewbox=(1000, 560), frag=FRAG,
    ids=["act", "body", "tail", "head", "leg-near", "leg-far", "arm-near", "arm-far", "forearm-near"],
    action=ACTION, dur=1.6, gsap=GSAP,
    action_label="Make the paleontologist cheer with the fossil", action_verb="cheer", page_bg="#DCD3BF",
)

if __name__ == "__main__":
    K.write_all(SPEC)

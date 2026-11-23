import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # src/
ROOT = _os.path.dirname(HERE)                          # repository root
"""Skeptic co-host for two-speaker episodes, in the same big-head explainer style as char_paleontologist.py:
oversized round head with dinokit face kit, backwards baseball cap, casual hoodie, sneakers, holding a smartphone
in the near hand. Building SPEC has no side effects; run as a script to write outputs.
Signature move: "point", leaning forward pointing skeptically."""
import sys
sys.path.insert(0, HERE)
import dinokit as K
from dinokit import SKIN, OL, path, stroke, piv
C = "skp"
LOOK = K.Look(C, skin="#ECCEB0", belly="#ECCEB0")
CAP, CAP_BRIM, HAIR, HOODIE, HOOD_IN, JEANS, SNEAKER, SOLE = "#4A7BA7", "#365B7D", "#3B2820", "#C85A4A", "#9E3E31", "#3E4C63", "#E8E2D4", "#4A4340"
PHONE, SCREEN = "#2D3446", "#88C9F2"
OW = 3.5


def tube(color, w, *pts):
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)
    return stroke(d, w + 2 * OW) + stroke(d, w, color)


def shaded(d, fill, w=OW):
    return path(d, fill) + path(d, LOOK.url("shade")) + stroke(d, w)


def hand(x, y):
    return f'<circle cx="{x}" cy="{y}" r="7.5" fill="{SKIN}" stroke="{OL}" stroke-width="{OW}"></circle>'


def sneaker(x, y=514):
    return (shaded(f"M{x-11} {y-14} C{x-11} {y-20} {x+5} {y-20} {x+8} {y-14} C{x+20} {y-12} {x+29} {y-8} {x+29} {y-2} "
                   f"C{x+29} {y+1} {x+24} {y} {x+18} {y} L{x-9} {y} C{x-13} {y} {x-13} {y-4} {x-11} {y-14} Z", SNEAKER, 3)
            + stroke(f"M{x-11} {y-2} L{x+27} {y-2}", 3.5, SOLE))


# ---------------- geometry (1000 x 560, ground at 514, facing right)
LEG_FAR = piv("leg-far", f"{C}-leg-far", 496, 392, tube(JEANS, 9, (496, 392), (490, 450), (488, 498)) + sneaker(488))
LEG_NEAR = piv("leg-near", f"{C}-leg-near", 512, 392, tube(JEANS, 9, (512, 392), (518, 450), (514, 498)) + sneaker(514))

ARM_FAR = piv("arm-far", f"{C}-arm-far", 478, 292,
              tube(HOODIE, 9, (478, 292), (456, 340), (458, 378)) + hand(458, 378))

phone = (f'<g transform="rotate(-12 582 326)">'
         + shaded("M572 308 L594 308 C597 308 598 310 598 313 L598 346 C598 349 597 351 594 351 L572 351 C569 351 568 349 568 346 L568 313 C568 310 569 308 572 308 Z", PHONE, 2.8)
         + path("M572 314 L594 314 L594 343 L572 343 Z", SCREEN)
         + "</g>")
FOREARM = piv("forearm-near", f"{C}-forearm-near", 546, 340,
              tube(HOODIE, 9, (546, 340), (580, 330)) + phone + hand(580, 330))
ARM_NEAR = piv("arm-near", f"{C}-arm-near", 526, 292,
               tube(HOODIE, 11, (526, 292), (546, 340)) + FOREARM)

TORSO_D = "M472 292 C472 279 485 276 504 276 C523 276 536 279 536 292 L542 384 C542 393 535 399 526 399 L482 399 C473 399 466 393 466 384 Z"
BODY = piv("body", f"{C}-body", 504, 396,
           shaded(TORSO_D, HOODIE)
           + shaded("M484 344 L526 344 L532 378 L478 378 Z", HOOD_IN, 2.4)               # kangaroo pocket
           + stroke("M498 290 L496 322 M512 290 L514 322", 2.8, SNEAKER)                 # hoodie strings
           + stroke("M472 388 L536 388", 5, HOOD_IN))                                    # ribbed hem
TAIL = piv("tail", f"{C}-tail", 488, 282,
           shaded("M492 276 C474 278 460 288 456 306 C472 308 486 300 498 286 Z", HOOD_IN, 3))  # resting hood

hair = "M450 212 A56 56 0 0 1 558 208 C544 198 524 202 510 198 C492 204 470 202 450 212 Z"
MOUTH_IN = "#7A2E2E"
mouths = {"smile": stroke("M518 241 Q527 248 536 238", 3.4),
          "grin": path("M516 238 Q526 256 538 237 Z", MOUTH_IN) + stroke("M516 238 Q526 256 538 237 Z", 3),
          "open": f'<ellipse cx="527" cy="245" rx="5.5" ry="7" fill="{MOUTH_IN}" stroke="{OL}" stroke-width="3"></ellipse>',
          "frown": stroke("M518 248 Q526 239 535 247", 3.4),
          "flat": stroke("M518 243 L535 242", 3.4)}
face = (f'<g class="{C}-blush" opacity="0.38">'
        + "".join(f'<ellipse cx="{x}" cy="235" rx="6.5" ry="4" fill="{K.BLUSH}"></ellipse>' for x in (502, 550)) + "</g>"
        + K.face_eye(C, 512, 220, 5.5, SKIN) + K.face_eye(C, 538, 220, 5.5, SKIN, mirror=True)
        + "".join(f'<g class="{C}-mouth-{k}">{v}</g>' for k, v in mouths.items())
        + K.drop(558, 198, 1.1, f"{C}-sweat"))
# Backwards baseball cap: dome over top + flat brim pointing LEFT (-x)
cap = (f'<g transform="rotate(4 504 182)">'
       + shaded("M452 190 C454 156 476 140 508 140 C538 140 556 158 556 188 Z", CAP)
       + stroke("M506 141 C502 158 502 174 504 188", 2.2, OL, 0.4)
       + shaded("M456 184 L414 188 C408 189 408 197 416 198 L466 194 Z", CAP_BRIM, 3)
       + f'<circle cx="508" cy="140" r="4.5" fill="{CAP_BRIM}" stroke="{OL}" stroke-width="2.4"></circle>'
       + "</g>")
HEAD = piv("head", f"{C}-head", 504, 276,
           f'<circle cx="504" cy="218" r="56" fill="{SKIN}"></circle>'
           + path(hair, HAIR)
           + f'<circle cx="504" cy="218" r="56" fill="none" stroke="{OL}" stroke-width="{OW}"></circle>'
           + face + cap)

SHADOW = f'<ellipse cx="502" cy="514" rx="62" ry="7" fill="{OL}" opacity="0.3"></ellipse>'
FRAG = K.face_css(C) + SHADOW + piv("act", f"{C}-act", 504, 514, LEG_FAR + LEG_NEAR + ARM_FAR + TAIL + BODY + HEAD + ARM_NEAR)

# ------------------------------------------------------------------ motion: dramatic skeptical lean + arm thrust
ACTION = {
    "act": [(0, "translateY(0)"), (0.25, "translate(12px,-12px) rotate(4deg)"), (0.7, "translate(12px,-12px) rotate(4deg)"), (1, "translateY(0)")],
    "arm-near": [(0, "rotate(0)"), (0.25, "rotate(-62deg)"), (0.7, "rotate(-62deg)"), (1, "rotate(0)")],
    "forearm-near": [(0, "rotate(0)"), (0.25, "rotate(26deg)"), (0.7, "rotate(26deg)"), (1, "rotate(0)")],
    "head": [(0, "rotate(0)"), (0.25, "rotate(-6deg)"), (0.7, "rotate(-6deg)"), (1, "rotate(0)")],
}
GSAP = """      .to(parts.act, { x: 12, y: -12, rotation: 4, duration: 0.25, ease: 'back.out(1.6)' }, 0)
      .to(parts.arm_near, { rotation: -62, duration: 0.25, ease: 'back.out(1.6)' }, 0)
      .to(parts.forearm_near, { rotation: 26, duration: 0.25 }, 0)
      .to(parts.head, { rotation: -6, duration: 0.25 }, 0)
      .to([parts.act, parts.arm_near, parts.forearm_near, parts.head], { x: 0, y: 0, rotation: 0, duration: 0.45, ease: 'power2.inOut' }, 0.9)"""

SPEC = dict(
    code=C, slug="skeptic", name="Skeptic", short="skeptic", look=LOOK,
    viewbox=(1000, 560), frag=FRAG,
    ids=["act", "body", "tail", "head", "leg-near", "leg-far", "arm-near", "arm-far", "forearm-near"],
    action=ACTION, dur=1.4, gsap=GSAP,
    action_label="Make the skeptic argue", action_verb="argue", page_bg="#D4DDE6",
)

if __name__ == "__main__":
    K.write_all(SPEC)

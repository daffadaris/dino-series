"""Fossil props for the episodes, in the big-head explainer look (flat fills, one shade gradient, charcoal outer lines).
Original drawings from general anatomy only. Each prop is its own SVG with a transparent background; running this
writes svg/props/<name>.svg and public/sprites/props/<name>.png at 2x.

- horn-healed: Triceratops brow-horn core with two T. rex tooth pits whose rims healed (Happ 2008).
- trike-skull: Triceratops skull, side view facing left: tooth scores on the frill and on the occipital condyle
  (Fowler et al. 2012). It sits on neck-bones and pops off in Ep01.
- neck-bones: a fused front neck block and four vertebrae; the block's socket takes the skull's condyle.
Run: python3 src/props.py"""
import pathlib
import random
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from dinokit import OL
from sprites import browser, shoot

ROOT = HERE.parent
FOSSIL, FOSSIL_DK, HEALED, PIT, FRILL = "#E2CFA6", "#B79A6E", "#F6EBD0", "#5B4434", "#E9D9B6"
OW = 5


def defs(*ids):
    """vertical shade gradient per fill: light on top, the fill's dark tone at the bottom"""
    return "<defs>" + "".join(
        f'<linearGradient id="{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0.35" stop-color="{FOSSIL_DK}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{FOSSIL_DK}" stop-opacity="0.75"/></linearGradient>' for i in ids) + "</defs>"


def shape(d, fill, grad="shade", w=OW):
    return f'<path d="{d}" fill="{fill}"/><path d="{d}" fill="url(#{grad})"/><path d="{d}" fill="none" stroke="{OL}" stroke-width="{w}" stroke-linejoin="round"/>'


def line(d, color=FOSSIL_DK, w=3.2):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'


def pit(x, y, r, healed):
    """tooth puncture; a healed one has an uneven, raised rim of new bone (seeded, so rebuilds match)"""
    out = ""
    if healed:
        rnd = random.Random(f"pit-{x}-{y}")
        pts = [(x + c * r * (1.7 + rnd.uniform(-0.18, 0.18)), y + s_ * r * (1.45 + rnd.uniform(-0.18, 0.18))) for c, s_ in _ring(18)]
        out += f'<path d="{_smooth(pts)}" fill="{HEALED}" stroke="{FOSSIL_DK}" stroke-width="3" stroke-linejoin="round"/>'
    return out + f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.8:.1f}" fill="{PIT}"/>'


def _smooth(pts):
    """closed curve through the midpoints, using each point as a quadratic control"""
    mids = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(pts, pts[1:] + pts[:1])]
    return f"M{mids[-1][0]:.1f} {mids[-1][1]:.1f} " + " ".join(f"Q{p[0]:.1f} {p[1]:.1f} {m[0]:.1f} {m[1]:.1f}" for p, m in zip(pts, mids)) + " Z"


def _ring(n):
    import math
    return [(math.cos(2 * math.pi * k / n), math.sin(2 * math.pi * k / n)) for k in range(n)]


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d for a, b, c, d in zip(p0, p1, p2, p3))


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{defs("shade")}{body}</svg>'


# ---------------------------------------------------------------- horn-healed (800 x 360; base left, tip right)
HORN_D = ("M122 172 C300 156 540 128 704 70 C600 140 380 250 142 306 "
          "L130 288 L112 266 L126 246 L108 220 L124 198 Z")
HORN = svg(800, 360,
           shape(HORN_D, FOSSIL)
           + line("M150 210 C320 185 500 145 650 104") + line("M160 250 C330 220 480 175 610 125")   # vascular grooves
           + line("M118 200 C120 230 124 260 132 290", OL, 3)                                         # broken base
           + pit(398, 180, 15, True) + pit(470, 160, 13, True)
           + line("M545 140 L565 128", PIT, 4) + line("M552 152 L574 139", PIT, 4))                   # small unhealed scrapes

# ---------------------------------------------------------------- trike-skull (1000 x 620; beak left, condyle at 626 420)
FRILL_EDGE = [((610, 52), (690, 22), (790, 40), (860, 100)), ((860, 100), (910, 145), (920, 220), (880, 280)),
              ((880, 280), (850, 320), (800, 335), (740, 340))]
SKULL_D = ("M78 392 C100 350 150 318 210 304 L250 296 C300 286 340 276 372 262 L430 236 C460 170 520 90 610 52 "
           + " ".join(f"C{b[0]} {b[1]} {c[0]} {c[1]} {d[0]} {d[1]}" for _, b, c, d in FRILL_EDGE)
           + " C690 345 650 360 630 392 L600 430 L572 470 C440 488 240 462 130 424 C100 414 84 404 78 392 Z")


def epoccipitals():
    out = ""
    for seg in FRILL_EDGE:
        for t in (0.15, 0.4, 0.65, 0.9):
            x, y = bez(*seg, t)
            x2, y2 = bez(*seg, min(1, t + 0.02))
            nx, ny = y2 - y, -(x2 - x)                       # outward normal (edge runs clockwise)
            n = (nx * nx + ny * ny) ** 0.5 or 1
            nx, ny = nx / n, ny / n
            tx, ty = -ny, nx
            out += (f'<path d="M{x - tx * 14:.1f} {y - ty * 14:.1f} L{x + nx * 20:.1f} {y + ny * 20:.1f} L{x + tx * 14:.1f} {y + ty * 14:.1f} Z" '
                    f'fill="{FRILL}" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>')
    return out


def brow_horn(dx, dy, fill):
    return shape(f"M{382 + dx} {262 + dy} C{340 + dx} {200 + dy} {285 + dx} {120 + dy} {228 + dx} {66 + dy} "
                 f"C{310 + dx} {104 + dy} {390 + dx} {170 + dy} {442 + dx} {234 + dy} Z", fill)


SKULL = svg(1000, 620,
            brow_horn(36, 8, FOSSIL_DK)                                    # far horn
            + epoccipitals()
            + shape("M606 418 C606 398 630 392 644 406 C658 420 650 446 626 448 C610 448 604 434 606 418 Z", HEALED)  # occipital condyle
            + line("M624 412 L638 438", PIT, 3.4) + line("M634 406 L648 428", PIT, 3.4)                              # tooth scores, condyle
            + shape(SKULL_D, FOSSIL)
            + "".join(line(f"M{x} {y} L{x + 34} {y + 30}", PIT, 4) for x, y in ((690, 190), (722, 182), (754, 176), (786, 172)))  # frill scores
            + shape("M226 300 C220 268 226 246 236 230 C250 252 262 272 270 292 Z", FOSSIL)                          # nasal horn
            + brow_horn(0, 0, FOSSIL)
            + f'<ellipse cx="410" cy="300" rx="27" ry="21" fill="{PIT}"/><ellipse cx="180" cy="342" rx="22" ry="14" fill="{PIT}"/>'
            + line("M108 404 C250 428 420 444 566 450", OL, 4)              # mouth line
            + line("M452 450 C462 416 492 402 516 410", FOSSIL_DK)          # coronoid process
            + line("M480 322 C540 312 600 322 640 352") + line("M720 290 C770 262 820 242 850 222"))  # cracks

# ---------------------------------------------------------------- neck-bones (760 x 300; socket at 64 205, ground 280)
def vertebra(x, w, h, spine):
    """spool-shaped centrum with a neural spine leaning back"""
    top, bot = 272 - h, 272
    body = (f"M{x} {top} C{x + w * 0.3} {top + 9} {x + w * 0.7} {top + 9} {x + w} {top} "
            f"C{x + w + 9} {top + h * 0.35} {x + w + 9} {bot - h * 0.35} {x + w} {bot} "
            f"C{x + w * 0.7} {bot - 9} {x + w * 0.3} {bot - 9} {x} {bot} C{x - 9} {bot - h * 0.35} {x - 9} {top + h * 0.35} {x} {top} Z")
    sp = (f"M{x + w * 0.22} {top + 8} C{x + w * 0.3} {top - spine * 0.5} {x + w * 0.5} {top - spine} {x + w * 0.78} {top - spine - 4} "
          f"C{x + w * 0.74} {top - spine * 0.5} {x + w * 0.7} {top - 4} {x + w * 0.72} {top + 8} Z")
    return shape(sp, FOSSIL) + shape(body, FOSSIL)


NECK = svg(760, 300,
           "".join(vertebra(x, 104, h, s) for x, h, s in ((604, 78, 80), (490, 84, 88), (376, 90, 96), (262, 96, 104)))
           + shape("M140 150 C150 104 182 72 226 62 C216 98 214 124 220 150 Z", FOSSIL)              # spine of the fused block
           + shape("M64 150 C110 140 200 138 254 146 C264 186 264 236 254 270 C200 280 110 278 64 262 "
                   "C84 236 90 220 90 206 C90 192 84 172 64 150 Z", FOSSIL)                         # fused front neck block
           + f'<path d="M64 156 C46 176 44 236 64 256 C80 236 84 176 64 156 Z" fill="{PIT}"/>')   # socket for the condyle

PROPS = {"horn-healed": (HORN, 800, 360), "trike-skull": (SKULL, 1000, 620), "neck-bones": (NECK, 760, 300)}


def main():
    exe = browser()
    (ROOT / "svg" / "props").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        for name, (src, w, h) in PROPS.items():
            (ROOT / "svg" / "props" / f"{name}.svg").write_text(src, encoding="utf-8")
            big = src.replace(f'width="{w}" height="{h}"', f'width="{w * 2}" height="{h * 2}"', 1)
            shoot(exe, big, ROOT / "public" / "sprites" / "props" / f"{name}.png", w * 2, h * 2, pathlib.Path(t))


if __name__ == "__main__":
    main()

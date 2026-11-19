import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # repo root: all paths are relative to it
"""Realistic-proportion T. rex, built from layered shapes; same group ids and pivots as before."""
import pathlib, random, re
from matplotlib.path import Path as MPath

SKIN = "SKIN"
D, L = "#000000", "#FFFFFF"
TOOTH, CLAW, EYE = "#EFE6D0", "#3A2A2C", "#E0B04A"
OL, BELLY = "#2A1C22", "#DCC8A4"
random.seed(7)

def piv(gid, cls, x, y, inner, scale=None):
    ident = f' id="{gid}"' if gid else ""
    sc = f" scale({scale})" if scale else ""
    return f'<g transform="translate({x} {y}){sc}"><g{ident} class="{cls}"><g transform="translate({-x} {-y})">{inner}</g></g></g>'

def dark(shapes, op):
    return f'<g fill="{D}" stroke="none" opacity="{op}">{shapes}</g>'

def stripe(x, y, ln, w=14):
    return f'<path d="M{x} {y} L{x+w} {y+1} L{x+w*0.45:.0f} {y+ln} L{x+w*0.1:.0f} {y+ln*0.9:.0f} Z"></path>'

# rough polygons for scattering texture inside the silhouette
TORSO_POLY = [(470,166),(560,152),(650,168),(700,184),(740,182),(790,160),(806,204),(788,272),(760,356),(690,394),(600,400),(520,402),(470,350)]
TAIL_POLY = [(60,212),(220,186),(380,164),(470,162),(470,320),(420,306),(320,258),(200,232),(60,219)]
def scatter(poly, n, rmin, rmax):
    path = MPath(poly); xs = [p[0] for p in poly]; ys = [p[1] for p in poly]; out = []
    while len(out) < n:
        x, y = random.uniform(min(xs), max(xs)), random.uniform(min(ys), max(ys))
        if path.contains_point((x, y)): out.append((round(x,1), round(y,1), round(random.uniform(rmin, rmax),1)))
    return out

# ------------------------------------------------------------------ far leg
far_leg = '''
<path d="M452 336 C488 338 500 364 488 388 C472 410 448 422 434 432 C424 440 410 434 412 424 C418 404 428 380 438 356 C442 344 446 338 452 336 Z"></path>
<path d="M410 420 C420 410 436 414 438 426 L448 484 C448 494 432 498 428 488 L408 434 Z"></path>
<path d="M424 484 C440 478 466 480 486 486 C504 490 516 498 516 506 C516 512 508 514 500 512 L432 514 C418 514 414 492 424 484 Z"></path>
<path d="M410 220 C446 196 512 216 518 276 C522 330 498 358 470 356 C438 352 418 318 410 284 Z"></path>'''
FAR_LEG = f'''<g id="leg-far" fill="{SKIN}">{far_leg}
{dark(far_leg, "0.3")}
<path d="M514 500 C522 500 528 505 528 511 C523 508 518 507 512 508 Z" fill="{CLAW}"></path>
</g>'''

# ------------------------------------------------------------------ far arm
far_arm = '<polyline points="748,296 770,328 788,334" fill="none" stroke="CLR" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"></polyline>'
FAR_ARM = piv("arm-far", "tr-arm-far", 748, 296, f'''{far_arm.replace("CLR", SKIN)}
{far_arm.replace("CLR", D).replace("<polyline", '<polyline opacity="0.38"')}
<path d="M788 331 C795 333 798 340 795 345 C793 340 790 338 786 338 Z M784 335 C790 339 791 346 787 350 C786 345 784 342 780 341 Z" fill="{CLAW}"></path>''')

# ------------------------------------------------------------------ tail
tail_spots = "".join(f'<ellipse cx="{x}" cy="{y}" rx="{r*2.2:.1f}" ry="{r:.1f}" transform="rotate({random.randint(-20,10)} {x} {y})"></ellipse>' for x,y,r in scatter([(80,212),(220,188),(380,166),(470,164),(470,206),(380,200),(220,210),(80,214)], 16, 2.5, 5))
tail_scales = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"></circle>' for x,y,r in scatter(TAIL_POLY, 120, 0.8, 1.6))
TAIL = piv("tail", "tr-tail", 470, 230, f'''
<path d="M480 156 C380 158 230 180 30 208 C22 210 22 220 30 221 C190 228 330 262 420 312 C446 326 466 334 480 338 Z" fill="{SKIN}"></path>
<path d="M480 156 C380 158 230 180 30 208 C26 210 26 212 30 212 C230 192 380 182 480 186 Z" fill="{D}" opacity="0.3"></path>
<path d="M30 221 C190 228 330 262 420 312 C446 326 466 334 480 338 L480 314 C440 292 400 268 368 254 C270 224 150 214 44 216 Z" fill="{BELLY}"></path>
<g fill="{D}" opacity="0.32">{stripe(70,203,13,7)}{stripe(120,196,20,9)}{stripe(180,188,30,11)}{stripe(240,179,40,13)}{stripe(300,171,48,15)}{stripe(360,165,55,16)}{stripe(420,161,60,17)}</g>
<g fill="{D}" opacity="0.14">{tail_spots}</g>
<g fill="{D}" opacity="0.1">{tail_scales}</g>
<path d="M120 204 C200 194 300 184 400 180" stroke="{L}" stroke-width="2" fill="none" opacity="0.07"></path>''')

# ------------------------------------------------------------------ body
body_spots = "".join(f'<ellipse cx="{x}" cy="{y}" rx="{r*1.8:.1f}" ry="{r:.1f}" transform="rotate({random.randint(-30,30)} {x} {y})"></ellipse>' for x,y,r in scatter([(470,166),(560,154),(650,170),(700,186),(740,184),(780,166),(780,210),(700,236),(600,230),(470,226)], 30, 3, 7))
body_scales = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"></circle>' for x,y,r in scatter(TORSO_POLY, 260, 0.8, 1.7))
body_lights = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"></circle>' for x,y,r in scatter(TORSO_POLY, 90, 0.6, 1.2))
BODY = piv("body", "tr-body", 600, 350, f'''
<path d="M450 160 C520 146 612 154 690 180 C712 186 726 186 740 180 C762 168 786 156 806 150 L840 220 C826 244 800 268 782 290 C778 330 758 372 716 390 C670 408 608 406 562 398 C536 400 516 408 502 400 C482 390 464 366 444 340 Z" fill="{SKIN}"></path>
<path d="M450 160 C520 146 612 154 690 180 C712 186 726 186 740 180 C762 168 786 156 806 150 L810 168 C788 176 766 190 744 202 C722 206 706 206 690 202 C612 178 530 172 450 184 Z" fill="{D}" opacity="0.3"></path>
<path d="M450 184 C530 172 612 178 690 202 C706 206 722 206 744 202 L762 226 C738 234 712 234 690 230 C612 210 530 206 450 214 Z" fill="{D}" opacity="0.1"></path>
<path d="M840 220 C826 244 800 268 782 290 C778 330 758 372 716 390 C670 408 608 406 562 398 C536 400 516 408 502 400 C482 390 464 366 444 340 L450 318 C478 344 504 360 534 366 C584 370 642 368 690 354 C728 338 748 304 758 272 C770 246 796 226 818 204 Z" fill="{BELLY}"></path>
<path d="M560 388 C610 394 668 388 712 376 C696 396 652 404 604 404 C584 404 568 400 560 388 Z" fill="{D}" opacity="0.08"></path>
<g fill="{D}" opacity="0.32">{stripe(486,154,56,18)}{stripe(540,151,62,19)}{stripe(596,155,62,19)}{stripe(650,166,54,18)}{stripe(700,181,42,16)}{stripe(746,178,34,14)}{stripe(778,163,28,12)}</g>
<g fill="{D}" opacity="0.14">{body_spots}</g>
<g fill="{D}" opacity="0.1">{body_scales}</g>
<g fill="{L}" opacity="0.07">{body_lights}</g>
<path d="M620 230 C634 280 634 340 618 386 M652 228 C666 276 666 334 652 380 M684 234 C696 274 696 318 684 356" stroke="{D}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.05"></path>
<path d="M766 210 C778 228 784 250 780 270 M786 196 C798 212 804 232 800 250 M806 186 C816 200 820 218 818 234 M748 226 C758 242 762 262 758 282" stroke="{D}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.18"></path>
<path d="M520 158 C580 156 640 166 690 182" stroke="{L}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.08"></path>''')

# ------------------------------------------------------------------ near leg
leg_scales = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"></circle>' for x,y,r in scatter([(392,206),(470,178),(550,196),(596,256),(586,340),(540,376),(490,360),(400,266)], 100, 0.8, 1.5))
NEAR_LEG = f'''<g id="leg-near">
<path d="M524 344 C562 346 578 374 566 400 C552 424 528 438 512 450 C502 458 486 454 486 442 C488 422 496 398 504 372 C510 356 514 346 524 344 Z" fill="{SKIN}"></path>
<path d="M566 400 C552 424 528 438 512 450 C502 458 490 456 488 448 C504 438 522 422 536 404 C546 390 552 374 556 362 C566 372 570 386 566 400 Z" fill="{D}" opacity="0.16"></path>
<path d="M486 436 C496 426 514 430 516 442 L536 488 C538 498 522 502 516 494 L484 450 Z" fill="{SKIN}"></path>
<path d="M486 436 C496 426 514 430 516 442 L536 488 C538 498 522 502 516 494 L484 450 Z" fill="{D}" opacity="0.08"></path>
<path d="M502 472 C494 476 490 482 492 486 C496 482 500 480 504 480 Z" fill="{CLAW}"></path>
<path d="M506 486 C520 480 548 482 570 488 C590 492 604 498 606 506 C606 512 598 514 590 512 L520 514 C504 514 498 494 506 486 Z" fill="{SKIN}"></path>
<path d="M506 486 C520 480 548 482 570 488 C590 492 604 498 606 506 C590 502 560 498 530 500 C518 500 508 496 506 486 Z" fill="{L}" opacity="0.08"></path>
<path d="M548 488 C552 496 554 504 552 512 M574 492 C578 498 580 506 578 512" stroke="{D}" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.3"></path>
<path d="M604 500 C614 500 620 506 619 513 C614 509 609 508 603 509 Z M588 506 C596 507 600 512 598 516 C594 513 590 512 585 512 Z" fill="{CLAW}"></path>
<path d="M380 200 C420 164 530 168 580 222 C618 262 616 330 584 362 C556 390 512 390 488 370 C454 342 404 304 386 268 C374 246 372 220 380 200 Z" fill="{SKIN}"></path>
<path d="M488 370 C512 390 556 390 584 362 C616 330 618 262 580 222 C600 270 596 324 570 348 C544 372 512 374 488 370 Z" fill="{D}" opacity="0.2"></path>
<path d="M394 198 C434 170 518 172 566 214" stroke="{L}" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.12"></path>
<path d="M430 226 C470 214 516 220 552 244 M420 262 C462 252 514 260 556 286 M468 312 C498 306 532 314 560 330" stroke="{D}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.13"></path>
<g fill="{D}" opacity="0.1">{leg_scales}</g>
</g>'''

# ------------------------------------------------------------------ head
def teeth_down(pts):
    return "".join(f'<path d="M{x-3} {y} C{x-2} {y+h*0.6:.1f} {x} {y+h} {x+0.6} {y+h} C{x+2} {y+h*0.5:.1f} {x+3} {y+1} {x+4} {y} Z"></path>' for x,y,h in pts)
def teeth_up(pts):
    return "".join(f'<path d="M{x-3} {y} C{x-2} {y-h*0.6:.1f} {x} {y-h} {x+0.6} {y-h} C{x+2} {y-h*0.5:.1f} {x+3} {y-1} {x+4} {y} Z"></path>' for x,y,h in pts)

upper = [(852,203,5),(872,201,6),(892,199,7),(912,196,6),(932,193,6),(950,191,5),(964,189,4)]
lower = [(860,194,6),(884,193,7),(908,192,7),(932,191,6),(952,190,5)]
jaw_scales = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"></circle>' for x,y,r in scatter([(812,202),(962,194),(944,210),(880,226),(830,226)], 34, 0.7, 1.3))
head_scales = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"></circle>' for x,y,r in scatter([(812,146),(870,124),(930,130),(970,156),(970,182),(900,196),(830,202),(804,180)], 80, 0.7, 1.4))

JAW = piv("jaw", "tr-jaw", 816, 198, f'''
<path d="M816 198 C860 180 914 158 956 146 C968 158 976 174 974 190 Z" fill="#4A1C1E"></path>
<path d="M840 194 C880 186 930 182 958 184 L954 190 C920 190 880 194 842 198 Z" fill="#8E3A3E"></path>
<g fill="{TOOTH}">{teeth_up(lower)}</g>
<path d="M804 196 L972 188 C980 190 980 198 974 202 C952 216 902 228 852 234 C828 236 808 230 800 218 C794 208 796 200 804 196 Z" fill="{SKIN}"></path>
<path d="M800 218 C808 230 828 236 852 234 C902 228 952 216 974 202 L970 196 C948 206 902 216 852 220 C830 221 812 216 802 206 Z" fill="{BELLY}"></path>
<path d="M806 198 C830 204 842 216 844 230" stroke="{D}" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.2"></path>
<path d="M814 198 C870 196 930 192 972 190" stroke="{D}" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.35"></path>
<g fill="{D}" opacity="0.14">{jaw_scales}</g>''')

EYELID = f'<ellipse cx="878" cy="140" rx="6.5" ry="6" fill="{SKIN}"></ellipse>'

HEAD_INNER = f'''
{JAW}
<path d="M804 142 C820 126 846 118 870 118 C880 118 888 121 894 126 C902 122 912 122 922 125 C944 130 962 140 974 152 C982 160 984 172 980 182 L974 188 C940 194 880 202 836 206 C816 208 802 200 796 186 C790 170 792 154 804 142 Z" fill="{SKIN}"></path>
<g fill="{TOOTH}">{teeth_down(upper)}</g>
<path d="M836 206 C860 204 880 201 900 199 C920 196 940 193 974 188" stroke="{D}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.4"></path>
<path d="M804 142 C820 126 846 118 870 118 C880 118 888 121 894 126 C902 122 912 122 922 125 C944 130 962 140 974 152 L970 157 C958 147 940 140 920 136 C908 134 898 136 890 140 C876 132 852 132 832 140 C818 148 808 158 800 170 Z" fill="{D}" opacity="0.26"></path>
<path d="M904 128 C932 132 956 142 972 154" stroke="{L}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.14"></path>
<path d="M900 164 C912 152 932 152 944 162 C932 170 914 172 900 164 Z" fill="{D}" opacity="0.12"></path>
<path d="M796 186 C802 200 816 208 836 206 C824 194 818 176 818 150 C806 158 798 172 796 186 Z" fill="{D}" opacity="0.14"></path>
<path d="M818 152 C822 172 830 190 842 202" stroke="{D}" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.18"></path>
<path d="M944 182 C956 180 968 180 976 182" stroke="{D}" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.16"></path>
<g fill="{D}" opacity="0.22"><circle cx="908" cy="128" r="1.8"></circle><circle cx="920" cy="130" r="1.8"></circle><circle cx="932" cy="133" r="1.7"></circle><circle cx="944" cy="137" r="1.6"></circle><circle cx="955" cy="142" r="1.5"></circle><circle cx="964" cy="148" r="1.4"></circle></g>
<g fill="{D}" opacity="0.14">{head_scales}</g>
<g fill="{D}" opacity="0.2"><circle cx="860" cy="200" r="1.2"></circle><circle cx="880" cy="198" r="1.2"></circle><circle cx="900" cy="196" r="1.2"></circle><circle cx="920" cy="193" r="1.2"></circle><circle cx="940" cy="191" r="1.2"></circle><circle cx="958" cy="189" r="1.2"></circle></g>
<path d="M965 160 C969 158 974 159 976 162" stroke="{D}" stroke-width="2.2" fill="none" stroke-linecap="round" opacity="0.6"></path>
<path d="M884 130 C888 121 897 120 901 127 L897 136 Z" fill="{SKIN}"></path>
<path d="M884 130 C888 121 897 120 901 127 L897 136 Z" fill="{D}" opacity="0.28"></path>
<ellipse cx="878" cy="140" rx="7.5" ry="6.8" fill="{D}" opacity="0.38"></ellipse>
<ellipse cx="878" cy="140" rx="4.4" ry="4.1" fill="{EYE}"></ellipse>
<circle cx="878.4" cy="140" r="2.2" fill="#15110D"></circle>
<circle cx="879.6" cy="138.6" r="0.9" fill="{L}"></circle>
{piv("", "tr-eyelid", 878, 140, EYELID)}
<path d="M864 136 C870 128 886 126 896 132 C898 134 896 136 894 136 C884 132 872 132 866 140 C864 140 862 138 864 136 Z" fill="{D}" opacity="0.45"></path>'''
HEAD = piv("head", "tr-head", 800, 180, HEAD_INNER, scale=1.4)

# ------------------------------------------------------------------ near arm
near_arm = f'''<polyline points="760,300 782,334 800,338" fill="none" stroke="{SKIN}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"></polyline>
<polyline points="763,304 778,328" fill="none" stroke="{L}" stroke-width="3" stroke-linecap="round" opacity="0.15"></polyline>
<path d="M801 334 C809 336 813 343 810 349 C807 343 803 341 798 341 Z M797 339 C803 343 805 351 800 355 C799 349 796 346 792 345 Z" fill="{CLAW}"></path>'''
NEAR_ARM = piv("arm-near", "tr-arm", 760, 300, near_arm)

def add_outline(part, d, close=True, where="last"):
    o = f'<path d="{d if close else d.rstrip(" Z")}" fill="none" stroke="{OL}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"></path>'
    if where == "piv":  # inside the innermost wrapper of a pivot group
        i = part.rfind("</g></g></g>")
    elif where == "first-piv":
        i = part.find("</g></g></g>")
    else:
        i = part.rfind("</g>")
    return part[:i] + o + part[i:]

def silhouette(part, startswith):
    m = re.search(r'<path d="(' + re.escape(startswith) + r'[^"]*)" fill="SKIN"', part)
    return m.group(1)

TAIL = add_outline(TAIL, silhouette(TAIL, "M480 156"), close=False, where="piv")
BODY = add_outline(BODY, silhouette(BODY, "M450 160"), close=False, where="piv")
def stroke(d, w=3):
    return f'<path d="{d}" fill="none" stroke="{OL}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"></path>'
LOWER_LEG_OUTLINES = (stroke("M524 344 C562 346 578 374 566 400 C552 424 528 438 512 450") +
                      stroke("M486 442 C488 422 496 398 504 372 C510 356 514 346 524 344") +
                      stroke("M516 442 L536 488 C538 498 522 502 516 494 L484 450") +
                      stroke(silhouette(NEAR_LEG, "M506 486")))
thigh_at = NEAR_LEG.index('<path d="M380 200')
NEAR_LEG = NEAR_LEG[:thigh_at] + LOWER_LEG_OUTLINES + NEAR_LEG[thigh_at:]
i = NEAR_LEG.rfind("</g>")
NEAR_LEG = NEAR_LEG[:i] + stroke("M580 222 C618 262 616 330 584 362 C556 390 512 390 488 370 C454 342 404 304 386 268") + NEAR_LEG[i:]
FAR_LEG = FAR_LEG.replace('<g id="leg-far" fill="SKIN">', '<g id="leg-far" fill="SKIN" stroke="#2A1C22" stroke-width="3" stroke-linejoin="round">')
# head is drawn at 1.4x, so its strokes are thinner to read at the same weight as the body
j = HEAD.find("</g></g></g>")
HEAD = HEAD[:j] + stroke("M972 188 C980 190 980 198 974 202 C952 216 902 228 852 234 C828 236 808 230 800 218", 2.2) + HEAD[j:]
k = HEAD.rfind("</g></g></g>")
HEAD = HEAD[:k] + stroke("M826 124 C840 119 856 118 870 118 C880 118 888 121 894 126 C902 122 912 122 922 125 C944 130 962 140 974 152 C982 160 984 172 980 182 L974 188 C940 194 880 202 836 206", 2.2) + HEAD[k:]
def arm_outline(part, pts, w):
    i = part.find("<polyline")
    o = f'<polyline points="{pts}" fill="none" stroke="{OL}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"></polyline>'
    return part[:i] + o + part[i:]
FAR_ARM = arm_outline(FAR_ARM, "748,296 770,328 788,334", 15)
NEAR_ARM = arm_outline(NEAR_ARM, "760,300 782,334 800,338", 17)

FRAG = f'''<g transform="translate(450 514) scale(0.93) translate(-480 -514)">
<ellipse cx="490" cy="514" rx="310" ry="12" fill="{D}" opacity="0.3"></ellipse>
{FAR_LEG}
{FAR_ARM}
{TAIL}
{BODY}
{NEAR_LEG}
{HEAD}
{NEAR_ARM}
</g>'''

DEFAULT_SKIN = "#9E6B7B"
SWATCHES = ["#9E6B7B", "#6B6250", "#4E6E63", "#7A5A48"]
JAW_OPEN, HEAD_REAR = 16, -8

CSS = f"""
.tr-tail,.tr-body,.tr-head,.tr-jaw,.tr-arm,.tr-arm-far{{transform-origin:0 0}}
.tr-eyelid{{transform-origin:0 0;transform:scaleY(0)}}
.tr-anim .tr-tail{{animation:tr-tail 5s ease-in-out infinite}}
.tr-anim .tr-body{{animation:tr-breath 3.2s ease-in-out infinite}}
.tr-anim .tr-head{{animation:tr-head 7s ease-in-out infinite}}
.tr-anim .tr-jaw{{animation:tr-roar 7s ease-in-out infinite}}
.tr-anim .tr-eyelid{{animation:tr-blink 5s linear infinite}}
@keyframes tr-tail{{0%,100%{{transform:rotate(0)}}50%{{transform:rotate(-1.5deg)}}}}
@keyframes tr-breath{{0%,100%{{transform:scale(1,1)}}50%{{transform:scale(1.006,1.016)}}}}
@keyframes tr-head{{0%,55%,92%,100%{{transform:rotate(0)}}64%,82%{{transform:rotate({HEAD_REAR}deg)}}}}
@keyframes tr-roar{{0%,57%,92%,100%{{transform:rotate(0)}}66%,82%{{transform:rotate({JAW_OPEN}deg)}}}}
@keyframes tr-blink{{0%,93%,100%{{transform:scaleY(0)}}95.5%{{transform:scaleY(1)}}}}
@media (prefers-reduced-motion: reduce){{.tr-anim *{{animation:none !important}}}}
""".strip()

std = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 560" width="1000" height="560" class="tr-anim" role="img" aria-label="Animated Tyrannosaurus rex">
<title>T. rex (animatable)</title>
<!-- Groups you can animate: #tail #body #leg-far #leg-near #arm-far #arm-near #head #jaw .tr-eyelid
     Each moving group sits inside a wrapper whose origin is its joint, so rotate/scale with transform-origin 0 0
     (GSAP: svgOrigin "0 0"). Remove class="tr-anim" on the root to stop the built-in idle loop. -->
<style>
{CSS}
</style>
{FRAG.replace(SKIN, DEFAULT_SKIN)}
</svg>
'''
pathlib.Path(HERE + "/trex-animated.svg").write_text(std)

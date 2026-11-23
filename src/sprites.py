"""Episode sprites: transparent 1600 px PNGs of the big-head explainer drawings (svg/styles/<species>-explainer.svg, and the
host from svg/paleontologist-animated.svg), one per pose and emotion, for the 2D-in-3D pipeline.
Also exports the Hell Creek scenery cards (svg/scenery/) as transparent foliage cards for the 3D set.
Run: python3 src/sprites.py [species ...]   (writes public/sprites/<species>/<pose>.png and public/sprites/scenery/<card>.png;
needs Microsoft Edge or Chrome)"""
import os, pathlib, re, shutil, subprocess, sys, tempfile
from dinokit import EMOTIONS

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H = 1600, 896
OUT = ROOT / "public" / "sprites"
CARDS, CARD_SCALE = ["hell-creek-ferns", "hell-creek-fan-palm", "hell-creek-broadleaf-tree", "hell-creek-dawn-redwood",
                     "any-habitat-boulder", "any-habitat-pebbles", "any-habitat-cloud"], 3   # 300x400 cards -> 900x1200

# CSS pose overrides per class prefix. Moving parts pivot at their joint (transform-origin 0 0), so a rotation is about the joint.
BASE = {
    **EMOTIONS,
    "walk": "#leg-near{{transform:rotate(16deg)}}#leg-far{{transform:rotate(-16deg)}}"
            "#{fore}-near{{transform:rotate(-14deg)}}#{fore}-far{{transform:rotate(14deg)}}#act{{transform:translateY(-4px)}}",
}
# body language added to each emotion's face. Whole-body lean goes on #act (pivot at the feet) so no part detaches at a joint;
# a dinosaur's tail rotates up with positive angles. The host's arms bend at the elbow (forearm-near).
BODY = {
    "dino": {
        "happy": "#act{{transform:translateY(-16px)}}.{p}-tail{{transform:rotate(12deg)}}#{fore}-near{{transform:rotate(-22deg)}}"
                 "#{fore}-far{{transform:rotate(-14deg)}}#leg-near{{transform:rotate(-6deg)}}",
        "angry": "#act{{transform:translateX(14px) rotate(2deg)}}.{p}-tail{{transform:rotate(-8deg)}}#{fore}-near{{transform:rotate(-10deg)}}"
                 "#{fore}-far{{transform:rotate(8deg)}}#leg-near{{transform:rotate(8deg)}}#leg-far{{transform:rotate(-6deg)}}",
        "sad": "#act{{transform:translateY(6px)}}.{p}-tail{{transform:rotate(-14deg)}}#{fore}-near{{transform:rotate(10deg)}}#{fore}-far{{transform:rotate(8deg)}}",
        "surprised": "#act{{transform:translate(-18px,-16px) rotate(-2deg)}}.{p}-tail{{transform:rotate(14deg)}}#{fore}-near{{transform:rotate(-30deg)}}"
                     "#{fore}-far{{transform:rotate(-24deg)}}#leg-near{{transform:rotate(10deg)}}",
        "scared": "#act{{transform:translate(-26px,6px) rotate(-3deg)}}.{p}-tail{{transform:rotate(-16deg)}}#{fore}-near{{transform:rotate(16deg)}}"
                  "#{fore}-far{{transform:rotate(12deg)}}#leg-near{{transform:rotate(12deg)}}#leg-far{{transform:rotate(-8deg)}}",
        "smug": "#act{{transform:translateX(-6px)}}.{p}-tail{{transform:rotate(8deg)}}#{fore}-near{{transform:rotate(-8deg)}}",
    },
    "host": {
        "happy": "#act{{transform:translateY(-14px)}}.{p}-arm-near{{transform:rotate(-95deg)}}.{p}-forearm-near{{transform:rotate(70deg)}}"
                 ".{p}-arm-far{{transform:rotate(110deg)}}.{p}-leg-near{{transform:rotate(-10deg)}}.{p}-leg-far{{transform:rotate(10deg)}}.{p}-tail{{transform:rotate(-10deg)}}",
        "angry": "#act{{transform:rotate(3deg)}}.{p}-arm-near{{transform:rotate(15deg)}}.{p}-forearm-near{{transform:rotate(75deg)}}"
                 ".{p}-arm-far{{transform:rotate(-20deg)}}.{p}-leg-near{{transform:rotate(-9deg)}}.{p}-leg-far{{transform:rotate(9deg)}}",
        "sad": "#act{{transform:translateY(3px) rotate(2deg)}}.{p}-arm-near{{transform:rotate(12deg)}}.{p}-forearm-near{{transform:rotate(95deg)}}"
               ".{p}-arm-far{{transform:rotate(-15deg)}}.{p}-leg-near{{transform:rotate(5deg)}}.{p}-leg-far{{transform:rotate(-4deg)}}.{p}-tail{{transform:rotate(10deg)}}",
        "surprised": "#act{{transform:translateY(-8px) rotate(-3deg)}}.{p}-arm-near{{transform:rotate(-70deg)}}.{p}-forearm-near{{transform:rotate(30deg)}}"
                     ".{p}-arm-far{{transform:rotate(80deg)}}.{p}-leg-near{{transform:rotate(-12deg)}}",
        "scared": "#act{{transform:translate(-10px,4px) rotate(-5deg)}}.{p}-arm-near{{transform:rotate(-55deg)}}.{p}-forearm-near{{transform:rotate(-60deg)}}"
                  ".{p}-arm-far{{transform:rotate(40deg)}}.{p}-leg-near{{transform:rotate(-14deg)}}.{p}-leg-far{{transform:rotate(12deg)}}",
        "smug": "#act{{transform:rotate(-2deg)}}.{p}-arm-near{{transform:rotate(-10deg)}}.{p}-forearm-near{{transform:rotate(140deg)}}"
                ".{p}-leg-near{{transform:rotate(-6deg)}}",
    },
}


def pose_css(sp, pose):
    p, fore, _ = SPECIES[sp]
    if pose == "default": return ""
    body = BODY["host" if sp in ("paleontologist", "skeptic") else "dino"].get(pose, "")
    return (BASE[pose] + body).format(p=p, fore=fore)


# signature move frozen at its peak (values from each species' ACTION keyframes / GSAP timeline)
MOVE = {
    "trex": ("roaring", ".{p}-head{{transform:rotate(-8deg)}}.{p}-jaw{{transform:rotate(16deg)}}"
                        "#arm-near,#arm-far{{transform:rotate(14deg)}}"),
    "triceratops": ("charging", "#act{{transform:translate(22px,5px)}}.{p}-body{{transform:rotate(2.8deg) scale(1.015,.99)}}"
                                ".{p}-head{{transform:rotate(15deg)}}.{p}-tail{{transform:rotate(7deg)}}"
                                "#foreleg-near{{transform:rotate(-13deg)}}#foreleg-far{{transform:rotate(11deg)}}"
                                "#leg-near{{transform:rotate(13deg)}}#leg-far{{transform:rotate(-10deg)}}"),
    "pachycephalosaurus": ("headbutt", "#act{{transform:translateX(26px)}}.{p}-head{{transform:rotate(15deg)}}"
                                       ".{p}-tail{{transform:rotate(5deg)}}"),
    "paleontologist": ("eureka", "#act{{transform:translateY(-44px)}}.{p}-arm-near{{transform:rotate(-87deg)}}"
                                 ".{p}-forearm-near{{transform:rotate(52deg)}}.{p}-head{{transform:rotate(-8deg)}}.{p}-tail{{transform:rotate(-14deg)}}"
                                 "#leg-near{{transform:rotate(-18deg)}}#leg-far{{transform:rotate(14deg)}}"
                                 ".{p}-eyelid{{transform:scaleY(1)}}.{p}-mouth-smile{{opacity:0}}.{p}-mouth-grin{{opacity:1}}"),
    "skeptic": ("point", "#act{{transform:translate(12px,-12px) rotate(4deg)}}.{p}-arm-near{{transform:rotate(-62deg)}}"
                         ".{p}-forearm-near{{transform:rotate(26deg)}}.{p}-head{{transform:rotate(-6deg)}}"
                         ".{p}-mouth-smile{{opacity:0}}.{p}-mouth-open{{opacity:1}}"),
}
POSES = ["default", *EMOTIONS, "walk"]
# limbs drawn without a pivot wrapper: rotate them about the top centre of their own box instead of the page origin
NO_PIVOT = {"trex": "#leg-near,#leg-far", "pachycephalosaurus": "#leg-near,#leg-far,#arm-near,#arm-far"}
SPECIES = {"trex": ("tr", "arm", POSES), "triceratops": ("tri", "foreleg", POSES), "pachycephalosaurus": ("pch", "arm", POSES),
           "paleontologist": ("pal", "arm", POSES), "skeptic": ("skp", "arm", POSES)}


def browser():
    for c in ("msedge", "microsoft-edge", "google-chrome", "chrome"):
        if shutil.which(c): return shutil.which(c)
    for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe", os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")):
        if os.path.exists(p): return p
    sys.exit("no Edge or Chrome found")


def posed(sp, pose, css):
    src = (ROOT / "svg" / (f"{sp}-animated.svg" if sp in ("paleontologist", "skeptic") else f"styles/{sp}-explainer.svg")).read_text(encoding="utf-8")
    src = re.sub(r'(<svg [^>]*?) class="[^"]*"', r"\1", src, count=1)           # stops the idle loop
    src = re.sub(r'width="1000" height="560"', f'width="{W}" height="{H}"', src, count=1)
    i = src.rindex("</style>")   # after the last stylesheet, so poses override the face kit's defaults
    return src[:i] + css + src[i:]


def shoot(exe, svg_text, png, w, h, tmp):
    svg = tmp / (png.stem + ".svg"); svg.write_text(svg_text, encoding="utf-8")
    png.parent.mkdir(parents=True, exist_ok=True)
    png.unlink(missing_ok=True)
    for _ in range(2):  # a headless shot can hang on Windows; retry once with a fresh process
        try:
            subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", f"--user-data-dir={tmp / 'profile'}",
                            f"--window-size={w},{h}", "--default-background-color=00000000", f"--screenshot={png}", svg.as_uri()],
                           capture_output=True, timeout=45)
        except subprocess.TimeoutExpired:
            pass
        if png.exists(): break
    print(png.relative_to(ROOT), "ok" if png.exists() else "MISSING")


def main(names):
    exe = browser()
    with tempfile.TemporaryDirectory() as t:
        tmp = pathlib.Path(t)
        for sp in names or SPECIES:
            p, fore, poses = SPECIES[sp]
            move, move_css = MOVE[sp]
            for pose in poses + [move]:
                css = move_css.format(p=p, fore=fore) if pose == move else pose_css(sp, pose)
                if sp in NO_PIVOT: css = NO_PIVOT[sp] + "{transform-box:fill-box;transform-origin:50% 0}" + css
                shoot(exe, posed(sp, pose, css), OUT / sp / f"{pose}.png", W, H, tmp)
        if not names:
            w, h = 300 * CARD_SCALE, 400 * CARD_SCALE
            for card in CARDS:
                src = (ROOT / "svg" / "scenery" / f"{card}.svg").read_text(encoding="utf-8")
                shoot(exe, src.replace('width="300" height="400"', f'width="{w}" height="{h}"', 1), OUT / "scenery" / f"{card}.png", w, h, tmp)


if __name__ == "__main__":
    main(sys.argv[1:])

import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # repo root: all paths are relative to it
import pathlib, json, importlib.util
spec = importlib.util.spec_from_file_location("dino", HERE + "/build5.py")
dino = importlib.util.module_from_spec(spec); spec.loader.exec_module(dino)
sk = lambda m: m.replace(dino.SKIN, "{{skin}}")

S = 0.8  # scale of the exploded parts
PARTS = [  # (label, markup, viewBox x y w h)
    ("Head and jaw", "#head, #jaw", dino.HEAD, (776, 80, 292, 192)),
    ("Body and neck", "#body", dino.BODY, (434, 138, 416, 280)),
    ("Tail", "#tail", dino.TAIL, (16, 146, 474, 202)),
    ("Near leg", "#leg-near", dino.NEAR_LEG, (366, 158, 270, 362)),
    ("Far leg", "#leg-far", dino.FAR_LEG, (400, 192, 132, 330)),
]
ARMS = [(dino.NEAR_ARM, (748, 288, 70, 74)), (dino.FAR_ARM, (738, 286, 62, 66))]

def part_svg(markup, vb, label):
    x, y, w, h = vb
    return (f'<svg role="img" aria-label="{label}" viewBox="{x} {y} {w} {h}" width="{w*S:.0f}" height="{h*S:.0f}" style="display: block">'
            f'{sk(markup)}</svg>')

def caption(name, ids):
    return (f'<div style="display: flex; flex-direction: column; gap: 2px">'
            f'<span style="font-size: 17px; font-weight: 600; color: #ECE6E8">{name}</span>'
            f'<span style="font-size: 14px; color: #B9B3B6">{ids}</span></div>')

items = []
for name, ids, markup, vb in PARTS:
    items.append(f'<div style="display: flex; flex-direction: column; gap: 14px; align-items: flex-start">{part_svg(markup, vb, name)}{caption(name, ids)}</div>')
arms = "".join(part_svg(m, vb, "Arm") for m, vb in ARMS)
items.append(f'<div style="display: flex; flex-direction: column; gap: 14px; align-items: flex-start"><div style="display: flex; gap: 18px; align-items: flex-end">{arms}</div>{caption("Arms", "#arm-near, #arm-far")}</div>')

HTML = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>T. rex rig sheet</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;600&amp;display=swap">
<style>
body{{margin:0}}
a{{color:#ECE6E8}}a:hover{{color:#FFFFFF}}
.tr-tail,.tr-body,.tr-head,.tr-jaw,.tr-arm,.tr-arm-far{{transform-origin:0 0}}
.tr-eyelid{{transform-origin:0 0;transform:scaleY(0)}}
</style>
</helmet>
<div style="width: 1700px; height: 960px; box-sizing: border-box; padding: 40px 56px; background: #3E3E40; font-family: 'Public Sans', system-ui, sans-serif; color: #ECE6E8; display: flex; flex-direction: column; gap: 28px">
<div style="display: flex; justify-content: space-between; align-items: flex-start">
<div style="display: flex; flex-direction: column; gap: 6px; max-width: 420px">
<h1 style="margin: 0; font-size: 34px; font-weight: 600">T. rex rig</h1>
<p style="margin: 0; font-size: 17px; line-height: 1.5; color: #B9B3B6">Each part is its own group in the SVG, pivoting at its joint. Overlapping ends stay hidden when the parts are assembled.</p>
</div>
<svg role="img" aria-label="Assembled T. rex" viewBox="0 0 1000 560" width="1000" height="560" style="display: block; margin-top: -24px">
{sk(dino.FRAG)}
</svg>
</div>
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: auto">
{"".join(items)}
</div>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"skin":{{"editor":"color","default":"{dino.DEFAULT_SKIN}","options":{json.dumps(dino.SWATCHES)}}},"$preview":{{"width":1700,"height":960}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{ skin: this.props.skin ?? '{dino.DEFAULT_SKIN}' }};
}}
}}
</script>
</body>
</html>
'''
pathlib.Path(HERE + "/project/Rig.dc.html").write_text(HTML)
prev = (HTML.replace('<script src="./support.js"></script>', "").replace("<helmet>", "").replace("</helmet>", "")
        .replace("<x-dc>", "").replace("</x-dc>", "").replace("{{skin}}", dino.DEFAULT_SKIN))
prev = prev[:prev.index('<script type="text/x-dc"')] + "</body></html>"
pathlib.Path(HERE + "/shots/rig.html").write_text(prev)
print("ok")

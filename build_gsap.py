import os as _os
HERE = _os.path.dirname(_os.path.abspath(__file__))  # repo root: all paths are relative to it
import pathlib, importlib.util
spec = importlib.util.spec_from_file_location("dino", HERE + "/build5.py")
dino = importlib.util.module_from_spec(spec); spec.loader.exec_module(dino)

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>T. rex: GSAP animation</title>
<style>
  body {{ margin: 0; min-height: 100vh; display: grid; place-items: center; background: #C9D6DA; font-family: system-ui, sans-serif; color: #2B1E16; }}
  main {{ width: min(1000px, 100%); padding: 24px; box-sizing: border-box; }}
  button {{ all: unset; display: block; width: 100%; cursor: pointer; border-radius: 12px; }}
  button:focus-visible {{ outline: 3px solid #2B1E16; outline-offset: 4px; }}
  svg {{ display: block; width: 100%; height: auto; }}
  p {{ margin: 12px 0 0; font-size: 16px; }}
</style>
</head>
<body>
<main>
  <button type="button" id="rex" aria-label="Make the T. rex roar">
    <svg viewBox="0 0 1000 560" aria-hidden="true">
{dino.FRAG.replace(dino.SKIN, "#9E6B7B")}
    </svg>
  </button>
  <p>Click or tap the T. rex, or press Enter, to make it roar.</p>
</main>

<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script>
  // Every moving part sits in a wrapper whose origin is its joint,
  // so svgOrigin "0 0" pivots each part at the right place.
  const q = (s) => document.querySelector(s);
  const parts = {{
    head: q('#head'), jaw: q('#jaw'), tail: q('#tail'), body: q('#body'),
    armNear: q('#arm-near'), armFar: q('#arm-far'), lid: q('.tr-eyelid')
  }};
  gsap.set(Object.values(parts), {{ svgOrigin: '0 0' }});
  gsap.set(parts.lid, {{ scaleY: 0 }});

  const mm = gsap.matchMedia();

  mm.add('(prefers-reduced-motion: no-preference)', () => {{
    // Idle: quiet and continuous
    gsap.to(parts.body, {{ scaleY: 1.016, scaleX: 1.006, duration: 1.6, ease: 'sine.inOut', yoyo: true, repeat: -1 }});
    gsap.to(parts.tail, {{ rotation: -1.5, duration: 2.5, ease: 'sine.inOut', yoyo: true, repeat: -1 }});
    gsap.timeline({{ repeat: -1, repeatDelay: 4 }})
      .to(parts.lid, {{ scaleY: 1, duration: 0.08, ease: 'power1.in' }})
      .to(parts.lid, {{ scaleY: 0, duration: 0.12, ease: 'power1.out' }});

    // Roar: one choreographed moment, played on demand
    const roar = gsap.timeline({{ paused: true }})
      .addLabel('wind-up')
      .to(parts.head, {{ rotation: 4, duration: 0.25, ease: 'power2.out' }}, 'wind-up')
      .addLabel('open')
      .to(parts.head, {{ rotation: -8, duration: 0.35, ease: 'back.out(2)' }}, 'open')
      .to(parts.jaw, {{ rotation: 16, duration: 0.3, ease: 'power3.out' }}, 'open')
      .to([parts.armNear, parts.armFar], {{ rotation: 14, duration: 0.3, ease: 'power2.out', stagger: 0.05 }}, 'open')
      .to(parts.jaw, {{ rotation: 14, duration: 0.08, yoyo: true, repeat: 5, ease: 'none' }}, 'open+=0.3')
      .addLabel('close', '+=0.1')
      .to([parts.head, parts.jaw, parts.armNear, parts.armFar], {{ rotation: 0, duration: 0.5, ease: 'power2.inOut' }}, 'close');

    const play = () => roar.restart();
    q('#rex').addEventListener('click', play);
    return () => q('#rex').removeEventListener('click', play);
  }});
</script>
</body>
</html>
'''
pathlib.Path(HERE + "/trex-gsap.html").write_text(page)
print("ok")

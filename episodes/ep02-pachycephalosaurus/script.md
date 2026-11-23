# Episode 02 — Pachycephalosaurus (Script & Beat Sheet)

- **Format:** 9:16 vertical short (`1080×1920`, `30 fps`, target `~60 s` / `1800` frames)
- **Setting:** Hell Creek Formation floodplain (`svg/scenery/set-hell-creek.svg`)
- **Cast:** *Pachycephalosaurus wyomingensis* (low-poly sprites in `sprites/pachycephalosaurus-*.png`, from `svg/styles/pachycephalosaurus-lowpoly.svg`)
- **Plain VO text:** [voiceover.txt](voiceover.txt) — 233 words, ~3.9 words/sec.
- **Paradox:** the most famous head-butter is known from little more than a skull, and scientists still argue whether it butted anything.

---

## Beat Sheet

| Target Time | Frames (30 fps) | Beat | Lighting Mood | Camera (zero hard cuts) | Voiceover Line | Visual / Sprite / Badge / SFX |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0:00–0:06` | `0–180` | **1. Paradox Hook** | Warm **Daylight** (`#ffe2a8` key, `#475c96` shadow) | Slow frontal push-in on the dome | *"Pachycephalosaurus is the most famous head-butter in dinosaur history. The strange part? We mostly have its skull. And scientists still argue about whether it butted anything at all."* | `pachycephalosaurus-default.png` centred; badge `SKULL ONLY` pops on "skull" (`paper-snap.wav`, `-8 dB`, 2f early). |
| `0:06–0:16` | `180–480` | **2a. Escalation (Stats)** | Warm **Daylight** | 23f cubic glide behind foreground ferns, then slow push-in | *"Sixty-nine to sixty-six million years ago, this three-meter, four-hundred-fifty-kilogram plant eater roamed Montana, South Dakota, Wyoming and Alberta, carrying a dome of solid bone up to twenty-five centimeters thick. Its beak cropped plants and its teeth were tiny and leaf-shaped, so the weapon was clearly not the mouth."* | `pachycephalosaurus-walk.png` pose swap. Badges: `69–66 MYA`, `3 m`, `25 cm DOME`. On "teeth", `pachycephalosaurus-mouth.png` swap. |
| `0:16–0:24` | `480–720` | **2b. Detail + Dry Gag** | Warm **Daylight** | Lateral drift across the dome and snout | *"Bony knobs line the back of that dome, blunt little spikes decorate the snout, and the eyes face forward for a perfect view of whatever it's about to hit. Basically a crash helmet that grew a personality."* | Callout rings on rear knobs and snout knobs; eye glint on "forward". On "personality", `pachycephalosaurus-blink.png` deadpan blink (`blink-tick.wav`). |
| `0:24–0:43` | `720–1290` | **3. *"You see..."* Pivot** | **Night Blue** (`#6db4ff` key + `#ffad5c` rim, 36f lerp `708–744`) | 23f orbit-push to a low angle on the skull | *"You see, the skull is nearly everything we have. The short neck, small arms and stiff tail are borrowed from smaller relatives, like Stegoceras and Homalocephale. Then in two thousand eight, researchers modeled its skull and found the dome could handle high-energy, head-to-head collisions. Case closed? Not quite. That same study says big adults probably relied on showing off and flank-butting instead."* | Body dims to a ghost outline, leaving only the skull lit (`BORROWED BODY` badge). `pachycephalosaurus-headbutt.png` swap on "head-to-head" (`thud.wav`, `-8 dB`, 2f early). On "Not quite", badge `2008 STUDY` flips to `FLANK-BUTT?`. |
| `0:43–1:00` | `1290–1800` | **4. Ironic Payoff** | **Sunset Glow** (`#ff9d5c` key + `#4c2d6e` shadow, 40f lerp `1270–1310`) | 30f pull-back to wide dusk vista | *"So the most famous head-butter may have shoved ribs, or just shown off, like a deer with antlers. Scientists even argue whether its spiky cousins, Stygimoloch and Dracorex, were separate animals or just teenagers. Hell Creek's biggest head-butter, and we're still not sure it ever butted heads. Call it a skull in search of a story. Hard-headed? Definitely."* | Pachycephalosaurus holds a deadpan stare to camera (`pachycephalosaurus-default.png`); badge `HEAD-BUTTING: DEBATED`. Final 3 s: dust motes drift, `pachycephalosaurus-blink.png` on "Definitely". |

---

## Scientific Accuracy & Sources

| Claim in the script | Source |
| :--- | :--- |
| About 3 m, 450 kg | Natural History Museum Dino Directory. Wikipedia instead gives about 4.5 m and 370–450 kg (Paul 2010); the NHM figure is used. |
| 69–66 million years ago; Montana, South Dakota, Wyoming, Alberta | NHM Dino Directory (Wikipedia gives 70–66 Ma). |
| Dome up to 25 cm; rear knobs, blunt snout spikes, forward-facing eyes, beak, small leaf-shaped teeth | Wikipedia, *Pachycephalosaurus* (description; its lead gives 22 cm). NHM: beak for cropping plants. |
| Body inferred from relatives (short neck, small arms, stiff tail); only skull described | Wikipedia; Moore and others 2026, *J. Vertebr. Paleontol.* (postcranial data lacking in most pachycephalosaurids). |
| 2008 study: skull permitted high-energy head-to-head collisions; large adults likely used display and flank-butting | Snively and Cox 2008, *Palaeontologia Electronica* 11.1.3A. |
| Head-butting vs display debated | NHM Dino Directory. |
| *Stygimoloch* and *Dracorex* as juveniles, disputed | NHM (most scientists think so); Wikipedia (disputed). Written as "argue whether". |

**Deliberately not used:** the "22% of domes show injuries" figure (not verified against the paper), the 2023 keratin-covering finding (not confirmed on the pages read), any bite, speed or force numbers, any claim of a complete skeleton.

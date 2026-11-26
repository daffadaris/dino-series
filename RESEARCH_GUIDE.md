# Research guide: the seven dinosaurs

Read this before drawing, redrawing or rigging any species, in 2D or 3D, and before writing any on-screen claim. It sets the species, the evidence behind each one, size and proportion targets, rig rules and what to avoid. Where it disagrees with a decision in `CLAUDE.md` ("Decisions that must hold"), `CLAUDE.md` wins.

Compiled 2026-11-24 from the user's research bible (research cutoff 24 November 2026) and the reconstruction standard, per-species, comparison, production and reference files that followed it. The values below are the bible's working values. They have not all been re-checked against the primary papers; the sign-off list in [Verification checklist](#verification-checklist) tracks that. When you check one, cite it in the README's "Scientific accuracy" section.

## Contents

- [Series rules](#series-rules)
- [Evidence labels and source order](#evidence-labels-and-source-order)
- [Anatomical workflow](#anatomical-workflow)
- [Measurements](#measurements)
- [The seven at a glance](#the-seven-at-a-glance)
- [Who lived together](#who-lived-together)
- Species: [T. rex](#tyrannosaurus-rex) · [Triceratops](#triceratops-horridus) · [Stegosaurus](#stegosaurus-stenops) · [Dreadnoughtus](#dreadnoughtus-schrani) · [Ankylosaurus](#ankylosaurus-magniventris) · [Spinosaurus](#spinosaurus-aegyptiacus) · [Pachycephalosaurus](#pachycephalosaurus-wyomingensis)
- [Rig architecture](#rig-architecture)
- [Debates and the series position](#debates-and-the-series-position)
- [Verification checklist](#verification-checklist)
- [Verification log and citations](#verification-log-and-citations)
- [Sources](#sources)

## Series rules

1. **Anatomy makes them different.** Each animal must read as itself from its skeleton-driven silhouette, at thumbnail size, not from colour, extra spikes or cartoon exaggeration. All seven share one line weight, shading, eye style, detail scale and light direction.
2. **Never invent a fossil measurement** to make proportions convenient. Unknown value: leave a placeholder and say so.
3. **Never confuse a reconstructed soft-tissue outline with preserved bone.** A sail outline, a lip, a skin pattern is reconstruction; say so in the docs.
4. **Never drop a distinctive anatomical feature** because it makes the rig harder.
5. **Uncertainty goes in the documentation, not necessarily in the picture.** The finished animal can look coherent; the README records what is inferred.
6. **Colour is always artistic interpretation.** No fossil pigment exists for any of the seven. Never claim a colour as fact (no "T. rex was green", no "plates were red").
7. **A museum mount is not a range of motion.** Joint limits come from articulated bones and joint surfaces, not from how a mount is posed. Mounts are often composites.
8. **Plausible is not unique.** Ankylosaurus, Dreadnoughtus, Spinosaurus and Pachycephalosaurus each allow more than one defensible look; pick the mainstream one and note the alternative.
9. **Group poster:** all seven together is a size comparison, labelled as such, never one shared ecosystem.

## Evidence labels and source order

Use these four labels in notes, code comments, README rows and design reviews. A debated feature never looks settled in explanatory material.

| Label | Meaning |
|---|---|
| PRESERVED | Directly represented by fossil bone, skin impressions or other trace evidence |
| RECONSTRUCTED | A reasonable completion from preserved material, close relatives, biomechanics or repeated skeletal patterns |
| DEBATED | Several live interpretations; pick one working version and record the others |
| UNVERIFIED | A number, claim or feature not yet checked against a primary or authoritative source |

Order of authority: (1) peer-reviewed descriptions and specimen monographs, for what is preserved; (2) peer-reviewed biomechanical, histological and comparative studies; (3) museum specimen pages and curator-written summaries; (4) museum mounts and technical skeletal reconstructions, for proportions and articulation; (5) established palaeoartists and skeletal projects, as visual references only; (6) encyclopedias (NHM Dino Directory for quick sizes and ages, Wikipedia as an index to references), never the final word for a rig. A mount may hold casts, mirrored elements, inferred bones or outdated restorations: check it against the specimen description.

## Anatomical workflow

1. Start from a lateral skeletal reference.
2. Set the pelvis, shoulder girdle, ribcage and spine.
3. Place the joints before any muscle volume.
4. Build the skull from bone landmarks, not a generic reptile head.
5. Add muscle envelopes, keeping joint centres and limb proportions visible.
6. Add skin only where evidence or close comparison supports it.
7. Test the silhouette at thumbnail size, without colour.
8. Test standing, walking, turning, feeding and a defensive or signature pose.
9. Log every inferred feature (README "Scientific accuracy", with its label).

A strong reconstruction is not the one with the most detail; it is the one where every visible detail has a defensible reason to be there.

## Measurements

| Term | Definition |
|---|---|
| Total length | Snout tip to tail tip (along the midline when the neck is raised) |
| Hip height | Ground to top of the pelvis, over the hip socket |
| Shoulder height | Ground to top of the shoulder |
| Body length | Shoulder to pelvis, without neck and tail |
| Skull length | Snout tip to back of the skull |
| Tail share | Tail length ÷ total length |
| Forelimb ratio | Forelimb length ÷ hindlimb length |

Proportion tables per species are drawing targets to check a reconstruction against, not published constants. Each species gets its own proportions; never reuse one rig's proportions for another.

**Recording a number:** give the specimen or reconstruction it belongs to; whether it is measured, estimated or extrapolated; the method (mounted skeleton, limb-bone scaling, volumetric model); the source and year; and a range where the uncertainty matters. Keep typical adult and largest known apart, and never present the largest estimate as typical. Never pair a length from one specimen with a mass from another without saying so. Avoid false precision; for Dreadnoughtus and Spinosaurus show competing estimates, not one mass.

**Size comparisons** (group poster, episode stat cards):

1. One 1.75 m human for every species; a scale aid, not a claim they shared a habitat.
2. A common ground line.
3. Say whether a height is hip, shoulder or top of the back.
4. Typical adult shown apart from the largest known or proposed individual.
5. Dreadnoughtus and Spinosaurus dimensions labelled as uncertain.
6. No perspective that changes apparent scale.

## The seven at a glance

| Species | Length | Hip height | Mass | Age | Where | Diet |
|---|---|---|---|---|---|---|
| *Tyrannosaurus rex* | 11.5–12.3 m | 3.5–4 m | 5–8 t | 68–66 Ma | Western North America | Carnivore |
| *Triceratops horridus* | 7.5–9 m | 2.5–3 m | 6–10 t | 68–66 Ma | Western North America | Herbivore |
| *Stegosaurus stenops* | 7–9 m (see note) | 2.5–3 m | 4–7 t | 152–145 Ma | Western North America (Morrison) | Herbivore |
| *Dreadnoughtus schrani* | ~26 m | ~3.9 m (reconstructed) | ~22–59 t (method-dependent) | ~76 Ma | Patagonia, Argentina | Herbivore |
| *Ankylosaurus magniventris* | 6–7 m (up to ~8) | 1.2–1.7 m (reconstructed) | 4–6 t | ~68–66 Ma | Western North America | Herbivore |
| *Spinosaurus aegyptiacus* | 13–14 m | 1.5–2 m (reconstruction-dependent) | Highly uncertain | ~99–93.5 Ma | North Africa | Mainly fish |
| *Pachycephalosaurus wyomingensis* | 4–4.5 m (see note) | 1.3–1.6 m (reconstructed) | 0.3–0.4 t | ~70–66 Ma | Western North America | Herbivore, possibly omnivore |

Open length conflicts (resolve against primaries before changing a drawing): the README draws *S. stenops* at about 6.5 m and says the 9 m figure belongs to *S. ungulatus*; the README draws Pachycephalosaurus at 3.0 m (NHM) against this table's 4–4.5 m.

| Species | Design identity | Shape | Emphasis | Palette direction (artistic) |
|---|---|---|---|---|
| T. rex | The Crushing Wedge | Forward-heavy, triangular, muscular | Skull, thighs, jaws | Charcoal, earthy brown, muted rust |
| Triceratops | The Three-Horned Shield | Broad, front-loaded | Horns and frill | Warm stone, olive, muted ochre |
| Stegosaurus | The Walking Sawtooth | Sloping back, high hips | Alternating plates, tail spikes | Muted green, sandy brown, dark plate accents |
| Dreadnoughtus | The Colossal Column | Very long, cylindrical, towering | Neck, ribcage, limbs | Dusty clay, warm grey, muted red-brown |
| Ankylosaurus | The Armoured Fortress | Low, broad, compact | Armour and tail club | Dark olive, earth brown, stone grey |
| Spinosaurus | The River Sail | Long, low-slung, sail-dominated | Sail and deep tail | Deep teal, slate, muted sand |
| Pachycephalosaurus | The Living Dome | Compact, upright, rounded | Dome and hindquarters | Warm sandstone, muted brown, subdued green |

## Who lived together

- **One real community:** T. rex, Triceratops, Ankylosaurus and Pachycephalosaurus overlap in the Maastrichtian of western North America (Hell Creek and related formations), though not every species is known from the same site or layer. Only these four may share a prehistoric scene, with that caution.
- **Not contemporaries:** Stegosaurus (~150 Ma, Morrison Formation), Dreadnoughtus (~76 Ma, Patagonia), Spinosaurus (~99–93.5 Ma, North Africa).

## Tyrannosaurus rex

Relatively strong skeletal evidence. A large adult, not automatically scaled to the largest specimen. **Series override:** the boxy, blunt-snouted head at 1.4x in `CLAUDE.md` stays even where it exceeds the skull target below.

**Size:** typical adult 11.5–12.3 m, 5–8 t (NHM: ~12 m, 5–7 t; Hutchinson et al. 2011: large adults 6–8 t, Sue ~9.5 t). Largest ~13 m, ~9–9.5 t (Sue, Scotty).

| Skull | Neck | Torso | Tail | Hip height | Fore/hind |
|---|---|---|---|---|---|
| 12–14% | 10–12% | 30–34% | 40–45% | 29–34% | 25–32% |

**Build:**
- Skull deep and robust, broad at the back, narrower snout; large antorbital openings; robust nasal and lacrimal regions; eyes placed for strong forward overlap, not on the sides. Pneumatic inside, solid-looking outside.
- Jaw deep with a strong joint. Teeth thick, recurved, serrated and varied along the jaw, not identical daggers. **Lips cover the teeth when the mouth is closed** (Cullen et al. 2023).
- Neck short, thick, muscular, slight S-curve; never swan-like.
- Torso deep ribcage, big belly, broad pelvis, mass around torso and hips.
- Arms tiny but robust: two fingers, large claws, real shoulder muscle. Not vestigial props.
- Legs: three weight-bearing toes, the fourth small and raised; big thighs, long shins and metatarsals; digitigrade.
- Tail long, deep at the base, gradual taper, heavy caudofemoral muscle. A counterweight, not a whip.

**Rig:** skull limited pitch and yaw; jaw opens wide and closes hard; torso rigid; hip, knee and ankle drive the stride; tail in segments with controlled side-to-side swing. Walk: pelvis shifts a little each step, tail counter-swings, head steadier than the feet, little bounce.

**Skin:** small irregular scales with larger pebbly ones in places; no large plates; no dense feathers on the adult (Bell et al. 2017). Countershading is a hypothesis.

**Avoid:** upright posture, dragging tail, exposed teeth with the mouth shut, big arms, small skull, thin legs, feathers as fact, a mammal-like palm-down wrist. Lip coverage is still debated (the series picks lips); scaly skin rests on absence of feather evidence, which is not proof of absence.

**Model brief (user):** separate skull, upper jaw, lower jaw, tooth rows, left and right eyes, neck, chest, abdomen, pelvis; tail base, middle and tip; left and right upper arms, forearms, two-fingered hands, thighs, lower legs, feet and toes. Massive deep skull with a broad rear and deep snout, horizontal posture, exactly two functional fingers, three weight-bearing toes, powerful thighs and tail, naturalistic scales; skull large but credible; no upright posture or mammal-like limbs.

**Build (2026-11-24):** `src/sp_trex.py` replaces the boxy-head build: 12 m, skull 1.45 m (12%), tail 5.5 m, hips 4.05 m. Tooth rows sit behind the jaws so they show only when the mouth opens (lips, Cullen et al. 2023). The far eye is its own group, hidden behind the skull in this view. Head look follows a user-supplied life restoration for general anatomy only (not traced): rugose brow and nasal ridge, heavy lid, jaw-muscle mass behind the eye, deep rear lower jaw, S-neck with the head hanging forward. Its feathery coat is not followed (adults scaly, per this guide); the orange ridge colour is artistic. Skull drawn at about 1.6 m (13%).

**Scale:** a 1.75 m person reaches the upper thigh to lower chest. **Check against:** FMNH PR 2081 (Sue), MOR 980, CM 9380 (holotype), RSM P2523.8 (Scotty); never merge their dimensions without saying so; Scott Hartman's skeletal. Views: side (skull and tail), front (ribcage, pelvis, limb width), top (skull width, torso taper), three-quarter (skull depth, neck).

## Triceratops horridus

Good skull and skin evidence. *T. horridus*, not *T. prorsus*; never mix their skull proportions (no derived *prorsus* snout).

**Size:** 7.5–9 m, 6–10 t (NHM: ~9 m, 10 t; some estimates to ~13 t). Estimates, not one complete skeleton.

| Skull | Neck | Torso | Tail | Hip height | Fore/hind |
|---|---|---|---|---|---|
| 25–32% | 12–15% | 30–35% | 30–35% | 28–34% | 70–85% |

**Build:**
- Skull very large: short deep snout, parrot-like beak, two massive brow horn cores and a smaller nasal horn, large orbit and temporal openings, strong cheek and jaw. Rear cheek teeth shear plants.
- Horns are bone cores with keratin sheaths; adult orientation, not a scaled-up juvenile; no two individuals identical.
- Frill broad, follows the parietal and squamosal bones, not a perfect circle; edges vary.
- Neck short, strong, heavily muscled.
- Torso broad, deep chest, wide pelvis, massive shoulders; the front half feels very heavy.
- Limbs four weight-bearing, forelimbs short and powerful and not over-splayed, hoof-like keratin on the feet.
- Tail short, thick at the base, tapering; not a weapon.

**Rig:** frill and horns fixed to the skull; head limited pitch and turn; neck limited; torso stable; shoulder protracts, elbow flexes, wrist barely moves. Walk: alternating quadruped gait, head barely bobs, forelimbs carry real weight.

**Skin:** large polygonal (hexagonal, rounded) scales with small ones between, pebbled; smaller scales at joints (Horridus specimen, Melbourne Museum). No bristle coat, no crocodile scutes.

**Avoid:** round frill, three equal horns, fur, a small body under a giant head, bipedal pose, identical horns across a herd.

**Scale:** a person stands about at the lower shoulder. **Check against:** Horridus (Melbourne Museum), YPM 1820 (holotype), MOR 1122, growth-series studies (de Rooij et al. 2024). Views: front (horn spread, frill width), side, three-quarter (horn projection, frill depth), top.

## Stegosaurus stenops

Exceptionally informative: "Sophie", NHMUK PV R36730, described by Maidment, Brassey and Barrett (2015). Make Sophie the primary reference.

**Size:** 7–9 m, 4–7 t (NHM lists 9 m). See the length conflict under [The seven at a glance](#the-seven-at-a-glance).

| Skull | Neck | Torso | Tail | Hip height | Fore/hind |
|---|---|---|---|---|---|
| 6–8% | 12–15% | 30–35% | 40–45% | 28–35% | 50–65% |

**Build:**
- Skull small, narrow snout, toothless front beak, small leaf-shaped cheek teeth, low feeding posture.
- Neck short, blends into the trunk; never giraffe-like.
- Back slopes up to hips much higher than the shoulders; this is the key silhouette.
- **Plates:** two staggered, alternating rows (never pairs side by side); largest over the trunk, smaller to neck and tail; dermal, set in skin, not on vertebral spines. Sophie preserves 18; 19 total is likely.
- Tail long and muscular with **four spikes in two pairs**, never six or eight.
- Limbs: short forelimbs from real manus material (not a generic paw); long, powerful hindlimbs with three main toes; broad feet.

**Rig:** plates and spikes fixed to the skin groups; plate bases follow the back's deformation, almost no independent motion. Head and jaw small movements, neck moderate, torso rigid. Slow quadruped walk driven by the hindlimbs; tail swings sideways as counterweight and weapon, never whipping all the time.

**Skin:** small scales, subtle folds, smooth around plate bases; no armour between plates. **Plate colour unknown:** do not default to red, orange or yellow; a display role is plausible but unproven.

**Avoid:** paired plates, plates on spines, extra spikes, long neck, tall front half, dragging tail. Do not lay all four spikes flat in one sideways plane without checking the chosen reconstruction.

**Model brief (user):** separate skull, upper and lower jaw, neck, chest, abdomen, pelvis; tail base, middle and tip; every dorsal plate its own group; four tail spikes each their own group; left and right fore and hind limbs; feet and toes. Very small head, short neck, bulky torso, high hips and shorter forelimbs, alternating staggered plates, four prominent spikes, long tapering tail. Plates are separate objects with bases blending into the body.

**Numbers used (2026-11-24):** adult *S. stenops* 6.5 m and 3.5 t (Wikipedia). Sophie (Maidment, Brassey and Barrett 2015): 5.5–6 m young adult, femur 86.8 cm, 13 cervical and 14 dorsal vertebrae, 18 plates found and 19 estimated, staggered, Pl13 the largest; four spikes in two pairs, posterodorsolateral, the front pair at about 70° and the back pair at about 80° to the horizontal; hand not preserved. Largest plates in the genus over the hips, up to about 1 m tall (Wikipedia). Hind feet three short hoofed toes; front feet five toes, inner two hoofed (Wikipedia). Throat ossicles absent in Sophie. The old "plates flush red" move is dropped: plate colour is unknown.

**Scale:** a person reaches the lower body to shoulder; plates rise above. **Check against:** Sophie and Maidment et al. (2015) with its skeletal diagrams. Views: side (back profile, hindlimbs), top (plate staggering), front (plate and body width), rear (four spikes).

## Dreadnoughtus schrani

The series titanosaur (decided 2026-11-24; replaces *Patagotitan*). About 70.4% of expected postcranial elements preserved (Lacovara et al. 2014), which is not 70.4% of the animal: the skull and most of the neck are missing, and the neck is restored from relatives such as *Futalognkosaurus*. The holotype was still growing.

**Size:** ~26 m (original reconstruction), hip ~3.9 m (reconstructed). Mass 59.3 t from limb-bone circumference (Lacovara et al. 2014) against much lower volumetric estimates (Bates et al. 2015): show a range with its method, never 59.3 t as the adult mass.

| Skull | Neck | Torso | Tail | Hip height | Fore/hind |
|---|---|---|---|---|---|
| 4–6% | 30–35% | 25–30% | 35–40% | 14–16% | 95–110% |

The describing team's own segment lengths override these targets (Lacovara et al. 2014 via Drexel's FAQ): head about 0.9 m, neck 11.3 m, torso and hips 5.1 m, tail 8.7 m, so neck about 43% and tail about 33% of 26 m. Lacovara et al. held the neck closer to horizontal than in *Brachiosaurus*; forelimbs long but not much longer than the hind limbs; wide-gauge stance (Wikipedia, citing Ullmann and Lacovara 2016). Masses: 59.3 t (limb circumference), 22.1–38.2 t (Bates et al. 2015, volumetric), 48 t (Campione 2017), 49 t (Otero et al. 2020). UNVERIFIED: hip height (guide ~3.9 m; the drawing uses ~4.2 m to the top of the pelvis) and Wikipedia's 6 m shoulder height. Holotype: only a maxilla fragment and a tooth from the skull, one posterior cervical; no hand; hind foot partial (metatarsals I–II, digit I claw).

**Model brief (user):** separate skull, upper and lower jaw; neck in several articulated sections; chest, abdomen and pelvis; tail in several sections; left and right fore and hind limbs; feet and toes. Enormous barrel torso, very thick columnar legs, long muscular neck, relatively small skull, long tapering tail, weight-bearing stance. Conservative titanosaur comparison for unknown regions.

| Region | Evidence |
|---|---|
| Skull | Fragmentary craniodental remains |
| Neck | Mostly reconstructed |
| Back vertebrae, sacrum, ribs, shoulder girdle | Preserved |
| Tail vertebrae | Substantial series |
| Fore and hind limbs | Substantial |
| Pelvis | Preserved, parts reconstructed |
| Feet | Incomplete |

**Build:**
- Head small, long, low narrow snout, peg-like teeth (titanosaur reference). Not a *Camarasaurus*-style box. Not fossil-proven: say so.
- Neck very long, sweeping, comparative; do not state a cervical count without checking the restoration.
- Torso very deep and broad, huge ribcage, massive shoulders and pelvis.
- Limbs thick and columnar: structural supports, not running legs; weight-bearing sauropod hands.
- Tail long, muscular at the base, gradual taper; not a *Diplodocus* whip.

**Rig:** the most constrained rig. Head limited; neck bends in a broad gradual curve, never crane-rigid; torso barely deforms; elbow, knee, wrist and ankle limited. Slow quadruped walk of short weight transfers, feet never lifted high; tail counterbalances turns. Neck carriage anywhere from horizontal to raised is defensible.

**Skin:** small scales, slightly larger in places; osteoderms only sparse and labelled as an uncertain titanosaur possibility; no full armour, no mammal wrinkles.

**Avoid:** a "known" head, whip tail, armour as fact, a precise adult maximum mass, a rigid neck. Say whether a size refers to the holotype or a hypothetical fully grown animal.

**Scale:** by far the longest; use a 1.75 m person (two or three along the body) and a bus. **Check against:** Lacovara et al. (2014) reconstruction and Bates et al. (2015) volumetric models, never a generic titanosaur mount. Views: side, front (shoulder and pelvis width), top (torso, tail taper), three-quarter (limbs, neck-to-torso join).

## Ankylosaurus magniventris

No complete skeleton; the reconstruction must be a composite: AMNH 5895 for most of the body, AMNH 5214 for skull and club, CMN 8880 for the large-animal skull.

**Size:** 6–7 m typical, 4–6 t. Arbour and Mallon (2017): AMNH 5214, the smallest measured individual, ~4.78 t and 6.02–7.95 m with missing parts restored; CMN 8880 implies a larger animal. No established maximum mass.

| Skull | Neck | Torso | Tail | Hip height | Fore/hind |
|---|---|---|---|---|---|
| 10–13% | 8–10% | 35–40% | 35–40% | 15–22% | 75–90% |

**Build:**
- Skull broad, low, wide snout, large nostrils, small teeth, sculpted bony armour, not a smooth box.
- Neck short and broad under cervical armour.
- Torso very wide and low, heavy ribcage, broad pelvis.
- **Armour:** many osteoderm shapes (keeled, pyramidal) in their real positions, large shoulder and pelvic elements, small scales between, following Arbour and Mallon (2017). Not copied from *Euoplocephalus* or *Zuul*; not perfectly symmetrical by invention.
- Limbs short, columnar, broad feet; five digits front and back as the general ankylosaurine plan (check specimens).
- Tail two parts: a stiff muscular handle and a club of fused osteoderms (AMNH 5214 knob ~60 cm long, 49 cm wide, 19 cm high), not a bone stuck on the last vertebra.

**Rig:** armour follows the body; neck restricted; club is one rigid unit; the handle bends only a little, so the club's arc comes from that limited flex, never from a snake-like base. Short strides, low centre of mass, almost no bob.

**Skin:** major osteoderms over pebbled skin, folds at joints; full scale map unknown.

**Avoid:** smooth body, tall legs, thin flexible tail, spiked club or a club like a metal mace, a porcupine field of long spikes, another ankylosaur's armour. The club's bone is PRESERVED; its soft-tissue outline is RECONSTRUCTED. Record which specimen supplies each body region.

**Scale:** a person stands taller than the back; the club sits at torso height or lower. **Check against:** AMNH 5895, AMNH 5214, CMN 8880, Arbour and Mallon (2017). Views: top (armour, width), side (low profile), rear (club width), front (head and shoulder armour).

## Spinosaurus aegyptiacus

The most debated of the seven; never present one reconstruction as settled. Working view: semiaquatic, mostly fish, bipedal on land, a tail suited to some aquatic propulsion, swimming plausible, degree of underwater specialisation disputed.

**Size:** 13–14 m (NHM ~14 m; Sereno et al. 2022 just under 14 m; Ibrahim et al. 2014 longer). Mass highly uncertain. A composite, not one specimen.

| Skull | Neck | Torso | Tail | Hip height | Fore/hind |
|---|---|---|---|---|---|
| 10–12% | 10–13% | 20–25% | 35–40% | 11–15% | 70–90% |

**Build:**
- Skull very long, narrow, crocodile-like, expanded rosette at the jaw tip; conical gripping teeth with little serration, unlike every other predator here.
- Neck fairly long and strong.
- **Sail:** tall narrow neural spines joined by a continuous soft-tissue envelope; not a rigid triangle; its outline need not match the spines.
- Arms strong, three fingers, big claws.
- Legs short (shorter than T. rex), three main toes, big claws. Never long enough to look like a generic theropod with a sail.
- Tail deep at the far end from tall spines and long chevrons, flattened side to side; not a normal tail with a fleshy fin added.

**Rig:** jaw opens wide; torso rigid; sail fixed to the spine group; tail base strong lateral motion, tip more flexible. On land, balanced over the hips. In water, side-to-side tail beats with the body following, never up-and-down like a whale. Build two posture presets: land biped and swimming. Never state swimming speed or manoeuvrability.

**Skin:** scaly, no armour, no feathers assumed; sail covered by soft tissue. Sail colour is a good artistic accent, labelled as such.

**Debates:** tail anatomy real (Ibrahim et al. 2020), hydrodynamics disputed (Hone and Holtz 2021; Sereno et al. 2022); posture quadruped (Ibrahim 2014) vs biped (Sereno 2022): use biped, not as settled; bone density is not a simple aquatic test (2024 review). *S. mirabilis* (Feb 2026) has a scimitar crest: never give it to *S. aegyptiacus*.

**Avoid:** quadruped as fact, whale-like body, giant fleshy tail fin, long legs, short T. rex-like skull, serrated blade teeth, sail on skin rather than spine, the *mirabilis* crest.

**Model brief (user):** long, low skull with a rounded, expanded snout tip and visible conical teeth (not a deep T. rex skull); long neck; tall sail of neural spines with an irregular, natural outline that rises gradually from the neck and falls toward the tail, integrated with the spine (not a triangle fin); short hind legs; deep, laterally expanded paddle tail from tall neural and haemal spines; bipedal standing pose balanced over the hips and tail, never a fully aquatic quadruped; subtle skin texture; no *S. mirabilis* crest.

**Numbers used (2026-11-24; Sereno et al. 2022 and Ibrahim et al. 2020 were not reachable, so from Wikipedia and the NHM):** 14 m, 7.4 t (Sereno 2022); skull 1.6 m (Hendrickx et al. 2016; Dal Sasso et al. 2005 gave 1.75 m); hind limbs a little over a quarter of body length (Wikipedia summary, UNVERIFIED), so the hip socket sits at about 2.5 m, above the guide's 1.5–2 m working figure; spines at least 1.65 m (Wikipedia), sail about 1.5 m high (NHM); subadult neotype tail up to 5.3 m.

**Scale:** longer than T. rex but lower at the hips; compare with a person and T. rex together. **Check against:** BSP 1912 VIII 19, FSAC-KK 11888 (neotype), Ibrahim et al. 2014 and 2020, Sereno et al. 2022. Views: side (sail, skull), top (snout, torso width), front (sail thickness, limbs), three-quarter (tail depth).

## Pachycephalosaurus wyomingensis

The skull is known far better than the body: reconstruct the body conservatively from relatives. Best postcranial reference: *Stegoceras validum* UALVP 2 (and its 2022 limb-muscle study); *Homalocephale* for the pelvis, *Prenocephale* for skull comparison, neither copied wholesale.

**Size:** 4–4.5 m, 300–400 kg (~370 kg, Chinzorig et al. 2025 via a 2026 postcranial study; an estimate). No reliable maximum. See the length conflict under [The seven at a glance](#the-seven-at-a-glance).

| Skull | Neck | Torso | Tail | Hip height | Fore/hind |
|---|---|---|---|---|---|
| 15–19% | 10–13% | 30–35% | 35–40% | 29–36% | 35–50% |

**Directly known:** the frontoparietal dome, skull roof, ornament, parts of the skull, a few isolated body bones. Not known as a complete skeleton: neck, spine, ribs, shoulder, arms, pelvis, legs, tail.

**Build:**
- Dome thick, rounded bone (not an inflated forehead, not keratin, not a sphere or basketball), nodes along the rear skull margin, large orbits, beak, small leaf-shaped back teeth.
- Adult only: full dome, no flat *Dracorex* skull, no long *Stygimoloch* horns (Horner and Goodwin 2009 read the three as growth stages; influential, not settled).
- Neck short, strong, from relatives; never swan-like.
- Torso compact, broad pelvis, muscular hindquarters.
- Arms short and weak, small hands. Legs strong, bipedal, three main toes.
- Tail fairly long, stiffened by ossified tendons (the caudal basket); never whip-like.

**Rig:** dome fixed to skull; head controlled pitch and yaw, never bird-like on a thin neck; torso rigid; tail limited lateral movement. Walk: hindlimbs drive, tail counterbalances, head steady.

**Head-butting:** unsettled (head-to-head, oblique, flank strikes, display, or a mix). The dome could take heavy loads and *Stegoceras* hips suit a stable stance (2022), but that is not proof. Do not animate repeated high-speed, perfectly head-on collisions as established behaviour.

**Skin:** small pebbly scales, no armour or body spikes, no feathers assumed; not proven identical to relatives.

**Avoid:** keratin dome, oversized sphere, *Dracorex* skull, *Stygimoloch* horns, strong arms, whip tail, head-butting as fact, a "fully known" skeleton.

**Scale:** the smallest; a 1.75 m person stands about as tall as the back or taller. **Check against:** Pachycephalosaurus skull material, UALVP 2, *Homalocephale*, *Prenocephale*, Horner and Goodwin (2009), the 2022 *Stegoceras* myology paper. Views: side (dome, balance), front (dome thickness), top (skull outline), rear (dome-to-neck, nodes).

## Rig architecture

A shared hierarchy with species-specific modules. In the SVG rigs, existing group ids, classes and pivots stay (`CLAUDE.md`); add finer pivots inside an existing group rather than renaming it.

```text
Root
├── Pelvis
├── Torso (Chest, Abdomen)
├── Neck (Neck_01..05) > Head (Skull, Upper_Jaw, Lower_Jaw, Eyes)
├── Tail (Tail_01..08, Tail_Tip)
├── Forelimbs L/R (Upper, Lower, Wrist, Foot)
└── Hindlimbs L/R (Thigh, Lower, Ankle, Foot)
Species modules: T. rex Arms · Triceratops Horns, Frill · Stegosaurus Plate_01..19, Thagomizer
  · Dreadnoughtus Long_Neck · Ankylosaurus Osteoderms, Tail_Club · Spinosaurus Sail, Paddle_Tail · Pachycephalosaurus Dome
```

| Feature | Construction |
|---|---|
| Jaw | Separate upper and lower jaw pivots |
| Eyes | Own groups, constrained movement |
| Tail | 4–8 segments, by how much it animates |
| Neck | 2–5 segments, by length |
| Limbs | Three main sections |
| Armour, plates | Attached to skin groups, never floating |
| Frill, dome | Fixed to the skull |
| Sail | Attached to the spine and its soft tissue |
| Tail club | One rigid terminal unit |

Keep three limits apart for every joint: **anatomical** (what the joint could plausibly do), **animation** (what reads well on screen) and **illustration deformation** (how far to exaggerate for readability). An appealing move must stay inside the anatomical limit.

**Pivots** sit at estimated joint centres (shoulder, hip, elbow, knee, wrist, ankle, jaw hinge, neck and tail joints), never just where two vector shapes overlap. For a new species or a redraw, keep a hidden skeletal guide layer so joint positions survive later edits. Linework and fill of a part stay in one group so they never separate in motion.

**Motion checks** (standing, walk, head turn, jaw, tail, signature move): feet do not slide; limbs do not pass through the torso; outlines do not split at joints; no bending in the middle of a long bone; no mammal-like wrist on a theropod; neck and tail do not bend as one rubber tube; plates, armour and horns stay on their attachment; the centre of mass stays over the feet unless the move is meant to tip.

**3D handoff:** keep the same anatomical names as the 2D rig. Separate the deforming mesh, the rigid structures (plates, osteoderms, horns, spikes), the control rig, the reference skeleton and the colour interpretation. Controls may differ between 2D and 3D; the anatomy must agree.

## Debates and the series position

| Topic | Positions | Series choice |
|---|---|---|
| T. rex lips | Exposed vs covered teeth | Lips cover teeth when closed |
| T. rex skin | Scales vs some feathers | Scales |
| T. rex posture | Upright vs horizontal | Horizontal (high confidence) |
| Triceratops frill | Defence vs display | Structural, possibly display |
| Triceratops / *Torosaurus* | Separate vs growth stage | Not settled; don't treat as synonyms |
| Stegosaurus plates | Thermoregulation vs display/defence | Display-capable, function uncertain |
| Dreadnoughtus mass | Limb scaling vs volumetric | Show a range |
| Ankylosaurus armour | Exact arrangement | Composite, evidence-based |
| Spinosaurus posture | Biped vs quadruped | Biped on land |
| Spinosaurus swimming | Shore forager vs pursuit swimmer | Semiaquatic, swimming plausible |
| Pachycephalosaurus dome | Combat vs display | Possibly both |
| Pachycephalosaurus growth | Three taxa vs one growth series | Adult form; note the debate |

## Verification checklist

Tick these off against primary sources before approving the final seven; record each in the README with its citation. Suggested approval order: Stegosaurus, T. rex, Triceratops, Ankylosaurus, Dreadnoughtus, Spinosaurus, Pachycephalosaurus.

- [ ] T. rex: skull-to-body proportions against Sue or Scotty
- [ ] T. rex: latest reading of facial scales, lips and tooth exposure
- [ ] Triceratops: skull is *T. horridus*, not *T. prorsus*
- [ ] Triceratops: adult horn orientation and frill shape against the chosen specimen
- [ ] Stegosaurus: Sophie's plate order and four-spike arrangement
- [ ] Stegosaurus: forefoot digits and joint surfaces
- [ ] Dreadnoughtus: preserved-element share, and which neck parts are reconstructed
- [ ] Dreadnoughtus: which mass estimate is shown, with its method
- [ ] Dreadnoughtus: hip height from the published skeletal, not a life restoration
- [ ] Ankylosaurus: skull, body and club reconciled across their specimens
- [ ] Ankylosaurus: osteoderm arrangement against Arbour and Mallon (2017)
- [ ] Ankylosaurus: digits and feet from ankylosaurine specimens
- [ ] Spinosaurus: 2014, 2020 and 2022 skeletals compared
- [ ] Spinosaurus: tail, body proportions and sail outline checked independently
- [ ] Spinosaurus: no swimming speed or pursuit ability stated as fact
- [ ] Spinosaurus: *S. mirabilis* (2026) crest not transferred
- [ ] Pachycephalosaurus: which skull elements are directly preserved
- [ ] Pachycephalosaurus: body rebuilt from *Stegoceras* and relatives
- [ ] Pachycephalosaurus: *Dracorex*/*Stygimoloch* growth reading and its caveats
- [ ] All: direct skin impressions told apart from inferred scale patterns
- [ ] All: joint limits from articulated skeletal evidence
- [ ] All: colour schemes labelled as artistic interpretation

## Verification log and citations

Log each claim before it goes on a drawing, poster or screen; the README's "Scientific accuracy" rows are where checked entries end up.

| Claim or feature | Taxon | Source (author, year, DOI) | Specimen | Evidence type | Status |
|---|---|---|---|---|---|
| e.g. adult length | | | | measured / estimated / reconstructed | UNVERIFIED |
| e.g. limb posture | | | | fossil / biomechanical / comparative | UNVERIFIED |
| e.g. skin texture | | | | skin impression / comparative | UNVERIFIED |
| e.g. colour | | | | pigment evidence / artistic | UNVERIFIED |

Before citing, confirm the exact title, authors, year, DOI, specimen number and the specific claim: a source for one feature does not cover every number. Record the date checked for any web page.

**Finished videos:** a short on-screen credit only where it stays readable; full references in the video description or a linked bibliography. Every striking number needs a traceable source; if it cannot be verified, drop it or call it an estimate.

## Sources

- **T. rex:** NHM Dino Directory, *Tyrannosaurus*; Hutchinson et al. (2011), A computational analysis of limb and body dimensions in *Tyrannosaurus rex*; Bates et al. (2009); Bell et al. (2017), tyrannosauroid integument; Cullen et al. (2023), Theropod dinosaur facial reconstruction and the importance of soft tissues in paleobiology; Rowe and Rayfield (2024), giantism in tyrannosauroids.
- **Triceratops:** NHM, *Triceratops* and Biggest dinosaurs; de Rooij et al. (2024), the ceratopsid growth record; Melbourne Museum, Horridus revealed.
- **Stegosaurus:** Maidment, Brassey and Barrett (2015), The postcranial skeleton of an exceptionally complete individual of *Stegosaurus stenops*; NHM, *Stegosaurus*.
- **Dreadnoughtus:** Lacovara et al. (2014), A gigantic, exceptionally complete titanosaurian sauropod dinosaur from southern Patagonia, Argentina; Bates et al. (2015), Downsizing a giant: re-evaluating *Dreadnoughtus* body mass.
- **Ankylosaurus:** Arbour and Mallon (2017), Unusual cranial and postcranial anatomy in the archetypal ankylosaur *Ankylosaurus magniventris*.
- **Spinosaurus:** NHM, *Spinosaurus*; Ibrahim et al. (2014, 2020); Hone and Holtz (2021); Sereno et al. (2022), *Spinosaurus* is not an aquatic dinosaur; 2024 review, Diving dinosaurs? Caveats on bone compactness and pFDA; University of Chicago (2026), *Spinosaurus mirabilis*.
- **Pachycephalosaurus:** Horner and Goodwin (2009), Extreme cranial ontogeny in *Pachycephalosaurus*; The appendicular myology of *Stegoceras validum* (2022); 2026 pachycephalosaur postcranial study (citing Chinzorig et al. 2025).

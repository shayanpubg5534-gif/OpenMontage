# Character versions (reproducible register)

The approved production character system is **Rig v4**. It is unchanged and remains the production default. The
MPFB character layer stays experimental until it passes visual, motion, interaction and performance approval.

| Version | Status | What it is | Where | How to reproduce |
|---|---|---|---|---|
| **Rig v4** | **Production** (unchanged) | Hand-authored vector characters (founder, investor) | `epoch-ledger/kit/rig4.js`, `kit/rig4.py` | As used by the existing episode builds; nothing in the character lab touches these files |
| **M2.3b** | Technical milestone (approved); superseded as a look | MPFB characters (`elias`, `nadia`) with stock MakeHuman heads and hair; three treatments | commit `c2215dc`; specs `charlab/specs/elias.json`, `nadia.json`; viewer `viewer/lookdev2.html` | `charlab/README.md`, section "M2.3b". Rebuilding `elias.json` with today's `build_dressed.py` gives an identical report (checked in M2.3c) |
| **M2.3c** | **Provisional visual baseline** (approved for the next milestone, not for production) | Designed faces, original procedural hair, designed brows, lash lines, illustrated eyes; flat editorial | commit `736fc94`; specs `elias_c.json`, `nadia_c.json`; `stylise.py`; viewer `viewer/lookdev3.html` | `P2_M23C_REPORT.md`, "Reproducibility" |
| **M3 (motion lab)** | Conditionally accepted as a technical foundation (not a visual standard) | M2.3c characters with mocap clips, a deterministic performance compiler and animated demos | `charlab/motion/` (`elmotion.js`, `stage.js`, `demos/`), `viewer/motion.html`, `motion_render.mjs`; Nadia's spec adds `cloth_follow_legs` | `P2_M3_REPORT.md`, "Reproducibility" |
| **M4 (environments, story, HyperFrames)** | Approved as an experimental technical baseline (not a visual standard) | Set library, bank and bakery sets, motion-quality layers, narrated story through HyperFrames, presets | `charlab/motion/{env,runtime}.js`, `sets/`, `hf_build.py`, `build_m4.sh` | `P2_M4_REPORT.md`, "Reproducibility" |
| **M5 (look, characters D, narration-driven sequence)** | Conditionally accepted as an experimental technical baseline only (option a). **Not approved for production; characters rejected as an artistic standard** | Editorial look (soft shadows, crease AO, haze, DOF, coloured lines); natural gaze and head/neck; redesigned D characters (`elias_d`, `nadia_d`) with mouth units for lip sync; bakery set rebuilt; lip sync for spoken lines only; narration-driven 25 s sequence (3D + document + timeline + chart) | `motion/stage.js` (`look: editorial`), `elmotion.js` (gaze, `speech`), specs `*_d.json`, `lipsync.py`, `splice_dialogue.py`, `hf_sequence.py`, `sequences/m5_acceptance.py`, `DIRECTION.md` | `P2_M5_REPORT.md`, "Reproducibility". M2.3c/M4 characters (`*_c`) and the cel look stay the defaults |
| **Artistic-direction gate** | Decided: option D, hybrid (Snow as the craft reference; conversion feasibility next; no artist or purchases yet) | Blender Studio characters (CC-BY), code-drawn 2D, CharMorph and M5 compared in static sheets; integration and cost measured | `charlab/bstudio/`, `charlab/illus/`, `viewer/integration.html` | `P2_ARTGATE_REPORT.md` |
| **Conversion feasibility (Snow)** | In progress | Blender-to-runtime conversion of a professionally made CC-BY character: baked geometry, face poses baked to morph targets under our unit names, baked materials, skeleton mapped to our bone names | `charlab/convert/` | `P2_CONVERT_REPORT.md` (at the gate) |

Rules:
- New lab work adds files or opt-in spec fields. A spec without the new fields builds exactly as before.
- The M2.3b and M2.3c viewers (`lookdev2.html`, `lookdev3.html`) are frozen; M3 uses its own module (`motion/stage.js`).
- Third-party assets and generated GLBs stay out of git (`.runtime/`); everything is rebuilt from scripts.

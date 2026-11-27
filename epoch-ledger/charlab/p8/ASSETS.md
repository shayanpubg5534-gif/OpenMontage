# P8 asset provenance and licensing

Raw third-party files are kept in `.runtime/charlab/p8/src/` (git-ignored) and are **not committed**. Only our own code,
our derived renders and the notes below are in the repository.

| Asset | Supplied as | SHA-256 (first 16) | Source / author | Licence | Notes |
|---|---|---|---|---|---|
| Businessman | `businessman.blend` (Blender 4.0) | `7d545daf5ad3e5ba` | Daydreams Creative Studios, Fab (free listing) | **Fab Standard License**: rendered video allowed; the asset itself may not be redistributed | Built with MPFB/MakeHuman: MakeHuman body, skin, `toigo_male_suit_3`, `afro01`, `shoes04`, eyebrows, lashes, teeth and tongue are MakeHuman system assets (CC0 upstream). Rigify rig |
| Businessman | `businessman.glb` | `a4c4d845f46950f9` | same (generator "fab-model-conversion") | same | 8 skins, no morph targets, no animations; contains a stray 2 m "Icosphere" helper mesh |
| Businessman | `businessman.fbx` (FBX 7400) | `ab2fd8a366126919` | same | same | Subdivision baked (suit about 65k triangles); FBX import adds leaf bones (1,667) |
| Open Peeps (multicolour) | `open-peeps.fig` (Figma "fig-kiwi") | `d32f1937a6a8e7ab` | Pablo Stanley, openpeeps.com | **CC0** | Decoded by `figdecode.py` / `peeps_extract.py` (no Figma needed) |
| Open Peeps Flat Assets | `Flat Assets.zip` | `2e0a4e79c868ae71` | Pablo Stanley | **CC0** | 358 SVG + 185 PNG, monochrome (ink and white, one blue accent): "Separate Atoms" (parts) and "Templates" (bust, sitting, standing) |
| Bank set | `motion/sets/bank_office.json` | — | ours (P4) | ours | |

Renders of the Fab asset are images, which the Fab Standard License permits. Open Peeps derivatives are CC0 (no
attribution required; we credit the artist anyway).

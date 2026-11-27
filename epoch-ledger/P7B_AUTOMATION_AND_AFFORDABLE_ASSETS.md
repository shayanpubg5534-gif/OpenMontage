# P7 (supplementary) — automation compatibility, affordable character assets, 2D / 2.5D / 3D (decision gate)

**Constraint added:**
- You work only from an Android phone.
- Production must run through Claude Code in the Linux cloud environment, so anything that needs a person at a
  Windows or macOS desktop is unsuitable.

**Scope:** research only. Nothing was purchased, installed, built or rendered. Variant B (P6), Rig v4, the P5 renderer,
production defaults and the narration and dialogue standard are unchanged. Date: 2026-11-27.

**Evidence limit:**
- Vendor sites are blocked from this environment (DNS), so facts come from web searches restricted to each vendor's
  domain, with links.
- **No asset's appearance was inspected; none is claimed to pass the artistic standard.**
- §6 lists what to open on your phone and screenshot.

## 1. Character Creator 5 under the Android + Linux constraint: **not suitable**

| Question | Verified | Not verified / theoretical |
|---|---|---|
| Runs on Linux, macOS or a VM? | **No.** Reallusion's FAQ: CC5 and iClone 8 support Windows only and do not support virtual machines ([CC5 store page](https://www.reallusion.com/plan-and-pricing/individual/perpetual/character-creator-5-3101); [Linux thread](https://discussions.reallusion.com/t/linux-for-reallusion-software/12694)) | Wine: no evidence it works |
| Scripting / headless | CC has a Python API, but scripts run **inside the running CC GUI**. A community project reports that headless runs crash with access violations, so it falls back to a GUI plugin job queue ([Hephaestus PR #41](https://github.com/Athibault36/Hephaestus/pull/41)). Community MCP bridges forward commands to a plugin inside a running CC5 ([cc5-mcp-server](https://github.com/mackatwentytsuru/cc5-mcp-server)). Reallusion staff: Headshot "Mesh to Head" is not yet scriptable ([forum](https://discussions.reallusion.com/t/automating-landmark-placement-in-headshot-3/18419)) | "Headless FBX export" appears only in a marketplace description of a community tool |
| Remote execution | Possible only with a rented or owned Windows machine running the GUI and a bridge plugin | Cost, reliability and licence for a cloud Windows VM not verified |
| Customise exported characters in Blender with Python? | Yes for import: the free official Blender Auto Setup add-on (soupday `cc_blender_tools`, rebranded by Reallusion in 2024) imports CC exports into Blender ([GitHub](https://github.com/soupday/cc_blender_tools); [CGChannel](https://www.cgchannel.com/2024/11/free-tool-reallusions-blender-auto-setup-plugin/)). Exported meshes, rigs, materials and any exported shape keys can then be edited with Blender Python | New identities, ActorMIXER blends and the CC wardrobe fitting need CC5 again, so every new character needs a Windows session |

**Conclusion:** CC5 cannot be part of an Android-controlled automated workflow. A one-time batch made on someone's
Windows PC would be possible, but it is outside your constraint. It is withdrawn from the recommendation.

## 2. Affordable artist-made 3D characters (Blender Python and GLB compatible)

| Asset | Source | Price (verified where marked) | Licence | What you get | Fit for our standard |
|---|---|---|---|---|---|
| **Lab3 Studio "Business Man 01"** | [Fab](https://www.fab.com/listings/1d062181-d5bc-49b0-9331-ae6b7895548d), seller [Lab3 Studio](https://www.fab.com/sellers/Lab3%20Studio/about); also [Characters Bundle 01](https://www.fab.com/listings/af731659-11b3-4306-b9cf-ecabfccad059) and [Business Essentials Bundle 01](https://forums.unrealengine.com/t/lab3-studio-lab3-business-essentials-bundle-01/2667075) | **$39.99** (listing data; per-tier price not visible); bundles unverified | [Fab Standard License](https://www.fab.com/eula): rendered video allowed; engine-agnostic | Stylised "contemporary/corporate" man, modular parts, ARKit face shapes, blink example, Unreal Quinn skeleton, **source FBX** | **Most promising cheap 3D option; appearance unknown** |
| "Businessman – Modular – Rigged – Animated" | [Fab](https://www.fab.com/listings/7ddc1954-f7d7-49cf-acd0-b8662cc6ba7f) | **$79.99** | Fab Standard | One modular businessman; face rig not confirmed | Unknown |
| **Quaternius Universal Base Characters** | [quaternius.com](https://quaternius.com/packs/universalbasecharacters.html), [itch.io](https://quaternius.itch.io/universal-base-characters) | **Free** | **CC0** | 6 bodies (regular, superhero and teen; male and female), 20 hairstyles, humanoid rig, FBX, glTF and .blend, about 13k triangles; **no face rig mentioned**; outfits only fantasy ([kit](https://quaternius.com/packs/modularcharacteroutfitsfantasy.html)) | Low-poly game style, **below our standard**; useful only for crowds and tests |
| KayKit character series | [itch.io](https://kaylousberg.itch.io/kaykit-series-5) | From $19.99 | CC0 | Blocky game characters | Fails the mature standard |
| Mixamo characters and animations | [Adobe FAQ](https://helpx.adobe.com/au/creative-cloud/faq/mixamo-faq.html) | **Free** (Adobe ID) | Royalty-free for commercial films and videos; no redistribution of raw files | Game-style characters; **a large mocap animation library** | Characters below standard; **animations useful** with any rig we retarget (as in M3–P5) |
| Sketchfab CC-BY business men (e.g. [Eric rigged](https://sketchfab.com/3d-models/eric-rigged-001-rigged-3d-business-man-a46bc9f67aaa415bb4f3241eef900e7f)) | Sketchfab | Free | CC-BY (per listing) | Single characters, mixed quality | Unknown, inconsistent styles |

**Practical constraint:**
- Store downloads (Fab, Superhive, itch.io, Mixamo) need your account in a browser. You would buy or download once
  on your phone and put the file where this session can read it, for example an upload or a private release on the
  repository.
- After that, everything (Blender Python, conversion to our skeleton, GLB, rendering) runs here automatically, as for
  Snow in P3.

**Assessment:** no affordable 3D source was found that offers a **consistent 6–10-character adult cast in one premium
style with interchangeable wardrobe and face rigs**. Lab3 Studio is the only seller whose line appears built for
exactly this setting: several corporate men and women, modular clothing, ARKit faces. It needs your screenshots before
any judgement.

## 3. Budget tiers (research tiers, not spending limits)

| Tier | 3D option | 2D / 2.5D option |
|---|---|---|
| **Free** | Quaternius (CC0), Mixamo animations, CC-BY singles; P6 Variant B as a technical base | Our approved Rig v4 vector characters; [Open Peeps](https://openpeeps.com) (CC0, modular hand-drawn SVG people); code-drawn designs (P2 art gate) |
| **< $25** | KayKit series ($19.99, CC0) | One layered vector character kit (marketplace kits typically about $15–40; e.g. a [Gumroad set of 10 business characters, 2 angles each, AI/SVG/PNG, A$35](https://dkirkland.gumroad.com/l/SdkpFB), slightly above) |
| **< $50** | **Lab3 "Business Man 01" ($39.99)**: one character plus parts | One or two layered vector business-character kits |
| **< $100** | Lab3 man plus a Lab3 woman, or a bundle (prices unverified); or the $79.99 Fab businessman | Vector kit with extended licence (e.g. [Adobe Stock constructor](https://stock.adobe.com/images/businessman-front-view-animated-flat-vector-character-design-office-worker-character-animation-creation-cartoon-set-top-manager-ceo-constructor-with-various-face-emotion-hand-gestures-legs-kit/282594877), extended licence about $79.99 per one listing) |
| **< $200** | Lab3 bundles (if prices fit) for a small corporate cast | Several matching kits from **one** illustrator (a consistent style), enough for 6–10 characters |

## 4. Licensing: internal real-time rendering to MP4 vs distributing an interactive app

Our three.js runtime renders frames internally; only MP4 video is published. No 3D asset or application is distributed.

| Source | Rendered video | Internal real-time renderer | Needs written confirmation? |
|---|---|---|---|
| **Fab Standard** | Allowed ("rendered linear media", e.g. "broadcast or streamed video files") ([EULA](https://www.fab.com/eula)) | Engine-agnostic ([Fab docs](https://dev.epicgames.com/documentation/en-us/fab/licenses-and-pricing-in-fab)); the restriction is redistributing the asset | No for our use. The Personal tier needs revenue under about $100k |
| **CC0** (Quaternius, Open Peeps) | Unrestricted | Unrestricted | No |
| **Mixamo** | Allowed (films and videos) ([FAQ](https://helpx.adobe.com/au/creative-cloud/faq/mixamo-faq.html)) | Allowed; no raw-file redistribution | No |
| **CC-BY** (Reom, Sketchfab, Blender Studio) | Allowed with attribution | Allowed | No (credit line needed) |
| **Reallusion** (if ever) | Standard licence allows export and commercial video ([policy](https://www.reallusion.com/license/content.html)) | Clause limiting "interactive services" to one character per licence; internal rendering is probably not an interactive service | **Yes** |
| **Daz** | 2D renders and animation allowed ([EULA](https://www.daz3d.com/eula)) | "Interactive Licences" cover games and apps; whether export to another program is allowed is disputed | **Yes** |
| Stock vector kits (Adobe Stock, Envato) | Standard licences usually allow video use; some limit views or copies, and extended licences remove limits | Not relevant (2D) | Check per item |

Internal real-time rendering is **not** treated as an interactive product unless a licence says so explicitly. Under
Fab, CC0, CC-BY and Mixamo it is clearly fine.

## 5. 2D vs 2.5D vs 3D vs hybrid (objective comparison with our own measurements)

| | **2D vector (production today)** | **2.5D** (layered 2D characters in a depth or parallax scene with camera, light and DOF) | **3D** (P3–P6 lab) | **Hybrid** (3D sets and props + 2.5D characters) |
|---|---|---|---|---|
| Render speed (this 4-core CPU) | **≈ 2.3 min per 10 s** (0.47 s per frame, scene-cached; `epoch-ledger/README.md`) | ≈ 2D to 1.5× 2D (layer compositing and DOF; existing `scene3d.js`, `three_kit.js`) | **8.4 min per 10 s** (P5, measured) | Between, depending on the set (P4 sets about 0.6–1.2 s per frame) |
| Fully automated in Linux, phone-controlled | **Yes** (approved pipeline) | **Yes** (same tools) | Yes, once assets exist | Yes |
| Character assets | Code-drawn (Rig v4); P2 art gate: clean editorial, but hands, hair and three-quarter faces below premium | Same art, with depth and light adding production value | **Unsolved:** no affordable premium cast found | 2D art problem only |
| Path to premium art at low cost | **Artist-made layered vector kits** (about $15–80 each) or a small 2D commission, converted to SVG and rigged by our code | Same, plus painted texture overlays (paper, grain, brush shading through SVG filters, free) | Artist-made 3D cast (P7: $8k–25k custom; cheap packs unverified) | Same as 2.5D |
| Consistency across 6–10 characters | High if all from one illustrator or kit family | High | Hard: mixing packs breaks the style | High |
| Expressions, gestures, lip sync (scripted dialogue only) | Proven in Rig v4 (poses, expressions; mouth only via `say()`) | Same | Proven in the lab (P3–P5) | Same as 2D |
| Fit to "premium animated financial and historical documentaries" | Good for diagrams and editorial; characters limited by the art | **Strong:** the illustrated-documentary look (layered art, parallax, lighting, camera moves) | Strong only with a premium cast | **Strong** |
| Cost to start | $0 | $0–100 | $40–200 for a few unverified characters, or thousands custom | $0–100 |

**Tools for 2D/2.5D without desktop operation:**
- **Already working:** our SVG rigs (Rig v4) in HyperFrames, GSAP, three.js planes for 2.5D, Inkscape command line
  for conversions, all free and headless.
- **Rejected:**
  - Synfig has a command-line renderer, but its SVG import is unreliable ([wiki](https://wiki.synfig.org/Svg2sif)).
  - Rive's runtimes are MIT, but its editor is a GUI and free exports carry a splash ([pricing](https://rive.app/pricing)).
  - Spine's runtimes are tied to a paid editor licence (per a [competitor comparison](https://rive.app/rive-vs-spine); unverified).
  - All three would add manual desktop work.

**Conclusion:**
- For this production setup (phone control, Linux automation, CPU rendering, low budget), **2.5D and hybrid are the
  better route to premium-looking documentaries**: about 3.6× faster than 3D in measured terms, already automated, and
  cheap to upgrade artistically.
- 3D characters remain blocked by the lack of an affordable, consistent, premium cast.
- **The deciding factor for 2D/2.5D is the artwork source, not the technology.** Our code-drawn ceiling (P2) is below
  premium. Artist-made layered vector characters are the cheapest way past it, but their style must be checked: many
  kits are generic "flat corporate explainer" art.

## 6. What to open on your phone and screenshot (2–3 images each)
1. Lab3 Studio [Business Man 01](https://www.fab.com/listings/1d062181-d5bc-49b0-9331-ae6b7895548d): face close-up and full body. Also the seller page [Lab3 Studio](https://www.fab.com/sellers/Lab3%20Studio/about), for women and other characters in the same style.
2. Fab [Businessman – Modular – Rigged – Animated](https://www.fab.com/listings/7ddc1954-f7d7-49cf-acd0-b8662cc6ba7f).
3. Quaternius [Universal Base Characters](https://quaternius.com/packs/universalbasecharacters.html) (to confirm it fails, quickly).
4. 2D: the [Gumroad business characters set](https://dkirkland.gumroad.com/l/SdkpFB), the [Adobe Stock business constructor](https://stock.adobe.com/images/businessman-front-view-animated-flat-vector-character-design-office-worker-character-animation-creation-cartoon-set-top-manager-ceo-constructor-with-various-face-emotion-hand-gestures-legs-kit/282594877), and [Open Peeps](https://openpeeps.com).
5. Optionally, any illustrator whose documentary style you like (e.g. on ArtStation or Behance) that offers layered
   character sets. That style decision matters more than the tool.

## 7. Recommended direction (your decision)

**1. Approve 2.5D / hybrid as the main character direction for P8**, using what is already automated:
- the Rig v4 vector rig system;
- layered, lit characters in parallax and depth scenes (the existing `scene3d.js` and three.js tools, and P4 sets as
  backdrops if wanted);
- painted texture treatments;
- 3D kept for environments, props and data scenes.

**2. Choose the artwork source by screenshots (§6).** Either:
- a matching set of artist-made layered vector characters (research estimate: under $100–200 for 6–10 characters from
  one illustrator or kit family), converted and rigged by code; or
- if none convinces you, stay on our own vector designs for now.

**3. Keep the 3D lab as is** (P6 Variant B, the P5 renderer). Revisit a 3D cast only if a screenshot-verified
affordable source appears (the Lab3 line is the one to watch).

**4. CC5 and Daz:** withdrawn under the Android + Linux constraint.

**5. Custom commissions** are not the default fallback.

Stopping here at the decision gate.

# Hybrid-architecture feasibility spike (not production)

Skinned 3D characters rendered by three.js (MIT) in headless Chromium on the CPU (SwiftShader), with toon shading and
ink outlines, a prop parented to the hand bone, a table that occludes a character through the depth buffer, three
camera framings, and deterministic seeking (`AnimationMixer.setTime`).

Reproduce (from this folder; assets are fetched, not committed):

    npm pack three@0.160.0 && mkdir -p pkg && tar xzf three-0.160.0.tgz -C pkg
    mkdir -p models
    curl -o models/RobotExpressive.glb https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/RobotExpressive/RobotExpressive.glb   # CC0
    curl -o models/CesiumMan.glb https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/main/2.0/CesiumMan/glTF-Binary/CesiumMan.glb      # CC BY 4.0
    python3 -m http.server 8765 &   # ES modules need http, not file://
    node drive.mjs http://localhost:8765/index.html .     # stills, ms/frame, determinism
    node grip.mjs  http://localhost:8765/index.html .     # six consecutive frames of the held prop

Measured on this container (4 CPUs, no GPU): SwiftShader WebGL; 168 ms per 1080p frame including shadows,
outlines and PNG readback; identical pixels for the same time from different seek histories.
The assets are test models (a robot and a Khronos sample figure with a placeholder texture). They prove the
mechanics, not the look. `evidence/spike_frames.png`: top row wide / medium / close-up; below, six consecutive
frames of the folder held by the hand bone during a walk cycle.

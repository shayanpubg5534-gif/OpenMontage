// Character lab (M4.2): single-file bundle entry for HyperFrames compositions (esbuild → el3d.js; no import map,
// so render.py's literal-path dependency scan and isolated chunk workspaces see one file).
export { loadShot, QUALITY } from './runtime.js';

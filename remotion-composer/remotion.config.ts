import { Config } from "@remotion/cli/config";

// Sandboxed/offline machines (e.g. cloud containers) often cannot reach
// remotion.media to download Chrome Headless Shell. Set
// REMOTION_BROWSER_EXECUTABLE to a preinstalled headless Chrome/Chromium
// binary to use it for every `npx remotion render` / `still` call.
const browserExecutable = process.env.REMOTION_BROWSER_EXECUTABLE;
if (browserExecutable) {
  Config.setBrowserExecutable(browserExecutable);
}

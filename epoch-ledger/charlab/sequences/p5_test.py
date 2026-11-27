"""P5 end-to-end test (9.96 s): "Profit is not cash", P4 look, Balanced profile, rendered through the continuous-session
architecture (hf_sequence.py --prerender: shot_render.mjs → cached mp4 → HyperFrames video layer under captions/labels).
Beats: n1 wide slow push "A baker brought his bank an odd problem." · his own line, locked-off medium close-up, lip-synced
"We sell more bread than ever. So where does the money go?" · n3 slow pull-back from a new angle "Profit is not cash."
Snow is used only to validate rendering (technical test character, not a cast member).
Credit: Snow Rig (CC) Blender Foundation | studio.blender.org
"""
from kit.assemble import Scene

TITLE = "The Epoch Ledger · P5 continuous-session test · Profit is not cash"
EPISODE = "projects/charlab_p5/story"
NARRATION_WAV = "projects/charlab_p5/hf/narration.wav"
DURATION = 9.96
SHOTS = [{"id": "bank", "demo": "epoch-ledger/charlab/motion/demos/p5_test.json", "start": 0.0, "quality": "cin_balanced"}]
CSS = """
.p3tag{position:absolute;left:56px;top:48px;padding:9px 16px;border-radius:6px;background:rgba(14,14,16,.62);font:600 20px Inter,sans-serif;letter-spacing:2px;text-transform:uppercase;color:#f6eedf}
.p3credit{position:absolute;left:56px;top:96px;padding:6px 12px;border-radius:5px;background:rgba(14,14,16,.55);font:500 17px Inter,sans-serif;color:#efe6d6}
"""


def scenes(T):
    js = ("tl.fromTo('#p3tag',{opacity:0},{opacity:1,duration:.6,immediateRender:false},.3);"
          "tl.to('#p3tag',{opacity:0,duration:.6},2.6);")
    return [Scene("tag", 0.0, 3.4, '<div id="p3tag" class="p3tag">Illustrative reconstruction</div>'
                  '<div class="p3credit">Snow Rig (CC) Blender Foundation | studio.blender.org</div>', js=js)]

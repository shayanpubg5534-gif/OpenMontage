"""P3 cinematic test (13.7 s): "Profit is not cash". Narration-driven; one continuous 3D performance with cuts.

Beats (times from the episode's timeline.json):
  n1  wide, slow push over the banker's chair   "A baker brought his bank an odd problem."     → listening, then concern
  n2  medium                                     "His shop made a profit. But the cash kept running out."
                                                 → a palm-up explanation on "profit", uncertainty on "running out"
  dlg close-up (lip sync, Standard preset)       "We sell more bread than ever. So where does the money go?"
  n3  slow pull-back, alone at the desk          "Profit is not cash."                          → thoughtful
Snow (Blender Studio, CC-BY) is a technical test character only, not a cast member; the scene is labelled as an
illustrative reconstruction. Credit: Snow Rig (CC) Blender Foundation | studio.blender.org
"""
from kit.assemble import Scene

TITLE = "The Epoch Ledger · P3 cinematic test · Profit is not cash"
EPISODE = "projects/charlab_p3/story"
NARRATION_WAV = "projects/charlab_p3/hf/narration.wav"
DURATION = 13.71
SHOTS = [
    # windows split at the cuts: each is its own cached chunk; Standard for the lip-sync close-up
    {"id": "bank", "demo": "epoch-ledger/charlab/motion/demos/p3_cinematic_test.json", "start": 0.0,
     "windows": [{"to": 3.0, "quality": "balanced"}, {"to": 6.9, "quality": "balanced"},
                 {"to": 10.6, "quality": "standard"}, {"to": 13.71, "quality": "balanced"}]},
]
CSS = """
.p3tag{position:absolute;left:64px;top:52px;font:600 19px Inter,sans-serif;letter-spacing:2px;text-transform:uppercase;color:rgba(255,246,230,.82);text-shadow:0 1px 6px rgba(0,0,0,.45)}
.p3credit{position:absolute;right:56px;top:54px;font:500 15px Inter,sans-serif;color:rgba(255,246,230,.6);text-shadow:0 1px 6px rgba(0,0,0,.45)}
"""


def scenes(T):
    js = ("tl.fromTo('#p3tag',{opacity:0},{opacity:1,duration:.6,immediateRender:false},.3);"
          "tl.to('#p3tag',{opacity:0,duration:.6},2.6);")
    return [Scene("tag", 0.0, 3.4, '<div id="p3tag" class="p3tag">Illustrative reconstruction</div>'
                  '<div class="p3credit">Snow Rig (CC) Blender Foundation | studio.blender.org</div>', js=js)]

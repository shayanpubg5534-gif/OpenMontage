"""P4 benchmark (3 s of the P3 shot, cin_balanced, through render.py; a measurement, not a deliverable).
Derived from the P4 cinematic test (prepared, NOT rendered before approval): the P3 story with the P4 look (cinematicVariant p4, face key,
window rim, 3D street) and a readable reconstruction label and credit. Same narration, timing and performance as P3.

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

TITLE = "P4 benchmark"
EPISODE = "projects/charlab_p3/story"
NARRATION_WAV = "projects/charlab_p3/hf/narration.wav"
DURATION = 3.0
SHOTS = [{"id": "bank", "demo": "epoch-ledger/charlab/motion/demos/p3_cinematic_test.json", "start": 0.0, "quality": "cin_balanced",
           "windows": [{"to": 1.5, "quality": "cin_balanced"}, {"to": 3.0, "quality": "cin_balanced"}]}]
CSS = """
.p3tag{position:absolute;left:56px;top:48px;padding:9px 16px;border-radius:6px;background:rgba(14,14,16,.62);font:600 20px Inter,sans-serif;letter-spacing:2px;text-transform:uppercase;color:#f6eedf}
.p3credit{position:absolute;left:56px;top:96px;padding:6px 12px;border-radius:5px;background:rgba(14,14,16,.55);font:500 17px Inter,sans-serif;color:#efe6d6}
"""


def scenes(T):
    js = ("tl.fromTo('#p3tag',{opacity:0},{opacity:1,duration:.6,immediateRender:false},.3);"
          "tl.to('#p3tag',{opacity:0,duration:.6},2.6);")
    return [Scene("tag", 0.0, 3.4, '<div id="p3tag" class="p3tag">Illustrative reconstruction</div>'
                  '<div class="p3credit">Snow Rig (CC) Blender Foundation | studio.blender.org</div>', js=js)]

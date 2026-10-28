"""Writes caps.js (caption chunks with timing and speaker) for editado.html,
reusing the proof-read lines and chunking from legendar.py.

Usage: python3 make_caps.py transcript.json
"""
import json
import sys

import legendar
from legendar import build_ass

# longer two-line phrases, like the reference style
legendar.MAX_WORDS, legendar.MAX_CHARS = 7, 30

_, events = build_ass(json.load(open(sys.argv[1])))
caps = [{"s": round(s, 3), "e": round(e, 3), "q": who == "Q", "t": txt} for s, e, who, txt in events]
with open("caps.js", "w") as f:
    f.write("const CAPS = " + json.dumps(caps, ensure_ascii=False) + ";\n")
print(len(caps), "caption chunks -> caps.js")

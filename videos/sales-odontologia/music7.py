"""Soundtrack for reel7.html (carrossel aparelho): 110 BPM bouncy pop with a swipe
whoosh and pop on every slide change.

Usage: python3 music7.py [out.wav]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from synth import *  # noqa: E402,F403

T = Track(40 * 60 / 110 + 0.8, 110)
CH = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]  # C G Am F
RT = [48, 43, 45, 41]
START = [0, 5, 11, 17, 23, 29]
MEL = [76, 79, 81, 79, 76, 74, 72, 74]


def groove(a, z, gain=1.0):
    bt = a
    while bt < z - 1e-6:
        bar = int(bt // 4)
        k = bt % 4
        if k in (0, 2):
            T.addb(kick(), bt, 0.85 * gain)
        if k in (1, 3):
            T.addb(clap(), bt, 0.45 * gain)
        T.addb(hat(), bt + 0.5, 0.25 * gain, 0.3)
        T.addb(sub(RT[bar % 4], T.at(0.8)), bt, 0.55 * gain)
        T.addb(stab([n + 12 for n in CH[bar % 4]], 0.25), bt + 0.5, 0.2 * gain)
        T.addb(pluck(MEL[int(bt) % 8], 0.4), bt, 0.18 * gain, 0.2)
        bt += 1


T.addb(impact(1.2), 0, 0.5)
T.addb(bubble(79), 0.15, 0.6)
groove(0, 40)
for s in START[1:]:
    T.addb(whoosh(0.35), s - 0.4, 0.5)
    T.addb(bubble(76 + START.index(s) * 2), s + 0.15, 0.6)
    T.addb(kick(), s, 0.6)
T.addb(sparkle(84), 29, 0.5)
T.addb(bubble(79), 30.5, 0.6)
T.addb(bubble(84), 31.5, 0.7)
T.addb(stab([60, 64, 67, 72], 0.9), 40, 0.5)
T.addb(sub(48, 0.8), 40, 0.6)

T.write(sys.argv[1] if len(sys.argv) > 1 else "music7.wav")

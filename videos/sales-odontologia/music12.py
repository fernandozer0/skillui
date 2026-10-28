"""Soundtrack for reel12.html (rotina do sorriso): 100 BPM acoustic-feel pop that
thins out for the night scene and warms back up for the CTA.

Usage: python3 music12.py [out.wav]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from synth import *  # noqa: E402,F403

T = Track(40 * 0.6 + 0.8, 100)
CH = [[60, 64, 67, 72], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]  # C G Am F
RT = [48, 43, 45, 41]
MS = [4 + 7 * i for i in range(4)]


def groove(a, z, gain=1.0, drums=True):
    bt = a
    while bt < z - 1e-6:
        bar = int(bt // 4)
        k = bt % 4
        if drums:
            if k in (0, 2):
                T.addb(kick(0.4, 1.2), bt, 0.7 * gain)
            if k in (1, 3):
                T.addb(snap(), bt, 0.4 * gain)
            T.addb(hat(), bt + 0.5, 0.2 * gain, 0.3)
        # guitar-ish strum: pluck the chord tones in quick succession
        for j, n in enumerate(CH[bar % 4]):
            T.add(pluck(n, 0.6, 3200), T.at(bt) + j * 0.018, 0.12 * gain, -0.2 + j * 0.13)
            T.add(pluck(n, 0.4, 3200), T.at(bt + 0.5) + j * 0.014, 0.07 * gain, 0.2 - j * 0.13)
        if k in (0, 2):
            T.addb(sub(RT[bar % 4], T.at(1.8)), bt, 0.45 * gain)
        bt += 1


T.addb(chime([79, 84, 88], 0.12), 0, 0.5)   # sunrise
groove(0, MS[2])
for s in MS:
    T.addb(whoosh(0.4), s - 0.2, 0.35)
    T.addb(bubble(76), s, 0.55)
groove(MS[2], MS[3], 0.6, drums=False)       # night: no drums, soft bells
for k in range(7):
    T.addb(bell(84 + (k % 3) * 3, 0.9, 3), MS[2] + k, 0.18, (-0.4, 0.4)[k % 2])
T.addb(chime([79, 84, 88], 0.12), MS[3], 0.45)
groove(MS[3], 40)
T.addb(impact(1.2), 32, 0.45)
T.addb(sparkle(84), 32, 0.5)
T.addb(bubble(79), 34, 0.6)
T.addb(bubble(84), 35, 0.7)
T.addb(ep([48, 55, 60, 64, 67], 1.3), 40, 0.5)

T.write(sys.argv[1] if len(sys.argv) > 1 else "music12.wav", reverb=0.2)

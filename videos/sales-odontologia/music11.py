"""Soundtrack for reel11.html (Você sabia?): 115 BPM bouncy comic pop with a counting
tick-up under the numbers and a "boing" when each card lands.

Usage: python3 music11.py [out.wav]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from synth import *  # noqa: E402,F403

T = Track(42 * 60 / 115 + 0.8, 115)
CH = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]
RT = [48, 45, 41, 43]
FS = [4 + 7 * i for i in range(4)]
COUNTS = [True, False, True, False]


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
        T.addb(sub(RT[bar % 4], T.at(0.4)), bt, 0.55 * gain)
        T.addb(sub(RT[bar % 4] + 7, T.at(0.4)), bt + 0.5, 0.35 * gain)  # oom-pah bass
        T.addb(pluck(CH[bar % 4][int(bt) % 3] + 12, 0.3), bt + 0.5, 0.2 * gain, 0.3)
        bt += 1


T.addb(bubble(72), 0, 0.6)
T.addb(boing(), 0.3, 0.5)
T.addb(impact(1.0), 1, 0.6)
T.addb(stab([n + 12 for n in CH[0]]), 1, 0.6)
groove(2, 32)
for s, counts in zip(FS, COUNTS):
    T.addb(whoosh(0.35), s - 0.2, 0.4)
    if counts:  # rising ticks while the number counts up
        for k in range(16):
            T.add(tick(k % 2 == 0), T.at(s) + 0.1 + k * T.at(2) / 16, 0.35 + 0.02 * k)
        T.addb(chime([84, 91], 0.06), s + 2, 0.5)
    else:
        T.addb(bubble(76), s, 0.7)
        T.addb(sparkle(84), s + 0.2, 0.4)
    T.addb(boing(), s + 1.5, 0.45)
T.addb(impact(), 32, 0.6)
groove(32, 42)
T.addb(bubble(79), 34, 0.6)
T.addb(bubble(84), 35, 0.7)
T.addb(stab([60, 64, 67, 72], 0.9), 42, 0.5)

T.write(sys.argv[1] if len(sys.argv) > 1 else "music11.wav")

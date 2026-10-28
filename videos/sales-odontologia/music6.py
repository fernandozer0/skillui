"""Soundtrack for reel6.html (implante em 3 passos): 95 BPM clean "tech explainer"
with a scanner sweep, a drill-like whir as the implant goes in and a sparkle on the crown.

Usage: python3 music6.py [out.wav]
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from synth import *  # noqa: E402,F403

T = Track(40 * 60 / 95 + 0.8, 95)
CH = [[60, 64, 67, 71], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 67]]  # Cmaj7 Am7 Fmaj7 G
RT = [48, 45, 41, 43]
SS = [5 + 8 * i for i in range(3)]


def groove(a, z, gain=1.0, drums=True):
    bt = a
    while bt < z - 1e-6:
        bar = int(bt // 4)
        k = bt % 4
        if k == 0:
            T.addb(ep(CH[bar % 4], T.at(4) + 0.3), bt, 0.45 * gain)
        if drums:
            if k == 0:
                T.addb(kick(), bt, 0.8 * gain)
                T.addb(kick(), bt + 2.5, 0.8 * gain)
            if k in (1, 3):
                T.addb(snap(), bt, 0.45 * gain)
            T.addb(hat(), bt + 0.5, 0.22 * gain, 0.3)
        T.addb(pluck(CH[bar % 4][int(bt * 2) % 4] + 12, 0.35, 3000), bt, 0.16 * gain, -0.3)
        T.addb(pluck(CH[bar % 4][int(bt * 2 + 1) % 4] + 12, 0.35, 3000), bt + 0.5, 0.12 * gain, 0.3)
        if k in (0, 2):
            T.addb(sub(RT[bar % 4], T.at(1.8)), bt, 0.5 * gain)
        bt += 1


def scanner(d):
    t = t_(d)
    f = 900 + 500 * (t / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.12 * (0.6 + 0.4 * np.sin(2 * np.pi * 12 * t)) * np.sin(np.pi * t / d)


def whir(d):
    t = t_(d)
    f = 180 + 120 * np.minimum(1, t / 0.3)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3 + filt(noise(len(t)), "bandpass", [1500, 4000]) * 0.2
    return filt(x, "lowpass", 2500) * np.minimum(1, t / 0.1) * np.clip((d - t) / 0.3, 0, 1) * 0.4


# hook: teeth draw in over a soft chord, gap "?" blinks
T.addb(ep(CH[1], T.at(5)), 0, 0.4)
T.addb(impact(1.2), 0, 0.4)
T.addb(bubble(76), 1.5, 0.5)
groove(2, 5, 0.6, drums=False)
T.addb(riser(T.at(1)), 4, 0.35)

# step 1: scanner sweep + lock-on beep
groove(SS[0], SS[1])
T.addb(scanner(T.at(3)), SS[0] + 0.5, 1.0)
T.addb(chime([88, 93], 0.08), SS[0] + 3.5, 0.5)
# step 2: implant goes in
groove(SS[1], SS[2])
T.addb(whir(T.at(2.6)), SS[1] + 0.8, 0.8)
T.addb(kick(), SS[1] + 3.4, 0.6)
T.addb(bell(84, 0.6), SS[1] + 3.8, 0.35)
# step 3: abutment click, crown drop, sparkle
groove(SS[2], 31.5)
T.addb(tick(True), SS[2] + 0.5, 0.6)
T.addb(whoosh(0.4), SS[2] + 1.2, 0.4)
T.addb(kick(), SS[2] + 2.6, 0.7)
T.addb(sparkle(88), SS[2] + 3.2, 0.6)
for s in SS:
    T.addb(whoosh(0.4), s - 0.25, 0.35)

# note + CTA
groove(29, 31.5, 0.6, drums=False)
T.addb(impact(), 31.5, 0.6)
groove(31.5, 40)
T.addb(bubble(79), 33.5, 0.6)
T.addb(bubble(84), 34.5, 0.7)
T.addb(ep([48, 55, 60, 64, 67], 1.2), 40, 0.5)

T.write(sys.argv[1] if len(sys.argv) > 1 else "music6.wav", reverb=0.2)

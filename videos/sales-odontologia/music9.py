"""Soundtrack for reel9.html (perguntas frequentes): 85 BPM lo-fi with typing under
each question and a soft chime + kick when the answer lands.

Usage: python3 music9.py [out.wav]
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from synth import *  # noqa: E402,F403

T = Track(35 * 60 / 85 + 0.8, 85)
CH = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [55, 59, 62, 65]]  # Fmaj7 Em7 Dm7 G7
RT = [41, 40, 38, 43]
QS = [3 + 6 * i for i in range(4)]
rng = np.random.default_rng(9)


def key_click():
    t = t_(0.025)
    return (filt(noise(len(t)), "bandpass", [2500, 7000]) * 0.5 + np.sin(2 * np.pi * 2200 * t) * 0.25) * np.exp(-t * 260)


def groove(a, z, gain=1.0):
    bt = a
    while bt < z - 1e-6:
        bar = int(bt // 4)
        k = bt % 4
        if k == 0:
            T.addb(ep(CH[bar % 4], T.at(4) + 0.4), bt, 0.5 * gain)
        if k == 0:
            T.addb(kick(0.4, 1.2), bt, 0.7 * gain)
            T.addb(kick(0.4, 1.2), bt + 2.5, 0.7 * gain)
        if k in (1, 3):
            T.addb(snap(), bt, 0.4 * gain)
        T.addb(hat(), bt + 0.5 + 0.06, 0.18 * gain, 0.3)  # lazy swing
        if k in (0, 2):
            T.addb(sub(RT[bar % 4], T.at(1.8)), bt, 0.5 * gain)
        bt += 1


T.addb(ep(CH[0], T.at(3)), 0, 0.45)
T.addb(bubble(76), 0, 0.5)
T.addb(chime([84, 88], 0.09), 0.6, 0.4)
groove(1, 35)
for i, s in enumerate(QS):
    T.addb(whoosh(0.4), s - 0.2, 0.4)
    n = [38, 22, 17, 33][i]  # characters typed (matches the question lengths)
    for k in range(n):
        T.add(key_click(), T.at(s + 0.5) + k * T.at(2) / n + rng.uniform(-0.01, 0.01), 0.3, rng.uniform(-0.2, 0.2))
    T.addb(chime([88, 91, 96], 0.07), s + 3, 0.55)
    T.addb(kick(), s + 3, 0.6)
T.addb(impact(1.2), 27, 0.45)
T.addb(bubble(79), 28.8, 0.6)
T.addb(bubble(84), 29.6, 0.7)
T.addb(ep([53, 57, 60, 64, 69], 1.3), 35, 0.5)

T.write(sys.argv[1] if len(sys.argv) > 1 else "music9.wav", reverb=0.22)

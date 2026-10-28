"""Soundtrack for reel10.html (Este ou aquele): 120 BPM synthwave with arcade blips
as the selector bounces and a chime when the tip lands.

Usage: python3 music10.py [out.wav]
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from synth import *  # noqa: E402,F403

T = Track(38 * 0.5 + 0.8, 120)
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
RT = [45, 41, 48, 43]
RS = [4 + 6 * i for i in range(4)]


def blip(note, d=0.09):
    t = t_(d)
    return np.sign(np.sin(2 * np.pi * hz(note) * t)) * np.exp(-t * 30) * 0.25


def saw_pad(notes, d):
    t = t_(d)
    x = sum(2 * ((t * hz(n + det)) % 1.0) - 1 for n in notes for det in (-0.1, 0.1))
    env = np.minimum(1, t / 0.2) * np.clip((d - t) / 0.3, 0, 1)
    return filt(x, "lowpass", 1600) * env / (2 * len(notes)) * 0.6


def groove(a, z, gain=1.0):
    bt = a
    while bt < z - 1e-6:
        bar = int(bt // 4)
        k = bt % 4
        T.addb(kick(), bt, 0.85 * gain)
        if k in (1, 3):
            T.addb(snap(), bt, 0.5 * gain)
        T.addb(hat(), bt + 0.5, 0.25 * gain, 0.3)
        for e in range(4):  # 16th-note arp bass
            T.addb(sub(RT[bar % 4] + (12 if e % 2 else 0), T.at(0.22)), bt + e * 0.25, 0.35 * gain)
        if k == 0:
            T.addb(saw_pad([n + 12 for n in CH[bar % 4]], T.at(4)), bt, 0.4 * gain)
        bt += 1


T.addb(impact(1.2), 0, 0.5)
for bt in (0, 1, 2):
    T.addb(kick(), bt, 1.0)
    T.addb(blip(84 + bt * 3, 0.2), bt, 0.6)
groove(2, 28)
for s in RS:
    T.addb(whoosh(0.35), s - 0.2, 0.45)
    for k in range(6):  # selector bouncing left/right
        T.addb(blip(79 if k % 2 == 0 else 84), s + k * 0.5, 0.6, -0.5 if k % 2 == 0 else 0.5)
    T.addb(chime([84, 88, 91], 0.07), s + 3, 0.6)
T.addb(impact(), 28, 0.6)
groove(28, 38)
T.addb(bubble(79), 30, 0.6)
T.addb(bubble(84), 31, 0.7)
T.addb(saw_pad([57, 60, 64, 69], 1.2), 38, 0.5)
T.addb(kick(), 38, 1.0)

T.write(sys.argv[1] if len(sys.argv) > 1 else "music10.wav")

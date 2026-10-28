"""Soundtrack for reel13.html (trailer): 80 BPM cinematic — low drone, a "braam" hit on
every title card, ticking build, riser into the title and a heroic final chord.

Usage: python3 music13.py [out.wav]
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from synth import *  # noqa: E402,F403

T = Track(31 * 0.75 + 0.8, 80)


def drone(note, d):
    t = t_(d)
    x = sum(2 * ((t * hz(note + det)) % 1.0) - 1 for det in (-0.07, 0, 0.07))
    x = filt(x, "lowpass", 400, 4)
    env = np.minimum(1, t / 1.5) * np.clip((d - t) / 1.0, 0, 1)
    return x * env * 0.35


def braam(notes, d=2.5):
    t = t_(d)
    x = sum(2 * ((t * hz(n + det)) % 1.0) - 1 for n in notes for det in (-0.12, 0.12))
    cut = 300 + 1800 * np.exp(-t * 2.5)
    out = np.zeros(len(t))
    seg = 1024
    for i in range(0, len(t), seg):  # filter sweeping closed
        out[i : i + seg] = filt(x[i : i + seg + 2048], "lowpass", float(cut[i]), 2)[:seg][: len(out[i : i + seg])]
    env = np.minimum(1, t / 0.02) * np.exp(-t * 0.9)
    return np.tanh(out * env * 0.5) * 0.9


def strings(notes, d):
    t = t_(d)
    x = sum(np.sin(2 * np.pi * hz(n) * t * (1 + 0.003 * np.sin(2 * np.pi * 5 * t))) for n in notes)
    env = np.minimum(1, t / 1.2) * np.clip((d - t) / 1.0, 0, 1)
    return x * env / len(notes) * 0.4


T.addb(drone(33, T.at(20)), 0, 1.0)
for bt in (0, 4, 9, 12, 16):
    T.addb(braam([33, 40, 45]), bt, 0.9)
    T.addb(impact(2.0), bt, 0.5)
T.addb(strings([57, 60, 64], T.at(8)), 4, 0.6)
T.addb(strings([53, 57, 60], T.at(4)), 12, 0.6)
for k in range(8):  # ticking clock build before "apresenta"
    T.addb(tick(k % 2 == 0), 8 + k * 0.5, 0.4)
for k in range(8):
    T.addb(tick(k % 2 == 0), 16 + k * 0.5, 0.35 + 0.04 * k)
T.addb(riser(T.at(3.5)), 16.5, 0.6)
# title: big hit + heroic chord
T.addb(braam([33, 45, 52, 57], 4.0), 20, 1.0)
T.addb(impact(2.2), 20, 0.8)
T.addb(strings([57, 61, 64, 69], T.at(6)), 20, 0.8)
T.addb(sparkle(88), 20.3, 0.4)
# CTA: warm major chord + soft pulse
T.addb(strings([53, 57, 60, 65], T.at(5)), 26, 0.7)
for k in range(5):
    T.addb(kick(0.5, 1.2), 26 + k, 0.5)
T.addb(bubble(84), 27.5, 0.5)
T.addb(braam([33, 45, 52], 2.5), 31, 0.6)

T.write(sys.argv[1] if len(sys.argv) > 1 else "music13.wav", reverb=0.35, drive=1.2)

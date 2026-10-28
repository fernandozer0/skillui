"""Soundtrack for reel8.html (erros na escovação): 125 BPM punchy pop; each mistake gets
a buzzer and minor stab, each fix a bright chime as the groove lifts.

Usage: python3 music8.py [out.wav]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from synth import *  # noqa: E402,F403

T = Track(42 * 0.48 + 0.8, 125)
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
RT = [45, 41, 48, 43]
ES = [5 + 7 * i for i in range(4)]


def groove(a, z, gain=1.0, half=False):
    bt = a
    while bt < z - 1e-6:
        bar = int(bt // 4)
        k = bt % 4
        if (k in (0, 2)) or (not half and k in (1, 3)):
            T.addb(kick(), bt, 0.85 * gain)
        if k in (1, 3):
            T.addb(clap(), bt, 0.5 * gain)
        T.addb(hat(), bt + 0.5, 0.28 * gain, 0.3)
        T.addb(sub(RT[bar % 4], T.at(0.45)), bt + 0.5, 0.55 * gain)
        bt += 1


# hook
T.addb(bell(76, 0.6), 0, 0.4)
T.addb(kick(), 1, 1.0)
T.addb(stab([n + 12 for n in CH[0]]), 1, 0.5)
T.addb(impact(1.2), 2, 0.6)
T.addb(buzzer(0.5), 2, 0.5)
groove(3, 5, 0.7)

for s in ES:
    T.addb(whoosh(0.35), s - 0.2, 0.4)
    T.addb(bubble(72), s, 0.5)
    T.addb(buzzer(0.35), s + 0.6, 0.5)
    groove(s, s + 3.5, 0.75, half=True)
    T.addb(stab([n + 12 for n in CH[0]], 0.5), s + 1, 0.35)
    # fix
    T.addb(chime([84, 88, 91], 0.07), s + 3.5, 0.8)
    T.addb(impact(0.8), s + 3.5, 0.3)
    groove(s + 3.5, s + 7)
    T.addb(stab([n + 12 for n in CH[2]], 0.4), s + 3.5, 0.35)

T.addb(impact(), 33, 0.6)
T.addb(sparkle(84), 33, 0.6)
groove(33, 42)
T.addb(bubble(79), 35, 0.6)
T.addb(bubble(84), 36, 0.7)
T.addb(stab([57, 60, 64, 69], 0.9), 42, 0.5)
T.addb(sub(45, 0.8), 42, 0.6)

T.write(sys.argv[1] if len(sys.argv) > 1 else "music8.wav")

"""Soundtrack for reel4.html (Mito ou Verdade): 120 BPM game-show pop.
Drums drop out under each 3-2-1 countdown (ticks only) and slam back on the reveal.

Usage: python3 music4.py [out.wav]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from synth import *  # noqa: E402,F403

T = Track(48 * 0.5 + 0.8, 120)
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
RT = [45, 41, 48, 43]
ANSWERS = [False, False, True, False]  # mirrors Q in reel4.html
QS = [4 + 8 * i for i in range(4)]


def groove(a, z, gain=1.0):
    bt = a
    while bt < z - 1e-6:
        bar = int(bt // 4)
        k = bt % 4
        if k in (0, 2):
            T.addb(kick(), bt, 0.9 * gain)
        if k in (1, 3):
            T.addb(clap(), bt, 0.5 * gain)
        T.addb(hat(), bt + 0.5, 0.3 * gain, 0.3)
        T.addb(sub(RT[bar % 4], T.at(0.9)), bt, 0.55 * gain)
        T.addb(pluck(CH[bar % 4][int(bt * 2) % 3] + 12, 0.3), bt, 0.22 * gain, -0.3)
        T.addb(pluck(CH[bar % 4][int(bt * 2 + 1) % 3] + 24, 0.25), bt + 0.5, 0.15 * gain, 0.3)
        bt += 1


# intro: MITO hit, VERDADE hit, OU + thinking boing
T.addb(impact(), 0, 0.6)
T.addb(stab([n + 12 for n in CH[0]]), 0, 0.6)
T.addb(kick(), 0, 1.0)
T.addb(stab([n + 12 for n in CH[2]]), 1, 0.6)
T.addb(kick(), 1, 1.0)
T.addb(bubble(76), 2, 0.7)
T.addb(boing(), 2.3, 0.6)
groove(2, 4, 0.7)
T.addb(whoosh(0.5), 3.4, 0.4)

for s, ans in zip(QS, ANSWERS):
    T.addb(whoosh(0.4), s - 0.2, 0.45)
    T.addb(kick(), s, 0.8)
    groove(s, s + 1, 0.8)
    # countdown: ticks + rising tension pad, no drums
    for k in range(3):
        T.addb(tick(True), s + 1 + k, 1.4)
        T.addb(tick(False), s + 1.5 + k, 0.9)
        T.addb(pluck(76 + k * 2, 0.5), s + 1 + k, 0.4)
    T.addb(sub(RT[0], T.at(3), decay=0.3), s + 1, 0.45)  # tension drone
    T.addb(riser(T.at(1)), s + 3, 0.35)
    # reveal
    if ans:
        T.addb(chime([84, 88, 91, 96], 0.07), s + 4, 0.9)
    else:
        T.addb(buzzer(), s + 4, 0.7)
        T.addb(bell(72, 0.8), s + 4.05, 0.3)
    T.addb(impact(1.0), s + 4, 0.4)
    groove(s + 4, s + 8)

# CTA
T.addb(impact(), 36, 0.7)
T.addb(sparkle(84), 36, 0.6)
groove(36, 48)
T.addb(bubble(79), 39, 0.6)
T.addb(bubble(84), 40, 0.7)
T.addb(kick(), 48, 1.0)
T.addb(stab([57, 60, 64, 69], 0.9), 48, 0.5)
T.addb(sub(45, 0.8), 48, 0.6)

T.write(sys.argv[1] if len(sys.argv) > 1 else "music4.wav")

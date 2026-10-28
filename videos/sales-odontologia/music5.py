"""Soundtrack for reel5.html (5 sinais): 128 BPM energetic pop with a siren hook,
slot-roll ticks on every new number and an alarm-clock hit on "Não espere doer".

Usage: python3 music5.py [out.wav]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from synth import *  # noqa: E402,F403

T = Track(50 * 60 / 128 + 0.8, 128)
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
RT = [45, 41, 48, 43]
SS = [6 + 6 * i for i in range(5)]


def groove(a, z, gain=1.0, toms=False):
    bt = a
    while bt < z - 1e-6:
        bar = int(bt // 4)
        k = bt % 4
        T.addb(kick(), bt, 0.9 * gain)                      # four on the floor
        if k in (1, 3):
            T.addb(clap(), bt, 0.5 * gain)
        T.addb(hat(), bt + 0.5, 0.32 * gain, 0.3)
        T.addb(hat(0.03), bt + 0.25, 0.12 * gain, -0.3)
        T.addb(hat(0.03), bt + 0.75, 0.12 * gain, -0.3)
        T.addb(sub(RT[bar % 4], T.at(0.45)), bt + 0.5, 0.6 * gain)  # off-beat bass
        T.addb(stab([n + 12 for n in CH[bar % 4]], 0.22), bt + 0.5, 0.18 * gain)
        bt += 1


# hook: siren + a hit per line
T.add(siren(T.at(3.8)), 0, 0.5)
for bt in (0, 1, 2, 3):
    T.addb(kick(), bt, 1.0)
    T.addb(stab([n + 12 for n in CH[bt % 4]], 0.4), bt, 0.5)
T.addb(impact(1.2), 3, 0.5)
T.addb(riser(T.at(2)), 4, 0.5)

# signs
for i, s in enumerate(SS):
    T.addb(impact(1.0), s, 0.55)
    for k in range(6):  # slot-roll ticks as the number spins in
        T.addb(tick(k % 2 == 0), s + k * 0.08, 0.35)
    T.addb(bubble(72 + i * 2), s + 0.4, 0.6)   # emoji pop
    T.addb(whoosh(0.35), s - 0.15, 0.35)
    groove(s, s + 6)

# recap: drop the drums, clock tick-tock, alarm hit on "Não espere doer"
T.addb(impact(), 36, 0.6)
for k in range(4):
    T.addb(tick(True), 36 + k, 0.6)
    T.addb(tick(False), 36.5 + k, 0.4)
T.addb(sub(41, T.at(2)), 36, 0.5)
for k in range(10):  # alarm-clock ring
    T.addb(bell(96 if k % 2 == 0 else 93, 0.2, 18), 38 + k * 0.12, 0.35)
T.addb(kick(), 38, 1.0)
T.addb(riser(T.at(1.5)), 38.5, 0.5)

# CTA
T.addb(impact(), 40, 0.7)
T.addb(sparkle(84), 40, 0.5)
groove(40, 50)
T.addb(bubble(79), 42, 0.6)
T.addb(bubble(84), 43, 0.7)
T.addb(kick(), 50, 1.0)
T.addb(stab([57, 60, 64, 69], 0.9), 50, 0.5)
T.addb(sub(45, 0.8), 50, 0.6)

T.write(sys.argv[1] if len(sys.argv) > 1 else "music5.wav")

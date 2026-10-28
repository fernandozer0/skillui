"""Background bed + sound effects for editado.html, written as two stems so the
voice-over mix can set their levels independently.

Usage: python3 editado_audio.py   (writes trilha.wav and sfx.wav)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from synth import *  # noqa: E402,F403

DUR = 50.233 + 2.6
QS = [4.17, 14.6, 22.0, 33.97, 43.8]                       # question starts (blur)
STAMPS = [(6.94, False), (16.5, False), (25.28, True), (35.42, False)]
CARDS = [7.75, 10.9, 17.1, 19.9, 26.0, 36.1, 37.8, 39.9, 47.3]

# --- lo-fi bed, 90 BPM, kept simple so it sits under speech ---
bed = Track(DUR, 90)
CH = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [55, 59, 62, 65]]
RT = [41, 40, 38, 43]
bt = 0
while bed.at(bt) < DUR - 1:
    bar, k = int(bt // 4), bt % 4
    if k == 0:
        bed.addb(ep(CH[bar % 4], bed.at(4) + 0.4), bt, 0.5)
        bed.addb(kick(0.4, 1.1), bt, 0.5)
        bed.addb(kick(0.4, 1.1), bt + 2.5, 0.4)
    if k in (1, 3):
        bed.addb(snap(), bt, 0.3)
    bed.addb(hat(), bt + 0.56, 0.12, 0.3)
    if k in (0, 2):
        bed.addb(sub(RT[bar % 4], bed.at(1.8)), bt, 0.4)
    bt += 1
bed.add(ep([53, 57, 60, 65, 69], 2.4), 50.3, 0.6)          # end-card resolve
bed.write("trilha.wav", reverb=0.2)

# --- sound effects ---
fx = Track(DUR, 90)
fx.add(impact(1.2), 0.05, 0.6)
fx.add(whoosh(0.4), 0.4, 0.4)
for q in QS:
    fx.add(whoosh(0.35), q - 0.15, 0.5)
    fx.add(bubble(79), q + 0.2, 0.5)
for s, ok in STAMPS:
    fx.add(impact(0.9), s, 0.5)
    if ok:
        fx.add(chime([84, 88, 91, 96], 0.07), s, 0.9)
    else:
        fx.add(buzzer(0.4), s, 0.6)
for c in CARDS:
    fx.add(whoosh(0.3), c - 0.12, 0.3)
    fx.add(bubble(76), c + 0.1, 0.45)
fx.add(chime([84, 88], 0.08), 13.4, 0.5)                   # implants click in
fx.add(sparkle(88), 30.5, 0.5)                             # bone graft
fx.add(sparkle(84), 50.3, 0.6)                             # end card
fx.write("sfx.wav", reverb=0.12, drive=1.1)

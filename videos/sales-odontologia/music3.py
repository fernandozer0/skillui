"""Soundtrack for reel3.html: warm chill-pop at 100 BPM with phone-UI sound design
(original synthesized chimes, typing, check pops, bubble pops) synced to the edit.

Usage: python3 music3.py [out.wav]
"""
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
B = 0.6
DUR = 38 * B + 0.8
N = int(SR * DUR)
rng = np.random.default_rng(8)
L = np.zeros(N)
R = np.zeros(N)


def t_(d):
    return np.arange(int(SR * d)) / SR


def at(beat):
    return beat * B


def add(sig, sec, gain=1.0, pan=0.0):
    i = int(sec * SR)
    if i >= N or i < 0:
        return
    sig = sig[: N - i] * gain
    L[i : i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    R[i : i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, kind, fs=SR, output="sos"), x)


def hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ---------------- instruments ----------------
def kick(d=0.45):
    t = t_(d)
    ph = 2 * np.pi * np.cumsum(50 + 90 * np.exp(-t * 26)) / SR
    return np.tanh(np.sin(ph) * np.exp(-t * 7) * 1.5)


def snap():
    t = t_(0.18)
    n = filt(rng.standard_normal(len(t)), "bandpass", [1500, 6000])
    return n * (np.exp(-t * 60) + 0.3 * np.exp(-t * 18)) * 0.7


def hat(d=0.05):
    t = t_(d)
    return filt(rng.standard_normal(len(t)), "highpass", 8000) * np.exp(-t * 80) * 0.4


def ep(notes, d):
    """Electric-piano-ish chord: sine + soft 2nd/3rd partials, tremolo, decay."""
    t = t_(d)
    x = np.zeros(len(t))
    for n in notes:
        f = hz(n)
        x += np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t * 4) + 0.12 * np.sin(6 * np.pi * f * t) * np.exp(-t * 8)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 5 * t)
    env = np.minimum(1, t / 0.01) * np.exp(-t * 1.1) * np.clip((d - t) / 0.15, 0, 1)
    return x * trem * env / len(notes) * 0.7


def sub(note, d):
    t = t_(d)
    env = np.minimum(1, t / 0.01) * np.clip((d - t) / 0.06, 0, 1) * np.exp(-t * 1.5)
    return np.sin(2 * np.pi * hz(note) * t) * env * 0.6


def chime(notes=(88, 93), gap=0.11):
    """Original two-note notification chime (bell partials)."""
    out = np.zeros(int(SR * 1.2))
    for k, n in enumerate(notes):
        t = t_(1.2 - k * gap)
        f = hz(n)
        x = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)) * np.exp(-t * 4.5)
        i = int(k * gap * SR)
        out[i : i + len(x)] += x
    return out * 0.4


def key_click():
    t = t_(0.025)
    return (filt(rng.standard_normal(len(t)), "bandpass", [2500, 7000]) * 0.5 + np.sin(2 * np.pi * 2200 * t) * 0.25) * np.exp(-t * 260)


def bubble(note):
    t = t_(0.16)
    f = hz(note) * (0.6 + 0.5 * np.minimum(1, t / 0.05))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 26) * 0.6


def check_pop(note):
    c = chime((note + 12,), 0) * 0.25
    c[: int(SR * 0.16)] += bubble(note) * 1.1
    return c


def whoosh(d=0.45, up=True):
    t = t_(d)
    n = rng.standard_normal(len(t))
    lo, hi = filt(n, "bandpass", [300, 1500]), filt(n, "bandpass", [2500, 9000])
    m = (t / d) ** 1.4 if up else 1 - (t / d) ** 1.4
    return (lo * (1 - m) + hi * m) * np.sin(np.pi * t / d) ** 2 * 0.8


def boing():
    t = t_(0.5)
    f = 220 + 160 * np.sin(2 * np.pi * 7 * t) * np.exp(-t * 5)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * 0.5


def soft_impact():
    t = t_(1.4)
    boom = np.sin(2 * np.pi * np.cumsum(40 + 50 * np.exp(-t * 9)) / SR) * np.exp(-t * 3)
    air = filt(rng.standard_normal(len(t)), "highpass", 4000) * np.exp(-t * 4) * 0.2
    return np.tanh(boom * 1.6) * 0.8 + air


def sparkle(base=84):
    out = np.zeros(int(SR * 1.4))
    for k, n in enumerate([0, 4, 7, 12, 16]):
        c = chime((base + n,), 0)
        i = int(k * 0.06 * SR)
        out[i : i + len(c)] += c[: len(out) - i]
    return out * 0.6


# ---------------- arrangement ----------------
# Fmaj7 – G6 – Em7 – Am7, one bar (4 beats) each
CHORDS = [[53, 57, 60, 64], [55, 59, 62, 64], [52, 55, 59, 62], [57, 60, 64, 67]]
ROOTS = [41, 43, 40, 45]


def groove(from_beat, to_beat, drums=True, gain=1.0):
    bt = from_beat
    while bt < to_beat - 1e-6:
        bar = int(bt // 4)
        beat_in_bar = bt % 4
        if beat_in_bar == 0:
            add(ep(CHORDS[bar % 4], at(4) + 0.3), at(bt), 0.5 * gain)
        if drums:
            if beat_in_bar in (0, 2):
                add(kick(), at(bt), 0.85 * gain)
            if beat_in_bar in (1, 3):
                add(snap(), at(bt), 0.55 * gain)
            if beat_in_bar == 2:
                add(kick(), at(bt + 0.75), 0.5 * gain)
            for h in (0, 0.5):
                swing = 0.06 if h else 0
                add(hat(), at(bt + h) + swing * B, (0.25 if h else 0.15) * gain, 0.3)
        if beat_in_bar in (0, 2.5):
            add(sub(ROOTS[bar % 4], at(1.4)), at(bt), 0.7 * gain)
        bt += 0.5


# S1 lock screen: soft pad, notification chimes, hook hit
add(ep(CHORDS[0], at(3)), 0, 0.35)
add(chime(), at(0), 0.8)
add(chime((86, 91)), at(1), 0.8)
add(soft_impact(), at(3), 0.8)
add(boing(), at(3.6), 0.6)
add(whoosh(at(0.7)), at(5.3), 0.5)

# S2 Notes: groove in, typing per item, check pops, sparkle
groove(6, 15.5)
for bt in (7, 8, 9, 10.5):
    for i in range(8):
        add(key_click(), at(bt) - 0.25 + i * 0.035, 0.3, rng.uniform(-0.2, 0.2))
for bt, n in ((12, 79), (13, 81), (13.6, 84), (14.2, 86)):
    add(check_pop(n), at(bt), 0.7)
add(sparkle(88), at(14.5), 0.5)
add(whoosh(0.5), at(15.4), 0.4)

# S3 home screen: bubble pops per icon (rising pentatonic)
groove(16, 23.5)
PENTA = [72, 74, 76, 79, 81, 84, 86, 88]
for i, n in enumerate(PENTA):
    add(bubble(n), at(16.5) + i * at(0.35), 0.6, (-0.3, 0.3)[i % 2])
add(check_pop(84), at(20.5), 0.5)
add(whoosh(at(0.8)), at(23.2), 0.55)

# S4 spotlight: drums out, typing, result chime, tap
groove(24, 29.5, drums=False, gain=0.8)
for i in range(20):
    add(key_click(), at(24.5) + i * at(2) / 20 + rng.uniform(-0.008, 0.008), 0.35, rng.uniform(-0.2, 0.2))
add(chime((84, 88)), at(27), 0.5)
add(key_click() * 2, at(29.3), 0.6)
add(whoosh(0.4), at(29.6), 0.4)

# S5 CTA: calendar chime, full groove, hits, sparkles under the emoji rain
add(chime((88, 93, 96), 0.1), at(30), 0.8)
groove(30, 38)
add(soft_impact(), at(31.5), 0.6)
add(check_pop(84), at(32.5), 0.6)
for k in range(5):
    add(sparkle(84 + (k % 3) * 2), at(33 + k), 0.25, (-0.5, 0.5)[k % 2])
add(ep([57, 60, 64, 67, 72], 1.2), at(38), 0.5)
add(sub(45, 1.0), at(38), 0.6)

# ---------------- mix ----------------
tt = np.arange(N) / SR
ir_t = t_(1.4)
ir = filt(rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 3.5), "lowpass", 5500)
ir /= np.sqrt(np.sum(ir**2))
L = L + 0.2 * fftconvolve(L, ir)[:N]
R = R + 0.2 * fftconvolve(R, np.roll(ir, 113))[:N]
fade = np.clip((DUR - tt) / 0.6, 0, 1)
mix = np.stack([L * fade, R * fade], axis=1)
mix = filt(mix.T, "highpass", 30).T
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.3)
mix = mix / np.max(np.abs(mix)) * 0.93

out = sys.argv[1] if len(sys.argv) > 1 else "music3.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("wrote", out, f"{DUR:.2f}s")

"""Soundtrack for reel2.html: Brazilian-funk-flavoured beat at 130 BPM (A minor),
with sound design synced to the edit (stamps, slider, strobe cuts, typing, send, ding).

Usage: python3 music2.py [out.wav]
"""
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
B = 60 / 130
STEP = B / 4
DUR = 48 * B + 0.7
N = int(SR * DUR)
rng = np.random.default_rng(5)
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
def kick(d=0.4):
    t = t_(d)
    ph = 2 * np.pi * np.cumsum(48 + 110 * np.exp(-t * 32)) / SR
    click = filt(rng.standard_normal(len(t)), "highpass", 2500) * np.exp(-t * 350) * 0.35
    return np.tanh((np.sin(ph) * np.exp(-t * 8) + click) * 1.8)


def b808(note, d):
    t = t_(d)
    f = hz(note) * (1 + 0.6 * np.exp(-t * 40))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = np.minimum(1, t / 0.005) * np.exp(-t * 2.2) * np.clip((d - t) / 0.03, 0, 1)
    return np.tanh(x * env * 2.2) * 0.8


def clap():
    t = t_(0.22)
    env = np.zeros(len(t))
    for k, o in enumerate([0, 0.009, 0.018, 0.027]):
        i = int(o * SR)
        env[i:] += np.exp(-t[: len(t) - i] * (110 if k < 3 else 20))
    return filt(rng.standard_normal(len(t)), "bandpass", [1000, 5000]) * env * 0.75


def tom(f0, d=0.22):
    t = t_(d)
    ph = 2 * np.pi * np.cumsum(f0 * (1 + 0.5 * np.exp(-t * 30))) / SR
    return np.sin(ph) * np.exp(-t * 14) * 0.8


def hat(d=0.045):
    t = t_(d)
    return filt(rng.standard_normal(len(t)), "highpass", 7500) * np.exp(-t * 95) * 0.5


def stab(notes, d=0.35):
    t = t_(d)
    x = sum(2 * ((t * hz(n + det)) % 1.0) - 1 for n in notes for det in (-0.08, 0.08))
    return filt(x, "lowpass", 2600, 2) * np.exp(-t * 7) / (2 * len(notes)) * 1.2


def lead(note, d):
    t = t_(d)
    f = hz(note)
    sq = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sin(2 * np.pi * 2 * f * t) * 0.3
    vib = 1
    return filt(sq, "lowpass", 3200) * np.exp(-t * 5) * np.minimum(1, t / 0.004) * 0.45 * vib


def whoosh(d=0.35):
    t = t_(d)
    n = rng.standard_normal(len(t))
    lo = filt(n, "bandpass", [300, 1500])
    hi = filt(n, "bandpass", [2500, 9000])
    m = (t / d) ** 1.4
    return (lo * (1 - m) + hi * m) * np.sin(np.pi * t / d) ** 2 * 0.9


def riser(d):
    t = t_(d)
    n = filt(rng.standard_normal(len(t)), "highpass", 1800)
    tone = np.sin(2 * np.pi * np.cumsum(300 + 1500 * (t / d) ** 2) / SR) * 0.2
    return (n * 0.5 + tone) * (t / d) ** 2


def impact():
    t = t_(1.6)
    boom = np.sin(2 * np.pi * np.cumsum(36 + 70 * np.exp(-t * 10)) / SR) * np.exp(-t * 2.6)
    crash = filt(rng.standard_normal(len(t)), "highpass", 3500) * np.exp(-t * 3.5) * 0.3
    return np.tanh(boom * 2) * 0.9 + crash


def key_click():
    t = t_(0.03)
    return (filt(rng.standard_normal(len(t)), "bandpass", [2000, 6000]) * 0.6 + np.sin(2 * np.pi * 1800 * t) * 0.3) * np.exp(-t * 220)


def pop():
    t = t_(0.12)
    return np.sin(2 * np.pi * np.cumsum(380 + 900 * t / 0.12) / SR) * np.exp(-t * 30) * 0.8


def ding():
    t = t_(0.9)
    return (np.sin(2 * np.pi * 1318.5 * t) * np.exp(-t * 6) + 0.6 * np.sin(2 * np.pi * 1760 * t) * np.exp(-(t - 0.09).clip(0) * 6) * (t > 0.09)) * 0.35


def scratch(d=0.3):
    t = t_(d)
    f = 400 + 900 * np.abs(np.sin(2 * np.pi * 5 * t))
    x = filt(rng.standard_normal(len(t)), "bandpass", [500, 3000]) * 0.4 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
    return x * np.sin(np.pi * t / d)


# ---------------- arrangement ----------------
CHORDS = [[57, 60, 64], [53, 57, 60], [55, 60, 64], [55, 59, 62]]  # Am F C G (1 bar each)
ROOTS = [33, 29, 36, 31]
MELODY = [76, 74, 72, 74, 76, 79, 76, 74, 72, 69, 72, 74, 72, 69, 67, 69]  # 8ths over 2 bars

KICKS = [0, 3, 8, 11]
CLAPS = [4, 12]
TOMS = {6: 110, 7: 165, 14: 110, 15: 165}


def funk_bar(bar_beat, toms=True, bass=True, hats=True, gain=1.0):
    bar = int(bar_beat // 4)
    root = ROOTS[bar % 4]
    s0 = at(bar_beat)
    for s in KICKS:
        add(kick(), s0 + s * STEP, 0.95 * gain)
        if bass:
            add(b808(root, STEP * 2.8), s0 + s * STEP, 0.75 * gain)
    for s in CLAPS:
        add(clap(), s0 + s * STEP, 0.6 * gain)
    if toms:
        for s, f in TOMS.items():
            add(tom(f), s0 + s * STEP, 0.35 * gain, -0.3 if f < 150 else 0.3)
    if hats:
        for s in range(0, 16, 2):
            add(hat(), s0 + s * STEP, (0.32 if s % 4 else 0.2) * gain, 0.25)


def melody(from_beat, beats, gain=0.3):
    for k in range(int(beats * 2)):
        add(lead(MELODY[k % 16], B * 0.45), at(from_beat) + k * B / 2, gain, 0.15)


# S1 hook (0-6): a stamp hit per word, then the 🤭 slash and a riser into the drop
for bt, ch in [(0, 0), (1, 0), (2, 1), (3, 3)]:
    add(kick(), at(bt), 0.9)
    add(stab([n + 12 for n in CHORDS[ch]]), at(bt), 0.55)
    add(b808(ROOTS[ch], B * 0.9), at(bt), 0.6)
add(scratch(), at(4), 0.6)
add(riser(at(1.6)), at(4.4), 0.55)

# Drop + before/after (6-16): full beat + lead hook
add(impact(), at(6), 0.9)
for bar_beat in range(6, 16, 4):
    funk_bar(bar_beat)
melody(6, 10)
add(whoosh(0.5), at(7), 0.25)        # slider moves
add(whoosh(0.5), at(11), 0.25)
add(ding(), at(12.5), 0.5)            # sparkle

# Reasons (16-28): beat + chord stabs, whoosh into each card
add(impact(), at(16), 0.5)
for bar_beat in range(16, 28, 4):
    funk_bar(bar_beat)
    add(stab([n + 12 for n in CHORDS[int(bar_beat // 4) % 4]], 0.6), at(bar_beat), 0.35)
for c in (16, 20, 24):
    add(whoosh(), at(c) - 0.22, 0.4)

# Strobe (28-36): a hit on every cut + snare roll build
for k in range(8):
    add(kick(), at(28 + k), 1.0)
    add(clap(), at(28 + k), 0.45)
    add(stab([n + 12 for n in CHORDS[k % 4]], 0.25), at(28 + k), 0.4)
    add(b808(ROOTS[k % 4], B * 0.9), at(28 + k), 0.7)
for i in range(16):  # 16th claps rising over the last 2 beats
    add(clap(), at(34) + i * STEP / 2, 0.15 + 0.4 * i / 16)
add(riser(at(2)), at(34), 0.5)

# CTA (36-48): lighter groove, typing clicks, send pop, message dings, melody returns
add(impact(), at(36), 0.8)
for bar_beat in range(36, 48, 4):
    funk_bar(bar_beat, toms=bar_beat >= 44, gain=0.85)
add(ding(), at(37), 0.45)
n_chars = 32
for i in range(n_chars):
    add(key_click(), at(38) + i * at(3) / n_chars + rng.uniform(-0.01, 0.01), 0.35, rng.uniform(-0.2, 0.2))
add(pop(), at(41.5), 0.6)
add(whoosh(0.25), at(41.4), 0.25)
add(ding(), at(43.5), 0.45)
melody(44, 4, 0.28)

# Final hit
add(kick(), at(48), 1.0)
add(impact(), at(48), 0.7)
add(stab([57, 60, 64, 69], 0.9), at(48), 0.5)
add(b808(33, 0.7), at(48), 0.7)

# ---------------- mix ----------------
tt = np.arange(N) / SR
ir_t = t_(0.9)
ir = filt(rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 6), "lowpass", 6000)
ir /= np.sqrt(np.sum(ir**2))
L = L + 0.12 * fftconvolve(L, ir)[:N]
R = R + 0.12 * fftconvolve(R, np.roll(ir, 131))[:N]
fade = np.clip((DUR - tt) / 0.5, 0, 1)
mix = np.stack([L * fade, R * fade], axis=1)
mix = filt(mix.T, "highpass", 30).T
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.5)
mix = mix / np.max(np.abs(mix)) * 0.93

out = sys.argv[1] if len(sys.argv) > 1 else "music2.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("wrote", out, f"{DUR:.2f}s")

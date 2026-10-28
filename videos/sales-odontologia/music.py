"""Synthesizes the reel soundtrack (120 BPM, A minor), synced to the cuts in reel.html.

Usage: python3 music.py [out.wav]
"""
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
DUR = 23.0
BEAT = 0.5
N = int(SR * DUR)
rng = np.random.default_rng(3)

L = np.zeros(N)
R = np.zeros(N)


def t_(d):
    return np.arange(int(SR * d)) / SR


def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i : i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    R[i : i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, kind, fs=SR, output="sos"), x)


def hz(note):  # MIDI -> Hz
    return 440.0 * 2 ** ((note - 69) / 12)


# ---------------- instruments ----------------
def kick(d=0.45):
    t = t_(d)
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 7)
    click = filt(rng.standard_normal(len(t)), "highpass", 2000) * np.exp(-t * 300) * 0.3
    return np.tanh((body + click) * 1.6)


def clap():
    t = t_(0.25)
    n = rng.standard_normal(len(t))
    env = np.zeros(len(t))
    for k, o in enumerate([0, 0.011, 0.022]):
        i = int(o * SR)
        env[i:] += np.exp(-(t[: len(t) - i]) * (90 if k < 2 else 22))
    return filt(n, "bandpass", [900, 4000]) * env * 0.8


def hat(open_=False):
    t = t_(0.18 if open_ else 0.05)
    return filt(rng.standard_normal(len(t)), "highpass", 7000) * np.exp(-t * (18 if open_ else 90)) * 0.5


def pluck(note, d=0.45):
    t = t_(d)
    f = hz(note)
    x = sum(np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * (6 + 5 * k)) for k in range(1, 8))
    return filt(x, "lowpass", 3800) * 0.5


def pad(notes, d):
    t = t_(d)
    x = np.zeros(len(t))
    for n in notes:
        for det in (-0.12, 0.0, 0.12):
            f = hz(n + det)
            x += 2 * ((t * f) % 1.0) - 1
    x = filt(x, "lowpass", 1400, 4) / (len(notes) * 3)
    a = np.minimum(1, t / 0.35)
    r = np.minimum(1, (d - t) / 0.4)
    return x * a * np.clip(r, 0, 1)


def sub(note, d):
    t = t_(d)
    x = np.sin(2 * np.pi * hz(note) * t) + 0.25 * np.sin(4 * np.pi * hz(note) * t)
    env = np.minimum(1, t / 0.01) * np.clip((d - t) / 0.05, 0, 1)
    return x * env * 0.55


def whoosh(d=0.45):
    t = t_(d)
    n = rng.standard_normal(len(t))
    out = np.zeros(len(t))
    seg = 512
    for i in range(0, len(t), seg):  # sweeping bandpass, chunked
        c = 600 + 6000 * (i / len(t)) ** 1.5
        out[i : i + seg] = filt(n[i : i + seg + 2048], "bandpass", [c * 0.6, min(c * 1.6, 18000)])[:seg][: len(out[i : i + seg])]
    env = np.sin(np.pi * np.minimum(1, t / d)) ** 2
    return out * env * 0.9


def riser(d):
    t = t_(d)
    n = filt(rng.standard_normal(len(t)), "highpass", 1500)
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / d) ** 2) / SR) * 0.25
    return (n * 0.6 + tone) * (t / d) ** 2.2


def impact():
    t = t_(2.2)
    boom = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-t * 9)) / SR) * np.exp(-t * 2.2)
    crash = filt(rng.standard_normal(len(t)), "highpass", 3000) * np.exp(-t * 3.0) * 0.35
    return np.tanh(boom * 1.8) * 0.9 + crash


# ---------------- arrangement ----------------
CHORDS = [  # (root for bass, pad voicing, arp notes) per 2-second bar
    (45, [57, 60, 64], [69, 72, 76, 72]),  # Am
    (41, [57, 60, 65], [69, 72, 77, 72]),  # F
    (48, [55, 60, 64], [67, 72, 76, 72]),  # C
    (43, [55, 59, 62], [67, 71, 74, 71]),  # G
]


def chord_at(t):
    return CHORDS[int(t // 2) % 4]


# Hook (0-3): tension — hits on each slammed word, drone, riser into the drop
for h in (0.0, 0.5, 1.0, 1.5):
    add(kick(), h, 0.8)
    add(pluck(81 if h < 1.5 else 84, 0.6), h, 0.35)
add(pad([45, 52, 57], 3.0), 0.0, 0.35)
add(riser(1.0), 2.0, 0.5)

# Drop at 3.0 and second impact at the CTA
add(impact(), 3.0, 1.0)
add(impact(), 17.5, 0.9)

# Groove sections: (start, end, full drums?)
for a, b, full in [(3.0, 15.0, True), (17.5, 22.0, True)]:
    t = a
    while t < b - 1e-6:
        beat_idx = round((t - a) / BEAT)
        add(kick(), t, 0.95)
        if t >= 5.0 or a == 17.5:
            if beat_idx % 2 == 1:
                add(clap(), t, 0.55)
            add(hat(), t + BEAT / 2, 0.35, 0.3)
            add(hat(), t + BEAT / 4, 0.15, -0.3)
            add(hat(), t + 3 * BEAT / 4, 0.15, -0.3)
        root, voicing, arp = chord_at(t)
        add(sub(root, BEAT * 0.45), t + BEAT / 2, 0.75)  # off-beat bass (pumps against kick)
        for k in range(4):  # 16th arp
            add(pluck(arp[k], 0.35), t + k * BEAT / 4, 0.17, (-0.4, 0.4)[k % 2])
        t += BEAT

# Pads across everything after the drop
for bar in range(int(3 // 2), int(22 // 2) + 1):
    s = max(3.0, bar * 2.0)
    e = min(bar * 2.0 + 2.0, 22.0)
    if e > s:
        add(pad(chord_at(s)[1], e - s + 0.4), s, 0.32)

# Breakdown (15-17.5): emotional, no drums — sparse plucks + heartbeat + riser
for k, t in enumerate(np.arange(15.0, 17.25, BEAT)):
    root, voicing, arp = chord_at(t)
    add(pluck(arp[k % 4], 0.8), t, 0.3, (-0.3, 0.3)[k % 2])
    add(kick(0.3), t, 0.35 if k % 2 == 0 else 0.22)  # soft heartbeat
add(sub(41, 2.2), 15.0, 0.5)
add(riser(1.25), 16.25, 0.55)

# Whooshes on the cuts
for w in (2.6, 4.7, 6.75, 8.25, 9.75, 11.25, 12.75, 14.75, 17.2):
    add(whoosh(), w - 0.15, 0.4, 0.0)

# Final chord ring-out
add(pad([57, 60, 64, 69], 1.0 + 0.4), 22.0, 0.4)
add(pluck(81, 1.2), 22.0, 0.35)
add(kick(), 22.0, 0.8)
add(impact(), 22.0, 0.35)

# ---------------- mix ----------------
# sidechain: duck everything except the kick by following the beat grid
duck = np.ones(N)
tt = np.arange(N) / SR
for a, b in [(3.0, 15.0), (17.5, 22.0)]:
    m = (tt >= a) & (tt < b)
    ph = ((tt[m] - a) % BEAT) / BEAT
    duck[m] = 0.55 + 0.45 * np.minimum(1, ph / 0.45)
# (applied lightly to the whole bus — kick transient survives because it's at the duck's start)
L *= 0.6 + 0.4 * duck
R *= 0.6 + 0.4 * duck

# small room reverb
ir_t = t_(1.2)
ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 4.5)
ir = filt(ir, "lowpass", 5000)
ir /= np.sqrt(np.sum(ir**2))
L = L + 0.18 * fftconvolve(L, ir)[:N]
R = R + 0.18 * fftconvolve(R, np.roll(ir, 97))[:N]

# fade-out last 0.6s, soft clip, normalize
fade = np.clip((DUR - tt) / 0.6, 0, 1)
mix = np.stack([L * fade, R * fade], axis=1)
mix = filt(mix.T, "highpass", 28).T
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.4)
mix = mix / np.max(np.abs(mix)) * 0.93

out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("wrote", out)

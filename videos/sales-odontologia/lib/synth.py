"""Shared synth + mixer for the reel soundtracks (music4.py onwards)."""
import wave

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
_rng = np.random.default_rng(1)


def t_(d):
    return np.arange(int(SR * d)) / SR


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, kind, fs=SR, output="sos"), x)


def hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def noise(n):
    return _rng.standard_normal(n)


class Track:
    def __init__(self, dur, bpm):
        self.dur, self.B = dur, 60 / bpm
        self.N = int(SR * dur)
        self.L, self.R = np.zeros(self.N), np.zeros(self.N)

    def at(self, beat):
        return beat * self.B

    def add(self, sig, sec, gain=1.0, pan=0.0):
        i = int(sec * SR)
        if i >= self.N or i < 0:
            return
        sig = sig[: self.N - i] * gain
        self.L[i : i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
        self.R[i : i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))

    def addb(self, sig, beat, gain=1.0, pan=0.0):
        self.add(sig, self.at(beat), gain, pan)

    def write(self, path, reverb=0.15, drive=1.4, fade=0.6):
        L, R, N = self.L, self.R, self.N
        ir_t = t_(1.1)
        ir = filt(noise(len(ir_t)) * np.exp(-ir_t * 4.5), "lowpass", 5500)
        ir /= np.sqrt(np.sum(ir**2))
        L = L + reverb * fftconvolve(L, ir)[:N]
        R = R + reverb * fftconvolve(R, np.roll(ir, 117))[:N]
        tt = np.arange(N) / SR
        f = np.clip((self.dur - tt) / fade, 0, 1)
        mix = np.stack([L * f, R * f], axis=1)
        mix = filt(mix.T, "highpass", 30).T
        mix = np.tanh(mix / np.max(np.abs(mix)) * drive)
        mix = mix / np.max(np.abs(mix)) * 0.93
        with wave.open(path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((mix * 32767).astype(np.int16).tobytes())
        print("wrote", path, f"{self.dur:.2f}s")


# ---------------- instruments ----------------
def kick(d=0.42, punch=1.6):
    t = t_(d)
    ph = 2 * np.pi * np.cumsum(48 + 100 * np.exp(-t * 28)) / SR
    click = filt(noise(len(t)), "highpass", 2500) * np.exp(-t * 320) * 0.3
    return np.tanh((np.sin(ph) * np.exp(-t * 7.5) + click) * punch)


def snap():
    t = t_(0.18)
    return filt(noise(len(t)), "bandpass", [1500, 6000]) * (np.exp(-t * 60) + 0.3 * np.exp(-t * 18)) * 0.7


def clap():
    t = t_(0.22)
    env = np.zeros(len(t))
    for k, o in enumerate([0, 0.009, 0.018, 0.027]):
        i = int(o * SR)
        env[i:] += np.exp(-t[: len(t) - i] * (110 if k < 3 else 20))
    return filt(noise(len(t)), "bandpass", [1000, 5000]) * env * 0.75


def hat(d=0.05):
    t = t_(d)
    return filt(noise(len(t)), "highpass", 7500) * np.exp(-t * 85) * 0.45


def sub(note, d, decay=1.5):
    t = t_(d)
    env = np.minimum(1, t / 0.01) * np.clip((d - t) / 0.05, 0, 1) * np.exp(-t * decay)
    return (np.sin(2 * np.pi * hz(note) * t) + 0.2 * np.sin(4 * np.pi * hz(note) * t)) * env * 0.6


def pluck(note, d=0.4, bright=3800):
    t = t_(d)
    f = hz(note)
    x = sum(np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * (6 + 5 * k)) for k in range(1, 7))
    return filt(x, "lowpass", bright) * 0.5


def stab(notes, d=0.35):
    t = t_(d)
    x = sum(2 * ((t * hz(n + det)) % 1.0) - 1 for n in notes for det in (-0.08, 0.08))
    return filt(x, "lowpass", 2600) * np.exp(-t * 7) / (2 * len(notes)) * 1.2


def ep(notes, d):
    t = t_(d)
    x = np.zeros(len(t))
    for n in notes:
        f = hz(n)
        x += np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t * 4)
    env = np.minimum(1, t / 0.01) * np.exp(-t * 1.1) * np.clip((d - t) / 0.15, 0, 1)
    return x * (1 + 0.1 * np.sin(2 * np.pi * 5 * t)) * env / len(notes) * 0.7


def bell(note, d=1.0, decay=4.5):
    t = t_(d)
    f = hz(note)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)) * np.exp(-t * decay) * 0.4


def chime(notes, gap=0.1, d=1.2):
    out = np.zeros(int(SR * (d + gap * len(notes))))
    for k, n in enumerate(notes):
        x = bell(n, d)
        i = int(k * gap * SR)
        out[i : i + len(x)] += x
    return out


def tick(high=True):
    t = t_(0.06)
    f = 2400 if high else 1600
    return (np.sin(2 * np.pi * f * t) * 0.6 + filt(noise(len(t)), "highpass", 3000) * 0.3) * np.exp(-t * 120)


def buzzer(d=0.45):
    t = t_(d)
    x = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (110, 116.5))
    env = np.minimum(1, t / 0.01) * np.clip((d - t) / 0.05, 0, 1)
    return filt(x, "lowpass", 1800) * env * 0.3


def bubble(note):
    t = t_(0.16)
    f = hz(note) * (0.6 + 0.5 * np.minimum(1, t / 0.05))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 26) * 0.6


def boing():
    t = t_(0.5)
    f = 220 + 160 * np.sin(2 * np.pi * 7 * t) * np.exp(-t * 5)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * 0.5


def whoosh(d=0.4):
    t = t_(d)
    n = noise(len(t))
    lo, hi = filt(n, "bandpass", [300, 1500]), filt(n, "bandpass", [2500, 9000])
    m = (t / d) ** 1.4
    return (lo * (1 - m) + hi * m) * np.sin(np.pi * t / d) ** 2 * 0.85


def riser(d):
    t = t_(d)
    n = filt(noise(len(t)), "highpass", 1800)
    tone = np.sin(2 * np.pi * np.cumsum(300 + 1400 * (t / d) ** 2) / SR) * 0.2
    return (n * 0.5 + tone) * (t / d) ** 2


def impact(d=1.6):
    t = t_(d)
    boom = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-t * 9)) / SR) * np.exp(-t * 2.6)
    crash = filt(noise(len(t)), "highpass", 3500) * np.exp(-t * 3.5) * 0.3
    return np.tanh(boom * 1.8) * 0.85 + crash


def siren(d=1.0, rate=3.0):
    t = t_(d)
    f = 700 + 300 * np.sin(2 * np.pi * rate * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return filt(x, "lowpass", 3000) * np.minimum(1, t / 0.05) * np.clip((d - t) / 0.1, 0, 1) * 0.3


def sparkle(base=84):
    out = np.zeros(int(SR * 1.4))
    for k, n in enumerate([0, 4, 7, 12, 16]):
        c = bell(base + n, 1.0)
        i = int(k * 0.06 * SR)
        out[i : i + len(c)] += c[: len(out) - i]
    return out * 0.6

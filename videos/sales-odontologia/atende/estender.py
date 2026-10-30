"""Extends the 3:4 photos to 9:16 without AI by stretching their top and bottom edges.

Near the seam the photo continues at 1:1 scale; further out the edge rows are
stretched more and more (exponential mapping), blurred progressively and given a
little grain so the extension reads as out-of-focus wall/sky and floor.

Usage: python3 estender.py fotos fotos-9x16
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

W, H = 1080, 1440
TOP, BOTTOM = 260, 220            # rows added -> 1080 x 1920
SRC_TOP, SRC_BOTTOM = 150, 40     # how many edge rows get re-stretched


def stretch_map(src_rows, out_rows):
    """Output row -> source row (0 = seam). 1:1 at the seam, compressing outward."""
    ratio = out_rows / src_rows
    k = 0.01
    while k / (1 - np.exp(-k)) < ratio:  # solve k/(1-e^-k) = ratio for f'(0) = ratio
        k += 0.01
    x = np.arange(out_rows) / out_rows
    f = (1 - np.exp(-k * x)) / (1 - np.exp(-k))
    return np.clip(f * src_rows, 0, src_rows - 1)


def sample_rows(img, rows):
    lo = np.floor(rows).astype(int)
    hi = np.minimum(lo + 1, img.shape[0] - 1)
    w = (rows - lo)[:, None, None]
    return img[lo] * (1 - w) + img[hi] * w


def soften(strip, from_seam):
    """Blend toward a blurred copy and add grain, increasing away from the seam."""
    blurred = np.asarray(Image.fromarray(strip.astype(np.uint8)).filter(ImageFilter.GaussianBlur(14)), dtype=np.float32)
    a = np.clip(from_seam / 140.0, 0, 1)[:, None, None] ** 0.8
    out = strip * (1 - a) + blurred * a
    rng = np.random.default_rng(0)
    out += rng.normal(0, 3.0, out.shape) * a
    return out


def extend(path):
    img = np.asarray(Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS), dtype=np.float32)
    # bottom: rows H-SRC_BOTTOM .. H-1 re-laid over SRC_BOTTOM+BOTTOM rows
    n = SRC_BOTTOM + BOTTOM
    rows = (H - SRC_BOTTOM) + stretch_map(SRC_BOTTOM, n)
    bot = sample_rows(img, rows)
    bot = soften(bot, np.maximum(np.arange(n) - (n - BOTTOM) * 0.35, 0))
    # top: mirror of the same idea, reading upward from row SRC_TOP
    n2 = SRC_TOP + TOP
    rows2 = (SRC_TOP - 1) - stretch_map(SRC_TOP, n2)
    top = sample_rows(img, rows2)[::-1]
    top = soften(top[::-1], np.maximum(np.arange(n2) - (n2 - TOP) * 0.35, 0))[::-1]
    mid = img[SRC_TOP:H - SRC_BOTTOM]
    return np.clip(np.concatenate([top, mid, bot]), 0, 255).astype(np.uint8)


if __name__ == "__main__":
    src, dst = sys.argv[1:3]
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(src)):
        if f.endswith(".jpg"):
            out = extend(os.path.join(src, f))
            assert out.shape[:2] == (H + TOP + BOTTOM, W), out.shape
            Image.fromarray(out).save(os.path.join(dst, f), quality=93)
            print(f, out.shape[1], "x", out.shape[0])

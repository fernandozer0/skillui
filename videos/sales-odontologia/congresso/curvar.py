"""Applies the spherical "bulge" warp of the reference reel to the flat caption:
the middle of the text block swells, the edges shrink and the lines bow
(top line arches up, bottom line sags down).

Usage: python3 curvar.py legenda_plana.png legenda.png
"""
import sys

import numpy as np
from PIL import Image

STRENGTH = 0.18     # 0 = flat; centre is magnified by 1/(1-STRENGTH)

src = np.asarray(Image.open(sys.argv[1]).convert("RGBA")).astype(np.float32)
a = src[..., 3]
ys, xs = np.nonzero(a > 8)
cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
rx, ry = (xs.max() - xs.min()) / 2 * 1.08, (ys.max() - ys.min()) / 2 * 1.2

H, W = a.shape
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
dx, dy = (xx - cx) / rx, (yy - cy) / ry
r = np.sqrt(dx * dx + dy * dy)
inside = r < 1
# smooth inverse map: centre samples a smaller source radius (magnified), rim unchanged
f = np.where(inside, 1 - STRENGTH * (1 - r * r), 1.0)
sx, sy = cx + dx * f * rx, cy + dy * f * ry


def bilinear(img, x, y):
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    x1, y1 = x0 + 1, y0 + 1
    wx, wy = (x - x0)[..., None], (y - y0)[..., None]
    c = lambda X, Y: img[np.clip(Y, 0, H - 1), np.clip(X, 0, W - 1)]
    return (c(x0, y0) * (1 - wx) * (1 - wy) + c(x1, y0) * wx * (1 - wy)
            + c(x0, y1) * (1 - wx) * wy + c(x1, y1) * wx * wy)


out = np.where(inside[..., None], bilinear(src, sx, sy), src)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(sys.argv[2])
print("warped", sys.argv[2])

"""Python twin of the scene3d.js camera (same maths), for laying out 2D overlays on 3D plates at build time.

    cam = Camera(pos=[0, 1.5, 2.6], look=[0, 1.25, -4], fov=50)
    x, y, depth = cam.project([1.0, 0.74, -2.6])
"""
from __future__ import annotations

import math


def _sub(a, b): return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def _norm(a):
    n = math.sqrt(_dot(a, a)) or 1
    return [a[0] / n, a[1] / n, a[2] / n]


class Camera:
    def __init__(self, pos, look, fov=40, shift=(0, 0), w=1920, h=1080, up=(0, 1, 0)):
        self.pos, self.w, self.h, self.shift, self.look, self.fov = list(pos), w, h, shift, list(look), fov
        self.f = _norm(_sub(look, pos)); self.r = _norm(_cross(self.f, list(up))); self.u = _cross(self.r, self.f)
        self.focal = (h / 2) / math.tan(fov * math.pi / 360)

    def js(self, *_):
        """The identical camera for scene3d.js (plates and live layers must share it)."""
        return f"S3.camera({{ pos: {self.pos}, look: {self.look}, fov: {self.fov}, shift: {list(self.shift)} }})"

    def project(self, p):
        d = _sub(p, self.pos)
        c = [_dot(d, self.r), _dot(d, self.u), _dot(d, self.f)]
        if c[2] <= .15:
            return None
        return (self.w / 2 + self.shift[0] + c[0] * self.focal / c[2], self.h / 2 + self.shift[1] - c[1] * self.focal / c[2], c[2])

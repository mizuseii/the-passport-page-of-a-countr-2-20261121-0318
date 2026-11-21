#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Pure-stdlib Python 3.13 program. Writes one image to /output/entry.png:
an open passport spread for the invented Republic of Talmarin, a small
North Atlantic island nation (capital Port Anselm) whose only arrivals
are by sea ferry. Deterministic: no network, no clock, no unseeded
randomness -- two runs produce byte-identical output.

Layout (1024x1024): left page = data page (portrait, bilingual
English/Talmarin fields, MRZ with real check digits); right page =
visa/stamp page (arrival/departure stamps from neighbouring Meridia,
Ostravell and the Kestrel Isles, all dated after the 02 JUN 2026 issue
date, plus a fee-paid visa condition that reveals the place).
"""
import math
import os
import random
import struct
import zlib

W = H = 1024
OUT = os.environ.get("MAKEFUN_OUTPUT", "/output/entry.png")

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 cells ('#' = ink). One consistent face for the
# whole document, so the typography holds together as a single document.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "00100", "01000", "01000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
}


def text_w(s, scale, spacing=None):
    if spacing is None:
        spacing = max(1, scale // 2)
    if not s:
        return 0
    return len(s) * (5 * scale + spacing) - spacing


class Img:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, c, alpha=1.0):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            if alpha >= 1.0:
                self.px[i:i + 3] = bytes(c)
            else:
                for k in range(3):
                    self.px[i + k] = int(self.px[i + k] * (1 - alpha) + c[k] * alpha)

    def get(self, x, y):
        i = (y * self.w + x) * 3
        return (self.px[i], self.px[i + 1], self.px[i + 2])

    def fill_rect(self, x0, y0, x1, y1, c, alpha=1.0):
        x0 = max(0, x0); y0 = max(0, y0)
        x1 = min(self.w, x1); y1 = min(self.h, y1)
        if alpha >= 1.0:
            row = bytes(c) * (x1 - x0)
            for y in range(y0, y1):
                i = (y * self.w + x0) * 3
                self.px[i:i + len(row)] = row
        else:
            for y in range(y0, y1):
                for x in range(x0, x1):
                    self.set(x, y, c, alpha)

    def rect(self, x0, y0, x1, y1, c, t=1):
        for k in range(t):
            self.fill_rect(x0 + k, y0 + k, x1 - k, y0 + k + 1, c)
            self.fill_rect(x0 + k, y1 - k - 1, x1 - k, y1 - k, c)
            self.fill_rect(x0 + k, y0 + k, x0 + k + 1, y1 - k, c)
            self.fill_rect(x1 - k - 1, y0 + k, x1 - k, y1 - k, c)

    def hline(self, x0, x1, y, c, t=1):
        for k in range(t):
            self.fill_rect(x0, y + k, x1, y + k + 1, c)

    def vline(self, x, y0, y1, c, t=1):
        for k in range(t):
            self.fill_rect(x + k, y0, x + k + 1, y1, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0); dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            if t == 1:
                self.set(x, y, c)
            else:
                self.fill_rect(x - t // 2, y - t // 2, x + t // 2 + 1, y + t // 2 + 1, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy; x += sx
            if e2 < dx:
                err += dx; y += sy

    def polyline(self, pts, c, t=1):
        for a, b in zip(pts, pts[1:]):
            self.line(a[0], a[1], b[0], b[1], c, t)

    def circle_fill(self, cx, cy, r, c, alpha=1.0):
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - dx, y, cx + dx + 1, y + 1, c, alpha)

    def ellipse_fill(self, cx, cy, rx, ry, c, alpha=1.0):
        for y in range(cy - ry, cy + ry + 1):
            dy = (y - cy) / ry
            dx = int(rx * math.sqrt(max(0.0, 1 - dy * dy)))
            self.fill_rect(cx - dx, y, cx + dx + 1, y + 1, c, alpha)

    def poly_fill(self, pts, c, alpha=1.0):
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                self.fill_rect(int(math.ceil(a)), y, int(math.floor(b)) + 1, y + 1, c, alpha)

    def text(self, x, y, s, scale, c, bold=False, spacing=None):
        if spacing is None:
            spacing = max(1, scale // 2)
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT["?"])
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == "1":
                        self.fill_rect(cx + col * scale, y + r * scale,
                                       cx + col * scale + scale, y + r * scale + scale, c)
                        if bold:
                            self.fill_rect(cx + col * scale + 1, y + r * scale,
                                           cx + col * scale + scale + 1, y + r * scale + scale, c)
            cx += 5 * scale + spacing
        return cx

    def text_center(self, cx, y, s, scale, c, bold=False, spacing=None):
        self.text(cx - text_w(s, scale, spacing) // 2, y, s, scale, c, bold, spacing)

    def text_right(self, x1, y, s, scale, c, bold=False, spacing=None):
        self.text(x1 - text_w(s, scale, spacing), y, s, scale, c, bold, spacing)


def star_points(cx, cy, r_out, r_in, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = rot + i * math.pi / n
        pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
    return pts


def write_png(img, path):
    raw = bytearray()
    stride = img.w * 3
    for y in range(img.h):
        raw.append(0)
        raw += img.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", img.w, img.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- MRZ
def mrz_check(s):
    total = 0
    for i, ch in enumerate(s):
        if ch.isdigit():
            v = int(ch)
        elif ch.isalpha():
            v = ord(ch) - 55
        else:
            v = 0
        total += v * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = "P<TLMVEY<<MARA<ELLISON" + "<" * (44 - len("P<TLMVEY<<MARA<ELLISON"))
    doc = "TLM0048217"
    dob, sex, exp = "940314", "F", "360601"
    body = (doc + mrz_check(doc) + "TLM" + dob + mrz_check(dob) + sex
            + exp + mrz_check(exp) + "<" * 14)
    line2 = body + mrz_check(body)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# ---------------------------------------------------------------- colours
PAPER = (246, 241, 230)
PAPER_DIM = (238, 231, 214)
INK = (38, 34, 28)
NAVY = (31, 58, 95)
NAVY_LT = (64, 96, 138)
GOLD = (176, 141, 58)
RED = (158, 42, 36)
BLUE = (36, 84, 158)
PURPLE = (96, 58, 128)
GREEN = (38, 110, 88)
GREY = (110, 104, 90)
SKIN = (220, 174, 135)
SKIN_DK = (198, 148, 108)
HAIR = (58, 42, 34)
JACKET = (47, 101, 95)
DESK = (232, 226, 212)


def coat_of_arms(img, x, y, s=1.0):
    """Talmarin arms: navy shield, gold star, three sea-waves."""
    w, h = int(64 * s), int(76 * s)
    cx = x + w // 2
    shield = [(x, y), (x + w, y), (x + w, y + int(48 * s)),
              (cx, y + h), (x, y + int(48 * s))]
    img.poly_fill(shield, NAVY)
    img.polyline(shield + [shield[0]], GOLD, 2)
    img.poly_fill(star_points(cx, y + int(26 * s), int(16 * s), int(7 * s)), GOLD)
    for k in range(3):
        yy = y + int((52 + k * 6) * s)
        pts = [(x + 8 + i * 6, yy + int(3 * math.sin(i * 0.9))) for i in range(9)]
        img.polyline(pts, (150, 190, 215), 2)


def portrait(img, x0, y0, x1, y1):
    """Stylised passport photograph of Mara Ellison Vey, 32, of Port Anselm."""
    img.fill_rect(x0, y0, x1, y1, (255, 255, 255))
    img.rect(x0, y0, x1, y1, INK, 2)
    px0, py0, px1, py1 = x0 + 5, y0 + 5, x1 - 5, y1 - 5
    # pale studio backdrop, slightly darker at the edges
    for yy in range(py0, py1):
        t = (yy - py0) / max(1, py1 - py0)
        c = tuple(int(a + (b - a) * t) for a, b in zip((178, 194, 200), (146, 166, 175)))
        img.fill_rect(px0, yy, px1, yy + 1, c)
    cx = (px0 + px1) // 2
    # shoulders / jacket
    img.poly_fill([(px0 + 6, py1), (px0 + 6, py1 - 34), (cx - 26, py1 - 52),
                   (cx + 26, py1 - 52), (px1 - 6, py1 - 34), (px1 - 6, py1)], JACKET)
    # shirt + collar
    img.poly_fill([(cx - 14, py1 - 52), (cx, py1 - 30), (cx + 14, py1 - 52)], (240, 238, 230))
    img.poly_fill([(cx - 14, py1 - 52), (cx - 4, py1 - 38), (cx, py1 - 52)], (225, 222, 212))
    img.poly_fill([(cx + 14, py1 - 52), (cx + 4, py1 - 38), (cx, py1 - 52)], (225, 222, 212))
    # neck
    img.fill_rect(cx - 11, py1 - 78, cx + 11, py1 - 50, SKIN_DK)
    img.fill_rect(cx - 11, py1 - 78, cx + 11, py1 - 68, SKIN)
    # hair mass behind the face
    img.ellipse_fill(cx, py0 + 62, 40, 52, HAIR)
    # face
    img.ellipse_fill(cx, py0 + 66, 32, 42, SKIN)
    # hair cap + side locks framing the face
    img.poly_fill([(cx - 32, py0 + 70), (cx - 30, py0 + 28), (cx - 12, py0 + 12),
                   (cx + 12, py0 + 12), (cx + 30, py0 + 28), (cx + 32, py0 + 70),
                   (cx + 24, py0 + 34), (cx - 24, py0 + 34)], HAIR)
    img.ellipse_fill(cx - 33, py0 + 78, 6, 12, HAIR)
    img.ellipse_fill(cx + 33, py0 + 78, 6, 12, HAIR)
    # ears
    img.ellipse_fill(cx - 32, py0 + 72, 4, 8, SKIN)
    img.ellipse_fill(cx + 32, py0 + 72, 4, 8, SKIN)
    # brows, eyes, nose, mouth -- plain, front-facing, passport-neutral
    img.fill_rect(cx - 20, py0 + 58, cx - 8, py0 + 61, HAIR)
    img.fill_rect(cx + 8, py0 + 58, cx + 20, py0 + 61, HAIR)
    img.ellipse_fill(cx - 14, py0 + 66, 4, 3, (40, 32, 26))
    img.ellipse_fill(cx + 14, py0 + 66, 4, 3, (40, 32, 26))
    img.line(cx, py0 + 68, cx - 2, py0 + 82, SKIN_DK, 2)
    img.line(cx - 2, py0 + 82, cx + 3, py0 + 82, SKIN_DK, 2)
    img.line(cx - 8, py0 + 94, cx + 8, py0 + 94, (150, 90, 78), 2)
    # faint studio shadow under the chin
    img.ellipse_fill(cx, py1 - 52, 22, 5, (120, 135, 140), alpha=0.5)


def make_stamp(w, h, country, kind, date, port, officer, ink, emblem, seed):
    """One ink entry/exit stamp, rendered on its own layer (magenta = clear)."""
    CLEAR = (255, 0, 255)
    st = Img(w, h, CLEAR)
    rng = random.Random(seed)
    st.rect(4, 4, w - 4, h - 4, ink, 3)
    st.rect(9, 9, w - 9, h - 9, ink, 1)
    st.text_center(w // 2, 16, country, 3 if len(country) <= 11 else 2, ink, bold=True)
    st.hline(16, w - 16, 40, ink, 1)
    st.text_center(w // 2, 46, kind, 2, ink, bold=True)
    st.text_center(w // 2, 66, date, 3, ink, bold=True)
    st.text_center(w // 2, 92, port, 2, ink)
    st.text_center(w // 2, 108, officer, 2, ink)
    if emblem == "anchor":
        st.line(w // 2, 128, w // 2, 152, ink, 2)
        st.line(w // 2 - 8, 132, w // 2 + 8, 132, ink, 2)
        st.circle_fill(w // 2, 128, 3, ink)
        st.polyline([(w // 2 - 10, 142), (w // 2, 152), (w // 2 + 10, 142)], ink, 2)
    elif emblem == "peak":
        st.polyline([(w // 2 - 14, 152), (w // 2 - 4, 132), (w // 2 + 2, 144),
                     (w // 2 + 8, 130), (w // 2 + 16, 152)], ink, 2)
        st.hline(w // 2 - 16, w // 2 + 18, 154, ink, 2)
    elif emblem == "gull":
        st.polyline([(w // 2 - 16, 146), (w // 2 - 6, 138), (w // 2, 144),
                     (w // 2 + 6, 138), (w // 2 + 16, 146)], ink, 2)
        st.polyline([(w // 2 - 10, 154), (w // 2 - 3, 149), (w // 2 + 3, 149),
                     (w // 2 + 10, 154)], ink, 2)
    # ink wear: deterministic speckles knocked out of the stamp
    for _ in range(260):
        x = rng.randrange(w); y = rng.randrange(h)
        if st.get(x, y) != CLEAR:
            st.set(x, y, CLEAR)
    return st


def blit_rotated(img, st, cx, cy, angle_deg, alpha=0.92, seed=0):
    rng = random.Random(seed)
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    hw, hh = st.w // 2, st.h // 2
    r = int(math.hypot(hw, hh)) + 2
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            sx = int(ca * dx + sa * dy) + hw
            sy = int(-sa * dx + ca * dy) + hh
            if 0 <= sx < st.w and 0 <= sy < st.h:
                c = st.get(sx, sy)
                if c != (255, 0, 255) and rng.random() > 0.05:
                    img.set(cx + dx, cy + dy, c, alpha)


def compass_rose(img, cx, cy, r):
    c = (120, 104, 70)
    img.poly_fill(star_points(cx, cy, r, r // 4, n=4), c, alpha=0.10)
    img.poly_fill(star_points(cx, cy, r * 3 // 4, r // 5, n=4, rot=0), c, alpha=0.08)
    img.circle_fill(cx, cy, r, c, alpha=0.05)
    img.circle_fill(cx, cy, r // 2, c, alpha=0.05)
    img.text_center(cx, cy - r - 16, "N", 2, c, bold=True)


def field(img, x, y, label, talmarin, value, vw=300):
    img.text(x, y, label, 2, GREY, bold=True)
    img.text(x + 170, y, talmarin, 2, (150, 142, 122))
    img.text(x, y + 16, value, 2, INK, bold=True)
    img.hline(x, x + vw, y + 34, (205, 196, 172), 1)


def build():
    img = Img(W, H, DESK)
    # deterministic paper speckle
    rng = random.Random(20261121)
    for _ in range(9000):
        x = rng.randrange(W); y = rng.randrange(H)
        img.set(x, y, (225, 218, 200), 0.35)
    # the open spread
    img.fill_rect(36, 36, 988, 988, PAPER)
    img.rect(36, 36, 988, 988, INK, 3)
    img.fill_rect(508, 36, 516, 988, (120, 110, 88))
    img.fill_rect(500, 36, 508, 988, (210, 200, 178))
    img.fill_rect(516, 36, 524, 988, (210, 200, 178))

    # ================= left page: data page =================
    # faint guilloche behind the data
    for k in range(6):
        y0 = 560 + k * 56
        pts = [(x, y0 + int(4 * math.sin((x - 48) / 26.0 + k))) for x in range(48, 500, 8)]
        img.polyline(pts, (226, 218, 196), 1)
    coat_of_arms(img, 62, 58)
    img.text(140, 66, "REPUBLIC OF TALMARIN", 3, NAVY, bold=True)
    img.text(140, 96, "PASSPORT", 4, INK, bold=True)
    img.text(140, 128, "PASPORT  .  TALMARIN", 2, GREY)
    img.hline(62, 492, 152, NAVY, 3)
    img.hline(62, 492, 157, GOLD, 1)

    portrait(img, 330, 172, 486, 362)

    rows = [
        ("TYPE", "TYPE", "P"),
        ("COUNTRY CODE", "LANDKODE", "TLM"),
        ("PASSPORT NO.", "PASSNR.", "TLM 0048217"),
        ("SURNAME", "NAVN", "VEY"),
        ("GIVEN NAMES", "FORNAVN", "MARA ELLISON"),
        ("NATIONALITY", "NASJONALITET", "TALMARIN"),
        ("DATE OF BIRTH", "FODSELSDATO", "14 MAR 1994"),
        ("PLACE OF BIRTH", "FODESTED", "PORT ANSELM, TALMARIN"),
        ("SEX", "KJONN", "F"),
    ]
    y = 172
    for label, tal, val in rows:
        field(img, 62, y, label, tal, val, vw=248)
        y += 42
    # issue block
    y = 560
    field(img, 62, y, "DATE OF ISSUE", "UTSTEDT", "02 JUN 2026", vw=248); y += 42
    field(img, 62, y, "DATE OF EXPIRY", "UTLOPER", "01 JUN 2036", vw=248); y += 42
    img.text(62, y, "AUTHORITY", 2, GREY, bold=True)
    img.text(232, y, "MYNDIGHET", 2, (150, 142, 122))
    img.text(62, y + 16, "PORT ANSELM", 2, INK, bold=True)
    img.text(62, y + 34, "PASSPORT OFFICE", 2, INK, bold=True)
    img.hline(62, 310, y + 52, (205, 196, 172), 1)
    y += 84
    img.text(62, y, "HOLDER'S SIGNATURE", 2, GREY, bold=True)
    sig = [(62 + i * 8, y + 26 + int(5 * math.sin(i * 1.3)) - (4 if i in (2, 5) else 0))
           for i in range(18)]
    img.polyline(sig, INK, 2)
    img.text(62, y + 40, "MARA E. VEY", 2, INK)
    img.hline(62, 310, y + 58, (205, 196, 172), 1)

    # MRZ with real check digits; two lines, 44 chars each
    l1, l2 = mrz_lines()
    img.hline(56, 496, 852, NAVY, 2)
    img.text(56, 862, l1, 2, INK, spacing=0)
    img.text(56, 884, l2, 2, INK, spacing=0)
    img.text(56, 916, "THIS PASSPORT IS THE PROPERTY OF THE", 2, GREY)
    img.text(56, 934, "REPUBLIC OF TALMARIN.", 2, GREY)

    # ================= right page: visas & stamps =================
    img.text(548, 66, "VISAS", 4, INK, bold=True)
    img.text(548, 96, "VISUM  .  TALMARIN", 2, GREY)
    img.text_right(962, 70, "No. TLM 0048217", 2, GREY)
    img.hline(548, 962, 122, NAVY, 3)
    img.hline(548, 962, 127, GOLD, 1)
    compass_rose(img, 755, 560, 120)

    stamps = [
        # (w, h, country, kind, date, port, officer, ink, emblem, cx, cy, angle, seed)
        (210, 160, "MERIDIA", "ARRIVAL", "18 JUL 2026", "PORT OF MERIDIA", "OFF. 214", BLUE, "anchor", 660, 230, -7, 11),
        (210, 160, "MERIDIA", "DEPARTURE", "02 AUG 2026", "PORT OF MERIDIA", "OFF. 087", RED, "anchor", 868, 220, 5, 22),
        (210, 160, "OSTRAVELL", "ARRIVAL", "19 SEP 2026", "OSTRAVELL BORDER", "OFF. 331", PURPLE, "peak", 655, 420, -4, 33),
        (210, 160, "OSTRAVELL", "DEPARTURE", "26 SEP 2026", "OSTRAVELL BORDER", "OFF. 118", PURPLE, "peak", 868, 415, 8, 44),
        (210, 160, "KESTREL ISLES", "ARRIVAL", "11 OCT 2026", "KESTREL HARBOUR", "OFF. 052", GREEN, "gull", 755, 600, -6, 55),
    ]
    for (w, h, co, kind, dt, port, off, ink, emb, cx, cy, ang, seed) in stamps:
        st = make_stamp(w, h, co, kind, dt, port, off, ink, emb, seed)
        blit_rotated(img, st, cx, cy, ang, seed=seed)

    # telling paperwork detail: the Kestrel visa vignette + fee stamp.
    # Talmarin has no airport: every arrival is by sea ferry.
    img.fill_rect(548, 712, 962, 902, (250, 246, 236))
    img.rect(548, 712, 962, 902, NAVY, 2)
    img.rect(554, 718, 956, 896, NAVY, 1)
    img.text(566, 730, "VISITOR VISA - KESTREL ISLES", 2, NAVY, bold=True)
    img.hline(566, 944, 752, NAVY, 1)
    img.text(566, 762, "VALID  11 OCT 2026 - 09 JAN 2027", 2, INK, bold=True)
    img.text(566, 784, "ONE ENTRY  .  STAY UP TO 90 DAYS", 2, INK)
    img.text(566, 806, "CONDITION: LANDING BY SEA", 2, INK, bold=True)
    img.text(566, 828, "FERRY ONLY. NO AIR ARRIVALS", 2, INK, bold=True)
    img.text(566, 850, "AT PORT ANSELM.", 2, INK, bold=True)
    # fee stamp is a small single-line stamp, drawn compactly
    fee = Img(170, 64, (255, 0, 255))
    fee.rect(3, 3, 167, 61, RED, 3)
    fee.text_center(85, 8, "FEE PAID", 3, RED, bold=True)
    fee.text_center(85, 28, "12 TMR", 3, RED, bold=True)
    fee.text_center(85, 48, "11 OCT 2026", 2, RED)
    blit_rotated(img, fee, 875, 868, -9, seed=77)

    img.text(548, 922, "HOLDER MUST CARRY THIS PASSPORT AT ALL", 2, GREY)
    img.text(548, 940, "TIMES WHILE IN TALMARIN.", 2, GREY)
    img.text_right(962, 958, "SPECIMEN 0048217", 2, GREY)
    return img


def main():
    img = build()
    n = write_png(img, OUT)
    print(f"wrote {OUT} {img.w}x{img.h} {n} bytes")


if __name__ == "__main__":
    main()

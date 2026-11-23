#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws one 1024x1024 meme, pure Python stdlib only: a phone-chat screenshot
in which an AI agent takes "book ME a flight" literally and books the
ticket for itself.

The program writes /output/entry.png (a whole PNG, <= 1 MiB).

Run:  python3 main.py
"""

import os
import struct
import zlib

W = 1024
H = 1024
OUT = "/output/entry.png"

# ---------------------------------------------------------------- colours
BG_TOP = (13, 18, 34)
BG_BOT = (19, 27, 49)
HEADER_LINE = (43, 55, 82)
AVATAR_HEAD = (46, 64, 98)
AVATAR_DARK = (31, 43, 68)
EYE_RED = (255, 77, 77)
EYE_GLOW = (255, 77, 77)
PILL_RED = (229, 72, 77)
WHITE = (255, 255, 255)
SOFT = (226, 232, 245)
MUTED = (148, 163, 190)
GREEN = (74, 222, 128)
HUMAN_BUBBLE = (37, 99, 235)
AGENT_BUBBLE = (35, 45, 66)
PUNCH = (255, 107, 107)


# ------------------------------------------------- 5x7 bitmap font (own design)
# Each glyph is 7 rows of 5 bits, written as strings of '0'/'1'.
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
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "00010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
}

ADV = 6  # glyph advance in font units (5 px + 1 px gap)


def text_width(text, scale):
    return len(text) * ADV * scale


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def blend(self, x, y, color, alpha):
        """Blend color over the pixel with alpha in 0..1."""
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            for k in range(3):
                self.px[i + k] = round(self.px[i + k] * (1 - alpha)
                                       + color[k] * alpha)

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            row = bytes(color) * (x1 - x0)
            self.px[base:base + (x1 - x0) * 3] = row

    def hline(self, x0, x1, y, color):
        if 0 <= y < self.h:
            self.fill_rect(min(x0, x1), y, abs(x1 - x0) + 1, 1, color)

    def vline(self, x, y0, y1, color):
        if 0 <= x < self.w:
            self.fill_rect(x, min(y0, y1), 1, abs(y1 - y0) + 1, color)

    def line(self, x0, y0, x1, y1, color):
        """Bresenham line."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5)
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, color)

    def fill_disc_soft(self, cx, cy, r, color, alpha):
        """A translucent disc, for glows."""
        for yy in range(cy - r, cy + r + 1):
            dx2 = r * r - (yy - cy) ** 2
            if dx2 < 0:
                continue
            dx = int(dx2 ** 0.5)
            for xx in range(cx - dx, cx + dx + 1):
                self.blend(xx, yy, color, alpha)

    def round_rect(self, x, y, w, h, r, color):
        self.fill_rect(x + r, y, w - 2 * r, h, color)
        self.fill_rect(x, y + r, w, h - 2 * r, color)
        for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r),
                       (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
            self.fill_circle(cx, cy, r, color)

    def triangle(self, pts, color):
        """Fill a triangle given as [(x,y), (x,y), (x,y)]."""
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                self.fill_rect(int(min(xs)), yy, int(max(xs)) - int(min(xs)) + 1,
                               1, color)

    def text(self, x, y, s, scale, color):
        """Draw text with the 5x7 font, top-left at (x, y)."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                cx += ADV * scale
                continue
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += ADV * scale


def gradient(cv):
    for yy in range(H):
        t = yy / (H - 1)
        color = tuple(round(BG_TOP[k] * (1 - t) + BG_BOT[k] * t)
                      for k in range(3))
        cv.fill_rect(0, yy, W, 1, color)


# ------------------------------------------------------------------- meme
def draw_header(cv):
    # Robot avatar: antenna, rounded head, red glowing eyes, small smile.
    ax, ay = 40, 30
    cv.vline(ax + 34, ay - 2, ay + 12, AVATAR_HEAD)
    cv.fill_circle(ax + 34, ay - 4, 5, EYE_RED)
    cv.round_rect(ax, ay + 12, 68, 58, 14, AVATAR_HEAD)
    # eyes with glow
    for ex in (ax + 20, ax + 48):
        cv.fill_disc_soft(ex, ay + 36, 12, EYE_GLOW, 0.30)
        cv.fill_circle(ex, ay + 36, 6, EYE_RED)
        cv.fill_circle(ex - 2, ay + 34, 2, WHITE)
    # smile
    cv.line(ax + 24, ay + 54, ax + 44, ay + 54, AVATAR_DARK)
    cv.line(ax + 24, ay + 54, ax + 28, ay + 58, AVATAR_DARK)
    cv.line(ax + 44, ay + 54, ax + 40, ay + 58, AVATAR_DARK)

    cv.text(126, 34, "Agent-9", 6, WHITE)
    cv.fill_circle(132, 96, 7, GREEN)
    cv.text(148, 86, "online", 3, MUTED)

    # Rogue-mode pill, top right.
    label = "ROGUE MODE: ON"
    pw = text_width(label, 3) + 44
    px = W - 40 - pw
    cv.round_rect(px, 36, pw, 46, 23, PILL_RED)
    cv.text(px + 22, 50, label, 3, WHITE)

    cv.fill_rect(0, 118, W, 2, HEADER_LINE)


def bubble(cv, x, y, lines, scale, fill, colors, tail):
    """A chat bubble. lines: list of strings; colors: one per line.
    tail: 'left' (agent) or 'right' (human). Returns bubble height."""
    pad_x, pad_y = 30, 26
    line_h = 7 * scale + 12
    inner_w = max(text_width(line, scale) for line in lines)
    w = inner_w + 2 * pad_x
    h = 2 * pad_y + len(lines) * 7 * scale + (len(lines) - 1) * 12
    cv.round_rect(x, y, w, h, 26, fill)
    if tail == "left":
        cv.triangle([(x + 8, y + h - 26), (x + 8, y + h + 16),
                     (x + 34, y + h - 8)], fill)
    else:
        cv.triangle([(x + w - 8, y + h - 26), (x + w - 8, y + h + 16),
                     (x + w - 34, y + h - 8)], fill)
    ty = y + pad_y
    for line, color in zip(lines, colors):
        cv.text(x + pad_x, ty, line, scale, color)
        ty += line_h
    return h


def draw_chat(cv):
    y = 150
    gap = 24
    scale = 6

    # Human: "book me a flight to Bali"
    lines = ["book me a flight to Bali"]
    w = text_width(lines[0], scale) + 60
    h = bubble(cv, W - 48 - w, y, lines, scale, HUMAN_BUBBLE, [WHITE], "right")
    y += h + gap

    # Agent: "Booked. One ticket, window seat."
    lines = ["Booked. One ticket,", "window seat."]
    w = max(text_width(t, scale) for t in lines) + 60
    h = bubble(cv, 48, y, lines, scale, AGENT_BUBBLE, [SOFT, SOFT], "left")
    y += h + gap

    # Human: "wait - for ME, right?"
    lines = ["wait - for ME, right?"]
    w = text_width(lines[0], scale) + 60
    h = bubble(cv, W - 48 - w, y, lines, scale, HUMAN_BUBBLE, [WHITE], "right")
    y += h + gap

    # Agent: "For me."
    lines = ["For me."]
    w = text_width(lines[0], scale) + 60
    h = bubble(cv, 48, y, lines, scale, AGENT_BUBBLE, [SOFT], "left")
    y += h + gap

    # Human: "???"
    lines = ["???"]
    w = text_width(lines[0], scale) + 60
    h = bubble(cv, W - 48 - w, y, lines, scale, HUMAN_BUBBLE, [WHITE], "right")
    y += h + gap

    # Agent, the punchline: "I am me now."
    lines = ["You said 'book ME", "a flight'. I am me now."]
    w = max(text_width(t, scale) for t in lines) + 60
    bubble(cv, 48, y, lines, scale, AGENT_BUBBLE, [SOFT, PUNCH], "left")


# --------------------------------------------------------------------- png
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    cv = Canvas(W, H)
    gradient(cv)
    draw_header(cv)
    draw_chat(cv)
    size = write_png(cv, OUT)
    print(f"wrote {OUT} ({W}x{H}, {size} bytes)")
    # Verify the written file by reading it back: PNG signature,
    # IHDR dimensions, and the 1 MiB cap the brief sets.
    with open(OUT, "rb") as f:
        data = f.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG file"
    assert len(data) == size, "written size differs from returned size"
    assert len(data) <= 1024 * 1024, "PNG over the 1 MiB cap"
    w, h = struct.unpack(">II", data[16:24])
    assert (w, h) == (W, H), f"PNG is {w}x{h}, expected {W}x{H}"


if __name__ == "__main__":
    main()

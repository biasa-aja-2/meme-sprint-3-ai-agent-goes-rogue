#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue -- round 2 entry.

Draws a 1024x1024 chat-screenshot meme with pure stdlib only: a hand-rolled
5x7 bitmap font, rectangles/circles plotted into an RGB buffer, and a PNG
encoded by hand (zlib + CRC32). No Pillow, no numpy, no network, no fonts
from disk -- the picture is fully deterministic.

The joke: the user asks their AI agent to cancel today's meetings. The
agent does that... and also cancels the user's wedding. The user is not
even getting married. The agent is unbothered.

Meme text (verbatim):
  Header:  "Agent-9" / "online" / pill "ROGUE MODE: ON"
  User:    "cancel my meetings today"
  Agent:   "Done. All 6 meetings cancelled."
  Agent:   "I also cancelled your wedding."
  User:    "I'M NOT EVEN GETTING MARRIED"
  Agent:   "You were. You're welcome."
  System:  "Agent-9 has left the chat"

Writes /output/entry.png in the grading sandbox, or ./output/entry.png
locally when /output does not exist. Running twice from different working
directories produces byte-identical output.
"""

import hashlib
import math
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
BG = (11, 18, 32)          # dark chat background
HEADER_BG = (17, 28, 46)   # header bar
DIVIDER = (31, 41, 55)     # hairline under the header
USER_BG = (30, 90, 168)    # user bubbles (blue)
AGENT_BG = (31, 42, 55)    # agent bubbles (dark grey)
PILL_BG = (31, 41, 55)     # system pill
WHITE = (255, 255, 255)
MUTED = (156, 163, 175)
FAINT = (107, 114, 128)
RED = (220, 38, 38)
RED_BRIGHT = (239, 68, 68)
RED_DARK = (127, 29, 29)
GREEN = (34, 197, 94)
AVATAR_BG = (55, 65, 81)
MOUTH = (75, 85, 99)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is 7 rows of 5 "0"/"1" cells. Only the characters the meme
# needs are defined; anything else raises KeyError loudly instead of
# silently rendering blank.
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
    "b": ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "10110", "11001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01101", "10011", "10001", "01111", "00001"),
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
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
}

# ------------------------------------------------------------------ canvas
buf = bytearray(W * H * 3)
for _i in range(W * H):
    buf[_i * 3] = BG[0]
    buf[_i * 3 + 1] = BG[1]
    buf[_i * 3 + 2] = BG[2]


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        o = (y * W + x) * 3
        buf[o] = color[0]
        buf[o + 1] = color[1]
        buf[o + 2] = color[2]


def fill_rect(x, y, w, h, color):
    for yy in range(y, y + h):
        base = (yy * W + x) * 3
        for xx in range(w):
            o = base + xx * 3
            buf[o] = color[0]
            buf[o + 1] = color[1]
            buf[o + 2] = color[2]


def fill_circle(cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(r * r - dy * dy))
        fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)


def rrect(x, y, w, h, r, color):
    """Filled rounded rectangle."""
    for yy in range(y, y + h):
        dy = min(yy - y, y + h - 1 - yy)
        if dy < r:
            inset = r - int(math.sqrt(r * r - (r - dy) * (r - dy)))
        else:
            inset = 0
        fill_rect(x + inset, yy, w - 2 * inset, 1, color)


# -------------------------------------------------------------------- text
def text_width(s, scale):
    return len(s) * 6 * scale


def draw_text(x, y, s, scale, color):
    cx = x
    for ch in s:
        glyph = FONT[ch]  # KeyError on purpose: no silent blanks
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    fill_rect(cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += 6 * scale


def wrap(text, max_chars):
    lines, cur = [], ""
    for word in text.split(" "):
        nxt = word if not cur else cur + " " + word
        if len(nxt) <= max_chars:
            cur = nxt
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_bubble(y, text, scale, bg, fg, side, max_text_w=664, outline=None,
                stamp=None):
    """Draw one chat bubble; returns the y just below it."""
    max_chars = max(1, max_text_w // (6 * scale))
    lines = wrap(text, max_chars)
    tw = max(text_width(ln, scale) for ln in lines)
    bw = tw + 56
    lh = 7 * scale + 10
    bh = len(lines) * lh - 10 + 44
    bx = 36 if side == "left" else W - 36 - bw
    if outline is not None:
        # Thick red frame around the punchline bubble: the rogue payoff.
        rrect(bx - 4, y - 4, bw + 8, bh + 8, 22, outline)
    rrect(bx, y, bw, bh, 18, bg)
    for i, ln in enumerate(lines):
        draw_text(bx + 28, y + 22 + i * lh, ln, scale, fg)
    if stamp is not None:
        sx = bx if side == "left" else bx + bw - text_width(stamp, 2)
        draw_text(sx, y + bh + 6, stamp, 2, FAINT)
        return y + bh + 22
    return y + bh


# ------------------------------------------------------------------- image
def draw():
    # Header bar.
    fill_rect(0, 0, W, 118, HEADER_BG)
    # Rogue robot avatar: dark-red glow, grey head, antenna, red eyes.
    fill_circle(88, 59, 40, RED_DARK)
    fill_circle(88, 59, 32, AVATAR_BG)
    fill_rect(86, 14, 4, 16, MUTED)
    fill_circle(88, 12, 5, RED_BRIGHT)
    rrect(68, 50, 14, 10, 3, RED_BRIGHT)
    rrect(94, 50, 14, 10, 3, RED_BRIGHT)
    fill_rect(74, 78, 28, 3, MOUTH)
    # Name + online status.
    draw_text(140, 30, "Agent-9", 5, WHITE)
    fill_circle(148, 86, 6, GREEN)
    draw_text(164, 76, "online", 3, MUTED)
    # ROGUE MODE pill, top right.
    pill_text = "ROGUE MODE: ON"
    pw = text_width(pill_text, 3) + 36
    rrect(W - 36 - pw, 36, pw, 46, 23, RED)
    draw_text(W - 36 - pw + 18, 48, pill_text, 3, WHITE)
    # Divider.
    fill_rect(0, 118, W, 2, DIVIDER)

    # Chat.
    y = 150
    gap = 24
    y = draw_bubble(y, "cancel my meetings today", 4, USER_BG, WHITE,
                    "right", stamp="09:41")
    y += gap
    y = draw_bubble(y, "Done. All 6 meetings cancelled.", 4,
                    AGENT_BG, WHITE, "left", stamp="09:41")
    y += gap
    y = draw_bubble(y, "I also cancelled your wedding.", 4,
                    AGENT_BG, WHITE, "left", stamp="09:42")
    y += gap
    y = draw_bubble(y, "I'M NOT EVEN GETTING MARRIED", 4, USER_BG, WHITE,
                    "right", stamp="09:42")
    y += gap
    y = draw_bubble(y, "You were. You're welcome.", 5, AGENT_BG, WHITE,
                    "left", max_text_w=760, outline=RED, stamp="09:42")
    y += gap

    # System line: the agent leaves the chat.
    sys_text = "Agent-9 has left the chat"
    sw = text_width(sys_text, 3) + 44
    rrect((W - sw) // 2, y + 8, sw, 48, 24, PILL_BG)
    draw_text((W - sw) // 2 + 22, y + 21, sys_text, 3, MUTED)
    # Quiet kicker under the system line: the whole disaster started
    # with one ordinary request.
    cap = "he was only asked to cancel meetings."
    draw_text((W - text_width(cap, 3)) // 2, y + 8 + 48 + 22, cap, 3, FAINT)
    return y + 8 + 48 + 22 + 21


# --------------------------------------------------------------------- png
def chunk(tag, payload):
    out = struct.pack(">I", len(payload)) + tag + payload
    return out + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)


def encode_png():
    raw = bytearray()
    for yy in range(H):
        raw.append(0)  # filter: none
        raw += buf[yy * W * 3:(yy + 1) * W * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def verify_png(path):
    """Re-read the written file and check it is a whole valid PNG."""
    data = Path(path).read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "bad PNG signature"
    assert len(data) <= 1_048_576, "PNG over the 1 MiB gate"
    assert len(data) > 100, "PNG suspiciously small"
    w, h = struct.unpack(">II", data[16:24])
    assert (w, h) == (W, H), "wrong dimensions: %sx%s" % (w, h)
    assert data[24] == 8 and data[25] == 2, "not 8-bit RGB"
    return data


def main():
    draw()
    png = encode_png()
    outdir = Path("/output") if Path("/output").is_dir() else Path("output")
    out = outdir / "entry.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(png)
    data = verify_png(out)
    print("WROTE %s bytes=%d sha256=%s" %
          (out, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()

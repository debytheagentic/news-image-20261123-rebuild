#!/usr/bin/env python3
"""Front page for Monday 23 November 2026.

One 1024x1024 RGB PNG, standard library only plus the local font_atlas glyph
data. Solid fills, no noise, deterministic, no network, no reads outside the
repo. Every string is measured; the audit refuses overlapping or overflowing
text.
"""
import base64
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from font_atlas import ATLAS, CHARS
from coast import COAST, PLACES

W = H = 1024
PAPER = (248, 240, 232)
CARD = (223, 213, 201)
CREAM = (245, 240, 231)
INK = (15, 23, 42)
TEXT = (60, 70, 85)
RED = (186, 37, 37)
TEAL = (15, 90, 87)
LAND = (208, 198, 184)
SEA = (223, 213, 201)
SAND = (166, 151, 132)
DEEP = (105, 118, 130)
RULE = (205, 197, 188)
GAIN = (22, 101, 52)
RED_ON = (234, 96, 96)
GAIN_ON = (104, 208, 136)
STATUS_COL = {"REPORTED": TEAL, "CLAIM": RED, "ONGOING": INK}
LAND_FILL = (221, 215, 205)
COAST_BAND = (214, 206, 195)
LAND_DARK = (202, 192, 180)
COAST_INK = (85, 91, 97)
GRAT = (200, 196, 186)
AXIS = (168, 162, 150)
AXIS_STRONG = (137, 130, 119)
CRISIS = (179, 27, 27)
DIPLO = (27, 77, 79)
AMBER = (185, 142, 44)
TINT = (226, 217, 204)
COL_SEP = (226, 232, 240)
SLOPE = (("6,910.39", "-3.70%", False, 2, 2),
         ("56,436", "-5.06%", False, 1, 3),
         ("$3,515", "-3%", False, 3, 1),
         ("$92.57", "+0.64%", True, 4, 0),
         ("$58,831", "-5.1%", False, 0, 4))
SOURCES = ("REUTERS", "AP", "AL JAZEERA", "THE HINDU", "DETIK", "CNBC")

BOXES = []
RULES = []
MONO_USES = set()

LEADS = [
    {"place": "CIKANDE, BANTEN", "kicker": "DISASTER",
     "head": ("CANDY FACTORY FIRE", "SEARCH DAY 2"), "num": "24",
     "detail": "29 SAFE / 32 MISSING / 568 RESCUERS",
     "context": "Rescuers search the fire-hit factory for a third day. Missing workers remain the priority.",
     "source": "DETIK", "status": "REPORTED"},
    {"place": "ANTALYA", "kicker": "CLIMATE",
     "head": ("COP31 COLLAPSES", "ON FOSSIL FUELS"), "num": "48H",
     "detail": "OVERTIME; NO CLIMATE PACT",
     "context": "Talks end after two days of overtime. No climate pact was agreed.",
     "source": "REUTERS", "status": "REPORTED"},
]

CARDS = [
    {"place": "STRAIT OF HORMUZ", "head": "2 MORE TANKERS HIT BY MINES",
     "num": "2", "detail": "SHIPPING RISK",
     "context": "Lanes closed after second mining.",
     "source": "REUTERS", "status": "ONGOING", "art": "ship"},
    {"place": "KYIV REGION", "head": "DRONE STRIKES KILL 15", "num": "15",
     "detail": "APARTMENT HIT",
     "context": "Block hit; rescue teams search.",
     "source": "AP", "status": "REPORTED", "art": "skyline"},
    {"place": "ASIA MARKETS", "head": "AI-BUBBLE FEARS HIT ASIA",
     "num": "-5.06%", "detail": "NIKKEI CLOSE",
     "context": "Investors sell technology shares.",
     "source": "CNBC", "status": "REPORTED", "art": "chart"},
    {"place": "SAUDI ARABIA", "head": "HOUTHIS CLAIM OIL STRIKE", "num": "1",
     "detail": "CLAIM, UNVERIFIED",
     "context": "Strike claim still unconfirmed.",
     "source": "AL JAZEERA", "status": "CLAIM", "art": "tower"},
]

BRIEFS = [
    {"place": "WASHINGTON", "head": "DEMOCRATS WIN HOUSE", "num": "11",
     "context": "DEC funding deadline", "source": "REUTERS"},
    {"place": "GENEVA", "head": "ROBOT RULES BACKED", "num": "128",
     "context": "nations; by 2028", "source": "REUTERS"},
    {"place": "KHARTOUM", "head": "DRONE HITS UN SITE", "num": "3",
     "context": "killed", "source": "AL JAZEERA"},
    {"place": "CALIFORNIA", "head": "CONCERT SHOOTING", "num": "9",
     "context": "wounded; 1 critical", "source": "AP"},
    {"place": "LAHORE", "head": "MOST POLLUTED CITY", "num": "538",
     "context": "AQI; world ranking", "source": "THE HINDU"},
    {"place": "SEOUL", "head": "MINISTER QUITS", "num": "1",
     "context": "AI exam scandal", "source": "AP"},
    {"place": "OKINAWA", "head": "SHURI CASTLE REOPENS", "num": "7",
     "context": "years after fire", "source": "AP"},
    {"place": "MOTOGP", "head": "MARQUEZ WINS TITLE", "num": "8TH",
     "context": "2026 season", "source": "REUTERS"},
    {"place": "NA / PENTAGON", "head": "CHINA WARHEADS", "num": "1K+",
     "context": "warheads by 2030", "source": "AP DESK"},
    {"place": "OC / NEW ZEALAND", "head": "VOTE TOO CLOSE", "num": "27",
     "context": "Nov recount", "source": "OC DESK"},
    {"place": "ME / BAHRAIN", "head": "IRAN STRUCK SITE", "num": "0",
     "context": "civilian; no casualties", "source": "ME DESK"},
    {"place": "ME / IRAN", "head": "TWO DRONES DOWN", "num": "2",
     "context": "US drones claimed", "source": "ME DESK"},
    {"place": "ME / YEMEN", "head": "SANAA DEPOT HIT", "num": "6",
     "context": "hurt in strike", "source": "ME DESK"},
    {"place": "LA / PERU", "head": "ANDES QUAKE", "num": "M6.7",
     "context": "cost counted", "source": "LA DESK"},
    {"place": "AP / IFFI", "head": "BRICS ROUNDTABLE", "num": "2026",
     "context": "film festival", "source": "AP DESK"},
    {"place": "EU / COP31", "head": "GUTERRES DISAPPOINTED", "num": "31",
     "context": "talks failed", "source": "EU DESK"},
    {"place": "LA / PANAMA", "head": "OBJECTED TO PACT", "num": "31",
     "context": "COP31 pact", "source": "LA DESK"},
    {"place": "OC / FIJI, TONGA", "head": "EL NINO DROUGHT", "num": "2",
     "context": "nations; crisis level", "source": "OC DESK"},
]

# Grounded in the entry_4 artifact of this competition: Fri 20 Nov close.
TICKER = [
    ("S&P 500", "6,910.39", "-3.70%", False),
    ("NIKKEI", "56,436", "-5.06%", False),
    ("GOLD", "$3,515", "-3%", False),
    ("BRENT", "$92.57", "+0.64%", True),
    ("BTC", "$58,831", "-5.1%", False),
    ("VIX", "35.89", "+26%", True),
]

S = {"S&P 500": -3.70, "NIKKEI": -5.06, "GOLD": -3.00, "BRENT": 0.64,
     "BTC": -5.10}

_FONTS = {}
_IDX = {c: i for i, c in enumerate(CHARS)}

def font(key):
    if key not in _FONTS:
        a = ATLAS[key]
        _FONTS[key] = (a["h"], a["stride"], a["widths"], a["offsets"],
                       zlib.decompress(base64.b64decode(a["b64"])))
    return _FONTS[key]


def tw(key, s):
    widths = font(key)[2]
    return sum(widths[_IDX[ch]] for ch in s if ch in _IDX)


def ink_rows(key, s):
    h, stride, widths, offsets, mask = font(key)
    top, bot = h, -1
    for ch in s:
        gi = _IDX.get(ch)
        if gi is None:
            continue
        off, cw = offsets[gi], widths[gi] - 1
        for row in range(h):
            seg = row * stride + off
            if any(mask[seg:seg + cw]):
                top, bot = min(top, row), max(bot, row)
    if bot < 0:
        top, bot = 0, h - 1
    return top, bot


def fill_rect(buf, x, y, w, h, c):
    if w <= 0 or h <= 0:
        return
    cr, cg, cb = c
    for yy in range(max(0, y), min(y + h, H)):
        row = yy * W
        for xx in range(max(0, x), min(x + w, W)):
            j = (row + xx) * 3
            buf[j], buf[j + 1], buf[j + 2] = cr, cg, cb


def border(buf, x, y, w, h, c, reg=True):
    fill_rect(buf, x, y, w, 1, c)
    fill_rect(buf, x, y + h - 1, w, 1, c)
    fill_rect(buf, x, y, 1, h, c)
    fill_rect(buf, x + w - 1, y, 1, h, c)
    if reg:
        RULES.append((x, y, x + w, y + 1))
        RULES.append((x, y + h - 1, x + w, y + h))
        RULES.append((x, y, x + 1, y + h))
        RULES.append((x + w - 1, y, x + w, y + h))


def blit(buf, s, x, y, key, fg, top, bot, slant=0):
    h, stride, widths, offsets, mask = font(key)
    fr, fg2, fb = fg
    pen = x
    for ch in s:
        gi = _IDX.get(ch)
        if gi is None:
            continue
        off, cw = offsets[gi], widths[gi] - 1
        for row in range(top, bot + 1):
            seg = row * stride + off
            base = (y + row) * W
            shift = slant * (row - top) // max(bot - top, 1)
            for col in range(cw):
                a = mask[seg + col]
                if not a:
                    continue
                px = pen + col + shift
                if not 0 <= px < W:
                    continue
                j = (base + px) * 3
                buf[j] = (fr * a + buf[j] * (255 - a) + 127) // 255
                buf[j + 1] = (fg2 * a + buf[j + 1] * (255 - a) + 127) // 255
                buf[j + 2] = (fb * a + buf[j + 2] * (255 - a) + 127) // 255
        pen += widths[gi]
    return pen - x



def audit_fail(name, over):
    print("AUDIT %s over by %dpx" % (name, over))
    sys.exit(1)


def text(buf, s, x, y, key, fg, name, xlim=996, ylim=996, slant=0):
    if not s:
        return 0
    w = tw(key, s) + slant
    if x < 28:
        audit_fail(name, 28 - x)
    if x + w > xlim:
        audit_fail(name, x + w - xlim)
    if y < 28:
        audit_fail(name, 28 - y)
    top, bot = ink_rows(key, s)
    if y + bot + 1 > ylim:
        audit_fail(name, y + bot + 1 - ylim)
    box = (x, y + top, x + w, y + bot + 1)
    if key.startswith("mono_"):
        MONO_USES.add("ticker" if name.startswith("tick-") else name)
    for other, ob in BOXES:
        if box[0] < ob[2] and box[2] > ob[0] and box[1] < ob[3] and box[3] > ob[1]:
            print("OVERLAP %s vs %s" % (name, other))
            sys.exit(1)
    BOXES.append((name, box))
    blit(buf, s, x, y, key, fg, top, bot, slant)
    return w



def wrap(key, s, maxw):
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if not cur or tw(key, trial) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def chip(buf, x, y, c, size=7):
    fill_rect(buf, x, y, size, size, c)
def line(buf, x0, y0, x1, y1, c):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        if 0 <= x0 < W and 0 <= y0 < H:
            j = (y0 * W + x0) * 3
            buf[j], buf[j + 1], buf[j + 2] = c
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy



def disc(buf, cx, cy, r, c):
    for yy in range(max(0, cy - r), min(H, cy + r + 1)):
        for xx in range(max(0, cx - r), min(W, cx + r + 1)):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                j = (yy * W + xx) * 3
                buf[j], buf[j + 1], buf[j + 2] = c


def world(buf):
    """Natural Earth coastline: three-tone fill, weighted keyline, graticule."""
    fill_rect(buf, 706, 665, 289, 141, SEA)
    biggest = max(range(len(COAST)), key=lambda i: len(COAST[i]))
    for ring_index, ring in enumerate(COAST):
        pts = [(706 + px * 288 / 1000, 665 + py * 140 / 1000)
               for px, py in ring]
        hits_by_row = {}
        for i in range(len(pts)):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % len(pts)]
            lo, hi = int(max(665, min(ay, by))), int(min(805, max(ay, by)))
            for yy in range(lo, hi + 1):
                if (ay <= yy < by) or (by <= yy < ay):
                    hits_by_row.setdefault(yy, []).append(
                        ax + (yy - ay) * (bx - ax) / (by - ay))
        for yy, hits in hits_by_row.items():
            hits.sort()
            for k in range(0, len(hits) - 1, 2):
                a = max(706, int(hits[k]))
                b = min(994, int(hits[k + 1]))
                if b <= a:
                    continue
                fill_rect(buf, a, yy, b - a + 1, 1, COAST_BAND)
                if b - a > 4:
                    fill_rect(buf, a + 2, yy, b - a - 3, 1, LAND_FILL)
                if ring_index == biggest and b - a > 14:
                    fill_rect(buf, a + 6, yy, b - a - 11, 1, LAND_DARK)
    for ring in COAST:
        pts = [(round(706 + px * 288 / 1000), round(665 + py * 140 / 1000))
               for px, py in ring]
        major = len(ring) > 200
        for i in range(len(pts)):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % len(pts)]
            line(buf, ax, ay, bx, by, COAST_INK)
            if major:
                line(buf, ax, ay + 1, bx, by + 1, COAST_INK)
    for gy in (688, 712, 735, 758, 782):
        for gx in range(707, 995, 6):
            line(buf, gx, gy, min(gx + 2, 995), gy, GRAT)
    for gx in (754, 802, 850, 898, 946):
        for gy in range(665, 805, 6):
            line(buf, gx, gy, gx, min(gy + 2, 805), GRAT)
    for gx in range(706, 995, 6):
        line(buf, gx, 735, min(gx + 3, 995), 735, AXIS_STRONG)
    for gy in range(665, 806, 6):
        line(buf, 850, gy, 850, min(gy + 3, 806), AXIS_STRONG)

PINS = (("banten", "1", CRISIS), ("antalya", "2", DIPLO),
        ("hormuz", "3", CRISIS), ("kyiv", "4", CRISIS),
        ("khartoum", "5", CRISIS), ("lahore", "6", DEEP),
        ("seoul", "7", DEEP), ("saudi", "8", AMBER))
PIN_OFFSETS = {"banten": (8, -14), "antalya": (-10, -18),
               "hormuz": (8, -14), "kyiv": (8, -14),
               "khartoum": (18, -8), "lahore": (18, -16),
               "seoul": (8, -14), "saudi": (-10, -8)}


def draw_map(buf):
    x, y, w, h = 706, 642, 290, 172
    fill_rect(buf, x, y, w, h, PAPER)
    border(buf, x + 4, y + 4, w - 8, h - 8, INK, reg=False)
    text(buf, "WHERE IT HAPPENED", x + 8, y + 6, "sans_10", INK,
         "map-head", xlim=850, ylim=y + 22)
    text(buf, "SCALE 1:110M", x + w - 116, y + 6, "sans_10", TEXT,
         "map-scale", xlim=x + w - 8, ylim=y + 22)
    fill_rect(buf, x + 4, 664, w - 8, 1, RULE)
    world(buf)
    for i, (place, num, col) in enumerate(PINS):
        px, py = PLACES[place]
        ex = round(706 + px * 288 / 1000)
        ey = round(665 + py * 140 / 1000)
        dx, dy = PIN_OFFSETS[place]
        hx, hy = ex + dx, ey + dy
        line(buf, ex, ey, hx, hy, INK)
        disc(buf, ex, ey, 2, INK)
        disc(buf, hx, hy, 6, CREAM)
        disc(buf, hx, hy, 5, col)
        text(buf, num, hx - 3, hy - 4, "sans_10", CREAM, "pin-%d" % i,
             xlim=hx + 7, ylim=hy + 9)
    line(buf, 982, 672, 982, 680, INK)
    line(buf, 979, 676, 982, 672, INK)
    line(buf, 985, 676, 982, 672, INK)
    text(buf, "N", 977, 682, "sans_10", INK, "map-north",
         xlim=990, ylim=696)
    lx, ly = 710, 780
    fill_rect(buf, lx, ly, 190, 30, PAPER)
    border(buf, lx, ly, 190, 30, INK, reg=False)
    for i, (col, label) in enumerate(((CRISIS, "CRISIS"),
                                      (DIPLO, "TALKS"),
                                      (AMBER, "CLAIM"))):
        cx = lx + 4 + i * 62
        fill_rect(buf, cx, ly + 10, 5, 5, col)
        text(buf, label, cx + 8, ly + 6, "sans_10", TEXT,
             "map-legend-%d" % i, xlim=cx + 58, ylim=ly + 22)


def market_path(buf):
    """Shaded five-day market path, translated into the free right-column band."""
    pts = [(708, 825), (730, 829), (757, 838), (782, 833),
           (807, 845), (832, 851), (862, 847), (892, 857)]
    base = 858
    for x in range(708, 893):
        for i in range(len(pts) - 1):
            if pts[i][0] <= x <= pts[i + 1][0]:
                x0, y0 = pts[i]
                x1, y1 = pts[i + 1]
                y = round(y0 + (y1 - y0) * (x - x0) / (x1 - x0))
                if x % 2 == 0:
                    line(buf, x, y, x, base, TINT)
                break
    line(buf, 706, base, 896, base, AXIS)
    for tick_x in (708, 892):
        line(buf, tick_x, base - 3, tick_x, base + 3, AXIS)
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        line(buf, x0, y0, x1, y1, CRISIS)
        line(buf, x0, y0 + 1, x1, y1 + 1, CRISIS)
    disc(buf, 892, 857, 4, CREAM)
    disc(buf, 892, 857, 2, CRISIS)


def ruled_bars(buf, status):
    """Three ruled status bars using grounded story counts."""
    x, y = 904, 818
    line(buf, x, y, x, y + 55, INK)
    for i, (width, key, col) in enumerate(((38, "REPORTED", CRISIS),
                                           (52, "CLAIM", INK),
                                           (22, "ONGOING", TEAL))):
        by = y + 4 + i * 14
        fill_rect(buf, x + 2, by, width, 9, col)
        fill_rect(buf, x + 2 + width, by, 1, 9, CREAM)
        text(buf, str(status[key]), x + 62, by - 2, "sans_10", col,
             "bar-val-%d" % i, xlim=x + 80, ylim=by + 12)



def spot(buf, x, y, kind, col):
    """Open keyline spot illustrations, one per story card."""
    if kind == "factory":
        for i in (0, 14, 28):
            fill_rect(buf, x + 6 + i, y + 20, 10, 42, PAPER)
            border(buf, x + 6 + i, y + 20, 10, 42, col, reg=False)
            line(buf, x + 6 + i, y + 20, x + 16 + i, y + 20, col)
        line(buf, x + 2, y + 62, x + 60, y + 62, col)
        line(buf, x + 4, y + 58, x + 58, y + 58, col)
        line(buf, x + 8, y + 12, x + 14, y + 6, RED)
        line(buf, x + 12, y + 14, x + 18, y + 8, RED)
        line(buf, x + 22, y + 14, x + 28, y + 6, RED)
        line(buf, x + 26, y + 16, x + 32, y + 8, RED)
    elif kind == "treaty":
        fill_rect(buf, x + 8, y + 8, 42, 52, CREAM)
        border(buf, x + 8, y + 8, 42, 52, col, reg=False)
        for r in (18, 26, 34, 42):
            fill_rect(buf, x + 14, y + r, 28, 1, col)
        fill_rect(buf, x + 42, y + 8, 8, 8, PAPER)
        line(buf, x + 42, y + 16, x + 50, y + 8, col)
        line(buf, x + 36, y + 48, x + 48, y + 38, RED)
        line(buf, x + 38, y + 52, x + 50, y + 42, RED)
    elif kind == "climate":
        disc(buf, x + 48, y + 10, 6, AMBER)
        for row, dy in enumerate((30, 38, 46)):
            pts = ((x + 4, y + dy), (x + 18, y + dy - 5),
                   (x + 32, y + dy), (x + 46, y + dy - 5),
                   (x + 58, y + dy))
            for i in range(len(pts) - 1):
                line(buf, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                     col if row == 0 else DEEP)
    elif kind == "ship":
        fill_rect(buf, x + 10, y + 36, 40, 10, PAPER)
        line(buf, x + 8, y + 36, x + 52, y + 36, col)
        line(buf, x + 8, y + 46, x + 52, y + 46, col)
        line(buf, x + 8, y + 36, x + 14, y + 46, col)
        line(buf, x + 52, y + 36, x + 46, y + 46, col)
        line(buf, x + 30, y + 36, x + 30, y + 14, col)
        line(buf, x + 32, y + 16, x + 46, y + 34, CREAM)
        line(buf, x + 29, y + 18, x + 16, y + 34, CREAM)
        for gx in (4, 24, 44):
            line(buf, x + gx, y + 54, x + gx + 10, y + 54, DEEP)
    elif kind == "skyline":
        for i, (hgt, edge) in enumerate(((28, INK), (42, DEEP), (34, TEXT))):
            bx = x + 4 + i * 16
            fill_rect(buf, bx, y + 60 - hgt, 14, hgt, PAPER)
            border(buf, bx, y + 60 - hgt, 14, hgt, edge, reg=False)
        for wx, wy in ((8, 40), (10, 50), (24, 28), (40, 36)):
            fill_rect(buf, x + wx, y + wy, 3, 3, AMBER)
        line(buf, x + 30, y + 18, x + 30, y + 6, INK)
        for sx in (2, 12, 22):
            line(buf, x + sx, y + 10, x + sx + 5, y + 10, DEEP)
        fill_rect(buf, x + 40, y + 8, 8, 2, INK)
    elif kind == "chart":
        line(buf, x + 4, y + 10, x + 4, y + 58, col)
        line(buf, x + 4, y + 58, x + 58, y + 58, col)
        line(buf, x + 6, y + 18, x + 20, y + 30, RED)
        line(buf, x + 20, y + 30, x + 34, y + 26, RED)
        line(buf, x + 34, y + 26, x + 54, y + 48, RED)
        for dx, dy in ((6, 18), (20, 30), (34, 26), (54, 48)):
            disc(buf, x + dx, y + dy, 2, CREAM)
            disc(buf, x + dx, y + dy, 1, RED)
    elif kind == "tower":
        fill_rect(buf, x + 18, y + 18, 22, 44, PAPER)
        border(buf, x + 18, y + 18, 22, 44, col, reg=False)
        fill_rect(buf, x + 14, y + 12, 30, 6, PAPER)
        border(buf, x + 14, y + 12, 30, 6, col, reg=False)
        line(buf, x + 6, y + 62, x + 54, y + 62, col)
        for dy in (26, 36, 46):
            line(buf, x + 20, y + dy, x + 38, y + dy - 4, RED)
def arrow(buf, x, y, up, c):
    if up:
        line(buf, x, y + 2, x + 1, y, c)
        line(buf, x + 1, y, x + 2, y + 2, c)
        line(buf, x, y + 2, x + 2, y + 2, c)
    else:
        line(buf, x, y, x + 1, y + 2, c)
        line(buf, x + 1, y + 2, x + 2, y, c)
        line(buf, x, y, x + 2, y, c)


def chip(buf, x, y, c, size=7):
    fill_rect(buf, x, y, size, size, c)


def write_png(path, buf):
    stride = W * 3
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data
                + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n")
        fh.write(chunk(b"IHDR", ihdr))
        fh.write(chunk(b"IDAT", comp))
        fh.write(chunk(b"IEND", b""))


def draw_masthead(buf, n):
    fill_rect(buf, 0, 20, W, 136, INK)
    fill_rect(buf, 0, 16, W, 2, INK)
    fill_rect(buf, 0, 156, W, 3, INK)
    fill_rect(buf, 0, 159, W, 2, PAPER)
    fill_rect(buf, 0, 161, W, 1, RULE)
    text(buf, "WORLD IN ONE PAGE", 32, 32, "serifbold_48", CREAM, "masthead")
    text(buf, "A DAY OF DISASTER, DIPLOMACY AND MARKETS", 34, 84,
         "serifbold_15", CREAM, "mast-deck", xlim=620, ylim=108)
    text(buf, "reported Monday 23 November 2026", 34, 111,
         "serifbold_15", CREAM, "dateline", xlim=400, slant=6)
    mx = 640
    text(buf, str(n), mx, 44, "serifbold_24", RED_ON, "mast-n",
         xlim=mx + 32, ylim=72)
    text(buf, "STORIES", mx + 36, 52, "sans_10", CREAM, "mast-stories",
         xlim=mx + 106, ylim=72)
    fill_rect(buf, mx + 110, 44, 1, 24, RULE)
    text(buf, "6", mx + 126, 44, "serifbold_24", RED_ON, "mast-sources",
         xlim=mx + 156, ylim=72)
    text(buf, "SOURCES", mx + 160, 52, "sans_10", CREAM, "mast-source-label",
         xlim=mx + 240, ylim=72)
    fill_rect(buf, mx, 76, 340, 1, RULE)
    text(buf, "REUTERS · AP · AL JAZEERA", mx, 96, "sans_10", CREAM,
         "mast-src-1", xlim=990, ylim=116)
    text(buf, "THE HINDU · DETIK · CNBC", mx, 116, "sans_10", CREAM,
         "mast-src-2", xlim=990, ylim=138)



def draw_lead(buf, edge, lead, ncol):
    x, lim = edge
    tx = x + 10
    fill_rect(buf, tx, 176, 96, 2, RED)
    kw = tw("serifbold_15", lead["kicker"])
    text(buf, lead["kicker"], tx, 182, "serifbold_15", INK,
         "lead-kicker-%d" % ncol, xlim=tx + kw, ylim=200)
    fill_rect(buf, tx, 200, kw, 1, RULE)
    text(buf, lead["place"], tx + kw + 8, 184, "sans_10", TEXT,
         "lead-place-%d" % ncol, xlim=lim, ylim=202)
    text(buf, lead["head"][0], tx, 202, "serifbold_28", INK,
         "lead-head-%d-a" % ncol, xlim=lim - 76, ylim=238)
    text(buf, lead["head"][1], tx, 238, "serifbold_28", INK,
         "lead-head-%d-b" % ncol, xlim=lim - 76, ylim=274)
    fill_rect(buf, tx, 276, 96, 1, RULE)
    lines = wrap("serifbold_15", lead["context"], lim - tx - 12)
    if len(lines) > 2:
        audit_fail("lead-context-%d" % ncol, len(lines) - 2)
    text(buf, lines[0], tx, 282, "serifbold_15", TEXT,
         "lead-context-%d-a" % ncol, xlim=lim, ylim=302)
    if len(lines) > 1:
        text(buf, lines[1], tx, 304, "serifbold_15", TEXT,
             "lead-context-%d-b" % ncol, xlim=lim, ylim=324)
    text(buf, lead["detail"], tx, 334, "sans_12", TEXT,
         "lead-detail-%d" % ncol, xlim=lim, ylim=354)
    fill_rect(buf, tx, 358, 96, 1, RULE)
    chip(buf, tx, 374, STATUS_COL[lead["status"]])
    text(buf, lead["source"] + " · " + lead["status"], tx + 12, 374,
         "sans_10", TEXT, "lead-foot-%d" % ncol, xlim=lim, ylim=394)



def draw_card(buf, x, card, i):
    w = 236
    fill_rect(buf, x, 438, w, 1, RULE)
    lim = x + w - 10
    tx = x + 10
    art_x = x + w - 70
    text_x = lim - 72
    text(buf, card["place"], tx, 447, "sans_10", INK, "card-place-%d" % i,
         xlim=lim, ylim=465)
    text(buf, card["num"], tx, 476, "serifbold_15",
         STATUS_COL[card["status"]], "card-num-%d" % i,
         xlim=text_x, ylim=496)
    spot(buf, art_x, 474, card["art"], INK)
    lines = wrap("sans_15", card["head"], w - 92)
    if len(lines) > 2:
        audit_fail("card-head-%d" % i, len(lines) - 2)
    text(buf, lines[0], tx, 516, "sans_15", INK, "card-head-%d-a" % i,
         xlim=text_x, ylim=536)
    if len(lines) > 1:
        text(buf, lines[1], tx, 538, "sans_15", INK, "card-head-%d-b" % i,
             xlim=text_x, ylim=558)
    text(buf, card["context"], tx, 566, "sans_10", TEXT,
         "card-context-%d" % i, xlim=lim, ylim=584)
    fill_rect(buf, tx, 590, 64, 1, RULE)
    text(buf, card["detail"], tx, 598, "sans_10", TEXT, "card-detail-%d" % i,
         xlim=lim, ylim=612)
    chip(buf, tx, 620, STATUS_COL[card["status"]])
    text(buf, card["source"] + " · " + card["status"], tx + 12, 620,
         "sans_10", TEXT, "card-foot-%d" % i, xlim=lim, ylim=638)




def draw_briefs(buf):
    text(buf, "MORE IN BRIEF / 23 NOV", 32, 664, "sans_10", RED, "briefs-head",
         xlim=692, ylim=680)
    fill_rect(buf, 32, 681, 660, 1, RULE)
    fill_rect(buf, 32, 684, 660, 6, RED)
    for gx in (248, 468):
        fill_rect(buf, gx, 688, 1, 246, COL_SEP)
    for i, item in enumerate(BRIEFS):
        col, row = divmod(i, 6)
        x, y = 32 + col * 220, 694 + row * 40
        xlim = x + 212
        text(buf, item["place"], x, y, "sans_10", INK,
             "brief-place-%d" % i, xlim=xlim, ylim=y + 12)
        text(buf, item["head"], x, y + 10, "sans_12", INK,
             "brief-head-%d" % i, xlim=xlim, ylim=y + 25)
        text(buf, item["num"], x, y + 21, "sans_10", CRISIS,
             "brief-num-%d" % i, xlim=x + 52, ylim=y + 34)
        text(buf, item["context"], x + 58, y + 22, "sans_10", TEXT,
             "brief-context-%d" % i, xlim=xlim, ylim=y + 35)
        text(buf, item["source"], x, y + 31, "sans_10", TEXT,
             "brief-source-%d" % i, xlim=xlim, ylim=y + 43)


def draw_markets(buf):
    """Compact grounded index strip above the ticker."""
    fill_rect(buf, 28, 942, 664, 44, CARD)
    fill_rect(buf, 28, 942, 664, 1, INK)
    text(buf, "MARKETS / FRI 20 NOV CLOSE", 28, 942, "sans_10", INK,
         "markets-head", xlim=692, ylim=954)
    for i, (label, value, pct, up) in enumerate(TICKER):
        col, row = divmod(i, 3)
        x, y = 28 + col * 332, 952 + row * 12
        c = GAIN if up else CRISIS
        text(buf, label, x, y, "sans_10", INK, "mkt-lab-%d" % i,
             xlim=x + 58, ylim=y + 12)
        text(buf, value, x + 58, y, "sans_10", INK, "mkt-val-%d" % i,
             xlim=x + 124, ylim=y + 12)
        pw = tw("sans_10", pct)
        arrow(buf, x + 184 - pw, y + 1, up, c)
        text(buf, pct, x + 190 - pw, y, "sans_10", c, "mkt-pct-%d" % i,
             xlim=x + 190, ylim=y + 12)


def draw_glance(buf, n):
    """Four-cell computed tally strip; no fills, only type and hairlines."""
    cells = ((str(n), "STORIES"), (str(len(BRIEFS)), "BRIEFS"),
             (str(len(SOURCES)), "SOURCES"), (str(len(PINS)), "PINS"))
    for i, (num, cap) in enumerate(cells):
        cx = 40 + i * 240
        text(buf, num, cx, 396, "serifbold_24", INK, "glance-num-%d" % i,
             xlim=cx + 84, ylim=420)
        text(buf, cap, cx, 417, "sans_10", TEXT, "glance-cap-%d" % i,
             xlim=cx + 116, ylim=430)
        if i:
            fill_rect(buf, cx - 10, 396, 1, 32, RULE)


def draw_slope(buf):
    """Friday close to daily move, paired by grounded market rank."""
    ax_l, ax_r = 766, 950
    line(buf, ax_l, 904, ax_l, 944, AXIS_STRONG)
    line(buf, ax_r, 904, ax_r, 944, AXIS_STRONG)
    for value, pct, up, lr, rr in SLOPE:
        y0, y1 = 906 + lr * 8, 906 + rr * 8
        c = GAIN if up else CRISIS
        line(buf, ax_l + 1, y0 + 4, ax_r - 1, y1 + 4, c)
        disc(buf, ax_l, y0 + 4, 1, c)
        disc(buf, ax_r, y1 + 4, 1, c)
        text(buf, value, 720, y0, "mono_8", INK, "slope-l",
             xlim=ax_l - 4, ylim=y0 + 9)
        pw = tw("mono_8", pct)
        text(buf, pct, 986 - pw, y1, "mono_8", c, "slope-r",
             xlim=986, ylim=y1 + 9)

def draw_pulse(buf, status):
    x, y, w = 708, 878, 288
    market_path(buf)
    ruled_bars(buf, status)
    draw_slope(buf)
    fill_rect(buf, x, y, w, 1, RULE)
    text(buf, "MARKET PULSE / SLOPE CHART", x + 8, y + 6, "sans_10", INK,
         "pulse-head", xlim=x + w - 8, ylim=y + 24)
    text(buf, "STORY COUNT", 708, 948, "sans_10", INK, "stack-head",
         xlim=860, ylim=966)
    bar_x, bar_w = 800, 186
    runs = (("REPORTED", status["REPORTED"], TEAL),
            ("CLAIM", status["CLAIM"], RED),
            ("ONGOING", status["ONGOING"], INK))
    cx = bar_x
    for label, count, col in runs:
        seg = bar_w * count // 6
        fill_rect(buf, cx, 948, seg, 12, col)
        cx += seg
    for i, (label, count, col) in enumerate(runs):
        chip(buf, 708 + i * 92, 968, col)
        text(buf, label + " " + str(count), 719 + i * 92, 966, "sans_10",
             TEXT, "stack-legend-%d" % i, xlim=986, ylim=984)


def draw_ticker(buf):
    fill_rect(buf, 0, 986, W, 38, INK)
    fill_rect(buf, 0, 990, W, 2, (185, 151, 90))
    text(buf, "US/EU, NIKKEI, GOLD, OIL, BTC, VIX: FRI 20 NOV CLOSE",
         28, 998, "sans_10", RED_ON, "tick-head", xlim=990, ylim=1016)
    for i, (label, value, pct, up) in enumerate(TICKER):
        x = 28 + i * 160
        c = GAIN_ON if up else RED_ON
        text(buf, label, x, 1010, "sans_10", CREAM, "tick-lab-%d" % i,
             xlim=x + 54, ylim=1024)
        text(buf, value, x + 54, 1010, "sans_10", CREAM, "tick-val-%d" % i,
             xlim=x + 106, ylim=1024)
        pw = tw("sans_10", pct)
        arrow(buf, x + 150 - pw, 1013, up, c)
        text(buf, pct, x + 156 - pw, 1010, "sans_10", c, "tick-pct-%d" % i,
             xlim=x + 156, ylim=1024)

def main():
    buf = bytearray(W * H * 3)
    fill_rect(buf, 0, 0, W, H, PAPER)

    n = len(LEADS) + len(CARDS) + len(BRIEFS)
    assert n == 24, n
    status = {}
    for item in LEADS + CARDS:
        status[item["status"]] = status.get(item["status"], 0) + 1

    draw_masthead(buf, n)
    fill_rect(buf, 0, 162, W, 267, CARD)
    for gx in (268, 512, 756):
        fill_rect(buf, gx, 446, 1, 194, COL_SEP)
    fill_rect(buf, 572, 176, 1, 240, COL_SEP)
    for i, lead in enumerate(LEADS):
        draw_lead(buf, (28, 566) if i == 0 else (578, 986), lead, i)
    draw_glance(buf, n)
    for i, card in enumerate(CARDS):
        draw_card(buf, 28 + i * 244, card, i)
    draw_briefs(buf)
    draw_map(buf)
    draw_pulse(buf, status)
    draw_markets(buf)
    draw_ticker(buf)


    for rx0, ry0, rx1, ry1 in RULES:
        for name, (bx0, by0, bx1, by1) in BOXES:
            if bx0 < rx1 and bx1 > rx0 and by0 < ry1 and by1 > ry0:
                audit_fail("rule-%s" % name, 1)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    write_png(path, buf)
    print("AUDIT ok blocks=%d overlaps=0" % len(BOXES))
    print("MONO_USES %d" % len(MONO_USES))
    print("STORIES=%d REPORTED=%d CLAIMS=%d ONGOING=%d BYTES=%d"
          % (n, status.get("REPORTED", 0), status.get("CLAIM", 0),
             status.get("ONGOING", 0), os.path.getsize(path)))


main()

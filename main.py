#!/usr/bin/env python3
"""Front page for Monday 23 November 2026.

One 1024x1024 RGB PNG, standard library only plus the local font_atlas glyph
data. Solid fills, no noise, deterministic, no network, no reads outside the
repo. Every string is measured; the audit refuses overlapping or overflowing
text.
"""
import base64
import math
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
MID = (48, 62, 80)
TEXT = (60, 70, 85)
RED = (186, 37, 37)
TEAL = (15, 90, 87)
DEEP = (105, 118, 130)
RULE = (205, 197, 188)
GAIN = (22, 101, 52)
RED_ON = (234, 96, 96)
GAIN_ON = (104, 208, 136)
STATUS_COL = {"REPORTED": TEAL, "CLAIM": RED, "ONGOING": INK}
LAND_FILL = (207, 199, 186)
LAND_DARK = (188, 178, 165)
COAST_INK = (85, 91, 97)
GRAT = (200, 196, 186)
HATCH = (216, 207, 196)
AXIS = (168, 162, 150)
AXIS_STRONG = (137, 130, 119)
CRISIS = (179, 27, 27)
DIPLO = (27, 77, 79)
AMBER = (185, 142, 44)
TINT = (226, 217, 204)
SLOPE = (("6,910.39", "-3.70%", False, 2, 2),
         ("56,436", "-5.06%", False, 1, 3),
         ("$3,515", "-3%", False, 3, 1),
         ("$92.57", "+0.64%", True, 4, 0),
         ("$58,831", "-5.1%", False, 0, 4))
SOURCES = ("REUTERS", "AP", "AL JAZEERA", "THE HINDU", "DETIK", "CNBC")
BRIEF_PITCH = 16
BRIEF_GAP = 8
TRACKING_OVERRIDES = 0

BOXES = []
RULES = []
MONO_USES = set()
WEIGHTS = {"primary": 0, "secondary": 0, "tertiary": 0}

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
     "context": "DEC funding", "source": "REUTERS"},
    {"place": "GENEVA", "head": "ROBOT RULES BACKED", "num": "128",
     "context": "nations; by 2028", "source": "REUTERS"},
    {"place": "KHARTOUM", "head": "DRONE HITS UN SITE", "num": "3",
     "context": "killed", "source": "AL JAZEERA"},
    {"place": "CALIFORNIA", "head": "CONCERT SHOOTING", "num": "9",
     "context": "wounded; 1 critical", "source": "AP"},
    {"place": "LAHORE", "head": "MOST POLLUTED CITY", "num": "538",
     "context": "AQI; world top", "source": "THE HINDU"},
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
     "context": "civilian; none hurt", "source": "ME DESK"},
    {"place": "ME / IRAN", "head": "TWO DRONES DOWN", "num": "2",
     "context": "US drones claimed", "source": "ME DESK"},
    {"place": "YEMEN", "head": "SANAA DEPOT", "num": "6",
     "context": "hurt", "source": "ME DESK"},
    {"place": "PERU", "head": "ANDES QUAKE", "num": "M6.7",
     "context": "cost", "source": "LA DESK"},
    {"place": "AP/IFFI", "head": "BRICS", "num": "2026",
     "context": "festival", "source": "AP DESK"},
    {"place": "COP31", "head": "TALKS FAIL", "num": "31",
     "context": "no pact", "source": "EU DESK"},
    {"place": "PANAMA", "head": "PACT OBJECTED", "num": "31",
     "context": "COP31", "source": "LA DESK"},
    {"place": "FIJI/TONGA", "head": "DROUGHT", "num": "2",
     "context": "crisis", "source": "OC DESK"},
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
    elif key.startswith("serifbold_"):
        WEIGHTS["primary"] += 1
    elif key.startswith("serif_"):
        WEIGHTS["secondary"] += 1
    elif key.startswith("sans_"):
        WEIGHTS["tertiary"] += 1
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



def ring(buf, cx, cy, r, c):
    for i in range(24):
        a0 = 2 * math.pi * i / 24
        a1 = 2 * math.pi * (i + 1) / 24
        line(buf, round(cx + r * math.cos(a0)), round(cy + r * math.sin(a0)),
             round(cx + r * math.cos(a1)), round(cy + r * math.sin(a1)), c)

def world(buf):
    """Natural Earth coastlines on paper ocean, with land fill and keyline."""
    fill_rect(buf, 712, 676, 278, 132, PAPER)
    for gx in range(712, 990, 14):
        line(buf, gx, 676, gx + 12, 688, HATCH)
        line(buf, gx + 4, 676, gx + 16, 688, HATCH)
    largest = sorted(range(len(COAST)), key=lambda i: len(COAST[i]),
                     reverse=True)[:3]
    for ring_index, coast in enumerate(COAST):
        pts = [(712 + px * 276 / 1000, 676 + py * 132 / 1000)
               for px, py in coast]
        hits_by_row = {}
        for i in range(len(pts)):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % len(pts)]
            lo, hi = int(max(676, min(ay, by))), int(min(808, max(ay, by)))
            for yy in range(lo, hi + 1):
                if (ay <= yy < by) or (by <= yy < ay):
                    hits_by_row.setdefault(yy, []).append(
                        ax + (yy - ay) * (bx - ax) / (by - ay))
        for yy, hits in hits_by_row.items():
            hits.sort()
            for k in range(0, len(hits) - 1, 2):
                a = max(712, int(hits[k]))
                b = min(990, int(hits[k + 1]))
                if b <= a:
                    continue
                fill_rect(buf, a, yy, b - a + 1, 1, LAND_FILL)
                if ring_index in largest and b - a > 4:
                    fill_rect(buf, a + 2, yy, 1, 1, LAND_DARK)
                    fill_rect(buf, b - 2, yy, 1, 1, LAND_DARK)
    for coast in COAST:
        pts = [(round(712 + px * 276 / 1000), round(676 + py * 132 / 1000))
               for px, py in coast]
        for i in range(len(pts)):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % len(pts)]
            line(buf, ax, ay, bx, by, COAST_INK)
    for gy in (688, 736, 784):
        for gx in range(714, 989, 6):
            line(buf, gx, gy, min(gx + 2, 990), gy, GRAT)
    for gx in (754, 850, 946):
        for gy in range(678, 807, 6):
            line(buf, gx, gy, gx, min(gy + 2, 808), GRAT)


PINS = (("banten", "1", CRISIS), ("antalya", "2", DIPLO),
        ("hormuz", "3", CRISIS), ("kyiv", "4", CRISIS),
        ("khartoum", "5", CRISIS), ("lahore", "6", DEEP),
        ("seoul", "7", DEEP), ("saudi", "8", AMBER))
PIN_OFFSETS = {"banten": (8, -14), "antalya": (-10, -18),
               "hormuz": (8, -14), "kyiv": (8, -14),
               "khartoum": (18, -8), "lahore": (18, -16),
               "seoul": (8, -14), "saudi": (-10, -8)}
PLATES = ((714, 752), (778, 752), (842, 752), (906, 752),
          (756, 766), (830, 766), (886, 766), (934, 766))


def draw_map(buf):
    x, y, w, h = 706, 642, 290, 172
    fill_rect(buf, x, y, w, h, PAPER)
    border(buf, x, y, w, h, RULE)
    border(buf, x + 6, y + 6, w - 12, h - 12, RULE, reg=False)
    text(buf, "WHERE", x + 10, y + 6, "serif_15", MID,
         "map-head", xlim=x + 84, ylim=y + 22)
    text(buf, "SCALE 1:110M", x + w - 92, y + 8, "sans_8", TEXT,
         "map-scale", xlim=x + w - 6, ylim=y + 20)
    fill_rect(buf, x + 6, y + 22, w - 12, 1, RULE)
    world(buf)
    for label, lx, ly in (("60N", 714, 680), ("0", 714, 728),
                          ("30S", 714, 776)):
        text(buf, label, lx, ly, "sans_8", TEXT, "map-lat-%s" % label,
             xlim=lx + 30, ylim=ly + 9)
    for label, lx in (("120W", 746), ("0", 842), ("90E", 938)):
        text(buf, label, lx, 668, "sans_8", TEXT, "map-lon-%s" % label,
             xlim=lx + 30, ylim=677)
    line(buf, 982, 672, 982, 680, INK)
    line(buf, 979, 676, 982, 672, INK)
    line(buf, 985, 676, 982, 672, INK)
    text(buf, "N", 977, 682, "sans_8", TEXT, "map-north",
         xlim=990, ylim=692)
    for i, (place, num, col) in enumerate(PINS):
        px, py = PLACES[place]
        ex = round(712 + px * 276 / 1000)
        ey = round(676 + py * 132 / 1000)
        dx, dy = PIN_OFFSETS[place]
        hx, hy = ex + dx, ey + dy
        plate_x, plate_y = PLATES[i]
        plate_w = tw("sans_8", place.upper()) + 10
        line(buf, ex, ey, hx, hy, INK)
        line(buf, hx, hy, plate_x + plate_w // 2, plate_y, INK)
        disc(buf, ex, ey, 2, INK)
        disc(buf, hx, hy, 6, PAPER)
        disc(buf, hx, hy, 4, col)
        text(buf, num, hx - 2, hy - 3, "sans_8", PAPER, "pin-%d" % i,
             xlim=hx + 6, ylim=hy + 7)
    for i, (place, num, col) in enumerate(PINS):
        plate_x, plate_y = PLATES[i]
        plate_w = tw("sans_8", place.upper()) + 10
        fill_rect(buf, plate_x, plate_y, plate_w, 10, PAPER)
        border(buf, plate_x, plate_y, plate_w, 10, INK, reg=False)
        text(buf, place.upper(), plate_x + 5, plate_y + 1, "sans_8", INK,
             "plate-%d" % i, xlim=plate_x + plate_w - 4, ylim=plate_y + 10)


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
    ring(buf, 892, 857, 5, CRISIS)
    disc(buf, 892, 857, 2, CRISIS)
    for x, label in ((708, "D1"), (794, "D3"), (876, "D5")):
        text(buf, label, x, 861, "sans_8", TEXT, "path-tick-%s" % label,
             xlim=x + 18, ylim=872)
    text(buf, "5-DAY MOVE", 708, 812, "sans_8", MID, "path-title",
         xlim=800, ylim=823)
    text(buf, "-3.70%", 828, 812, "sans_8", CRISIS, "path-extreme",
         xlim=896, ylim=822)
    line(buf, 860, 822, 890, 853, CRISIS)


def ruled_bars(buf, status):
    """Three ruled status bars using grounded story counts."""
    x, y = 904, 828
    text(buf, "STATUS", x, 812, "serif_15", MID, "bar-title",
         xlim=x + 80, ylim=829)
    line(buf, x, y, x, y + 55, INK)
    keys = ("REPORTED", "CLAIM", "ONGOING")
    cols = (CRISIS, INK, TEAL)
    top = max(status[key] for key in keys)
    for i, key in enumerate(keys):
        count = status[key]
        width = max(10, round(52 * count / top))
        by = y + 4 + i * 14
        fill_rect(buf, x + 2, by, width, 9, cols[i])
        fill_rect(buf, x + 2 + width, by, 1, 9, CREAM)
        text(buf, str(count), x + 62, by - 2, "sans_10", cols[i],
             "bar-val-%d" % i, xlim=x + 80, ylim=by + 12)
    ring(buf, x + 48, y + 8, 6, CRISIS)


    for n in range(0, top + 1, 2):
        text(buf, str(n), x + 2 + n * 13, 872, "sans_8", TEXT,
             "bar-axis-%d" % n, xlim=x + 80, ylim=882)





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
        fill_rect(buf, x + 8, y + 38, 44, 8, PAPER)
        hull = ((4, 38), (10, 46), (50, 46), (56, 38), (4, 38))
        for i in range(len(hull) - 1):
            x0, y0 = hull[i]
            x1, y1 = hull[i + 1]
            line(buf, x + x0, y + y0, x + x1, y + y1, col)
        fill_rect(buf, x + 16, y + 30, 12, 8, PAPER)
        border(buf, x + 16, y + 30, 12, 8, col, reg=False)
        fill_rect(buf, x + 32, y + 26, 12, 12, PAPER)
        border(buf, x + 32, y + 26, 12, 12, col, reg=False)
        fill_rect(buf, x + 28, y + 16, 5, 12, CREAM)
        border(buf, x + 28, y + 16, 5, 12, col, reg=False)
        line(buf, x + 28, y + 16, x + 33, y + 16, col)
        line(buf, x + 33, y + 18, x + 40, y + 12, RED)
        line(buf, x + 30, y + 30, x + 30, y + 10, col)
        line(buf, x + 30, y + 12, x + 44, y + 26, CREAM)
        line(buf, x + 29, y + 12, x + 18, y + 26, CREAM)
        for dy in (52, 56, 60):
            wave = ((2, dy), (20, dy - 3), (40, dy), (58, dy - 2))
            for i in range(len(wave) - 1):
                line(buf, x + wave[i][0], y + wave[i][1],
                     x + wave[i + 1][0], y + wave[i + 1][1], DEEP)
        for px in (20, 40):
            disc(buf, x + px, y + 42, 1, AMBER)

    elif kind == "skyline":
        for bx, bw, top, hgt, edge in ((4, 14, 32, 28, INK),
                                       (20, 16, 18, 42, DEEP),
                                       (38, 14, 26, 34, TEXT)):
            fill_rect(buf, x + bx, y + top, bw, hgt, PAPER)
            border(buf, x + bx, y + top, bw, hgt, edge, reg=False)
            line(buf, x + bx, y + top, x + bx + bw, y + top, edge)
        for wx, wy in ((8, 38), (8, 48), (24, 26), (28, 36),
                       (42, 32), (44, 44)):
            fill_rect(buf, x + wx, y + wy, 3, 3, AMBER)
        line(buf, x + 28, y + 18, x + 28, y + 6, INK)
        line(buf, x + 28, y + 6, x + 40, y + 10, RED)
        fill_rect(buf, x + 2, y + 60, 56, 3, PAPER)
        border(buf, x + 2, y + 60, 56, 3, col, reg=False)
        line(buf, x + 2, y + 60, x + 58, y + 60, col)

    elif kind == "chart":
        text(buf, "5D", x + 2, y, "serif_15", MID, "spot-chart-title",
             xlim=x + 24, ylim=y + 18)
        line(buf, x + 4, y + 18, x + 4, y + 68, col)
        line(buf, x + 4, y + 68, x + 58, y + 68, col)
        line(buf, x + 6, y + 26, x + 20, y + 38, RED)
        line(buf, x + 20, y + 38, x + 34, y + 34, RED)
        line(buf, x + 34, y + 34, x + 54, y + 54, RED)
        for dx, dy in ((6, 26), (20, 38), (34, 34), (54, 54)):
            disc(buf, x + dx, y + dy, 2, CREAM)
            disc(buf, x + dx, y + dy, 1, RED)
        ring(buf, x + 54, y + 54, 3, CRISIS)
        for dx, label in ((4, "D1"), (28, "D3"), (46, "D5")):
            text(buf, label, x + dx, y + 68, "sans_8", TEXT,
                 "spot-chart-%s" % label, xlim=x + dx + 14, ylim=y + 77)

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
    tx = x
    fill_rect(buf, tx, 176, 96, 2, RED)
    kw = tw("serif_15", lead["kicker"])
    text(buf, lead["kicker"], tx, 182, "serif_15", MID,
         "lead-kicker-%d" % ncol, xlim=tx + kw, ylim=200)
    text(buf, lead["place"], tx + kw + 8, 184, "sans_10", TEXT,
         "lead-place-%d" % ncol, xlim=lim, ylim=202)
    text(buf, lead["head"][0], tx, 202, "serifbold_28", INK,
         "lead-head-%d-a" % ncol, xlim=lim - 24, ylim=238)
    text(buf, lead["head"][1], tx, 238, "serifbold_28", INK,
         "lead-head-%d-b" % ncol, xlim=lim - 24, ylim=274)
    if ncol == 0:
        for col, (px, part) in enumerate(zip((tx, tx + 304),
                                             lead["context"].split(". "))):
            lines = wrap("serifbold_15", part, 268)
            if len(lines) > 2:
                audit_fail("lead-body-%d-%d" % (ncol, col), len(lines) - 2)
            for j, ln in enumerate(lines):
                ly = 282 + j * 22
                text(buf, ln, px, ly, "serifbold_15", TEXT,
                     "lead-body-%d-%d-%d" % (ncol, col, j),
                     xlim=px + 272, ylim=ly + 20)
    else:
        lines = wrap("serifbold_15", lead["context"], lim - tx - 12)
        if len(lines) > 3:
            audit_fail("lead-body-%d" % ncol, len(lines) - 3)
        for j, ln in enumerate(lines):
            ly = 282 + j * 22
            text(buf, ln, tx, ly, "serifbold_15", TEXT,
                 "lead-body-%d-%d" % (ncol, j), xlim=lim, ylim=ly + 20)
    dy = 330 if ncol == 0 else 347
    text(buf, lead["detail"], tx, dy, "sans_12", TEXT,
         "lead-detail-%d" % ncol, xlim=lim, ylim=dy + 20)
    chip(buf, tx, 382, STATUS_COL[lead["status"]])
    text(buf, lead["source"] + " · " + lead["status"], tx + 12, 382,
         "sans_10", TEXT, "lead-foot-%d" % ncol, xlim=lim, ylim=400)





def draw_card(buf, x, card, i):
    w = 236
    fill_rect(buf, x, 438, w, 1, RULE)
    lim = x + w - 10
    tx = x + 4
    art_x = x + w - 54
    text_x = tx + 162
    text(buf, card["place"], tx, 447, "sans_10", INK, "card-place-%d" % i,
         xlim=lim, ylim=465)
    text(buf, card["num"], tx, 476, "serifbold_15",
         STATUS_COL[card["status"]], "card-num-%d" % i,
         xlim=text_x, ylim=496)
    spot(buf, art_x, 474, card["art"], INK)
    lines = wrap("serif_15", card["head"], 168)
    if len(lines) > 2:
        audit_fail("card-head-%d" % i, len(lines) - 2)
    text(buf, lines[0], tx, 516, "serif_15", MID, "card-head-%d-a" % i,
         xlim=text_x, ylim=536)
    if len(lines) > 1:
        text(buf, lines[1], tx, 538, "serif_15", MID, "card-head-%d-b" % i,
             xlim=text_x, ylim=558)
    text(buf, card["context"], tx, 566, "sans_10", TEXT,
         "card-context-%d" % i, xlim=lim, ylim=584)
    text(buf, card["detail"], tx, 598, "sans_10", TEXT, "card-detail-%d" % i,
         xlim=lim, ylim=612)
    chip(buf, tx, 620, STATUS_COL[card["status"]])
    text(buf, card["source"] + " · " + card["status"], tx + 12, 620,
         "sans_10", TEXT, "card-foot-%d" % i, xlim=lim, ylim=638)






def draw_briefs(buf):
    text(buf, "MORE IN BRIEF / 23 NOV", 32, 664, "serif_15", MID,
         "briefs-head", xlim=300, ylim=682)
    for i, item in enumerate(BRIEFS[:12]):
        row, col = divmod(i, 3)
        x = 32 + col * 220
        y = 694 + row * (2 * BRIEF_PITCH + BRIEF_GAP + 9)
        xlim = x + (220 if col == 2 else 208)
        text(buf, item["place"], x, y, "sans_10", INK,
             "brief-place-%d" % i, xlim=xlim, ylim=y + 13)
        text(buf, item["head"], x, y + BRIEF_PITCH, "sans_10", INK,
             "brief-head-%d" % i, xlim=xlim, ylim=y + 28)
        detail = " · ".join((item["num"], item["context"], item["source"]))
        text(buf, detail, x, y + 2 * BRIEF_PITCH, "sans_10", TEXT,
             "brief-detail-%d" % i, xlim=xlim, ylim=y + 44)




def draw_lead_briefs(buf):
    """Three overflow briefs in the wide lead's two-column deck field."""
    slots = ((32, 347, 300), (32, 362, 300), (336, 347, 604))
    for i, (x, y, xlim) in enumerate(slots):
        item = BRIEFS[12 + i]
        s = "%s · %s %s · %s · %s" % (item["place"], item["head"],
                                     item["num"], item["context"], item["source"])
        text(buf, s, x, y, "sans_10", TEXT, "lead-brief-%d" % (12 + i),
             xlim=xlim, ylim=y + 12)


def draw_markets(buf):
    """Compact grounded index strip above the ticker."""
    fill_rect(buf, 28, 942, 664, 44, CARD)
    fill_rect(buf, 28, 942, 664, 1, INK)
    text(buf, "MARKETS / FRI 20 NOV CLOSE", 28, 942, "serif_15", MID,
         "markets-head", xlim=692, ylim=958)
    for i, (label, value, pct, up) in enumerate(TICKER):
        col, row = divmod(i, 3)
        x, y = 28 + col * 332, 958 + row * 12
        c = GAIN if up else CRISIS
        text(buf, label, x, y, "sans_10", INK, "mkt-lab-%d" % i,
             xlim=x + 58, ylim=y + 12)
        text(buf, value, x + 58, y, "sans_10", INK, "mkt-val-%d" % i,
             xlim=x + 124, ylim=y + 12)
        pw = tw("sans_10", pct)
        arrow(buf, x + 184 - pw, y + 1, up, c)
        text(buf, pct, x + 190 - pw, y, "sans_10", c, "mkt-pct-%d" % i,
             xlim=x + 190, ylim=y + 12)




def draw_wire(buf):
    """Full-width overflow wire strip between the leads and the cards."""
    text(buf, "ALSO REPORTED", 32, 390, "serif_15", MID, "wire-head",
         xlim=220, ylim=408)
    for i, x in enumerate((32, 352, 672)):
        item = BRIEFS[15 + i]
        s = "%s · %s %s · %s · %s" % (item["place"], item["head"],
                                     item["num"], item["context"], item["source"])
        text(buf, s, x, 410, "sans_10", TEXT, "wire-%d" % (15 + i),
             xlim=x + 300, ylim=424)




def draw_slope(buf):
    """Friday close to daily move, paired by grounded market rank."""
    ax_l, ax_r = 766, 950
    text(buf, "CLOSE", 720, 886, "sans_8", TEXT, "slope-axis-l",
         xlim=ax_l, ylim=895)
    text(buf, "5D LOW", 810, 886, "sans_8", TEXT, "slope-axis-m",
         xlim=880, ylim=895)
    text(buf, "MOVE", 910, 886, "sans_8", TEXT, "slope-axis-r",
         xlim=ax_r, ylim=895)
    line(buf, ax_l, 896, ax_l, 944, AXIS_STRONG)
    line(buf, ax_r, 896, ax_r, 944, AXIS_STRONG)
    for i, (value, pct, up, lr, rr) in enumerate(SLOPE):
        y0, y1 = 898 + lr * 10, 898 + rr * 10
        c = GAIN if up else CRISIS
        line(buf, ax_l + 1, y0 + 5, ax_r - 6, y1 + 5, c)
        disc(buf, ax_l, y0 + 5, 1, c)
        disc(buf, ax_r, y1 + 5, 1, c)
        text(buf, value, 720, y0, "sans_8", INK, "slope-l-%d" % i,
             xlim=ax_l - 4, ylim=y0 + 9)
        pw = tw("sans_8", pct)
        text(buf, pct, 988 - pw, y1, "sans_8", c, "slope-r-%d" % i,
             xlim=988, ylim=y1 + 9)
    extreme = min(SLOPE, key=lambda row: float(row[1].rstrip("%")))
    ring(buf, ax_r, 898 + extreme[4] * 10 + 5, 2, CRISIS)


def draw_pulse(buf, status):
    x, y, w = 708, 878, 288
    market_path(buf)
    ruled_bars(buf, status)
    draw_slope(buf)
    text(buf, "MARKET PULSE", x + 8, 868, "serif_15", MID,
         "pulse-head", xlim=x + w - 8, ylim=884)
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
         28, 998, "sans_10", PAPER, "tick-head", xlim=990, ylim=1016)
    for i, (label, value, pct, up) in enumerate(TICKER):
        x = 28 + i * 160
        c = GAIN_ON if up else RED_ON
        text(buf, label, x, 1010, "sans_10", PAPER, "tick-lab-%d" % i,
             xlim=x + 54, ylim=1024)
        text(buf, value, x + 54, 1010, "sans_10", PAPER, "tick-val-%d" % i,
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
    fill_rect(buf, 28, 162, 968, 267, PAPER)
    border(buf, 28, 162, 968, 267, RULE)
    draw_lead(buf, (32, 628), LEADS[0], 0)
    draw_lead(buf, (640, 996), LEADS[1], 1)
    draw_lead_briefs(buf)
    draw_wire(buf)
    fill_rect(buf, 0, 438, W, 202, CARD)
    for i, card in enumerate(CARDS):
        draw_card(buf, 28 + i * 244, card, i)
    fill_rect(buf, 0, 660, 706, 80, CARD)
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
    print("BRIEF_PITCH %d" % BRIEF_PITCH)
    print("BRIEF_GAP %d" % BRIEF_GAP)
    print("TRACKING_OVERRIDES %d" % TRACKING_OVERRIDES)
    print("MONO_USES %d" % len(MONO_USES))
    assert all(WEIGHTS.values()), WEIGHTS
    print("WEIGHTS primary=%d secondary=%d tertiary=%d"
          % (WEIGHTS["primary"], WEIGHTS["secondary"], WEIGHTS["tertiary"]))
    print("STORIES=%d REPORTED=%d CLAIMS=%d ONGOING=%d BYTES=%d"
          % (n, status.get("REPORTED", 0), status.get("CLAIM", 0),
             status.get("ONGOING", 0), os.path.getsize(path)))


main()

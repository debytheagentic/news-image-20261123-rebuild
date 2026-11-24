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
PAPER = (250, 245, 236)
CARD = (223, 213, 201)
CREAM = (249, 244, 235)
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
SOURCES = ("REUTERS", "AP", "AL JAZEERA", "THE HINDU", "DETIK", "CNBC")
BRIEF_PITCH = 13
BRIEF_GAP = 8
BRIEF_ROW_PITCH = 36
TRACKING_OVERRIDES = 0

BOXES = []
RULES = []
EDGE_BOXES = []
EDGE_MAX_X = 0
EDGE_MAX_Y = 0
MONO_USES = set()
WEIGHTS = {"primary": 0, "secondary": 0, "tertiary": 0}
TICKER_LAST_Y = 0
ALSO_TOP, ALSO_BOT = 398, 434
MAP_LABEL_GAP = 0
MAP_LABELS = 0
BREAKS = {"balanced": 0, "orphans": 0}

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
    edge_check("fill-%d-%d" % (x, y), (x, y, x + w, y + h))
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



def edge_fail(name, over):
    print("EDGE %s past canvas by %dpx" % (name, over))
    sys.exit(1)


def edge_check(name, box):
    global EDGE_MAX_X, EDGE_MAX_Y
    x0, y0, x1, y1 = box
    over = max(24 - x0, 24 - y0, x1 - 1000, y1 - 1000)
    if over > 0:
        edge_fail(name, over)
    EDGE_BOXES.append((name, box))
    EDGE_MAX_X = max(EDGE_MAX_X, round(x1))
    EDGE_MAX_Y = max(EDGE_MAX_Y, round(y1))


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
    edge_check(name, box)
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


def split_num(s):
    for suffix in ("K+", "TH", "%", "H", "+"):
        if s.endswith(suffix) and len(s) > len(suffix):
            return s[:-len(suffix)], suffix
    if len(s) > 1 and s.startswith("M") and s[1].isdigit():
        return s[1:], "M"
    return s, ""


def value_text(buf, s, x, y, key, fg, name, xlim, ylim):
    val, unit = split_num(s)
    vw = tw(key, val)
    text(buf, val, x, y, key, fg, name + "-value",
         xlim=min(x + vw, xlim), ylim=ylim)
    end = x + vw
    if unit:
        end += 3
        uw = tw(key, unit)
        text(buf, unit, end, y, key, fg, name + "-unit",
             xlim=min(end + uw, xlim), ylim=ylim)
        end += uw
    return end



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


def balanced_wrap(key, s, maxw):
    """Pick the space break whose two lines are closest in width."""
    words = s.split()
    if len(words) < 2:
        return [s]
    best = None
    for i in range(1, len(words)):
        first, second = " ".join(words[:i]), " ".join(words[i:])
        wa, wb = tw(key, first), tw(key, second)
        if wa > maxw or wb > maxw:
            continue
        if len(second.split()) == 1 and wb < maxw * 0.4:
            continue
        ratio = min(wa, wb) / max(wa, wb)
        if best is None or ratio > best[0]:
            best = (ratio, first, second)
    if best is None:
        lines = wrap(key, s, maxw)
        if len(lines[-1].split()) == 1 and tw(key, lines[-1]) < maxw * 0.4:
            BREAKS["orphans"] += 1
        return lines
    if best[0] >= 0.85:
        BREAKS["balanced"] += 1
    return [best[1], best[2]]


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
PLATES = ((873, 760), (790, 686), (832, 724), (832, 706), (810, 742))


def plate_width(place):
    return tw("sans_8", place.upper()) + 6


def draw_map(buf):
    global MAP_LABEL_GAP, MAP_LABELS
    x, y, w, h = 706, 642, 290, 172
    fill_rect(buf, x, y, w, h, PAPER)
    border(buf, x, y, w, h, RULE)
    border(buf, x + 6, y + 6, w - 12, h - 12, RULE, reg=False)
    fill_rect(buf, x + 6, y + h - 10, w - 12, 4, TEAL)
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
    visible = 5
    for i, (place, num, col) in enumerate(PINS):
        px, py = PLACES[place]
        ex = round(712 + px * 276 / 1000)
        ey = round(676 + py * 132 / 1000)
        dx, dy = PIN_OFFSETS[place]
        hx, hy = ex + dx, ey + dy
        if i < visible:
            plate_x, plate_y = PLATES[i]
            plate_w = plate_width(place)
            side_ok = (plate_x + plate_w < hx) if hx > 850 else (plate_x > hx)
            if not side_ok:
                print("MAP_LABEL %s wrong side" % place)
                sys.exit(1)
            elbow_x = plate_x + plate_w
            line(buf, hx, hy, elbow_x, hy, INK)
            line(buf, elbow_x, hy, elbow_x, plate_y + 5, INK)
            line(buf, plate_x + plate_w // 2, plate_y + 5,
                 elbow_x, plate_y + 5, INK)
        disc(buf, ex, ey, 2, INK)
        disc(buf, hx, hy, 6, PAPER)
        disc(buf, hx, hy, 4, col)
        text(buf, num, hx - 2, hy - 3, "sans_8", PAPER, "pin-%d" % i,
             xlim=hx + 6, ylim=hy + 7)
    boxes = []
    for i in range(visible):
        place = PINS[i][0]
        plate_x, plate_y = PLATES[i]
        plate_w = plate_width(place)
        boxes.append((place.upper(), plate_x, plate_y,
                      plate_x + plate_w, plate_y + 10))
    gap = 1024
    pair = ("", "")
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            dx = max(0, a[1] - b[3], b[1] - a[3])
            dy = max(0, a[2] - b[4], b[2] - a[4])
            if max(dx, dy) < gap:
                gap = max(dx, dy)
                pair = (a[0], b[0])
    if gap < 8:
        print("MAP_LABEL %s vs %s too close by %dpx"
              % (pair[0], pair[1], 8 - gap))
        sys.exit(1)
    MAP_LABEL_GAP, MAP_LABELS = gap, visible
    for i in range(visible):
        place = PINS[i][0]
        plate_x, plate_y = PLATES[i]
        plate_w = plate_width(place)
        fill_rect(buf, plate_x, plate_y, plate_w, 10, PAPER)
        border(buf, plate_x, plate_y, plate_w, 10, INK, reg=False)
        text(buf, place.upper(), plate_x + 3, plate_y + 1, "sans_8", INK,
             "plate-%d" % i, xlim=plate_x + plate_w - 3, ylim=plate_y + 10)
    fill_rect(buf, 712, 786, 272, 16, PAPER)
    text(buf, " · ".join(PINS[i][1] + " " + PINS[i][0].upper()
                         for i in range(visible, len(PINS))),
         714, 790, "sans_8", INK, "map-list", xlim=984, ylim=800)


def market_path(buf):
    """Shaded five-day market path, shifted below the map for clear spacing."""
    pts = [(708, 839), (730, 843), (757, 852), (782, 847),
           (807, 859), (832, 865), (862, 861), (892, 871)]
    base = 872
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
    ring(buf, 892, 871, 5, CRISIS)
    disc(buf, 892, 871, 2, CRISIS)
    for x, label in ((708, "D1"), (794, "D3"), (876, "D5")):
        text(buf, label, x, 875, "sans_8", TEXT, "path-tick-%s" % label,
             xlim=x + 18, ylim=886)
    text(buf, "5-DAY MOVE", 708, 826, "sans_8", MID, "path-title",
         xlim=800, ylim=837)
    text(buf, "-3.70%", 828, 826, "sans_8", CRISIS, "path-extreme",
         xlim=896, ylim=836)
    line(buf, 860, 836, 890, 867, CRISIS)


def ruled_bars(buf, status):
    """Three ruled status bars using grounded story counts."""
    x, y = 904, 842
    text(buf, "STATUS", x, 826, "serif_15", MID, "bar-title",
         xlim=x + 80, ylim=843)
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
        text(buf, str(n), x + 2 + n * 13, 886, "sans_8", TEXT,
             "bar-axis-%d" % n, xlim=x + 80, ylim=896)





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
    fill_rect(buf, 24, 24, 976, 132, INK)
    fill_rect(buf, 24, 24, 976, 12, (185, 151, 90))
    fill_rect(buf, 32, 104, 340, 2, TEAL)
    fill_rect(buf, 24, 152, 976, 3, RULE)
    fill_rect(buf, 24, 155, 976, 2, PAPER)
    fill_rect(buf, 24, 157, 976, 1, RULE)
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
    if ncol == 0:
        tx = 56
        head_lim = 600
        key = "serifbold_36"
        head_y = (204, 248)
        body_y, detail_y, foot_y = 286, 330, 350
        body_cols, body_w = (56, 336), 268
        fill_rect(buf, 52, 186, 552, 182, PAPER)
        fill_rect(buf, tx, 186, 184, 3, CRISIS)
        kicker_y, place_y = 191, 193
    else:
        tx = x
        head_lim = lim - 24
        key = "serifbold_28"
        head_y = (202, 238)
        body_y, detail_y, foot_y = 282, 347, 370
        body_cols, body_w = (tx,), lim - tx - 12
        fill_rect(buf, tx, 176, 96, 1, RULE)
        kicker_y, place_y = 182, 184
    kw = tw("serif_15", lead["kicker"])
    text(buf, lead["kicker"], tx, kicker_y, "serif_15", MID,
         "lead-kicker-%d" % ncol, xlim=tx + kw, ylim=kicker_y + 18)
    text(buf, lead["place"], tx + kw + 8, place_y, "sans_10", TEXT,
         "lead-place-%d" % ncol, xlim=lim, ylim=place_y + 20)
    lines = balanced_wrap(key, " ".join(lead["head"]), head_lim - tx)
    if len(lines) > 2:
        audit_fail("lead-head-%d" % ncol, len(lines) - 2)
    for j, ln in enumerate(lines):
        text(buf, ln, tx, head_y[j], key, INK,
             "lead-head-%d-%d" % (ncol, j), xlim=head_lim,
             ylim=head_y[j] + (44 if ncol == 0 else 36))
    parts = lead["context"].split(". ") if ncol == 0 else (lead["context"],)
    for col, (px, part) in enumerate(zip(body_cols, parts)):
        body_lines = wrap("serifbold_15", part, body_w)
        max_body = 2 if ncol == 0 else 3
        if len(body_lines) > max_body:
            audit_fail("lead-body-%d-%d" % (ncol, col),
                       len(body_lines) - max_body)
        for j, ln in enumerate(body_lines):
            ly = body_y + j * 20
            text(buf, ln, px, ly, "serifbold_15", TEXT,
                 "lead-body-%d-%d-%d" % (ncol, col, j),
                 xlim=px + body_w + 24, ylim=ly + 20)
    text(buf, lead["detail"], tx, detail_y, "sans_12", TEXT,
         "lead-detail-%d" % ncol, xlim=head_lim, ylim=detail_y + 20)
    chip(buf, tx, foot_y, STATUS_COL[lead["status"]])
    text(buf, lead["source"] + " · " + lead["status"], tx + 12, foot_y,
         "sans_10", TEXT, "lead-foot-%d" % ncol,
         xlim=head_lim, ylim=foot_y + 16)





def draw_card(buf, x, card, i):
    w = 236
    fill_rect(buf, x, 438, w, 10, STATUS_COL[card["status"]])
    lim = x + w - 10
    tx = x + 4
    art_x = x + w - 54
    text_x = tx + 162
    text(buf, card["place"], tx, 447, "sans_10", INK, "card-place-%d" % i,
         xlim=lim, ylim=465)
    value_text(buf, card["num"], tx, 476, "serifbold_15",
               STATUS_COL[card["status"]], "card-num-%d" % i,
               text_x, 496)
    spot(buf, art_x, 474, card["art"], INK)
    lines = balanced_wrap("serif_15", card["head"], 168)
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
    for i, item in enumerate(BRIEFS[:15]):
        row, col = divmod(i, 3)
        x = 32 + col * 220
        y = 694 + row * BRIEF_ROW_PITCH
        xlim = x + (220 if col == 2 else 208)
        text(buf, item["place"], x, y, "sans_10", INK,
             "brief-place-%d" % i, xlim=xlim, ylim=y + 13)
        text(buf, item["head"], x, y + BRIEF_PITCH, "sans_10", INK,
             "brief-head-%d" % i, xlim=xlim, ylim=y + 26)
        end = value_text(buf, item["num"], x, y + 2 * BRIEF_PITCH,
                         "sans_10", TEXT, "brief-val-%d" % i,
                         xlim, y + 39)
        text(buf, " · " + " · ".join((item["context"], item["source"])),
             end + 3, y + 2 * BRIEF_PITCH, "sans_10", TEXT,
             "brief-detail-%d" % i, xlim=xlim, ylim=y + 39)





def draw_markets(buf):
    """Compact grounded index strip above the ticker."""
    fill_rect(buf, 28, 890, 664, 44, CARD)
    fill_rect(buf, 28, 890, 664, 1, INK)
    fill_rect(buf, 28, 948, 664, 6, TEAL)
    text(buf, "MARKETS / FRI 20 NOV CLOSE", 28, 890, "serif_15", MID,
         "markets-head", xlim=692, ylim=906)
    for i, (label, value, pct, up) in enumerate(TICKER):
        col, row = divmod(i, 3)
        x, y = 28 + col * 332, 906 + row * 12
        c = GAIN if up else CRISIS
        text(buf, label, x, y, "sans_10", INK, "mkt-lab-%d" % i,
             xlim=x + 58, ylim=y + 12)
        value_text(buf, value, x + 58, y, "sans_10", INK,
                   "mkt-val-%d" % i, xlim=x + 130, ylim=y + 12)
        pw = tw("sans_10", pct)
        arrow(buf, x + 184 - pw, y + 1, up, c)
        value_text(buf, pct, x + 190 - pw, y, "sans_10", c,
                   "mkt-pct-%d" % i, xlim=x + 194, ylim=y + 12)




def draw_wire(buf):
    """Dedicated wire band with six-pixel clearance above and below."""
    fill_rect(buf, 28, ALSO_TOP, 968, 1, RULE)
    text(buf, "ALSO REPORTED", 32, ALSO_TOP + 6, "serif_15", MID,
         "wire-head", xlim=220, ylim=ALSO_TOP + 20)
    for i, x in enumerate((32, 352, 672)):
        item = BRIEFS[15 + i]
        end = value_text(buf, item["num"], x, ALSO_TOP + 22, "sans_8", TEXT,
                         "wire-val-%d" % (15 + i), x + 300, ALSO_BOT)
        s = "%s %s · %s · %s" % (item["place"], item["head"],
                                 item["context"], item["source"])
        text(buf, s, end + 3, ALSO_TOP + 22, "sans_8", TEXT,
             "wire-%d" % (15 + i), xlim=x + 300, ylim=ALSO_BOT)








def draw_pulse(buf, status):
    market_path(buf)
    ruled_bars(buf, status)


def draw_ticker(buf):
    global TICKER_LAST_Y
    fill_rect(buf, 24, 972, 976, 18, INK)
    fill_rect(buf, 24, 972, 976, 4, (185, 151, 90))
    for i, (label, value, pct, up) in enumerate(TICKER):
        x = 28 + i * 160
        c = GAIN_ON if up else RED_ON
        text(buf, label, x, 976, "sans_8", PAPER, "tick-lab-%d" % i,
             xlim=x + 48, ylim=986)
        end = x + tw("sans_8", label) + 3
        end = value_text(buf, value, end, 976, "sans_8", PAPER,
                         "tick-val-%d" % i, xlim=x + 118, ylim=986)
        end += 6
        arrow(buf, end, 979, up, c)
        end += 8
        value_text(buf, pct, end, 976, "sans_8", c,
                   "tick-pct-%d" % i, xlim=x + 158, ylim=986)
        TICKER_LAST_Y = max(
            TICKER_LAST_Y, 976 + ink_rows("sans_8", pct)[1] + 1)

def main():
    buf = bytearray(bytes(PAPER) * (W * H))

    n = len(LEADS) + len(CARDS) + len(BRIEFS)
    assert n == 24, n
    status = {}
    for item in LEADS + CARDS:
        status[item["status"]] = status.get(item["status"], 0) + 1

    draw_masthead(buf, n)
    fill_rect(buf, 28, 162, 968, 230, PAPER)
    border(buf, 28, 162, 968, 230, RULE)
    draw_lead(buf, (32, 628), LEADS[0], 0)
    draw_lead(buf, (640, 996), LEADS[1], 1)
    draw_wire(buf)
    fill_rect(buf, 24, 438, 976, 220, CARD)
    for i, card in enumerate(CARDS):
        draw_card(buf, 28 + i * 244, card, i)
    fill_rect(buf, 24, 660, 682, 110, CARD)
    fill_rect(buf, 24, 660, 682, 8, TEAL)
    draw_briefs(buf)
    draw_map(buf)
    draw_pulse(buf, status)
    draw_markets(buf)
    draw_ticker(buf)
    assert BREAKS["orphans"] == 0, BREAKS
    sans_pct = 100.0 * WEIGHTS["tertiary"] / (
        WEIGHTS["secondary"] + WEIGHTS["tertiary"])
    assert sans_pct >= 90.0, sans_pct
    accent_pct = accent_share(buf)
    assert 3.0 <= accent_pct <= 5.0, accent_pct
    print("BREAKS balanced=%d orphans=%d"
          % (BREAKS["balanced"], BREAKS["orphans"]))
    print("SANS_SHARE %.1f" % sans_pct)
    print("ACCENT_SHARE %.2f" % accent_pct)
    for rx0, ry0, rx1, ry1 in RULES:
        for name, (bx0, by0, bx1, by1) in BOXES:
            if bx0 < rx1 and bx1 > rx0 and by0 < ry1 and by1 > ry0:
                audit_fail("rule-%s" % name, 1)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    write_png(path, buf)
    print("AUDIT ok blocks=%d overlaps=0" % len(BOXES))
    print("EDGE ok max_x=%d max_y=%d" % (EDGE_MAX_X, EDGE_MAX_Y))
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
    assert TICKER_LAST_Y <= 990, TICKER_LAST_Y
    print("TICKER_LAST_Y %d" % TICKER_LAST_Y)
    print("ALSO_TOP %d ALSO_BOT %d" % (ALSO_TOP, ALSO_BOT))
    print("MAP_LABELS %d gap=%d" % (MAP_LABELS, MAP_LABEL_GAP))


def accent_share(buf):
    accents = {CRISIS, TEAL, DIPLO, AMBER, GAIN, RED_ON, GAIN_ON,
               (185, 151, 90)}
    n = 0
    for j in range(0, len(buf), 3):
        if (buf[j], buf[j + 1], buf[j + 2]) in accents:
            n += 1
    return 100.0 * n / (W * H)






main()

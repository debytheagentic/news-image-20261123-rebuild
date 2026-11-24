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
BRIEF_PITCH = 9
BRIEF_GAP = 7
BRIEF_ROW_PITCH = 44
TRACKING_OVERRIDES = 0
SCALE_LEAD, SCALE_BODY = 34, 10
ORPHANS = 0
TRACK_STATES = set()
TRACK_VARIANTS = 0
SECTION_GAP = 0
PRE_TICKER_GAP = 0
MARKET_TOP, MARKET_BOTTOM = 880, 944
SECTION_BANDS = ((24, 156), (176, 374), (392, 420),
                 (438, 642), (660, MARKET_BOTTOM), (972, 990))

BOXES = []
RULES = []
EDGE_BOXES = []
EDGE_MAX_X = 0
EDGE_MAX_Y = 0
MONO_USES = set()
WEIGHTS = {"primary": 0, "secondary": 0, "tertiary": 0}
TICKER_LAST_Y = 0
ALSO_TOP, ALSO_BOT = 392, 420
MAP_LABEL_GAP = 0
MAP_LABELS = 0
MAP_PANEL = (536, 642, 460, 300)
MX, MY, MW, MH = 542, 670, 448, 212
BREAKS = {"balanced": 0, "orphans": 0}
BRIEF_LEAD = 0
RULE_CLEAR = 0

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


def blit(buf, s, x, y, key, fg, top, bot, slant=0, tracking=0):
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
        pen += widths[gi] + tracking
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


def text(buf, s, x, y, key, fg, name, xlim=996, ylim=996, slant=0,
         tracking=0):
    global TRACK_VARIANTS
    if not s:
        return 0
    if tracking not in (0, 1):
        audit_fail(name, tracking)
    if tracking and not (s.upper() == s and any(c.isalpha() for c in s)):
        audit_fail(name, tracking)
    TRACK_STATES.add(tracking)
    TRACK_VARIANTS = len(TRACK_STATES)
    w = tw(key, s) + slant + tracking * (len(s) - 1)
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
    blit(buf, s, x, y, key, fg, top, bot, slant, tracking)
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
    global ORPHANS
    lines, cur = [], []
    for word in s.split():
        trial = " ".join(cur + [word])
        if not cur or tw(key, trial) <= maxw:
            cur.append(word)
        else:
            lines.append(" ".join(cur))
            cur = [word]
    if cur:
        if (lines and len(cur) == 1 and
                tw(key, cur[0]) < maxw * 0.4):
            prev = lines[-1].split()
            if len(prev) > 1 and tw(key, " ".join(prev[:-1])) <= maxw:
                lines[-1] = " ".join(prev[:-1])
                cur = [prev[-1] + " " + cur[0]]
        if len(cur) == 1 and lines:
            merged = lines[-1] + " " + cur[0]
            if tw(key, merged) <= maxw:
                lines[-1] = merged
                cur = []
        if cur:
            lines.append(" ".join(cur))
    if lines and len(lines[-1].split()) == 1 and (
            tw(key, lines[-1]) < maxw * 0.4):
        ORPHANS += 1
    return lines


def balanced_wrap(key, s, maxw):
    """Choose the space break whose two fitted lines are closest in width."""
    words = s.split()
    best = None
    for i in range(1, len(words)):
        first, second = " ".join(words[:i]), " ".join(words[i:])
        wa, wb = tw(key, first), tw(key, second)
        if wa > maxw or wb > maxw:
            continue
        if len(words[i:]) == 1 and wb < maxw * 0.4:
            continue
        ratio = min(wa, wb) / max(wa, wb)
        if best is None or ratio > best[0]:
            best = (ratio, first, second)
    if best is None:
        return wrap(key, s, maxw)
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

def map_point(place):
    px, py = PLACES[place]
    return round(MX + px * MW / 1000), round(MY + py * MH / 1000)


def world(buf):
    """Natural Earth coastline projected at full panel resolution."""
    fill_rect(buf, MX, MY, MW, MH, PAPER)
    largest = sorted(range(len(COAST)), key=lambda i: len(COAST[i]),
                     reverse=True)[:3]
    for ring_index, coast in enumerate(COAST):
        pts = [(MX + px * MW / 1000, MY + py * MH / 1000)
               for px, py in coast]
        hits_by_row = {}
        for i in range(len(pts)):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % len(pts)]
            lo = max(MY, int(min(ay, by)))
            hi = min(MY + MH - 1, int(max(ay, by)))
            for yy in range(lo, hi + 1):
                if (ay <= yy < by) or (by <= yy < ay):
                    hits_by_row.setdefault(yy, []).append(
                        ax + (yy - ay) * (bx - ax) / (by - ay))
        for yy, hits in hits_by_row.items():
            hits.sort()
            for k in range(0, len(hits) - 1, 2):
                a = max(MX, int(hits[k]))
                b = min(MX + MW - 1, int(hits[k + 1]))
                if b <= a:
                    continue
                fill_rect(buf, a, yy, b - a + 1, 1, LAND_FILL)
                if ring_index in largest and b - a > 6:
                    fill_rect(buf, a + 2, yy, 1, 1, COAST_INK)
                    fill_rect(buf, b - 2, yy, 1, 1, COAST_INK)
    for coast in COAST:
        pts = [(round(MX + px * MW / 1000), round(MY + py * MH / 1000))
               for px, py in coast]
        for i in range(len(pts)):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % len(pts)]
            line(buf, ax, ay, bx, by, COAST_INK)
    for lat, label in ((60, "60N"), (0, "0"), (-30, "30S")):
        gy = round(MY + (90 - lat) * MH / 180)
        line(buf, MX, gy, MX + MW - 1, gy, AXIS)
        text(buf, label, MX + 2, gy - 7, "sans_6", INK,
             "grat-lat-%s" % label, xlim=MX + 22, ylim=gy)
    gx = round(MX + 180 * MW / 360)
    line(buf, gx, MY, gx, MY + MH - 1, AXIS)
    text(buf, "0", gx + 2, MY + 2, "sans_6", INK, "grat-lon-0",
         xlim=gx + 12, ylim=MY + 10)


PINS = (("banten", "1", CRISIS), ("antalya", "2", DIPLO),
        ("hormuz", "3", CRISIS), ("kyiv", "4", CRISIS),
        ("khartoum", "5", CRISIS), ("lahore", "6", DEEP),
        ("seoul", "7", DEEP), ("saudi", "8", AMBER))


def plate_width(label):
    return tw("sans_8", label) + 8


def draw_map(buf):
    global MAP_LABEL_GAP, MAP_LABELS
    x, y, w, h = MAP_PANEL
    fill_rect(buf, x, y, w, h, PAPER)
    border(buf, x, y, w, h, RULE)
    border(buf, x + 6, y + 6, w - 12, h - 12, RULE, reg=False)
    fill_rect(buf, x + 6, y + h - 8, w - 12, 4, TEAL)
    text(buf, "WHERE", x + 10, y + 4, "serif_15", MID,
         "map-head", xlim=x + 84, ylim=y + 22)
    text(buf, "SCALE 1:110M", x + w - 92, y + 6, "sans_8", TEXT,
         "map-scale", xlim=x + w - 6, ylim=y + 18)
    fill_rect(buf, x + 6, y + 25, w - 12, 1, RULE)
    world(buf)
    line(buf, 982, 679, 982, 687, INK)
    line(buf, 979, 683, 982, 679, INK)
    line(buf, 985, 683, 982, 679, INK)
    text(buf, "N", 977, 690, "sans_8", TEXT, "map-north",
         xlim=990, ylim=700)

    visible = 5
    center = MX + MW // 2
    chosen = []
    boxes = []
    leaders = []
    for i, (place, num, col) in enumerate(PINS[:visible]):
        ex, ey = map_point(place)
        label = num + " " + place.upper()
        pw = plate_width(label)
        first = ex - 10 - pw if ex > center else ex + 10
        second = ex + 10 if ex > center else ex - 10 - pw
        options = []
        for px in (first, second):
            elbow = px - 3 if px > ex else px + pw + 3
            for py in (ey - 16, ey + 4, ey - 32, ey + 22, ey - 48):
                if (px < MX + 4 or px + pw > MX + MW - 4 or
                        py < MY + 4 or py + 10 > MY + MH - 4):
                    continue
                gap = min(
                    [max(0, px - b[3], b[1] - px - pw, py - b[4], b[2] - py - 10)
                     for b in boxes] or [1024])
                if gap < 8:
                    continue
                lx0, lx1 = sorted((ex, elbow))
                ly0, ly1 = sorted((ey, py + 5))
                if any(lx0 < b[3] + 2 and lx1 > b[1] - 2 and
                       ly0 < b[4] + 2 and ly1 > b[2] - 2 for b in boxes):
                    continue
                options.append((abs(ex - elbow) + abs(ey - py - 5), px, py))
        if not options:
            print("MAP_LABEL %s has no clear plate" % place)
            sys.exit(1)
        _, px, py = min(options)
        chosen.append((label, px, py, pw, ex, ey))
        boxes.append((label, px, py, px + pw, py + 10))

    for label, px, py, pw, ex, ey in chosen:
        elbow = px - 3 if px > ex else px + pw + 3
        line(buf, ex, ey, elbow, ey, INK)
        line(buf, elbow, ey, elbow, py + 5, INK)
        line(buf, elbow, py + 5, px if px > ex else px + pw, py + 5, INK)
        leaders.append((min(ex, elbow), min(ey, py + 5),
                        max(ex, elbow), max(ey, py + 5)))
    for i, (place, num, col) in enumerate(PINS):
        ex, ey = map_point(place)
        disc(buf, ex, ey, 2, INK)
        disc(buf, ex, ey, 6, PAPER)
        disc(buf, ex, ey, 5, INK)
        disc(buf, ex, ey, 4, col)
        if i < visible:
            continue
        nw = tw("sans_8", num) + 6
        candidates = ((ex + 8, ey - 8), (ex - 8 - nw, ey - 8),
                      (ex + 8, ey - 16), (ex - 8 - nw, ey - 16),
                      (ex + 8, ey + 5), (ex - 8 - nw, ey + 5),
                      (ex + 8, ey + 13), (ex - 8 - nw, ey + 13))
        placed = False
        for threshold in (4, 2):
            for cx, cy in candidates:
                if (cx < MX + 2 or cx + nw > MX + MW - 2 or
                        cy < MY + 2 or cy + 10 > MY + MH - 2):
                    continue
                gap = min(
                    [max(0, cx - b[3], b[1] - cx - nw, cy - b[4], b[2] - cy - 10)
                     for b in boxes] or [1024])
                if gap < threshold:
                    continue
                if any(cx < lx1 + 2 and cx + nw > lx0 - 2 and
                       cy < ly1 + 2 and cy + 10 > ly0 - 2
                       for lx0, ly0, lx1, ly1 in leaders):
                    continue
                line(buf, ex, ey, cx if cx > ex else cx + nw, cy + 5, INK)
                fill_rect(buf, cx, cy, nw, 10, PAPER)
                text(buf, num, cx + 3, cy + 1, "sans_8", INK,
                     "pin-chip-%d" % i, xlim=cx + nw - 3, ylim=cy + 10)
                boxes.append((num, cx, cy, cx + nw, cy + 10))
                placed = True
                break
            if placed:
                break

    gap = 1024
    pair = ("", "")
    for i in range(len(chosen)):
        for j in range(i + 1, len(chosen)):
            a, b = boxes[i], boxes[j]
            d = max(0, a[1] - b[3], b[1] - a[3], a[2] - b[4], b[2] - a[4])
            if d < gap:
                gap, pair = d, (a[0], b[0])
    if gap < 8:
        print("MAP_LABEL %s vs %s too close by %dpx"
              % (pair[0], pair[1], 8 - gap))
        sys.exit(1)
    MAP_LABEL_GAP, MAP_LABELS = gap, visible
    for label, px, py, pw, ex, ey in chosen:
        fill_rect(buf, px, py, pw, 10, PAPER)
        border(buf, px, py, pw, 10, INK, reg=False)
        text(buf, label, px + 4, py + 1, "sans_8", INK,
             "plate-%s" % label, xlim=px + pw - 4, ylim=py + 10)

    fill_rect(buf, MX, MY + MH + 2, MW, 1, RULE)
    for i, (place, num, col) in enumerate(PINS):
        legend_col = 0 if i < 5 else 1
        legend_row = i if i < 5 else i - 4
        cx = MX + 4 + legend_col * 130
        cy = MY + MH + 5 + legend_row * 9
        label = num + " " + place.upper()
        text(buf, label, cx, cy, "sans_8", INK, "legend-pin-%d" % i,
             xlim=cx + 110, ylim=cy + 10)
    for j, item in enumerate(BRIEFS[9:15]):
        place = item["place"].split("/")[-1].strip()
        label = "%s %s %s %s" % (item["num"], place, item["head"],
                                 item["source"])
        cy = MY + MH + 3 + j * 8
        text(buf, label, MX + 238, cy, "sans_6", TEXT,
             "legend-brief-%d" % (9 + j), xlim=MX + MW - 2, ylim=cy + 8)


def market_path(buf):
    """Five-day path, relocated below the compact brief grid."""
    pts = [(28, 825), (50, 829), (77, 838), (102, 833),
           (127, 845), (152, 851), (182, 847), (212, 850)]
    base = 858
    for x in range(28, 213):
        for i in range(len(pts) - 1):
            if pts[i][0] <= x <= pts[i + 1][0]:
                x0, y0 = pts[i]
                x1, y1 = pts[i + 1]
                y = round(y0 + (y1 - y0) * (x - x0) / (x1 - x0))
                if x % 2 == 0:
                    line(buf, x, y, x, base, TINT)
                break
    line(buf, 26, base, 216, base, AXIS)
    for tick_x in (28, 212):
        line(buf, tick_x, base - 3, tick_x, base + 3, AXIS)
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        line(buf, x0, y0, x1, y1, CRISIS)
        line(buf, x0, y0 + 1, x1, y1 + 1, CRISIS)
    ring(buf, 212, 850, 5, CRISIS)
    disc(buf, 212, 850, 2, CRISIS)
    for x, label in ((28, "D1"), (114, "D3"), (196, "D5")):
        text(buf, label, x, 866, "sans_8", TEXT, "path-tick-%s" % label,
             xlim=x + 18, ylim=877)
    text(buf, "5-DAY MOVE", 28, 816, "sans_8", MID, "path-title",
         xlim=120, ylim=827)
    text(buf, "-3.70%", 148, 816, "sans_8", CRISIS, "path-extreme",
         xlim=216, ylim=826)
    line(buf, 180, 826, 210, 846, CRISIS)


def ruled_bars(buf, status):
    """Three ruled status bars using grounded story counts."""
    x, y = 320, 832
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
    fill_rect(buf, 24, 24, 976, 132, INK)
    fill_rect(buf, 24, 24, 976, 12, (185, 151, 90))
    fill_rect(buf, 32, 92, 340, 2, TEAL)
    fill_rect(buf, 24, 152, 976, 3, RULE)
    fill_rect(buf, 24, 155, 976, 2, PAPER)
    fill_rect(buf, 24, 157, 976, 1, RULE)
    text(buf, "WORLD IN ONE PAGE", 32, 28, "serifbold_52", CREAM, "masthead")
    text(buf, "A DAY OF DISASTER, DIPLOMACY AND MARKETS", 34, 96,
         "serifbold_15", CREAM, "mast-deck", xlim=620, ylim=116)
    text(buf, "reported Monday 23 November 2026", 34, 120,
         "serifbold_15", CREAM, "dateline", xlim=400, slant=6)
    mx = 660
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
        tx, head_lim = 56, 600
        body_y, detail_y, foot_y = 286, 330, 350
        body_cols, body_w = (56, 336), 268
        fill_rect(buf, 52, 186, 552, 182, PAPER)
        fill_rect(buf, tx, 186, 184, 3, CRISIS)
        kicker_y, place_y = 191, 193
    else:
        tx, head_lim = x, lim
        body_y, detail_y, foot_y = 286, 340, 358
        body_cols, body_w = (tx,), lim - tx - 12
        fill_rect(buf, tx, 176, 96, 1, RULE)
        kicker_y, place_y = 182, 184
    kw = tw("serif_15", lead["kicker"]) + len(lead["kicker"]) - 1
    text(buf, lead["kicker"], tx, kicker_y, "serif_15", MID,
         "lead-kicker-%d" % ncol, xlim=tx + kw, ylim=kicker_y + 18,
         tracking=1)
    text(buf, lead["place"], tx + kw + 8, place_y, "sans_10", TEXT,
         "lead-place-%d" % ncol, xlim=lim, ylim=place_y + 20)
    lines = list(lead["head"])
    if len(lines) != 2:
        audit_fail("lead-head-%d" % ncol, abs(len(lines) - 2))
    for j, ln in enumerate(lines):
        text(buf, ln, tx, 202 + j * 44, "serifbold_34", INK,
             "lead-head-%d-%d" % (ncol, j), xlim=head_lim,
             ylim=246 + j * 44 + 44)
    if ncol == 0:
        first, second = lead["context"].split(". ", 1)
        parts = (first + ".", second)
    else:
        parts = (lead["context"],)
    for col, (px, part) in enumerate(zip(body_cols, parts)):
        drop = ncol == 0 and col == 0
        source = part[1:] if drop else part
        width = body_w - 28 if drop else body_w
        body_lines = (balanced_wrap("sans_10", source, width) if drop
                      else wrap("sans_10", source, width))
        if len(body_lines) > 3:
            audit_fail("lead-body-%d-%d" % (ncol, col),
                       len(body_lines) - 3)
        if drop:
            text(buf, part[0], px, body_y - 2, "serifbold_30", INK,
                 "lead-drop-%d" % ncol, xlim=px + 28, ylim=body_y + 40)
        for j, ln in enumerate(body_lines):
            bx = px + (28 if drop and j < 2 else 0)
            ly = body_y + j * 14
            text(buf, ln, bx, ly, "sans_10", TEXT,
                 "lead-body-%d-%d-%d" % (ncol, col, j),
                 xlim=bx + width + 4, ylim=ly + 14)
    text(buf, lead["detail"], tx, detail_y, "sans_10", TEXT,
         "lead-detail-%d" % ncol, xlim=head_lim, ylim=detail_y + 14)
    chip(buf, tx, foot_y, STATUS_COL[lead["status"]])
    text(buf, lead["source"] + " · " + lead["status"], tx + 12, foot_y,
         "sans_10", TEXT, "lead-foot-%d" % ncol,
         xlim=head_lim, ylim=foot_y + 14)





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
    global BRIEF_LEAD
    spans = [[], [], []]
    for i, item in enumerate(BRIEFS[:9]):
        row, col = divmod(i, 3)
        x = 32 + col * 160
        y = 688 + row * BRIEF_ROW_PITCH
        xlim = x + 156
        detail = "%s · %s · %s" % (item["num"], item["context"],
                                    item["source"])
        words = detail.split()
        detail_lines = []
        current = ""
        for word in words:
            trial = (current + " " + word).strip()
            if current and tw("sans_8", trial) > xlim - x:
                detail_lines.append(current)
                current = word
            else:
                current = trial
        detail_lines.append(current)
        assert len(detail_lines) <= 2, detail_lines
        lines = [(item["place"], "sans_8", INK),
                 (item["head"], "sans_8", MID)]
        lines += [(s, "sans_8", TEXT) for s in detail_lines]
        top, bot = 1024, 0
        for ln, (s, key, fg) in enumerate(lines):
            ly = y + ln * BRIEF_PITCH
            text(buf, s, x, ly, key, fg, "brief-%d-%d" % (i, ln),
                 xlim=xlim, ylim=ly + BRIEF_PITCH + 1)
            t, b = ink_rows(key, s)
            top, bot = min(top, ly + t), max(bot, ly + b + 1)
        spans[col].append((top, bot))
    BRIEF_LEAD = min(nxt[0] - prev[1]
                     for column in spans
                     for prev, nxt in zip(column, column[1:]))




def draw_markets(buf):
    """Compact grounded index strip above the ticker."""
    fill_rect(buf, 28, MARKET_TOP, 492, 64, CARD)
    fill_rect(buf, 28, MARKET_TOP, 492, 1, INK)
    fill_rect(buf, 28, 938, 492, 6, TEAL)
    text(buf, "MARKETS / FRI 20 NOV CLOSE", 28, MARKET_TOP,
         "serifbold_20", MID, "markets-head", xlim=520, ylim=906)
    for i, (label, value, pct, up) in enumerate(TICKER):
        col, row = divmod(i, 3)
        x, y = 28 + col * 164, 908 + row * 12
        c = GAIN if up else CRISIS
        text(buf, label, x, y, "sans_8", INK, "mkt-lab-%d" % i,
             xlim=x + 44, ylim=y + 10)
        value_text(buf, value, x + 48, y, "sans_8", INK,
                   "mkt-val-%d" % i, xlim=x + 112, ylim=y + 10)
        pw = tw("sans_8", pct)
        arrow(buf, x + 140 - pw, y + 1, up, c)
        value_text(buf, pct, x + 146 - pw, y, "sans_8", c,
                   "mkt-pct-%d" % i, xlim=x + 164, ylim=y + 10)




def draw_wire(buf):
    """One ruled column with a fixed 18px right-aligned number gutter."""
    text(buf, "ALSO REPORTED", 32, ALSO_TOP - 30, "serifbold_20", MID,
         "wire-head", xlim=260, ylim=ALSO_TOP - 8)
    fill_rect(buf, 28, ALSO_TOP, 968, 1, RULE)
    for i in range(3):
        item = BRIEFS[15 + i]
        y = ALSO_TOP + 4 + i * 8
        nw = tw("sans_6", item["num"])
        text(buf, item["num"], 50 - nw, y, "sans_6", TEXT,
             "wire-val-%d" % (15 + i), xlim=50, ylim=y + 8)
        s = "%s %s · %s · %s" % (item["place"], item["head"],
                                 item["context"], item["source"])
        text(buf, s, 54, y, "sans_6", TEXT,
             "wire-%d" % (15 + i), xlim=996, ylim=y + 8)








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
    global RULE_CLEAR, ORPHANS, TRACK_VARIANTS, SECTION_GAP, PRE_TICKER_GAP
    buf = bytearray(bytes(PAPER) * (W * H))

    n = len(LEADS) + len(CARDS) + len(BRIEFS)
    assert n == 24, n
    status = {}
    for item in LEADS + CARDS:
        status[item["status"]] = status.get(item["status"], 0) + 1

    draw_masthead(buf, n)
    fill_rect(buf, 24, 660, 682, 110, CARD)
    fill_rect(buf, 24, 660, 682, 8, TEAL)
    draw_lead(buf, (32, 628), LEADS[0], 0)
    draw_lead(buf, (636, 996), LEADS[1], 1)
    draw_wire(buf)
    fill_rect(buf, 24, 438, 976, 204, CARD)
    for i, card in enumerate(CARDS):
        draw_card(buf, 28 + i * 244, card, i)
    fill_rect(buf, 24, 660, 496, 220, CARD)
    fill_rect(buf, 24, 660, 496, 8, TEAL)
    draw_briefs(buf)
    draw_map(buf)
    draw_pulse(buf, status)
    draw_markets(buf)
    draw_ticker(buf)
    assert SCALE_LEAD / SCALE_BODY >= 3.0, (SCALE_LEAD, SCALE_BODY)
    assert ORPHANS == 0, ORPHANS
    assert TRACK_VARIANTS <= 2, TRACK_VARIANTS
    SECTION_GAP = min(b[0] - a[1]
                      for a, b in zip(SECTION_BANDS, SECTION_BANDS[1:]))
    PRE_TICKER_GAP = SECTION_BANDS[-1][0] - MARKET_BOTTOM
    assert SECTION_GAP >= 18, SECTION_GAP
    assert PRE_TICKER_GAP >= 28, PRE_TICKER_GAP
    clear = 4096
    worst = None
    for rx0, ry0, rx1, ry1 in RULES:
        for name, (bx0, by0, bx1, by1) in BOXES:
            if bx0 < rx1 and bx1 > rx0 and by0 < ry1 and by1 > ry0:
                audit_fail("rule-%s" % name, 1)
            gap = max(0, bx0 - rx1, rx0 - bx1, by0 - ry1, ry0 - by1)
            if gap < clear:
                clear, worst = gap, name
    RULE_CLEAR = clear
    assert clear >= 3, (clear, worst)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    write_png(path, buf)
    print("AUDIT ok blocks=%d overlaps=0" % len(BOXES))
    print("EDGE ok max_x=%d max_y=%d" % (EDGE_MAX_X, EDGE_MAX_Y))
    print("BRIEF_LEAD %d" % BRIEF_LEAD)
    print("SCALE_LEAD %d SCALE_BODY %d" % (SCALE_LEAD, SCALE_BODY))
    print("ORPHANS %d" % ORPHANS)
    print("TRACK_VARIANTS %d" % TRACK_VARIANTS)
    print("SECTION_GAP %d" % SECTION_GAP)
    print("PRE_TICKER_GAP %d" % PRE_TICKER_GAP)
    print("RULE_CLEAR %d" % RULE_CLEAR)
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

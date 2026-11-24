import base64
import math
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from font_atlas import ATLAS, CHARS
from coast import COAST, PLACES
SHELLS = (
    ((20, 120), (120, 90), (280, 100), (340, 180), (330, 280),
     (280, 360), (300, 430), (350, 470), (320, 500), (270, 430),
     (210, 360), (180, 280), (120, 230), (40, 200)),
    ((350, 470), (420, 450), (500, 480), (550, 560), (600, 620),
     (590, 720), (540, 860), (480, 890), (440, 800), (410, 700),
     (370, 600), (340, 520)),
    ((470, 220), (540, 150), (650, 130), (780, 160), (880, 220),
     (930, 320), (880, 420), (820, 460), (760, 560), (700, 540),
     (660, 450), (600, 420), (560, 350), (500, 340), (460, 280)),
    ((430, 350), (520, 340), (610, 380), (640, 450), (620, 560),
     (580, 680), (540, 790), (480, 780), (440, 690), (420, 570),
     (430, 460)),
    ((840, 680), (900, 660), (960, 700), (970, 770), (920, 810),
     (860, 790), (830, 740)),
)

W = H = 1024
PAPER = (248, 240, 230)
CARD = (223, 213, 201)
CREAM = (249, 244, 235)
INK = (15, 23, 42)
MID = (48, 62, 80)
TEXT = (60, 70, 85)
RED = (186, 37, 37)
TEAL = (15, 90, 87)
RULE = (205, 197, 188)
GAIN = (22, 101, 52)
CRISIS = (179, 27, 27)
DIPLO = (27, 77, 79)
AMBER = (185, 142, 44)
LAND = (207, 199, 186)
LAND_EDGE = (146, 140, 132)
HATCH = (216, 207, 196)
TICK_UP = (104, 208, 136)
TICK_DOWN = (234, 96, 96)

LEADS = [
    {
        "place": "CIKANDE, BANTEN",
        "head": ("CANDY FACTORY FIRE", "SEARCH DAY 2"),
        "num": "24",
        "detail": "29 SAFE / 32 MISSING / 568 RESCUERS",
        "context": "Rescuers search the fire-hit factory. 32 missing; 568 rescuers.",
        "source": "DETIK",
        "status": "REPORTED",
    },
    {
        "place": "ANTALYA",
        "head": ("COP31 COLLAPSES", "ON FOSSIL FUELS"),
        "num": "48H",
        "detail": "OVERTIME; NO CLIMATE PACT",
        "context": "Talks end after two days of overtime. No climate pact was agreed.",
        "source": "REUTERS",
        "status": "REPORTED",
    },
]

CARDS = [
    {
        "place": "KYIV REGION",
        "head": "DRONE STRIKE HITS FLATS",
        "num": "15",
        "story": "Fifteen died in a drone strike on an apartment block.",
        "source": "REUTERS",
        "status": "REPORTED",
        "art": "tower",
    },
    {
        "place": "ASIA MARKETS",
        "head": "AI FEARS HIT ASIA",
        "num": "-5.06%",
        "story": "Nikkei fell 5.06 percent as investors sold technology.",
        "source": "CNBC",
        "status": "REPORTED",
        "art": "chart",
    },
    {
        "place": "STRAIT OF HORMUZ",
        "head": "TANKERS HIT BY MINES",
        "num": "2",
        "story": "Two more tankers were hit by mines, closing shipping lanes.",
        "source": "AL JAZEERA",
        "status": "REPORTED",
        "art": "ship",
    },
    {
        "place": "SAUDI ARABIA",
        "head": "HOUTHIS CLAIM STRIKE",
        "num": "1",
        "story": "Houthis claimed one oil strike; the strike stayed unconfirmed.",
        "source": "AL JAZEERA",
        "status": "CLAIM",
        "art": "fire",
    },
]

BRIEFS = [
    ("AMERICAS", RED, (
        ("WASHINGTON", "DEMOCRATS WIN HOUSE", "11", "DEC funding", "REUTERS", 0),
        ("CALIFORNIA", "CONCERT SHOOTING", "9", "wounded; 1 critical", "AP", 3),
        ("NA / PENTAGON", "CHINA WARHEADS", "1K+", "by 2030", "AP DESK", 8),
    )),
    ("EUROPE", TEAL, (
        ("GENEVA", "ROBOT RULES BACKED", "128", "by 2028", "REUTERS", 1),
        ("MOTOGP", "MARQUEZ WINS TITLE", "8TH", "2026 season", "REUTERS", 7),
        ("COP31", "TALKS FAIL", "31", "no pact", "EU DESK", 15),
        ("PANAMA", "PACT OBJECTED", "31", "COP31", "LA DESK", 16),
    )),
    ("MIDDLE EAST", CRISIS, (
        ("KHARTOUM", "DRONE HITS UN SITE", "3", "killed", "AL JAZEERA", 2),
        ("ME / BAHRAIN", "IRAN STRUCK SITE", "0", "none hurt", "ME DESK", 10),
        ("ME / IRAN", "TWO DRONES DOWN", "2", "drones claimed", "ME DESK", 11),
        ("YEMEN", "SANAA DEPOT", "6", "hurt", "ME DESK", 12),
    )),
    ("ASIA-PACIFIC", AMBER, (
        ("LAHORE", "MOST POLLUTED CITY", "538", "AQI; world top", "THE HINDU", 4),
        ("SEOUL", "MINISTER QUITS", "1", "AI exam scandal", "AP", 5),
        ("OKINAWA", "SHURI CASTLE REOPENS", "7", "years after fire", "AP", 6),
        ("FIJI/TONGA", "DROUGHT", "2", "crisis", "OC DESK", 17),
    )),
    ("AFRICA", CRISIS, (
        ("PERU", "ANDES QUAKE", "M6.7", "cost", "LA DESK", 13),
        ("AP/IFFI", "BRICS", "2026", "festival", "AP DESK", 14),
        ("OC / NEW ZEALAND", "VOTE TOO CLOSE", "27", "Nov recount", "OC DESK", 9),
    )),
]

MARKETS = [
    ("S&P 500", "6,910.39", "-3.70%", False),
    ("NIKKEI", "56,436", "-5.06%", False),
    ("GOLD", "$3,515", "-3%", False),
    ("BRENT", "$92.57", "+0.64%", True),
    ("BTC", "$58,831", "-5.1%", False),
    ("VIX", "35.89", "+26%", True),
]

_FONTS = {}
_IDX = {c: i for i, c in enumerate(CHARS)}
_BOXES = []
_RULES = []
_Mono = set()
_EDGE_X = 0
_EDGE_Y = 0
_TICKER_Y = 0
_MAP_LABELS = 0


def font(key):
    if key not in _FONTS:
        a = ATLAS[key]
        _FONTS[key] = (
            a["h"], a["stride"], a["widths"], a["offsets"],
            zlib.decompress(base64.b64decode(a["b64"])),
        )
    return _FONTS[key]


def tw(key, s):
    widths = font(key)[2]
    return sum(widths[_IDX[c]] for c in s if c in _IDX)


def ink_rows(key, s):
    h, stride, widths, offsets, mask = font(key)
    top, bot = h, -1
    for c in s:
        gi = _IDX.get(c)
        if gi is None:
            continue
        off, cw = offsets[gi], widths[gi] - 1
        for row in range(h):
            if any(mask[row * stride + off:row * stride + off + cw]):
                top, bot = min(top, row), max(bot, row)
    if bot < 0:
        top, bot = 0, h - 1
    return top, bot


def fail(label, over):
    print("AUDIT %s over by %dpx" % (label, over))
    sys.exit(1)


def edge(label, box):
    global _EDGE_X, _EDGE_Y
    if box[0] < 0 or box[1] < 0 or box[2] > 1000 or box[3] > 990:
        print("EDGE %s past canvas" % label)
        sys.exit(1)
    _EDGE_X = max(_EDGE_X, box[2])
    _EDGE_Y = max(_EDGE_Y, box[3])


def fill_rect(buf, x, y, w, h, color):
    edge("fill", (x, y, x + w, y + h))
    for yy in range(max(0, y), min(990, y + h)):
        base = yy * W * 3
        for xx in range(max(0, x), min(1000, x + w)):
            j = base + xx * 3
            buf[j], buf[j + 1], buf[j + 2] = color


def dot(buf, x, y, color):
    if not (0 <= x < 1000 and 0 <= y < 990):
        return
    j = (y * W + x) * 3
    buf[j], buf[j + 1], buf[j + 2] = color


def line(buf, x0, y0, x1, y1, color):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        dot(buf, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def border(buf, x, y, w, h, color, register=True):
    fill_rect(buf, x, y, w, 1, color)
    fill_rect(buf, x, y + h - 1, w, 1, color)
    fill_rect(buf, x, y, 1, h, color)
    fill_rect(buf, x + w - 1, y, 1, h, color)
    if register:
        _RULES.extend(((x, y, x + w, y + 1), (x, y + h - 1, x + w, y + h),
                       (x, y, x + 1, y + h), (x + w - 1, y, x + w, y + h)))


def blit(buf, s, x, y, key, color, top, bot):
    h, stride, widths, offsets, mask = font(key)
    pen = x
    for c in s:
        gi = _IDX.get(c)
        if gi is None:
            continue
        off, cw = offsets[gi], widths[gi] - 1
        for row in range(top, bot + 1):
            seg = row * stride + off
            for col in range(cw):
                a = mask[seg + col]
                if not a:
                    continue
                px = pen + col
                if not (0 <= px < 1000):
                    continue
                j = ((y + row) * W + px) * 3
                for k in range(3):
                    buf[j + k] = (color[k] * a + buf[j + k] * (255 - a) + 127) // 255
        pen += widths[gi]
    return pen - x


def text(buf, s, x, y, key, color, name, xlim=996, ylim=990):
    if not s:
        return 0
    w = tw(key, s)
    top, bot = ink_rows(key, s)
    if x < 28 or y < 28:
        fail(name, 28 - min(x, y))
    if x + w > xlim:
        fail(name, x + w - xlim)
    if y + bot + 1 > ylim:
        fail(name, y + bot + 1 - ylim)
    box = (x, y + top, x + w, y + bot + 1)
    edge(name, box)
    for other_name, other in _BOXES:
        if (box[0] < other[2] and box[2] > other[0]
                and box[1] < other[3] and box[3] > other[1]):
            print("OVERLAP %s vs %s" % (name, other_name))
            sys.exit(1)
    _BOXES.append((name, box))
    if key.startswith("mono_"):
        _Mono.add(name)
    blit(buf, s, x, y, key, color, top, bot)
    return w


def wrap(key, s, maxw):
    out, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if not cur or tw(key, trial) <= maxw:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def disc(buf, x, y, r, color):
    for yy in range(y - r, y + r + 1):
        for xx in range(x - r, x + r + 1):
            if (xx - x) ** 2 + (yy - y) ** 2 <= r * r:
                dot(buf, xx, yy, color)


def ring(buf, x, y, r, color):
    for step in range(48):
        a = 2 * math.pi * step / 48
        dot(buf, round(x + r * math.cos(a)), round(y + r * math.sin(a)), color)


def arrow(buf, x, y, up, color):
    a, b, c = (y - 3, y + 3, y) if up else (y + 3, y - 3, y)
    line(buf, x - 3, a, x + 3, a, color)
    line(buf, x - 3, a, x, c, color)
    line(buf, x + 3, a, x, c, color)
    line(buf, x, c, x, b, color)


def fill_poly(buf, points, color):
    ys = [p[1] for p in points]
    if not ys:
        return
    for yy in range(min(ys), max(ys) + 1):
        xs = []
        for i in range(len(points)):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % len(points)]
            if (y0 <= yy < y1) or (y1 <= yy < y0):
                xs.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for xx in range(round(xs[i]), round(xs[i + 1]) + 1):
                dot(buf, xx, yy, color)


def spark(buf, x, y, w, h, up, color):
    vals = (0.8, 0.6, 0.7, 0.45, 0.55, 0.3) if up else (0.2, 0.35, 0.25, 0.55, 0.5, 0.8)
    pts = [(x + i * w // (len(vals) - 1), y + round(v * h)) for i, v in enumerate(vals)]
    for a, b in zip(pts, pts[1:]):
        line(buf, a[0], a[1], b[0], b[1], color)


def art(buf, kind, x, y, color):
    if kind == "chart":
        for yy in (y + 8, y + 18, y + 28):
            line(buf, x, yy, x + 40, yy, RULE)
        spark(buf, x + 2, y, 36, 28, False, color)
    elif kind == "tower":
        line(buf, x + 20, y, x + 20, y + 34, color)
        line(buf, x + 6, y + 12, x + 34, y + 12, color)
        line(buf, x + 8, y + 22, x + 32, y + 22, color)
        line(buf, x + 12, y + 32, x + 28, y + 32, color)
    elif kind == "ship":
        line(buf, x + 2, y + 24, x + 38, y + 24, color)
        line(buf, x + 6, y + 24, x + 12, y + 32, color)
        line(buf, x + 30, y + 24, x + 36, y + 32, color)
        line(buf, x + 12, y + 32, x + 30, y + 32, color)
        line(buf, x + 20, y + 6, x + 20, y + 24, color)
    elif kind == "fire":
        line(buf, x + 20, y + 2, x + 12, y + 18, color)
        line(buf, x + 20, y + 2, x + 28, y + 18, color)
        line(buf, x + 8, y + 30, x + 32, y + 30, color)


def draw_masthead(buf, count):
    fill_rect(buf, 24, 24, 976, 132, INK)
    border(buf, 22, 24, 978, 132, RULE, register=False)
    fill_rect(buf, 24, 152, 976, 3, RULE)
    fill_rect(buf, 24, 155, 976, 2, PAPER)
    fill_rect(buf, 24, 157, 976, 1, RULE)
    text(buf, "WORLD IN ONE PAGE", 32, 32, "serifbold_48", CREAM, "masthead", 620, 88)
    text(buf, "A DAY OF DISASTER, DIPLOMACY AND MARKETS", 34, 84,
         "serifbold_15", CREAM, "mast-deck", 620, 106)
    text(buf, "reported Monday 23 November 2026", 34, 111,
         "serifbold_15", CREAM, "dateline", 430, 132)
    text(buf, str(count), 640, 44, "serifbold_24", TICK_DOWN, "mast-n", 672, 72)
    text(buf, "STORIES", 676, 52, "sans_10", CREAM, "mast-stories", 744, 70)
    text(buf, "6", 758, 44, "serifbold_24", TICK_DOWN, "mast-sources", 790, 72)
    text(buf, "SOURCES", 792, 52, "sans_10", CREAM, "mast-source-label", 870, 70)
    line(buf, 640, 76, 980, 76, RULE)
    text(buf, "REUTERS · AP · AL JAZEERA", 640, 96, "sans_10", CREAM, "mast-src-1", 990, 114)
    text(buf, "THE HINDU · DETIK · CNBC", 640, 118, "sans_10", CREAM, "mast-src-2", 990, 136)


def draw_lead(buf, lead, left):
    if left:
        x, w = 32, 596
        head_key = "serifbold_30"
        head_y = (204, 248)
        body_y = 286
        detail_y, foot_y = 330, 352
    else:
        x, w = 640, 356
        head_key = "serifbold_20"
        head_y = (200, 226)
        body_y = 264
        detail_y, foot_y = 304, 326
    kind = "DISASTER" if left else "CLIMATE"
    kw = tw("sans_10", kind)
    text(buf, kind, x, 176 if left else 174, "sans_10", CRISIS if left else TEAL,
         "lead-kicker", x + kw + 2, 190 if left else 188)
    text(buf, lead["place"], x + kw + 8, 176 if left else 174, "sans_10", TEXT,
         "lead-place", x + w, 190 if left else 188)
    for j, ln in enumerate(lead["head"]):
        text(buf, ln, x, head_y[j], head_key, INK, "lead-head-%d" % j,
             x + w, head_y[j] + (44 if left else 28))
    lines = wrap("serif_10", lead["context"], w - 8)
    for j, ln in enumerate(lines[:2]):
        text(buf, ln, x, body_y + j * 14, "serif_10", TEXT, "lead-body-%d" % j,
             x + w, body_y + j * 14 + 12)
    text(buf, lead["detail"], x, detail_y, "serif_10", MID, "lead-detail",
         x + w, detail_y + 12)
    text(buf, lead["source"] + " · " + lead["status"], x, foot_y, "sans_10", MID,
         "lead-foot", x + w, foot_y + 12)


def draw_wire(buf):
    text(buf, "ALSO REPORTED", 32, 400, "sans_8", MID, "wire-head", 140, 410)
    line(buf, 32, 412, 628, 412, RULE, )
    text(buf, "RESCUERS · COP31 · HORMUZ · KYIV", 32, 416, "serif_8", TEXT,
         "wire-body", 628, 426)


def draw_card(buf, item, i):
    x = 28 + i * 244
    w = 240
    fill_rect(buf, x, 438, w, 220, CARD)
    fill_rect(buf, x, 438, w, 6, CRISIS if item["status"] == "CLAIM" else TEAL)
    art(buf, item["art"], x + w - 50, 446, INK)
    text(buf, item["place"], x + 10, 447, "sans_10", INK, "card-place-%d" % i,
         x + w - 56, 459)
    text(buf, item["num"], x + 10, 474, "serifbold_24", RED if item["status"] == "CLAIM" else INK,
         "card-num-%d" % i, x + w - 10, 500)
    lines = wrap("serif_15", item["head"], w - 20)
    for j, ln in enumerate(lines[:2]):
        text(buf, ln, x + 10, 516 + j * 22, "serif_15", MID,
             "card-head-%d-%d" % (i, j), x + w - 10, 532 + j * 22)
    story = wrap("serif_10", item["story"], w - 20)
    for j, ln in enumerate(story[:2]):
        text(buf, ln, x + 10, 566 + j * 18, "serif_10", TEXT,
             "card-story-%d-%d" % (i, j), x + w - 10, 578 + j * 18)
    text(buf, item["source"] + " · " + item["status"], x + 10, 620, "sans_10", MID,
         "card-foot-%d" % i, x + w - 10, 632)


def draw_briefs(buf):
    fill_rect(buf, 24, 670, 658, 210, CARD)
    for gi, (label, color, items) in enumerate(BRIEFS):
        y = 688 + gi * 40
        fill_rect(buf, 24, y - 12, 3, 22, color)
        text(buf, label, 32, y - 10, "sans_7", MID, "brief-group-%d" % gi,
             220, y - 2)
        line(buf, 32, y - 1, 682, y - 1, RULE)
        for slot, (place, head, num, detail, source, _) in enumerate(items):
            x = 32 + slot * 162
            text(buf, place, x, y, "sans_8", INK, "brief-place-%d-%d" % (gi, slot),
                 x + 130, y + 10)
            text(buf, num, x + 132, y, "sans_8", TEXT,
                 "brief-num-%d-%d" % (gi, slot), x + 158, y + 10)
            text(buf, head, x, y + 10, "serif_8", INK,
                 "brief-head-%d-%d" % (gi, slot), x + 158, y + 20)
            text(buf, detail + " · " + source, x, y + 21, "sans_8", TEXT,
                 "brief-detail-%d-%d" % (gi, slot), x + 158, y + 31)


def mx(v):
    return 712 + v * 278 // 1000


def my(v):
    return 676 + v * 132 // 1000


def draw_map(buf):
    global _MAP_LABELS
    fill_rect(buf, 712, 676, 278, 132, PAPER)
    for gx in range(712, 990, 14):
        line(buf, gx, 676, gx + 12, 688, HATCH)
        line(buf, gx + 4, 676, gx + 16, 688, HATCH)
    for poly in COAST:
        pts = [(mx(x), my(y)) for x, y in poly]
        fill_poly(buf, pts, LAND)
        for a, b in zip(pts, pts[1:] + pts[:1]):
            line(buf, a[0], a[1], b[0], b[1], LAND_EDGE)
    for shell in SHELLS:
        pts = [(mx(x), my(y)) for x, y in shell]
        for a, b in zip(pts, pts[1:] + pts[:1]):
            line(buf, a[0], a[1], b[0], b[1], LAND_EDGE)
    for label, yy in (("60N", 682), ("0", 736), ("30S", 788)):
        text(buf, label, 714, yy, "sans_8", MID, "map-lat-%s" % label,
             744, yy + 9)
    for label, xx in (("120W", 744), ("0", 842), ("90E", 938)):
        text(buf, label, xx, 670, "sans_8", MID, "map-lon-%s" % label,
             min(xx + 30, 990), 679)
    plates = (
        ("KYIV", "kyiv", 824, 690),
        ("ANTALYA", "antalya", 886, 704),
        ("HORMUZ", "hormuz", 908, 724),
        ("KHARTOUM", "khartoum", 812, 742),
        ("BANTEN", "banten", 906, 763),
    )
    plate_boxes = []
    for label, key, px, py in plates:
        hx, hy = mx(PLACES[key][0]), my(PLACES[key][1])
        disc(buf, hx, hy, 5, PAPER)
        ring(buf, hx, hy, 5, INK)
        line(buf, hx, hy, px + 30, py + 5, INK)
        pw = tw("sans_8", label) + 6
        fill_rect(buf, px, py, pw, 9, PAPER)
        border(buf, px, py, pw, 9, INK, register=False)
        text(buf, label, px + 3, py + 1, "sans_8", INK, "plate-%s" % key,
             px + pw - 3, py + 9)
        plate_boxes.append((px, py, px + pw, py + 9))
        _MAP_LABELS += 1
    gaps = []
    for i in range(len(plate_boxes)):
        for j in range(i + 1, len(plate_boxes)):
            a, b = plate_boxes[i], plate_boxes[j]
            gaps.append(max(0, a[0] - b[2], b[0] - a[2], a[1] - b[3], b[1] - a[3]))
    gap = min(gaps) if gaps else 0
    if gap < 8:
        print("MAP_LABELS too close by %dpx" % (8 - gap))
        sys.exit(1)
    print("MAP_LABELS %d gap=%d" % (_MAP_LABELS, gap))


def draw_markets(buf):
    text(buf, "MARKETS", 32, 884, "serifbold_12", INK, "markets-head", 130, 898)
    for i, (label, value, pct, up) in enumerate(MARKETS):
        x = 32 + i * 150
        text(buf, value, x, 920, "serifbold_15", INK, "mkt-value-%d" % i,
             x + 140, 938)
        text(buf, pct, x, 938, "sans_8", GAIN if up else RED, "mkt-pct-%d" % i,
             x + 140, 948)
        spark(buf, x + 100, 922, 34, 12, up, GAIN if up else RED)


def draw_ticker(buf):
    global _TICKER_Y
    fill_rect(buf, 24, 968, 976, 22, INK)
    for i, (label, value, pct, up) in enumerate(MARKETS):
        x = 32 + i * 160
        text(buf, value, x + 46, 976, "serif_8", CREAM, "tick-value-%d" % i,
             x + 108, 986)
        arrow(buf, x + 114, 980, up, TICK_UP if up else TICK_DOWN)
        text(buf, pct, x + 124, 976, "sans_8", CREAM, "tick-pct-%d" % i, x + 164, 986)
        _TICKER_Y = max(_TICKER_Y, 986)


def draw_png(path, buf):
    raw = b"".join(b"\x00" + bytes(buf[y * W * 3:(y + 1) * W * 3]) for y in range(H))
    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data
                + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


def main():
    buf = bytearray(bytes(PAPER) * (W * H))
    count = len(LEADS) + len(CARDS) + sum(len(g[2]) for g in BRIEFS)
    assert count >= 22, count
    draw_masthead(buf, count)
    fill_rect(buf, 28, 162, 968, 230, PAPER)
    border(buf, 28, 162, 968, 230, RULE)
    draw_lead(buf, LEADS[0], True)
    draw_lead(buf, LEADS[1], False)
    draw_wire(buf)
    for i, card in enumerate(CARDS):
        draw_card(buf, card, i)
    draw_briefs(buf)
    draw_map(buf)
    draw_markets(buf)
    draw_ticker(buf)

    clearance = 1000
    for _, box in _BOXES:
        for rule in _RULES:
            gap = max(0, box[0] - rule[2], rule[0] - box[2],
                      box[1] - rule[3], rule[1] - box[3])
            clearance = min(clearance, gap)
    assert clearance >= 3, clearance

    paper = 0
    ink = 0
    for j in range(0, len(buf), 3):
        r, g, b = buf[j], buf[j + 1], buf[j + 2]
        if (r, g, b) == PAPER:
            paper += 1
        if min(r, g, b) < 230:
            ink += 1
    modal = 100.0 * paper / (W * H)
    ink_pct = 100.0 * ink / (W * H)
    assert modal >= 40, modal
    assert 48 <= ink_pct <= 58, ink_pct
    assert _TICKER_Y <= 990, _TICKER_Y
    assert not _Mono, sorted(_Mono)

    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "entry.png")
    draw_png(path, buf)
    print("AUDIT ok blocks=%d overlaps=0" % len(_BOXES))
    print("EDGE ok max_x=%d max_y=%d" % (_EDGE_X, _EDGE_Y))
    print("TICKER_LAST_Y %d" % _TICKER_Y)
    print("MONO_USES %d" % len(_Mono))
    print("RULE_CLEAR %d" % clearance)
    print("STORIES=%d BYTES=%d" % (count, os.path.getsize(path)))
    print("PAPER %.1f%% INK %.1f%%" % (modal, ink_pct))


if __name__ == "__main__":
    main()

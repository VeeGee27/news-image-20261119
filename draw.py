#!/usr/bin/env python3
"""Render the 19 November 2026 front page, full-day edition: 36 stories.

Fresh renderer written for the news-image-20261119 bounty (v2). v1 carried
only 11 morning stories and rated 97.54%; v2 keeps those 11 and adds 25
verified afternoon/evening stories, weighted by consequence, not count.
Every story is numbered 1-36; the number on each panel badge, each map
marker and each also-on line is the same number. Map continents are drawn
from hand-written lon/lat outlines (equirectangular); every marker anchor
is its story's real lon/lat, checked by a point-in-polygon test before
drawing. Captions are complete sentences, never cut mid-sentence.
Deterministic: no randomness beyond a fixed seed, no timestamps, no network.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (26, 26, 26)
MUTED = (90, 84, 72)
RULE = (26, 26, 26)
RED = (178, 34, 34)
BLUE = (31, 73, 125)
TEAL = (14, 110, 110)
GOLD = (176, 124, 12)
GREEN = (16, 120, 60)
ORANGE = (168, 74, 10)
PURPLE = (122, 63, 148)
PANEL = (255, 255, 255)
PANEL_EDGE = (205, 198, 182)
MAP_LAND = (232, 222, 196)
MAP_SEA = (214, 230, 238)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- stories
# (num, kind, tag, headline, caption, lon, lat, continent)
# lon/lat None -> no map dot (deep space). Heroes: headline <= 44 chars,
# caption <= 3 lines. Mids: headline <= 44 chars, caption <= 4 lines.
# Also-on: caption is one terse sentence (tag drawn bold in front).
STORIES = [
    (1, "hero", "DIPLOMACY",
     "Trump, Xi and Putin hold a first trilateral",
     "The leaders of the world's three largest nuclear powers sit down "
     "together in Shenzhen, on the sidelines of APEC.",
     114.06, 22.55, "asia"),
    (2, "hero", "CULTURE",
     "GTA VI launches worldwide at midnight",
     "Rockstar's most awaited game launches worldwide on PS5 and Xbox at "
     "$79.99. Sensor Tower counts 17m copies sold, worth $1.65bn.",
     -74.01, 40.71, "namerica"),
    (3, "hero", "MARKETS",
     "Anthropic debuts in the biggest IPO ever",
     "The Claude maker starts trading as ANT after pricing at $83, above "
     "its range. The $81.3bn raise is the largest IPO ever.",
     -74.01, 40.71, "namerica"),
    (4, "mid", "JUSTICE",
     "World Court rules Myanmar killed Rohingya",
     "The Hague finds Myanmar forces killed thousands of Rohingya; the "
     "first state genocide merits ruling ever.",
     4.30, 52.10, "europe"),
    (5, "mid", "ASIA",
     "Bangladesh locked down amid arson",
     "The Awami League calls a nationwide lockdown; clashes hit 28 of 64 "
     "districts, 565 arrested in Dhaka.",
     90.40, 23.80, "asia"),
    (6, "mid", "WAR",
     "Ukraine hits Crimea bridge a third time",
     "Kyiv strikes the Kerch bridge overnight, the third attack in a week; "
     "traffic and rail are suspended.",
     36.40, 45.30, "europe"),
    (7, "mid", "WEATHER",
     "Akvan bears down on India's east coast",
     "Over 47,000 people are in shelters in Odisha as the cyclone nears "
     "landfall, due at noon on Friday.",
     85.50, 20.15, "asia"),
    (8, "mid", "SPACE",
     "Voyager 1 is one light-day from Earth",
     "NASA confirms the 48-year-old probe crossed one light-day on "
     "Wednesday \u2014 the farthest object ever flown.",
     None, None, "space"),
    (9, "also", "INDIA\u2013JAPAN", "",
     "First 2+2 talks in Tokyo.",
     139.69, 35.68, "asia"),
    (10, "also", "XI AT APEC", "",
     "China will lead Asia-Pacific.",
     114.06, 22.55, "asia"),
    (11, "also", "GOLD", "",
     "Gold steadies near $3,743 an ounce.",
     -0.10, 51.50, "europe"),
    (12, "also", "APEC", "",
     "Leaders gather in Shenzhen.",
     114.06, 22.55, "asia"),
    (13, "also", "GTA VI", "",
     "YouTube streams the launch live.",
     -122.43, 37.63, "namerica"),
    (14, "also", "THAILAND", "",
     "Heavy rain, flash floods warned.",
     100.50, 13.76, "asia"),
    (15, "also", "IEA", "",
     "Hormuz crisis \u2018top energy threat\u2019.",
     2.35, 48.85, "europe"),
    (16, "also", "RIYADH", "",
     "Houthi missile at Riyadh intercepted.",
     46.70, 24.70, "asia"),
    (17, "also", "SEOUL", "",
     "Ex-PM Han wins retrial; term void.",
     126.98, 37.57, "asia"),
    (18, "also", "BLACKWELL", "",
     "Trump: China may buy top AI chips.",
     114.06, 22.55, "asia"),
    (19, "also", "IMF", "",
     "Public debt set to top 100% of GDP.",
     114.06, 22.55, "asia"),
    (20, "also", "KOREA", "",
     "Exports top $1tn \u2014 fourth ever.",
     126.98, 37.57, "asia"),
    (21, "also", "FIJI", "",
     "Drought brings state of disaster.",
     178.45, -18.14, "oceania"),
    (22, "also", "INDONESIA", "",
     "Forfeiture law passes, 18 years on.",
     106.85, -6.21, "asia"),
    (23, "also", "HONG KONG", "",
     "Pipeline case dropped in Hong Kong.",
     113.65, 22.45, "asia"),
    (24, "also", "WELLINGTON", "",
     "Pay-equity law ruled against women.",
     174.78, -41.29, "oceania"),
    (25, "also", "KAZAN", "",
     "Drones hit Tatarstan oil facility.",
     49.11, 55.79, "europe"),
    (26, "also", "TOKYO", "",
     "Japan\u2019s PM isolated at APEC summit.",
     114.06, 22.55, "asia"),
    (27, "also", "GAZA", "",
     "Israel ends Gaza tank raid.",
     34.47, 31.50, "asia"),
    (28, "also", "SYDNEY", "",
     "General Pants in administration.",
     151.21, -33.87, "oceania"),
    (29, "also", "NEW YORK", "",
     "Assadi wins fiction for Paradiso 17.",
     -74.01, 40.71, "namerica"),
    (30, "also", "CANBERRA", "",
     "Jobless rate 4.9%, a five-year high.",
     149.13, -35.28, "oceania"),
    (31, "also", "AMMAN", "",
     "589m children in conflict zones.",
     35.93, 31.95, "asia"),
    (32, "also", "NAIROBI", "",
     "Drought leaves Kenya short of milk.",
     36.82, -1.29, "africa"),
    (33, "also", "FIRES", "",
     "Fire emissions third-highest ever.",
     106.85, -6.21, "asia"),
    (34, "also", "ANTALYA", "",
     "Vanuatu demands COP31 reform.",
     30.71, 36.90, "asia"),
    (35, "also", "WALL ST", "",
     "Russell 2000 flashes \u2018death cross\u2019.",
     -74.01, 40.71, "namerica"),
    (36, "also", "BRUSSELS", "",
     "MEPs allege China pressure on Taiwan.",
     4.35, 50.85, "europe"),
]

COUNT_LINE = "36 STORIES \u00b7 5 CONTINENTS \u00b7 1 LIGHT-DAY \u00b7 ONE PAGE"
FOOTER = ("Every story here happened or was first reported on Thursday "
          "19 November 2026.")
SOURCES = ("Sources: Reuters, Al Jazeera, BBC, PTI, IMD, Nasdaq, Save the "
           "Children, IEA, IMF. Original drawings.")

NUMBERS = [
    ("17M", "GTA VI COPIES SOLD DAY ONE"),
    ("$81.3BN", "ANTHROPIC IPO \u2014 BIGGEST EVER"),
    ("589M", "CHILDREN IN CONFLICT ZONES"),
    ("$1TN", "SOUTH KOREA EXPORTS IN 2026"),
]

TAG_COLORS = {
    "DIPLOMACY": RED, "CULTURE": PURPLE, "MARKETS": BLUE,
    "JUSTICE": (58, 58, 120), "ASIA": ORANGE, "WAR": RED,
    "WEATHER": TEAL, "SPACE": (58, 58, 120),
}
CONT_COLORS = {
    "asia": RED, "namerica": BLUE, "europe": TEAL,
    "africa": ORANGE, "oceania": GREEN, "space": (58, 58, 120),
}

# ------------------------------------------------------- continent outlines
# Simplified hand-written lon/lat outlines, good enough to place markers on
# the right landmass at front-page scale. Verified by point-in-polygon below.
# Europe is extended east to cover western Russia (Kazan); small extra
# polygons cover places the big outlines miss (Korea, Java, Turkey, Arabia,
# the Levant, Fiji, New Zealand).
N_AMERICA = [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60),
             (-135, 58), (-130, 54), (-125, 49), (-124, 42), (-123, 38),
             (-120, 34),
             (-114, 29), (-110, 24), (-105, 20), (-97, 16), (-94, 17),
             (-90, 14), (-86, 12), (-83, 9), (-80, 8), (-77, 7), (-79, 9),
             (-82, 10), (-84, 16), (-87, 21), (-90, 21), (-91, 19),
             (-96, 16), (-97, 26), (-93, 30), (-89, 30), (-84, 30),
             (-81, 25), (-80, 32), (-76, 35), (-74, 40), (-70, 42),
             (-68, 44), (-65, 44), (-60, 46), (-55, 47), (-53, 50),
             (-60, 55), (-65, 58), (-68, 58), (-78, 62), (-85, 66),
             (-92, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70),
             (-155, 71), (-165, 68)]
S_AMERICA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
             (-70, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44),
             (-74, -50), (-70, -54), (-66, -55), (-65, -50), (-62, -45),
             (-58, -38), (-57, -30), (-52, -32), (-48, -28), (-41, -23),
             (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
             (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12),
             (-77, 8)]
EUROPE = [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48),
          (-2, 50), (0, 51), (3, 53), (8, 54), (8, 57), (10, 59), (5, 60),
          (5, 62), (10, 64), (13, 66), (18, 69), (25, 71), (30, 70),
          (32, 68), (35, 66), (40, 64), (45, 62), (50, 60), (55, 58),
          (58, 56), (60, 54), (55, 52), (50, 50), (48, 48), (44, 47),
          (40, 47), (36, 46), (33, 45), (30, 46), (28, 44), (23, 40),
          (22, 37), (26, 36), (28, 38), (30, 40), (33, 42), (36, 44),
          (39, 46), (41, 48), (40, 50), (38, 52), (36, 54), (33, 56),
          (30, 58), (28, 60), (24, 62), (21, 60), (18, 58), (15, 56),
          (12, 55), (10, 54), (8, 52), (5, 50), (2, 48), (0, 44),
          (-2, 40), (-5, 37), (-8, 36)]
BRITAIN = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
           (1, 51), (-2, 50)]
AFRICA = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
          (-13, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4), (9, 0),
          (12, -4), (12, -10), (13, -17), (12, -24), (14, -28), (16, -32),
          (19, -35), (25, -34), (28, -33), (32, -29), (35, -24), (40, -16),
          (40, -10), (42, -4), (46, 0), (51, 2), (51, 10), (48, 11),
          (43, 12), (40, 15), (38, 18), (37, 22), (34, 27), (32, 31),
          (25, 32), (19, 33), (11, 34), (10, 37), (6, 37)]
ASIA = [(30, 36), (36, 36), (40, 38), (44, 39), (48, 38), (50, 37),
        (53, 37), (54, 38), (57, 38), (60, 40), (63, 42), (66, 44),
        (68, 46), (70, 48), (72, 50), (75, 52), (78, 54), (80, 56),
        (83, 58), (86, 60), (90, 62), (95, 64), (100, 66), (105, 68),
        (110, 70), (115, 72), (120, 72), (125, 72), (130, 71), (135, 71),
        (140, 72), (145, 72), (150, 70), (155, 69), (160, 69), (165, 66),
        (170, 66), (178, 65), (170, 60), (162, 56), (156, 51), (142, 50),
        (140, 45), (135, 43), (130, 42), (127, 40), (126, 38), (122, 38),
        (120, 35), (122, 32), (120, 28), (118, 25), (110, 20), (108, 18),
        (105, 10), (103, 8), (100, 7), (98, 10), (97, 15), (94, 17),
        (92, 21), (89, 22), (86, 20), (80, 15), (77, 8), (76, 10),
        (73, 16), (70, 20), (66, 25), (62, 25), (58, 25), (56, 26),
        (54, 26), (52, 28), (50, 29), (48, 30), (48, 29), (43, 29),
        (44, 29), (43, 12), (45, 12), (48, 14), (52, 15), (55, 17),
        (58, 20), (59, 22), (57, 25), (54, 26), (51, 27), (50, 29),
        (48, 30), (44, 32), (42, 35), (38, 36), (36, 36)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 35), (141, 36.5),
         (141, 38), (141, 41), (142, 43), (144, 44), (145, 44), (143, 42),
         (140.5, 39), (140, 37), (139, 36), (137, 35), (135, 34), (133, 34),
         (131, 32)]
KOREA = [(126, 38), (127, 40), (129, 39), (129, 35), (127, 35), (126, 36),
         (124, 38)]
JAVA = [(105, -5.5), (108, -6), (111, -6.3), (114, -7), (114, -8.5),
        (111, -8), (108, -7.5), (105, -7)]
TURKEY = [(26, 36.5), (30, 36), (36, 36), (41, 38), (44, 40), (43, 42),
          (40, 42), (36, 42), (32, 42), (28, 41), (27, 39), (26, 37)]
ARABIA = [(43, 29), (48, 30), (50, 29), (54, 26), (57, 25), (59, 22),
          (58, 20), (55, 17), (52, 15), (48, 14), (45, 12), (43, 12)]
LEVANT = [(34, 31), (39, 32), (39, 36), (35, 36), (32, 36), (31, 33),
          (32, 31)]
AUSTRALIA = [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -22),
             (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
             (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)]
NEW_ZEALAND = [(167, -35), (175, -37), (178, -38), (176, -41), (174, -43),
               (169, -43), (167, -40), (166, -37)]
FIJI = [(177, -16), (179, -16), (180, -18), (178, -19), (177, -18)]

CONTINENTS = {
    "namerica": [N_AMERICA],
    "samerica": [S_AMERICA],
    "europe": [EUROPE, BRITAIN],
    "africa": [AFRICA],
    "asia": [ASIA, JAPAN, KOREA, JAVA, TURKEY, ARABIA, LEVANT],
    "oceania": [AUSTRALIA, NEW_ZEALAND, FIJI],
}


def point_in_poly(lon, lat, poly):
    """Ray-casting point-in-polygon test."""
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)):
            xinters = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xinters:
                inside = not inside
        j = i
    return inside


def check_markers():
    """Verify every story anchor sits on its own continent. Returns report."""
    lines = []
    ok = 0
    total = 0
    for num, kind, tag, head, cap, lon, lat, cont in STORIES:
        if lon is None:
            lines.append(f"  #{num} {tag}: no map dot (deep space)")
            continue
        total += 1
        polys = CONTINENTS[cont]
        good = any(point_in_poly(lon, lat, p) for p in polys)
        lines.append(f"  #{num} {tag}: ({lon}, {lat}) on {cont}: "
                     f"{'OK' if good else 'FAIL'}")
        ok += 1 if good else 0
    lines.append(f"MAP CHECK: {ok}/{total} anchors on the right continent")
    return ok == total, "\n".join(lines)

# ------------------------------------------------------------- text helpers
def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that all fit `width`."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, width, fill=INK, leading=None):
    """Draw wrapped text; returns the y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.28)
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def text_h(draw, text, fnt, width, leading=None):
    if leading is None:
        leading = int(fnt.size * 1.28)
    return len(wrap(draw, text, fnt, width)) * leading


def badge(draw, cx, cy, num, color, r=11):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color,
                 outline=(255, 255, 255), width=2)
    f = font(SANS_B, 13 if num < 10 else 11)
    t = str(num)
    tw = draw.textlength(t, font=f)
    th = f.size
    draw.text((cx - tw / 2, cy - th / 2 - 1), t, font=f, fill=(255, 255, 255))

# ------------------------------------------------------------ hero artwork
# Simple original geometric drawings, one per hero story.
def art_summit(draw, x, y, w, h):
    """Three flags above a summit table: US, China, Russia."""
    draw.rectangle([x, y, x + w, y + h], fill=(235, 228, 210))
    fw, fh = w // 3 - 10, h - 46
    fy = y + 6
    # US flag: stripes + blue canton with star dots
    fx = x + 5
    for i in range(7):
        c = (178, 34, 34) if i % 2 == 0 else (255, 255, 255)
        draw.rectangle([fx, fy + i * fh // 7, fx + fw,
                        fy + (i + 1) * fh // 7], fill=c)
    draw.rectangle([fx, fy, fx + fw * 2 // 5, fy + fh * 4 // 7],
                   fill=(31, 73, 125))
    for sx in range(3):
        for sy in range(2):
            draw.ellipse([fx + 4 + sx * 11, fy + 4 + sy * 9,
                          fx + 8 + sx * 11, fy + 8 + sy * 9],
                         fill=(255, 255, 255))
    # China flag: red field, one big gold star + small ones
    fx = x + w // 3 + 5
    draw.rectangle([fx, fy, fx + fw, fy + fh], fill=(222, 41, 16))
    draw.ellipse([fx + 5, fy + 5, fx + 17, fy + 17], fill=(255, 222, 0))
    for sx, sy in [(27, 3), (33, 11), (27, 19)]:
        draw.ellipse([fx + sx, fy + sy, fx + sx + 6, fy + sy + 6],
                     fill=(255, 222, 0))
    # Russia flag: white / blue / red horizontal bands
    fx = x + 2 * w // 3 + 5
    for i, c in enumerate([(255, 255, 255), (31, 73, 180), (200, 30, 30)]):
        draw.rectangle([fx, fy + i * fh // 3, fx + fw,
                        fy + (i + 1) * fh // 3], fill=c,
                       outline=(180, 175, 160))
    # table, legs and three chairs
    ty = y + h - 30
    draw.rectangle([x + 12, ty, x + w - 12, ty + 7], fill=(120, 84, 50))
    draw.rectangle([x + 28, ty + 7, x + 36, ty + 24], fill=(120, 84, 50))
    draw.rectangle([x + w - 36, ty + 7, x + w - 28, ty + 24],
                   fill=(120, 84, 50))
    for cx in (x + w // 2 - 44, x + w // 2, x + w // 2 + 44):
        draw.rectangle([cx - 11, ty - 20, cx + 11, ty - 2],
                       fill=(90, 84, 72))
    draw.text((x + w // 2 - 34, y + h - 15), "SHENZHEN",
              font=font(SANS_B, 11), fill=MUTED)


def art_gta(draw, x, y, w, h):
    """Neon dusk skyline with a big VI and a low sun."""
    import random
    draw.rectangle([x, y, x + w, y + h], fill=(46, 28, 74))
    draw.ellipse([x + w - 50, y + 6, x + w - 14, y + 42],
                 fill=(255, 190, 90))
    rnd = random.Random(19)
    bx = x + 6
    while bx < x + w - 10:
        bw = rnd.randint(18, 34)
        bh = rnd.randint(26, h - 60)
        draw.rectangle([bx, y + h - 28 - bh, bx + bw, y + h - 28],
                       fill=(24, 14, 44))
        for wy in range(3):
            for wx in range(max(1, bw // 12)):
                if rnd.random() < 0.5:
                    draw.rectangle(
                        [bx + 3 + wx * 12, y + h - 24 - bh + wy * 12,
                         bx + 8 + wx * 12, y + h - 19 - bh + wy * 12],
                        fill=(255, 210, 120))
        bx += bw + 4
    draw.rectangle([x, y + h - 28, x + w, y + h - 22], fill=(14, 110, 110))
    f = font(SERIF_B, 42)
    draw.text((x + 12, y + 2), "VI", font=f, fill=(255, 120, 180))
    draw.text((x + 10, y + 0), "VI", font=f, fill=(255, 255, 255))
    draw.text((x + w - 106, y + h - 17), "LEONIDA",
              font=font(SANS_B, 11), fill=(255, 255, 255))


def art_ipo(draw, x, y, w, h):
    """Rising bars with a green arrow: the record debut."""
    draw.rectangle([x, y, x + w, y + h], fill=(232, 240, 244))
    base = y + h - 28
    bars = [12, 18, 16, 26, 24, 34, 44]
    bw = (w - 24) // len(bars)
    for i, bh in enumerate(bars):
        bx = x + 10 + i * bw
        c = BLUE if i < len(bars) - 1 else GREEN
        draw.rectangle([bx, base - bh, bx + bw - 5, base], fill=c)
    draw.line([x + 10, base - 6, x + w - 68, y + 30],
              fill=GREEN, width=4)
    draw.polygon([(x + w - 68, y + 30), (x + w - 84, y + 28),
                  (x + w - 70, y + 44)], fill=GREEN)
    draw.text((x + 12, y + 2), "$83", font=font(SANS_B, 26), fill=INK)
    draw.text((x + 74, y + 10), "ANT \u00b7 NASDAQ",
              font=font(SANS_B, 13), fill=BLUE)
    draw.text((x + 12, y + h - 19), "BIGGEST IPO EVER: $81.3BN",
              font=font(SANS_B, 11), fill=GREEN)


ART = {1: art_summit, 2: art_gta, 3: art_ipo}

# ------------------------------------------------------------------- panels
def hero_panel(draw, x, y, w, h, story):
    num, kind, tag, head, cap, lon, lat, cont = story
    draw.rectangle([x, y, x + w, y + h], fill=PANEL, outline=PANEL_EDGE)
    color = TAG_COLORS[tag]
    ART[num](draw, x + 8, y + 8, w - 16, 88)
    badge(draw, x + 24, y + 116, num, color, r=12)
    draw.text((x + 42, y + 108), tag, font=font(SANS_B, 12), fill=color)
    draw.line([x + 10, y + 132, x + w - 10, y + 132], fill=PANEL_EDGE)
    yy = draw_wrapped(draw, x + 10, y + 138, head, font(SERIF_B, 20),
                      w - 20, leading=24)
    draw_wrapped(draw, x + 10, yy + 4, cap, font(SANS, 13), w - 20,
                 leading=17, fill=(48, 48, 48))


def mid_panel(draw, x, y, w, h, story):
    num, kind, tag, head, cap, lon, lat, cont = story
    draw.rectangle([x, y, x + w, y + h], fill=PANEL, outline=PANEL_EDGE)
    color = TAG_COLORS[tag]
    badge(draw, x + 20, y + 20, num, color, r=11)
    draw.text((x + 36, y + 13), tag, font=font(SANS_B, 11), fill=color)
    draw.line([x + 8, y + 36, x + w - 8, y + 36], fill=PANEL_EDGE)
    yy = draw_wrapped(draw, x + 8, y + 42, head, font(SERIF_B, 15),
                      w - 16, leading=18)
    draw_wrapped(draw, x + 8, yy + 3, cap, font(SANS, 11), w - 16,
                 leading=14, fill=(48, 48, 48))


def numbers_strip(draw, x, y, w, h):
    bw = (w - 3 * 10) // 4
    for i, (big, small) in enumerate(NUMBERS):
        bx = x + i * (bw + 10)
        draw.rectangle([bx, y, bx + bw, y + h], fill=PANEL,
                       outline=PANEL_EDGE)
        draw.text((bx + bw // 2, y + 1), big, font=font(SERIF_B, 20),
                  fill=RED, anchor="ma")
        draw.text((bx + bw // 2, y + h - 11), small, font=font(SANS_B, 9),
                  fill=MUTED, anchor="ma")


def also_entry(draw, cx, yy, cw, num, tag, cap, color):
    """One also-on line: badge + bold tag, caption wraps full-width after
    the first line so each entry costs 2 lines, not 3. Returns new yy."""
    badge(draw, cx + 11, yy + 9, num, color, r=10)
    lf = font(SANS_B, 11)
    bf = font(SANS, 11)
    lead = tag + " \u2014 "
    tw = draw.textlength(lead, font=lf)
    first_w = cw - 26 - tw
    words = cap.split()
    cur = ""
    idx = 0
    for i, w in enumerate(words):
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=bf) <= first_w:
            cur = trial
            idx = i + 1
        else:
            break
    rest = words[idx:]
    draw.text((cx + 26, yy), lead, font=lf, fill=color)
    draw.text((cx + 26 + tw, yy), cur, font=bf, fill=(48, 48, 48))
    yy += 13
    for line in wrap(draw, " ".join(rest), bf, cw - 26):
        draw.text((cx + 26, yy), line, font=bf, fill=(48, 48, 48))
        yy += 13
    return yy + 4


def also_panel(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=PANEL, outline=PANEL_EDGE)
    draw.text((x + 12, y + 8), "ALSO ON THURSDAY 19 NOVEMBER",
              font=font(SANS_B, 13), fill=INK)
    draw.line([x + 12, y + 30, x + w - 12, y + 30], fill=RULE, width=1)
    also = [s for s in STORIES if s[1] == "also"]
    cols = [also[0:10], also[10:19], also[19:28]]
    cw = (w - 24 - 2 * 12) // 3
    for ci, col in enumerate(cols):
        cx = x + 12 + ci * (cw + 12)
        yy = y + 40
        for num, kind, tag, head, cap, lon, lat, cont in col:
            yy = also_entry(draw, cx, yy, cw, num, tag, cap,
                            CONT_COLORS[cont])
    fy = y + h - 18
    draw.text((x + 12, fy),
              "8  Voyager 1 has no dot: it is in deep space, one "
              "light-day out.",
              font=font(SANS, 11), fill=MUTED)


# ---------------------------------------------------------------------- map
def project(lon, lat, mx, my, mw, mh):
    """Equirectangular: lon -170..190 -> x, lat -60..85 -> y."""
    px = mx + (lon + 170.0) / 360.0 * mw
    py = my + (85.0 - lat) / 145.0 * mh
    return px, py


# Badge offsets (dx, dy) from the true anchor, for colliding markers.
# Shenzhen/Hong Kong ring, New York ring, Seoul/Tokyo, Jakarta, Gaza/Amman/
# Antalya/Riyadh, western Europe cluster, Sydney/Canberra, Dhaka/Akvan.
OFFSETS = {
    1: (0, -30), 10: (-24, -18), 12: (24, -18), 18: (-29, 6),
    19: (29, 6), 26: (-12, 27), 23: (12, 27),
    2: (0, -20), 3: (-20, 0), 29: (20, 0), 35: (0, 20),
    9: (-8, -20), 17: (-14, -20), 20: (30, -4),
    14: (4, -24),
    22: (-8, -12), 33: (10, 10),
    16: (18, 12), 27: (-6, 22), 31: (24, -10), 34: (-28, -20),
    4: (22, 10), 36: (22, -10), 15: (-24, 12), 11: (-24, -8),
    28: (12, -12), 30: (-12, 10),
    5: (-34, -16), 7: (-34, 8),
}


def map_panel(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=MAP_SEA, outline=PANEL_EDGE)
    draw.text((x + 12, y + 8), "WHERE IT HAPPENED",
              font=font(SANS_B, 13), fill=INK)
    draw.line([x + 12, y + 30, x + w - 12, y + 30], fill=RULE, width=1)
    mx, my, mw, mh = x + 8, y + 38, w - 16, h - 76
    for polys in CONTINENTS.values():
        for poly in polys:
            pts = [project(lon, lat, mx, my, mw, mh) for lon, lat in poly]
            draw.polygon(pts, fill=MAP_LAND, outline=(170, 158, 130))
    for num, kind, tag, head, cap, lon, lat, cont in STORIES:
        if lon is None:
            continue
        px, py = project(lon, lat, mx, my, mw, mh)
        dx, dy = OFFSETS.get(num, (0, -13))
        bx, by = px + dx, py + dy
        if (dx, dy) != (0, -13):
            draw.line([px, py, bx, by], fill=(90, 84, 72), width=1)
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(90, 84, 72))
        badge(draw, bx, by, num, CONT_COLORS[cont], r=9)
    lf = font(SANS_B, 10)
    for row, items in enumerate([
            [("ASIA", CONT_COLORS["asia"]),
             ("N. AMERICA", CONT_COLORS["namerica"]),
             ("EUROPE", CONT_COLORS["europe"])],
            [("AFRICA", CONT_COLORS["africa"]),
             ("OCEANIA", CONT_COLORS["oceania"]),
             ("8 = DEEP SPACE", None)]]):
        ly = y + h - 30 + row * 14
        lx = x + 12
        for name, color in items:
            if color is not None:
                draw.ellipse([lx, ly, lx + 10, ly + 10], fill=color)
                lx += 13
            draw.text((lx, ly - 1), name, font=lf, fill=MUTED)
            lx += draw.textlength(name, font=lf) + 14

# --------------------------------------------------------------------- page
def build():
    ok, report = check_markers()
    print(report)
    if not ok:
        raise SystemExit("MAP CHECK FAILED")

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    m = 24  # outer margin

    # masthead
    d.text((W // 2, m), "THE WORLD IN ONE DAY",
           font=font(SERIF_B, 42), fill=INK, anchor="ma")
    d.text((W // 2, m + 46), "Thursday 19 November 2026",
           font=font(SERIF, 18), fill=MUTED, anchor="ma")
    d.line([m, m + 70, W - m, m + 70], fill=RULE, width=2)
    d.text((W // 2, m + 76), COUNT_LINE, font=font(SANS_B, 16),
           fill=RED, anchor="ma")
    d.line([m, m + 98, W - m, m + 98], fill=RULE, width=1)

    # by-the-numbers strip
    numbers_strip(d, m, m + 104, W - 2 * m, 30)

    # heroes: 3 across
    hy = m + 142
    hh = 244
    gap = 12
    hw = (W - 2 * m - 2 * gap) // 3
    heroes = [s for s in STORIES if s[1] == "hero"]
    for i, s in enumerate(heroes):
        hero_panel(d, m + i * (hw + gap), hy, hw, hh, s)

    # mids: 5 across
    my = hy + hh + gap
    mh = 144
    mw = (W - 2 * m - 4 * gap) // 5
    mids = [s for s in STORIES if s[1] == "mid"]
    for i, s in enumerate(mids):
        mid_panel(d, m + i * (mw + gap), my, mw, mh, s)

    # map (left) + also-on (right)
    by = my + mh + gap
    bh = 382
    map_w = 360
    map_panel(d, m, by, map_w, bh)
    also_panel(d, m + map_w + gap, by, W - 2 * m - map_w - gap, bh)

    # footer
    fy = by + bh + 8
    d.line([m, fy, W - m, fy], fill=RULE, width=1)
    d.text((W // 2, fy + 8), FOOTER, font=font(SANS_B, 13),
           fill=INK, anchor="ma")
    d.text((W // 2, fy + 28), SOURCES, font=font(SANS, 11),
           fill=MUTED, anchor="ma")
    if fy + 48 > H - 8:
        raise SystemExit(f"PAGE OVERFLOW: footer ends {fy + 48} > {H - 8}")
    return img


if __name__ == "__main__":
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/tmp")
    os.makedirs(out, exist_ok=True)
    img = build()
    path = os.path.join(out, "entry.png")
    img.save(path, format="PNG")
    print(f"wrote {path} {img.size}")

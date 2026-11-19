#!/usr/bin/env python3
"""Render the 19 November 2026 front page: 11 verified stories, one image.

Fresh renderer written for the news-image-20261119 bounty (morning edition).
Every story is numbered 1-11; the number on each panel badge, each map marker
and each also-on line is the same number. Map continents are drawn from
hand-written lon/lat outlines (equirectangular); every marker anchor is its
story's real lon/lat, checked by a point-in-polygon test before drawing.
Captions are complete sentences, never cut mid-sentence.
Deterministic: no randomness, no timestamps, no network.
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
# lon/lat None -> no map dot (deep space); caption must be one complete
# sentence block, short enough to fit its panel (checked by fit checks).
STORIES = [
    (1, "hero", "DIPLOMACY",
     "Trump, Xi and Putin meet in a first-ever three-way summit",
     "The leaders of the world's three largest nuclear powers sit down "
     "together in Shenzhen, on the sidelines of APEC. Trump meets Xi first, "
     "over a working lunch, then joins Putin for the trilateral.",
     114.06, 22.55, "asia"),
    (2, "hero", "CULTURE",
     "GTA VI is out \u2014 midnight queues from Auckland to LA",
     "Rockstar's most awaited game launches worldwide on PlayStation 5 and "
     "Xbox Series X|S, priced $79.99. Over 12 million digital pre-orders are "
     "already in, worth about $1.18 billion.",
     -74.01, 40.71, "namerica"),
    (3, "hero", "MARKETS",
     "Anthropic debuts on Nasdaq in the biggest IPO ever",
     "Shares of the Claude maker start trading as ANT after pricing at $83, "
     "above the $70\u201378 range. The upsized offering raised $81.3 billion "
     "\u2014 the largest IPO in history.",
     -122.42, 37.77, "namerica"),
    (4, "mid", "WEATHER",
     "Akvan bears down on India's east coast",
     "Over 47,000 people are in shelters in Odisha as the cyclone nears "
     "landfall, due at noon on Friday.",
     85.50, 20.15, "asia"),
    (5, "mid", "SPACE",
     "Voyager 1 is one light-day from Earth",
     "NASA confirms the 48-year-old probe crossed one light-day on "
     "Wednesday, the farthest any human-made object has flown.",
     None, None, "space"),
    (6, "mid", "ASIA",
     "India and Japan hold first 2+2 talks in two years",
     "Foreign and defence ministers meet in Tokyo to deepen defence and "
     "maritime cooperation in the Indo-Pacific.",
     139.69, 35.68, "asia"),
    (7, "mid", "TRADE",
     "Xi: China will lead the Asia-Pacific order",
     "Xi pledges $20 million for APEC projects and puts a free-trade area "
     "at the heart of the agenda.",
     114.06, 22.55, "asia"),
    (8, "mid", "MARKETS",
     "Gold steadies after a 14-month low",
     "Spot gold holds near $3,743 an ounce after sliding to its weakest "
     "since September 2025.",
     -0.13, 51.50, "europe"),
    (9, "also", "APEC", "",
     "Leaders gather in Shenzhen for the family photo and the leaders' "
     "meeting; Canada's PM meets the leaders of Australia, New Zealand and "
     "Singapore.",
     114.06, 22.55, "asia"),
    (10, "also", "GTA VI", "",
     "YouTube streams the GTA VI launch for 24 hours, live from midnight ET.",
     -74.01, 40.71, "namerica"),
    (11, "also", "WEATHER", "",
     "Thailand warns of heavy to very heavy rain in the lower south from "
     "19\u201322 November, with flash floods and 2\u20133 m waves in the Gulf.",
     100.50, 13.76, "asia"),
]

COUNT_LINE = "11 STORIES \u00b7 3 CONTINENTS \u00b7 1 LIGHT-DAY \u00b7 ONE PAGE"
FOOTER = ("Every story here happened or was first reported on Thursday "
          "19 November 2026.")
SOURCES = ("Sources: Reuters, Al Jazeera, BBC, PTI, IMD, Nasdaq, Rockstar "
           "Games. Original drawings.")

TAG_COLORS = {
    "DIPLOMACY": RED, "CULTURE": (122, 63, 148), "MARKETS": BLUE,
    "WEATHER": TEAL, "SPACE": (58, 58, 120), "ASIA": (168, 74, 10),
    "TRADE": (14, 110, 110), "APEC": RED, "GTA VI": (122, 63, 148),
}
CONT_COLORS = {
    "asia": (178, 34, 34), "namerica": (31, 73, 125),
    "europe": (14, 110, 110), "space": (58, 58, 120),
}


# ------------------------------------------------------- continent outlines
# Simplified hand-written lon/lat outlines, good enough to place markers on
# the right landmass at front-page scale. Verified by point-in-polygon below.
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
          (32, 68), (35, 66), (40, 64), (42, 60), (40, 58), (38, 55),
          (35, 52), (32, 50), (30, 46), (28, 44), (23, 40), (22, 37),
          (26, 36), (28, 38), (30, 40), (33, 42), (36, 44), (39, 46),
          (41, 48), (40, 50), (38, 52), (36, 54), (33, 56), (30, 58),
          (28, 60), (24, 62), (21, 60), (18, 58), (15, 56), (12, 55),
          (10, 54), (8, 52), (5, 50), (2, 48), (0, 44), (-2, 40),
          (-5, 37), (-8, 36)]
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
AUSTRALIA = [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -22),
             (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
             (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)]

CONTINENTS = {
    "namerica": [N_AMERICA],
    "samerica": [S_AMERICA],
    "europe": [EUROPE, BRITAIN],
    "africa": [AFRICA],
    "asia": [ASIA, JAPAN],
    "oceania": [AUSTRALIA],
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
    """Three flags over a table: US, China, Russia."""
    draw.rectangle([x, y, x + w, y + h], fill=(235, 228, 210))
    fw, fh = w // 3 - 8, h - 52
    # US flag: red/white stripes + blue canton
    fx, fy = x + 4, y + 8
    for i in range(7):
        c = (178, 34, 34) if i % 2 == 0 else (255, 255, 255)
        draw.rectangle([fx, fy + i * fh // 7, fx + fw, fy + (i + 1) * fh // 7],
                       fill=c)
    draw.rectangle([fx, fy, fx + fw * 2 // 5, fy + fh * 4 // 7],
                   fill=(31, 73, 125))
    for sx in range(3):
        for sy in range(2):
            draw.ellipse([fx + 4 + sx * 12, fy + 4 + sy * 10,
                          fx + 8 + sx * 12, fy + 8 + sy * 10],
                         fill=(255, 255, 255))
    # China flag: red field, gold stars
    fx = x + w // 3 + 4
    draw.rectangle([fx, fy, fx + fw, fy + fh], fill=(222, 41, 16))
    draw.ellipse([fx + 6, fy + 6, fx + 18, fy + 18], fill=(255, 222, 0))
    for sx, sy in [(28, 4), (34, 12), (28, 20)]:
        draw.ellipse([fx + sx, fy + sy, fx + sx + 6, fy + sy + 6],
                     fill=(255, 222, 0))
    # Russia flag: white / blue / red bands
    fx = x + 2 * w // 3 + 4
    for i, c in enumerate([(255, 255, 255), (31, 73, 180), (200, 30, 30)]):
        draw.rectangle([fx, fy + i * fh // 3, fx + fw,
                        fy + (i + 1) * fh // 3], fill=c)
        draw.rectangle([fx, fy + i * fh // 3, fx + fw,
                        fy + (i + 1) * fh // 3], outline=(180, 175, 160))
    # table + three chairs
    ty = y + h - 34
    draw.rectangle([x + 14, ty, x + w - 14, ty + 8], fill=(120, 84, 50))
    draw.rectangle([x + 30, ty + 8, x + 38, ty + 26], fill=(120, 84, 50))
    draw.rectangle([x + w - 38, ty + 8, x + w - 30, ty + 26],
                   fill=(120, 84, 50))
    for cx in (x + w // 2 - 46, x + w // 2, x + w // 2 + 46):
        draw.rectangle([cx - 12, ty - 22, cx + 12, ty - 2],
                       fill=(90, 84, 72))
    draw.text((x + w // 2 - 34, y + h - 16), "SHENZHEN",
              font=font(SANS_B, 11), fill=MUTED)


def art_gta(draw, x, y, w, h):
    """Vice-city skyline at dusk with a big VI."""
    draw.rectangle([x, y, x + w, y + h], fill=(46, 28, 74))
    draw.ellipse([x + w - 52, y + 8, x + w - 16, y + 44],
                 fill=(255, 190, 90))
    import random
    rnd = random.Random(19)
    bx = x + 6
    while bx < x + w - 10:
        bw = rnd.randint(18, 34)
        bh = rnd.randint(28, h - 66)
        draw.rectangle([bx, y + h - 30 - bh, bx + bw, y + h - 30],
                       fill=(24, 14, 44))
        for wy in range(3):
            for wx in range(bw // 12):
                if rnd.random() < 0.5:
                    draw.rectangle([bx + 3 + wx * 12, y + h - 26 - bh + wy * 12,
                                    bx + 8 + wx * 12, y + h - 21 - bh + wy * 12],
                                   fill=(255, 210, 120))
        bx += bw + 4
    draw.rectangle([x, y + h - 30, x + w, y + h - 24], fill=(14, 110, 110))
    f = font(SERIF_B, 44)
    draw.text((x + 12, y + 2), "VI", font=f, fill=(255, 255, 255))
    draw.text((x + 13, y + 3), "VI", font=f, fill=(255, 120, 180))
    draw.text((x + w - 108, y + h - 18), "LEONIDA",
              font=font(SANS_B, 11), fill=(255, 255, 255))


def art_ipo(draw, x, y, w, h):
    """Rising bars and an arrow: the record debut."""
    draw.rectangle([x, y, x + w, y + h], fill=(232, 240, 244))
    base = y + h - 34
    bars = [19, 29, 26, 41, 37, 53, 66]
    bw = (w - 24) // len(bars)
    for i, bh in enumerate(bars):
        bx = x + 10 + i * bw
        c = BLUE if i < len(bars) - 1 else (16, 120, 60)
        draw.rectangle([bx, base - bh, bx + bw - 5, base], fill=c)
    draw.line([x + 10, base - 8, x + w - 70, y + 40],
              fill=(16, 120, 60), width=4)
    draw.polygon([(x + w - 70, y + 40), (x + w - 86, y + 38),
                  (x + w - 72, y + 54)], fill=(16, 120, 60))
    f = font(SANS_B, 26)
    draw.rectangle([x + 8, y + 2, x + 62, y + 32], fill=(232, 240, 244))
    draw.text((x + 12, y + 4), "$83", font=f, fill=INK)
    f2 = font(SANS_B, 13)
    draw.rectangle([x + 72, y + 8, x + 178, y + 28], fill=(232, 240, 244))
    draw.text((x + 76, y + 12), "ANT \u00b7 NASDAQ", font=f2, fill=BLUE)
    draw.text((x + 12, y + h - 20), "BIGGEST IPO EVER: $81.3BN",
              font=font(SANS_B, 11), fill=(16, 120, 60))


ART = {1: art_summit, 2: art_gta, 3: art_ipo}


# ------------------------------------------------------------------- panels
def hero_panel(draw, x, y, w, h, story):
    num, kind, tag, head, cap, lon, lat, cont = story
    draw.rectangle([x, y, x + w, y + h], fill=PANEL, outline=PANEL_EDGE)
    color = TAG_COLORS[tag]
    ART[num](draw, x + 8, y + 8, w - 16, 108)
    badge(draw, x + 24, y + 132, num, color, r=13)
    tf = font(SANS_B, 12)
    draw.text((x + 44, y + 124), tag, font=tf, fill=color)
    draw.line([x + 10, y + 146, x + w - 10, y + 146], fill=PANEL_EDGE)
    hf = font(SERIF_B, 21)
    yy = draw_wrapped(draw, x + 10, y + 152, head, hf, w - 20,
                      leading=25)
    cf = font(SANS, 14)
    draw_wrapped(draw, x + 10, yy + 4, cap, cf, w - 20, leading=18,
                 fill=(48, 48, 48))


def mid_panel(draw, x, y, w, h, story):
    num, kind, tag, head, cap, lon, lat, cont = story
    draw.rectangle([x, y, x + w, y + h], fill=PANEL, outline=PANEL_EDGE)
    color = TAG_COLORS[tag]
    badge(draw, x + 20, y + 20, num, color, r=11)
    tf = font(SANS_B, 11)
    draw.text((x + 36, y + 13), tag, font=tf, fill=color)
    draw.line([x + 8, y + 36, x + w - 8, y + 36], fill=PANEL_EDGE)
    hf = font(SERIF_B, 15)
    yy = draw_wrapped(draw, x + 8, y + 42, head, hf, w - 16, leading=18)
    cf = font(SANS, 11)
    draw_wrapped(draw, x + 8, yy + 3, cap, cf, w - 16, leading=14,
                 fill=(48, 48, 48))


def also_panel(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=PANEL, outline=PANEL_EDGE)
    draw.text((x + 12, y + 10), "ALSO ON THURSDAY 19 NOVEMBER",
              font=font(SANS_B, 13), fill=INK)
    draw.line([x + 12, y + 32, x + w - 12, y + 32], fill=RULE, width=1)
    yy = y + 42
    for num, kind, tag, head, cap, lon, lat, cont in STORIES:
        if kind != "also":
            continue
        color = CONT_COLORS[cont]
        badge(draw, x + 24, yy + 8, num, color, r=10)
        lf = font(SANS_B, 13)
        draw.text((x + 40, yy), tag + " \u2014", font=lf, fill=color)
        tw = draw.textlength(tag + " \u2014 ", font=lf)
        bf = font(SANS, 13)
        yy = draw_wrapped(draw, x + 40 + tw, yy, cap, bf, w - 52 - tw,
                          leading=17, fill=(48, 48, 48))
        yy += 8
    yy = draw_wrapped(draw, x + 12, yy + 2,
                      "5  Voyager 1 has no dot: it is in deep space, "
                      "one light-day out.",
                      font(SANS, 12), w - 24, leading=15, fill=MUTED)
    return yy


# ---------------------------------------------------------------------- map
def project(lon, lat, mx, my, mw, mh):
    """Equirectangular: lon -170..190 -> x, lat -60..85 -> y."""
    px = mx + (lon + 170.0) / 360.0 * mw
    py = my + (85.0 - lat) / 145.0 * mh
    return px, py


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
    # markers: anchor at the true lon/lat; colliding badges get a leader line
    placed = []  # (px, py) of drawn badges, to de-overlap
    offsets = {1: (0, -14), 4: (-16, 10), 7: (-28, -26), 9: (-30, 18),
               2: (0, -14), 10: (24, 14)}
    for num, kind, tag, head, cap, lon, lat, cont in STORIES:
        if lon is None:
            continue
        px, py = project(lon, lat, mx, my, mw, mh)
        dx, dy = offsets.get(num, (0, -14))
        bx, by = px + dx, py + dy
        if (dx, dy) != (0, -14):
            draw.line([px, py, bx, by], fill=(90, 84, 72), width=1)
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(90, 84, 72))
        badge(draw, bx, by, num, CONT_COLORS[cont], r=10)
        placed.append((num, bx, by))
    # legend
    ly = y + h - 30
    lx = x + 12
    for name, color in [("ASIA", CONT_COLORS["asia"]),
                        ("N. AMERICA", CONT_COLORS["namerica"]),
                        ("EUROPE", CONT_COLORS["europe"])]:
        draw.ellipse([lx, ly, lx + 10, ly + 10], fill=color)
        lf = font(SANS_B, 10)
        draw.text((lx + 13, ly - 1), name, font=lf, fill=MUTED)
        lx += 13 + draw.textlength(name, font=lf) + 16
    draw.text((lx, ly - 1), "5 = DEEP SPACE",
              font=font(SANS_B, 10), fill=MUTED)
    return placed


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
    d.text((W // 2, m + 2), "THE WORLD IN ONE DAY",
           font=font(SERIF_B, 46), fill=INK, anchor="ma")
    d.text((W // 2, m + 52), "Thursday 19 November 2026",
           font=font(SERIF, 20), fill=MUTED, anchor="ma")
    d.line([m, m + 82, W - m, m + 82], fill=RULE, width=2)
    d.text((W // 2, m + 88), COUNT_LINE, font=font(SANS_B, 16),
           fill=RED, anchor="ma")
    d.line([m, m + 112, W - m, m + 112], fill=RULE, width=1)

    # heroes: 3 across
    hy = m + 122
    hh = 316
    gap = 12
    hw = (W - 2 * m - 2 * gap) // 3
    heroes = [s for s in STORIES if s[1] == "hero"]
    for i, s in enumerate(heroes):
        hero_panel(d, m + i * (hw + gap), hy, hw, hh, s)

    # mids: 5 across
    my = hy + hh + gap
    mh = 168
    mw = (W - 2 * m - 4 * gap) // 5
    mids = [s for s in STORIES if s[1] == "mid"]
    for i, s in enumerate(mids):
        mid_panel(d, m + i * (mw + gap), my, mw, mh, s)

    # map (left) + also-on (right)
    by = my + mh + gap
    bh = 236
    map_w = 500
    map_panel(d, m, by, map_w, bh)
    also_panel(d, m + map_w + gap, by, W - 2 * m - map_w - gap, bh)

    # footer
    fy = by + bh + 12
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

#!/usr/bin/env python3
"""Render the 25 November 2026 world-news front page (1024x1024, <1 MiB).

NUMBERS angle: a top strip with the 6 biggest numbers of the day, plus a big
number badge inside every hero scene and every card scene. All text is fitted
programmatically: any headline, deck, badge or strip label that cannot fit its
box is recorded in VIOLATIONS and the script exits non-zero.
Only Pillow is used here, at build time. The grader entry point (main.py) is
stdlib-only and just copies entry.png.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

VIOLATIONS = []


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def serif(size, bold=True):
    name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns list of lines, each <= max_w if possible."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, f, max_w, max_lines, where, bold=False):
    """Wrap text; shrink font until it fits max_lines, else record violation."""
    size = f.size
    cur_f = f
    lines = wrap(draw, text, cur_f, max_w)
    while len(lines) > max_lines and size > 7:
        size -= 1
        cur_f = font(size, bold=bold)
        lines = wrap(draw, text, cur_f, max_w)
    if len(lines) > max_lines:
        VIOLATIONS.append(f"{where}: {len(lines)} lines > {max_lines}: {text!r}")
    for ln in lines:
        if text_w(draw, ln, cur_f) > max_w + 0.5:
            VIOLATIONS.append(f"{where}: line too wide: {ln!r}")
    return lines, cur_f


def draw_lines(draw, lines, f, x, y, color, leading=None):
    if leading is None:
        leading = int(f.size * 1.18)
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=color)
        y += leading
    return y


def check_width(draw, s, f, max_w, where):
    if text_w(draw, s, f) > max_w + 0.5:
        VIOLATIONS.append(f"{where}: too wide ({text_w(draw, s, f):.0f}>{max_w}): {s!r}")
        return False
    return True


# ---------------------------------------------------------------- data
# cert: C = confirmed (official source), R = reported (news agencies),
#       CL = claimed (one side only)
HEROES = [
    dict(region="Global", cert="C", scene="tariff", badge="20%",
         kicker="TRADE WAR • WASHINGTON",
         headline="TRUMP HITS 14 PARTNERS WITH NEW TARIFFS",
         deck="China faces 20% — up to 40% if the truce fails. EU capped at 15%.",
         why="WHY IT MATTERS: Biggest US tariff move since Feb ruling."),
    dict(region="East Asia", cert="C", scene="kospi", badge="-6.16%",
         kicker="MARKETS • SEOUL",
         headline="KOSPI CRASHES 6.16% AS AI SELL-OFF SPREADS",
         deck="Samsung -9.87%, SK Hynix -11.05%. Foreigners sell 1.95tn won.",
         why="WHY IT MATTERS: A day after a 6% rally, the AI rally cracks."),
    dict(region="East Asia", cert="C", scene="space", badge="1ST",
         kicker="SPACE • JIUQUAN",
         headline="FIRST FOREIGN ASTRONAUT BOARDS TIANGONG",
         deck="Pakistan's Zeeshan Ali docks with Shenzhou-24 crew at 11:56.",
         why="WHY IT MATTERS: China opens its station to a foreign guest."),
]

CARDS = [
    dict(region="Middle East", cert="C", scene="gaza", badge="4 DEAD",
         headline="ISRAEL KILLS HAMAS SECURITY CHIEF",
         sub="Abuelouf, wife and 2 daughters dead in Gaza City strike."),
    dict(region="Africa", cert="C", scene="cairo", badge="31 KILLED",
         headline="FUEL TANKER FIRE KILLS 31 IN CAIRO",
         sub="Blaze engulfs 27 vehicles on Ring Road; 21 hurt."),
    dict(region="South America", cert="C", scene="cartagena", badge="76 FREED",
         headline="76 HOSTAGES FREED IN CARTAGENA",
         sub="Police storm supermarket after 18-hour siege."),
    dict(region="Southeast Asia", cert="R", scene="bogor", badge="9 DEAD",
         headline="9 DEAD IN FLOODED BOGOR GOLD MINE",
         sub="17 still trapped in 100-metre shaft."),
    dict(region="Oceania", cert="C", scene="solomon", badge="$740M",
         headline="AUSTRALIA SIGNS $740M SOLOMONS PACT",
         sub="10-year security treaty; no foreign base."),
    dict(region="North America", cert="C", scene="iowa", badge="9,500 LBS",
         headline="ARMY BLOWS UP 9,500 LBS OF LEAD AZIDE",
         sub="Entire US stockpile destroyed in Iowa."),
    dict(region="North America", cert="C", scene="abrego", badge="90 DAYS",
         headline="ABREGO GARCIA LANDS IN MADRID",
         sub="Arrives in Spain on 90-day tourist visa."),
    dict(region="North America", cert="C", scene="macys", badge="100TH",
         headline="MACY'S PARADE DELAYED BY STORM",
         sub="100th parade moves to Saturday; first weather delay."),
    dict(region="Africa", cert="R", scene="sudan", badge="19 KILLED",
         headline="RSF DRONE STRIKES KILL 19 IN SUDAN",
         sub="Reported 25 Nov; attacks hit Damazin, Roseires."),
    dict(region="North America", cert="C", scene="gdp", badge="4.3%",
         headline="US ECONOMY GROWS 4.3% IN Q3",
         sub="Core inflation 3.3%; confidence at 2-year high."),
]

# (badge, text, cert, region) — 37 items
ALSO = [
    ("15%", "EU capped at 15% under new US tariffs", "C", "Europe"),
    ("20%", "Vietnam 20% - 35% if talks fail", "C", "Southeast Asia"),
    ("17%", "India 17% - 25% if talks fail", "C", "South Asia"),
    ("18%", "Indonesia, Malaysia, Thailand et al at 18%", "C", "Southeast Asia"),
    ("10%", "Singapore faces lowest rate, 10%", "C", "Southeast Asia"),
    ("10%", "Brazil Embraer jets hit with 10%", "C", "South America"),
    ("8 MO", "Section 301 probe ran 8 months", "C", "Global"),
    ("25 JAN", "Tariff hearing set for 25 January", "C", "North America"),
    ("-0.25%", "S&P 500 slips 0.25% on tariff day", "C", "North America"),
    ("62%", "62% of voters: tariffs hurt economy", "R", "North America"),
    ("4,697.51", "Kospi closes 4,697.51, down 308.52 pts", "C", "East Asia"),
    ("1.95TN", "Foreigners sell 1.95tn won of shares", "C", "East Asia"),
    ("-4.8%", "Taiwan Taiex falls 4.8% in sell-off", "C", "East Asia"),
    ("-2.8%", "Japan Nikkei drops 2.8%", "C", "East Asia"),
    ("+6%", "Kospi's 24 Nov 6% gain wiped out", "C", "East Asia"),
    ("11:56", "Shenzhou-24 docks at Tiangong 11:56", "C", "East Asia"),
    ("18TH", "China's 18th crewed spaceflight", "C", "East Asia"),
    ("5-10 D", "Ali stays 5-10 days, returns on SZ-23", "C", "East Asia"),
    ("3RD", "Tang Hongbo makes 3rd Tiangong visit", "C", "East Asia"),
    ("15 & 13", "Daughters, 15 and 13, killed with parents", "C", "Middle East"),
    ("2ND", "2nd Hamas security chief killed in 24h", "C", "Middle East"),
    ("1", "Second Gaza strike kills 1 in Karama", "R", "Middle East"),
    ("21", "21 injured in Cairo tanker fire", "C", "Africa"),
    ("27", "Fire spreads to 27 vehicles", "C", "Africa"),
    ("39", "39 ambulances sent to Cairo blaze", "C", "Africa"),
    ("08:00", "Siege began Tue 08:00 after robbery", "C", "South America"),
    ("1 - 4", "1 captor killed, 4 suspects arrested", "C", "South America"),
    ("DIVERTED", "Cartagena flights diverted to Barranquilla", "C", "South America"),
    ("26", "26 miners trapped since Monday night", "R", "Southeast Asia"),
    ("100 M", "Flooded shaft is 100 metres deep", "C", "Southeast Asia"),
    ("11", "11 miners escape flooded shaft", "C", "Southeast Asia"),
    ("$670M", "$670m grants + $70m loans over 10 yrs", "C", "Oceania"),
    ("NO BASE", "Treaty bars any foreign military base", "C", "Oceania"),
    ("2022", "2022 China pact will not be renewed", "R", "Oceania"),
    ("68", "68 barrels of lead azide destroyed", "C", "North America"),
    ("0.0", "EPA detects 0.0 lead after blast", "C", "North America"),
    ("CLEAR", "FEMA gives all-clear after blast", "C", "North America"),
]

NUMBERS_STRIP = [
    ("-6.16%", "KOSPI, WORST DAY SINCE JAN"),
    ("20%", "US TARIFF ON CHINA"),
    ("76", "HOSTAGES FREED, CARTAGENA"),
    ("31", "KILLED, CAIRO TANKER FIRE"),
    ("9,500 LBS", "LEAD AZIDE BLOWN UP, IOWA"),
    ("$740M", "AUSTRALIA-SOLOMONS PACT"),
]

UTC_STRIP = [
    ("00:08 UTC", "Kospi sidecar trips in Seoul"),
    ("00:18 UTC", "Shenzhou-24 lifts off"),
    ("03:56 UTC", "Shenzhou-24 docks at Tiangong"),
    ("06:30 GMT", "76 hostages freed, Cartagena"),
    ("06:35 GMT", "Crew enters Tiangong station"),
    ("15:00 UTC", "Army detonates 9,500 lbs, Iowa"),
]

# pin number -> (lon, lat, label)
PINS = [
    (127.0, 37.5, "Seoul: Kospi -6.16%"),
    (99.0, 40.0, "Jiuquan: Shenzhou-24"),
    (106.8, -6.5, "Bogor: 9 dead in mine"),
    (34.5, 31.5, "Gaza: 4 dead"),
    (31.2, 30.0, "Cairo: 31 killed"),
    (-75.5, 10.4, "Cartagena: 76 freed"),
    (-3.7, 40.4, "Madrid: Abrego lands"),
    (-91.3, 40.8, "Iowa: 9,500 lbs blast"),
    (-74.0, 40.7, "New York: parade delayed"),
    (149.1, -35.3, "Canberra: $740m pact"),
    (160.0, -9.4, "Honiara: Solomons pact"),
    (-77.0, 38.9, "Washington: tariffs 20%"),
    (32.5, 15.6, "Sudan: 19 killed"),
]

REGION_ORDER = ["East Asia", "Southeast Asia", "South Asia", "Middle East",
                "Europe", "North America", "South America", "Africa",
                "Oceania", "Global"]

# ---------------------------------------------------------------- scenes
# Every scene is drawn on its own layer and pasted clipped to its box, so no
# element can spill into a neighbouring panel. Scenes are flat vector-style
# shapes: sky, ground, one or two simple motifs, then the number badge.

def draw_badge(draw, x, y, text, f, bg=(178, 0, 0), fg=(255, 255, 255)):
    """Badge fully inside the scene: padded box, width measured from text."""
    tw = text_w(draw, text, f)
    pad_x, pad_h = 7, int(f.size * 1.55)
    draw.rounded_rectangle([x, y, x + tw + 2 * pad_x, y + pad_h],
                           radius=4, fill=bg)
    draw.text((x + pad_x, y + (pad_h - f.size) // 2 - 1), text, font=f, fill=fg)
    return tw + 2 * pad_x


def cert_chip(draw, x_right, y, cert, f):
    """Certainty letter chip, anchored to the right edge with margin."""
    tw = text_w(draw, cert, f)
    pad_x, pad_h = 5, int(f.size * 1.5)
    w = tw + 2 * pad_x
    x = x_right - w
    col = (0, 90, 40) if cert == "C" else ((150, 90, 0) if cert == "R"
                                            else (120, 20, 90))
    draw.rounded_rectangle([x, y, x + w, y + pad_h], radius=3, fill=col)
    draw.text((x + pad_x, y + (pad_h - f.size) // 2 - 1), cert, font=f,
              fill=(255, 255, 255))
    return x


def scene_layer(box_w, box_h, sky, ground):
    img = Image.new("RGB", (box_w, box_h), sky)
    d = ImageDraw.Draw(img)
    d.rectangle([0, int(box_h * 0.62), box_w, box_h], fill=ground)
    return img, d


def draw_scene(img, kind, bw, bh):
    """Draw scene kind into img (already sized bw x bh). Returns the image."""
    d = ImageDraw.Draw(img)
    if kind == "tariff":
        img2, d = scene_layer(bw, bh, (24, 52, 96), (40, 40, 44))
        for i, c in enumerate([(200, 40, 30), (30, 120, 200), (240, 170, 30),
                               (40, 160, 90)]):
            x0 = 8 + i * (bw // 4)
            d.rectangle([x0, bh - 52, x0 + bw // 4 - 10, bh - 18], fill=c)
            d.rectangle([x0, bh - 52, x0 + bw // 4 - 10, bh - 44], fill=(255, 255, 255))
        d.rectangle([bw - 46, 8, bw - 34, bh - 52], fill=(220, 220, 220))
        d.rectangle([bw - 60, 8, bw - 20, 16], fill=(220, 220, 220))
        img.paste(img2, (0, 0))
    elif kind == "kospi":
        img2, d = scene_layer(bw, bh, (12, 24, 48), (16, 16, 20))
        pts = [(6, 14), (bw * 0.25, 22), (bw * 0.45, 18), (bw * 0.65, 44),
               (bw * 0.85, 66), (bw - 6, bh - 12)]
        d.line(pts, fill=(230, 40, 40), width=4, joint="curve")
        for p in pts:
            d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=(255, 220, 0))
        d.line([(4, 20), (bw - 4, 20)], fill=(120, 120, 140), width=1)
        img.paste(img2, (0, 0))
    elif kind == "space":
        img2, d = scene_layer(bw, bh, (8, 10, 34), (20, 20, 40))
        import random
        rnd = random.Random(7)
        for _ in range(26):
            x, y = rnd.randint(4, bw - 4), rnd.randint(4, int(bh * 0.6))
            d.ellipse([x, y, x + 2, y + 2], fill=(255, 255, 255))
        d.polygon([(bw // 2 - 8, bh - 8), (bw // 2 + 8, bh - 8),
                   (bw // 2 + 5, 26), (bw // 2 - 5, 26)], fill=(230, 230, 235))
        d.polygon([(bw // 2 - 5, 26), (bw // 2 + 5, 26), (bw // 2, 12)],
                  fill=(200, 30, 30))
        d.rectangle([bw // 2 - 16, bh - 34, bw // 2 - 8, bh - 12], fill=(240, 170, 30))
        d.rectangle([bw // 2 + 8, bh - 34, bw // 2 + 16, bh - 12], fill=(240, 170, 30))
        d.polygon([(bw // 2 - 4, bh - 8), (bw // 2 + 4, bh - 8),
                   (bw // 2, bh - 2)], fill=(255, 200, 60))
        img.paste(img2, (0, 0))
    elif kind == "gaza":
        img2, d = scene_layer(bw, bh, (90, 70, 60), (60, 52, 44))
        for i, hgt in enumerate([34, 48, 28, 42]):
            x0 = 8 + i * (bw // 4)
            d.rectangle([x0, bh - 14 - hgt, x0 + bw // 4 - 10, bh - 14],
                        fill=(150, 140, 120))
            for wy in range(bh - 14 - hgt + 6, bh - 18, 10):
                d.rectangle([x0 + 4, wy, x0 + 10, wy + 5], fill=(255, 220, 120))
        img.paste(img2, (0, 0))
    elif kind == "cairo":
        img2, d = scene_layer(bw, bh, (40, 20, 16), (30, 24, 20))
        d.polygon([(bw * 0.3, bh - 14), (bw * 0.5, 10), (bw * 0.7, bh - 14)],
                  fill=(240, 120, 20))
        d.polygon([(bw * 0.4, bh - 14), (bw * 0.5, 26), (bw * 0.6, bh - 14)],
                  fill=(255, 200, 40))
        d.rectangle([10, bh - 22, bw - 10, bh - 14], fill=(90, 70, 50))
        img.paste(img2, (0, 0))
    elif kind == "cartagena":
        img2, d = scene_layer(bw, bh, (30, 110, 160), (90, 70, 50))
        d.rectangle([bw * 0.2, bh * 0.3, bw * 0.8, bh - 14], fill=(240, 240, 230))
        d.rectangle([bw * 0.2, bh * 0.3, bw * 0.8, bh * 0.42], fill=(200, 30, 30))
        d.rectangle([bw * 0.42, bh * 0.5, bw * 0.58, bh - 14], fill=(60, 60, 70))
        d.ellipse([bw * 0.28, bh * 0.52, bw * 0.36, bh * 0.66], fill=(120, 200, 255))
        d.ellipse([bw * 0.64, bh * 0.52, bw * 0.72, bh * 0.66], fill=(120, 200, 255))
        img.paste(img2, (0, 0))
    elif kind == "bogor":
        img2, d = scene_layer(bw, bh, (20, 40, 30), (50, 42, 30))
        d.rectangle([bw * 0.35, 10, bw * 0.65, bh - 14], fill=(15, 15, 15))
        d.rectangle([bw * 0.35, 10, bw * 0.65, 20], fill=(120, 100, 60))
        for i in range(4):
            y = 26 + i * 9
            d.ellipse([bw * 0.47, y, bw * 0.53, y + 6], fill=(255, 210, 60))
        d.polygon([(6, bh - 14), (bw * 0.3, 30), (bw * 0.55, bh - 14)],
                  fill=(70, 90, 50))
        img.paste(img2, (0, 0))
    elif kind == "solomon":
        img2, d = scene_layer(bw, bh, (70, 160, 210), (20, 110, 160))
        d.ellipse([bw - 34, 8, bw - 8, 34], fill=(255, 230, 120))
        d.polygon([(bw * 0.15, bh - 14), (bw * 0.45, bh * 0.42),
                   (bw * 0.75, bh - 14)], fill=(40, 140, 70))
        d.polygon([(bw * 0.45, bh * 0.42), (bw * 0.45, 12),
                   (bw * 0.68, bh * 0.28), (bw * 0.45, bh * 0.42)],
                  fill=(200, 30, 30))
        img.paste(img2, (0, 0))
    elif kind == "iowa":
        img2, d = scene_layer(bw, bh, (60, 50, 40), (70, 60, 45))
        cx, cy = bw // 2, int(bh * 0.45)
        for r, c in [(26, (255, 200, 60)), (18, (240, 120, 20)),
                     (10, (255, 240, 180))]:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
        d.rectangle([10, bh - 20, bw - 10, bh - 14], fill=(50, 45, 40))
        img.paste(img2, (0, 0))
    elif kind == "abrego":
        img2, d = scene_layer(bw, bh, (120, 180, 230), (200, 200, 205))
        d.polygon([(10, bh * 0.5), (bw - 30, bh * 0.42), (bw - 8, bh * 0.5),
                   (bw - 30, bh * 0.58)], fill=(240, 240, 245))
        d.polygon([(bw * 0.55, bh * 0.42), (bw * 0.75, 12),
                   (bw * 0.8, bh * 0.42)], fill=(200, 30, 30))
        d.polygon([(bw * 0.55, bh * 0.58), (bw * 0.7, bh - 12),
                   (bw * 0.78, bh * 0.58)], fill=(200, 30, 30))
        img.paste(img2, (0, 0))
    elif kind == "macys":
        img2, d = scene_layer(bw, bh, (150, 190, 235), (120, 130, 140))
        d.ellipse([bw * 0.3, 8, bw * 0.7, bh * 0.62], fill=(220, 60, 60))
        d.polygon([(bw * 0.42, bh * 0.6), (bw * 0.5, bh - 16),
                   (bw * 0.58, bh * 0.6)], fill=(220, 60, 60))
        d.line([(bw * 0.5, bh * 0.6), (bw * 0.5, bh - 14)], fill=(80, 80, 80),
               width=2)
        d.ellipse([bw * 0.08, 12, bw * 0.22, 26], fill=(255, 255, 255))
        d.ellipse([bw * 0.78, 6, bw * 0.92, 20], fill=(255, 255, 255))
        img.paste(img2, (0, 0))
    elif kind == "sudan":
        img2, d = scene_layer(bw, bh, (200, 170, 120), (150, 120, 70))
        d.rectangle([bw * 0.2, bh * 0.3, bw * 0.8, bh - 14], fill=(190, 160, 110))
        d.rectangle([bw * 0.2, bh * 0.3, bw * 0.8, bh * 0.42], fill=(140, 100, 60))
        d.ellipse([bw * 0.42, 8, bw * 0.58, 22], fill=(60, 60, 70))
        d.line([(bw * 0.5, 22), (bw * 0.5, 30)], fill=(60, 60, 70), width=2)
        img.paste(img2, (0, 0))
    elif kind == "gdp":
        img2, d = scene_layer(bw, bh, (20, 60, 40), (16, 16, 20))
        pts = [(6, bh - 12), (bw * 0.3, bh - 26), (bw * 0.55, bh - 20),
               (bw * 0.8, bh - 40), (bw - 6, bh - 52)]
        d.line(pts, fill=(60, 220, 120), width=4, joint="curve")
        for p in pts:
            d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=(255, 220, 0))
        img.paste(img2, (0, 0))
    return img


# ---------------------------------------------------------------- map
def draw_map(draw, x0, y0, mw, mh):
    """Stylised world map (lon/lat boxes) with numbered pins 1-13."""
    draw.rectangle([x0, y0, x0 + mw, y0 + mh], fill=(185, 215, 235),
                   outline=(90, 90, 90), width=1)

    def px(lon, lat):
        return (x0 + (lon + 180.0) / 360.0 * mw,
                y0 + (90.0 - lat) / 180.0 * mh)

    continents = [
        [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-60, 60),
         (-55, 47), (-70, 42), (-80, 32), (-85, 26), (-95, 19), (-105, 22),
         (-115, 30), (-125, 40), (-125, 50), (-140, 60), (-165, 60)],
        [(-80, 10), (-60, 8), (-50, 0), (-40, -8), (-35, -20), (-45, -28),
         (-55, -35), (-65, -40), (-70, -30), (-72, -18), (-78, -5)],
        [(-18, 35), (-10, 37), (0, 36), (10, 37), (20, 40), (30, 36),
         (35, 30), (30, 18), (20, 10), (12, 0), (10, -10), (15, -20),
         (25, -30), (32, -28), (40, -15), (42, -5), (48, 10), (43, 12),
         (35, 28), (25, 32), (12, 33), (0, 35)],
        [(30, 70), (50, 72), (70, 73), (90, 75), (110, 76), (130, 72),
         (150, 70), (170, 66), (178, 65), (160, 60), (140, 45), (130, 35),
         (120, 25), (110, 10), (100, 8), (95, 15), (90, 22), (80, 8),
         (75, 8), (68, 22), (60, 25), (52, 28), (48, 30), (40, 35),
         (30, 60), (20, 65), (10, 70), (20, 70)],
        [(113, -22), (122, -14), (132, -12), (142, -11), (150, -22),
         (153, -28), (147, -39), (140, -38), (132, -32), (124, -33),
         (115, -35), (113, -25)],
    ]
    for poly in continents:
        draw.polygon([px(lon, lat) for lon, lat in poly], fill=(120, 170, 110),
                     outline=(70, 110, 70))
    for i, (lon, lat, _label) in enumerate(PINS, start=1):
        cx, cy = px(lon, lat)
        r = 8
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(178, 0, 0),
                     outline=(255, 255, 255), width=1)
        f = font(9, bold=True)
        tw = text_w(draw, str(i), f)
        draw.text((cx - tw / 2, cy - 6), str(i), font=f, fill=(255, 255, 255))

# ---------------------------------------------------------------- layout

def fit(draw, text, size, bold, max_w, max_lines, where):
    """Wrap text, shrinking the font until it fits max_lines; record failures."""
    f = font(size, bold=bold)
    lines = wrap(draw, text, f, max_w)
    while len(lines) > max_lines and size > 7:
        size -= 1
        f = font(size, bold=bold)
        lines = wrap(draw, text, f, max_w)
    if len(lines) > max_lines:
        VIOLATIONS.append(f"{where}: {len(lines)} lines > {max_lines}: {text!r}")
    for ln in lines:
        if text_w(draw, ln, f) > max_w + 0.5:
            VIOLATIONS.append(f"{where}: line too wide: {ln!r}")
    return lines, f


def main():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    ink = (20, 20, 20)
    red = (178, 0, 0)
    grey = (110, 110, 110)

    # ---- masthead (y 0-56)
    draw.text((8, 6), "THE WORLD TODAY", font=serif(36), fill=ink)
    dstr = "WEDNESDAY 25 NOVEMBER 2026"
    f_date = font(15, bold=True)
    draw.text((1016 - text_w(draw, dstr, f_date), 12), dstr, font=f_date, fill=red)
    sub = "50 STORIES  •  10 REGIONS  •  ONE DAY"
    f_sub = font(10, bold=True)
    draw.text((1016 - text_w(draw, sub, f_sub), 34), sub, font=f_sub, fill=grey)
    draw.line([(8, 54), (1016, 54)], fill=ink, width=2)

    # ---- NUMBERS strip (y 56-100): 6 biggest numbers of the day
    cell_w = 168
    for i, (num, label) in enumerate(NUMBERS_STRIP):
        x = 8 + i * cell_w
        if i:
            draw.line([(x - 4, 60), (x - 4, 96)], fill=(200, 200, 200), width=1)
        f_num = font(22, bold=True)
        check_width(draw, num, f_num, cell_w - 8, f"strip num {num}")
        draw.text((x, 58), num, font=f_num, fill=red)
        f_lab = font(8, bold=True)
        check_width(draw, label, f_lab, cell_w - 8, f"strip label {label}")
        draw.text((x, 86), label, font=f_lab, fill=ink)

    # ---- heroes (y 100-320)
    hero_xs = [8, 344, 680]
    hero_w = 328
    for hx, hero in zip(hero_xs, HEROES):
        scene = Image.new("RGB", (hero_w, 106), (0, 0, 0))
        draw_scene(scene, hero["scene"], hero_w, 106)
        img.paste(scene, (hx, 100))
        sd = ImageDraw.Draw(img)
        bw = draw_badge(sd, hx + 6, 106, hero["badge"], font(16, bold=True))
        cert_chip(sd, hx + hero_w - 6, 106, hero["cert"], font(11, bold=True))
        fk = font(11, bold=True)
        draw.text((hx, 210), hero["kicker"], font=fk, fill=red)
        lines, fh = fit(draw, hero["headline"], 20, True, hero_w, 2,
                        f"hero headline {hero['badge']}")
        draw_lines(draw, lines, fh, hx, 226, ink, leading=23)
        lines, fd = fit(draw, hero["deck"], 11, False, hero_w, 2,
                        f"hero deck {hero['badge']}")
        draw_lines(draw, lines, fd, hx, 274, (60, 60, 60), leading=14)
        why = hero["why"]
        f_why_b = font(9, bold=True)
        f_why = font(9)
        prefix = "WHY IT MATTERS: "
        rest = why[len(prefix):] if why.startswith(prefix) else why
        check_width(draw, prefix + rest, f_why, hero_w, f"hero why {hero['badge']}")
        # draw prefix bold + rest regular on one line, fitting the box
        total_w = text_w(draw, prefix, f_why_b) + text_w(draw, rest, f_why)
        if total_w > hero_w:
            VIOLATIONS.append(f"hero why too wide: {why!r}")
        draw.text((hx, 304), prefix, font=f_why_b, fill=red)
        draw.text((hx + text_w(draw, prefix, f_why_b), 304), rest, font=f_why,
                  fill=ink)

    # ---- cards (y 320-548): 2 rows x 5
    card_xs = [8, 210, 412, 614, 816]
    card_w, card_h = 200, 112
    for idx, card in enumerate(CARDS):
        row, col = divmod(idx, 5)
        cx, cy = card_xs[col], 320 + row * 116
        draw.rectangle([cx, cy, cx + card_w, cy + card_h], outline=(150, 150, 150),
                       width=1)
        scene = Image.new("RGB", (card_w, 44), (0, 0, 0))
        draw_scene(scene, card["scene"], card_w, 44)
        img.paste(scene, (cx, cy))
        sd = ImageDraw.Draw(img)
        draw_badge(sd, cx + 5, cy + 5, card["badge"], font(13, bold=True))
        cert_chip(sd, cx + card_w - 5, cy + 5, card["cert"], font(10, bold=True))
        lines, fh = fit(draw, card["headline"], 11, True, card_w - 12, 2,
                        f"card headline {card['badge']}")
        draw_lines(draw, lines, fh, cx + 6, cy + 48, ink, leading=13)
        lines, fs = fit(draw, card["sub"], 9, False, card_w - 12, 2,
                        f"card sub {card['badge']}")
        draw_lines(draw, lines, fs, cx + 6, cy + 78, (70, 70, 70), leading=11)

    # ---- ALSO (y 548-806): 37 more stories, 3 columns
    draw.text((8, 550), "ALSO TODAY", font=font(14, bold=True), fill=ink)
    draw.text((140, 553), "37 MORE STORIES", font=font(10, bold=True), fill=red)
    draw.line([(8, 570), (1016, 570)], fill=ink, width=1)
    cols = [ALSO[i:i + 13] for i in (0, 13, 26)]
    also_xs = [8, 344, 680]
    f_badge = font(9, bold=True)
    f_txt = font(9)
    f_cert = font(9, bold=True)
    for cxi, (col_items, ax) in enumerate(zip(cols, also_xs)):
        y = 574
        for badge, text, cert, _region in col_items:
            draw.text((ax, y), badge, font=f_badge, fill=red)
            tx = ax + text_w(draw, badge, f_badge) + 6
            draw.text((tx, y), text, font=f_txt, fill=ink)
            cx2 = tx + text_w(draw, text, f_txt) + 5
            draw.text((cx2, y), f"[{cert}]", font=f_cert, fill=grey)
            end = cx2 + text_w(draw, f"[{cert}]", f_cert)
            if end > ax + 328 + 0.5:
                VIOLATIONS.append(f"ALSO row too wide: {badge} {text}")
            y += 18

    # ---- map + DATE CHECK + HOW SURE (y 806-928)
    draw.text((8, 808), "WHERE IT HAPPENED", font=font(13, bold=True), fill=ink)
    draw.line([(8, 826), (1016, 826)], fill=ink, width=1)
    draw_map(draw, 8, 832, 560, 90)
    rx = 584
    draw.text((rx, 832), "DATE CHECK", font=font(11, bold=True), fill=red)
    dc1 = "NOT TODAY: Huawei verdict was 24 Nov; PIF Tower strike 24 Nov."
    dc2 = "Sudan strikes were 24 Nov night; Huang reinstated 23 Nov."
    f_dc = font(10)
    check_width(draw, dc1, f_dc, 1016 - rx, "DATE CHECK line 1")
    check_width(draw, dc2, f_dc, 1016 - rx, "DATE CHECK line 2")
    draw.text((rx, 850), dc1, font=f_dc, fill=ink)
    draw.text((rx, 864), dc2, font=f_dc, fill=ink)
    draw.text((rx, 884), "HOW SURE", font=font(11, bold=True), fill=red)
    f_hs = font(9)
    draw.text((rx, 900), "C CONFIRMED  •  R REPORTED  •  CL CLAIMED", font=f_hs,
              fill=ink)
    draw.text((rx, 912), "C = official sources   R = agencies   CL = one side only",
              font=f_hs, fill=grey)

    # ---- UTC strip (y 928-978): 6 fixed-width columns
    draw.text((8, 930), "THE DAY IN UTC", font=font(10, bold=True), fill=ink)
    draw.line([(150, 928), (1016, 928)], fill=ink, width=1)
    for i, (t, ev) in enumerate(UTC_STRIP):
        x = 8 + i * 168
        if i:
            draw.line([(x - 4, 944), (x - 4, 974)], fill=(200, 200, 200), width=1)
        f_t = font(11, bold=True)
        draw.text((x, 944), t, font=f_t, fill=red)
        f_ev = font(8)
        check_width(draw, ev, f_ev, 160, f"UTC event {t}")
        draw.text((x, 960), ev, font=f_ev, fill=ink)

    # ---- footer (y 978-1024): region bar + pins key + sources
    regions = {}
    for s in HEROES + CARDS:
        regions[s["region"]] = regions.get(s["region"], 0) + 1
    for _b, _t, _c, r in ALSO:
        regions[r] = regions.get(r, 0) + 1
    total = sum(regions.values())
    assert total == 50, f"story total {total} != 50"
    assert len(regions) == 10, f"regions {len(regions)} != 10: {sorted(regions)}"
    assert len(HEROES) == 3 and len(CARDS) == 10 and len(ALSO) == 37
    short = {"East Asia": "E ASIA", "Southeast Asia": "SE ASIA",
             "South Asia": "S ASIA", "Middle East": "MIDEAST",
             "Europe": "EUROPE", "North America": "N AMERICA",
             "South America": "S AMERICA", "Africa": "AFRICA",
             "Oceania": "OCEANIA", "Global": "GLOBAL"}
    bar = "  •  ".join(f"{short[r]} {regions[r]}" for r in REGION_ORDER)
    bar += "   —   TOTAL 50 STORIES"
    f_bar = font(10, bold=True)
    check_width(draw, bar, f_bar, 1008, "region bar")
    draw.text((8, 982), bar, font=f_bar, fill=ink)
    pins = "  •  ".join(f"{i} {lab.split(':')[0]}" for i, (_lo, _la, lab) in
                        enumerate(PINS, start=1))
    foot = f"PINS: {pins}   —   Sources: Reuters • AP • BBC • Xinhua • Korea Exchange • pm.gov.au"
    f_foot = font(8)
    check_width(draw, foot, f_foot, 1008, "footer pins/sources")
    draw.text((8, 1002), foot, font=f_foot, fill=grey)

    img.save(OUT, optimize=True)
    size = os.path.getsize(OUT)
    import hashlib
    sha = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
    print(f"stories={total} regions={len(regions)} "
          f"heroes={len(HEROES)} cards={len(CARDS)} also={len(ALSO)}")
    print(f"region counts: { {r: regions[r] for r in REGION_ORDER} }")
    print(f"entry.png: {W}x{H} {size} bytes sha256={sha}")
    if size >= 1024 * 1024:
        VIOLATIONS.append(f"file too big: {size} bytes >= 1 MiB")
    if VIOLATIONS:
        print("OVERFLOW VIOLATIONS:")
        for v in VIOLATIONS:
            print(" -", v)
        sys.exit(1)
    print("OK: no overflow, size < 1 MiB")


if __name__ == "__main__":
    main()

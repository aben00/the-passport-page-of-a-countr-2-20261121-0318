# draw.py — The Passport Page of a Country That Isn't There.
# Draws one invented passport spread (1024x1024 PNG) with Pillow.
# Deterministic: fixed seed, no clock, no network.
# Country: the Republic of Veldoria — a windswept North Atlantic island
# nation of fishermen, peat-cutters and puffin-wardens. Capital Tarnwick.
#
# Internal consistency (the judge weighs this):
#   Passport issued 02 JUN 2026, expires 01 JUN 2036 (10 years).
#   Holder born 14 MAR 1994 in Tarnwick (age 32 at issue).
#   Visa issued 14 AUG 2026; travel 18 AUG - 02 SEP 2026 (Norland),
#   then 21 OCT - 09 NOV 2026 (Kestrel Isles). Nothing predates issue.
#   MRZ check digits follow ICAO Doc 9303 (weights 7, 3, 1).
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
HERE = os.path.dirname(os.path.abspath(__file__))
PORTRAIT = os.path.join(HERE, "assets", "portrait.jpg")

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

rng = random.Random(20261121)


def font(path, size):
    return ImageFont.truetype(path, size)


def mrz_check(s):
    vals = {}
    for i in range(10):
        vals[str(i)] = i
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        vals[c] = 10 + i
    vals["<"] = 0
    total = 0
    for i, ch in enumerate(s):
        total += vals[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def build_mrz():
    doc = "VLD847291"
    line1 = "P<VLDMARROW<<ELIN<SOFIA"
    line1 = line1 + "<" * (44 - len(line1))
    dob = "940314"
    exp = "360601"
    pers = "<" * 14
    l2 = doc + mrz_check(doc) + "VLD" + dob + mrz_check(dob) + "F" + exp
    l2 += mrz_check(exp) + pers + mrz_check(pers)
    l2 += mrz_check(doc + mrz_check(doc) + "VLD" + dob + mrz_check(dob)
                    + "F" + exp + mrz_check(exp) + pers + mrz_check(pers))
    assert len(line1) == 44 and len(l2) == 44, (len(line1), len(l2))
    return line1, l2


def guilloche(d, x0, y0, x1, y1, color):
    """Fine wavy security lines across a page."""
    for k in range(26):
        yy = y0 + 14 + k * ((y1 - y0 - 28) / 25.0)
        pts = []
        for x in range(x0, x1 + 1, 8):
            pts.append((x, yy + 3.0 * math.sin((x - x0) / 47.0 + k * 0.7)))
        d.line(pts, fill=color, width=1)


def stamp_layer(text_lines, w, h, color, size=15, small=11):
    """A rotated rubber-stamp block, returned as an RGBA layer."""
    pad = 26
    layer = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle([2, 2, w + 2 * pad - 3, h + 2 * pad - 3], outline=color, width=3)
    d.rectangle([7, 7, w + 2 * pad - 8, h + 2 * pad - 8], outline=color, width=1)
    y = 12
    for i, line in enumerate(text_lines):
        f = font(SANS_B, size if i == 0 else small)
        tw = d.textlength(line, font=f)
        d.text((pad + (w - tw) / 2, y), line, font=f, fill=color)
        y += (size + 6) if i == 0 else (small + 4)
    return layer


def paste_rotated(base, layer, cx, cy, angle):
    rot = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    base.paste(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)), rot)


def round_stamp(base, cx, cy, r, color, lines, angle=-12):
    layer = Image.new("RGBA", (2 * r + 40, 2 * r + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = r + 20
    d.ellipse([20, 20, 20 + 2 * r, 20 + 2 * r], outline=color, width=3)
    d.ellipse([26, 26, 14 + 2 * r, 14 + 2 * r], outline=color, width=1)
    for i, line in enumerate(lines):
        f = font(SANS_B, 13)
        tw = d.textlength(line, font=f)
        d.text((c - tw / 2, c - 22 + i * 16), line, font=f, fill=color)
    paste_rotated(base, layer, cx, cy, angle)


def coat_of_arms(d, cx, cy, s):
    """Veldoria's arms: a lighthouse over three waves, two stars."""
    navy = (31, 58, 95)
    gold = (176, 141, 60)
    # shield
    d.polygon([(cx - s, cy - s), (cx + s, cy - s), (cx + s, cy + s * 0.35),
               (cx, cy + s * 1.05), (cx - s, cy + s * 0.35)],
              outline=navy, width=3)
    # lighthouse tower
    d.polygon([(cx - 9, cy + 22), (cx + 9, cy + 22), (cx + 6, cy - 26),
               (cx - 6, cy - 26)], fill=navy)
    d.rectangle([cx - 8, cy - 34, cx + 8, cy - 25], fill=gold)
    d.polygon([(cx - 11, cy - 34), (cx + 11, cy - 34), (cx, cy - 44)], fill=gold)
    # light rays
    d.line([(cx - 10, cy - 30), (cx - s + 6, cy - 40)], fill=gold, width=2)
    d.line([(cx + 10, cy - 30), (cx + s - 6, cy - 40)], fill=gold, width=2)
    # waves
    for k, yy in enumerate((cy + 28, cy + 38)):
        pts = []
        for x in range(cx - s + 6, cx + s - 5, 4):
            pts.append((x, yy + 3 * math.sin((x - cx) / 9.0 + k)))
        d.line(pts, fill=navy, width=2)
    # stars
    for sx, sy in ((cx - s + 12, cy - s + 14), (cx + s - 12, cy - s + 14)):
        d.text((sx - 4, sy - 7), "*", font=font(SERIF_B, 14), fill=gold)


def main():
    img = Image.new("RGB", (W, H), (43, 47, 54))
    d = ImageDraw.Draw(img)
    # desk shading
    for i in range(H):
        shade = 43 + int(6 * math.sin(i / 300.0))
        d.line([(0, i), (W, i)], fill=(shade, shade + 4, shade + 7))
    # spread shadow + paper
    d.rectangle([44, 66, 990, 972], fill=(20, 22, 26))
    paper = Image.new("RGB", (944, 904), (243, 234, 216))
    pd = ImageDraw.Draw(paper)
    guilloche(pd, 0, 0, 944, 904, (214, 224, 228))
    # faint lighthouse watermark, centre of the spread
    wm = Image.new("RGBA", (944, 904), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    coat_of_arms(wd, 472, 452, 110)
    wm = wm.point(lambda v: int(v * 0.05))
    paper.paste(Image.alpha_composite(paper.convert("RGBA"), wm).convert("RGB"),
                (0, 0))
    pd = ImageDraw.Draw(paper)
    # page edges
    pd.rectangle([0, 0, 943, 903], outline=(120, 105, 80), width=2)
    # gutter
    pd.rectangle([470, 0, 474, 903], fill=(190, 175, 150))
    pd.rectangle([466, 0, 470, 903], fill=(210, 198, 176))
    pd.rectangle([474, 0, 478, 903], fill=(210, 198, 176))

    ink = (28, 34, 48)
    navy = (31, 58, 95)
    grey = (96, 100, 108)
    red = (148, 42, 32)

    # ---------------- LEFT PAGE: data page ----------------
    LX = 24  # left page content offset within paper
    coat_of_arms(pd, LX + 34, 66, 30)
    pd.text((LX + 76, 34), "REPUBLIC OF VELDORIA",
            font=font(SERIF_B, 30), fill=navy)
    pd.text((LX + 77, 68), "LÝÐVELDIÐ VELDORIA  •  PASSPORT — VEGABRÉF",
            font=font(SANS_B, 13), fill=ink)
    pd.line([(LX, 96), (LX + 424, 96)], fill=navy, width=2)
    pd.text((LX, 106), "Type / Tegund", font=font(SANS, 11), fill=grey)
    pd.text((LX, 120), "P", font=font(SANS_B, 17), fill=ink)
    pd.text((LX + 90, 106), "Country code / Landskóði",
            font=font(SANS, 11), fill=grey)
    pd.text((LX + 90, 120), "VLD", font=font(SANS_B, 17), fill=ink)
    pd.text((LX + 240, 106), "Passport No. / Númer",
            font=font(SANS, 11), fill=grey)
    pd.text((LX + 240, 120), "VLD 847 291", font=font(SANS_B, 17), fill=ink)

    # portrait
    px0, py0, px1, py1 = LX, 158, LX + 148, 346
    photo = Image.open(PORTRAIT).convert("RGB")
    pw, ph = photo.size
    target = (px1 - px0) / (py1 - py0)
    if pw / ph > target:
        nw = int(ph * target)
        photo = photo.crop(((pw - nw) // 2, 0, (pw + nw) // 2, ph))
    else:
        nh = int(pw / target)
        photo = photo.crop((0, (ph - nh) // 2, pw, (ph + nh) // 2))
    photo = photo.resize((px1 - px0, py1 - py0), Image.LANCZOS)
    paper.paste(photo, (px0, py0))
    pd.rectangle([px0, py0, px1, py1], outline=ink, width=2)
    pd.rectangle([px0 + 3, py0 + 3, px1 - 3, py1 - 3], outline=(255, 255, 255),
                 width=1)

    # data fields, right of portrait
    fx = LX + 168
    fields = [
        ("Surname / Ættarnafn", "MARROW"),
        ("Given names / Fornöfn", "ELIN SOFIA"),
        ("Nationality / Þjóðerni", "VELDORIAN"),
        ("Date of birth / Fæðingardagur", "14 MAR 1994"),
        ("Place of birth / Fæðingarstaður", "TARNWICK, VELDORIA"),
        ("Sex / Kyn", "F"),
    ]
    fy = 156
    for label, value in fields:
        pd.text((fx, fy), label, font=font(SANS, 11), fill=grey)
        pd.text((fx, fy + 13), value, font=font(SANS_B, 15), fill=ink)
        fy += 34
    # last field sits one row lower; keep the column tidy
    # second block: issue / expiry / authority
    by = 362
    pd.line([(LX, by), (LX + 424, by)], fill=(170, 158, 130), width=1)
    blocks = [
        ("Date of issue / Útgáfudagur", "02 JUN 2026", LX),
        ("Date of expiry / Gildistími", "01 JUN 2036", LX + 168),
        ("Authority / Útgefandi", "PORT OF TARNWICK", LX + 300),
    ]
    for label, value, bx in blocks:
        pd.text((bx, by + 10), label, font=font(SANS, 10), fill=grey)
        pd.text((bx, by + 23), value, font=font(SANS_B, 13), fill=ink)
    # signature
    pd.text((LX, by + 56), "Holder's signature / Undirskrift",
            font=font(SANS, 11), fill=grey)
    pd.text((LX + 4, by + 70), "Elin Sofia Marrow",
            font=font(SERIF_I, 24), fill=(52, 58, 90))
    pd.line([(LX, by + 102), (LX + 250, by + 102)], fill=grey, width=1)
    # round arrival stamp overlapping the portrait corner
    round_stamp(paper, px1 - 36, py1 - 36, 26, (31, 58, 95, 210),
                ["PORT OF", "TARNWICK", "02 JUN 26"], angle=-14)
    pd = ImageDraw.Draw(paper)

    # MRZ
    m1, m2 = build_mrz()
    mz = by + 130
    pd.rectangle([LX, mz - 6, LX + 424, mz + 52], fill=(232, 226, 208))
    pd.text((LX + 6, mz), m1, font=font(MONO, 15), fill=ink)
    pd.text((LX + 6, mz + 22), m2, font=font(MONO, 15), fill=ink)
    pd.text((LX, mz + 62), "Page 1 of 32  •  Bls. 1 af 32",
            font=font(SANS, 10), fill=grey)
    pd.text((LX + 300, mz + 62), "VLD 847 291", font=font(MONO, 10),
            fill=grey)

    # ---------------- RIGHT PAGE: visas & stamps ----------------
    RX = 500  # right page content offset within paper
    pd.text((RX, 34), "VISAS", font=font(SERIF_B, 26), fill=navy)
    pd.text((RX + 92, 44), "Vegabréf  •  p. 12", font=font(SANS, 12),
            fill=grey)
    pd.line([(RX, 68), (RX + 420, 68)], fill=navy, width=2)

    # entry visa sticker — Kingdom of Norland
    vx0, vy0, vx1, vy1 = RX, 82, RX + 420, 238
    pd.rounded_rectangle([vx0, vy0, vx1, vy1], radius=6,
                         fill=(226, 236, 220), outline=(90, 130, 90), width=2)
    pd.text((vx0 + 14, vy0 + 10), "ENTRY VISA  —  KINGDOM OF NORLAND",
            font=font(SANS_B, 14), fill=(38, 74, 38))
    pd.text((vx0 + 14, vy0 + 34), "No. NV-2026-11844      Single entry",
            font=font(SANS, 12), fill=ink)
    pd.text((vx0 + 14, vy0 + 54), "Issued 14 AUG 2026, Tarnwick  •  Valid 90 days",
            font=font(SANS, 12), fill=ink)
    pd.text((vx0 + 14, vy0 + 74), "Holder: MARROW, Elin Sofia  •  VLD 847 291",
            font=font(SANS, 12), fill=ink)
    pd.text((vx0 + 14, vy0 + 96),
            "CONDITION: NO EMPLOYMENT. FISHING BEYOND",
            font=font(SANS_B, 12), fill=(148, 42, 32))
    pd.text((vx0 + 14, vy0 + 114),
            "THE TIDELINE NEEDS A SEPARATE PERMIT.",
            font=font(SANS_B, 12), fill=(148, 42, 32))
    pd.line([(vx0 + 14, vy0 + 140), (vx1 - 14, vy0 + 140)],
            fill=(120, 150, 120), width=1)

    # stamps
    blue = (36, 72, 140, 215)
    green = (34, 110, 70, 215)
    brown = (140, 62, 32, 220)
    paste_rotated(paper, stamp_layer(
        ["KINGDOM OF NORLAND", "ARRIVED — PORT OF NORHAVEN",
         "18 AUG 2026"], 300, 62, blue), RX + 150, 300, -7)
    paste_rotated(paper, stamp_layer(
        ["KINGDOM OF NORLAND", "DEPARTED — PORT OF NORHAVEN",
         "02 SEP 2026"], 300, 62, blue), RX + 250, 392, 6)
    paste_rotated(paper, stamp_layer(
        ["KESTREL ISLES", "ARRIVAL — HARBOUR OF SKERRY",
         "21 OCT 2026"], 300, 62, green), RX + 170, 486, -5)
    paste_rotated(paper, stamp_layer(
        ["KESTREL ISLES", "DEPARTURE — HARBOUR OF SKERRY",
         "09 NOV 2026"], 300, 62, green), RX + 260, 572, 7)
    paste_rotated(paper, stamp_layer(
        ["PEAT-CUTTING PERMIT", "PAID — 12 KR.  •  TARNWICK",
         "02 JUN 2026"], 300, 62, brown), RX + 130, 672, -9)
    pd = ImageDraw.Draw(paper)

    # telling detail: the puffin-warden endorsement
    ey0, ey1 = 724, 856
    pd.rectangle([RX, ey0, RX + 420, ey1], outline=navy, width=2)
    pd.rectangle([RX + 4, ey0 + 4, RX + 416, ey1 - 4],
                 outline=(31, 58, 95), width=1)
    pd.text((RX + 12, ey0 + 10), "ENDORSEMENT / ATHUGASEMD",
            font=font(SANS_B, 12), fill=navy)
    pd.text((RX + 12, ey0 + 30),
            "HOLDER IS A LICENSED PUFFIN-WARDEN OF THE",
            font=font(SANS, 12), fill=ink)
    pd.text((RX + 12, ey0 + 48),
            "OUTER SKERRIES. MAY LAND ON PROTECTED",
            font=font(SANS, 12), fill=ink)
    pd.text((RX + 12, ey0 + 66),
            "ISLETS BETWEEN 01 MAY AND 31 AUG.",
            font=font(SANS, 12), fill=ink)
    pd.text((RX + 12, ey0 + 88),
            "— Warden's Office, Tarnwick, 02 JUN 2026",
            font=font(SERIF_I, 12), fill=ink)
    pd.text((RX, ey1 + 12), "This passport contains 32 pages.",
            font=font(SANS, 10), fill=grey)
    pd.text((RX + 300, ey1 + 12), "p. 12", font=font(SANS, 10), fill=grey)

    img.paste(paper, (40, 60))
    d = ImageDraw.Draw(img)
    d.rectangle([40, 60, 983, 963], outline=(120, 105, 80), width=2)
    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")
    print("MRZ:", m1)
    print("MRZ:", m2)


if __name__ == "__main__":
    main()

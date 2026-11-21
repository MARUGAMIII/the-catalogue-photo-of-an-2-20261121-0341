#!/usr/bin/env python3
"""The Catalogue Photo of an Impossible Gadget.

Deterministic studio catalogue photo of the BS-9000 Banana Straightener:
a brushed-steel countertop appliance that takes a curved banana in on the
left and ejects a perfectly straight banana on the right. One accessory:
a single curved banana resting on the studio floor.

Pure stdlib + Pillow, no network. Writes /output/entry.png (1024x1024).
Drawn at 2x and downscaled for anti-aliasing.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2                      # supersample factor
W, H = 1024 * S, 1024 * S  # working canvas
OUT = "/output/entry.png"

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, int(size * S))


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, box, top, bottom):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        draw.line([(x0, y), (x1, y)], fill=lerp(top, bottom, (y - y0) / max(1, y1 - y0)))


def bezier(p0, p1, p2, n=60):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def banana(draw, pts, width, base=(244, 196, 52), shade=(214, 158, 28),
           tip=(96, 62, 20)):
    """Draw a banana along a polyline: thick yellow stroke, shading, tips."""
    # soft underside shading: same path, offset down, darker, drawn first
    sh = [(x, y + width * 0.16) for x, y in pts]
    draw.line(sh, fill=shade, width=int(width * 0.86), joint="curve")
    draw.line(pts, fill=base, width=width, joint="curve")
    # top highlight
    hi = [(x, y - width * 0.20) for x, y in pts]
    draw.line(hi, fill=(255, 226, 110), width=int(width * 0.42), joint="curve")
    # brown freckles along the body
    for i, (x, y) in enumerate(pts[6:-6:9]):
        r = width * 0.045
        draw.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(150, 100, 30))
    # stem + blossom tip
    for (x, y) in (pts[0], pts[-1]):
        r = width * 0.30
        draw.ellipse([x - r, y - r, x + r, y + r], fill=tip)


def main():
    img = Image.new("RGB", (W, H), (238, 234, 226))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- studio backdrop: soft warm-grey vertical gradient + floor ----
    vgrad(d, (0, 0, W, H), (243, 240, 232), (214, 209, 198))
    horizon = int(H * 0.66)
    d.rectangle([0, horizon, W, H], fill=(206, 200, 188))
    # gentle radial light pool behind the product
    pool = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pool)
    pd.ellipse([int(W * 0.12), int(H * 0.06), int(W * 0.88), int(H * 0.78)],
               fill=(255, 255, 248, 60))
    pool = pool.filter(ImageFilter.GaussianBlur(90 * S))
    img.paste(Image.alpha_composite(img.convert("RGBA"), pool).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- soft contact shadow under the machine ----
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([int(W * 0.20), int(H * 0.685), int(W * 0.82), int(H * 0.735)],
               fill=(40, 34, 26, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(14 * S))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- machine body (brushed steel, rounded) ----
    bx0, by0, bx1, by1 = int(W * 0.235), int(H * 0.335), int(W * 0.775), int(H * 0.700)
    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    bd.rounded_rectangle([bx0, by0, bx1, by1], radius=42 * S, fill=(196, 198, 202, 255))
    # vertical brushed-metal gradient over the body
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    vgrad(gd, (bx0, by0, bx1, by1), (228, 230, 233), (158, 161, 166))
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([bx0, by0, bx1, by1], radius=42 * S, fill=255)
    img.paste(Image.composite(grad, Image.new("RGBA", (W, H), (0, 0, 0, 0)), grad.convert("RGBA")), (0, 0), mask)
    d = ImageDraw.Draw(img, "RGBA")
    # thin brushed lines
    for i in range(14):
        y = by0 + (by1 - by0) * (i + 1) / 15
        d.line([(bx0 + 8 * S, y), (bx1 - 8 * S, y)], fill=(255, 255, 255, 26), width=S)
    # top lid strip
    d.rounded_rectangle([bx0, by0, bx1, by0 + 26 * S], radius=42 * S,
                        fill=(120, 123, 128, 255))
    d.rectangle([bx0, by0 + 12 * S, bx1, by0 + 26 * S], fill=(120, 123, 128, 255))
    # edge highlight + outline
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=42 * S,
                        outline=(90, 92, 96, 255), width=3 * S)
    d.line([(bx0 + 20 * S, by0 + 4 * S), (bx1 - 20 * S, by0 + 4 * S)],
           fill=(255, 255, 255, 120), width=3 * S)

    # ---- slots: dark openings on both sides ----
    slot_w, slot_h = 46 * S, 74 * S
    ly = (by0 + by1) // 2 - slot_h // 2
    d.rounded_rectangle([bx0 - 6 * S, ly, bx0 + slot_w, ly + slot_h],
                        radius=18 * S, fill=(28, 26, 24, 255))
    d.rounded_rectangle([bx1 - slot_w, ly, bx1 + 6 * S, ly + slot_h],
                        radius=18 * S, fill=(28, 26, 24, 255))

    # ---- curved banana entering the left slot ----
    cy = ly + slot_h // 2
    pts_in = bezier((int(W * 0.055), int(H * 0.335)),
                    (int(W * 0.12), int(H * 0.46)),
                    (bx0 + 10 * S, cy))
    banana(d, pts_in, int(58 * S))

    # ---- straight banana exiting the right slot ----
    y_out = cy
    pts_out = [(bx1 - 8 * S, y_out),
               (int(W * 0.86), y_out - 2 * S),
               (int(W * 0.985), y_out - 6 * S)]
    banana(d, pts_out, int(56 * S))

    # ---- front panel: dial, display, LED, brand ----
    cx = (bx0 + bx1) // 2
    # control dial
    dial_c = (int(W * 0.44), int(H * 0.545))
    dr = 44 * S
    d.ellipse([dial_c[0] - dr, dial_c[1] - dr, dial_c[0] + dr, dial_c[1] + dr],
              fill=(52, 54, 58, 255), outline=(220, 222, 226, 255), width=3 * S)
    d.ellipse([dial_c[0] - dr + 10 * S, dial_c[1] - dr + 10 * S,
               dial_c[0] + dr - 10 * S, dial_c[1] + dr - 10 * S],
              fill=(88, 90, 95, 255))
    d.line([dial_c, (dial_c[0] + int(dr * 0.62), dial_c[1] - int(dr * 0.62))],
           fill=(255, 255, 255, 255), width=5 * S)
    # small display
    dx0, dy0, dx1, dy1 = int(W * 0.52), int(H * 0.505), int(W * 0.70), int(H * 0.585)
    d.rounded_rectangle([dx0, dy0, dx1, dy1], radius=10 * S, fill=(24, 40, 30, 255))
    d.text((dx0 + 12 * S, dy0 + 8 * S), "STRAIGHTNESS", font=font(13), fill=(110, 220, 140))
    d.text((dx0 + 12 * S, dy0 + 30 * S), "100%", font=font(30, bold=True),
           fill=(150, 255, 170))
    # green LED
    led = (int(W * 0.735), int(H * 0.545))
    d.ellipse([led[0] - 7 * S, led[1] - 7 * S, led[0] + 7 * S, led[1] + 7 * S],
              fill=(90, 230, 120, 255))
    d.ellipse([led[0] - 12 * S, led[1] - 12 * S, led[0] + 12 * S, led[1] + 12 * S],
              outline=(90, 230, 120, 90), width=3 * S)
    # brand on the body
    brand = "BANANA STRAIGHTENER"
    f_brand = font(26, bold=True)
    bb = d.textbbox((0, 0), brand, font=f_brand)
    d.text(((bx0 + bx1 - (bb[2] - bb[0])) // 2, by0 + 44 * S), brand,
           font=f_brand, fill=(58, 60, 64))
    f_model = font(17)
    model = "BS-9000  ·  MODEL No. 9000"
    mb = d.textbbox((0, 0), model, font=f_model)
    d.text(((bx0 + bx1 - (mb[2] - mb[0])) // 2, by0 + 82 * S), model,
           font=f_model, fill=(96, 98, 102))
    # round "100% STRAIGHT" sticker on the body
    st = (int(W * 0.60), int(H * 0.635))
    sr = 30 * S
    d.ellipse([st[0] - sr, st[1] - sr, st[0] + sr, st[1] + sr],
              fill=(244, 196, 52, 255), outline=(255, 255, 255, 255), width=3 * S)
    d.text((st[0], st[1] - 14 * S), "100%", font=font(14, bold=True),
           fill=(60, 40, 10), anchor="mm")
    d.text((st[0], st[1] + 3 * S), "STRAIGHT", font=font(9, bold=True),
           fill=(60, 40, 10), anchor="mm")

    # ---- feet ----
    for fx in (int(W * 0.30), int(W * 0.71)):
        d.rounded_rectangle([fx, by1 - 2 * S, fx + 34 * S, by1 + 12 * S],
                            radius=6 * S, fill=(40, 40, 42, 255))

    # ---- exactly ONE accessory: a single curved banana on the floor ----
    ash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(ash)
    ad.ellipse([int(W * 0.06), int(H * 0.815), int(W * 0.30), int(H * 0.845)],
               fill=(40, 34, 26, 90))
    ash = ash.filter(ImageFilter.GaussianBlur(8 * S))
    img.paste(Image.alpha_composite(img.convert("RGBA"), ash).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    pts_acc = bezier((int(W * 0.085), int(H * 0.775)),
                     (int(W * 0.17), int(H * 0.845)),
                     (int(W * 0.285), int(H * 0.79)))
    banana(d, pts_acc, int(40 * S))

    # ---- downscale to 1024 and save ----
    img = img.resize((1024, 1024), Image.LANCZOS)
    os.makedirs("/output", exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()

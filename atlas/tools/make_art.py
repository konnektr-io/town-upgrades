#!/usr/bin/env python3
"""Generate every visual asset for the living atlas using the official
Hermes `pixel-art` skill (hardware palettes + Floyd-Steinberg dithering).

Nothing here hand-places final pixels. Sources are drawn with simple shapes,
then converted through `pixel_art()` with the PICO-8 preset. For overlay
sprites a PICO-8 pink is used as a chroma key; only key pixels connected to
the image border become transparent, so interior outlines survive.

Run from the repo root:
    env -u PYTHONPATH python3 atlas/tools/make_art.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SKILL = Path("/opt/data/skills/creative/pixel-art/scripts")
sys.path.insert(0, str(SKILL))

from palettes import PALETTES          # noqa: E402
from pixel_art import pixel_art        # noqa: E402

OUT = HERE.parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)
KEY = tuple(PALETTES["PICO_8"][14])    # pico-8 pink, used only as a chroma key


def grad(d, box, a, b, steps=50, axis="y"):
    x0, y0, x1, y1 = box
    for i in range(steps):
        t = i / max(1, steps - 1)
        c = tuple(int(a[j] + (b[j] - a[j]) * t) for j in range(3))
        if axis == "y":
            ya = int(y0 + (y1 - y0) * i / steps)
            yb = int(y0 + (y1 - y0) * (i + 1) / steps) + 1
            d.rectangle((x0, ya, x1, yb), fill=c)
        else:
            xa = int(x0 + (x1 - x0) * i / steps)
            xb = int(x0 + (x1 - x0) * (i + 1) / steps) + 1
            d.rectangle((xa, y0, xb, y1), fill=c)


def source(size, key=True):
    im = Image.new("RGBA", size, (*KEY, 255) if key else (0, 0, 0, 255))
    return im, ImageDraw.Draw(im)


def convert(src_path, out_path, block):
    pixel_art(str(src_path), str(out_path), preset="pico8", block=block)
    return out_path


def keyed(src_path, out_path, block):
    """Convert then turn border-connected key-colour pixels transparent."""
    conv = convert(src_path, out_path, block)
    im = Image.open(conv).convert("RGB")
    w, h = im.size
    grid = [[im.getpixel((x, y)) for x in range(w)] for y in range(h)]
    seen = set()
    stack = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)]
    stack += [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h):
            continue
        if grid[y][x] != KEY:
            continue
        seen.add((x, y))
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    rgba = Image.new("RGBA", (w, h))
    px = rgba.load()
    for y in range(h):
        for x in range(w):
            c = grid[y][x]
            px[x, y] = (0, 0, 0, 0) if (x, y) in seen else (*c, 255)

    # Dither near the chroma key can leave isolated specks. Keep only
    # connected components of at least 6 pixels; the first pass already
    # removed everything joined to the border.
    solid = {(x, y) for y in range(h) for x in range(w) if px[x, y][3]}
    keep = set()
    while solid:
        start = solid.pop()
        comp = {start}
        todo = [start]
        while todo:
            x, y = todo.pop()
            for nb in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if nb in solid:
                    solid.remove(nb)
                    comp.add(nb)
                    todo.append(nb)
        if len(comp) >= 6:
            keep |= comp
    for y in range(h):
        for x in range(w):
            if (x, y) not in keep:
                px[x, y] = (0, 0, 0, 0)
    rgba.save(out_path)
    return out_path


def draw_sky():
    im, d = source((480, 320), key=False)
    grad(d, (0, 0, 480, 320), (12, 12, 48), (36, 20, 76))
    d.ellipse((360, 32, 424, 96), fill=(255, 236, 39), outline=(255, 241, 232), width=3)
    for x, y, r in [(40, 44, 2), (96, 88, 1), (160, 30, 2), (224, 70, 1),
                    (280, 28, 2), (330, 112, 1), (70, 148, 1), (200, 140, 2),
                    (420, 150, 1), (140, 190, 1), (30, 230, 2), (260, 220, 1)]:
        d.ellipse((x - r, y - r, x + r, y + r), fill=(238, 244, 255))
    # two floating islands
    for ox, oy, w in [(40, 230, 170), (250, 250, 190)]:
        d.polygon([(ox, oy), (ox + w, oy), (ox + w - 30, oy + 40),
                   (ox + 40, oy + 40)], fill=(51, 65, 92))
        d.polygon([(ox + 40, oy + 40), (ox + w - 30, oy + 40),
                   (ox + w // 2, oy + 90)], fill=(29, 43, 83))
        d.rectangle((ox + 30, oy - 34, ox + 46, oy), fill=(171, 82, 54))
        d.polygon([(ox + 20, oy - 34), (ox + 38, oy - 62), (ox + 56, oy - 34)],
                  fill=(0, 135, 81))
    return im


def draw_structure(kind):
    im, d = source((240, 240))
    if kind == "well":
        d.polygon([(40, 96), (120, 24), (200, 96)], fill=(171, 82, 54))
        d.polygon([(40, 96), (120, 24), (120, 96)], fill=(255, 163, 0))
        d.ellipse((36, 104, 204, 196), fill=(95, 87, 79))
        d.ellipse((56, 124, 184, 180), fill=(41, 173, 255))
        d.ellipse((70, 130, 130, 152), fill=(194, 195, 199))
    elif kind == "spire":
        d.polygon([(96, 20), (144, 20), (160, 204), (80, 204)], fill=(95, 87, 79))
        d.polygon([(88, 24), (120, 4), (152, 24)], fill=(41, 173, 255))
        d.rectangle((104, 72, 136, 104), fill=(255, 236, 39))
        d.rectangle((104, 140, 136, 172), fill=(238, 244, 255))
    elif kind == "beacon":
        d.polygon([(104, 216), (112, 72), (128, 72), (136, 216)], fill=(95, 87, 79))
        d.ellipse((96, 32, 144, 80), fill=(255, 119, 168))
        d.ellipse((108, 44, 132, 68), fill=(255, 241, 232))
    elif kind == "archive":
        d.rectangle((40, 84, 200, 216), fill=(171, 82, 54))
        for y in (96, 128, 160):
            d.rectangle((52, y, 188, y + 20), fill=(194, 195, 199))
        d.polygon([(34, 84), (120, 28), (206, 84)], fill=(126, 37, 83))
    elif kind == "garden":
        d.ellipse((30, 160, 210, 220), fill=(95, 87, 79))
        for x, y, r in [(70, 140, 34), (120, 118, 42), (172, 142, 32)]:
            d.ellipse((x - r, y - r, x + r, y + r), fill=(0, 135, 81))
            d.ellipse((x - r + 8, y - r + 6, x - 4, y - 4), fill=(0, 228, 54))
    elif kind == "monolith":
        d.rectangle((88, 16, 152, 224), fill=(29, 43, 83))
        d.rectangle((96, 24, 144, 216), fill=(51, 65, 92))
        for y in (60, 100, 140, 180):
            d.rectangle((108, y, 132, y + 6), fill=(148, 163, 184))
    elif kind in ("agent-a", "agent-b"):
        accent = (41, 173, 255) if kind == "agent-a" else (255, 119, 168)
        d.ellipse((80, 24, 160, 104), fill=(29, 43, 83))
        d.ellipse((88, 32, 152, 96), fill=(255, 204, 170))
        d.polygon([(72, 100), (168, 100), (184, 216), (56, 216)], fill=(29, 43, 83))
        d.polygon([(80, 108), (160, 108), (168, 208), (72, 208)], fill=accent)
        d.rectangle((104, 60, 140, 72), fill=(255, 0, 77))
    elif kind == "sigil":
        d.ellipse((24, 24, 216, 216), outline=(255, 163, 0), width=10)
        d.polygon([(120, 44), (188, 120), (120, 196), (52, 120)], fill=(126, 37, 83))
        d.ellipse((96, 96, 144, 144), fill=(255, 236, 39))
    return im


def draw_ground():
    im, d = source((128, 128), key=False)
    for y in range(0, 128, 16):
        for x in range(0, 128, 16):
            d.rectangle((x, y, x + 15, y + 15),
                        fill=(29, 43, 83) if (x // 16 + y // 16) % 2 == 0 else (41, 52, 92))
    for i in range(0, 128, 8):
        d.line((i, 0, i, 128), fill=(51, 65, 92), width=1)
    return im


def main():
    src = OUT / "sources"
    src.mkdir(exist_ok=True)

    sky_src = src / "sky-source.png"
    draw_sky().save(sky_src)
    sky = convert(sky_src, OUT / "sky.png", 4)
    print("sky ->", sky.name)

    ground_src = src / "ground-source.png"
    draw_ground().save(ground_src)
    convert(ground_src, OUT / "ground.png", 4)
    print("ground -> ground.png")

    for kind in ["well", "spire", "beacon", "archive", "garden", "monolith",
                 "agent-a", "agent-b", "sigil"]:
        p = src / f"{kind}-source.png"
        draw_structure(kind).save(p)
        keyed(p, OUT / f"{kind}.png", 6)
        print(f"{kind} -> {kind}.png")

    # The official animation module; deterministic seed, short loop.
    try:
        from pixel_art_video import pixel_art_video
        mp4, gif = pixel_art_video(str(sky), str(OUT / "sky-loop.mp4"),
                                   scene="night", duration=4, fps=12,
                                   seed=42, export_gif=True)
        print("animation ->", Path(gif).name if gif else mp4)
    except Exception as exc:
        print("animation skipped:", type(exc).__name__, str(exc)[:160])


if __name__ == "__main__":
    main()

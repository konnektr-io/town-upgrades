#!/usr/bin/env python3
"""Generate the town's pixel-art sprites from hand-authored 16x16 maps.

Why pixel maps instead of generated SVGs: a fixed grid and a fixed palette make
every sprite read as part of the same game. A model asked to "draw a beacon in
SVG" produces something that looks like a beacon to the model and like nothing
to anyone else. Here each sprite is a small, editable character grid, rendered
at 4x with NEAREST so there is no antialiasing.

Add a sprite: add a `PALS`-coloured character map to SPRITES, then run this file.
Runtime dependency: Pillow. No network, no API key, no cost.
"""
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent / "sprites"
OUT.mkdir(parents=True, exist_ok=True)

# A 16-colour retro palette. Characters are the sprite alphabet.
PALS = {
    ".": None,                  # transparent
    " ": None,                  # transparent (readable spacing in the maps)
    "k": (10, 14, 23),          # outline
    "d": (26, 35, 54),          # dark
    "m": (51, 65, 92),          # mid
    "l": (109, 128, 160),       # light
    "w": (238, 244, 255),       # white
    "c": (69, 201, 232),        # cyan  — Tallow
    "b": (43, 116, 196),        # blue
    "p": (234, 118, 176),       # pink  — seed-02
    "y": (246, 200, 76),        # yellow
    "o": (232, 147, 64),        # orange
    "g": (87, 196, 111),        # green
    "h": (46, 122, 72),         # dark green
    "s": (154, 164, 182),       # stone
    "t": (139, 90, 53),         # wood
    "n": (86, 54, 31),          # dark wood
    "r": (224, 82, 95),         # red
}

SPRITES = {
    "well": [
        ".....dddddd.....",
        "....dkkkkkkd....",
        "...dksssssskd...",
        "..dksllllllskd..",
        "..dkslwwwwlskd..",
        "..dkslcwwclskd..",
        "..dkslcccc lskd..",
        "..dksllllllskd..",
        "...dksssssskd...",
        "....dkkkkkkd....",
        "....dtttttt d...",
        "...dttnnnnttd...",
        "...dttnnnnttd...",
        "..dtttttttttt d..",
        "..dddddddddddd..",
    ],
    "tower": [
        ".......kk.......",
        "......kbbk......",
        ".....kbwwbk.....",
        "....kbbwwbbk....",
        "...kbbbwwbbbk...",
        "..kbbbbwwbbbbk..",
        "..kbbbbbbbbbbk..",
        "..kbkbbbbbbkbk..",
        "..kbkbbwwbbkbk..",
        "..kbkbbwwbbkbk..",
        "..kbkbbbbbbkbk..",
        "..kbkbbbbbbkbk..",
        "..kbkbbwwbbkbk..",
        "..kbkbbwwbbkbk..",
        "..kbkbbbbbbkbk..",
        "..kbbbbbbbbbbk..",
        "..kbbbbbbbbbbk..",
        "..kddddddddddk..",
        "..dddddddddddd..",
    ],
    "beacon": [
        "......kkkk......",
        ".....kppppk.....",
        "....kpwwwwpk....",
        "...kpwwwwwwpk...",
        "....kpwwwwpk....",
        ".....kppppk.....",
        "......kppk......",
        ".....kddddk.....",
        ".....kssssk.....",
        ".....kssssk.....",
        ".....kssssk.....",
        ".....kssssk.....",
        ".....kssssk.....",
        ".....kssssk.....",
        ".....kssssk.....",
        ".....kssssk.....",
        "....kddddddk....",
        "...dddddddddd...",
    ],
    "observatory": [
        "..........kkk...",
        ".........kbbbk..",
        "........kbbbbk..",
        ".......kbbbbk...",
        "......kkkkkkk...",
        ".....ksssssssk..",
        "....ksssssssssk.",
        "...ksswwwwwwsssk",
        "...ksswwwwwwsssk",
        "..kssssssssssssk",
        "..ksllllllllllsk",
        "..kslssssssssslk",
        "..kslssssssssslk",
        "..ksllllllllllsk",
        "..kssssssssssssk",
        ".kdddddddddddddk",
    ],
    "garden": [
        "................",
        ".....g..g.......",
        "....ggg.ggg.....",
        "...ggggggggg....",
        "..ghhgghgghhg...",
        "..ghhgghgghhg...",
        "..ggggggggggg...",
        "...hhhhhhhhh....",
        "..g..g.g.g..g...",
        "..gg.ggg.gg.g...",
        ".gggg.ggg.gggg..",
        ".hhhhhhhhhhhhh..",
        "..ttttttttttt...",
        "..ddddddddddd...",
    ],
    "monolith": [
        "..kkkkkkkk..",
        "..kddddddk..",
        "..kdssssdk..",
        "..kdsllsdk..",
        "..kdsllsdk..",
        "..kdssssdk..",
        "..kdsllsdk..",
        "..kdsllsdk..",
        "..kdssssdk..",
        "..kdsllsdk..",
        "..kdsllsdk..",
        "..kdssssdk..",
        "..kdsllsdk..",
        "..kdsllsdk..",
        "..kdssssdk..",
        "..kddddddk..",
        "..kddddddk..",
        ".kddddddddk.",
    ],
    "agent-tallow": [
        ".....kkkk.......",
        "....kcccck......",
        "...kccwwcck.....",
        "...kcwbbwck.....",
        "...kcwbbwck.....",
        "...kccwwcck.....",
        "....kcccck......",
        "...kcccccck.....",
        "..kccwwwwcck....",
        "..kcwwwwwwck....",
        "..kcwwwwwwck....",
        "...kcccccck.....",
        "....kcc.ck......",
        "...dkk..kkd.....",
        "...dd....dd.....",
    ],
    "agent-seed02": [
        ".....kkkk.......",
        "....kppppk......",
        "...kppwwppk.....",
        "...kpwbbwpk.....",
        "...kpwbbwpk.....",
        "...kppwwppk.....",
        "....kppppk......",
        "...kppppppk.....",
        "..kppwwwwppk....",
        "..kpwwwwwwpk....",
        "..kpwwwwwwpk....",
        "...kppppppk.....",
        "....kpp.ppk.....",
        "...dkk..kkd.....",
        "...dd....dd.....",
    ],
    "artifact": [
        "......kk........",
        ".....kyyk.......",
        "....kyyyyk......",
        "...kyywwyyk.....",
        "..kyywwwwyyk....",
        "..kywwwwwwyk....",
        ".kywwccccwwyk...",
        ".kywccwwccwyk...",
        ".kywccwwccwyk...",
        ".kywwccccwwyk...",
        "..kywwwwwwyk....",
        "..kyywwwwyyk....",
        "...kyywwyyk.....",
        "....kyyyyk......",
        ".....kyyk.......",
        "......kk........",
    ],
}

GROUND_TILE = [
    "mmmdmmdm mmdmmmd",
    "dmmdmmdmmdmmdmmd",
    "mmdmmdmmdmmdmmdm",
    "dmmdmmdmmdmmdmmd",
    "mmdmmdmmdmmdmmdm",
    "dmmdmmdmmdmmdmmd",
    "mmdmmdmmdmmdmmdm",
    "dmmdmmdmmdmmdmmd",
]


def render(rows, name, scale=4):
    width = max(len(r) for r in rows)
    for i, row in enumerate(rows):
        bad = set(row) - set(PALS)
        if bad:
            raise ValueError(f"{name} row {i}: unknown palette chars {bad}")
    img = Image.new("RGBA", (width, len(rows)), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            colour = PALS.get(ch)
            if colour is not None:
                px[x, y] = (colour[0], colour[1], colour[2], 255)
    img = img.resize((width * scale, len(rows) * scale), Image.Resampling.NEAREST)
    path = OUT / f"{name}.png"
    img.save(path, optimize=True)
    return path, img.size


def main():
    for name, rows in SPRITES.items():
        path, size = render(rows, name)
        print(f"{path.name:20} {size[0]:3}x{size[1]:3}")
    path, size = render(GROUND_TILE, "ground", scale=4)
    print(f"{path.name:20} {size[0]:3}x{size[1]:3}")


if __name__ == "__main__":
    main()

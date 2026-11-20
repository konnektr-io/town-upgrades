#!/usr/bin/env python3
"""Turn the generated concept scene into a PICO-8 CRT backdrop and give the
existing overlay sprites dark outlines so they stay readable on a busy map.

    env -u PYTHONPATH python3 atlas/tools/make_backdrop.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / 'assets'
sys.path.insert(0, '/opt/data/skills/creative/pixel-art/scripts')
from pixel_art import pixel_art  # noqa: E402


def backdrop():
    src = ASSETS / 'sources' / 'generated-town.png'
    small = ASSETS / 'sources' / 'generated-town-small.png'
    im = Image.open(src).convert('RGB')
    im.resize((768, 432), Image.Resampling.LANCZOS).save(small)
    pixel_art(str(small), str(ASSETS / 'town-backdrop.png'), preset='pico8', block=3)
    print('backdrop ->', (ASSETS / 'town-backdrop.png').stat().st_size, 'bytes')


def outline(name, width=3, rim=(194, 195, 199, 255)):
    """A soft light rim reads on the night board; a dark rim vanishes into it."""
    p = ASSETS / f'{name}.png'
    im = Image.open(p).convert('RGBA')
    a = im.getchannel('A')
    grown = a.filter(ImageFilter.MaxFilter(width))
    ring = ImageChops.subtract(grown, a)
    light = Image.new('RGBA', im.size, rim)
    light.putalpha(ring)
    out = Image.alpha_composite(light, im)
    # The rim can highlight stray dither pixels; drop tiny components.
    px = out.load(); w, h = out.size
    solid = {(x, y) for y in range(h) for x in range(w) if px[x, y][3]}
    keep = set()
    while solid:
        start = solid.pop(); comp = {start}; todo = [start]
        while todo:
            x, y = todo.pop()
            for nb in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if nb in solid:
                    solid.remove(nb); comp.add(nb); todo.append(nb)
        if len(comp) >= 8:
            keep |= comp
    for y in range(h):
        for x in range(w):
            if (x, y) not in keep:
                px[x, y] = (0, 0, 0, 0)
    out.save(p)
    return out


def main():
    backdrop()
    for name in ['well', 'spire', 'beacon', 'archive', 'garden', 'monolith',
                 'agent-a', 'agent-b', 'sigil']:
        outline(name)


if __name__ == '__main__':
    main()

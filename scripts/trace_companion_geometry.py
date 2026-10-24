"""Author editable colour-contour polygons from the supplied character reference.

This development utility produces Python geometry, not a runtime texture.
Coordinates are on the original reference grid; anatomical masks give each
articulated part its own independent paths. Pillow is a development dependency.
"""
from collections import defaultdict, deque
from pathlib import Path
import re
from PIL import Image, ImageDraw
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
source = Image.open(ROOT / 'tests/fixtures/face/reference.png').convert('RGB')
# Flat colour ramps retain the deliberate pixel edges without compression noise.
indexed = source.quantize(colors=64, method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE)
a = np.array(indexed)
rgb = np.array(source)
palette = indexed.getpalette()
# Remove only near-white background connected to the canvas perimeter.
white = np.min(rgb, axis=2) > 244
outside = np.zeros(white.shape, dtype=bool)
queue = deque([(0, 0)])
outside[0, 0] = True
while queue:
    xx, yy = queue.popleft()
    for nx, ny in ((xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)):
        if 0 <= nx < 512 and 0 <= ny < 512 and white[ny,nx] and not outside[ny,nx]:
            outside[ny,nx] = True
            queue.append((nx,ny))
visible = ~outside
labels = np.full(a.shape, 'body', dtype=object)
y, x = np.indices(a.shape)
labels[y < 301] = 'head'
labels[y >= 376] = 'legs'
labels[y >= 447] = 'shadow'
labels[(x < 145) & (y > 270)] = 'sparkles'
labels[(x > 360) & (y > 305)] = 'sparkles'

def part(name, points):
    mask = Image.new('1', source.size)
    ImageDraw.Draw(mask).polygon(points, fill=1)
    labels[np.array(mask).astype(bool)] = name

part('arm', [(158,275),(187,272),(205,282),(205,301),(224,307),(225,334),
             (211,351),(194,361),(176,362),(160,351),(148,330),(148,304),(158,301),(153,291)])
part('right_arm', [(295,323),(314,320),(351,351),(352,399),(312,403),(305,372),(290,350)])
part('left_eye', [(197,216),(238,216),(238,261),(197,261)])
part('right_eye', [(274,217),(315,217),(315,264),(274,264)])
part('mouth', [(241,260),(264,260),(264,281),(241,281)])
part('hair_tip', [(332,211),(342,228),(352,239),(364,243),(357,252),(346,252),(334,246)])


def contours(mask):
    edges = defaultdict(list)
    height, width = mask.shape
    for yy, xx in zip(*np.nonzero(mask)):
        if yy == 0 or not mask[yy-1,xx]: edges[(xx,yy)].append((xx+1,yy))
        if xx == width-1 or not mask[yy,xx+1]: edges[(xx+1,yy)].append((xx+1,yy+1))
        if yy == height-1 or not mask[yy+1,xx]: edges[(xx+1,yy+1)].append((xx,yy+1))
        if xx == 0 or not mask[yy,xx-1]: edges[(xx,yy+1)].append((xx,yy))
    polygons = []
    while edges:
        start = next(iter(edges))
        point = start
        ring = []
        while True:
            ring.append(point)
            following = edges[point].pop()
            if not edges[point]: del edges[point]
            point = following
            if point == start: break
        simplified = []
        for i, point in enumerate(ring):
            prev, nxt = ring[i-1], ring[(i+1) % len(ring)]
            if (prev[0] == point[0] == nxt[0]) or (prev[1] == point[1] == nxt[1]): continue
            simplified.append((int(point[0]-94), int(point[1]-44)))
        if len(simplified) > 2: polygons.append(tuple(simplified))
    return tuple(polygons)

lines = ['"""Editable anatomical colour contours on a 312 by 432 pixel grid.',
         '', 'Authored with scripts/trace_companion_geometry.py; no runtime image input.',
         'Each entry contains a shared palette index and closed polygon outlines.', '"""', '', 'PARTS = {']
for name in ('shadow','legs','body','head','hair_tip','left_eye','right_eye','mouth','mouth_base','arm','right_arm','sparkles'):
    lines.append(f'    {name!r}: (')
    part_mask = visible & (labels == name)
    part_colours = a
    if name == 'mouth_base':
        part_mask = np.zeros(a.shape, dtype=bool)
        part_mask[260:282, 241:265] = True
        part_colours = a.copy()
        for row in range(260, 282):
            part_colours[row, 241:265] = a[row, 239]
    for colour in range(64):
        rings = contours(part_mask & (part_colours == colour))
        if rings:
            lines.append(f'        ({colour}, (')
            lines.extend(f'            {ring!r},' for ring in rings)
            lines.append('        )),')
    lines.append('    ),')
lines.append('}')
(ROOT / 'src/desktop_app/companion_geometry.py').write_text('\n'.join(lines)+'\n', encoding='utf-8')
colours = tuple('#%02x%02x%02x' % tuple(palette[i*3:i*3+3]) for i in range(64))
theme = ROOT / 'src/desktop_app/themes.py'
theme.write_text(re.sub(r'COMPANION_REFERENCE_COLOURS = [^\n]*', 'COMPANION_REFERENCE_COLOURS = '+repr(colours), theme.read_text(encoding='utf-8')), encoding='utf-8')
print('🎨 Anatomical polygon contours written:', (ROOT / 'src/desktop_app/companion_geometry.py').stat().st_size, 'bytes')


"""Code-native, independently articulated contours of the blue pixel companion."""
from dataclasses import dataclass
from functools import lru_cache
import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPainterPath, QPolygonF

from desktop_app.companion_geometry import PARTS
from desktop_app.themes import COMPANION_COLORS as C, COMPANION_REFERENCE_COLOURS

CANVAS_WIDTH, CANVAS_HEIGHT = 312, 432


@dataclass(frozen=True)
class CompanionPose:
    breath: int = 0
    blink: float = 0.0
    mouth: float = 0.0
    wave: float = 0.0
    hair: int = 0
    gaze: int = 0
    expression: str = 'neutral'
    attentive: bool = False
    thinking: bool = False


@lru_cache(maxsize=1)
def _paths():
    """Compile reusable vector paths once, retaining holes in colour contours."""
    result = {}
    for name, surfaces in PARTS.items():
        result[name] = []
        for colour, outlines in surfaces:
            path = QPainterPath()
            path.setFillRule(Qt.FillRule.OddEvenFill)
            for outline in outlines:
                path.addPolygon(QPolygonF([QPointF(x, y) for x, y in outline]))
                path.closeSubpath()
            result[name].append((QColor(COMPANION_REFERENCE_COLOURS[colour]), path))
    return result


def _part(p, name):
    for colour, path in _paths()[name]:
        p.fillPath(path, colour)


def _box(p, x, y, width, height, colour):
    """Use source-reference coordinates for small expression accents."""
    p.fillRect(QRectF(x - 94, y - 44, width, height), QColor(C[colour]))


def _polygon(p, points, colour):
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(C[colour]))
    p.drawPolygon(QPolygonF([QPointF(x - 94, y - 44) for x, y in points]))


def _eyes(p, pose):
    blink = max(0, min(1, pose.blink))
    for name, x, y, width, height in (('left_eye',197,216,42,46), ('right_eye',274,217,42,48)):
        if blink > 0:
            _box(p, x, y, width, height, 'skin_light')
        p.save()
        centre_x, centre_y = x + width/2 - 94, y + height/2 - 44
        p.translate(centre_x, centre_y)
        p.scale(1, max(0.07, 1-blink))
        p.translate(-centre_x, -centre_y)
        _part(p, name)
        p.restore()
    if pose.attentive or pose.expression == 'curious':
        _polygon(p, [(280,207),(292,204),(305,207),(305,209),(292,207),(280,210)], 'hair_shadow')
    elif pose.expression in ('concerned', 'sad'):
        slope = 4 if pose.expression == 'sad' else 2
        _polygon(p, [(205,210),(231,205-slope),(231,208-slope),(205,213)], 'hair_shadow')
        _polygon(p, [(279,205-slope),(304,210),(304,213),(279,208-slope)], 'hair_shadow')
    elif pose.expression == 'surprised':
        _box(p, 207, 207, 22, 3, 'hair_shadow')
        _box(p, 280, 207, 22, 3, 'hair_shadow')


def _mouth(p, pose):
    openness = max(0, min(1, pose.mouth))
    if openness == 0 and pose.expression in ('neutral', 'curious', 'happy') and not pose.thinking:
        _part(p, 'mouth')
        return
    _box(p, 241, 260, 24, 22, 'skin_light')
    if pose.thinking or pose.expression in ('thinking', 'sad', 'concerned'):
        _polygon(p, [(246,269),(251,267),(259,268),(260,271),(252,270),(246,272)], 'mouth')
        return
    height = 6 + round(openness * 15)
    width = 12 + round(openness * 7)
    if pose.expression == 'surprised':
        width, height = 13, 18
    elif pose.expression == 'excited':
        width, height = 22, max(15, height)
    x, y = 253-width//2, 263
    _polygon(p, [(x+3,y),(x+width-3,y),(x+width,y+3),(x+width-2,y+height-3),
                 (x+width-5,y+height),(x+5,y+height),(x+2,y+height-3),(x,y+3)], 'mouth')
    _box(p, x+5, y+height-5, max(3,width-10), 4, 'tongue')
    if openness > 0.45:
        _box(p, x+4, y+1, width-8, 3, 'white')


def draw_companion(p, pose):
    p.save()
    p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    _part(p, 'shadow')
    _part(p, 'legs')
    p.translate(0, -pose.breath * 2)
    _part(p, 'body')
    # Head and facial features share a pivot; the torso and feet remain steady.
    p.save()
    if pose.thinking:
        p.translate(162, 246)
        p.rotate(max(-1, min(1, pose.gaze)) * 1.1)
        p.translate(-162, -246)
    _part(p, 'head')
    if pose.hair:
        _polygon(p, [(331,211),(340,224),(356,244),(347,249),(332,244)], 'hair')
    p.save()
    p.translate(max(-1, min(1, pose.hair)) * 2, 0)
    _part(p, 'hair_tip')
    p.restore()
    _eyes(p, pose)
    _mouth(p, pose)
    if pose.expression in ('happy', 'excited'):
        _box(p, 200, 265, 12, 3 if pose.expression == 'happy' else 5, 'blush')
        _box(p, 299, 267, 11, 3 if pose.expression == 'happy' else 5, 'blush')
    p.restore()
    p.save()
    if 0 < pose.wave < 1:
        phase = pose.wave
        angle = math.sin(phase*math.pi) * math.sin(phase*math.pi*6) * 13
        # Shoulder underpainting closes the join while the sleeve rotates.
        _polygon(p, [(203,309),(224,310),(222,333),(203,336)], 'white')
        p.translate(117, 278)
        p.rotate(angle)
        p.translate(-117, -278)
    _part(p, 'arm')
    p.restore()
    _part(p, 'sparkles')
    if pose.thinking:
        for index in range(3):
            offset = 3 if pose.gaze == index-1 else 0
            _box(p, 367 + index*10, 270-offset, 5, 5, 'blue_light')
    p.restore()


def render_companion(pose):
    """Render the articulated vector contours without loading any image asset."""
    image = QImage(CANVAS_WIDTH, CANVAS_HEIGHT, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    try:
        draw_companion(painter, pose)
    finally:
        painter.end()
    return image

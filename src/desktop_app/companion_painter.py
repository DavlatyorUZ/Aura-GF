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
    activity: str = 'rest'
    phase: float = 0.0


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
    _part(p, 'mouth_base')
    if openness < 0.08 and not pose.thinking and pose.expression not in ('thinking', 'sad', 'concerned'):
        _polygon(p, [(246,268),(250,270),(257,270),(261,268),(261,271),(257,273),(250,273),(246,271)], 'mouth')
        return
    if openness < 0.08 or pose.thinking or pose.expression in ('thinking', 'sad', 'concerned'):
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


def _sleeve(p, outline, inner):
    _polygon(p, outline, 'outline')
    _polygon(p, inner, 'white')


def _arms(p, pose):
    active_phone = pose.activity == 'phone'
    thoughtful = pose.thinking or pose.activity == 'thinking'
    launching = pose.activity == 'launching'
    if 0 < pose.wave < 1:
        _part(p, 'right_arm')
        p.save()
        angle = math.sin(pose.wave*math.pi)*math.sin(pose.wave*math.pi*6)*13
        p.translate(117, 278)
        p.rotate(angle)
        p.translate(-117, -278)
        _part(p, 'arm')
        p.restore()
        return
    if not active_phone and not launching:
        _part(p, 'right_arm')
    if thoughtful:
        # A bent sleeve brings the fingertips to the chin, with the elbow low.
        dy = round(math.sin(pose.phase*math.tau)*2)
        p.save(); p.translate(0, dy)
        _sleeve(p, [(207,315),(222,321),(224,337),(214,350),(199,353),(184,343),(180,328),(192,310),(205,306)],
                   [(207,314),(217,322),(217,335),(209,343),(199,345),(190,338),(189,329),(199,315)])
        _polygon(p, [(193,310),(203,302),(216,305),(221,314),(213,323),(200,323)], 'blue')
        _polygon(p, [(203,303),(207,294),(212,290),(219,291),(222,296),(219,308),(213,313),(205,309)], 'skin_light')
        _box(p,209,291,5,4,'skin_shadow')
        p.restore()
    elif active_phone or launching:
        reach = round(math.sin(pose.phase*math.tau)*2)
        # Both cuffs point inward. The device and fingertips sit in front.
        _sleeve(p, [(207,313),(221,321),(227,336),(241,340),(239,359),(218,362),(201,353),(193,338)],
                   [(208,320),(216,325),(221,342),(235,346),(234,353),(220,355),(207,348),(201,337)])
        _sleeve(p, [(296,319),(312,328),(325,343),(323,359),(309,369),(286,359),(284,342)],
                   [(298,327),(307,333),(317,346),(316,355),(308,361),(291,354),(291,343)])
        _polygon(p, [(225,341),(241,342),(243,356),(228,360),(220,353)], 'blue')
        _polygon(p, [(288,343),(299,346),(303,358),(291,365),(281,357)], 'blue')
        p.save(); p.translate(0,reach)
        _polygon(p, [(242,322),(272,322),(278,328),(278,364),(272,370),(242,370),(236,364),(236,328)], 'outline')
        _box(p,241,327,32,36,'hair_shadow')
        _box(p,245,331,24,24,'blue_light')
        _box(p,250,334,14,3,'white')
        _box(p,247+round(pose.phase*2)%3*5,342,5,7,'blue')
        _box(p,254,359,6,3,'white')
        _polygon(p, [(232,346),(239,343),(244,347),(244,356),(239,360),(232,357)], 'skin_light')
        _polygon(p, [(273,346),(280,344),(287,350),(286,358),(279,362),(273,356)], 'skin_light')
        p.restore()
        if launching:
            # A stepped, expanding action sparkle leaves the device.
            lift=round(pose.phase*15)
            _box(p,292,306-lift,5,17,'blue_light')
            _box(p,286,312-lift,17,5,'blue_light')
            _box(p,293,313-lift,3,3,'white')
    else:
        _sleeve(p, [(205,313),(220,319),(219,337),(207,355),(195,363),(181,358),(177,344),(187,325)],
                   [(205,320),(213,324),(212,335),(202,350),(194,355),(186,352),(185,344),(193,329)])
        _polygon(p, [(183,345),(194,350),(203,350),(204,361),(196,368),(183,364),(177,356)], 'blue')
        _polygon(p, [(185,363),(196,366),(199,373),(194,380),(185,378),(181,372)], 'outline')
        _polygon(p, [(187,364),(193,367),(195,372),(192,376),(187,374),(185,370)], 'skin_light')


def draw_companion(p, pose):
    p.save()
    p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    _part(p, 'shadow')
    p.save()
    # Extend the concealed trouser top beneath the moving hoodie.
    p.setClipRect(QRectF(90, 326, 130, 14))
    p.translate(0, -6)
    _part(p, 'legs')
    p.restore()
    _part(p, 'legs')
    p.translate(0, -pose.breath * 2)
    _part(p, 'body')
    # Fill clothing beneath independently posed sleeves.
    _polygon(p, [(205,310),(222,315),(219,341),(202,340),(194,326)], 'white')
    _polygon(p, [(291,316),(310,325),(321,345),(306,365),(293,347)], 'white')
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
    _arms(p, pose)
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

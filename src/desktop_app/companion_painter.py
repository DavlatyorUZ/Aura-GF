"""Code-drawn pixel character: articulated limbs, hood, hair and facial features.

Coordinates are in a 104 by 144 logical pixel canvas. Every shape is painted
from geometry; no textures, image assets, network or audio inputs are used.
"""

from dataclasses import dataclass
import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPen, QPolygonF

from desktop_app.themes import COMPANION_COLORS as C


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


def render_companion(pose: CompanionPose) -> QImage:
    """Rasterise procedural geometry on a consistent logical pixel grid."""
    canvas = QImage(104, 144, QImage.Format.Format_ARGB32_Premultiplied)
    canvas.fill(Qt.GlobalColor.transparent)
    painter = QPainter(canvas)
    try:
        draw_companion(painter, pose)
    finally:
        painter.end()
    return canvas


def _poly(p: QPainter, points, colour, outline=None):
    p.setBrush(QColor(C[colour]))
    p.setPen(QPen(QColor(C[outline]), 1, Qt.PenStyle.SolidLine,
                  Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin)
             if outline else Qt.PenStyle.NoPen)
    p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in points]))


def _box(p, x, y, width, height, colour):
    p.fillRect(QRectF(x, y, width, height), QColor(C[colour]))


def _boot(p, x, y):
    _poly(p, [(x+2,y),(x+14,y),(x+14,y+6),(x+17,y+6),(x+17,y+16),
              (x+15,y+18),(x,y+18),(x-2,y+15),(x-2,y+7),(x,y+7)], 'blue_dark', 'ink')
    _box(p, x+1, y+1, 12, 5, 'white')
    _box(p, x+1, y+7, 13, 6, 'blue_light')
    _box(p, x+3, y+7, 9, 4, 'snow_shadow')
    _box(p, x, y+14, 15, 2, 'blue')
    _box(p, x+1, y+16, 14, 1, 'ice')
    _box(p, x-1, y+7, 3, 5, 'cyan')


def _eye(p, x, y, pose):
    height = max(1, round((1 - pose.blink) * (12 if pose.attentive else 11)))
    if height <= 3:
        _poly(p, [(x-1,y+4),(x+2,y+6),(x+6,y+6),(x+9,y+3),
                  (x+9,y+5),(x+7,y+8),(x+2,y+8),(x-1,y+6)], 'ink')
        return
    top = y + (11-height)//2
    _poly(p, [(x-2,top),(x,top-2),(x+7,top-2),(x+9,top),(x+9,top+height-2),
              (x+7,top+height),(x+1,top+height),(x-1,top+height-2)], 'white', 'ink')
    pupil_x = x + 2 + pose.gaze
    _box(p, pupil_x, top, 5, height-1, 'blue_dark')
    _box(p, pupil_x+1, top+height//2, 4, height//2, 'blue')
    _box(p, pupil_x+1, top+height-3, 3, 2, 'cyan')
    _box(p, pupil_x, top, 2, 3, 'white')
    _box(p, pupil_x+3, top+height-4, 1, 2, 'white')
    _box(p, x-1, top-2, 9, 2, 'ink')
    _box(p, x-2, top-1, 2, 3, 'ink')
    if pose.expression in ('concerned', 'sad'):
        _poly(p, [(x-1,top-5),(x+8,top-3),(x+8,top-2),(x-1,top-4)], 'outline')


def _arm(p, pose):
    """The left sleeve and hand pivot together around the shoulder."""
    p.save()
    p.translate(33, 91)
    waving = pose.wave > 0
    p.rotate(-12 - math.sin(pose.wave * math.pi * 5) * 15 if waving else -3)
    if waving:
        _poly(p, [(-2,1),(-9,0),(-14,-5),(-14,-13),(-10,-16),(-5,-13),
                  (-3,-8),(4,-6),(6,0),(3,5)], 'white', 'ink')
        _poly(p, [(-14,-12),(-12,-16),(-5,-16),(-2,-11),(-4,-7),(-11,-7)], 'blue', 'outline')
        _poly(p, [(-12,-16),(-13,-20),(-11,-22),(-9,-18),(-9,-24),(-7,-24),
                  (-6,-19),(-5,-24),(-3,-23),(-3,-18),(-1,-21),(1,-19),
                  (-1,-14),(-5,-12),(-10,-13)], 'skin', 'ink')
        _box(p, -10, -18, 6, 3, 'skin_light')
        _poly(p, [(-12,-5),(-7,-3),(-2,-4),(1,1),(-4,3),(-10,0)], 'snow_shadow')
    else:
        _poly(p, [(0,-5),(-5,-4),(-10,2),(-12,12),(-9,16),(-2,17),
                  (3,13),(5,4)], 'white', 'ink')
        _poly(p, [(-11,10),(-4,12),(1,9),(3,13),(-2,18),(-9,17)], 'blue', 'outline')
        _poly(p, [(-8,17),(-2,18),(-1,21),(-4,23),(-9,21),(-10,18)], 'skin', 'ink')
        _box(p, -7, 18, 4, 2, 'skin_light')
        _poly(p, [(-7,1),(-9,8),(-7,11),(-4,11),(-2,0)], 'snow_shadow')
    p.restore()


def draw_companion(p: QPainter, pose: CompanionPose):
    """Paint an original blue-haired, headphone-wearing chibi companion."""
    p.save()
    p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    # Grounding shadow, boots and legs remain anchored while the torso breathes.
    _box(p, 28, 135, 48, 2, 'shadow')
    _box(p, 23, 137, 57, 2, 'shadow')
    _box(p, 29, 139, 45, 1, 'shadow')
    _poly(p, [(35,109),(49,109),(48,125),(44,130),(35,129),(33,121)], 'ink')
    _poly(p, [(54,109),(67,109),(69,125),(66,130),(56,130)], 'ink')
    _box(p, 36, 114, 9, 12, 'outline')
    _box(p, 57, 114, 8, 12, 'outline')
    _boot(p, 33, 119)
    _boot(p, 55, 119)

    p.translate(0, -pose.breath)
    # Hoodie torso and the relaxed right arm.
    _poly(p, [(67,87),(74,90),(79,101),(83,109),(82,115),(77,119),
              (71,116),(68,108),(63,99)], 'blue', 'ink')
    _poly(p, [(70,91),(73,93),(76,102),(70,106),(67,99)], 'white')
    _poly(p, [(76,112),(82,111),(83,115),(79,119),(74,117)], 'skin', 'ink')
    _box(p, 77, 113, 4, 3, 'skin_light')
    _poly(p, [(36,84),(65,84),(70,91),(70,101),(74,111),(69,116),
              (59,118),(39,116),(31,112),(33,100),(31,92)], 'white', 'ink')
    _poly(p, [(34,93),(38,96),(38,103),(35,110),(43,114),(34,113),(32,110)], 'snow_shadow')
    _poly(p, [(64,96),(69,94),(68,103),(72,110),(68,114),(61,114)], 'snow_shadow')
    _poly(p, [(35,106),(40,104),(43,107),(47,107),(47,109),(56,109),
              (56,106),(64,106),(66,109),(72,108),(73,113),(66,117),
              (57,118),(38,116),(31,112)], 'blue')
    _box(p, 41, 112, 20, 3, 'blue_light')
    _poly(p, [(43,98),(57,98),(59,103),(42,103)], 'snow_shadow')
    _poly(p, [(38,84),(44,82),(53,88),(62,82),(67,85),(62,91),
              (54,94),(46,90)], 'blue_dark', 'ink')
    _poly(p, [(39,84),(44,83),(52,89),(51,91),(43,88)], 'white')
    _poly(p, [(55,89),(62,83),(65,85),(60,89)], 'white')
    _box(p, 42, 91, 2, 8, 'blue')
    _box(p, 60, 91, 2, 10, 'blue')
    _box(p, 42, 98, 2, 2, 'blue_dark')
    _box(p, 60, 100, 2, 2, 'blue_dark')
    _arm(p, pose)

    # The headphones sit behind the thick, stepped snow hood.
    _poly(p, [(15,36),(24,34),(29,38),(28,59),(24,66),(16,64),
              (11,58),(9,49),(10,42)], 'blue', 'ink')
    _poly(p, [(79,35),(86,38),(92,44),(93,56),(90,63),(83,65),
              (77,60),(76,42)], 'blue', 'ink')
    _box(p, 12, 43, 5, 12, 'blue_light')
    _poly(p, [(17,41),(21,41),(19,47),(17,47),(15,53),(14,48)], 'cyan')
    _box(p, 86, 43, 3, 13, 'blue_light')
    _poly(p, [(83,40),(86,42),(87,49),(84,48),(84,44),(82,44)], 'cyan')
    _poly(p, [(45,5),(58,5),(58,7),(64,7),(64,10),(68,10),(68,15),
              (75,18),(75,20),(81,24),(81,28),(85,34),(87,43),
              (85,61),(81,74),(75,82),(67,86),(35,86),(27,81),
              (22,74),(18,61),(17,46),(20,33),(24,26),(29,21),
              (36,17),(38,12),(41,9),(45,9)], 'white', 'ink')
    _poly(p, [(40,12),(45,8),(57,8),(62,10),(65,14),(66,19),
              (58,17),(51,17),(46,19),(38,19)], 'blue_light')
    _box(p, 46, 7, 11, 2, 'blue')
    _poly(p, [(20,40),(23,33),(28,28),(28,34),(25,43),(23,54),
              (25,68),(31,76),(36,79),(35,83),(28,79),(23,72),(20,60)], 'snow_shadow')
    _poly(p, [(79,31),(82,38),(83,52),(81,64),(77,75),(70,81),
              (66,83),(65,79),(73,73),(77,64),(79,50)], 'snow_shadow')
    _poly(p, [(27,49),(30,40),(37,33),(46,29),(58,29),(68,32),
              (75,38),(78,48),(78,66),(73,78),(66,84),(37,84),
              (29,77),(25,67),(24,56)], 'blue_dark', 'ink')
    _poly(p, [(32,45),(37,38),(47,34),(59,34),(68,38),(73,46),
              (75,65),(69,78),(64,81),(39,81),(32,76),(28,66)], 'hair_shadow', 'outline')

    # Bobbed hair moves by one logical pixel independently of the face.
    h = pose.hair
    _poly(p, [(29,48),(36,48),(35,67),(38,78),(34+h,81),(29+h,78),
              (26+h,69),(26,58)], 'hair', 'outline')
    _poly(p, [(68,45),(74,48),(77,60),(80+h,66),(76+h,68),
              (74+h,77),(69,81),(65,79),(69,68)], 'hair', 'outline')
    _poly(p, [(29,59),(31,57),(30,71),(34,77),(31,77),(28,71)], 'hair_light')
    _poly(p, [(73,54),(75,61),(78+h,65),(75+h,65),(72,61)], 'hair_light')
    _poly(p, [(34,48),(42,42),(60,43),(68,49),(71,59),(70,72),
              (65,79),(59,82),(45,82),(38,78),(33,71),(32,60)], 'skin', 'outline')
    _poly(p, [(35,56),(39,49),(49,46),(61,47),(66,53),(67,70),
              (62,77),(44,78),(37,72)], 'skin_light')
    _box(p, 35, 74, 6, 2, 'blush')
    _box(p, 64, 74, 6, 2, 'blush')
    _eye(p, 38, 62, pose)
    _eye(p, 61, 62, pose)
    if pose.mouth > 0.1 or pose.expression in ('happy', 'excited', 'surprised'):
        opening = max(3, round(pose.mouth * 6))
        _poly(p, [(50,76),(56,76),(56,76+opening),(54,77+opening),
                  (51,76+opening)], 'mouth')
        _box(p, 52, 77+opening-2, 3, 2, 'tongue')
        _box(p, 51, 76, 4, 1, 'white')
    else:
        _poly(p, [(50,77),(52,78),(54,78),(56,76),(56,78),(54,79),(52,79)], 'mouth')

    # Separate locks and pixel highlights keep the forehead and eyes readable.
    _poly(p, [(30,48),(34,40),(41,36),(49,34),(59,35),(66,38),
              (71,43),(74,53),(76,59),(71,57),(67,50),(65,45),
              (62,55),(59,62),(53,61),(49,55),(46,46),(42,52),
              (36,57),(29,59)], 'hair', 'outline')
    _poly(p, [(32,47),(36,41),(43,38),(47,38),(44,43),(40,47),
              (38,53),(33,56),(30,56)], 'hair_light')
    _poly(p, [(49,37),(56,36),(61,38),(63,43),(61,52),(58,59),
              (54,58),(51,51)], 'hair_light')
    _poly(p, [(63,39),(67,41),(70,47),(72,54),(68,49),(66,44)], 'hair_shadow')
    _poly(p, [(46,43),(49,52),(53,59),(58,61),(54,61),(50,57)], 'hair_shadow')
    _box(p, 35, 43, 3, 2, 'white')
    _box(p, 38, 41, 3, 2, 'white')
    _box(p, 51, 40, 5, 2, 'white')
    _box(p, 56, 41, 2, 2, 'white')
    _box(p, 68, 47, 2, 3, 'ice')

    if pose.thinking:
        for index in range(3):
            _box(p, 82 + index*4, 77 - (1 if pose.gaze == index-1 else 0), 2, 2, 'blue_light')
    if pose.wave:
        _box(p, 10, 82, 2, 8, 'blue_light')
        _box(p, 7, 85, 8, 2, 'blue_light')
        _box(p, 88, 95, 2, 6, 'ice')
        _box(p, 86, 97, 6, 2, 'ice')
    p.restore()

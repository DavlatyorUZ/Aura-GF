"""Articulated pixel geometry for the local blue-haired companion.

The 104 by 144 canvas uses a stepped silhouette and discrete colour ramps.
Each part is painted locally; character textures and image files are absent.
"""

from dataclasses import dataclass, replace
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
    """Rasterise independently articulated parts without smoothing the pixel grid."""
    canvas = QImage(104, 144, QImage.Format.Format_ARGB32_Premultiplied)
    canvas.fill(Qt.GlobalColor.transparent)
    painter = QPainter(canvas)
    try:
        draw_companion(painter, pose)
    finally:
        painter.end()
    return canvas


def _poly(p, points, colour, outline=None, thickness=1):
    p.setBrush(QColor(C[colour]))
    p.setPen(QPen(QColor(C[outline]), thickness, Qt.PenStyle.SolidLine,
                  Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin)
             if outline else Qt.PenStyle.NoPen)
    p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in points]))


def _box(p, x, y, width, height, colour):
    p.fillRect(QRectF(x, y, width, height), QColor(C[colour]))


def _boot(p, x):
    _poly(p, [(x+2,124),(x+12,124),(x+12,127),(x+15,127),(x+15,137),
              (x+13,139),(x,139),(x-1,136),(x-1,129),(x+1,129)], 'blue_dark', 'ink', 1.5)
    _box(p, x+2, 123, 10, 5, 'white')
    _box(p, x+2, 126, 10, 2, 'snow_shadow')
    _poly(p, [(x+1,129),(x+12,129),(x+13,132),(x+12,136),(x+1,136)], 'white')
    _box(p, x+1, 135, 12, 2, 'blue_light')
    _box(p, x, 138, 13, 1, 'blue')
    _box(p, x-1, 128, 4, 6, 'blue')
    _box(p, x, 129, 2, 3, 'cyan')
    _box(p, x+12, 128, 3, 5, 'blue_light')
    _box(p, x+12, 129, 2, 3, 'ice')


def _eye(p, x, y, pose, mirrored=False):
    """Stepped oval iris, dark upper lashes and a luminous lower iris."""
    if pose.expression == 'happy' and pose.blink < 0.6:
        _poly(p, [(x-1, y+5), (x+2, y+2), (x+8, y+2), (x+11, y+5),
                  (x+10, y+7), (x+7, y+4), (x+3, y+4), (x, y+7)], 'ink')
        _poly(p, [(x+1, y-4), (x+8, y-4), (x+8, y-3), (x+1, y-3)], 'hair_shadow')
        return
    eye_h = 14 if pose.expression == 'surprised' else 13 if pose.attentive else 12
    height = max(1, round((1 - pose.blink) * eye_h))
    if height < 4:
        _poly(p, [(x,y+4),(x+3,y+6),(x+7,y+6),(x+10,y+3),
                  (x+10,y+5),(x+7,y+8),(x+3,y+8),(x,y+6)], 'ink')
        return
    top = y + (12 - height)//2
    p.save()
    p.translate(x, top)
    p.scale(1, height / 12)
    _poly(p, [(0,2),(2,0),(8,0),(10,2),(11,5),(10,10),(8,12),
              (3,12),(1,10),(0,7)], 'white')
    gaze = max(-1, min(1, pose.gaze))
    p.save()
    p.translate(gaze, 0)
    _poly(p, [(3,1),(7,1),(9,3),(9,9),(7,12),(4,12),(2,10),(2,4)], 'blue_dark')
    _poly(p, [(3,7),(8,7),(8,10),(6,12),(4,11),(3,10)], 'blue')
    _box(p, 4, 9, 4, 2, 'blue_light')
    _box(p, 5, 10, 2, 2, 'cyan')
    _poly(p, [(5,2),(7,3),(7,7),(6,9),(4,7),(4,4)], 'ink')
    _box(p, 3, 2, 3, 4, 'white')
    _box(p, 3, 6, 1, 1, 'ice')
    _box(p, 7, 8, 2, 2, 'white')
    if pose.expression == 'excited':
        _box(p, 5, 5, 2, 2, 'ice')
    p.restore()
    _poly(p, [(-1,3),(0,0),(2,-2),(7,-2),(10,0),(11,3),(9,2),
              (7,0),(3,0),(1,2),(1,5),(0,6)], 'ink')
    if mirrored:
        _poly(p, [(8,-1),(11,-2),(11,1),(10,3)], 'ink')
    else:
        _poly(p, [(-2,-1),(1,0),(2,2),(0,3)], 'ink')
    p.restore()
    if pose.expression in ('concerned', 'sad'):
        _poly(p, [(x,y-5),(x+8,y-3),(x+8,y-2),(x,y-4)], 'hair_shadow')
    elif pose.expression == 'surprised':
        _poly(p, [(x,y-7),(x+8,y-7),(x+8,y-6),(x,y-6)], 'hair_shadow')
    elif pose.expression == 'excited':
        _poly(p, [(x+1,y-6),(x+8,y-5),(x+8,y-4),(x+1,y-5)], 'hair_shadow')
    elif pose.expression == 'curious':
        if mirrored:
            _poly(p, [(x,y-6),(x+8,y-4),(x+8,y-3),(x,y-5)], 'hair_shadow')
        else:
            _poly(p, [(x,y-4),(x+8,y-4),(x+8,y-3),(x,y-3)], 'hair_shadow')
    elif pose.expression == 'thinking':
        _poly(p, [(x,y-4),(x+8,y-5),(x+8,y-4),(x,y-3)], 'hair_shadow')


def _greeting_arm(p, pose):
    """A raised hand rests beside the cheek and pivots during a greeting."""
    p.save()
    p.translate(35, 96)
    if pose.wave:
        # The envelope joins the resting pose at both ends of the gesture.
        p.rotate(math.sin(pose.wave * math.pi) * math.sin(pose.wave * math.pi * 6) * 12)
    _poly(p, [(2,-7),(-4,-8),(-10,-8),(-14,-6),(-14,0),(-11,5),
              (-6,8),(-1,7),(3,3),(5,-3)], 'white', 'ink', 1.5)
    _poly(p, [(-13,-1),(-9,3),(-4,4),(0,1),(1,-4),(3,-3),(2,3),
              (-2,6),(-6,6),(-10,3)], 'snow_shadow')
    _poly(p, [(-13,-7),(-10,-10),(-3,-10),(1,-7),(0,-3),
              (-4,-1),(-9,-2),(-12,-4)], 'blue_dark', 'outline')
    _poly(p, [(-12,-8),(-9,-9),(-3,-9),(-1,-7),(-3,-5),(-9,-5)], 'blue')
    _poly(p, [(-11,-10),(-11,-13),(-13,-15),(-13,-18),(-11,-18),
              (-9,-15),(-9,-20),(-7,-21),(-6,-16),(-5,-20),(-3,-19),
              (-3,-15),(-1,-17),(1,-16),(0,-12),(-3,-9),(-8,-9)], 'skin', 'ink')
    _poly(p, [(-10,-14),(-8,-13),(-7,-17),(-5,-14),(-3,-15),
              (-2,-13),(-4,-10),(-8,-10)], 'skin_light')
    _box(p, -11, -12, 2, 2, 'skin_shadow')
    p.restore()


def _hood(p):
    # Ear cups and the blue crown sit behind the soft white hood.
    _poly(p, [(7,34),(13,31),(20,31),(23,36),(22,53),(17,59),
              (9,59),(4,54),(2,48),(2,40)], 'blue', 'ink', 1.5)
    _poly(p, [(4,41),(6,37),(10,35),(13,35),(10,42),(10,53),(7,54),(4,49)], 'blue_light')
    _poly(p, [(11,37),(16,37),(14,41),(12,42),(11,46),(9,46),(9,42)], 'cyan')
    _poly(p, [(86,33),(93,34),(98,39),(101,44),(101,52),(97,58),
              (90,60),(85,55)], 'blue', 'ink', 1.5)
    _poly(p, [(94,38),(98,42),(99,50),(96,53),(94,48)], 'blue_light')
    _poly(p, [(90,38),(93,39),(94,45),(92,46),(91,42),(89,42)], 'cyan')
    _poly(p, [(37,16),(39,10),(43,6),(48,4),(59,4),(64,7),
              (68,12),(70,17)], 'blue_light', 'ink', 1.5)
    _box(p, 48, 5, 11, 2, 'blue')
    _poly(p, [(18,30),(20,24),(24,20),(29,17),(36,15),(40,15),
              (40,18),(47,18),(47,16),(56,15),(65,15),(65,16),
              (74,16),(80,19),(85,23),(88,28),(90,36),(90,43),
              (94,53),(95,63),(92,72),(86,80),(79,84),(68,85),
              (26,81),(18,77),(14,71),(11,62),(13,51),(16,42)], 'white', 'ink', 1.5)
    _poly(p, [(19,27),(22,23),(22,32),(25,34),(23,38),(20,39),(18,34)], 'snow_shadow')
    _poly(p, [(88,39),(90,47),(93,57),(92,66),(88,74),(82,79),
              (74,81),(75,77),(82,73),(87,65),(88,54),(85,44)], 'snow_shadow')
    _poly(p, [(15,53),(19,45),(23,38),(30,32),(38,28),(46,26),
              (59,26),(68,29),(77,35),(82,42),(86,53),(87,65),
              (83,75),(76,81),(66,83),(29,80),(20,75),(16,68)], 'blue_dark', 'ink', 1.5)
    _poly(p, [(23,45),(30,36),(39,31),(48,29),(60,29),(69,33),
              (76,39),(80,47),(84,61),(82,70),(77,77),(67,81),
              (29,78),(22,72),(20,63)], 'hair_shadow')
    _poly(p, [(13,54),(17,45),(23,37),(31,31),(41,27),(47,25),
              (59,25),(63,27),(46,27),(36,31),(28,37),(22,45),
              (18,55),(17,65),(20,72),(18,71),(15,65)], 'snow_shadow')


def _head(p, pose):
    _hood(p)
    h = pose.hair
    # Back locks frame a broad, rounded face.
    _poly(p, [(25,49),(33,48),(33,65),(36,76),(32+h,79),(27+h,77),
              (23+h,71),(22,63)], 'hair', 'outline')
    _poly(p, [(73,43),(78,49),(79,59),(83+h,65),(88+h,66),
              (84+h,69),(80,68),(79,75),(75,80),(69,82),(65,79)], 'hair', 'outline')
    _poly(p, [(25,59),(27,57),(27,69),(31+h,75),(30+h,77),(26,73)], 'hair_light')
    _poly(p, [(78,60),(81+h,65),(85+h,66),(80+h,66)], 'hair_light')
    _poly(p, [(34,52),(39,48),(47,46),(62,47),(70,52),(75,59),
              (75,70),(72,76),(67,80),(59,82),(47,82),(39,79),
              (34,75),(31,68),(31,60)], 'skin', 'outline')
    _poly(p, [(35,58),(40,52),(48,49),(62,50),(69,54),(72,60),
              (72,71),(68,76),(61,79),(46,79),(38,75),(34,68)], 'skin_light')
    _box(p, 34, 72, 6, 3, 'blush')
    _box(p, 69, 72, 5, 3, 'blush')
    _box(p, 35, 72, 2, 1, 'skin')
    _box(p, 71, 72, 2, 1, 'skin')
    if pose.expression in ('happy', 'excited'):
        _box(p, 33, 71, 8, 4, 'blush')
        _box(p, 68, 71, 7, 4, 'blush')
        _box(p, 35, 71, 2, 1, 'white')
        _box(p, 70, 71, 2, 1, 'white')
    _eye(p, 36, 61, pose)
    _eye(p, 62, 61, pose, mirrored=True)
    if pose.mouth > 0.05:
        open_h = round(pose.mouth * 5)
        w = 2 + round(pose.mouth * 2)
        _poly(p, [(53-w, 74), (53+w, 74), (54+w, 75+open_h),
                  (53, 76+open_h), (52-w, 75+open_h)], 'mouth')
        if open_h >= 2:
            _box(p, 52, 75 + open_h - 1, 3, 2, 'tongue')
            _box(p, 52, 74, 3, 1, 'white')
        _box(p, 51, 73, 4, 1, 'blush')
    elif pose.thinking or pose.expression == 'thinking':
        _box(p, 52, 75, 3, 2, 'mouth')
        _box(p, 53, 75, 1, 1, 'snow_shadow')
    elif pose.expression == 'surprised':
        _box(p, 52, 74, 3, 4, 'mouth')
        _box(p, 53, 75, 1, 2, 'tongue')
    elif pose.expression in ('happy', 'excited'):
        _poly(p, [(49,74),(51,76),(55,76),(57,74),(55,77),(51,77)], 'mouth')
        _box(p, 52, 75, 3, 1, 'blush')
    elif pose.expression in ('sad', 'concerned'):
        _poly(p, [(50,76),(53,74),(56,76),(53,75)], 'mouth')
    else:
        _poly(p, [(50,75),(53,76),(56,75),(53,77)], 'mouth')
    # Long side locks, separated curved fringe and a tapered central lock.
    _poly(p, [(23,49),(28,42),(35,37),(43,33),(51,32),(60,32),
              (67,35),(72,40),(75,46),(77,55),(80,62),(76,61),
              (72,57),(69,48),(67,46),(66,54),(63,58),(59,64),
              (54,63),(50,58),(47,50),(45,49),(42,54),(36,58),
              (30,62),(23,64),(19+h,64),(24+h,60),(25,54),(22,58)], 'hair', 'outline')
    _poly(p, [(26,49),(30,43),(36,39),(42,36),(46,36),(43,40),
              (38,42),(35,47),(32,52),(28,56),(25,57)], 'hair_light')
    _poly(p, [(48,37),(52,34),(58,34),(62,37),(64,41),(64,49),
              (61,56),(58,61),(54,59),(51,53),(49,46)], 'hair_light')
    _poly(p, [(49,44),(51,52),(55,59),(58,61),(61,58),(59,63),
              (55,62),(51,57),(48,50)], 'hair_shadow')
    _poly(p, [(66,38),(70,42),(73,49),(75,58),(72,54),(69,46)], 'hair_light')
    _poly(p, [(29,53),(31,48),(31,52),(28,58),(24,60)], 'blue_light')
    _box(p, 34, 43, 3, 2, 'white')
    _box(p, 38, 41, 3, 3, 'white')
    _box(p, 50, 41, 6, 2, 'white')
    _box(p, 56, 42, 2, 2, 'white')
    _box(p, 68, 44, 2, 4, 'white')
    _poly(p, [(75,68),(77,67),(76,75),(72,79),(68,80),(72,76)], 'hair_light')


def draw_companion(p: QPainter, pose: CompanionPose):
    """Paint the full character with a steady stance and a friendly raised hand."""
    pose = replace(pose, blink=max(0, min(1, pose.blink)), mouth=max(0, min(1, pose.mouth)))
    p.save()
    p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    _box(p, 29, 137, 44, 4, 'shadow')
    _box(p, 24, 138, 56, 2, 'shadow')
    _box(p, 34, 141, 34, 1, 'shadow')
    _poly(p, [(39,107),(51,109),(50,116),(48,126),(39,126),(38,118)], 'ink', 'ink')
    _poly(p, [(54,109),(66,108),(67,117),(67,126),(57,126),(55,118)], 'ink', 'ink')
    _poly(p, [(40,112),(48,113),(47,118),(46,124),(40,123)], 'outline')
    _poly(p, [(57,113),(64,112),(65,123),(59,124)], 'outline')
    _boot(p, 36)
    _boot(p, 54)
    p.translate(0, -pose.breath)
    # Loose sleeve, tiny hand and the oversized hoodie.
    _poly(p, [(65,88),(71,91),(76,96),(80,102),(82,109),(80,113),
              (74,115),(70,110),(67,103),(62,99)], 'white', 'ink', 1.5)
    _poly(p, [(75,109),(81,108),(83,111),(81,114),(77,116),(73,114)], 'skin', 'ink')
    _poly(p, [(74,101),(79,101),(81,106),(81,110),(76,112),(70,110)], 'blue', 'outline')
    _box(p, 75, 112, 3, 2, 'skin_light')
    _poly(p, [(39,83),(61,83),(66,88),(68,97),(69,102),(72,110),
              (70,114),(65,116),(55,114),(48,114),(39,116),(33,113),
              (32,108),(35,99),(35,91)], 'white', 'ink', 1.5)
    _poly(p, [(35,94),(38,94),(37,101),(35,105),(35,109),(32,109)], 'snow_shadow')
    _poly(p, [(64,92),(66,96),(66,103),(69,109),(65,109),(63,102)], 'snow_shadow')
    _poly(p, [(34,104),(39,102),(42,102),(42,104),(46,104),(48,107),
              (53,107),(55,109),(59,109),(59,106),(64,106),(65,104),
              (68,105),(71,111),(69,114),(64,115),(55,112),(47,112),
              (41,114),(35,113),(33,111)], 'blue_light')
    _poly(p, [(33,109),(37,109),(37,111),(44,110),(49,111),(56,111),
              (60,113),(69,111),(70,114),(65,116),(55,114),(47,113),
              (39,116),(34,113)], 'blue')
    _head(p, pose)
    # Collar overlaps the hair ends, while the greeting hand overlaps the hood.
    _poly(p, [(38,82),(44,81),(51,85),(55,86),(61,82),(66,83),
              (66,87),(60,89),(54,92),(48,89),(41,88),(37,85)], 'blue_dark', 'ink')
    _poly(p, [(38,82),(43,81),(48,83),(51,87),(49,88),(44,85),(39,85)], 'white')
    _poly(p, [(55,87),(60,83),(65,82),(67,84),(64,87),(59,88)], 'white')
    _box(p, 42, 89, 2, 8, 'blue_dark')
    _box(p, 43, 89, 1, 6, 'blue_light')
    _box(p, 61, 89, 2, 9, 'blue_dark')
    _box(p, 61, 89, 1, 7, 'blue_light')
    _greeting_arm(p, pose)
    if pose.thinking:
        shift = max(-1, min(1, pose.gaze))
        _box(p, 86, 44 - shift, 2, 2, 'blue_light')
        _box(p, 89, 36 + shift, 3, 3, 'cyan')
        _box(p, 90, 37 + shift, 1, 1, 'ice')
        _box(p, 93, 26 - shift, 4, 4, 'blue_light')
        _box(p, 94, 27 - shift, 2, 2, 'ice')
        for index in range(3):
            _box(p, 86 + index*4, 81 - (1 if pose.gaze == index-1 else 0), 2, 2, 'blue_light')
    if pose.wave:
        _box(p, 5, 81, 2, 8, 'blue_light')
        _box(p, 2, 84, 8, 2, 'blue_light')
        _box(p, 95, 93, 2, 8, 'blue_light')
        _box(p, 92, 96, 8, 2, 'blue_light')
    p.restore()

"""Independently articulated vector contours for the eight companion activities."""
from dataclasses import dataclass
from functools import lru_cache
import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPainterPath, QPolygonF
from desktop_app.companion_geometry import POSES, FEATURES
from desktop_app.themes import COMPANION_COLORS as C, COMPANION_REFERENCE_COLOURS

CANVAS_WIDTH, CANVAS_HEIGHT = 234, 268


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
    state: str = 'idle'
    articulate: bool = False


@lru_cache(maxsize=len(POSES))
def _paths(state):
    """Compile each activity's paths once, retaining holes and pixel corners."""
    parts = {}
    for name, surfaces in POSES[state].items():
        parts[name] = []
        for colour, outlines in surfaces:
            path = QPainterPath()
            path.setFillRule(Qt.FillRule.OddEvenFill)
            for outline in outlines:
                path.addPolygon(QPolygonF([QPointF(x,y) for x,y in outline]))
                path.closeSubpath()
            parts[name].append((QColor(COMPANION_REFERENCE_COLOURS[colour]),path))
    return parts


def _part(p, state, name):
    for colour,path in _paths(state)[name]:
        p.fillPath(path,colour)


def _box(p,x,y,width,height,colour):
    p.fillRect(QRectF(x,y,width,height),QColor(C[colour]))


def _polygon(p,points,colour):
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(C[colour]))
    p.drawPolygon(QPolygonF([QPointF(x,y) for x,y in points]))


def _state(pose):
    if pose.state in POSES and pose.state != 'idle':
        return pose.state
    if pose.thinking or pose.activity == 'thinking' or pose.expression == 'thinking':
        return 'thinking'
    if pose.activity == 'launching':
        return 'launching'
    return pose.state if pose.state in POSES else 'idle'


def _eyes(p,state,pose):
    blink = max(0,min(1,pose.blink)) if state not in ('asleep','launching','dictating') else 0
    gaze=max(-1,min(1,pose.gaze)) if state=="thinking" else 0
    if blink or gaze:
        _part(p,state,'eyes_base')
    for name,(x,y,width,height) in zip(('left_eye','right_eye'),FEATURES[state]['eyes']):
        if blink > .85:
            line=y+round(height*.6)
            _polygon(p,[(x+2,line),(x+8,line+2),(x+width-7,line+1),(x+width-2,line-1),
                        (x+width-2,line+1),(x+width-7,line+3),(x+8,line+4),(x+2,line+2)],'ink')
            continue
        p.save()
        p.translate(gaze,0)
        p.translate(x+width/2,y+height/2)
        p.scale(1,max(.07,1-blink))
        p.translate(-x-width/2,-y-height/2)
        _part(p,state,name)
        p.restore()
    if pose.attentive or pose.expression == 'curious':
        _polygon(p,[(80,104),(88,101),(100,102),(100,104),(88,103),(80,106)],'hair_shadow')
    elif pose.expression in ('sad','concerned'):
        slope=3 if pose.expression == 'sad' else 1
        _polygon(p,[(80,104),(101,99-slope),(101,102-slope),(80,107)],'hair_shadow')
        _polygon(p,[(132,99-slope),(152,104),(152,107),(132,102-slope)],'hair_shadow')


def _mouth(p,state,pose):
    openness=max(0,min(1,pose.mouth))
    expressive=pose.expression in ('sad','concerned','surprised','excited')
    if not pose.articulate and openness == 0 and not expressive:
        _part(p,state,'mouth')
        return
    _part(p,state,'mouth_base')
    x,y,width,height=FEATURES[state]['mouth']
    centre=x+width/2
    if openness < .08 and pose.expression not in ('surprised','excited'):
        bend=-1 if pose.expression in ('sad','concerned') else 1
        _polygon(p,[(centre-5,y+3),(centre,y+3+bend),(centre+5,y+3),
                    (centre+5,y+5),(centre,y+5+bend),(centre-5,y+5)],'mouth')
        return
    h=4+round(openness*8)
    w=10+round(openness*5)
    if pose.expression == 'surprised':w,h=10,13
    if pose.expression == 'excited':w,h=17,max(10,h)
    left=round(centre-w/2)
    _polygon(p,[(left+2,y+1),(left+w-2,y+1),(left+w,y+3),(left+w-2,y+h),
                (left+3,y+h),(left,y+3)],'mouth')
    _box(p,left+4,y+h-3,max(3,w-8),3,'tongue')
    if openness>.45:_box(p,left+3,y+2,w-6,2,'white')


def _phone(p,phase):
    """Two inward sleeves and independently tapping fingers hold a small phone."""
    _polygon(p,[(94,163),(83,173),(74,187),(78,201),(96,208),(109,200),(108,186),(99,180)],'outline')
    _polygon(p,[(94,169),(87,177),(81,188),(84,197),(96,201),(104,196),(103,190),(95,184)],'white')
    _polygon(p,[(141,163),(153,173),(162,188),(158,202),(139,208),(128,199),(130,185),(141,179)],'outline')
    _polygon(p,[(141,169),(149,178),(155,189),(152,198),(140,201),(134,196),(135,190),(145,184)],'white')
    _box(p,99,184,12,17,'blue');_box(p,128,184,12,17,'blue')
    lift=round(math.sin(phase*math.tau))
    _polygon(p,[(107,169+lift),(132,169+lift),(136,173+lift),(136,201+lift),
                (132,205+lift),(107,205+lift),(103,201+lift),(103,173+lift)],'outline')
    _box(p,107,174+lift,25,24,'blue_light')
    _box(p,112,178+lift,15,3,'white')
    _box(p,111+round(phase*3)%3*5,185+lift,4,7,'blue')
    _box(p,117,200+lift,5,2,'white')
    _polygon(p,[(100,186),(106,185),(110,189),(110,197),(105,200),(99,195)],'skin_light')
    _polygon(p,[(133,186),(139,185),(143,190),(141,198),(136,201),(132,195)],'skin_light')


def _waveforms(p,state,phase):
    for x,y,width,height in FEATURES[state]['waveforms']:
        centre=y+height/2
        for index,column in enumerate(range(x,x+width,4)):
            scale=1+.18*math.sin(phase*math.tau)*math.cos(index*.9+phase*math.pi)
            p.save();p.setClipRect(QRectF(column,y-8,4,height+16))
            p.translate(0,centre);p.scale(1,scale);p.translate(0,-centre)
            _part(p,state,'waveform');p.restore()


def draw_companion(p,pose):
    state=_state(pose)
    phase=max(0,min(1,pose.phase))
    p.save()
    p.setRenderHint(QPainter.RenderHint.Antialiasing,False)
    _part(p,state,'shadow')
    # A concealed overlap keeps the trouser/hoodie join opaque during breathing.
    p.save();p.setClipRect(QRectF(65,210,115,14));p.translate(0,-4)
    _part(p,state,'legs');p.restore()
    _part(p,state,'legs')
    p.save()
    lift=pose.breath+(1 if state=='thinking' and phase>.5 else 0)
    p.translate(0,-lift)
    phone=pose.activity=='phone' and state=='idle'
    greeting=0<pose.wave<1
    if phone or greeting:
        _polygon(p,[(95,161),(138,161),(151,176),(150,205),(143,214),(91,214),(83,204),(85,176)],'white')
        _box(p,91,204,54,10,'blue')
    _part(p,state,'body')
    if not phone:_part(p,state,'left_arm')
    if greeting:
        p.save();p.translate(145,166)
        p.rotate(math.sin(pose.wave*math.pi)*math.sin(pose.wave*math.pi*6)*12)
        p.translate(-145,-166);_part(p,'speaking','right_arm');p.restore()
    elif not phone:
        p.save()
        if state=='speaking':
            p.translate(145,166);p.rotate(math.sin(phase*math.tau)*3);p.translate(-145,-166)
        _part(p,state,'right_arm');p.restore()
    _part(p,state,'hair_tip')
    if pose.hair:
        p.save();p.translate(max(-1,min(1,pose.hair)),0)
        _part(p,state,'hair_tip');p.restore()
    _eyes(p,state,pose)
    _mouth(p,state,pose)
    if pose.expression in ('happy','excited'):
        _box(p,78,137,9,2 if pose.expression=='happy' else 4,'blush')
        _box(p,145,137,9,2 if pose.expression=='happy' else 4,'blush')
    if phone:_phone(p,phase)
    if state in ('launching','dictation_processing') and phase:
        p.save();p.setOpacity(.6)
        _box(p,106+round(phase*26),173,3,22,'ice');p.restore()
    p.restore()
    p.save()
    p.setOpacity(.85+.15*math.cos(phase*math.tau))
    p.translate(0,round(math.sin(phase*math.tau)))
    _part(p,state,'decor');p.restore()
    _waveforms(p,state,phase)
    p.restore()


def render_companion(pose):
    """Rasterise code-native contours; no image asset is loaded at runtime."""
    image=QImage(CANVAS_WIDTH,CANVAS_HEIGHT,QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter=QPainter(image)
    try:draw_companion(painter,pose)
    finally:painter.end()
    return image

"""Companion posture, quiet mouth and continuous clothing during movement."""
import numpy as np
import pytest
from desktop_app.companion_painter import CompanionPose, render_companion
from desktop_app.face_widget import FaceWidget
from desktop_app.companion_geometry import FEATURES

pytestmark = pytest.mark.unit


def pixels(pose):
    frame=render_companion(pose).convertToFormat(render_companion(pose).Format.Format_RGBA8888)
    return np.frombuffer(frame.constBits().asstring(frame.sizeInBytes()), dtype=np.uint8).reshape(frame.height(),frame.width(),4).copy()


def test_breathing_keeps_the_waist_sealed():
    rest=pixels(CompanionPose())
    inhale=pixels(CompanionPose(breath=1))
    # The middle of the hoodie/trousers seam stays opaque at both extremes.
    x,y,w,h=FEATURES['idle']['waist']
    assert np.all(inhale[y:y+h,x:x+w,3] == 255)
    assert np.all(rest[y:y+h,x:x+w,3] == 255)


def test_resting_mouth_is_closed():
    frame=pixels(CompanionPose())
    x,y,w,h=FEATURES['idle']['mouth']
    mouth=frame[y:y+h,x:x+w,:3].astype(int)
    pink=(mouth[:,:,0] > mouth[:,:,1]+35)
    assert np.count_nonzero(pink) < 65


@pytest.mark.parametrize('activity', ['rest','phone','thinking','launching'])
def test_only_greeting_raises_the_hand(activity):
    frame=pixels(CompanionPose(activity=activity, thinking=activity=='thinking'))
    raised=frame[110:142,47:75,:3].astype(int)
    skin=(raised[:,:,0]>raised[:,:,2]+20)&(raised[:,:,0]>180)
    assert not np.any(skin)


def test_phone_and_launch_have_distinct_animated_frames():
    frames=[pixels(CompanionPose(activity=activity, phase=phase)) for activity in ('phone','launching','thinking') for phase in (0.2,0.7)]
    assert all(not np.array_equal(a,b) for index,a in enumerate(frames) for b in frames[index+1:])


def test_companion_has_a_compact_default_footprint():
    assert FaceWidget.DESIGN_WIDTH <= 180
    assert FaceWidget.DESIGN_HEIGHT <= 280


@pytest.mark.parametrize('state',['listening','speaking','dictating'])
def test_sound_marks_change_height_with_animation_time(state):
    x,y,w,h=FEATURES[state]['waveforms'][0]
    initial=pixels(CompanionPose(state=state,phase=0))[max(0,y-6):y+h+6,x:x+w,3]
    animated=pixels(CompanionPose(state=state,phase=.25))[max(0,y-6):y+h+6,x:x+w,3]
    assert not np.array_equal(initial,animated)

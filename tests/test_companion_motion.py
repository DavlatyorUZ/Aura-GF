"""Companion posture, quiet mouth and continuous clothing during movement."""
import numpy as np
import pytest
from desktop_app.companion_painter import CompanionPose, render_companion
from desktop_app.face_widget import FaceWidget

pytestmark = pytest.mark.unit


def pixels(pose):
    frame=render_companion(pose).convertToFormat(render_companion(pose).Format.Format_RGBA8888)
    return np.frombuffer(frame.constBits().asstring(frame.sizeInBytes()), dtype=np.uint8).reshape(frame.height(),frame.width(),4).copy()


def test_breathing_keeps_the_waist_sealed():
    rest=pixels(CompanionPose())
    inhale=pixels(CompanionPose(breath=1))
    # The middle of the hoodie/trousers seam stays opaque at both extremes.
    assert np.all(inhale[329:335,126:185,3] == 255)
    assert np.all(rest[329:335,126:185,3] == 255)


def test_resting_mouth_is_closed():
    frame=pixels(CompanionPose())
    mouth=frame[218:237,149:172,:3].astype(int)
    pink=(mouth[:,:,0] > mouth[:,:,1]+35)
    assert np.count_nonzero(pink) < 65


@pytest.mark.parametrize('activity', ['rest','phone','thinking','launching'])
def test_only_greeting_raises_the_hand(activity):
    frame=pixels(CompanionPose(activity=activity, thinking=activity=='thinking'))
    raised=frame[234:263,68:106,:3].astype(int)
    skin=(raised[:,:,0]>raised[:,:,2]+20)&(raised[:,:,0]>180)
    assert not np.any(skin)


def test_phone_and_launch_have_distinct_animated_frames():
    frames=[pixels(CompanionPose(activity=activity, phase=phase)) for activity in ('phone','launching','thinking') for phase in (0.2,0.7)]
    assert all(not np.array_equal(a,b) for index,a in enumerate(frames) for b in frames[index+1:])


def test_companion_has_a_compact_default_footprint():
    assert FaceWidget.DESIGN_WIDTH <= 180
    assert FaceWidget.DESIGN_HEIGHT <= 280

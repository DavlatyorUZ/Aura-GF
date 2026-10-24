"""User-visible behaviour of the procedural, local desktop companion."""

from types import SimpleNamespace

import pytest
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QImage, QPainter, QRegion
from PyQt6.QtTest import QTest

from desktop_app import face_widget
from jarvis.activity import JarvisState

pytestmark = pytest.mark.unit


@pytest.mark.parametrize('feature', ['blink', 'mouth'])
def test_facial_motion_stays_within_its_end_poses(feature):
    from desktop_app.companion_painter import CompanionPose, render_companion

    for outside, endpoint in ((-3, 0), (4, 1)):
        assert render_companion(CompanionPose(**{feature: outside})) == render_companion(
            CompanionPose(**{feature: endpoint}))


def test_greeting_character_has_a_visible_raised_hand():
    from desktop_app.companion_painter import CompanionPose, render_companion

    image = render_companion(CompanionPose(wave=0.001)).scaled(104, 144)
    # The hand is visible in front of the lower left hood, beside the cheek.
    assert sum(image.pixelColor(x, y).red() > image.pixelColor(x, y).blue() + 15
               for y in range(78, 91) for x in range(23, 36)) > 25


@pytest.fixture
def companion(qapp, monkeypatch):
    state = SimpleNamespace(state=JarvisState.ASLEEP)
    monkeypatch.setattr(face_widget, 'get_jarvis_state', lambda: state)
    window = face_widget.FaceWindow()
    window.show()
    qapp.processEvents()
    window.face._animation_timer.stop()
    yield window, state
    window.close()


@pytest.mark.parametrize('click_child', [False, True])
def test_double_click_opens_chat_even_before_voice_is_ready(companion, click_child):
    window, _ = companion
    opened = []
    window.chat_requested.connect(lambda: opened.append(True))
    target = window.face if click_child else window
    QTest.mouseDClick(target, Qt.MouseButton.LeftButton, pos=target.rect().center())
    assert opened == [True]


def test_standby_explains_how_to_start_a_conversation(companion):
    window, _ = companion
    assert 'double-click' in window.toolTip().lower()
    assert 'chat' in window.toolTip().lower()
    assert window.face.status_text == 'Standby'


@pytest.mark.parametrize('state', list(JarvisState))
def test_each_activity_has_a_distinct_visible_status(companion, state):
    window, manager = companion
    statuses = []
    for activity in JarvisState:
        manager.state = activity
        window.face._animate()
        statuses.append(window.face.status_text)
    assert len(set(statuses)) == len(JarvisState)
    manager.state = state
    window.face._animate()
    assert window.face.status_text in window.face.accessibleDescription()


def test_character_has_a_filled_silhouette_on_a_transparent_canvas(companion):
    window, _ = companion
    image = QImage(window.size(), QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    window.render(image, QPoint(), QRegion(window.rect()),
                  window.RenderFlag.DrawChildren | window.RenderFlag.IgnoreMask)
    occupied = sum(image.pixelColor(x, y).alpha() > 200
                   for x in range(image.width()) for y in range(image.height()))
    assert image.width() * image.height() * 0.2 < occupied < image.width() * image.height() * 0.7
    assert image.pixelColor(0, 0).alpha() == 0


def test_wave_changes_the_pose_without_moving_the_window(companion, monkeypatch):
    window, manager = companion
    manager.state = JarvisState.IDLE
    window.face._animate()
    before = window.grab().toImage()
    position = window.pos()
    now = face_widget._time.monotonic()
    monkeypatch.setattr(face_widget._time, "monotonic", lambda: now)
    window.face.wave()
    now += 0.5
    window.face._animate()
    after = window.grab().toImage()
    assert before != after
    assert window.pos() == position


def test_voice_startup_greets_without_changing_the_activity(companion):
    window, manager = companion
    manager.state = JarvisState.IDLE
    window.face._animate()
    assert window.face._pose.wave > 0
    assert manager.state == JarvisState.IDLE


def test_animation_slows_when_resting_and_stops_when_hidden(companion):
    window, manager = companion
    manager.state = JarvisState.ASLEEP
    window.face._animate()
    resting_interval = window.face._animation_timer.interval()
    manager.state = JarvisState.THINKING
    window.face._animate()
    assert resting_interval > window.face._animation_timer.interval()
    window.hide()
    assert not window.face._animation_timer.isActive()


@pytest.mark.parametrize('feature', ['blink', 'mouth', 'hair', 'wave'])
def test_body_parts_animate_independently_without_character_image_files(feature, monkeypatch):
    from desktop_app.companion_painter import CompanionPose, render_companion
    from PyQt6.QtGui import QPixmap

    def reject_asset(*args, **kwargs):
        pytest.fail('The procedural character must not load images')

    monkeypatch.setattr(QImage, 'load', reject_asset)
    monkeypatch.setattr(QPixmap, 'load', reject_asset)
    neutral = render_companion(CompanionPose())
    animated = render_companion(CompanionPose(**{feature: 1 if feature != 'wave' else 0.3}))
    assert neutral != animated
    # Feet stay anchored when the face, hair or arm changes.
    assert neutral.copy(0, neutral.height()*5//6, neutral.width(), neutral.height()//6) == animated.copy(0, animated.height()*5//6, animated.width(), animated.height()//6)


@pytest.mark.parametrize('scale', [0.75, 1, 1.5, 2])
def test_greeting_stays_inside_the_click_region_at_different_sizes(companion, scale):
    window, _ = companion
    window.resize(round(face_widget.FaceWidget.DESIGN_WIDTH * scale),
                  round(face_widget.FaceWidget.DESIGN_HEIGHT * scale))
    from desktop_app.companion_painter import CompanionPose
    for phase in (0.05, 0.2, 0.4, 0.6, 0.8, 0.95):
        window.face._pose = CompanionPose(wave=phase, breath=1, hair=-1)
        image = window.grab().toImage()
        assert all(window.mask().contains(QPoint(x, y))
                   for y in range(image.height()) for x in range(image.width())
                   if image.pixelColor(x, y).alpha() > 10)


@pytest.mark.parametrize('expression', ['happy', 'surprised', 'thinking', 'curious', 'excited', 'sad', 'concerned'])
def test_each_expression_produces_a_distinct_visual_pose(expression):
    from desktop_app.companion_painter import CompanionPose, render_companion
    neutral = render_companion(CompanionPose(expression='neutral'))
    expressed = render_companion(CompanionPose(expression=expression))
    assert neutral != expressed


def test_speaking_mouth_has_greater_vertical_opening_than_resting():
    from desktop_app.companion_painter import CompanionPose, render_companion

    resting = render_companion(CompanionPose(mouth=0.0)).scaled(104, 144)
    speaking = render_companion(CompanionPose(mouth=1.0)).scaled(104, 144)
    # Mouth region is around x=48..58, y=73..82
    resting_mouth_pixels = sum(resting.pixelColor(x, y).red() > resting.pixelColor(x, y).green() + 35 for x in range(48, 59) for y in range(73, 83))
    speaking_mouth_pixels = sum(speaking.pixelColor(x, y).red() > speaking.pixelColor(x, y).green() + 35 for x in range(48, 59) for y in range(73, 83))
    assert speaking != resting
    assert speaking_mouth_pixels > resting_mouth_pixels



def test_thinking_pose_renders_floating_thought_particles():
    from desktop_app.companion_painter import CompanionPose, render_companion
    resting = render_companion(CompanionPose(thinking=False)).scaled(104, 144)
    thinking = render_companion(CompanionPose(thinking=True)).scaled(104, 144)
    # Thought particles appear beside the hood, outside the face.
    resting_upper = sum(resting.pixelColor(x, y).alpha() > 100 for x in range(90, 103) for y in range(72, 82))
    thinking_upper = sum(thinking.pixelColor(x, y).alpha() > 100 for x in range(90, 103) for y in range(72, 82))
    assert thinking_upper > resting_upper



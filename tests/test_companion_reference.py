"""Reference fidelity of the code-native companion at its authored resolution."""
from pathlib import Path
import numpy as np
from PIL import Image
import pytest
from desktop_app.companion_painter import CompanionPose, render_companion

pytestmark = pytest.mark.unit


def test_greeting_geometry_preserves_the_supplied_character():
    source = Image.open(Path(__file__).parent / 'fixtures/face/reference.png').convert('RGB').crop((94, 44, 406, 476))
    frame = render_companion(CompanionPose(wave=0.001, mouth=0.6))
    frame = frame.convertToFormat(frame.Format.Format_RGBA8888)
    actual = Image.frombytes('RGBA', (frame.width(), frame.height()), frame.constBits().asstring(frame.sizeInBytes()))
    actual = actual.resize(source.size, Image.Resampling.NEAREST)
    background = Image.new('RGB', source.size, (253, 253, 253))
    background.paste(actual, mask=actual.getchannel('A'))
    difference = np.abs(np.array(source).astype(float) - np.array(background).astype(float))
    assert difference.mean() < 5
    assert np.mean(difference.max(axis=2) > 35) < 0.035

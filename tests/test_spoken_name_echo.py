"""A short assistant-name echo cannot wake its own conversation."""
import pytest
from jarvis.listening.echo_detection import EchoDetector

pytestmark = pytest.mark.unit


@pytest.mark.parametrize('heard,start,end,energy,expected',[
    ('Jarvis',101,102,.005,True),
    ('Jarvis!',104.1,104.2,.005,True),
    ('Jarvis',105,106,.005,False),
    ('Jarvis',101,102,.05,False),
    ('Jarvis, Telegramni och',101,102,.005,False),
    ('Friday',101,102,.005,False),
])
def test_name_echo_requires_spoken_name_capture_overlap_and_echo_energy(heard,start,end,energy,expected):
    detector=EchoDetector(echo_tolerance=.3)
    detector._tts_start_time=100
    detector._last_tts_finish_time=104
    detector._tts_energy_baseline=.0045
    detector._last_tts_text='My name is Jarvis. How can I help?'
    assert detector.is_spoken_name_echo(heard, ['Jarvis','Friday'],start,end,energy) is expected


def test_spoken_name_fragment_cannot_flash_listening_or_start_a_query():
    from unittest.mock import Mock
    from test_hot_window_input import _create_listener, _process_transcript, _accepted_query
    listener,_=_create_listener()
    listener.tts.is_speaking.return_value=True
    listener.echo_detector.track_tts_start('My name is Jarvis, your local assistant.')
    began=listener.echo_detector._tts_start_time
    listening=Mock()
    listener._set_face_state_listening=listening
    try:
        _process_transcript(listener,'Jarvis',utterance_energy=.005,
                            utterance_start_time=began+.1,utterance_end_time=began+.4)
        assert _accepted_query(listener) == ''
        listening.assert_not_called()
    finally:
        listener.state_manager.stop()

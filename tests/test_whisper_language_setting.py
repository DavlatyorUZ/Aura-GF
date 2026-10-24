"""A configured recognition language is forwarded without changing speech guards."""
from types import SimpleNamespace
import pytest
from jarvis.listening.listener import VoiceListener

pytestmark=pytest.mark.unit

@pytest.mark.parametrize('language', [None,'uz','de'])
def test_recogniser_uses_configured_language(language):
    received=[]
    def transcribe(audio,**kwargs):
        received.append(kwargs)
        return [], SimpleNamespace(language=language)
    listener=object.__new__(VoiceListener)
    listener.cfg=SimpleNamespace(whisper_language=language,whisper_no_speech_threshold=.5)
    listener._whisper_device='cpu'
    listener.model=SimpleNamespace(transcribe=transcribe)
    listener._decode_faster_whisper_locked([])
    assert received[0]['language'] == language
    assert received[0]['vad_filter'] is True
    assert received[0]['condition_on_previous_text'] is False

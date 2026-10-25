"""Local MMS speech preparation and Uzbek text handling without audio devices."""
from contextlib import nullcontext
from types import SimpleNamespace
import sys
import numpy as np
import pytest
from jarvis.output.mms import MmsTTS, uzbek_cyrillic

pytestmark = pytest.mark.unit

@pytest.mark.parametrize('latin,cyrillic', [
    ("Salom, o'zbek qizi!", 'салом, ўзбек қизи!'),
    ('Oʻzbekiston, G‘afur, shahar, chiroyli', 'ўзбекистон, ғафур, шаҳар, чиройли'),
    ('Салом, дунё!', 'салом, дунё!'),
    ('Ertaga elektr kelsa, aytsa yetti.', 'эртага электр келса, айтса етти.'),
    ('Javob 5. Bugun 21 ta, jami 105 ta.', 'жавоб беш. бугун йигирма бир та, жами юз беш та.'),
    ('007 va 2026', 'нол нол етти ва икки минг йигирма олти'),
    ('7.5%', 'етти нуқта беш фоиз'),
    ('2+3=5', 'икки қўшув уч тенг беш'),
    ('3.14', 'уч нуқта бир тўрт'),
    ('3.5+2=5.5', 'уч нуқта беш қўшув икки тенг беш нуқта беш'),
    ('1000000000000000', 'бир нол нол нол нол нол нол нол нол нол нол нол нол нол нол нол'),
])
def test_uzbek_latin_and_cyrillic_are_supported(latin,cyrillic):
    assert uzbek_cyrillic(latin) == cyrillic


def test_missing_local_model_does_not_download(tmp_path):
    engine=MmsTTS(model_path=str(tmp_path/'missing'))
    ok, reason=engine._prepare_speech()
    assert not ok and reason


@pytest.fixture
def local_voice(tmp_path,monkeypatch):
    calls=[]
    def load(path,**kwargs):
        assert kwargs['local_files_only'] is True
        assert kwargs['trust_remote_code'] is False
        return voice
    class Wave:
        def squeeze(self): return self
        def cpu(self): return self
        def numpy(self): return np.array([0,.5,-.5],dtype=np.float32)
    class Voice:
        config=SimpleNamespace(sampling_rate=16000)
        def eval(self): return self
        def __call__(self,**kwargs): return SimpleNamespace(waveform=Wave())
    voice=Voice()
    class Tokenizer:
        language='uzb-script_cyrillic'
        def __call__(self,text,**kwargs):
            calls.append(text)
            return {}
    def tokenizer_load(path,**kwargs):
        assert kwargs['local_files_only'] and not kwargs['trust_remote_code']
        return Tokenizer()
    monkeypatch.setitem(sys.modules,'transformers',SimpleNamespace(
        VitsModel=SimpleNamespace(from_pretrained=load),
        AutoTokenizer=SimpleNamespace(from_pretrained=tokenizer_load)))
    monkeypatch.setitem(sys.modules,'torch',SimpleNamespace(inference_mode=nullcontext))
    engine=MmsTTS(model_path=str(tmp_path))
    assert engine._ensure_initialized()
    return engine, calls


def test_local_model_yields_pcm_and_uses_its_sample_rate(local_voice):
    engine, calls = local_voice
    chunks=list(engine._synthesise('Salom!'))
    assert calls == ['салом!']
    assert engine._sample_rate == 16000
    assert chunks[0].dtype == np.int16 and len(chunks[0]) == 3


def test_sentences_have_audible_boundaries_without_trailing_silence(local_voice):
    engine, calls = local_voice
    chunks=list(engine._synthesise('Salom. Javob 5.'))
    assert calls == ['салом.', 'жавоб беш.']
    assert len(chunks) == 3
    assert np.count_nonzero(chunks[1]) == 0
    assert len(chunks[1]) / engine._sample_rate == pytest.approx(0.2)
    assert np.count_nonzero(chunks[-1]) > 0


def test_other_voice_languages_keep_their_own_alphabet_and_numbers(local_voice):
    engine, calls = local_voice
    engine._tokenizer.language = 'eng'
    list(engine._synthesise('Answer 5.'))
    assert calls == ['Answer 5.']


def test_long_utterances_keep_all_words_in_bounded_synthesis_chunks(local_voice):
    engine, calls = local_voice
    text = ' '.join(['Salom'] * 51)
    chunks = list(engine._synthesise(text))
    assert [len(chunk.split()) for chunk in calls] == [50, 1]
    assert ' '.join(calls) == uzbek_cyrillic(text)
    assert len(chunks) == 3

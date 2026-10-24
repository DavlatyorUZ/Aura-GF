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
])
def test_uzbek_latin_and_cyrillic_are_supported(latin,cyrillic):
    assert uzbek_cyrillic(latin) == cyrillic


def test_missing_local_model_does_not_download(tmp_path):
    engine=MmsTTS(model_path=str(tmp_path/'missing'))
    ok, reason=engine._prepare_speech()
    assert not ok and reason


def test_local_model_yields_pcm_and_uses_its_sample_rate(tmp_path,monkeypatch):
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
    chunks=list(engine._synthesise('Salom!'))
    assert calls == ['салом!']
    assert engine._sample_rate == voice.config.sampling_rate
    assert chunks[0].dtype == np.int16 and len(chunks[0]) == 3

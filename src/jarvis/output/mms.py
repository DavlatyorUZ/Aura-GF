"""Offline VITS/MMS speech synthesis with local-only model loading."""
from pathlib import Path
import re
import unicodedata

from .tts import LocalNeuralTTS
from ..debug import debug_log


# Transliteration is specific to the selected voice's tokenizer alphabet.
_UZBEK_LETTERS = dict(zip('abdefghijklmnopqrstuvxyz', 'абдефгҳижклмнопқрстувхйз'))
_UZBEK_DIGRAPHS = {"o'": 'ў', "g'": 'ғ', 'sh': 'ш', 'ch': 'ч', 'yo': 'ё', 'yu': 'ю', 'ya': 'я', 'ye': 'е', 'ts': 'ц'}


def uzbek_cyrillic(text):
    """Accept Uzbek Latin apostrophe variants and preserve Cyrillic input."""
    text = unicodedata.normalize('NFKC', text).lower()
    text = text.translate(str.maketrans({c: "'" for c in 'ʻʼ‘’`ʹ'}))
    text = re.sub("o'|g'|sh|ch|yo|yu|ya|ye|ts", lambda match: _UZBEK_DIGRAPHS[match.group()], text)
    return ''.join(_UZBEK_LETTERS.get(c, 'ъ' if c == "'" else c) for c in text)


class MmsTTS(LocalNeuralTTS):
    """Use downloaded, safetensors-only VITS weights on the CPU."""

    def __init__(self, enabled=True, model_path=None):
        super().__init__(enabled)
        self.model_path = model_path
        self._tokenizer = None

    def _ensure_initialized(self):
        if not self.enabled:
            return False
        with self._init_lock:
            if self._initialized:
                return self._voice is not None
            try:
                if not self.model_path or not Path(self.model_path).expanduser().is_dir():
                    raise ValueError('Select a downloaded MMS voice directory in TTS Voice')
                from transformers import VitsModel, AutoTokenizer
                path = str(Path(self.model_path).expanduser().resolve())
                tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=False)
                voice = VitsModel.from_pretrained(path, local_files_only=True, trust_remote_code=False, use_safetensors=True)
                voice.eval()
                self._sample_rate = int(voice.config.sampling_rate)
                self._tokenizer, self._voice = tokenizer, voice
                debug_log(f'Local MMS voice ready: sample_rate={self._sample_rate}', 'tts')
            except Exception as exc:
                self._init_error = f'Local MMS voice unavailable: {type(exc).__name__}. Install requirements-mms.txt and select a downloaded voice directory.'
                debug_log(self._init_error, 'tts')
            self._initialized = True
            return self._voice is not None

    def _synthesise(self, text):
        import torch
        import numpy as np
        if self._tokenizer.language == 'uzb-script_cyrillic':
            text = uzbek_cyrillic(text)
        # Bound individual synthesis batches and release cancellation between sentences.
        sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
        for sentence in sentences:
            words = sentence.split()
            while words:
                chunk, words = words[:50], words[50:]
                inputs = self._tokenizer(' '.join(chunk), return_tensors='pt')
                with torch.inference_mode():
                    waveform = self._voice(**inputs).waveform.squeeze().cpu().numpy()
                yield (np.clip(waveform, -1, 1) * 32767).astype(np.int16)

"""Offline VITS/MMS speech synthesis with local-only model loading."""
from pathlib import Path
import re
import unicodedata

from .tts import LocalNeuralTTS
from ..debug import debug_log


# Transliteration is specific to the selected voice's tokenizer alphabet.
_UZBEK_LETTERS = dict(zip('abdefghijklmnopqrstuvxyz', 'абдефгҳижклмнопқрстувхйз'))
_UZBEK_DIGRAPHS = {"o'": 'ў', "g'": 'ғ', 'sh': 'ш', 'ch': 'ч', 'yo': 'ё', 'yu': 'ю', 'ya': 'я', 'ye': 'е'}
_UNITS = ('нол', 'бир', 'икки', 'уч', 'тўрт', 'беш', 'олти', 'етти', 'саккиз', 'тўққиз')
_TENS = ('', 'ўн', 'йигирма', 'ўттиз', 'қирқ', 'эллик', 'олтмиш', 'етмиш', 'саксон', 'тўқсон')


def _uzbek_integer(digits):
    """Speak quantities; preserve leading zeros and long identifiers as digits."""
    if len(digits) > 15 or (len(digits) > 1 and digits.startswith('0')):
        return ' '.join(_UNITS[int(digit)] for digit in digits)
    value = int(digits)
    if value < 10:
        return _UNITS[value]
    for scale, name in ((10**12, 'триллион'), (10**9, 'миллиард'),
                        (10**6, 'миллион'), (1000, 'минг'), (100, 'юз')):
        if value >= scale:
            whole, rest = divmod(value, scale)
            prefix = '' if whole == 1 and scale <= 1000 else _uzbek_integer(str(whole)) + ' '
            return prefix + name + (' ' + _uzbek_integer(str(rest)) if rest else '')
    tens, units = divmod(value, 10)
    return _TENS[tens] + (' ' + _UNITS[units] if units else '')


def uzbek_cyrillic(text):
    """Accept Uzbek Latin apostrophe variants and preserve Cyrillic input."""
    text = unicodedata.normalize('NFKC', text).lower()
    text = text.translate(str.maketrans({c: "'" for c in 'ʻʼ‘’`ʹ'}))
    # MMS has digit tokens with no reliable quantity pronunciation. Expand them
    # before tokenisation, which otherwise silently discards unsupported digits.
    text = re.sub(r'(?<=[0-9])\s*([+−=×÷-])\s*(?=[0-9])',
                  lambda match: {'+': ' қўшув ', '-': ' айирув ', '−': ' айирув ',
                                 '=': ' тенг ', '×': ' кўпайтирув ', '÷': ' бўлув '}[match[1]], text)
    text = re.sub(r'([0-9]+)\.([0-9]+)',
                  lambda match: _uzbek_integer(match[1]) + ' нуқта ' +
                  ' '.join(_UNITS[int(digit)] for digit in match[2]), text)
    text = re.sub(r'[0-9]+', lambda match: _uzbek_integer(match.group()), text)
    text = text.replace('%', ' фоиз')
    # Initial e is э; ye is е. A literal t followed by s remains two letters.
    text = re.sub(r'(?<!\w)e', 'э', text)
    text = re.sub("o'|g'|sh|ch|yo|yu|ya|ye", lambda match: _UZBEK_DIGRAPHS[match.group()], text)
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
                debug_log(f'Local MMS voice ready: voice={Path(path).name}, sample_rate={self._sample_rate}', 'tts')
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
        chunks = [' '.join(words[offset:offset+50]) for sentence in sentences
                  if (words := sentence.split()) for offset in range(0, len(words), 50)]
        debug_log(f'Local MMS synthesis batches: {len(chunks)}', 'tts')
        for index, chunk in enumerate(chunks):
            inputs = self._tokenizer(chunk, return_tensors='pt')
            with torch.inference_mode():
                waveform = self._voice(**inputs).waveform.squeeze().cpu().numpy()
            yield (np.clip(waveform, -1, 1) * 32767).astype(np.int16)
            if index < len(chunks)-1:
                yield np.zeros(round(self._sample_rate * 0.2), dtype=np.int16)

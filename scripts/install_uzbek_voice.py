"""Download an optional local Uzbek VITS voice, without transmitting user text."""
import argparse
from pathlib import Path
from huggingface_hub import snapshot_download

VOICES = {
    'female': 'MuzaffarSharofitdinov/mms-tts-uzbek-girl-voice_cyrillic',
    'mms': 'facebook/mms-tts-uzb-script_cyrillic',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--voice', choices=VOICES, default='female')
    parser.add_argument('--directory', type=Path)
    args = parser.parse_args()
    directory = args.directory or Path.home()/'.local/share/jarvis/models/mms'/('uzbek-'+args.voice)
    print(f'📥 Downloading local voice weights: {VOICES[args.voice]}', flush=True)
    snapshot_download(VOICES[args.voice], local_dir=directory,
                      allow_patterns=['*.json', '*.safetensors', 'README.md', 'LICENSE*'])
    print(f'✅ Local voice: {directory}', flush=True)
    print('  🔊 Select MMS as TTS Engine and this directory as TTS Voice.', flush=True)


if __name__ == '__main__':
    main()

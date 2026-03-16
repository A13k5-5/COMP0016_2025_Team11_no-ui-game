# nuitka-project: --mode=standalone

## nuitka-project: --include-package=kokoro
## nuitka-project: --include-package-data=kokoro

# nuitka-project: --nofollow-import-to=transformers.generation.tf_utils
# nuitka-project: --nofollow-import-to=transformers.generation.flax_utils
# nuitka-project: --nofollow-import-to=torch._dynamo
# nuitka-project: --nofollow-import-to=matplotlib

# nuitka-project: --module-parameter=torch-disable-jit=yes

# nuitka-project: --spacy-language-model=en_core_web_sm
# nuitka-project: --include-distribution-metadata=phonemizer
# nuitka-project: --include-distribution-metadata=phonemizer-fork
# nuitka-project: --include-distribution-metadata=spacy

from kokoro import KPipeline
import soundfile as sf

import warnings
warnings.filterwarnings('ignore')  # Suppress all warnings

class Talker:
    def __init__(self):
        # 'b' - for British English
        self.pipeline: KPipeline = KPipeline(lang_code='b', repo_id="hexgrad/Kokoro-82M")

    def generate_speech(self, text: str, output_file="output.wav"):
        generator = self.pipeline(text, voice='bm_lewis')

        audio_chunks = []
        for gs, ps, audio in generator:
            audio_chunks.append(audio)

        if audio_chunks:
            import numpy as np
            full_audio = np.concatenate(audio_chunks)
            sf.write(output_file, full_audio, 24000)
            print("Generated speech saved to: ", output_file)

if __name__ == "__main__":
    talker = Talker()
    prompt = "Once upon a time in a land far away"
    talker.generate_speech(prompt, "story.wav")

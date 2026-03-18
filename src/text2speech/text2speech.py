# nuitka-project: --standalone

# nuitka-project: --include-package=transformers
# nuitka-project: --nofollow-import-to=matplotlib

# nuitka-project: --spacy-language-model=en_core_web_sm



from kokoro import KPipeline
import soundfile as sf

import warnings
warnings.filterwarnings('ignore')  # Suppress all warnings

class Talker:
    def __init__(self):
        # 'b' - for British English
        self.pipeline: KPipeline | None = None

    def _get_pipeline(self) -> KPipeline:
        if self.pipeline is None:
            self.pipeline = KPipeline(lang_code='b', repo_id="hexgrad/Kokoro-82M")
        return self.pipeline

    def generate_speech(self, text: str, output_file: str, voice: str):
        generator = self._get_pipeline()(text, voice=voice)

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
    talker.generate_speech(prompt, "story.wav", "bf_emma")

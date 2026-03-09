from kokoro import KPipeline
import soundfile as sf

import warnings
warnings.filterwarnings('ignore')  # Suppress all warnings

pipeline = KPipeline(lang_code='b', repo_id="hexgrad/Kokoro-82M")
text = '''
Once upon a time in a land far away, there was a brave knight named Sir Cedric.
'''

generator = pipeline(text, voice='bm_lewis')
for i, (gs, ps, audio) in enumerate(generator):
    print(i, gs, ps)
    sf.write(f'{i}.wav', audio, 24000)

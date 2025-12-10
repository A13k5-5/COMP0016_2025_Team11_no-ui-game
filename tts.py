from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import soundfile as sf
import torch

def generateAudioFile(textToConvert: str, filepath: str):
    # Load models
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

    # Speaker embedding (fixed random seed for a consistent synthetic voice)
    g = torch.Generator().manual_seed(42)
    speaker_embeddings = torch.randn((1, 512), generator=g)

    # Text to synthesize
    inputs = processor(text=textToConvert, return_tensors="pt")

    # Generate speech
    with torch.no_grad():
        speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)

    # Save to WAV
    sf.write(filepath, speech.numpy(), samplerate=16000)

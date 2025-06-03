import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import os
from TTS.api import TTS

# --- Record audio ---
def record_audio(filename="input.wav", duration=10, samplerate=16000):
    print(f"🎙️ Speak now ({duration}s)...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    wav.write(filename, samplerate, audio)
    print("✅ Recording complete.")

# --- Transcribe audio to text using Whisper ---
def transcribe_audio(filename="input.wav"):
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    return result["text"]

# --- Convert text to speech using Coqui TTS ---
def speak_text(text):
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
    tts.tts_to_file(text=text, file_path="output.wav")
    os.system("afplay output.wav" if os.name == "posix" else "start output.wav")  # macOS vs Windows

# --- Main Loop ---
if __name__ == "__main__":
    while True:
        record_audio()
        text = transcribe_audio()
        print(f"🗣️ You said: {text}")
        speak_text(f"You said: {text}")
        
        cont = input("Press Enter to continue, or type 'q' to quit: ")
        if cont.lower().startswith("q"):
            break
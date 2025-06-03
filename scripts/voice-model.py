import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import os
from TTS.api import TTS
import time
from pynput import keyboard
import threading

import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")  # Suppress TTS warnings

# --- Record audio ---
def record_audio(filename="input.wav", samplerate=16000):
    print("🎙️ Speak now! (Press 's' to stop recording)")
    recording = []
    stop_flag = threading.Event()
    listener = None  # Declare listener in outer scope

    def on_press(key):
        try:
            if key.char == 's':
                stop_flag.set()
                if listener is not None:
                    listener.stop()  # Properly stop the listener
        except AttributeError:
            pass
        # Always return None

    def audio_callback(indata, frames, time, status):
        recording.append(indata.copy())
        if stop_flag.is_set():
            raise sd.CallbackStop

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', callback=audio_callback):
        while not stop_flag.is_set():
            sd.sleep(100)

    listener.join()
    audio = np.concatenate(recording, axis=0)
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
        cmd = input("Press 'r' to record or 'q' to quit: ").strip().lower()
        if cmd == 'q':
            print("Exiting.")
            break
        elif cmd == 'r':
            record_audio()
            text = transcribe_audio()
            print(f"🗣️ You said: {text}")
            speak_text(f"You said: {text}")
        else:
            print("Invalid input. Press 'r' to record or 'q' to quit.")
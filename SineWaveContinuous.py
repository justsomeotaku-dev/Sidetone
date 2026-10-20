import numpy as np
import sounddevice as sd  # pip install sounddevice numpy

SR = 48000
FREQ = 220.0  # Hz, left ear
VOLUME = 0.3

phase = 0.0  # running phase for [left, right]
inc = 2 * np.pi * FREQ / SR


def callback(outdata, frames, time, status):
    global phase
    ph = phase + inc * np.arange(1, frames + 1)  # shape (frames, 2)
    phase = ph[-1] % (2 * np.pi)
    outdata[:, 0] = np.sin(ph) * VOLUME


with sd.OutputStream(samplerate=SR, channels=2, callback=callback, blocksize=1024):
    input(f"Playing {FREQ} Hz beat. Press Enter to stop.")
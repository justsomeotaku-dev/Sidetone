import numpy as np
import sounddevice as sd  # pip install sounddevice numpy

SR = 48000
_carrier = 0.0  # Hz, left ear
_beat = 0.0      # Hz, right ear = CARRIER + BEAT

stream = None
_status_callback = None

_volume = 0


phase = np.zeros(2)  # [left;right] angle / start where the wave is in the cycle.
# inc is how far the angle turns per sample, all point is (phase + inc * [1,2,3,...,1024])
inc = (2 * np.pi) * (np.array([_carrier, _carrier + _beat]) / SR)
# Carrier/Sr gives cycles per sample
# 2pi converts cycles to radians per sample 

def update_inc():
    global inc
    inc = (2 * np.pi) * (np.array([_carrier, _carrier + _beat]) / SR)

def set_beat(beat):
    global _beat
    _beat = beat
    update_inc()

def set_carrier(carrier):
    global _carrier
    _carrier = carrier
    update_inc()

def report(msg):
    if _status_callback: # if status callback/main.py status_changed str Signal
        _status_callback(msg) # send status to that callback

def set_volume(volume):
    global _volume
    _volume = volume

# Duplex stream: whatever comes in goes straight out
def callback(outdata, frames, time, status):
    global phase
    ph = phase + inc * np.arange(1, frames + 1)[:, None]  
    # np.arange(1, frames + 1)[:, None] turns [1,2,3...1024] into [[1],[2]...[1024]],
    # which we then multiply by the two incs [0.5,0.55] for example
    phase = ph[-1] % (2 * np.pi)
    # ph[-1] is the last row, where the 2 waves ended up.
    # 2pi wraps the circle back into one unit circle, 361° = 1°
    outdata[:] = np.sin(ph) * _volume
    # sin tunrs the angles into heights between -1 and 1

def start(status_callback): # duplex stream that can input and output audio at the same time
    global stream, _status_callback
    _status_callback = status_callback

    if stream is not None:
        return
    
    stream = sd.OutputStream(
        samplerate=48000,
        channels=2,
        blocksize=1024,
        latency="low",
        callback=callback,
    )
    
    stream.start()
    report("Listening...")

def stop():
    global stream
    if stream is None:
        return

    stream.stop()
    stream.close()
    stream = None
    report("Stopped")
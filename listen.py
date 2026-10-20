import sounddevice as sd

stream = None
_status_callback = None

_volume = 1

def report(msg):
    if _status_callback: # if status callback/main.py status_changed str Signal
        _status_callback(msg) # send status to that callback

def set_volume(volume):
    _volume = volume

# Duplex stream: whatever comes in goes straight out
def callback(indata, outdata, frames, time, status):
    if status:
        report(status)
    outdata[:] = indata * _volume

def listen(input_device, output_device, status_callback): # duplex stream that can input and output audio at the same time
    global stream, _status_callback
    _status_callback = status_callback

    if stream is not None:
        return
    
    stream = sd.Stream( 
        device=(input_device, output_device),
        samplerate=48000,
        channels=2,
        dtype="float32",
        blocksize=0,
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

import sys, time
from faster_whisper import WhisperModel
audio, out, size, root = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
start = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
m = WhisperModel(size, device='cpu', compute_type='int8', download_root=root, cpu_threads=4)
def ts(s):
    s += start
    return f"{int(s//3600):02d}:{int(s%3600//60):02d}:{s%60:05.2f}"
import wave, numpy as np
w=wave.open(audio); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768.0
segs, info = m.transcribe(a, language='es', vad_filter=True, beam_size=5, word_timestamps=False, condition_on_previous_text=False)
t0 = time.time()
with open(out, 'w') as f:
    for s in segs:
        f.write(f"[{ts(s.start)} -> {ts(s.end)}] {s.text.strip()}\n"); f.flush()
print('done', time.time() - t0)

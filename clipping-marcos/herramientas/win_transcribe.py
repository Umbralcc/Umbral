import sys, wave, numpy as np, json
from faster_whisper import WhisperModel
audio, root, out = sys.argv[1], sys.argv[2], sys.argv[3]
wins = [tuple(map(int, w.split('-'))) for w in sys.argv[4:]]
w = wave.open(audio); sr = w.getframerate()
a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)/32768.0
m = WhisperModel('medium', device='cpu', compute_type='int8', download_root=root, cpu_threads=4)
def ts(s): return f"{int(s//3600):02d}:{int(s%3600//60):02d}:{s%60:05.2f}"
res = {}
for s0, s1 in wins:
    segs, _ = m.transcribe(a[s0*sr:s1*sr], language='es', beam_size=5, word_timestamps=True, condition_on_previous_text=False, vad_filter=False)
    L = []
    for s in segs:
        L.append({'start': s.start+s0, 'end': s.end+s0, 'text': s.text.strip(), 'words': [(x.start+s0, x.end+s0, x.word) for x in s.words]})
        print(f"[{ts(s.start+s0)}] {s.text.strip()}", flush=True)
    res[f"{s0}-{s1}"] = L
    print(f"=== done {s0}-{s1}", flush=True)
    json.dump(res, open(out, 'w'), ensure_ascii=False)

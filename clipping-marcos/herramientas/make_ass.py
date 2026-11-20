"""Genera subtítulos ASS (palabra a palabra, en bloques cortos) a partir de med.json.
Uso: make_ass.py med.json spec.json out.ass
spec: {"start": s, "end": s, "hook": "texto", "hook_dur": 3.0, "y": 1040,
       "fix": {"palabra_mal": "palabra_bien"}, "hl": ["palabra", ...], "drop": [[t0,t1],...],
       "cuts": [[t0,t1],...]}   # cuts = tramos conservados (en tiempo del stream), en orden
"""
import json, sys, re

med, spec, out = json.load(open(sys.argv[1])), json.load(open(sys.argv[2])), sys.argv[3]
cuts = spec.get('cuts') or [[spec['start'], spec['end']]]

def to_clip(t):
    """tiempo del stream -> tiempo del clip (con los tramos concatenados) o None"""
    acc = 0.0
    for a, b in cuts:
        if a <= t <= b:
            return acc + (t - a)
        acc += b - a
    return None

words = []
for segs in med.values():
    for s in segs:
        for (a, b, w) in s['words']:
            words.append((a, b, w.strip()))
words.sort()
# reemplazos de frase por tramo (correcciones revisadas): [t0, t1, "texto"] ("" = sin subtítulo)
for t0r, t1r, txt in spec.get('replace_at', []):
    inside = [x for x in words if t0r <= x[0] <= t1r]
    if not inside:
        continue
    a0, b0 = inside[0][0], inside[-1][1]
    words = [x for x in words if not (t0r <= x[0] <= t1r)]
    toks = txt.split()
    if toks:
        step = (b0 - a0) / len(toks)
        words += [(a0 + i*step, a0 + (i+1)*step, tk) for i, tk in enumerate(toks)]
words.sort()
seen = set(); W = []
for a, b, w in words:
    k = (round(a, 2), w)
    if k in seen or not w:
        continue
    seen.add(k)
    if any(x <= a <= y for x, y in spec.get('drop', [])):
        continue
    ca, cb = to_clip(a), to_clip(b)
    if ca is None:
        continue
    if cb is None:  # la palabra empieza dentro del tramo pero acaba fuera: se recorta al final del tramo
        cb = ca + 0.4
    for bad, good in spec.get('fix', {}).items():
        if re.sub(r'[^\wáéíóúñü]', '', w.lower()) == bad.lower():
            w = re.sub(re.escape(re.sub(r'[^\wáéíóúñüÁÉÍÓÚÑ]', '', w)), good, w) if re.sub(r'[^\wáéíóúñüÁÉÍÓÚÑ]', '', w) else good
    W.append([ca, cb, w])

# bloques de máx. 3 palabras, cortando en pausas > 0.6 s o puntuación fuerte
blocks, cur = [], []
for i, (a, b, w) in enumerate(W):
    if cur and (len(cur) >= 3 or a - cur[-1][1] > 0.6 or re.search(r'[.?!]$', cur[-1][2])):
        blocks.append(cur); cur = []
    cur.append((a, b, w))
if cur:
    blocks.append(cur)

hl = {h.lower() for h in spec.get('hl', [])}
def fmt(t):
    t = max(t, 0)
    return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"

y = spec.get('y', 1040)
hmv = spec.get('hook_mv', 190)
head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter Black,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,7,2,5,60,60,0,1
Style: Hook,Inter Black,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&HC8000000,1,0,0,0,100,100,0,0,3,18,0,8,70,70,{hmv},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
lines = []
if spec.get('hook'):
    lines.append(f"Dialogue: 1,{fmt(0)},{fmt(spec.get('hook_dur', 3.0))},Hook,,0,0,0,,{{\\fad(120,200)}}{spec['hook']}")
for bl in blocks:
    a = bl[0][0]; b = max(bl[-1][1], a + 0.35)
    txt = []
    for (_, _, w) in bl:
        key = re.sub(r'[^\wáéíóúñü]', '', w.lower())
        txt.append(f"{{\\c&H00E6FF&}}{w.upper()}{{\\c&HFFFFFF&}}" if key in hl else w.upper())
    lines.append(f"Dialogue: 0,{fmt(a)},{fmt(b)},Sub,,0,0,0,,{{\\pos(540,{y})\\fscx90\\fscy90\\t(0,80,\\fscx100\\fscy100)}}" + ' '.join(txt))
open(out, 'w').write(head + '\n'.join(lines) + '\n')
# SRT fiel (texto sin mayúsculas forzadas) para entregar
srt = []
for i, bl in enumerate(blocks, 1):
    a = bl[0][0]; b = max(bl[-1][1], a + 0.35)
    f = lambda t: f"{int(t//3600):02d}:{int(t%3600//60):02d}:{int(t%60):02d},{int((t%1)*1000):03d}"
    srt.append(f"{i}\n{f(a)} --> {f(b)}\n{' '.join(w for _,_,w in bl)}\n")
open(out.replace('.ass', '.srt'), 'w').write('\n'.join(srt))
print(len(blocks), 'bloques')

"""Renderiza todos los clips de un catálogo.
Uso: render_cat.py catalog.py med.json stream.mp4 outdir [ids...]
"""
import json, os, re, subprocess, sys
cat_path, med, src, outdir = sys.argv[1:5]
only = set(sys.argv[5:])
ns = {}
exec(open(cat_path).read(), ns)
here = os.path.dirname(os.path.abspath(__file__))
wm = '/tmp/claude-0/-home-user-Umbral/103299cb-7cc6-5615-898c-8dde6d176f21/scratchpad/img/marca_agua_twitch_marcosescuderohair_transparente.png'
os.makedirs(outdir, exist_ok=True)
for c in ns['CLIPS']:
    if only and c['id'] not in only:
        continue
    spec = dict(layout='irl', cw=c['cw'], cx=c['cx'], cuts=c['cuts'], hook=c['hook'], hook_dur=3.2,
                hook_mv=380, y=1450, hl=c.get('hl') or [w for w in re.findall(r'\w+', c['hook'].lower().replace('\\n', ' ')) if len(w) >= 5 or w.isdigit()], fix=c.get('fix', {}),
                replace_at=c.get('replace_at', []), drop=c.get('drop', []))
    sp = os.path.join(outdir, c['id'] + '.json'); json.dump(spec, open(sp, 'w'), ensure_ascii=False)
    ass = os.path.join(outdir, c['id'] + '.ass')
    subprocess.run(['python3', '-I', os.path.join(here, 'make_ass.py'), med, sp, ass], check=True)
    subprocess.run(['python3', '-I', os.path.join(here, 'render.py'), src, sp, ass, wm,
                    os.path.join(outdir, c['id'] + '.mp4')], check=True)

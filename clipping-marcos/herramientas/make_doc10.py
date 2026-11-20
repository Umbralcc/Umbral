"""MD: solo calendario + copies en orden de publicación (TikTok e Instagram, máx. 5 hashtags).
Prioridad D10 (GTA VI); se intercalan solo los clips de D8/D9 que siguen en el Drive."""
import sys
S = '/tmp/claude-0/-home-user-Umbral/103299cb-7cc6-5615-898c-8dde6d176f21/scratchpad'
out_md = sys.argv[1]

def load(p):
    ns = {}; exec(open(p).read(), ns); return ns['CLIPS']

cats = {k: load(f'{S}/work/catalog_{k}.py') for k in ['d10', 'd9', 'd8']}
clips = {c['id']: c for k in cats for c in cats[k]}
# disponibles en la carpeta del Drive (20/11). D8-13 fuera: anunciaba un directo con fecha ya pasada.
AVAIL = {'D8-01', 'D8-02', 'D8-04', 'D8-06', 'D8-07', 'D8-08', 'D8-10', 'D8-11', 'D8-14', 'D8-15', 'D8-16', 'D8-17', 'D8-18',
         'D9-01', 'D9-02', 'D9-03', 'D9-04', 'D9-06', 'D9-07', 'D9-11', 'D9-12', 'D9-13', 'D9-14'}
q10 = [c['id'] for c in sorted(cats['d10'], key=lambda c: -c['score'])]
o9 = [c['id'] for c in sorted(cats['d9'], key=lambda c: -c['score']) if c['id'] in AVAIL]
o8 = [c['id'] for c in sorted(cats['d8'], key=lambda c: -c['score']) if c['id'] in AVAIL]
qold = []
while o9 or o8:
    if o9: qold.append(o9.pop(0))
    if o8: qold.append(o8.pop(0))

days = []
while q10 or qold:
    day = []
    for _ in range(3):
        if q10: day.append(q10.pop(0))
    while len(day) < 5 and (qold or q10):
        day.append((qold or q10).pop(0))
    days.append(day)

def tags(c):
    t = ['#marcosescuderohair'] + [x for x in c['tags'].split() if x != '#marcosescuderohair']
    if '#twitch' not in t[:5]:
        t = t[:4] + ['#twitch']
    return ' '.join(t[:5])

L = []; w = L.append
w('# Calendario y copies · Marcos Escudero Hair\n')
w('## Calendario (TikTok + Instagram)\n')
w('| Día | 1º | 2º | 3º | 4º | 5º |\n|---|---|---|---|---|---|')
for i, d in enumerate(days, 1):
    cells = [f"**{x}** · {clips[x]['title']}" for x in d]
    while len(cells) < 5: cells.append('—')
    w(f'| Día {i} | ' + ' | '.join(cells) + ' |')
w('')
w('## Copies en orden de publicación\n')
n = 0
for i, d in enumerate(days, 1):
    w(f'### Día {i}\n')
    for x in d:
        n += 1; c = clips[x]
        w(f"**{n}. {x} · {c['title']}**  ")
        w(f"Texto en pantalla: {c['hook'].replace(chr(92) + 'N', ' ')}\n")
        w('```')
        w(c['caption']); w(c['cta'])
        w('📺 twitch.tv/marcosescuderohair · @marcosescuderohair')
        w(tags(c))
        w('```\n')
open(out_md, 'w').write('\n'.join(L))
print('ok', out_md, n, 'clips en', len(days), 'días')

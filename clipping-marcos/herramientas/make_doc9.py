"""MD final: solo calendario (4-5 al día) + copies para TikTok e Instagram (máx. 5 hashtags)."""
import sys
S = '/tmp/claude-0/-home-user-Umbral/103299cb-7cc6-5615-898c-8dde6d176f21/scratchpad'
out_md = sys.argv[1]

def load(p):
    ns = {}; exec(open(p).read(), ns); return ns['CLIPS']

cats = {k: load(f'{S}/work/catalog_{k}.py') for k in ['d9', 'd8', 'd7', 'd6']}
clips = {c['id']: c for k in cats for c in cats[k]}
PUBLISHED = {'D7-20', 'D7-03', 'D7-24', 'D7-07', 'D7-22', 'D7-06', 'D7-23', 'D7-27', 'D8-05', 'D8-12', 'D8-09'}
# no publicar el mismo día clips del mismo tema
SAME_TOPIC = [{'D7-11', 'D8-18'}]

def pend(k):
    return [c['id'] for c in sorted(cats[k], key=lambda c: -c['score']) if c['id'] not in PUBLISHED]

q9, q8, q67 = pend('d9'), pend('d8'), []
a7, a6 = pend('d7'), pend('d6')
while a7 or a6:                       # D6 y D7 intercalados
    if a6: q67.append(a6.pop(0))
    if a7: q67.append(a7.pop(0))

days = []
while q9 or q8 or q67:
    day = []
    # D9 manda: hasta 3 por día mientras queden; luego D8 y D6/D7 rellenan hasta 5
    for q, n in ((q9, 3), (q8, 1), (q67, 1)):
        for _ in range(n):
            if q: day.append(q.pop(0))
    for q in (q8, q67, q9):
        while len(day) < 5 and q:
            day.append(q.pop(0))
    days.append(day)

for d in days:  # separar temas repetidos
    for pair in SAME_TOPIC:
        if pair <= set(d):
            x = sorted(pair)[1]; i = days.index(d)
            if i + 1 < len(days):
                d.remove(x); days[i + 1].append(x)

# clips con fecha: adelantarlos (D8-13 anuncia el directo del sábado)
URGENT = {'D8-13': 1}
for cid, day_idx in URGENT.items():
    src = next(d for d in days if cid in d)
    if days.index(src) > day_idx:
        tgt = days[day_idx]; swap = next(x for x in reversed(tgt) if x.startswith('D8'))
        src[src.index(cid)] = swap; tgt[tgt.index(swap)] = cid

def tags(c):
    t = ['#marcosescuderohair'] + [x for x in c['tags'].split() if x != '#marcosescuderohair']
    if '#twitch' not in t[:5]:
        t = t[:4] + ['#twitch']
    return ' '.join(t[:5])

L = []; w = L.append
w('# Calendario y copies · Marcos Escudero Hair\n')
w('## Calendario (4-5 vídeos al día · TikTok + Instagram)\n')
w('| Día | 1º | 2º | 3º | 4º | 5º |\n|---|---|---|---|---|---|')
for i, d in enumerate(days, 1):
    cells = [f"**{x}** · {clips[x]['title']}" for x in d]
    while len(cells) < 5: cells.append('—')
    w(f'| Día {i} | ' + ' | '.join(cells) + ' |')
w('')
w('## Copies (TikTok e Instagram)\n')
order = [x for d in days for x in d]
for x in order:
    c = clips[x]
    w(f"### {x} · {c['title']}")
    w(f"**Texto en pantalla:** {c['hook'].replace(chr(92) + 'N', ' ')}\n")
    w('```')
    w(c['caption'])
    w(c['cta'])
    w('📺 twitch.tv/marcosescuderohair · @marcosescuderohair')
    w(tags(c))
    w('```\n')
open(out_md, 'w').write('\n'.join(L))
print('ok', out_md, len(order), 'clips en', len(days), 'días')

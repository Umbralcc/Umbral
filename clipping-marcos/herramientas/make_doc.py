"""Genera el documento de entrega (banco de clips + textos + calendario) a partir de los catálogos."""
import json, os, subprocess, sys
S = '/tmp/claude-0/-home-user-Umbral/103299cb-7cc6-5615-898c-8dde6d176f21/scratchpad'
out_md = sys.argv[1]

def load(p):
    ns = {}; exec(open(p).read(), ns); return ns['CLIPS']

cats = {'D7': load(f'{S}/work/catalog_d7.py'), 'D6': load(f'{S}/work/catalog_d6.py')}
clips = {c['id']: c for k in cats for c in cats[k]}

def ts(s):
    s = float(s); return f"{int(s//3600):02d}:{int(s%3600//60):02d}:{int(s%60):02d}"

def dur(c):
    f = f"{S}/out/{c['id'][:2].lower()}/{c['id']}.mp4"
    if os.path.exists(f):
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True)
        try: return float(r.stdout.strip())
        except ValueError: pass
    return sum(b - a for a, b in c['cuts'])

ORDER = [
 ['D7-20', 'D7-03', 'D7-24'], ['D7-07', 'D7-22', 'D7-06'], ['D7-23', 'D7-27', 'D6-02'],
 ['D7-01', 'D7-09', 'NEW'], ['D7-21', 'D7-25', 'NEW'], ['D6-04', 'D7-14', 'NEW'],
 ['D7-04', 'D6-09', 'NEW'], ['D7-16', 'D6-08', 'NEW'], ['D7-08', 'D6-13', 'NEW'],
 ['D7-05', 'D6-10', 'NEW'], ['D7-12', 'D6-14', 'NEW'], ['D7-02', 'D6-06', 'NEW'],
 ['D7-11', 'D6-05', 'NEW'], ['D7-15', 'D6-07', 'NEW'], ['D7-26', 'D6-11', 'NEW'],
 ['D7-18', 'D6-01', 'NEW'], ['D7-10', 'D6-12', 'D7-13'], ['D6-15', 'D7-17', 'D7-19'], ['D6-03']]
used = [x for d in ORDER for x in d if x != 'NEW']
assert sorted(used) == sorted(clips), set(clips) ^ set(used)

L = []
w = L.append
w('# Clips Directos 6 y 7 · Marcos Escudero Hair\n')
w('**Canal:** twitch.tv/marcosescuderohair · **Usuario obligatorio:** `@marcosescuderohair` (va en la marca de agua de todos los clips y en todos los textos).\n')
w(f'**Total:** {len(cats["D7"])} clips del Directo 7 (prioridad, es el más reciente) + {len(cats["D6"])} del Directo 6 = **{len(clips)} clips renderizados** en 9:16 (1080×1920, MP4) con subtítulos, gancho en pantalla y marca de agua.\n')
w('**Cómo se hizo:** transcripción completa de los dos directos, revisión de las 10 marcas de `Clips potenciales.pdf` y lectura entera de ambas transcripciones para sacar todo lo demás. Los subtítulos salen de una segunda transcripción más precisa de cada fragmento.\n')
w('> ⚠️ **Antes de publicar, escuchad cada clip con sus subtítulos.** La transcripción es automática y en algunos tramos (voces solapadas, chat leído en voz alta) puede tener palabras mal. La columna "Revisar" marca lo que conviene mirar con más cuidado.\n')

w('## Marcas del PDF del Directo 7 → clip\n')
w('| Marca | Clip | Qué pasa |\n|---|---|---|')
pdf = [('00:23:55', 'D7-03'), ('00:40:55', 'D7-07'), ('00:56:35', 'D7-11'), ('01:32:35', 'D7-20'), ('01:34:55', 'D7-22'),
       ('01:36:25', 'D7-23'), ('01:37:35', 'D7-24 / D7-25'), ('01:44:50', 'D7-26'), ('01:45:25', 'D7-26'), ('01:48:00', 'D7-16')]
for m, cid in pdf:
    w(f"| {m} | {cid} | {clips[cid.split(' ')[0]]['title']} |")
w('')

for k, name in [('D7', 'Directo 7'), ('D6', 'Directo 6')]:
    w(f'## Banco de clips · {name}\n')
    w('| Clip | Tramo(s) en el directo | Duración | Tema | Categoría | Potencial | Revisar |\n|---|---|---|---|---|---|---|')
    for c in sorted(cats[k], key=lambda c: -c['score']):
        tr = ' + '.join(f"{ts(a)}–{ts(b)}" for a, b in c['cuts'])
        w(f"| **{c['id']}** | {tr} | {dur(c):.0f} s | {c['title']} | {c['cat']} | {c['score']}/10 | {c['risk'] or '—'} |")
    w('')

w('## Lo que NO he sacado (y por qué)\n')
w('Las directrices de Marcos piden: no inventar ni alimentar polémicas, no sacar cosas de contexto y no mostrar información privada. Por eso he dejado fuera:\n')
w('| Directo | Tramo | Motivo |\n|---|---|---|')
for d, t, m in [
    ('7', '00:13:06–00:13:24 y 00:15:16–00:15:56', 'Comentarios sobre el físico de una compañera de trabajo ("la que me acosa"). Tercera persona identificable.'),
    ('7', '00:20:00–00:22:50', 'Cotilleo sobre la vida sentimental de dos creadores conocidos. Rumor sobre terceros.'),
    ('7', '00:25:32 y 00:32:15–00:34:30', 'Política (8M, entrevista a un líder político, polémicas de presentadores).'),
    ('7', '00:50:24–00:53:58', 'Tema de Hitler y opiniones políticas sobre amigos.'),
    ('7', '01:04:30–01:05:05', 'Insultos al físico de una cantante.'),
    ('7', '01:13:02–01:18:10', 'El padre de Marcos tontea en el chat con una chica que dice estar en 2º de bachillerato. Posible menor: no se publica.'),
    ('7', '01:22:58–01:23:30 y 01:25:15–01:26:30', 'Fiesta con "drogas, sustancias" y voto a un partido político.'),
    ('7', '01:44:52–01:45:24', 'Pregunta del chat sobre "moros". El clip D7-26 empieza justo después.'),
    ('6', '00:10:50–01:10:20 (casi toda la primera hora)', 'Conflicto con una chica concreta (nombrada en clips anteriores), su novio y amigos: mensajes privados, amenazas, acusaciones de infidelidad, un amigo que "le traiciona". Información privada de terceros y polémica directa.'),
    ('6', '00:50:20–00:53:40', 'Anécdota de contenido sexual de cuando tenía 8 años.'),
    ('6', '01:42:39–01:43:08', 'Comentarios cosificando a las chicas de Suiza.'),
    ('6', '01:49:00–02:26:28 (final)', 'Continúa el conflicto: insulto racista a un amigo suyo, llamadas grabadas, mensajes al novio en directo. Polémica y privacidad.'),
]:
    w(f'| {d} | {t} | {m} |')
w('\nSi Marcos quiere alguno de estos tramos, que lo pida explícitamente; están localizados por minuto.\n')

w('## Calendario de publicación (2-3 clips al día)\n')
w('- Cada clip se sube **el mismo día a TikTok, Instagram Reels y YouTube Shorts** (y Facebook Reels si queréis), con los textos de abajo.')
w('- Orden: primero el Directo 7 (el más reciente, como piden las directrices) y lo mejor de cada directo al principio, alternando temas para no repetir el mismo tipo de clip seguido.')
w('- **"🆕 NUEVO DIRECTO"** = hueco reservado para el mejor clip del directo que salga esa semana (Marcos hace 4 por semana). Si ese día no hay material nuevo, se rellena con el siguiente clip pendiente de la lista y todo se corre un hueco.')
w('- Horas: **[PENDIENTE]**, no hay datos previos de la cuenta. Propuesta para probar 2 semanas: 1º a mediodía, 2º a media tarde, 3º por la noche, y quedarse con la franja que más retenga.\n')
w('| Día | 1º (mediodía) | 2º (tarde) | 3º (noche) |\n|---|---|---|---|')
for i, d in enumerate(ORDER, 1):
    cells = []
    for x in d:
        cells.append('🆕 NUEVO DIRECTO' if x == 'NEW' else f"**{x}** · {clips[x]['title']}")
    while len(cells) < 3: cells.append('—')
    w(f'| Día {i} | ' + ' | '.join(cells) + ' |')
w('')

w('## Textos listos para copiar\n')
w('Cada bloque: **título** (para YouTube Shorts) y **descripción** (TikTok / Reels / Shorts).\n')
for k in ['D7', 'D6']:
    for c in cats[k]:
        w(f"### {c['id']} · {c['title']}")
        w(f"Gancho en pantalla: {c['hook'].replace(chr(92)+'N', ' ')}\n")
        w('```')
        w(f"{c['title']} #shorts")
        w('```')
        w('```')
        w(c['caption'])
        w(c['cta'])
        w('📺 twitch.tv/marcosescuderohair · @marcosescuderohair')
        w(f"#marcosescuderohair {c['tags']} #twitch")
        w('```\n')

open(out_md, 'w').write('\n'.join(L))
print('ok', out_md, len(clips))

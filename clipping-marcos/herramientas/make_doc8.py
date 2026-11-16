"""Documento del Directo 8 + calendario actualizado (D8 primero, luego D6/D7 intercalados)."""
import os, subprocess, sys
S = '/tmp/claude-0/-home-user-Umbral/103299cb-7cc6-5615-898c-8dde6d176f21/scratchpad'
out_md = sys.argv[1]

def load(p):
    ns = {}; exec(open(p).read(), ns); return ns['CLIPS']

d8 = load(f'{S}/work/catalog_d8.py'); d7 = load(f'{S}/work/catalog_d7.py'); d6 = load(f'{S}/work/catalog_d6.py')
clips = {c['id']: c for c in d8 + d7 + d6}
PUBLISHED = ['D7-20', 'D7-03', 'D7-24', 'D7-07', 'D7-22', 'D7-06', 'D7-23', 'D7-27']

def ts(s):
    s = float(s); return f"{int(s//3600):02d}:{int(s%3600//60):02d}:{int(s%60):02d}"

def dur(c):
    f = f"{S}/out/{c['id'][:2].lower()}/{c['id']}.mp4"
    if os.path.exists(f):
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True)
        try: return float(r.stdout.strip())
        except ValueError: pass
    return sum(b - a for a, b in c['cuts'])

D8_DAYS = [['D8-05', 'D8-12', 'D8-03'], ['D8-13', 'D8-08', 'D8-09'], ['D8-14', 'D8-02', 'D8-10'],
           ['D8-01', 'D8-07', 'D8-15'], ['D8-06', 'D8-11', 'D8-04']]
rest7 = sorted([c for c in d7 if c['id'] not in PUBLISHED], key=lambda c: -c['score'])
rest6 = sorted(d6, key=lambda c: -c['score'])
days = [list(d) for d in D8_DAYS]
while rest7 or rest6:
    day = []
    if rest6: day.append(rest6.pop(0)['id'])
    if rest7: day.append(rest7.pop(0)['id'])
    if len(day) < 2 and (rest7 or rest6):
        day.append((rest7 or rest6).pop(0)['id'])
    day.append('NEW')
    days.append(day)
used = [x for d in days for x in d if x != 'NEW']
assert sorted(used + PUBLISHED) == sorted(clips), set(clips) ^ set(used + PUBLISHED)

L = []; w = L.append
w('# Clips Directo 8 + calendario actualizado · Marcos Escudero Hair\n')
w('**Canal:** twitch.tv/marcosescuderohair · **Usuario obligatorio:** `@marcosescuderohair` (en la marca de agua y en todos los textos).\n')
w(f'**Directo 8:** {len(d8)} clips renderizados en 9:16 (1080×1920) con subtítulos, gancho y marca de agua. Es una videollamada de Discord de casi 3 h con amigos (Yasin, Hugo, Aiman, Rida) y espectadores que se meten a hablar; las partes de Discord se montan con las cámaras apiladas.\n')
w('> ⚠️ Escuchad cada clip antes de publicarlo: los subtítulos son automáticos y en Discord a veces se pisan las voces.\n')

w('## Banco de clips · Directo 8\n')
w('| Clip | Tramo(s) en el directo | Duración | Tema | Categoría | Potencial | Revisar |\n|---|---|---|---|---|---|---|')
for c in sorted(d8, key=lambda c: -c['score']):
    tr = ' + '.join(f"{ts(a)}–{ts(b)}" for a, b in c['cuts'])
    w(f"| **{c['id']}** | {tr} | {dur(c):.0f} s | {c['title']} | {c['cat']} | {c['score']}/10 | {c['risk'] or '—'} |")
w('')

w('## Lo que NO he sacado del Directo 8 (y por qué)\n')
w('| Tramo | Motivo |\n|---|---|')
for t, m in [
    ('00:00:00–00:08:50', 'Música con derechos de autor sonando de fondo (pantalla de espera). Riesgo de silenciado o retirada.'),
    ('00:19:29–00:20:20 y 00:23:20–00:35:10', 'El espectador "Rage" insulta (escoria humana, gordo…) y saca temas de política y sexo. Solo se usa el trozo limpio en D8-03 y D8-04.'),
    ('00:48:13–00:50:30', 'Comentarios despectivos sobre marroquíes y latinos en Barcelona y en su barrio.'),
    ('00:52:40–00:58:10 y 01:11:16–01:14:50', 'Preguntas sexuales y comentarios homófobos con una espectadora de 18-19 años en cámara.'),
    ('01:14:50–01:27:30', 'Vuelven a contar el conflicto con la chica y su novio ("hemos arruinado una relación"). Información privada de terceros.'),
    ('01:33:20–01:42:00 y 02:00:00–02:05:00', 'La "cita" en directo con la espectadora: preguntas sobre con quién se acostaría y su vida sentimental. Persona privada y tono sexual.'),
    ('02:28:00–02:35:20', 'Política (a quién votan, "España es un país de mierda").'),
    ('02:37:40–02:40:30', 'Anécdota con comentarios despectivos sobre "moros" y "negros" de su barrio.'),
    ('02:40:40–02:47:30', 'Historia de una casi pelea en un centro comercial: glorifica la violencia.'),
]:
    w(f'| {t} | {m} |')
w('')

w('## Calendario actualizado\n')
w('**Ya publicados (no se repiten):** ' + ', '.join(PUBLISHED) + '.\n')
w('- **Días 1-5:** los 15 clips del Directo 8 (3 al día), empezando por los más fuertes. **D8-13** (anuncia el directo de anécdotas "el sábado a las 9") va el día 2 para que salga **antes de ese sábado**.')
w('- **Desde el día 6:** se intercalan los pendientes del 6 y del 7 (2 al día, de mayor a menor potencial) + **🆕 NUEVO DIRECTO** reservado para el mejor clip del directo que salga esa semana. Si no hay directo nuevo, se sube el siguiente pendiente y todo se corre un hueco.')
w('- Cada clip, el mismo día en TikTok, Reels y Shorts. Horas: **[PENDIENTE]**; seguimos probando mediodía / tarde / noche.')
w('- **D7-15** (anuncia una "rueda de prensa") y **D6-07** (planes de verano): comprobad con Marcos que siguen en pie antes de subirlos.\n')
w('| Día | 1º (mediodía) | 2º (tarde) | 3º (noche) |\n|---|---|---|---|')
for i, d in enumerate(days, 1):
    cells = ['🆕 NUEVO DIRECTO' if x == 'NEW' else f"**{x}** · {clips[x]['title']}" for x in d]
    while len(cells) < 3: cells.append('—')
    w(f'| Día {i} | ' + ' | '.join(cells) + ' |')
w('')

w('## Textos listos para copiar · Directo 8\n')
for c in d8:
    w(f"### {c['id']} · {c['title']}")
    w(f"Gancho en pantalla: {c['hook'].replace(chr(92)+'N', ' ')}\n")
    w('```'); w(f"{c['title']} #shorts"); w('```')
    w('```'); w(c['caption']); w(c['cta']); w('📺 twitch.tv/marcosescuderohair · @marcosescuderohair')
    w(f"#marcosescuderohair {c['tags']} #twitch"); w('```\n')
w('Los textos de los clips del 6 y del 7 siguen en `../directos-06-07/CLIPS_Y_CALENDARIO.md`.\n')
open(out_md, 'w').write('\n'.join(L))
print('ok', out_md, len(days), 'días')

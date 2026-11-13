"""Renderiza un clip vertical 1080x1920.
Uso: render.py stream.mp4 spec.json clip.ass watermark.png out.mp4
Layouts:
  game: cámara de Marcos arriba (1080x921) + gameplay abajo (1080x999) con Hugo en PiP
  talk: Marcos arriba (1080x1122) + Hugo abajo (1080x798); recorta el chat de la izquierda
"""
import json, subprocess, sys
src, spec, ass, wm, out = sys.argv[1:6]
spec = json.load(open(spec))
cuts = spec.get('cuts') or [[spec['start'], spec['end']]]
t0 = max(cuts[0][0] - 5, 0)

fc = []
n = len(cuts)
fc.append(f"[0:v]split={n}" + ''.join(f"[iv{i}]" for i in range(n)) + f";[0:a]asplit={n}" + ''.join(f"[ia{i}]" for i in range(n)))
for i, (a, b) in enumerate(cuts):
    fc.append(f"[iv{i}]trim={a-t0:.3f}:{b-t0:.3f},setpts=PTS-STARTPTS[v{i}];[ia{i}]atrim={a-t0:.3f}:{b-t0:.3f},asetpts=PTS-STARTPTS[a{i}]")
fc.append(''.join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")

layout = spec.get('layout', 'game')
if layout == 'game':
    fc.append("[vc]split=3[s1][s2][s3]")
    fc.append("[s1]crop=395:337:885:0,scale=1080:920:flags=lanczos[top]")
    fc.append("[s2]crop=560:518:360:138,scale=1080:1000:flags=lanczos,eq=brightness=0.04:gamma=1.25[bot]")
    fc.append("[s3]crop=293:217:35:15,scale=380:282[pip]")
    fc.append("[top][bot]vstack[st];[st][pip]overlay=40:1300[lay]")
    wm_y = 1185
elif layout == 'irl':
    cw = int(spec.get('cw', 900)); cx = int(spec.get('cx', 960)); ch = 1030
    x = max(0, min(1920 - cw, cx - cw // 2))
    h = int(round(ch * 1080 / cw / 2) * 2); y = (1920 - h) // 2
    fc.append("[vc]split=2[s1][s2]")
    fc.append(f"[s2]scale=-2:480:flags=fast_bilinear,crop=270:480,boxblur=8:2,eq=brightness=-0.18,scale=1080:1920:flags=fast_bilinear[bg]")
    fc.append(f"[s1]crop={cw}:{ch}:{x}:0,scale=1080:{h}:flags=lanczos[fg]")
    fc.append(f"[bg][fg]overlay=0:{y}[lay]")
    wm_y = 215
else:
    fc.append("[vc]split=2[s1][s2]")
    fc.append("[s1]crop=610:634:200:0,scale=1080:1122:flags=lanczos[top]")
    fc.append("[s2]crop=470:347:810:373,scale=1080:798:flags=lanczos[bot]")
    fc.append("[top][bot]vstack[lay]")
    wm_y = 1135
fc.append(f"[1:v]scale=560:-1,format=rgba,colorchannelmixer=aa=0.92[wm];[lay][wm]overlay=(W-w)/2:{wm_y}[lw]")
fc.append(f"[lw]ass='{ass}',format=yuv420p[vout]")
fc.append("[ac]loudnorm=I=-14:TP=-1.5:LRA=11[aout]")

cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(t0), '-t', str(cuts[-1][1]-t0+1), '-i', src, '-i', wm,
       '-filter_complex', ';'.join(fc), '-map', '[vout]', '-map', '[aout]',
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-r', '30',
       '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart', out]
subprocess.run(cmd, check=True)
print('ok', out)

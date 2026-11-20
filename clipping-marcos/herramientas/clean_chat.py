"""Borra el texto del chat superpuesto (columna izquierda) en un tramo del stream.
Detecta trazos finos de texto (alto contraste local o color saturado de los nombres)
en x < XMAX y los sustituye por una versión muy desenfocada del fondo.
Uso: clean_chat.py stream.mp4 t_inicio t_fin salida.mp4
"""
import subprocess, sys
import numpy as np, cv2
src, t0, t1, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
W, H, XMAX = 1280, 720, 380
dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-ss', str(t0), '-t', str(t1 - t0), '-i', src,
                        '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                        '-s', f'{W}x{H}', '-r', '30', '-i', '-', '-ss', str(t0), '-t', str(t1 - t0), '-i', src,
                        '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '12', '-preset', 'veryfast',
                        '-c:a', 'aac', '-b:a', '256k', '-shortest', out], stdin=subprocess.PIPE)
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
n = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
    roi = f[:, :XMAX]
    g = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    bg = cv2.medianBlur(g, 21)
    dark = cv2.erode((bg < 60).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0   # fondo oscuro
    local = cv2.absdiff(g, bg)
    m1 = (local > 45) & dark                                # trazos de texto sobre fondo oscuro
    m2 = (hsv[..., 1] > 120) & (hsv[..., 2] > 150) & dark   # nombres de usuario en color
    mask = ((m1 | m2).astype(np.uint8) * 255)
    mask = cv2.dilate(mask, k, iterations=2)
    # solo filas con densidad de texto (evita borrar bordes de la cara aislados)
    rows = (mask > 0).mean(axis=1) > 0.04
    rows = cv2.dilate(rows.astype(np.uint8)[:, None], np.ones((15, 1), np.uint8))[:, 0] > 0
    mask[~rows] = 0
    blur = cv2.GaussianBlur(roi, (0, 0), 14)
    mf = cv2.GaussianBlur(mask, (0, 0), 3).astype(np.float32)[..., None] / 255.0
    f[:, :XMAX] = (roi * (1 - mf) + blur * mf).astype(np.uint8)
    enc.stdin.write(f.tobytes())
    n += 1
enc.stdin.close(); enc.wait(); dec.wait()
print('frames', n, out)

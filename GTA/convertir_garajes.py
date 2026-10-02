#!/usr/bin/env python3
"""
Convierte tu HTML antiguo (con <div class="propiedad"> ... flip-front / flip-back)
en garajes-data.js, que la nueva web carga automáticamente.

Uso:
    python convertir_garajes.py tu_pagina_antigua.html
Resultado:
    garajes-data.js  (déjalo en la misma carpeta que index.html)
"""
import html, json, re, sys
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit("Uso: python convertir_garajes.py tu_pagina_antigua.html")

src = Path(sys.argv[1]).read_text(encoding="utf-8")
src = re.sub(r"<!--.*?-->", "", src, flags=re.S)           # ignora comentarios

clean = lambda s: html.unescape(re.sub(r"\s+", " ", s)).strip()
chunks = re.split(r'<div\s+class="propiedad"', src)[1:]    # un trozo por garaje

car_re = re.compile(
    r'class="flip-front"[^>]*>.*?<img[^>]*?src="([^"]+)".*?<h3>(.*?)</h3>'
    r'.*?class="flip-back"[^>]*>.*?<img[^>]*?src="([^"]+)".*?<h3>(.*?)</h3>',
    re.S)

garages, total = [], 0
for i, ch in enumerate(chunks):
    h2 = re.search(r"<h2>(.*?)</h2>", ch, re.S)
    if not h2:
        continue
    title = clean(h2.group(1))
    m = re.match(r"^(.*?)\s*\((.*)\)\s*$", title)         # "Nombre (Tipo)"
    name, gtype = (m.group(1), m.group(2)) if m else (title, "Vehículos")
    cover = re.search(r'<img[^>]*?src="([^"]+)"', ch, re.S)
    id_ = re.search(r"toggleCoches\('([^']+)'", ch)
    cars = [[clean(fn), clean(bn), br.strip(), fr.strip()]   # [GTA, real, imgReal, imgGTA]
            for fr, fn, br, bn in car_re.findall(ch)]
    total += len(cars)
    garages.append({
        "id": id_.group(1) if id_ else f"g{i}",
        "name": name, "type": gtype,
        "cover": cover.group(1).strip() if cover else "",
        "cars": cars,
    })

out = "window.GARAGES = " + json.dumps(garages, ensure_ascii=False, indent=1) + ";\n"
Path("garajes-data.js").write_text(out, encoding="utf-8")
print(f"OK: {len(garages)} garajes y {total} vehículos → garajes-data.js")

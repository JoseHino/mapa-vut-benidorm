"""
Mapa de calor de Viviendas de Uso Turistico (VUT) de Benidorm.

Fuentes oficiales:
 - Registro de Turismo de la Comunitat Valenciana (GVA Dades Obertes),
   dataset "tur-gestur-vt": cada VUT con su referencia catastral.
 - Direccion General del Catastro, servicio Consulta_CPMRC: centroide de
   la parcela (EPSG:4326) a partir de los 14 primeros caracteres de la RC.

Genera un HTML autonomo (Leaflet + leaflet.heat + markercluster).
"""

import csv, json, os, re, time, urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date

CSV_URL = ("https://dadesobertes.gva.es/dataset/758f8f8e-c5af-4622-b268-a6c591710a51/"
           "resource/b1bdc28e-9813-422a-ab7a-63c21290493d/download/lista-de-viviendas-turisticas.csv")
CATASTRO = ("https://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCoordenadas.asmx/"
            "Consulta_CPMRC?Provincia=&Municipio=&SRS=EPSG:4326&RC={}")
BASE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE, "vut_gva_comunitat_valenciana.csv")
GEO_CACHE = os.path.join(BASE, "vut_benidorm_catastro_cache.json")
OUT_HTML = os.path.join(BASE, "index.html")
OUT_CSV = os.path.join(BASE, "VUT_Benidorm_geolocalizadas.csv")
UA = {"User-Agent": "Mozilla/5.0"}


def get(url, timeout=120):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()


# -- 1. Registro GVA -------------------------------------------------------
if not os.path.exists(CSV_PATH):
    print("Descargando registro GVA...")
    open(CSV_PATH, "wb").write(get(CSV_URL, 600))
rows = [r for r in csv.DictReader(open(CSV_PATH, encoding="utf8"), delimiter=";")
        if r["municipio"].strip().upper().startswith("BENIDORM")]
print(f"VUT en Benidorm: {len(rows)}")

# -- 2. Geolocalizacion por Catastro ---------------------------------------
cache = json.load(open(GEO_CACHE)) if os.path.exists(GEO_CACHE) else {}
pcs = sorted({r["ref_catastral"].strip()[:14] for r in rows if len(r["ref_catastral"].strip()) >= 14})


def consulta(pc):
    if cache.get(pc):
        return pc, cache[pc]
    for _ in range(3):
        try:
            t = get(CATASTRO.format(pc), 30).decode()
            x, y = re.search(r"<xcen>([^<]+)", t), re.search(r"<ycen>([^<]+)", t)
            ldt = re.search(r"<ldt>([^<]+)", t)
            return pc, ([float(x.group(1)), float(y.group(1)), ldt.group(1) if ldt else ""] if x else None)
        except Exception:
            time.sleep(2)
    return pc, None


with ThreadPoolExecutor(6) as ex:
    for pc, v in ex.map(consulta, pcs):
        cache[pc] = v
json.dump(cache, open(GEO_CACHE, "w"))
print(f"Parcelas: {len(pcs)} | geolocalizadas: {sum(1 for p in pcs if cache.get(p))}")


def num(v):
    try:
        return float(str(v).replace(",", ".").strip())
    except ValueError:
        return 0


def piso(direccion):
    # "AV MEDITERRANEO, 3, Es:1 Pl:05 Pt:B" -> "Es:1 Pl:05 Pt:B"
    m = re.search(r"(Es:.*)$", direccion)
    return m.group(1).strip() if m else ""


# -- 3. Agregacion por edificio --------------------------------------------
edif = defaultdict(list)
sin_geo = []
for r in rows:
    pc = r["ref_catastral"].strip()[:14]
    if cache.get(pc):
        edif[pc].append(r)
    else:
        sin_geo.append(r)

data = []
with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["signatura", "direccion", "cp", "ref_catastral", "plazas", "dormitorios",
                "superficie_m2", "fecha_alta", "lon", "lat"])
    for pc, lst in edif.items():
        lon, lat, ldt = cache[pc]
        unidades = []
        for r in sorted(lst, key=lambda r: r["direccion"]):
            unidades.append([r["signatura"], piso(r["direccion"]), int(num(r["plazas_totales"])),
                             int(num(r["dormit_totales"])), r["fecha_alta"], num(r["superficie"])])
            w.writerow([r["signatura"], r["direccion"], r["cp"], r["ref_catastral"],
                        r["plazas_totales"].strip(), r["dormit_totales"], r["superficie"],
                        r["fecha_alta"], f"{lon:.6f}", f"{lat:.6f}"])
        calle = re.sub(r",?\s*Es:.*$", "", lst[0]["direccion"]).strip()
        data.append([round(lat, 6), round(lon, 6), calle, lst[0]["cp"], pc, unidades])

data.sort(key=lambda d: -len(d[5]))
total = sum(len(d[5]) for d in data)
plazas = sum(u[2] for d in data for u in d[5])
anios = Counter(r["fecha_alta"][-4:] for r in rows if r["fecha_alta"])
cps = Counter(r["cp"] for r in rows)
print(f"Mapeadas: {total} VUT, {plazas} plazas, {len(data)} edificios; sin geolocalizar: {len(sin_geo)}")

meta = {
    "total": total, "plazas": plazas, "edificios": len(data), "registro": len(rows),
    "sin_geo": len(sin_geo), "fecha": date.today().strftime("%d/%m/%Y"),
    "anios": sorted(anios.items()), "cps": cps.most_common(),
}

# -- 4. HTML ----------------------------------------------------------------
html = open(os.path.join(BASE, "plantilla_mapa_vut_benidorm.html"), encoding="utf8").read()
html = html.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
html = html.replace("/*__META__*/null", json.dumps(meta, ensure_ascii=False, separators=(",", ":")))
open(OUT_HTML, "w", encoding="utf8").write(html)
print(f"OK -> {OUT_HTML} ({os.path.getsize(OUT_HTML) / 1e6:.1f} MB)")

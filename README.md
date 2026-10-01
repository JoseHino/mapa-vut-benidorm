# Mapa de calor de viviendas de uso turístico (VUT) · Benidorm

**Mapa:** https://josehino.github.io/mapa-vut-benidorm/

5.631 VUT en 752 edificios, 19.724 plazas (descarga del 01/10/2026).

## Actualización automática
Una tarea de GitHub Actions (`.github/workflows/actualizar.yml`) se ejecuta **cada día a las 07:30** (hora de Madrid):
1. Descarga el registro completo de la GVA y regenera el mapa (si la descarga falla, se mantiene la versión anterior).
2. Geolocaliza y pregunta al Catastro solo por las parcelas nuevas; en el resto solo recalcula qué viviendas son VUT.
3. Publica solo si algo ha cambiado.

También se puede lanzar a mano desde **Actions → Actualizar datos → Run workflow**.

## Fuentes oficiales
- **Registro de Turismo de la Comunitat Valenciana**: GVA Dades Obertes, dataset [`tur-gestur-vt`](https://dadesobertes.gva.es/es/dataset/tur-gestur-vt). Cada vivienda con su referencia catastral.
- **Dirección General del Catastro**: servicio `Consulta_CPMRC`, que da el centroide de la parcela a partir de la referencia catastral.

Las viviendas de un mismo edificio comparten punto. 3 VUT sin referencia catastral válida no aparecen en el mapa.

## Vista 3D por edificio
Al pulsar un edificio en el mapa (zoom 16 o más) y luego **Ver edificio en 3D**, se abre su volumetría real con cada planta coloreada según el % de unidades inscritas como VUT. Incluye una fachada esquemática por escalera (plantas × puertas) y la ortofoto PNOA como suelo para ver la orientación respecto al mar.

- Unidades por planta y puerta: Catastro, `Consulta_DNPRC` (69.928 unidades en los 752 edificios). Las VUT se cruzan por referencia catastral completa: 5.629 de 5.631 situadas en su piso.
- Volumetría: Catastro INSPIRE (edificios), huella y nº de plantas de cada cuerpo.
- Limitaciones: el Catastro no indica hacia dónde mira cada puerta, y la planta baja puede incluir locales.

## Archivos
- `index.html`: el mapa (Leaflet).
- `VUT_Benidorm_geolocalizadas.csv`: las viviendas con lat/lon (EPSG:4326).
- `generar_mapa_vut_benidorm.py`: descarga el registro, geolocaliza por Catastro y regenera `index.html`.
- `generar_edificios.py`: unidades y volumetría de cada edificio desde el Catastro (incremental) → `data/edificios/*.json`.
- `edificio3d.js`: visor 3D (three.js).

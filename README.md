# Mapa de calor de viviendas de uso turístico (VUT) · Benidorm

**Mapa:** https://josehino.github.io/mapa-vut-benidorm/

5.631 VUT en 752 edificios, 19.724 plazas (descarga del 01/10/2026).

## Fuentes oficiales
- **Registro de Turismo de la Comunitat Valenciana**: GVA Dades Obertes, dataset [`tur-gestur-vt`](https://dadesobertes.gva.es/es/dataset/tur-gestur-vt). Cada vivienda con su referencia catastral.
- **Dirección General del Catastro**: servicio `Consulta_CPMRC`, que da el centroide de la parcela a partir de la referencia catastral.

Las viviendas de un mismo edificio comparten punto. 3 VUT sin referencia catastral válida no aparecen en el mapa.

## Archivos
- `index.html`: el mapa (Leaflet).
- `VUT_Benidorm_geolocalizadas.csv`: las viviendas con lat/lon (EPSG:4326).
- `generar_mapa_vut_benidorm.py`: descarga el registro, geolocaliza por Catastro y regenera el mapa (`Mapa_VUT_Benidorm.html`; copiarlo como `index.html`).

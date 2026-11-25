# Recursos del rediseño

Piezas reutilizables de la síntesis «Revelado» (ver `../02-sintesis-revelado.md`).

| Archivo | Qué es |
| --- | --- |
| `tv.svg` | El televisor en vector, por capas: casco, tapa, costado con trama, frente con pinceladas, marco, pantalla (`tv-pantalla.jpg`), perillas, parlante, placa, carpeta tejida y antena con papel aluminio. Base para modelar o redibujar. |
| `stickers/*.svg` | Seis stickers originales: `perro` («¡Cuidado! Perro Bravo»), `diablo`, `copihue`, `estrella`, `fia` («Hoy no se fía, mañana sí»), `altiro` («¡Al tiro!»). Usan Encode Sans Condensed y Bodoni Moda. |
| `textura-negro.jpg`, `textura-rojo.jpg`, `textura-crema.jpg` | Texturas de 512 px que se repiten sin costuras: el cuarto, la luz y el papel. |
| `generadores/` | Scripts que produjeron los tableros de Figma. No son parte del sitio. |

## Regenerar los tableros

Requieren Python 3 con `numpy` y `Pillow`, y Node con Playwright (Chromium). Se corrieron desde una carpeta de trabajo con una subcarpeta `assets/`; antes de usarlos, ajusta las rutas `S` y `REPO` al principio de cada script.

1. `v1_assets_y_fuentes.py`: genera `assets/fonts.css` (fuentes de Google incrustadas) y los recursos de la primera iteración.
2. `s_assets.py`: texturas, fondos de sección y fotos reveladas.
3. `s_tv.py`: el TV y los stickers en SVG. `node s_render_svg.js <assets> s_tv_full.svg <salida.png> 2` lo rasteriza.
4. `s_fx.py`: textura pintada sobre el TV rasterizado y los rastros de cursor.
5. `s_board.py`: arma `s_boards.html` desde `s_boards.tpl.html`, listo para enviar a Figma.

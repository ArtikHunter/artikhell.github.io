# Portada «Revelado» v1 — plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar la portada del documento 03 en el sitio estático, con la galería anterior conservada y restilizada.

**Architecture:** HTML/CSS/JS sin compilación ni librerías. `script.js` conserva la galería y expone un registro de funciones por cuadro de scroll (`enCadaScroll`). Los módulos nuevos (`intro.js`, `liquido.js`, `secciones.js`, `cursor.js`) se cargan con `defer` después de los datos y de `script.js`, y comparten sus utilidades globales (`$`, `$$`, `clamp`, `lerp`, `smoothstep`, `reduceMotion`, `scheduleScroll`).

**Tech Stack:** HTML, CSS, JavaScript clásico, WebGL 1 (fondo líquido) y Canvas 2D (rastro del cursor, estática). Pruebas con Python `unittest` y Playwright.

**Spec:** `docs/rediseno/03-portada-en-codigo.md` (y `AGENTS.md`).

## Global Constraints

- Sin rótulos ni indicaciones visibles: el único `h2` visible es «Contacto».
- Paleta: negro `#0b0707`, rojo `#c42a1c`, antorcha `#ff5c3c`, crema `#efe6d2`. Roles: Dirección `#d7301f`, Fotografía `#3fa7b5`, Cámara `#b04a8f`, Gestión cultural `#c9b037`.
- Fuentes: Bodoni Moda, Encode Sans Condensed e IBM Plex Mono (Google Fonts, con fuentes del sistema como respaldo).
- `prefers-reduced-motion: reduce`: sin secciones bloqueadas, sin rastro de cursor, sin animaciones largas; se ve el estado final.
- Sitio estático para GitHub Pages: sin build, sin dependencias de npm y sin servicios externos, salvo Google Fonts, FormSubmit y los videos incrustados.
- Las pruebas bloquean las peticiones externas: todo debe funcionar sin las fuentes, sin FormSubmit y sin WebGL.

## Review Focus

- Una carga que nunca termina (falta una imagen o JS lento): la página debe quedar usable. Prueba: un 404 en `recursos/tv.webp` no deja `html` sin `listo`.
- Volver hacia arriba por las secciones bloqueadas: cada estado se invierte sin saltos. Prueba: el progreso 0,7 → 0,1 → 0,7 deja los mismos valores.
- Móvil con pantalla táctil: sin cursor propio, con TV y textos legibles a 390 px. Prueba: en contexto táctil `html` no tiene `cursor-activo`.
- Formulario enviado dos veces o sin red: no duplica ni se cuelga. Prueba: el botón queda desactivado mientras envía y un error de red muestra el correo directo.
- Datos incompletos (sin video, sin URL, sin fotos): nada se rompe. Prueba: una película sin `video` no es botón; un enlace sin `url` queda `aria-disabled`.

---

### Task 1: Recursos y entorno de pruebas

**Files:**
- Create: `recursos/tv.webp`, `recursos/tv-movil.webp`, `recursos/retrato.jpg`, `recursos/retrato-movil.jpg`, `recursos/carga.jpg`, `recursos/carta-ajuste.png`, `recursos/textura-negro.jpg`, `recursos/textura-crema.jpg`, `recursos/textura-rojo.jpg`, `recursos/fondo-tv.jpg`, `recursos/liquido.jpg`
- Modify: `docs/rediseno/recursos/generadores/s_tv.py` (salida del TV con la pantalla transparente)
- Test: `tests/test_portfolio.py` (helper `esperar_carga`)

- [ ] Generar el TV sin contenido de pantalla (anillo del marco con `fill-rule="evenodd"`, reflejo del vidrio semitransparente) a 2200 px y 900 px de ancho, en WebP de calidad 82.
- [ ] Generar el retrato revelado en rojo (2400×1500, hombre a la derecha) y el móvil (1080×1920), la copia de la carga (560×700), la carta de ajuste (600×450), las tres texturas de 512 px, el fondo del TV con el halo (1920×1200) y el respaldo del líquido (1920×1200).
- [ ] Verificar: `python3 -c` con Pillow imprime los tamaños esperados y cada archivo pesa menos de 900 KB.
- [ ] Commit.

### Task 2: Estructura, estilos base y limpieza de `script.js`

**Files:**
- Modify: `index.html` (estructura completa), `style.css` (tokens, texturas, secciones, galería restilizada), `script.js` (quitar portada vieja, ondas, menú, cursor viejo y retrato viejo; agregar el registro de scroll)
- Test: `tests/test_portfolio.py`

**Interfaces:**
- Produces: `enCadaScroll: Array<() => void>` y `scheduleScroll()` en `script.js`; `smoothstep(a, b, x)` global; `.site-header` con el enlace `.marca`; contenedores vacíos `#cine-peliculas`, `#trayectoria-filtros`, `#trayectoria-guia`.

- [ ] Prueba `test_only_contact_has_a_visible_section_title`: los `h2` visibles son exactamente `["Contacto"]` y no aparece en el texto visible ninguna de las palabras «Fotografía», «Cine» ni «Trayectoria» como título.
- [ ] Prueba `test_catalog_and_resources` actualizada: incluye los archivos de `recursos/`, `intro.js`, `liquido.js`, `secciones.js`, `cursor.js`, `peliculas.js` y `trayectoria.js`.
- [ ] Quitar `test_mobile_menu_escape_restores_focus` y `test_motion_preference_changes_do_not_accumulate_waves` (las funciones ya no existen).
- [ ] Ejecutar: `CHROMIUM_PATH=/opt/pw-browsers/chromium python -m unittest discover -s tests`. Esperado: las pruebas de galería siguen en verde.
- [ ] Commit.

### Task 3: Carga y TV (`intro.js`)

**Interfaces:**
- Produces: `cargaTerminada: Promise<void>`; clase `listo` en `html` al terminar; `cambiarCanal(paso = 1)`; `canalActual: number`.

- [ ] Prueba `test_loader_finishes_and_unlocks_scroll`: `html.listo` antes de 7 s, `.carga` oculta y `scrollY` cambia con `scrollTo`.
- [ ] Prueba `test_loader_survives_a_missing_tv_image`: con `recursos/tv.webp` en 404, `html.listo` igual llega.
- [ ] Prueba `test_tv_knob_changes_channel`: click en `.tv-perilla` cambia el `src` de `.tv-canal`.
- [ ] Implementar la precarga (mínimo 1200 ms, máximo 6000 ms) con `--carga` de 0 a 1, el reloj y el encendido del TV (`.tv.encendido`). Canales: `["DR-1.jpg","CFC-20.jpg","AH-1.jpg","VENT-1.jpg","recursos/carta-ajuste.png","HM-10.jpg"]`, cada 5000 ms, con estática de 280 ms entre canal y canal. Inclinación de ±6°, solo con mouse.
- [ ] Commit.

### Task 4: Retrato bloqueado (`intro.js`)

**Interfaces:**
- Produces: `introProgress: number` (0..1) y `updateIntroScroll()` registrada en `enCadaScroll`. Fases: zoom `0–0.22`, fundido `0.20–0.28`, nombre `0.28–0.50`, resumen `0.40–0.62`, pausa `0.62–0.80` y líquido `0.80–1`.

- [ ] Prueba `test_intro_reveals_name_and_summary`: en p = 0, `.tv-capa` con opacidad 1; en p = 0.7, `.tv-capa` con opacidad 0, el `h1` dentro de la ventana y `--resumen` = 1; en p = 1, `clip-path` del retrato distinto de `none`.
- [ ] Prueba `test_intro_states_reverse_cleanly`: los valores en p = 0.7 coinciden después de 0.7 → 0.1 → 0.7.
- [ ] Prueba `test_reduced_motion_intro_is_static`: con `reduced_motion="reduce"`, `.intro-escena` con `position` distinto de `sticky`, y `h1` y resumen visibles con opacidad 1.
- [ ] Commit.

### Task 5: Fondo líquido (`liquido.js`)

**Interfaces:**
- Consumes: `introProgress`, `galleryProgress`.
- Produces: `tintaPara(estado: {intro, galeria, cineTop, alto}) -> number` (función pura) y `liquido = { tinta: number, activo: boolean }`.

- [ ] Prueba `test_ink_darkens_down_the_page`: `tintaPara` crece entre el final del intro (0.35), el visor (0.62), el índice (0.82) y la llegada de cine (1.0).
- [ ] Shader WebGL a media resolución, en pausa fuera de la zona; sin WebGL, `html.sin-webgl` muestra `recursos/liquido.jpg`.
- [ ] Commit.

### Task 6: Galería restilizada

- [ ] Prueba `test_side_photos_float_and_turn`: las `.side-image` tienen una animación activa; con `reduced_motion` no la tienen. Pasar el mouse agrega `is-girando` al `.side-slot`.
- [ ] Actualizar `test_closed_eye_and_tear_offer_an_unobstructed_photo`: `.cursor-halo` pasa a `.cursor-mira`; la ayuda de navegación existe solo para lectores de pantalla.
- [ ] Ajustar el CSS (líquido visible, flotación, giro con reverso crema, brillo central, revelado negro → rojo → color) y quitar los números y la cantidad de fotos del índice.
- [ ] Commit.

### Task 7: Cine (`peliculas.js`, `secciones.js`)

**Interfaces:**
- Produces: `peliculas: Array<{id, titulo, anio, duracion, credito, fotograma, video}>`, `renderPeliculas()` y `urlIncrustada(url) -> string | null`.

- [ ] Prueba `test_films_show_year_duration_and_credit`: cada `.pelicula-datos` es igual a `anio · duracion · credito`.
- [ ] Prueba `test_video_embeds_only_when_available`: sin `video` no hay botón; con `https://youtu.be/abc123` el click crea un iframe `https://www.youtube-nocookie.com/embed/abc123?autoplay=1`.
- [ ] Apertura del fotograma destacado según el scroll (`--apertura` de 0 a 1) e inundación de tinta antes de la sección.
- [ ] Commit.

### Task 8: Trayectoria (`trayectoria.js`, `secciones.js`)

**Interfaces:**
- Produces: `roles` (id → `{nombre, color}`), `trayectoria: Array<{anio, rol, titulo, tipo, descripcion, imagenes, enlaces: [{nombre, url}]}>`, `renderTrayectoria()`.

- [ ] Prueba `test_career_filters_and_rows`: el filtro «Dirección» deja solo filas de dirección y marca `aria-pressed`; el click en una fila alterna `aria-expanded` y muestra su detalle; un enlace sin URL queda `aria-disabled="true"`.
- [ ] Estática de cambio de canal (pico de 0,55 cuando el borde superior pasa por la mitad de la pantalla) y entrada de las filas como teletexto.
- [ ] Commit.

### Task 9: Contacto (`secciones.js`)

- [ ] Prueba `test_contact_form_sends_and_reports`: con la ruta de FormSubmit simulada (`{"success":"true"}`), enviar muestra «Mensaje enviado» y limpia el formulario. Con un 500, muestra el correo directo. Vacío no envía nada.
- [ ] `fetch` a `action` con `/ajax/` insertado, JSON, botón desactivado mientras envía, trampa `_honey`, sala roja revelada desde la lámpara (`--luz`).
- [ ] Commit.

### Task 10: Cursor B (`cursor.js`)

**Interfaces:**
- Produces: `cursorFrame: number` (0 en reposo) y `.cursor-mira[data-estado]` ∈ `normal | foto | video | enlace`.

- [ ] Reescribir `test_pointer_animation_stops_when_idle`: mover el mouse muestra `.cursor-mira.is-visible`, y `cursorFrame` vuelve a 0 en reposo.
- [ ] Prueba `test_cursor_states_and_preferences`: sobre una `.side-image` el estado es `foto`; con `reduced_motion` o pantalla táctil, `html` no tiene `cursor-activo`.
- [ ] Commit.

### Task 11: Documentación y verificación final

- [ ] Actualizar `LEEME.md` (archivos nuevos, cómo editar películas, trayectoria y resumen, y la activación de FormSubmit) y `AGENTS.md` (cursor B).
- [ ] Suite completa en verde; capturas a 1440×900 y 390×844 en cada sección; sin errores en la consola.
- [ ] Commit y push a `claude/admiring-carson-jqybwj`.

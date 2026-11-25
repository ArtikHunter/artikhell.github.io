# Portada en código (v1) — diseño

Primera implementación de la portada «Revelado» en el sitio, con tu feedback del 25-11-2026 sobre la síntesis. Aprobaste avanzar a código para verla en el navegador; este documento fija qué se construye. Lo que es decisión mía va marcado como **(mi decisión)** para que lo revises.

## Qué cambia respecto de la síntesis

- **Cursor B · Fósforo** (elegido por ti).
- **Secciones que se «bloquean»** mientras haces scroll, como la galería de la versión anterior.
- **La galería vuelve a la portada**: las fotos esparcidas del recorrido anterior, con todo lo que ya estaba programado (crecer al centro, ficha técnica, flechas, ojo y lágrima, índice con filtros), adaptado al nuevo diseño.
- **Fondo líquido animado**: papel crema con tinta negra en movimiento detrás de la galería. Las fotos laterales flotan y giran sobre su eje al pasar el mouse; la del centro es la que está fuera del líquido.
- **Cine**: bajo cada video, año, duración y tu crédito.
- **Contacto**: aquí sí dice CONTACTO, con un formulario que envía el correo solo.
- **Transiciones** marcadas entre todas las secciones.

## Principios (sin cambios)

Ver `AGENTS.md`. Sin rótulos ni indicaciones, salvo «Contacto» y las etiquetas de los campos del formulario. Paleta negro / rojo / crema, fondos con textura y todo aparece desde la oscuridad. Con «reducir movimiento» no hay secciones bloqueadas ni rastro de cursor: se ve el estado final de cada sección.

## Recorrido de la página

| # | Sección | Qué pasa al hacer scroll |
| --- | --- | --- |
| 0 | Carga | Cuarto oscuro: una copia sale del corte y se revela mientras cargan el TV, el retrato y la primera foto. Al terminar, se apaga la luz y el TV se enciende con la línea del tubo. |
| 1 | TV → retrato (sección bloqueada) | La cámara entra a la pantalla del TV; la imagen pasa por estática y queda tu retrato revelado en rojo. Tu nombre sube desde abajo y aparece el resumen (3 a 5 líneas que escribirás tú). Pausa en el estado ideal. Después sube el líquido de revelado desde abajo y tapa el retrato. |
| 2 | Galería (sección bloqueada, código anterior) | Fotos esparcidas flotando en el líquido → la central crece con su ficha, flechas, ojo y lágrima → baja al índice de colecciones. El líquido se oscurece a medida que bajas. |
| 3 | Cine | La tinta inunda todo hasta negro; el fotograma de la película destacada se abre desde una línea, como un proyector. Debajo de cada video: año · duración · crédito. |
| 4 | Trayectoria | Cambio de canal: estática de TV al cruzar el borde. Las filas entran como teletexto. Guía por colores, filtros, filas que se abren con Letterboxd, TMDB y ficha. |
| 5 | Contacto | Se enciende la luz de seguridad: la sala roja aparece desde la lámpara. «CONTACTO», el formulario y tu correo. |

## Decisiones por sección

**Carga.** Precarga el TV, el retrato y la primera foto del TV. Dura entre 1,2 y 6 segundos; si algo falla, igual termina. Sin JavaScript no aparece. **(mi decisión)** El reloj de cuarto oscuro cuenta los segundos reales de carga.

**TV.** Se usa el TV 2D como imagen con la pantalla transparente; lo que se ve en la pantalla es HTML: tus fotos como canales (cambian solas cada 5 s y con la perilla), estática entre canal y canal y la carta de ajuste como un canal más. Se inclina unos grados siguiendo el mouse. Los stickers son SVG encima, para que puedas cambiarlos. Cuando tengas tu modelo 3D, reemplaza la imagen sin tocar el resto.

**Retrato.** Versión revelada en rojo de `perfil.jpg`, para escritorio y para móvil. El resumen se revela de arriba hacia abajo, línea por línea. **(mi decisión)** Mientras no lo escribas, se ve un texto entre corchetes.

**Galería.** Se conserva el código anterior completo. Cambios de diseño: fondo líquido (WebGL; si el navegador no lo tiene, una imagen fija), fotos laterales flotando y girando al pasar el mouse (con el reverso de papel crema), la central con brillo de copia mojada, revelado negro → rojo → color al entrar, y colores y tipografías nuevos. **(mi decisión)** Se quitan textos que son indicaciones: la ayuda «Para navegar, usar flechas o las teclas A/D» queda solo para lectores de pantalla, se quita «BENJAMÍN BRAVO» bajo el visor y se quitan la numeración y la cantidad de fotos del índice.

**Cine.** Los datos viven en `peliculas.js` (título, año, duración, crédito, fotograma, video). Si una película tiene enlace de YouTube o Vimeo, el fotograma se vuelve reproductor al hacer click; si no, es solo imagen. **(mi decisión)** Mientras faltan datos se muestran `[año]` y `[duración]`, y los fotogramas son fotos tuyas.

**Trayectoria.** Los datos viven en `trayectoria.js`. Colores de rol: Dirección rojo, Fotografía cian, Cámara magenta, Gestión cultural amarillo. Varias filas pueden estar abiertas a la vez. **(mi decisión)** Un enlace sin URL aparece apagado, para que veas dónde falta.

**Contacto.** Formulario con nombre, correo y mensaje. **(mi decisión)** Se envía con FormSubmit (gratis, sin cuenta, funciona en GitHub Pages). El primer mensaje real te llega como un correo de FormSubmit para activar el formulario; desde ahí, cada mensaje llega a tu correo. Si el envío falla, se muestra tu correo para escribir directo. Se puede cambiar por Formspree u otro servicio editando una línea.

**Cursor B.** Una mira fina con una línea roja que se apaga lento (el fósforo del tubo). Sobre una foto aparecen esquinas de visor; sobre un video, ▶; sobre un enlace, una línea. Solo con mouse; en pantallas táctiles y con «reducir movimiento» se usa el cursor normal.

## Archivos

- `index.html`: estructura nueva (portada completa).
- `style.css`: estilos nuevos; la galería conserva sus reglas de posición adaptadas al diseño nuevo.
- `script.js`: la galería anterior y las utilidades compartidas (se quitan la portada vieja, las ondas, el menú y el cursor viejo).
- `intro.js` (carga, TV, retrato), `liquido.js` (fondo animado), `secciones.js` (cine, trayectoria, contacto y sus transiciones), `cursor.js` (cursor B).
- `peliculas.js` y `trayectoria.js`: datos que editas tú, igual que `colecciones.js`.
- `recursos/`: TV, retratos revelados, copia de la carga y texturas.

## Fuera de esta versión

Miniaturas o versiones livianas de las 94 fotos originales (siguen pesando ~163 MB), el modelo 3D del TV, páginas de archivo separadas y una pantalla de carga más elaborada.

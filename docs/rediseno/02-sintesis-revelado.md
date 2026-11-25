# Rediseño — síntesis «Revelado» (segunda iteración)

Síntesis de las tres direcciones según tu feedback del 24-11-2026. Sigue siendo diseño: el código del sitio no se ha tocado.

**Figma:** https://www.figma.com/design/Ln30OsRkhUMcGoTd4unp8i — página **«Síntesis — Revelado»** (la exploración anterior quedó en «Rediseño — exploración»).

| Marco | Contenido |
| --- | --- |
| S · Página escritorio | La portada completa, sin rótulos |
| S · Notas de interacción | Notas alineadas con cada sección de la página (no forman parte del diseño) |
| S · Carga (escritorio) | Pantalla de carga en escritorio |
| S · Móvil | Carga, encabezado, retrato, fotos → cine, trayectoria, contacto |
| S · Cursor y rastro | Tres opciones de cursor (A recomendada) |
| S · Materiales | Idea rectora, texturas, revelado, tipografía, stickers y el TV en vector |

## Principio que manda sobre todo lo demás

**Nada de rótulos ni indicaciones.** Ni títulos de sección («Fotografía», «Cine», «Trayectoria»), ni conteos («8 colecciones», «89 fotos»), ni instrucciones («presiona OK»), ni etiquetas como «Presentación», «Ahora en pantalla» o «04 · Contacto». Quien abre el sitio ya te conoce; las imágenes, el orden y el cursor dicen dónde está y qué se puede abrir. Quedó escrito en `AGENTS.md` (y `CLAUDE.md` lo importa) para que cualquier sesión futura, de Claude o de Codex, lo respete.

## La idea que ordena la amalgama: «Revelado»

Todo aparece desde la oscuridad.

- **Negro = el cuarto.** Fondos con grano, polvo y pelusas de película.
- **Rojo = la luz que revela.** Luz de seguridad, brillo del tubo, fuego de los Diablos. Trama de cómic en los halos.
- **Crema = el papel.** Donde queda la imagen: copias, sobre, papel con fibras.

El TV, las fotos, el cine, la trayectoria y el sobre son objetos dentro de ese cuarto. Los colores de la carta de ajuste (cian, magenta, amarillo) solo viven en el TV y en los roles de la trayectoria.

## Qué se tomó de cada dirección

| Sección | Decisión (tuya) | Cómo quedó |
| --- | --- | --- |
| Carga | Pliego + Cuarto rojo, también en escritorio | Una copia sale de un corte en la página y se revela bajo la luz de seguridad. La imagen saliendo y revelándose *es* la barra de progreso; el reloj de cuarto oscuro (00:42) es opcional. |
| Encabezado | TV de Señal abierta, estilizado 2D, con stickers chilenos; lo modelarás tú | TV rojo con contorno de tinta, trama tipo cómic, pinceladas y registro corrido (Arcane / Spider-Verse), carpeta tejida y antena con papel aluminio. Stickers originales: «¡Cuidado! Perro Bravo», diablo, copihue, estrella. Sin texto en pantalla. Es una base editable. |
| Retrato | Foto tuya, solo nombre y una descripción corta, estilo Cuarto rojo | Retrato revelado en rojo a todo el ancho, nombre en Bodoni cursiva negra y una línea. |
| Fotografía | Señal abierta + el degradé claro → oscuro de Cuarto rojo | Cuatro fotos (una por colección) y una quinta cortada en el borde. El fondo pasa de papel a niebla y a negro. Cada foto se revela al entrar en pantalla. |
| Cine | Cuarto rojo | Película destacada a todo el ancho con el título como cartela; la segunda debajo. |
| Trayectoria | Señal abierta («la mejor por diferencia») + enlaces a TMDB / Letterboxd | La guía de programación, sin título. Los chips de color son filtro y leyenda a la vez. Las filas de películas abren sinopsis, fotograma y enlaces (Letterboxd, TMDB, ficha). Gestión abre fotos y afiche. |
| Contacto | Pliego + Cuarto rojo | «Fin.» sobre la sala roja y el sobre aeropostal (franjas rojo/negro) con tu correo; sticker «¡Al tiro!». |
| Móvil | Cuarto rojo | El retrato revelado a pantalla completa con el nombre encima. |

Para ir al archivo hay un solo gesto sin palabras: el botón rojo con «→» (heredado del botón OK del control remoto), además de las propias fotos y películas, que abren su colección o su ficha.

## Cursor y rastro (por elegir)

El cursor reemplaza a los rótulos: cambia de forma sobre lo que se puede abrir (foto → cuentahílos, película → ▶, enlace → ojo). Con «reducir movimiento» el rastro se apaga.

- **A · Luz de seguridad (recomendada):** punto de luz roja con estela de trama que se apaga. Es el revelado hecho cursor.
- **B · Fósforo:** mira fina con una línea que se apaga lento, como el fósforo del tubo. Más discreta.
- **C · Tinta:** gota que deja una pincelada crema con trama roja. La más expresiva y la más ruidosa.

## Tipografía

- **Bodoni Moda** cursiva negra: nombre, títulos, «Fin.».
- **Encode Sans Condensed** (Impallari Type, Argentina): trayectoria, cartelas, enlaces.
- **IBM Plex Mono**: años, roles, datos.

## Contenido de muestra que falta reemplazar

- La línea bajo tu nombre («Cine y fotografía — Santiago de Chile»): escríbela tú.
- Tu lista real de trabajos para la trayectoria: año, rol, título, tipo; enlaces de Letterboxd, TMDB o festivales; fotos y afiches de las actividades de gestión.
- Fotogramas reales de «Señales de Radio» y «Olmué» (en el diseño se usan fotos tuyas como reemplazo).
- Usuario de Instagram y, si lo quieres, el CV en PDF.

## Recursos guardados en el repositorio

`docs/rediseno/recursos/`: el TV en vector (`tv.svg`), los seis stickers en SVG, las tres texturas repetibles y los scripts que generaron los tableros (`generadores/`). Ver el README de esa carpeta.

## Siguiente paso

Elegir el cursor y revisar la síntesis en Figma (puedes comentar directamente sobre los marcos). Con eso se cierra el diseño de la portada; después se escribe el diseño técnico y recién ahí se toca el código.

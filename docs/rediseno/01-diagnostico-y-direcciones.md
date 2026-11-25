# Rediseño — diagnóstico y direcciones visuales

> Superado por [`02-sintesis-revelado.md`](02-sintesis-revelado.md): se conserva como historial.

Primera etapa del rediseño: diagnóstico del sitio actual y tres direcciones visuales para elegir **antes** de tocar el código. Todavía no se ha modificado ningún archivo del sitio.

**Figma:** https://www.figma.com/design/Ln30OsRkhUMcGoTd4unp8i — página «Rediseño — exploración», 8 tableros:

| Tablero | Contenido |
| --- | --- |
| 00 · Diagnóstico | Por qué se ve genérico, con capturas anotadas |
| 01 · Sitio actual | Recorrido completo en 10 pantallas + móvil (referencia) |
| D1 · Señal abierta | Escritorio completo + sistema, móvil y pantalla de carga |
| D2 · Pliego | Escritorio completo + sistema, móvil y pantalla de carga |
| D3 · Cuarto rojo | Escritorio completo + sistema, móvil y pantalla de carga |

Las capas son editables (texto, colores, imágenes). Las fotos son tuyas, con tratamientos de prueba. Los créditos del CV, años, festivales y textos de presentación son **de ejemplo** y van entre corchetes donde falta tu información.

## Diagnóstico: por qué se ve genérico

El sitio está bien construido. El problema es que casi todo lo que se ve viene de un repertorio común de «portafolio oscuro elegante» y casi nada viene de tus fotos, tus películas o de Chile.

1. **Tipografía de plantilla.** Italiana + DM Sans + DM Mono es la combinación estándar del portafolio «de lujo». Italiana es una didona finísima pensada para moda y cosmética.
2. **Paleta que no sale de tu obra.** Negro cálido, crema y un dorado (`#c8ad84`) que no aparece en ninguna foto. Tu obra es rojo antorcha, salitre, tierra de cancha y blanco y negro duro.
3. **Decoración sin contenido.** Órbitas, ruido, resplandores, ondas en canvas, línea central, halo del cursor. La portada no muestra ni una foto ni un fotograma.
4. **Patrones de plantilla.** Nombre gigante como portada, punto de color al final del título, navegación numerada en píldoras, botones redondos con flecha, microetiquetas mono.
5. **Sin voz ni lugar.** Textos en «placeholder»; Alto Hospicio, Humberstone, Iquique, los Diablos Rojos o el Cuteños FC no aparecen en el diseño.
6. **Fotos tratadas como piezas de interfaz.** Tarjetas flotantes y collage; el marco compite con la imagen. Marca de agua dentro de cada foto.
7. **El cine casi no existe.** Dos carteles con degradados de relleno.
8. **Lo que sí es tuyo y se conserva:** el ojo con la lágrima, el visor con datos técnicos, la transición al índice y los nombres de las colecciones.
9. **La estructura no calza con el objetivo.** El archivo completo vive hoy en la portada.

### Estructura propuesta

- **Portada (index):** quién eres · selección de fotos · uno o dos cortos · trayectoria interactiva (CV) · contacto.
- **/fotografia:** archivo con el visor actual, colecciones y filtros (se reutiliza casi todo el código existente).
- **/cine:** archivo con una ficha por película (fotogramas, sinopsis, créditos, festivales).

Pendiente técnico común a cualquier dirección: las 94 fotos suman ~163 MB a tamaño completo. Hacen falta miniaturas y versiones para pantalla.

## Las tres direcciones

### D1 · Señal abierta (televisión)

La portada es un televisor 3D que se sintoniza; cada sección es un canal. Fotos como fotogramas con código de tiempo, CV como guía de programación, contacto como la carta de ajuste del cierre de transmisiones.

- **Tipografía:** Encode Sans Condensed (Impallari Type, Argentina) + IBM Plex Mono.
- **Color:** negro tubo, fósforo, rojo señal y los colores de la carta de ajuste.
- **Referencias:** televisores chilenos de los 70 (IRT Antú, Arica); cierre de transmisiones; Cindy Sherman (*Untitled Film Stills*); Cildo Meireles (*Babel*); tu corto «Señales de Radio».
- **Riesgo:** lo retro puede volverse disfraz. El 3D (Three.js) pesa y debe cargarse después de la primera imagen.

### D2 · Pliego (papel por capas)

El sitio como archivo de papel: hojas que se despliegan por sus pliegues, fotos montadas con bisagras y papel mantequilla, sellos y un sobre. El CV es tu idea del corte en la página: cada trabajo es una hoja que sale del corte y vuelve a guardarse.

- **Tipografía:** Libre Caslon Display/Text (Impallari Type) + Courier Prime.
- **Color:** washi, sumi, óxido (única tinta), kraft, azul aeropostal.
- **Referencias:** Lira Popular; Eugenio Dittborn (*Pinturas Aeropostales*); Cildo Meireles (*Inserções em circuitos ideológicos*); papel japonés.
- **Riesgo:** puede caer en «scrapbook». Se controla con poca textura, mucha grilla y una sola tinta. Es la más lejana al sitio actual y la más legible en móvil.

### D3 · Cuarto rojo (salas de color)

La página como secuencia de salas teñidas por el color de tus series: rojo (Diablos Rojos), salitre (Humberstone, Alto Hospicio), negro (cine). Niebla entre salas, carga como luz de seguridad de cuarto oscuro, CV como créditos finales, el ojo y la lágrima como firma.

- **Tipografía:** Bodoni Moda (cursiva negra) + Schibsted Grotesk.
- **Color:** rojo sala, antorcha, negro, hueso, salitre, óxido.
- **Referencias:** Cildo Meireles (*Desvio para o vermelho*); Zdzisław Beksiński; Cindy Sherman; el cuarto oscuro.
- **Riesgo:** es la más cercana a lo que hay hoy; si el color no se empuja con fuerza, vuelve a parecer «portafolio oscuro».

Las direcciones se pueden mezclar (por ejemplo, el televisor de D1 como portada con el CV de papel de D2), pero conviene elegir **una** como sistema base: tipografía, color y tono.

## Siguiente paso

Elegir una dirección (o una base + elementos de otra) comentando directamente en Figma. Con eso se escribe el diseño definitivo de la portada y recién después se toca el código en esta rama.

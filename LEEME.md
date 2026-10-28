# Benjamín Bravo — Portafolio V9

## Instalación en Visual Studio Code

1. Guarda una copia de tu proyecto actual.
2. Extrae el ZIP.
3. Copia **index.html**, **style.css** y **script.js** a la carpeta donde trabajas.
4. Conserva todas las fotografías originales en sus ubicaciones y con sus nombres existentes. El ZIP contiene **solo código**, no fotos.
5. Para verlo, abre el proyecto con el servidor local de VS Code o con tu método habitual de previsualización.

## Nuevo recorrido fotográfico

El `gallery-runway` ahora tiene estas fases aproximadas, como fracción del trayecto total:

- **0.00–0.32:** la foto central crece mientras las seis laterales escapan por los márgenes a velocidades y direcciones distintas. No se dibujan rollos fílmicos.
- **0.32–0.56:** la imagen protagonista permanece ampliada. Se puede navegar con flechas y mostrar u ocultar los textos con el ojo.
- **0.56–0.69:** título, contador, flechas y ficha técnica se desvanecen; la foto sigue ampliada.
- **0.70–0.96:** la foto se reduce y se reúne con otras cuatro portadas en una hilera de cinco.
- Al continuar, aparece el **índice de colecciones** con su propia hilera visual, botones de filtro y paginación.

Estos puntos se modifican en `updateGalleryScroll()` dentro de `script.js`. Los tiempos exactos dependen del desplazamiento del visitante.

## Índice renovado

- Cinco portadas como máximo y cinco títulos como máximo por página.
- Filtros automáticos según los años presentes en `colecciones`.
- Paginación con controles anterior/siguiente.
- Clic en uno de los cuatro laterales: intercambio con la portada central sin deformación.
- Clic en un título cuya colección no está entre esos laterales: portada anterior sale hacia arriba y aparece la nueva debajo.
- Una vez seleccionada, la portada central hace una pulsación breve. Haz clic en ella para ir **directamente al visor ampliado**, sin repetir el recorrido de acercamiento.
- Clic en un título **ya no abre el visor** automáticamente.
- Desde el visor, `Esc` permite ir al índice de colecciones.

## Tus colecciones

Los datos siguen estando en el arreglo `colecciones`, al principio de `script.js`. Se conservaron todas las entradas, fotografías, nombres, títulos y metadatos de la V8. No hay necesidad de reingresarlos.

## Accesibilidad y adaptabilidad

Se mantienen controles accesibles con teclado, descripciones para lectores de pantalla y el respeto de `prefers-reduced-motion`. En móviles, las fotografías panorámicas muestran los mandos debajo para no tapar la imagen.

## Pendiente de afinar con fotografías originales

- Sincronía visual exacta entre la hilera que aparece al final del recorrido sticky y la hilera del índice que entra al seguir bajando.
- Proporciones y tratamiento de series especialmente verticales.
- Ritmo y dirección artística de los movimientos para tamaños de ventana poco habituales.

No se alteraron las secciones de cine, presentación y contacto.

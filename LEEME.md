# Benjamín Bravo — Portafolio

Sitio estático de fotografía y dirección audiovisual. Funciona en GitHub Pages y con un servidor local, sin compilación ni paquetes de JavaScript.

## Archivos

| Archivo | Qué editar aquí |
| --- | --- |
| `index.html` | Textos, secciones y estructura accesible. |
| `colecciones.js` | Colecciones, orden de fotos y metadatos. Una fotografía por línea. |
| `script.js` | Navegación, filtros, animaciones, menú y comportamiento. |
| `style.css` | Apariencia, distribución y adaptación a pantallas. |
| `PAUTA.md` | Plantilla para solicitar cambios a Codex. |
| `tests/` | Pruebas de regresión en navegador. No se necesitan para publicar el sitio. |

`colecciones.js` se carga antes de `script.js`. Al copiar o publicar el sitio, incluye ambos archivos, el HTML, el CSS y las fotografías.

## Desarrollo local

Abre esta carpeta en Visual Studio Code y usa Live Server, o ejecuta desde la raíz:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

No hacen falta claves, una base de datos ni una instalación de npm. Las fuentes de Google requieren conexión a Internet; el CSS incluye fuentes alternativas.

## Agregar fotografías

1. Copia las fotos a la raíz del proyecto. Respeta mayúsculas, extensión y nombres exactos.
2. Abre `colecciones.js` y busca la colección correspondiente.
3. Añade un objeto dentro de su lista `fotos`, separado del anterior por una coma:

```js
{ archivo: 'mi-foto.jpg', titulo: 'Título de la fotografía' },
```

Puedes añadir `lente`, `apertura`, `velocidad` e `iso` cuando conozcas sus valores. Los datos ausentes se omiten del panel técnico. Usa comillas dobles si un texto incluye un apóstrofo, o escápalo con `\'`.

Para crear una colección, copia una existente, cambia su `id` por uno único y completa `titulo`, `subtitulo`, `anio`, `camara` y sus fotografías. `lugar` es opcional. Cada colección necesita al menos una fotografía; la primera se utiliza como portada. Mantén `anio` como texto, por ejemplo `'2026'`. Los filtros se generan automáticamente y el índice muestra hasta cinco títulos por página.

## Recorrido de la galería

`updateGalleryScroll()` en `script.js` coordina las fases del recorrido:

- Inicio–0,32: la imagen central crece y los laterales salen por los márgenes.
- 0,32–0,56: visor ampliado, flechas y datos técnicos.
- 0,56–0,69: desaparecen los textos y los mandos.
- 0,70–0,96: la foto se reduce y se reúne con otras portadas.

Después aparece el índice con filtros y paginación. Seleccionar un lateral intercambia las portadas; seleccionar un título elige la colección. Pulsar la portada central del índice abre el visor ampliado. Las flechas del teclado cambian de foto y Escape vuelve al índice. El botón del ojo oculta los textos. En dispositivos con ratón, mantenerlo sobre una flecha cambia de foto cada cinco segundos. Con movimiento reducido se omiten las transiciones y ese avance automático.

## Comprobaciones

Después de editar los datos o la lógica:

```sh
node --check colecciones.js
node --check script.js
```

Para ejecutar las pruebas de navegador, necesitas Python 3, Playwright y Chromium. En el entorno de Codex ya están disponibles:

```sh
python3 -m unittest discover -s tests -v
```

En otra máquina puedes instalar las dependencias de pruebas en un entorno virtual:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r tests/requirements.txt
.venv/bin/python -m playwright install chromium
.venv/bin/python -m unittest discover -s tests -v
```

La suite usa Chromium del sistema cuando está disponible; puedes elegirlo con `CHROMIUM_PATH`. Inicia su propio servidor temporal y comprueba recursos, navegación, filtros, interrupción de animaciones, movimiento reducido y accesibilidad del teclado. Las fuentes externas se bloquean en las pruebas para no depender de Internet.

Para cambios visuales, revisa además escritorio, móvil y movimiento reducido. Las pruebas automatizadas no sustituyen la evaluación del encuadre o del ritmo de las animaciones.

## Estado de la limpieza

Se conservaron las ocho colecciones y sus 89 fotografías con el mismo orden y metadatos. Se quitaron capas visuales permanentemente ocultas, reglas CSS sobrescritas, variables sin uso y trabajo de animación innecesario en reposo. Se corrigieron la transición de la foto ampliada, la selección antigua que podía reaparecer al cambiar filtros y varios estados de teclado y movimiento reducido.

Los originales fotográficos permanecen intactos. Las 94 imágenes del repositorio suman aproximadamente 163 MB; crear miniaturas y versiones adaptadas a pantalla es la siguiente mejora de carga con mayor potencial. Requiere definir tamaños y calidad visual, y conservar los originales. La comparación visual de esta limpieza se realizó en Chromium; no se ha validado Safari ni Firefox.

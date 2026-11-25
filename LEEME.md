# Benjamín Bravo — Portafolio

Sitio estático de cine y fotografía. Funciona en GitHub Pages y con un servidor local, sin compilación ni paquetes de JavaScript. El diseño «Revelado» y sus decisiones están en `docs/rediseno/` y en `AGENTS.md`.

## Archivos

| Archivo | Qué editar aquí |
| --- | --- |
| `index.html` | Estructura y textos fijos: tu nombre, el resumen bajo el nombre y el formulario de contacto. |
| `colecciones.js` | Colecciones de fotos, orden y metadatos. Una fotografía por línea. |
| `peliculas.js` | Películas de la sección de cine: título, año, duración, crédito, fotograma y video. |
| `trayectoria.js` | Tu trayectoria (CV): roles con sus colores y una entrada por trabajo. |
| `script.js` | Galería de fotos (recorrido, visor, ojo y lágrima, índice) y utilidades compartidas. |
| `intro.js` | Pantalla de carga, TV (canales, perilla, inclinación) y retrato bloqueado. |
| `liquido.js` | Fondo líquido animado detrás de la galería (WebGL). |
| `secciones.js` | Cine, trayectoria y contacto, con sus transiciones. |
| `cursor.js` | Cursor fósforo. |
| `style.css` | Apariencia, distribución y adaptación a pantallas. |
| `recursos/` | TV, retratos revelados, copia de la carga, carta de ajuste, texturas y fondos. Se generan con `docs/rediseno/recursos/generadores/recursos_sitio.py`. |
| `PAUTA.md` | Plantilla para pedir cambios a un agente. |
| `tests/` | Pruebas en navegador. No se necesitan para publicar el sitio. |

Los datos (`colecciones.js`, `peliculas.js`, `trayectoria.js`) se cargan antes que el resto de los scripts. Al publicar, incluye todos los archivos de la raíz, la carpeta `recursos/` y las fotografías.

## Desarrollo local

Abre esta carpeta en Visual Studio Code y usa Live Server, o ejecuta desde la raíz:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

No hacen falta claves, una base de datos ni una instalación de npm. Las fuentes de Google requieren conexión a Internet; el CSS incluye fuentes alternativas. Para ver la página, ábrela con un servidor (Live Server o el comando anterior) y no como archivo suelto: el formulario de contacto y algunos navegadores lo necesitan.

## Recorrido de la portada

1. **Carga.** Una copia sale de un corte y se revela mientras cargan el TV, el retrato y el primer canal (entre 1,2 y 6 segundos). Después el TV se enciende.
2. **TV y retrato, sección bloqueada** (`updateIntroScroll()` en `intro.js`). Al bajar, la cámara entra a la pantalla (0–0,22), el TV se funde con el retrato (0,20–0,28), sube el nombre (0,28–0,50), aparece el resumen (0,40–0,62), hay una pausa (0,62–0,80) y sube el líquido de revelado (0,80–1).
3. **Galería** (ver abajo), sobre el líquido animado, que se oscurece a medida que se baja.
4. **Cine.** La tinta inunda todo y el fotograma destacado se abre desde una línea.
5. **Trayectoria.** Estática de cambio de canal al cruzar el borde; las filas entran como teletexto.
6. **Contacto.** La sala roja se enciende desde la lámpara.

Con «reducir movimiento» no hay secciones bloqueadas ni rastro de cursor: el TV y el retrato se muestran uno bajo el otro y cada sección aparece en su estado final.

## Editar el resumen bajo tu nombre

Está en `index.html`, dentro de `<p class="resumen">`. Reemplaza el texto entre corchetes por 3 a 5 líneas tuyas.

## Agregar fotografías

1. Copia las fotos a la raíz del proyecto. Respeta mayúsculas, extensión y nombres exactos.
2. Abre `colecciones.js` y busca la colección correspondiente.
3. Añade un objeto dentro de su lista `fotos`, separado del anterior por una coma:

```js
{ archivo: 'mi-foto.jpg', titulo: 'Título de la fotografía' },
```

Puedes añadir `lente`, `apertura`, `velocidad` e `iso` cuando conozcas sus valores. Los datos ausentes se omiten del panel técnico. Usa comillas dobles si un texto incluye un apóstrofo, o escápalo con `\'`.

Para crear una colección, copia una existente, cambia su `id` por uno único y completa `titulo`, `subtitulo`, `anio`, `camara` y sus fotografías. `lugar` es opcional. Cada colección necesita al menos una fotografía; la primera se utiliza como portada. Mantén `anio` como texto, por ejemplo `'2026'`. Los filtros se generan automáticamente y el índice muestra hasta cinco títulos por página.

Los canales del TV son las fotos de la lista `CANALES` en `intro.js`.

## Películas

En `peliculas.js`, una entrada por película. La primera es la destacada (a todo el ancho). Bajo cada video se muestra `anio · duracion · credito`.

```js
{
  id: "senales-de-radio",
  titulo: "Señales de Radio",
  anio: "2026",
  duracion: "14 min",
  credito: "Dirección",
  fotograma: "senales-fotograma.jpg",
  video: "https://vimeo.com/123456789",
},
```

`video` acepta un enlace de YouTube o Vimeo, o un archivo `.mp4`/`.webm` del repositorio. Si queda vacío, el fotograma es solo imagen.

## Trayectoria

En `trayectoria.js`, `roles` define el nombre y el color de cada rol, y `trayectoria` tiene una entrada por trabajo, de la más reciente a la más antigua:

```js
{
  anio: "2026",
  rol: "direccion",
  titulo: "Señales de Radio",
  tipo: "Cortometraje",
  descripcion: "Una línea de sinopsis.",
  imagenes: ["fotograma.jpg"],
  enlaces: [
    { nombre: "Letterboxd", url: "https://letterboxd.com/film/..." },
    { nombre: "TMDB", url: "https://www.themoviedb.org/movie/..." },
  ],
},
```

Un enlace con `url` vacía aparece apagado, para que sepas qué falta completar. Los enlaces que empiezan con `#` llevan a otra sección de la página.

## Formulario de contacto

El formulario envía los mensajes con [FormSubmit](https://formsubmit.co), sin cuenta ni claves. El destino está en `index.html`, en el `action` del formulario (`https://formsubmit.co/benbravod@gmail.com`).

**Activación:** la primera vez que alguien envíe un mensaje desde el sitio publicado, FormSubmit te mandará un correo para activar el formulario. Ábrelo y confirma; desde entonces cada mensaje llega a tu correo. Puedes hacer esa primera prueba tú mismo.

Si el envío falla, la página muestra tu correo para escribir directo y no borra lo escrito. Para usar otro servicio (Formspree, Web3Forms), cambia el `action` y, si hace falta, la función `urlAjax()` en `secciones.js`.

## Recorrido de la galería

`updateGalleryScroll()` en `script.js` coordina las fases del recorrido:

- Inicio–0,32: la imagen central crece y los laterales salen por los márgenes.
- 0,32–0,56: visor ampliado, flechas y datos técnicos.
- 0,56–0,69: desaparecen los textos y los mandos.
- 0,70–0,96: la foto se reduce hacia la portada central del índice real, que entra en la última pantalla del visor.

Las copias laterales flotan en el revelador: se revelan (negro → rojo → color) la primera vez que aparecen y, al pasar el mouse, giran sobre su eje mostrando el reverso de papel. La central es la que salió del líquido.

El índice continúa con filtros y paginación, sin otra banda duplicada. La foto del visor y la portada central se relevan en las mismas coordenadas; al subir se invierte el recorrido. Seleccionar un lateral intercambia las portadas; seleccionar un título elige la colección. Cada colección retoma la última fotografía explorada durante la visita, tanto en el visor como en sus portadas.

Pulsar la portada central del índice abre el visor ampliado. Las flechas del teclado y A/D cambian de foto y Escape vuelve al índice. El botón del ojo cierra el ojo y oculta los textos; las flechas se vuelven pequeñas y transparentes. La lágrima aparece debajo del círculo: dejar el puntero sobre la gota desvanece la interfaz y amplía la foto en 320 ms. Cualquier movimiento del ratón devuelve el ojo cerrado y el tamaño anterior. La ayuda de navegación existe solo para lectores de pantalla.

En pantallas táctiles se alterna el modo tocando la gota, y con teclado mediante Enter o Espacio. Tab, Escape, perder el foco de la ventana o abandonar el visor restauran la interfaz. En dispositivos con ratón, mantenerlo sobre una flecha cambia de foto cada cinco segundos. Con movimiento reducido se omiten las transiciones y ese avance automático.

## Comprobaciones

Después de editar los datos o la lógica:

```sh
for f in colecciones peliculas trayectoria script intro liquido secciones cursor; do node --check $f.js; done
```

Para ejecutar las pruebas de navegador necesitas Python 3, Playwright y Chromium. En otra máquina puedes instalarlas en un entorno virtual:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r tests/requirements.txt
.venv/bin/python -m playwright install chromium
.venv/bin/python -m unittest discover -s tests -v
```

La suite usa el Chromium indicado en `CHROMIUM_PATH` o el del sistema. Levanta su propio servidor temporal, espera el fin de la pantalla de carga y comprueba recursos, carga, TV, retrato, líquido, galería, cine, trayectoria, contacto (con FormSubmit simulado), cursor, movimiento reducido y accesibilidad del teclado. Las peticiones externas se bloquean para no depender de Internet.

Para cambios visuales, revisa además escritorio, móvil y movimiento reducido. Las pruebas no sustituyen la evaluación del encuadre o del ritmo de las animaciones.

## Pendientes conocidos

- Las 94 fotos originales suman unos 163 MB y se cargan a tamaño completo. Crear miniaturas y versiones para pantalla es la mejora de carga con mayor efecto.
- Faltan el resumen, los datos y videos de las películas, el CV real y los enlaces. Mientras tanto se ven textos entre corchetes y fotos de muestra.
- La comprobación visual se hizo en Chromium; falta revisar Safari y Firefox.

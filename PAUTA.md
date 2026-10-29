# Cómo pedir cambios a Codex

Describe lo que debe experimentar una persona al usar el sitio. No necesitas indicar funciones ni líneas de código. Para un ajuste pequeño basta con señalar dónde está y cómo debería quedar; para cambios de comportamiento, usa esta plantilla.

## Plantilla para copiar

```text
Objetivo:
[Qué quiero mejorar y para qué. Un objetivo principal por tarea.]

Ubicación:
[Sección, botón o etapa del recorrido.]

Cómo reproducir el estado actual:
1. [...]
2. [...]
Actual: [...]
Esperado: [...]

Debe conservarse:
[Diseño, textos, fotos, orden, encuadres o comportamientos específicos.]

Se puede cambiar:
[Elementos sobre los que Codex tiene libertad.]

Dispositivos:
[Escritorio / móvil / ambos. Navegador y tamaño, si el fallo depende de ellos.]

Referencias y archivos:
[Capturas, enlaces, nombres de fotos o fragmentos de la conversación anterior.]

Prioridad y límites:
[Qué importa más: aspecto, velocidad, accesibilidad, etc.
Dependencias permitidas, contenido que no se debe eliminar y otras restricciones.]

Lo daré por terminado cuando:
- [Resultado observable y comprobable.]
- [Otro criterio, si hace falta.]

Entrega:
Implementa, prueba y resume qué cambió, cómo se comprobó y qué quedó pendiente.
```

No necesitas completar campos que no aporten información. Distingue lo obligatorio de las preferencias. Si tienes varios objetivos independientes, enuméralos por prioridad; indica cuáles dependen de otros.

## Ejemplo

```text
Objetivo: que cambiar de foto sea cómodo en móvil.
Ubicación: visor ampliado de Fotografía.
Actual: al tocar la flecha el control tapa parte de la imagen.
Esperado: los controles deben quedar debajo de las fotos horizontales.
Conservar: orden de fotos, textos, vista de escritorio y posibilidad de ocultar datos.
Se puede cambiar: espacio y posición de controles en móvil.
Dispositivos: móvil vertical y horizontal; comprobar también escritorio.
Límites: mantener el sitio estático y no añadir librerías.
Terminado cuando: las dos flechas se pueden tocar sin cubrir la foto,
no aparece desplazamiento horizontal y funciona con movimiento reducido.
Entrega: implementa el cambio y explica las comprobaciones realizadas.
```

## Acuerdos útiles para este proyecto

- **Contenido:** para añadir fotos, indica la colección, los archivos, su orden y los metadatos conocidos. Evita inventar datos técnicos; usa `colecciones.js` para ediciones manuales.
- **Diseño:** señala qué parte debe cambiar y qué elementos actuales sirven de referencia. Si falta un detalle menor, puedes escribir «decide tú manteniendo el estilo actual».
- **Animaciones:** describe inicio, transición y final. Por ejemplo: «al ampliar», «durante la pausa» y «al llegar al índice». Indica qué debería ocurrir en móvil y con movimiento reducido.
- **Fallos:** incluye pasos para reproducirlos y qué ocurrió. Una captura ayuda con apariencia; una grabación ayuda con movimiento.
- **Alcance:** por defecto, conservar el contenido y el diseño que no se mencionen. Si buscas una exploración o un rediseño, dilo expresamente.
- **Decisiones:** autoriza resolver detalles reversibles durante la implementación. Reserva las consultas para decisiones que cambien el objetivo, eliminen contenido o requieran accesos o servicios nuevos.
- **Publicación:** distingue «dejar los cambios en el repositorio» de «publicar en GitHub Pages». Pide explícitamente la publicación cuando la necesites.

Codex puede trabajar con este repositorio y los archivos que compartas aquí. Para recuperar decisiones de la otra conversación de ChatGPT, pega un resumen o los fragmentos relevantes: no se puede asumir acceso automático a ese historial.

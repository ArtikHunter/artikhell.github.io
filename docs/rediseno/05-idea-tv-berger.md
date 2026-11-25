# Idea de Benjamín: la entrada por el TV (en estudio)

Propuesta de Benjamín (25-11-2026). Reemplazará la intro actual (TV → retrato) cuando el modelo, el video y el audio estén listos. Es un proyecto de meses.

## Recorrido

1. Al entrar solo se ve un TV muy pequeño en la oscuridad. Su pantalla brilla tan fuerte que no se distingue qué muestra, y de él sale música.
2. Al bajar con la rueda, el TV se acerca hasta ocupar toda la ventana.
3. Aparece un rótulo con su nombre, con letra de título de serie antigua.
4. Se reproduce un video de Benjamín parodiando a John Berger: saluda a quien visita, cuenta quién es y qué hace. Mientras dura, el scroll queda bloqueado.
5. Al terminar se desbloquea la rueda. Al seguir bajando, la voz se filtra hasta volverse ininteligible y la música toma el primer plano durante toda la navegación.

## Prioridades de peso

- **Computador:** puede ser pesado y tardar en cargar. Calidad ante todo.
- **Celular (la visita más común):** versión lo más liviana posible: imágenes en vez de 3D, video comprimido y menos efectos.

## Restricciones técnicas

- **Sonido:** los navegadores no dejan sonar audio hasta que la persona hace clic o toca la pantalla, y girar la rueda no cuenta. La música no puede empezar sola; hace falta un primer clic o toque, que debe resolverse sin instrucciones escritas (por ejemplo, el TV como lo único clicable, con el cursor cambiando sobre él).
- **Filtrar la voz:** requiere que el video y el audio se sirvan desde el propio sitio o desde un servidor que lo permita (CORS). Un video de YouTube o Vimeo no se puede filtrar. Conviene entregar la voz y la música como pistas separadas.
- **Archivos:** GitHub Pages no acepta archivos de más de 100 MB.
- **Bloquear el scroll:** debe tener una salida (Escape, o desbloqueo tras unos segundos), y en una segunda visita conviene saltarse el bloqueo. Con «reducir movimiento» no se bloquea ni se hace zoom.

## Plan

Modelo en Blender → texturas (2D pintadas, estilo Arcane / Spider-Verse) → iluminación → decidir el formato web → video y audio → integración. Lo de Blender se trabaja en un proyecto aparte de Claude.

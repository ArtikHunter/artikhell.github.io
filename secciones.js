"use strict";
/* ============================================================
   SECCIONES: cine, trayectoria y contacto.
   ============================================================ */

/* ---------------- Cine ---------------- */
const contenedorCine = $("#cine-peliculas");

// Devuelve la dirección del reproductor incrustado (YouTube o Vimeo), o null.
function urlIncrustada(url) {
  if (!url) return null;
  let enlace;
  try {
    enlace = new URL(url);
  } catch {
    return null;
  }
  const sitio = enlace.hostname.replace(/^www\./, "");
  if (sitio === "youtu.be") {
    const id = enlace.pathname.slice(1);
    return id ? `https://www.youtube-nocookie.com/embed/${id}?autoplay=1` : null;
  }
  if (sitio === "youtube.com" || sitio === "m.youtube.com") {
    const id = enlace.searchParams.get("v") || enlace.pathname.split("/").filter(Boolean).pop();
    return id ? `https://www.youtube-nocookie.com/embed/${id}?autoplay=1` : null;
  }
  if (sitio === "vimeo.com") {
    const id = enlace.pathname.split("/").filter(Boolean)[0];
    return /^\d+$/.test(id || "") ? `https://player.vimeo.com/video/${id}?autoplay=1` : null;
  }
  return null;
}

const esArchivoDeVideo = (url) => /\.(mp4|webm|mov)(\?.*)?$/i.test(url || "");

function reproducir(marco, pelicula) {
  const incrustada = urlIncrustada(pelicula.video);
  let reproductor;
  if (incrustada) {
    reproductor = document.createElement("iframe");
    reproductor.src = incrustada;
    reproductor.title = pelicula.titulo;
    reproductor.allow = "autoplay; fullscreen; picture-in-picture";
    reproductor.allowFullscreen = true;
  } else {
    reproductor = document.createElement("video");
    reproductor.src = pelicula.video;
    reproductor.controls = true;
    reproductor.autoplay = true;
    reproductor.playsInline = true;
  }
  marco.classList.add("reproduciendo");
  marco.replaceChildren(reproductor);
}

function renderPeliculas() {
  if (!contenedorCine) return;
  contenedorCine.replaceChildren();
  peliculas.forEach((pelicula, indice) => {
    const articulo = document.createElement("article");
    articulo.className = indice === 0 ? "pelicula pelicula-destacada" : "pelicula";
    const marco = document.createElement("div");
    marco.className = "pelicula-marco";
    const fotograma = document.createElement("img");
    fotograma.src = pelicula.fotograma;
    fotograma.alt = `Fotograma de ${pelicula.titulo}`;
    fotograma.loading = "lazy";
    fotograma.decoding = "async";
    marco.append(fotograma);
    const titulo = document.createElement("h3");
    titulo.className = "pelicula-titulo";
    titulo.textContent = pelicula.titulo;
    if (urlIncrustada(pelicula.video) || esArchivoDeVideo(pelicula.video)) {
      const ver = document.createElement("button");
      ver.type = "button";
      ver.className = "pelicula-ver";
      ver.dataset.cursor = "video";
      ver.setAttribute("aria-label", `Ver ${pelicula.titulo}`);
      ver.addEventListener("click", () => reproducir(marco, pelicula));
      marco.append(ver);
    }
    // En la destacada el título es la cartela sobre el fotograma.
    if (indice === 0) marco.append(titulo);
    const datos = document.createElement("p");
    datos.className = "pelicula-datos";
    datos.textContent = [pelicula.anio, pelicula.duracion, pelicula.credito]
      .filter(Boolean)
      .join(" · ");
    articulo.append(marco);
    if (indice !== 0) articulo.append(titulo);
    articulo.append(datos);
    contenedorCine.append(articulo);
  });
  scheduleScroll();
}

// El fotograma destacado se abre desde una línea, como un proyector, al acercarse al centro.
function updateCine() {
  const destacada = $(".pelicula-destacada");
  const marco = destacada?.querySelector(".pelicula-marco");
  if (!marco) return;
  const posicion = marco.getBoundingClientRect().top / innerHeight;
  const apertura = reduceMotion.matches ? 1 : smoothstep(0.92, 0.38, posicion);
  destacada.style.setProperty("--apertura", String(+apertura.toFixed(4)));
}

renderPeliculas();
enCadaScroll.push(updateCine);

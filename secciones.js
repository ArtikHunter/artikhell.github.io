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

/* ---------------- Trayectoria ---------------- */
const filtrosTrayectoria = $("#trayectoria-filtros");
const guiaTrayectoria = $("#trayectoria-guia");
let rolActivo = "todo";

function crearEnlace({ nombre, url }) {
  const enlace = document.createElement("a");
  enlace.className = "enlace";
  const externo = /^https?:/i.test(url || "");
  enlace.textContent = `${nombre} ${externo ? "↗" : "→"}`;
  if (!url) {
    // Falta la dirección: queda visible pero apagado, para saber qué completar.
    enlace.setAttribute("aria-disabled", "true");
    enlace.title = "Falta el enlace";
    return enlace;
  }
  enlace.href = url;
  if (externo) {
    enlace.target = "_blank";
    enlace.rel = "noopener";
  }
  return enlace;
}

function renderFiltros() {
  if (!filtrosTrayectoria) return;
  filtrosTrayectoria.replaceChildren();
  [["todo", { nombre: "Todo" }], ...Object.entries(roles)].forEach(([id, rol]) => {
    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "filtro";
    boton.dataset.rol = id;
    boton.setAttribute("aria-pressed", String(id === rolActivo));
    if (rol.color) {
      const muestra = document.createElement("i");
      muestra.style.setProperty("--color", rol.color);
      muestra.setAttribute("aria-hidden", "true");
      boton.append(muestra);
    }
    boton.append(rol.nombre);
    boton.addEventListener("click", () => filtrarTrayectoria(id));
    filtrosTrayectoria.append(boton);
  });
}

function filtrarTrayectoria(id) {
  rolActivo = id;
  $$(".filtro", filtrosTrayectoria).forEach((boton) =>
    boton.setAttribute("aria-pressed", String(boton.dataset.rol === id)),
  );
  $$(".entrada", guiaTrayectoria).forEach((entrada) => {
    entrada.hidden = id !== "todo" && entrada.dataset.rol !== id;
  });
}

function alternarFila(fila) {
  const abierta = fila.getAttribute("aria-expanded") !== "true";
  fila.setAttribute("aria-expanded", String(abierta));
  $(".fila-signo", fila).textContent = abierta ? "−" : "+";
  document.getElementById(fila.getAttribute("aria-controls")).hidden = !abierta;
}

function renderTrayectoria() {
  if (!guiaTrayectoria) return;
  renderFiltros();
  guiaTrayectoria.replaceChildren();
  trayectoria.forEach((trabajo, indice) => {
    const rol = roles[trabajo.rol] || { nombre: trabajo.rol, color: "#8c8278" };
    const entrada = document.createElement("li");
    entrada.className = "entrada";
    entrada.dataset.rol = trabajo.rol;
    entrada.style.setProperty("--i", String(indice));
    const fila = document.createElement("button");
    fila.type = "button";
    fila.className = "fila";
    fila.setAttribute("aria-expanded", "false");
    fila.setAttribute("aria-controls", `detalle-${indice}`);
    fila.innerHTML =
      '<span class="fila-anio"></span><span class="fila-rol"></span>' +
      '<span class="fila-titulo"></span><span class="fila-tipo"></span>' +
      '<span class="fila-signo" aria-hidden="true">+</span>';
    $(".fila-anio", fila).textContent = trabajo.anio;
    $(".fila-rol", fila).textContent = rol.nombre;
    $(".fila-rol", fila).style.setProperty("--color", rol.color);
    $(".fila-titulo", fila).textContent = trabajo.titulo;
    $(".fila-tipo", fila).textContent = trabajo.tipo || "";
    fila.addEventListener("click", () => alternarFila(fila));
    const detalle = document.createElement("div");
    detalle.className = "detalle";
    detalle.id = `detalle-${indice}`;
    detalle.hidden = true;
    const imagenes = document.createElement("div");
    imagenes.className = "detalle-imagenes";
    (trabajo.imagenes || []).forEach((archivo) => {
      const img = document.createElement("img");
      img.src = archivo;
      img.alt = "";
      img.loading = "lazy";
      img.decoding = "async";
      imagenes.append(img);
    });
    const texto = document.createElement("div");
    texto.className = "detalle-texto";
    const descripcion = document.createElement("p");
    descripcion.textContent = trabajo.descripcion || "";
    const enlaces = document.createElement("div");
    enlaces.className = "enlaces";
    (trabajo.enlaces || []).forEach((dato) => enlaces.append(crearEnlace(dato)));
    texto.append(descripcion, enlaces);
    detalle.append(imagenes, texto);
    entrada.append(fila, detalle);
    guiaTrayectoria.append(entrada);
  });
  filtrarTrayectoria(rolActivo);
  observarTeletexto();
}

// Las filas entran como teletexto la primera vez que aparecen.
let observadorTeletexto = null;
function observarTeletexto() {
  observadorTeletexto?.disconnect();
  if (reduceMotion.matches || !("IntersectionObserver" in window)) {
    $$(".entrada", guiaTrayectoria).forEach((entrada) => entrada.classList.add("visible"));
    return;
  }
  observadorTeletexto = new IntersectionObserver(
    (entradas) =>
      entradas.forEach((registro) => {
        if (!registro.isIntersecting) return;
        registro.target.classList.add("visible");
        observadorTeletexto.unobserve(registro.target);
      }),
    { threshold: 0.2 },
  );
  $$(".entrada", guiaTrayectoria).forEach((entrada) => observadorTeletexto.observe(entrada));
}

// Cambio de canal: estática de TV mientras el borde de la sección cruza la pantalla.
const capaEstatica = $(".estatica");
const lienzoEstatica = $(".estatica canvas");
const seccionTrayectoria = $("#trayectoria");
let estaticaSeccionFrame = 0;

function dibujarEstaticaSeccion() {
  estaticaSeccionFrame = 0;
  const ctx = lienzoEstatica?.getContext("2d");
  if (!ctx || Number(capaEstatica.style.opacity || 0) < 0.01 || document.hidden) return;
  const datos = ctx.createImageData(lienzoEstatica.width, lienzoEstatica.height);
  for (let i = 0; i < datos.data.length; i += 4) {
    const v = Math.random() * 255;
    datos.data[i] = datos.data[i + 1] = datos.data[i + 2] = v;
    datos.data[i + 3] = 255;
  }
  ctx.putImageData(datos, 0, 0);
  estaticaSeccionFrame = requestAnimationFrame(dibujarEstaticaSeccion);
}

function updateEstatica() {
  if (!capaEstatica || !seccionTrayectoria) return;
  const borde = seccionTrayectoria.getBoundingClientRect().top / innerHeight;
  const cerca = clamp(1 - Math.abs(borde - 0.5) / 0.16, 0, 1);
  const opacidad = reduceMotion.matches ? 0 : 0.55 * smoothstep(0, 1, cerca);
  capaEstatica.style.opacity = String(+opacidad.toFixed(3));
  if (opacidad >= 0.01 && !estaticaSeccionFrame)
    estaticaSeccionFrame = requestAnimationFrame(dibujarEstaticaSeccion);
}

renderTrayectoria();
enCadaScroll.push(updateEstatica);

/* ---------------- Contacto ---------------- */
const seccionContacto = $("#contacto");
const formularioContacto = $(".contacto-form");
const estadoContacto = $(".contacto-estado");
const botonEnviar = $(".contacto-enviar");

// FormSubmit recibe envíos con JavaScript en /ajax/<correo>; el formulario sin JS usa la ruta normal.
function urlAjax(accion) {
  const destino = new URL(accion);
  return `${destino.origin}/ajax${destino.pathname}`;
}

function correoDestino() {
  return decodeURIComponent(new URL(formularioContacto.action).pathname.slice(1));
}

function mostrarEstado(texto) {
  estadoContacto.replaceChildren(texto);
}

function mostrarErrorContacto() {
  const enlace = document.createElement("a");
  enlace.href = `mailto:${correoDestino()}`;
  enlace.textContent = correoDestino();
  estadoContacto.replaceChildren("No se pudo enviar. Escríbeme directo a ", enlace, ".");
}

formularioContacto?.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!formularioContacto.checkValidity()) {
    formularioContacto.reportValidity();
    return;
  }
  const datos = Object.fromEntries(new FormData(formularioContacto));
  const trampa = datos._honey;
  delete datos._honey;
  if (trampa) {
    // Un robot llenó el campo oculto: se le muestra éxito sin enviar nada.
    formularioContacto.reset();
    mostrarEstado("Mensaje enviado. Te respondo pronto.");
    return;
  }
  botonEnviar.disabled = true;
  mostrarEstado("Enviando…");
  try {
    const respuesta = await fetch(urlAjax(formularioContacto.action), {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(datos),
    });
    const resultado = await respuesta.json().catch(() => ({}));
    if (!respuesta.ok || String(resultado.success) !== "true") throw new Error("envío rechazado");
    formularioContacto.reset();
    formularioContacto.classList.remove("enviado");
    void formularioContacto.offsetWidth;
    formularioContacto.classList.add("enviado");
    mostrarEstado("Mensaje enviado. Te respondo pronto.");
  } catch {
    mostrarErrorContacto();
  } finally {
    botonEnviar.disabled = false;
  }
});

// Se enciende la luz de seguridad: la sala roja aparece desde la lámpara.
function updateContacto() {
  if (!seccionContacto) return;
  const posicion = seccionContacto.getBoundingClientRect().top / innerHeight;
  const luz = reduceMotion.matches ? 1 : smoothstep(0.95, 0.3, posicion);
  seccionContacto.style.setProperty("--luz", String(+luz.toFixed(4)));
  if (luz > 0.02) seccionContacto.classList.add("encendida");
}

enCadaScroll.push(updateContacto);
scheduleScroll();

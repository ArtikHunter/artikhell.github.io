"use strict";
/* ============================================================
   INTRO: pantalla de carga y TV.
   La carga espera el TV, el retrato y el primer canal (entre
   CARGA_MIN y CARGA_MAX) y luego enciende el TV.
   ============================================================ */

const raiz = document.documentElement;
const carga = $(".carga");
const tv = $(".tv");
const tvCanal = $(".tv-canal");
const tvEstatica = $(".tv-estatica");
const tvPerilla = $(".tv-perilla");
const CARGA_MIN = 1200;
const CARGA_MAX = 6000;

raiz.classList.add("cargando");

function esperarImagen(img) {
  return new Promise((resolve) => {
    if (!img || (img.complete && img.currentSrc !== "")) return resolve();
    img.addEventListener("load", resolve, { once: true });
    img.addEventListener("error", resolve, { once: true });
  });
}

function ponerCarga(valor) {
  carga?.style.setProperty("--carga", clamp(valor, 0, 1).toFixed(3));
}

const inicioCarga = performance.now();
const relojCarga = setInterval(() => {
  const segundos = Math.floor((performance.now() - inicioCarga) / 1000);
  const reloj = $(".carga-reloj");
  if (reloj) reloj.textContent = `00:${pad(segundos)}`;
}, 250);

const cargaTerminada = new Promise((resolve) => {
  const criticas = [$(".tv-cuerpo"), $(".retrato-foto img"), tvCanal];
  let listas = 0;
  const esperas = criticas.map((img) =>
    esperarImagen(img).then(() => ponerCarga(++listas / criticas.length)),
  );
  const tope = new Promise((r) => setTimeout(r, CARGA_MAX));
  const minimo = new Promise((r) =>
    setTimeout(r, reduceMotion.matches ? 0 : CARGA_MIN),
  );
  Promise.race([Promise.all(esperas), tope])
    .then(() => minimo)
    .then(resolve);
});

const CARGA_SALIDA = 700;
cargaTerminada.then(() => {
  clearInterval(relojCarga);
  ponerCarga(1);
  // Se apaga la luz: la capa se desvanece sin capturar el puntero y el TV se enciende.
  raiz.classList.add("saliendo");
  tv?.classList.add("encendido");
  setTimeout(
    () => {
      raiz.classList.remove("cargando", "saliendo");
      raiz.classList.add("listo");
      programarCanal();
      scheduleScroll();
    },
    reduceMotion.matches ? 0 : CARGA_SALIDA,
  );
});

/* ---------------- Canales ---------------- */
const CANALES = [
  "DR-1.jpg",
  "CFC-20.jpg",
  "AH-1.jpg",
  "VENT-1.jpg",
  "recursos/carta-ajuste.png",
  "HM-10.jpg",
];
const CANAL_CADA = 5000;
const ESTATICA_DURA = 280;
let canalActual = 0;
let canalTimer = 0;
let estaticaFrame = 0;

function dibujarEstatica() {
  const ctx = tvEstatica?.getContext("2d");
  if (!ctx) return;
  const { width, height } = tvEstatica;
  const datos = ctx.createImageData(width, height);
  for (let i = 0; i < datos.data.length; i += 4) {
    const v = Math.random() * 255;
    datos.data[i] = datos.data[i + 1] = datos.data[i + 2] = v;
    datos.data[i + 3] = 255;
  }
  ctx.putImageData(datos, 0, 0);
}

function mostrarEstatica(duracion) {
  if (!tvEstatica) return;
  cancelAnimationFrame(estaticaFrame);
  const fin = performance.now() + duracion;
  tvEstatica.classList.add("activa");
  const cuadro = (ahora) => {
    dibujarEstatica();
    if (ahora < fin) estaticaFrame = requestAnimationFrame(cuadro);
    else tvEstatica.classList.remove("activa");
  };
  estaticaFrame = requestAnimationFrame(cuadro);
}

function cambiarCanal(paso = 1) {
  canalActual = (canalActual + paso + CANALES.length) % CANALES.length;
  const nuevo = CANALES[canalActual];
  if (reduceMotion.matches) {
    tvCanal.src = nuevo;
  } else {
    mostrarEstatica(ESTATICA_DURA);
    setTimeout(() => {
      tvCanal.src = nuevo;
    }, ESTATICA_DURA / 2);
  }
  programarCanal();
}

function programarCanal() {
  clearTimeout(canalTimer);
  if (reduceMotion.matches) return;
  canalTimer = setTimeout(() => {
    // Solo cambia de canal mientras el TV está a la vista.
    if (!document.hidden && (typeof introProgress === "undefined" || introProgress < 0.2))
      cambiarCanal(1);
    else programarCanal();
  }, CANAL_CADA);
}

tvPerilla?.addEventListener("click", () => cambiarCanal(1));
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) programarCanal();
});

/* ---------------- Inclinación con el mouse ---------------- */
const inclinacion = { x: 0, y: 0, objetivoX: 0, objetivoY: 0, frame: 0 };
const INCLINACION_MAX = 6;

function animarInclinacion() {
  inclinacion.x += (inclinacion.objetivoX - inclinacion.x) * 0.08;
  inclinacion.y += (inclinacion.objetivoY - inclinacion.y) * 0.08;
  tv.style.setProperty("--rx", `${inclinacion.x.toFixed(2)}deg`);
  tv.style.setProperty("--ry", `${inclinacion.y.toFixed(2)}deg`);
  const pendiente =
    Math.abs(inclinacion.objetivoX - inclinacion.x) > 0.01 ||
    Math.abs(inclinacion.objetivoY - inclinacion.y) > 0.01;
  inclinacion.frame = pendiente ? requestAnimationFrame(animarInclinacion) : 0;
}

document.addEventListener(
  "pointermove",
  (event) => {
    if (!tv || event.pointerType !== "mouse" || reduceMotion.matches) return;
    if (typeof introProgress !== "undefined" && introProgress > 0.25) return;
    inclinacion.objetivoY = ((event.clientX / innerWidth) - 0.5) * 2 * INCLINACION_MAX;
    inclinacion.objetivoX = -((event.clientY / innerHeight) - 0.5) * 2 * INCLINACION_MAX;
    if (!inclinacion.frame) inclinacion.frame = requestAnimationFrame(animarInclinacion);
  },
  { passive: true },
);

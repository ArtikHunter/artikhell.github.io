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

/* ============================================================
   RETRATO BLOQUEADO
   Una sola escena fija mientras se recorre la sección:
   zoom a la pantalla → fundido al retrato → sube el nombre →
   aparece el resumen → pausa → sube el líquido de revelado.
   ============================================================ */
const intro = $(".intro");
const escena = $(".intro-escena");
const tvZoom = $(".tv-zoom");
const tvCapa = $(".tv-capa");
const tvLineas = $(".tv-lineas");
const tvRetrato = $(".tv-retrato");
const retratoCapa = $(".retrato-capa");
const retratoTexto = $(".retrato-texto");
const FASES = {
  zoom: [0, 0.22],
  fundido: [0.2, 0.28],
  nombre: [0.28, 0.5],
  resumen: [0.4, 0.62],
  liquido: [0.8, 1],
};
let introProgress = 0;
let olaFrame = 0;

const num = (valor) => String(+valor.toFixed(4));

function fase(nombre, p) {
  const [a, b] = FASES[nombre];
  return smoothstep(a, b, p);
}

// Superficie del líquido: el retrato queda visible solo por encima de la ola.
function recorteLiquido(nivel, tiempo) {
  if (nivel <= 0) return "none";
  const altura = (1 - nivel * 1.08) * 100;
  const puntos = [];
  for (let x = 100; x >= 0; x -= 5) {
    const ola =
      Math.sin(x * 0.075 + tiempo * 1.9) * 1.6 +
      Math.sin(x * 0.16 - tiempo * 1.2) * 0.8;
    puntos.push(`${x}% ${(altura + ola).toFixed(2)}%`);
  }
  return `polygon(0% 0%, 100% 0%, ${puntos.join(", ")})`;
}

function animarOla() {
  const nivel = fase("liquido", introProgress);
  retratoCapa.style.clipPath = recorteLiquido(nivel, performance.now() / 1000);
  olaFrame = nivel > 0 && nivel < 1 && !document.hidden ? requestAnimationFrame(animarOla) : 0;
}

function limpiarIntro() {
  [tvZoom, tvCapa, tvLineas, tvRetrato, retratoCapa, retratoTexto].forEach((el) =>
    el?.removeAttribute("style"),
  );
  ["--zoom", "--fundido", "--nombre", "--resumen", "--liquido"].forEach((v) =>
    escena.style.removeProperty(v),
  );
}

function updateIntroScroll() {
  if (!intro) return;
  const rect = intro.getBoundingClientRect();
  const recorrido = Math.max(1, rect.height - innerHeight);
  introProgress = clamp(-rect.top / recorrido, 0, 1);
  if (reduceMotion.matches) {
    limpiarIntro();
    return;
  }
  const p = introProgress;
  const zoom = fase("zoom", p);
  const fundido = fase("fundido", p);
  const nombre = fase("nombre", p);
  const resumen = fase("resumen", p);
  const liquido = fase("liquido", p);
  escena.style.setProperty("--zoom", num(zoom));
  escena.style.setProperty("--fundido", num(fundido));
  escena.style.setProperty("--nombre", num(nombre));
  escena.style.setProperty("--resumen", num(resumen));
  escena.style.setProperty("--liquido", num(liquido));

  // La cámara entra a la pantalla: escala exponencial con centro en la pantalla.
  const W = tv.offsetWidth;
  const H = tv.offsetHeight;
  const izquierda = innerWidth / 2 - W / 2;
  const arriba = innerHeight / 2 - H * 0.48;
  const pantalla = {
    x: izquierda + W * 0.174545,
    y: arriba + H * 0.366667,
    w: W * 0.450909,
    h: H * 0.408333,
  };
  const escalaFinal = Math.max(innerWidth / pantalla.w, innerHeight / pantalla.h) * 1.06;
  const escala = Math.pow(escalaFinal, zoom);
  const dx = (innerWidth / 2 - (pantalla.x + pantalla.w / 2)) * zoom;
  const dy = (innerHeight / 2 - (pantalla.y + pantalla.h / 2)) * zoom;
  tvZoom.style.transform = zoom > 0 ? `translate(${dx.toFixed(2)}px, ${dy.toFixed(2)}px) scale(${escala.toFixed(4)})` : "";
  tv.style.setProperty("--inclina", (1 - zoom).toFixed(3));
  tvLineas.style.opacity = (1 - zoom).toFixed(3);
  // Estática en la mitad del zoom; luego la pantalla muestra el retrato.
  const ruido = clamp(1 - Math.abs(zoom - 0.5) / 0.22, 0, 1);
  tvEstatica.style.opacity = (ruido * 0.85).toFixed(3);
  if (ruido > 0.02) dibujarEstatica();
  tvRetrato.style.opacity = smoothstep(0.5, 0.78, zoom).toFixed(3);
  tvCapa.style.opacity = (1 - fundido).toFixed(3);
  tvCapa.style.visibility = fundido >= 1 ? "hidden" : "";

  retratoTexto.style.opacity = (1 - smoothstep(0.82, 0.94, p)).toFixed(3);
  retratoCapa.style.clipPath = recorteLiquido(liquido, performance.now() / 1000);
  if (liquido > 0 && liquido < 1 && !olaFrame) olaFrame = requestAnimationFrame(animarOla);
}

enCadaScroll.push(updateIntroScroll);
reduceMotion.addEventListener("change", scheduleScroll);
scheduleScroll();

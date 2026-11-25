"use strict";
/* ============================================================
   CURSOR FÓSFORO
   Una mira fina que deja una línea roja que se apaga lento, como
   la persistencia del fósforo en un tubo. Cambia sobre lo que se
   puede abrir: foto (esquinas de visor), video (▶) y enlace.
   Solo con mouse y sin «reducir movimiento».
   ============================================================ */

const mira = $(".cursor-mira");
const punteroFino = matchMedia("(hover: hover) and (pointer: fine)");
const RASTRO_VIDA = 650;
const puntosRastro = [];
let cursorFrame = 0;
let lienzoRastro = null;
let ctxRastro = null;

mira.innerHTML =
  '<svg class="mira-normal" viewBox="0 0 36 36"><path d="M18 4v10M18 22v10M4 18h10M22 18h10"/><circle cx="18" cy="18" r="2"/></svg>' +
  '<svg class="mira-foto" viewBox="0 0 56 44"><path d="M2 12V2h12M42 2h12v10M54 32v10H42M14 42H2V32"/></svg>' +
  '<svg class="mira-video" viewBox="0 0 44 44"><path d="M15 11 L33 22 L15 33 Z"/></svg>' +
  '<svg class="mira-enlace" viewBox="0 0 44 20"><path d="M2 16h40"/><path class="tenue" d="M2 10h40"/></svg>';

function estadoCursor(objetivo) {
  if (!objetivo?.closest) return "normal";
  if (objetivo.closest("input, textarea, select")) return "texto";
  if (objetivo.closest('[data-cursor="video"]')) return "video";
  if (objetivo.closest(".side-image, .featured, .showcase-card, .detalle-imagenes img")) return "foto";
  if (objetivo.closest('a[href], button, label, [role="button"]')) return "enlace";
  return "normal";
}

function ajustarRastro() {
  if (!lienzoRastro) return;
  const escala = Math.min(devicePixelRatio || 1, 2);
  lienzoRastro.width = Math.round(innerWidth * escala);
  lienzoRastro.height = Math.round(innerHeight * escala);
  ctxRastro.setTransform(escala, 0, 0, escala, 0, 0);
}

function limpiarRastro() {
  puntosRastro.length = 0;
  ctxRastro?.clearRect(0, 0, innerWidth, innerHeight);
}

function activarCursor() {
  const activo = punteroFino.matches && !reduceMotion.matches;
  document.documentElement.classList.toggle("cursor-activo", activo);
  if (activo && !lienzoRastro) {
    lienzoRastro = document.createElement("canvas");
    lienzoRastro.className = "cursor-rastro";
    lienzoRastro.setAttribute("aria-hidden", "true");
    document.body.append(lienzoRastro);
    ctxRastro = lienzoRastro.getContext("2d");
    ajustarRastro();
  }
  if (!activo) {
    mira.classList.remove("is-visible");
    limpiarRastro();
  }
}

function dibujarRastro(ahora) {
  cursorFrame = 0;
  const limite = ahora - RASTRO_VIDA;
  while (puntosRastro.length && puntosRastro[0].t < limite) puntosRastro.shift();
  ctxRastro.clearRect(0, 0, innerWidth, innerHeight);
  ctxRastro.lineCap = "round";
  for (let i = 1; i < puntosRastro.length; i++) {
    // Cortes de barrido: el trazo se interrumpe cada cierto número de tramos.
    if (i % 6 === 5) continue;
    const a = puntosRastro[i - 1];
    const b = puntosRastro[i];
    const vida = clamp(1 - (ahora - b.t) / RASTRO_VIDA, 0, 1);
    ctxRastro.strokeStyle = `rgba(255, 140, 110, ${(vida ** 1.4).toFixed(3)})`;
    ctxRastro.shadowColor = `rgba(255, 92, 60, ${(vida * 0.8).toFixed(3)})`;
    ctxRastro.shadowBlur = 6;
    ctxRastro.lineWidth = 1.2 + 1.8 * vida;
    ctxRastro.beginPath();
    ctxRastro.moveTo(a.x, a.y);
    ctxRastro.lineTo(b.x, b.y);
    ctxRastro.stroke();
  }
  if (puntosRastro.length) cursorFrame = requestAnimationFrame(dibujarRastro);
}

document.addEventListener(
  "pointermove",
  (event) => {
    if (event.pointerType !== "mouse" || !document.documentElement.classList.contains("cursor-activo")) return;
    mira.style.transform = `translate3d(${event.clientX}px, ${event.clientY}px, 0)`;
    mira.classList.add("is-visible");
    puntosRastro.push({ x: event.clientX, y: event.clientY, t: performance.now() });
    if (!cursorFrame) cursorFrame = requestAnimationFrame(dibujarRastro);
  },
  { passive: true },
);
document.addEventListener("pointerover", (event) => {
  if (event.pointerType === "mouse") mira.dataset.estado = estadoCursor(event.target);
});
window.addEventListener("mouseout", (event) => {
  if (!event.relatedTarget) mira.classList.remove("is-visible");
});
addEventListener("resize", ajustarRastro);
punteroFino.addEventListener("change", activarCursor);
reduceMotion.addEventListener("change", activarCursor);
activarCursor();

"use strict";
/* ============================================================
   LÍQUIDO DE REVELADO
   Fondo animado de la galería: papel crema con tinta negra en
   movimiento (WebGL a media resolución). Se oscurece a medida
   que se baja y se inunda de negro antes de la sección de cine.
   Sin WebGL, html.sin-webgl muestra una imagen fija.
   ============================================================ */

const lienzoLiquido = $("#liquido");
const liquido = { tinta: 0.35, objetivo: 0.35, activo: false };

// Cantidad de tinta según el lugar de la página (0 = papel, 1 = negro).
function tintaPara({ intro, galeria, cineTop, alto }) {
  let tinta = 0.35;
  tinta = lerp(tinta, 0.62, smoothstep(0.05, 0.35, galeria));
  tinta = lerp(tinta, 0.82, smoothstep(0.7, 0.96, galeria));
  const llegada = 1 - clamp(cineTop / Math.max(1, alto), 0, 1);
  return lerp(tinta, 1, smoothstep(0, 1, llegada));
}

const SOMBREADOR_VERTICES = `
attribute vec2 p;
void main() { gl_Position = vec4(p, 0.0, 1.0); }`;

const SOMBREADOR_TINTA = `
precision mediump float;
uniform vec2 r;
uniform float t;
uniform float tinta;
float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float ruido(vec2 p) {
  vec2 i = floor(p), f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),
             mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}
float fbm(vec2 p) {
  float v = 0.0, a = 0.5;
  for (int i = 0; i < 4; i++) { v += a * ruido(p); p = p * 2.03 + vec2(17.1, 9.2); a *= 0.5; }
  return v;
}
void main() {
  vec2 uv = gl_FragCoord.xy / r;
  vec2 p = vec2(uv.x * r.x / r.y, uv.y) * 2.4;
  vec2 q = vec2(fbm(p + vec2(0.0, t * 0.035)), fbm(p + vec2(5.2, 1.3) - vec2(t * 0.025, 0.0)));
  float n = fbm(p + 1.8 * q + vec2(t * 0.01, -t * 0.02));
  float d = n + (1.0 - uv.y) * 0.55 - 0.25;
  float umbral = mix(1.25, -0.15, tinta);
  float m = smoothstep(umbral - 0.07, umbral + 0.07, d);
  vec3 crema = vec3(0.937, 0.902, 0.824);
  vec3 negro = vec3(0.043, 0.027, 0.027);
  vec3 oxido = vec3(0.42, 0.16, 0.11);
  vec3 color = mix(crema, negro, m);
  color = mix(color, oxido, (1.0 - abs(m * 2.0 - 1.0)) * 0.55);
  color *= 0.94 + 0.06 * hash(gl_FragCoord.xy + t);
  gl_FragColor = vec4(color, 1.0);
}`;

const gl = lienzoLiquido?.getContext("webgl", {
  alpha: false,
  antialias: false,
  depth: false,
  powerPreference: "low-power",
});
let programaLiquido = null;
let uniformes = {};
let liquidoFrame = 0;
const inicioLiquido = performance.now();

function compilar(tipo, fuente) {
  const sombreador = gl.createShader(tipo);
  gl.shaderSource(sombreador, fuente);
  gl.compileShader(sombreador);
  return gl.getShaderParameter(sombreador, gl.COMPILE_STATUS) ? sombreador : null;
}

function prepararLiquido() {
  if (!gl) return false;
  const vertices = compilar(gl.VERTEX_SHADER, SOMBREADOR_VERTICES);
  const fragmentos = compilar(gl.FRAGMENT_SHADER, SOMBREADOR_TINTA);
  if (!vertices || !fragmentos) return false;
  programaLiquido = gl.createProgram();
  gl.attachShader(programaLiquido, vertices);
  gl.attachShader(programaLiquido, fragmentos);
  gl.linkProgram(programaLiquido);
  if (!gl.getProgramParameter(programaLiquido, gl.LINK_STATUS)) return false;
  gl.useProgram(programaLiquido);
  const buffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  // Un triángulo que cubre toda la pantalla.
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  const atributo = gl.getAttribLocation(programaLiquido, "p");
  gl.enableVertexAttribArray(atributo);
  gl.vertexAttribPointer(atributo, 2, gl.FLOAT, false, 0, 0);
  uniformes = {
    r: gl.getUniformLocation(programaLiquido, "r"),
    t: gl.getUniformLocation(programaLiquido, "t"),
    tinta: gl.getUniformLocation(programaLiquido, "tinta"),
  };
  return true;
}

if (!prepararLiquido()) document.documentElement.classList.add("sin-webgl");

function ajustarLienzo() {
  if (!programaLiquido) return;
  // 40 % de la resolución: la tinta es difusa y así cuesta una sexta parte.
  const ancho = Math.max(2, Math.round(innerWidth * 0.4));
  const alto = Math.max(2, Math.round(innerHeight * 0.4));
  if (lienzoLiquido.width !== ancho || lienzoLiquido.height !== alto) {
    lienzoLiquido.width = ancho;
    lienzoLiquido.height = alto;
    gl.viewport(0, 0, ancho, alto);
  }
}

const LIQUIDO_INTERVALO = 1000 / 30;
let ultimoCuadroLiquido = 0;

function dibujarLiquido(ahora) {
  liquidoFrame = 0;
  if (!programaLiquido) return;
  // La tinta se mueve lento: 30 cuadros por segundo bastan y alivian la GPU.
  if (ahora - ultimoCuadroLiquido < LIQUIDO_INTERVALO - 1 && liquido.activo) {
    liquidoFrame = requestAnimationFrame(dibujarLiquido);
    return;
  }
  ultimoCuadroLiquido = ahora;
  ajustarLienzo();
  const quieto = reduceMotion.matches;
  liquido.tinta = quieto ? liquido.objetivo : lerp(liquido.tinta, liquido.objetivo, 0.08);
  gl.uniform2f(uniformes.r, lienzoLiquido.width, lienzoLiquido.height);
  gl.uniform1f(uniformes.t, quieto ? 12 : (ahora - inicioLiquido) / 1000);
  gl.uniform1f(uniformes.tinta, liquido.tinta);
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  const pendiente = Math.abs(liquido.tinta - liquido.objetivo) > 0.001;
  if (liquido.activo && !document.hidden && (!quieto || pendiente))
    liquidoFrame = requestAnimationFrame(dibujarLiquido);
}

const introLiquido = $("#inicio");

function updateLiquido() {
  // Se mide aquí mismo (no con introProgress) porque este módulo corre antes
  // que intro.js en cada cuadro y leería el valor del cuadro anterior.
  const rectIntro = introLiquido?.getBoundingClientRect();
  const progresoIntro = rectIntro
    ? clamp(-rectIntro.top / Math.max(1, rectIntro.height - innerHeight), 0, 1)
    : 1;
  const cine = $("#cine");
  const cineTop = cine ? cine.getBoundingClientRect().top : Infinity;
  liquido.objetivo = tintaPara({
    intro: progresoIntro,
    galeria: galleryProgress,
    cineTop,
    alto: innerHeight,
  });
  // Visible desde que sube la ola del retrato hasta que el cine lo cubre.
  liquido.activo = progresoIntro > 0.78 && cineTop > 0;
  lienzoLiquido?.classList.toggle("activo", liquido.activo);
  if (liquido.activo && !liquidoFrame) liquidoFrame = requestAnimationFrame(dibujarLiquido);
}

enCadaScroll.push(updateLiquido);
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) scheduleScroll();
});

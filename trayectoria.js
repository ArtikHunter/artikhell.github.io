"use strict";
// Trayectoria (CV). Cada rol tiene un color de la carta de ajuste del TV.
const roles = {
  direccion: { nombre: "Dirección", color: "#d7301f" },
  fotografia: { nombre: "Fotografía", color: "#3fa7b5" },
  camara: { nombre: "Cámara", color: "#b04a8f" },
  gestion: { nombre: "Gestión cultural", color: "#c9b037" },
};

// Una entrada por trabajo, de la más reciente a la más antigua.
// enlaces: [{ nombre, url }]. Si url está vacía, el enlace aparece apagado.
// Todo el contenido es de muestra: reemplázalo por tu CV real.
const trayectoria = [
  {
    anio: "2026",
    rol: "direccion",
    titulo: "Señales de Radio",
    tipo: "Cortometraje",
    descripcion: "[Sinopsis en una línea. Festivales y selecciones, si las hay.]",
    imagenes: ["remake-5.jpg"],
    enlaces: [
      { nombre: "Letterboxd", url: "" },
      { nombre: "TMDB", url: "" },
      { nombre: "Ficha", url: "#cine" },
    ],
  },
  {
    anio: "2026",
    rol: "fotografia",
    titulo: "Juglaría en llamas",
    tipo: "Serie · Diablos Rojos",
    descripcion: "[Contexto de la serie: dónde, cuándo, con quién.]",
    imagenes: ["DR-1.jpg", "DR-4.jpg"],
    enlaces: [{ nombre: "Colección", url: "#fotografia" }],
  },
  {
    anio: "2025",
    rol: "gestion",
    titulo: "Muestra de cortometrajes",
    tipo: "[Lugar]",
    descripcion: "[Qué fue, dónde, con quién; cuántas películas y qué público.]",
    imagenes: ["FECH-1.jpg", "FECH-5.jpg"],
    enlaces: [],
  },
  {
    anio: "2025",
    rol: "direccion",
    titulo: "Olmué",
    tipo: "Cortometraje",
    descripcion: "[Sinopsis en una línea.]",
    imagenes: ["HM-1.jpg"],
    enlaces: [
      { nombre: "Letterboxd", url: "" },
      { nombre: "TMDB", url: "" },
    ],
  },
  {
    anio: "2025",
    rol: "fotografia",
    titulo: "Carnaval Diurno",
    tipo: "Serie · FECH",
    descripcion: "[Contexto de la serie.]",
    imagenes: ["FECH-9.jpg"],
    enlaces: [{ nombre: "Colección", url: "#fotografia" }],
  },
  {
    anio: "20—",
    rol: "camara",
    titulo: "[Otro crédito]",
    tipo: "[Producción]",
    descripcion: "[Descripción del trabajo.]",
    imagenes: [],
    enlaces: [],
  },
];

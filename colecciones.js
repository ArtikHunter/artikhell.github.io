'use strict';

/* ============================================================
   ARCHIVO / DATOS EDITABLES
   Añade una nueva colección copiando un objeto de este arreglo.
   Puedes incluir tantas fotografías como necesites.
   IMPORTANTE: los nombres de archivo deben coincidir exactamente.
   ============================================================ */
const colecciones = [
  {
    id: 'juglaria',
    titulo: 'Juglaría en llamas',
    subtitulo: 'Diablos Rojos',
    lugar: 'Chile',
    anio: '2026',
    camara: 'Canon 80D',
    fotos: [
      { archivo: 'DR-1.jpg', titulo: 'Aprendan del Fuego', lente: '70 mm', apertura: 'f/5', velocidad: '1/50 s', iso: '4000' },
      { archivo: 'DR-2.jpg', titulo: 'Invasores', lente: '55 mm', apertura: 'f/5', velocidad: '1/50 s', iso: '4000' },
      { archivo: 'DR-3.jpg', titulo: 'Atalaya', lente: '250 mm', apertura: 'f/5.6', velocidad: '1/50 s', iso: '4000' },
      { archivo: 'DR-4.jpg', titulo: 'Carne a Baal', lente: '117 mm', apertura: 'f/5', velocidad: '1/50 s', iso: '4000' },
      { archivo: 'DR-5.jpg', titulo: 'La mitad lejana', lente: '109 mm', apertura: 'f/5', velocidad: '1/50 s', iso: '4000' },
      { archivo: 'DR-6.jpg', titulo: 'Barrio Rojo', lente: '157 mm', apertura: 'f/5.6', velocidad: '1/50 s', iso: '4000' },
      { archivo: 'DR-7.jpg', titulo: 'Sonrojar', lente: '135 mm', apertura: 'f/5', velocidad: '1/50 s', iso: '3200' },
      { archivo: 'DR-8.jpg', titulo: 'Tusa', lente: '55 mm', apertura: 'f/5', velocidad: '1/50 s', iso: '4000' },
      { archivo: 'DR-9.jpg', titulo: 'Hoguera', lente: '250 mm', apertura: 'f/5.6', velocidad: '1/50 s', iso: '4000' },
      { archivo: 'DR-10.jpg', titulo: 'Antorchas', lente: '250 mm', apertura: 'f/5.6', velocidad: '1/50 s', iso: '4000' },
      { archivo: 'DR-12.jpg', titulo: 'De vuelta a Chile', lente: '250 mm', apertura: 'f/5.6', velocidad: '1/50 s', iso: '4000' },
      { archivo: 'DR-13.jpg', titulo: 'Leonidas Isabel Díaz Díaz', lente: '113 mm', apertura: 'f/5', velocidad: '1/50 s', iso: '4000' }
    ]
  },
  {
    id: 'Cuteños',
    titulo: 'Costra Cocida',
    subtitulo: 'Cuteños FC',
    lugar: 'Chile',
    anio: '2026',
    camara: 'Canon 80D',
    fotos: [
      { archivo: 'CFC_1.jpg', titulo: 'Dios', lente: '55 mm', apertura: 'f/9', velocidad: '1/200 s', iso: '100' },
      { archivo: 'CFC_2.jpg', titulo: 'Adán', lente: '100 mm', apertura: 'f/9', velocidad: '1/200 s', iso: '100' },
      { archivo: 'CFC_3.jpg', titulo: 'Regar las Palmas', lente: '250 mm', apertura: 'f/9', velocidad: '1/200 s', iso: '100' },
      { archivo: 'CFC_4.jpg', titulo: 'Una misma Pasión', lente: '79 mm', apertura: 'f/9', velocidad: '1/200 s', iso: '100' },
      { archivo: 'CFC_5.jpg', titulo: 'Resoplo del Dragón', lente: '55 mm', apertura: 'f/9', velocidad: '1/200 s', iso: '100' },
      { archivo: 'CFC_6.jpg', titulo: 'Todo Pelota', lente: '55 mm', apertura: 'f/5', velocidad: '1/2000 s', iso: '500' },
      { archivo: 'CFC_7.jpg', titulo: 'Amateur', lente: '105 mm', apertura: 'f/14', velocidad: '1/5 s', iso: '100' },
      { archivo: 'CFC_8.jpg', titulo: 'Escala de Persecución', lente: '84 mm', apertura: 'f/9', velocidad: '1/2000 s', iso: '1000' },
      { archivo: 'CFC_9.jpg', titulo: 'Centro de Gravedad', lente: '135 mm', apertura: 'f/9', velocidad: '1/200 s', iso: '100' },
    ]
  },
  {
    id: 'Hospicio',
    titulo: 'Sales Solubles',
    subtitulo: 'Alto Hospicio 1',
    lugar: 'Chile',
    anio: '2026',
    camara: 'Canon 80D',
    fotos: [
      { archivo: 'AH-1.jpg', titulo: 'Encrespado', lente: '70 mm', apertura: 'f/10', velocidad: '1/250 s', iso: '1600' },
      { archivo: 'AH-2.jpg', titulo: 'Cumple', lente: '135 mm', apertura: 'f/25', velocidad: '1/100 s', iso: '1600' },
      { archivo: 'AH-3.jpg', titulo: 'Parada Doble', lente: '50 mm', apertura: 'f/22', velocidad: '1/125 s', iso: '400' },
      { archivo: 'AH-4.jpg', titulo: 'Pandemia', lente: '135 mm', apertura: 'f/25', velocidad: '1/60 s', iso: '1250' },
      { archivo: 'AH-5.jpg', titulo: 'Despojados', lente: '55 mm', apertura: 'f/22', velocidad: '1/50 s', iso: '1600' },
      { archivo: 'AH-6.jpg', titulo: 'Cocina', lente: '55 mm', apertura: 'f/22', velocidad: '1/50 s', iso: '1600' },
      { archivo: 'AH-7.jpg', titulo: 'Vecinos', lente: '55 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '320' },
      { archivo: 'AH-8.jpg', titulo: 'Aguinaldo', lente: '200 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '200' },
      { archivo: 'AH-9.jpg', titulo: 'Cuarto Piso', lente: '70 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '200' },
      { archivo: 'AH-10.jpg', titulo: 'Regalo de Diciembre 1', lente: '60 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '1600' },
      { archivo: 'AH-11.jpg', titulo: 'Regalo de Diciembre 2', lente: '60 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '1600' },
      { archivo: 'AH-12.jpg', titulo: 'Nuevo Mundo 1', lente: '79 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '320' },
      { archivo: 'AH-20.jpg', titulo: 'Nuevo Mundo 2', lente: '60 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '400' },
      { archivo: 'AH-21.jpg', titulo: ':(', lente: '60 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '400' },
      { archivo: 'AH-13.jpg', titulo: 'Decorado', lente: '113 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '400' },
      { archivo: 'AH-14.jpg', titulo: 'Retornable', lente: '55 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '100' },
      { archivo: 'AH-15.jpg', titulo: 'Bloques', lente: '55 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '160' },
      { archivo: 'AH-16.jpg', titulo: 'Medio Día', lente: '55 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '250' },
      { archivo: 'AH-17.jpg', titulo: 'Secado', lente: '55 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '250' },
      { archivo: 'AH-18.jpg', titulo: 'Peluche', lente: '55 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '100' },
      { archivo: 'AH-19.jpg', titulo: 'Colaciones a la Venta', lente: '100 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '400' },
      { archivo: 'AH-22.jpg', titulo: 'Media Luna', lente: '55 mm', apertura: 'f/18', velocidad: '1/50 s', iso: '160' },
    ]
  },
  {
    id: 'VENT',
    titulo: 'Lluvia Pronosticada',
    subtitulo: 'Nicolás Radic',
    lugar: 'Chile',
    anio: '2026',
    camara: 'Canon 80D',
    fotos: [
      { archivo: 'VENT-1.jpg', titulo: 'Rendija', lente: '40 mm', apertura: 'f/4', velocidad: '1/50 s', iso: '1600' },
      { archivo: 'VENT-2.jpg', titulo: 'Desborde', lente: '24 mm', apertura: 'f/8', velocidad: '2 s', iso: '100' },
      { archivo: 'VENT-3.jpg', titulo: 'Sin Señal', lente: '24 mm', apertura: 'f/4', velocidad: '1/50 s', iso: '1250' },
      { archivo: 'VENT-4.jpg', titulo: 'Invasores', lente: '24 mm', apertura: 'f/4', velocidad: '1/50 s', iso: '1250' },
      { archivo: 'VENT-5.jpg', titulo: 'Invasores', lente: '24 mm', apertura: 'f/4', velocidad: '1/50 s', iso: '1250' },
      { archivo: 'VENT-6.jpg', titulo: 'Invasores', lente: '65 mm', apertura: 'f/4', velocidad: '1/50 s', iso: '1250' },
      { archivo: 'VENT-7.jpg', titulo: 'Invasores', lente: '70 mm', apertura: 'f/4', velocidad: '1/50 s', iso: '1250' },
      { archivo: 'VENT-8.jpg', titulo: 'Invasores', lente: '82 mm', apertura: 'f/4', velocidad: '1/50 s', iso: '1250' },
    ]
  },
    {
    id: 'IQQ',
    titulo: 'Entre el Mar y el Desierto',
    subtitulo: 'Iquique 1',
    lugar: 'Chile',
    anio: '2026',
    camara: 'Canon 80D',
    fotos: [
      { archivo: 'IQQ-1.jpg', titulo: 'Zona Bien Franca', lente: '50 mm', apertura: 'f/5', velocidad: '1/2000 s', iso: '100' },
      { archivo: 'IQQ-2.jpg', titulo: 'El Segundo Infinito', lente: '50 mm', apertura: 'f/1.8', velocidad: '1/8000 s', iso: '100' },
      { archivo: 'IQQ-3.jpg', titulo: 'Sin Señal', lente: '50 mm', apertura: 'f/1.8', velocidad: '1/8000 s', iso: '100' },
      { archivo: 'IQQ-4.jpg', titulo: 'Invasores', lente: '50 mm', apertura: 'f/1.8', velocidad: '1/8000 s', iso: '100' },
    ]
  },
  {
    id: 'HM',
    titulo: 'Título pendiente',
    subtitulo: 'Colección pendiente',
    anio: '2026',
    camara: 'Canon 80D',
    fotos: [
      { archivo: 'HM-1.jpg', titulo: 'Título pendiente', lente: '50 mm', apertura: 'f/6.3', velocidad: '1/50 s', iso: '100' },
      { archivo: 'HM-2.jpg', titulo: 'Título pendiente', lente: '50 mm', apertura: 'f/6.3', velocidad: '1/50 s', iso: '100' },
      { archivo: 'HM-3.jpg', titulo: 'Título pendiente', lente: '50 mm', apertura: 'f/2.8', velocidad: '1/50 s', iso: '100' },
      { archivo: 'HM-4.jpg', titulo: 'Título pendiente', lente: '50 mm', apertura: 'f/9', velocidad: '1/50 s', iso: '100' },
      { archivo: 'HM-5.jpg', titulo: 'Título pendiente', lente: '50 mm', apertura: 'f/9', velocidad: '1/50 s', iso: '100' },
      { archivo: 'HM-6.jpg', titulo: 'Título pendiente', lente: '50 mm', apertura: 'f/2.5', velocidad: '1/50 s', iso: '100' },
      { archivo: 'HM-7.jpg', titulo: 'Título pendiente', lente: '50 mm', apertura: 'f/2.2', velocidad: '1/50 s', iso: '100' },
      { archivo: 'HM-8.jpg', titulo: 'Título pendiente', lente: '24 mm', apertura: 'f/4', velocidad: '1/50 s', iso: '3200' },
      { archivo: 'HM-9.jpg', titulo: 'Título pendiente', lente: '24 mm', apertura: 'f/4', velocidad: '1/50 s', iso: '3200' },
      { archivo: 'HM-10.jpg', titulo: 'Título pendiente', lente: '24 mm', apertura: 'f/4', velocidad: '1/50 s', iso: '800' },
      { archivo: 'HM-11.jpg', titulo: 'Título pendiente', lente: '24 mm', apertura: 'f/4', velocidad: '1/50 s', iso: '800' },
      { archivo: 'HM-12.jpg', titulo: 'Título pendiente', lente: '24 mm', apertura: 'f/4', velocidad: '1/50 s', iso: '800' },
      { archivo: 'HM-13.jpg', titulo: 'Título pendiente', lente: '24 mm', apertura: 'f/11', velocidad: '1/50 s', iso: '800' },
      { archivo: 'HM-14.jpg', titulo: 'Título pendiente', lente: '24 mm', apertura: 'f/5', velocidad: '1/50 s', iso: '800' },
      { archivo: 'HM-15.jpg', titulo: 'Título pendiente', lente: '65 mm', apertura: 'f/22', velocidad: '1/50 s', iso: '200' },
      { archivo: 'HM-16.jpg', titulo: 'Título pendiente', lente: '58 mm', apertura: 'f/22', velocidad: '1/50 s', iso: '200' },
      { archivo: 'HM-17.jpg', titulo: 'Título pendiente', lente: '82 mm', apertura: 'f/22', velocidad: '1/50 s', iso: '200' },
      { archivo: 'HM-18.jpg', titulo: 'Título pendiente', lente: '24 mm', apertura: 'f/4', velocidad: '1/50 s', iso: '400' },
      { archivo: 'HM-19.jpg', titulo: 'Título pendiente', lente: '24 mm', apertura: 'f/4', velocidad: '1/50 s', iso: '160' },
      { archivo: 'HM-20.jpg', titulo: 'Título pendiente', lente: '40 mm', apertura: 'f/13', velocidad: '1/50 s', iso: '100' },
      { archivo: 'HM-21.jpg', titulo: 'Título pendiente', lente: '32 mm', apertura: 'f/13', velocidad: '1/50 s', iso: '100' },
      { archivo: 'HM-22.jpg', titulo: 'Título pendiente', lente: '32 mm', apertura: 'f/5.6', velocidad: '1/100 s', iso: '100' },
      { archivo: 'HM-23.jpg', titulo: 'Título pendiente', lente: '47 mm', apertura: 'f/4', velocidad: '1/100 s', iso: '100' },
    ]
  },
  {
    id: 'HM2',
    titulo: 'Título pendiente',
    subtitulo: 'Colección pendiente',
    anio: '2026',
    camara: 'Canon 80D',
    fotos: [
      { archivo: 'HM2-1.jpg', titulo: 'Título pendiente', lente: '82 mm', apertura: 'f/22', velocidad: '1 s', iso: '800' },
      { archivo: 'HM2-2.jpg', titulo: 'Título pendiente', lente: '82 mm', apertura: 'f/22', velocidad: '1 s', iso: '800' },
      { archivo: 'HM2-3.jpg', titulo: 'Título pendiente', lente: '82 mm', apertura: 'f/22', velocidad: '1 s', iso: '800' },
      { archivo: 'HM2-4.jpg', titulo: 'Título pendiente', lente: '82 mm', apertura: 'f/22', velocidad: '1 s', iso: '800' },
      { archivo: 'HM2-5.jpg', titulo: 'Título pendiente', lente: '82 mm', apertura: 'f/22', velocidad: '1 s', iso: '800' },
      { archivo: 'HM2-6.jpg', titulo: 'Título pendiente', lente: '82 mm', apertura: 'f/22', velocidad: '1 s', iso: '800' },
      { archivo: 'HM2-7.jpg', titulo: 'Título pendiente', lente: '82 mm', apertura: 'f/22', velocidad: '1 s', iso: '800' },
      { archivo: 'HM2-8.jpg', titulo: 'Título pendiente', lente: '85 mm', apertura: 'f/22', velocidad: '1 s', iso: '800' },
      { archivo: 'HM2-9.jpg', titulo: 'Título pendiente', lente: '95 mm', apertura: 'f/5', velocidad: '1/50 s', iso: '800' },
    ]
  },
  {
    id: 'MX',
    titulo: 'Mix Media',
    subtitulo: 'Exp 1',
    lugar: 'Chile',
    anio: '2025',
    camara: 'Xiaomi 14T',
    fotos: [
      { archivo: 'MX-1.jpg', titulo: 'Industria' },
      { archivo: 'MX-2.jpg', titulo: 'Organico' },
    ]
  },
];


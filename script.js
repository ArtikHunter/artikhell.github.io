"use strict";

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const clamp = (n, min, max) => Math.min(max, Math.max(min, n));
const pad = (n) => String(n).padStart(2, "0");
const lerp = (a, b, t) => a + (b - a) * t;
const GALLERY_VIEW_PROGRESS = 0.44;
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)");
let serieActual = 0;
let fotoActual = 0;
let galleryAnimationFrame = 0;

const featured = $("#featured");
const featuredImage = $("#featured-image");
const featureEnter = $("#expand-photo");
const overlayToggle = $("#toggle-overlay");
const featuredImageFull = $("#featured-image-full");
const featureControls = $(".feature-controls");
let sideEntries = [];
let swapBusy = false;
let photoChangeTimer = 0;

function setImage(img, path, fallback) {
  if (!img) return;
  img.onerror = () => {
    img.classList.add("is-missing");
    if (fallback) fallback.classList.add("is-visible");
  };
  img.onload = () => {
    img.classList.remove("is-missing");
    if (fallback) fallback.classList.remove("is-visible");
  };
  img.classList.remove("is-missing");
  if (fallback) fallback.classList.remove("is-visible");
  img.src = path;
}

function mainPhoto() {
  return colecciones[serieActual].fotos[fotoActual];
}

function showPhoto({ animate = true, refreshSideSlots = true } = {}) {
  const serie = colecciones[serieActual];
  const foto = mainPhoto();
  clearTimeout(photoChangeTimer);
  featured.classList.remove("is-changing");
  if (animate && !reduceMotion.matches) {
    void featured.offsetWidth; // Reinicia la transición visual tras cada cambio.
    featured.classList.add("is-changing");
    photoChangeTimer = setTimeout(
      () => featured.classList.remove("is-changing"),
      520,
    );
  }
  setImage(featuredImage, foto.archivo, $("#featured-fallback"));
  setImage(featuredImageFull, foto.archivo);
  featuredImage.alt = `${foto.titulo} — ${serie.titulo}`;
  $("#featured-title").textContent = foto.titulo;
  $("#featured-photo-title").textContent = serie.titulo;
  $("#featured-count").innerHTML =
    `${fotoActual + 1}<span>/</span>${serie.fotos.length}`;
  if (refreshSideSlots) renderSideSlots();
  updateCollectionIndex();
  updateFullscreenSpecs();
}

function selectPhoto(
  collectionIndex,
  imageIndex = 0,
  { preserveSides = false, syncShowcase = true } = {},
) {
  if (!colecciones[collectionIndex]?.fotos.length) return;
  cancelPhotoSlide();
  serieActual = collectionIndex;
  fotoActual = clamp(
    imageIndex,
    0,
    colecciones[collectionIndex].fotos.length - 1,
  );
  showPhoto({ refreshSideSlots: !preserveSides });
  if (syncShowcase) renderShowcasePhotos(true);
}

let currentSlideAnimations = [];
function cancelPhotoSlide() {
  currentSlideAnimations.forEach((animation) => animation.cancel());
  currentSlideAnimations = [];
  $(".photo-slide-ghost")?.remove();
}

function stepPhoto(step) {
  const count = colecciones[serieActual].fotos.length;
  const direction = Math.sign(step) || 1;
  const expanded = sticky.classList.contains("is-expanded");
  const incomingLayer = expanded ? featuredImageFull : featuredImage;
  const outgoingPath = incomingLayer.currentSrc || incomingLayer.src;
  cancelPhotoSlide();
  let ghost = null;
  if (!reduceMotion.matches && outgoingPath) {
    ghost = document.createElement("img");
    ghost.className = "photo-slide-ghost";
    ghost.src = outgoingPath;
    ghost.alt = "";
    ghost.style.objectFit = expanded ? "contain" : "cover";
    $(".featured-image-wrap").append(ghost);
  }
  fotoActual = (fotoActual + step + count) % count;
  showPhoto({ animate: false, refreshSideSlots: false });
  const indexCenter = $(".showcase-center img");
  if (indexCenter && showcaseSlots[2] === serieActual)
    indexCenter.src = mainPhoto().archivo;
  if (!ghost) return;
  // Desplazamiento horizontal simultáneo, como páginas de un carrusel.
  const options = {
    duration: 660,
    easing: "cubic-bezier(.22,.75,.2,1)",
    fill: "both",
  };
  const a = ghost.animate(
    [
      { transform: "translate3d(0,0,0)", opacity: 1 },
      { transform: `translate3d(${-direction * 104}%,0,0)`, opacity: 0.72 },
    ],
    options,
  );
  const b = incomingLayer.animate(
    [
      { transform: `translate3d(${direction * 104}%,0,0)` },
      { transform: "translate3d(0,0,0)" },
    ],
    options,
  );
  currentSlideAnimations = [a, b];
  Promise.allSettled([a.finished, b.finished]).then(() => {
    ghost.remove();
    if (currentSlideAnimations[0] === a) cancelPhotoSlide();
  });
}

function shuffle(items) {
  const shuffled = [...items];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

function sideCandidates() {
  const groups = colecciones
    .map((serie, collectionIndex) => ({
      collectionIndex,
      serie,
      fotos: shuffle(
        serie.fotos
          .map((foto, imageIndex) => ({
            collectionIndex,
            imageIndex,
            foto,
            serie,
          }))
          .filter((candidate) => collectionIndex !== serieActual),
      ),
    }))
    .filter((group) => group.fotos.length);
  const result = [];

  while (result.length < 6 && groups.some((group) => group.fotos.length)) {
    shuffle(groups.filter((group) => group.fotos.length)).forEach((group) => {
      if (result.length < 6) result.push(group.fotos.pop());
    });
  }

  if (result.length < 6) {
    result.push(
      ...shuffle(
        colecciones[serieActual].fotos
          .map((foto, imageIndex) => ({
            collectionIndex: serieActual,
            imageIndex,
            foto,
            serie: colecciones[serieActual],
          }))
          .filter((candidate) => candidate.imageIndex !== fotoActual),
      ).slice(0, 6 - result.length),
    );
  }

  return result;
}

function renderSideSlot(index, entry) {
  const slot = sideSlots[index];
  slot.replaceChildren();
  if (!entry) {
    slot.hidden = true;
    return;
  }
  slot.hidden = false;
  const button = document.createElement("button");
  button.className = "side-image";
  button.type = "button";
  button.setAttribute(
    "aria-label",
    `Ver ${entry.foto.titulo}, colección ${entry.serie.titulo}`,
  );
  const img = document.createElement("img");
  img.alt = entry.foto.titulo;
  img.loading = "lazy";
  const empty = document.createElement("span");
  empty.className = "side-fallback";
  empty.textContent = entry.serie.titulo;
  const label = document.createElement("span");
  label.className = "side-label micro";
  label.textContent = entry.serie.titulo;
  button.append(img, empty, label);
  setImage(img, entry.foto.archivo, empty);
  button.addEventListener("click", () => swapCollection(index));
  slot.append(button);
}

function renderSideSlots(entries = sideCandidates()) {
  sideEntries = entries;
  sideSlots.forEach((_, index) => renderSideSlot(index, entries[index]));
}

// Índice visual: cinco portadas y cinco títulos como máximo por página.
const PAGE_SIZE = 5;
let archiveYear = "todos";
let archivePage = 0;
let showcaseSlots = [];
let showcaseBusy = false;
let showcasePulseTimer = 0;
let cancelShowcaseAnimation = null;

// Una nueva página o filtro puede interrumpir el intercambio sin aplicar una selección antigua.
function runShowcaseTransition(
  animations,
  ghosts,
  hiddenCards,
  finish,
  duration,
) {
  let completed = false;
  let timer;
  const complete = (cancelled = false) => {
    if (completed) return;
    completed = true;
    clearTimeout(timer);
    animations.forEach((animation) => animation.cancel());
    ghosts.forEach((ghost) => ghost.remove());
    hiddenCards.forEach((card) => card.classList.remove("is-switching"));
    showcaseBusy = false;
    cancelShowcaseAnimation = null;
    if (!cancelled) finish();
  };
  cancelShowcaseAnimation = () => complete(true);
  Promise.allSettled(animations.map((animation) => animation.finished)).then(
    () => complete(),
  );
  timer = setTimeout(() => complete(), duration + 150);
}

function filteredIndices() {
  return colecciones
    .map((serie, index) => ({ serie, index }))
    .filter(
      ({ serie }) =>
        archiveYear === "todos" || String(serie.anio) === archiveYear,
    )
    .map(({ index }) => index);
}
function pageIndices() {
  const indices = filteredIndices();
  archivePage = clamp(
    archivePage,
    0,
    Math.max(0, Math.ceil(indices.length / PAGE_SIZE) - 1),
  );
  return indices.slice(
    archivePage * PAGE_SIZE,
    archivePage * PAGE_SIZE + PAGE_SIZE,
  );
}
function createPreviewImage(collectionIndex, isCenter = false) {
  const collection = colecciones[collectionIndex];
  const img = document.createElement("img");
  img.alt = "";
  img.loading = "lazy";
  img.decoding = "async";
  img.src = isCenter ? mainPhoto().archivo : collection.fotos[0].archivo;
  return img;
}
function populatePreview(button, collectionIndex, isCenter) {
  button.replaceChildren();
  if (collectionIndex === undefined) {
    button.hidden = true;
    button.disabled = true;
    button.dataset.collection = "";
    return;
  }
  button.hidden = false;
  button.disabled = false;
  button.dataset.collection = String(collectionIndex);
  button.append(createPreviewImage(collectionIndex, isCenter));
  button.setAttribute(
    "aria-label",
    isCenter
      ? `Ampliar ${colecciones[collectionIndex].titulo}`
      : `Seleccionar ${colecciones[collectionIndex].titulo}`,
  );
}
function deriveShowcaseSlots() {
  const visible = pageIndices();
  const other = visible.filter((i) => i !== serieActual);
  const additional = filteredIndices().filter(
    (i) => i !== serieActual && !other.includes(i),
  );
  // Centro persistente incluso al cambiar el filtro o la página.
  return [
    other[0] ?? additional[0],
    other[1] ?? additional[1],
    serieActual,
    other[2] ?? additional[2],
    other[3] ?? additional[3],
  ];
}
function renderShowcasePhotos(reset = false) {
  if (reset || !showcaseSlots.length) showcaseSlots = deriveShowcaseSlots();
  showcaseSlots[2] = serieActual;
  $$(".showcase-card").forEach((node, i) =>
    populatePreview(node, showcaseSlots[i], i === 2),
  );
  const handoffSlots = [0, 1, 3, 4];
  $$(".handoff-card").forEach((node, i) => {
    node.replaceChildren();
    const collectionIndex = showcaseSlots[handoffSlots[i]];
    if (collectionIndex !== undefined)
      node.append(createPreviewImage(collectionIndex));
  });
}
function renderYearFilters() {
  const container = $("#showcase-filters");
  const years = [
    ...new Set(colecciones.map((s) => String(s.anio)).filter(Boolean)),
  ].sort((a, b) => Number(b) - Number(a));
  container.replaceChildren();
  ["todos", ...years].forEach((year) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "year-button micro";
    btn.textContent = year === "todos" ? "Todos" : year;
    btn.setAttribute("aria-pressed", String(archiveYear === year));
    btn.addEventListener("click", () => {
      archiveYear = year;
      archivePage = 0;
      const eligible = filteredIndices();
      if (eligible.length && !eligible.includes(serieActual)) {
        // Un filtro de año debe reflejarse también en la portada central.
        selectPhoto(eligible[0], 0, { syncShowcase: false });
      }
      renderArchivePage();
    });
    container.append(btn);
  });
}
function pulseShowcase() {
  const center = $(".showcase-center");
  center.classList.remove("is-pulsing");
  void center.offsetWidth;
  center.classList.add("is-pulsing");
  clearTimeout(showcasePulseTimer);
  showcasePulseTimer = setTimeout(
    () => center.classList.remove("is-pulsing"),
    1050,
  );
}
function animateShowcaseChoice(collectionIndex) {
  if (
    showcaseBusy ||
    collectionIndex === serieActual ||
    !colecciones[collectionIndex]
  )
    return;
  stopHoverAdvance();
  const sidePosition = showcaseSlots.findIndex(
    (index, i) => i !== 2 && index === collectionIndex,
  );
  const cards = $$(".showcase-card");
  const center = cards[2];
  const oldIndex = serieActual;
  const oldCenterImage = center.querySelector("img");
  const finish = () => {
    selectPhoto(collectionIndex, 0, {
      preserveSides: false,
      syncShowcase: false,
    });
    if (sidePosition >= 0) showcaseSlots[sidePosition] = oldIndex;
    showcaseSlots[2] = collectionIndex;
    renderShowcasePhotos();
    updateCollectionIndex();
    showcaseBusy = false;
    pulseShowcase();
  };
  if (reduceMotion.matches) {
    finish();
    return;
  }
  showcaseBusy = true;
  const duration = sidePosition >= 0 ? 850 : 680;
  if (sidePosition >= 0) {
    // FLIP: dos fotografías intercambian sus cajas manteniendo object-fit.
    const side = cards[sidePosition];
    const rectA = center.getBoundingClientRect();
    const rectB = side.getBoundingClientRect();
    const makeGhost = (source, rect, z) => {
      const ghost = document.createElement("div");
      ghost.className = "showcase-ghost";
      ghost.style.zIndex = String(z);
      Object.assign(ghost.style, {
        left: `${rect.left}px`,
        top: `${rect.top}px`,
        width: `${rect.width}px`,
        height: `${rect.height}px`,
      });
      const img = document.createElement("img");
      img.src = source;
      img.alt = "";
      ghost.append(img);
      document.body.append(ghost);
      return ghost;
    };
    const ghostA = makeGhost(
      oldCenterImage?.src || mainPhoto().archivo,
      rectA,
      240,
    );
    const ghostB = makeGhost(
      side.querySelector("img")?.src ||
        colecciones[collectionIndex].fotos[0].archivo,
      rectB,
      241,
    );
    center.classList.add("is-switching");
    side.classList.add("is-switching");
    const frames = (from, to) => [
      {
        left: `${from.left}px`,
        top: `${from.top}px`,
        width: `${from.width}px`,
        height: `${from.height}px`,
      },
      {
        left: `${to.left}px`,
        top: `${to.top}px`,
        width: `${to.width}px`,
        height: `${to.height}px`,
      },
    ];
    const easing = "cubic-bezier(.25,.85,.18,1)";
    const animations = [
      ghostA.animate(frames(rectA, rectB), {
        duration,
        easing,
        fill: "forwards",
      }),
      ghostB.animate(frames(rectB, rectA), {
        duration,
        easing,
        fill: "forwards",
      }),
    ];
    runShowcaseTransition(
      animations,
      [ghostA, ghostB],
      [center, side],
      finish,
      duration,
    );
  } else {
    // La selección no está en los cuatro laterales: el centro sale hacia arriba.
    const rect = center.getBoundingClientRect();
    const ghost = document.createElement("div");
    ghost.className = "showcase-ghost";
    Object.assign(ghost.style, {
      left: `${rect.left}px`,
      top: `${rect.top}px`,
      width: `${rect.width}px`,
      height: `${rect.height}px`,
    });
    const img = document.createElement("img");
    img.src = oldCenterImage?.src || mainPhoto().archivo;
    img.alt = "";
    ghost.append(img);
    document.body.append(ghost);
    center.classList.add("is-switching");
    selectPhoto(collectionIndex, 0, {
      preserveSides: false,
      syncShowcase: false,
    });
    showcaseSlots[2] = collectionIndex;
    renderShowcasePhotos();
    center.classList.remove("is-switching");
    const incoming = center.animate(
      [
        { opacity: 0, transform: "translateY(22px) scale(.96)" },
        { opacity: 1, transform: "none" },
      ],
      { duration: 650, easing: "cubic-bezier(.2,.9,.2,1)" },
    );
    const outgoing = ghost.animate(
      [
        { opacity: 1, transform: "translateY(0)" },
        { opacity: 0, transform: "translateY(-125%) scale(.85)" },
      ],
      { duration, easing: "cubic-bezier(.25,.8,.2,1)", fill: "forwards" },
    );
    runShowcaseTransition(
      [incoming, outgoing],
      [ghost],
      [],
      pulseShowcase,
      duration,
    );
  }
  $$(".collection-row").forEach((btn) =>
    btn.setAttribute(
      "aria-pressed",
      String(Number(btn.dataset.collection) === collectionIndex),
    ),
  );
}
function renderArchivePage() {
  cancelShowcaseAnimation?.();
  const visible = pageIndices();
  const all = filteredIndices();
  const totalPages = Math.max(1, Math.ceil(all.length / PAGE_SIZE));
  $("#page-count").textContent = `${pad(archivePage + 1)} / ${pad(totalPages)}`;
  $("#showcase-page-summary").textContent = `${all.length} COLECCIONES`;
  $("#page-prev").disabled = archivePage === 0;
  $("#page-next").disabled = archivePage >= totalPages - 1;
  $$(".year-button").forEach((button) =>
    button.setAttribute(
      "aria-pressed",
      String(
        (button.textContent.toLowerCase() === "todos"
          ? "todos"
          : button.textContent) === archiveYear,
      ),
    ),
  );
  const container = $("#collection-index");
  container.replaceChildren();
  visible.forEach((index, position) => {
    const serie = colecciones[index];
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "collection-row";
    btn.dataset.collection = String(index);
    btn.setAttribute("aria-pressed", String(serieActual === index));
    btn.innerHTML = `<span class="micro">${pad(archivePage * PAGE_SIZE + position + 1)}</span><strong></strong><span class="collection-meta micro"></span><span class="collection-arrow" aria-hidden="true">↗</span>`;
    btn.querySelector("strong").textContent = serie.titulo;
    btn.querySelector(".collection-meta").textContent =
      `${serie.subtitulo} · ${serie.fotos.length} fotos`;
    btn.addEventListener("click", () => {
      btn.classList.add("is-flashing");
      setTimeout(() => btn.classList.remove("is-flashing"), 1150);
      animateShowcaseChoice(index);
    });
    container.append(btn);
  });
  // Los ejemplos visuales corresponden a la página y al año seleccionados.
  renderShowcasePhotos(true);
}
$("#page-prev").addEventListener("click", () => {
  archivePage = Math.max(0, archivePage - 1);
  renderArchivePage();
});
$("#page-next").addEventListener("click", () => {
  archivePage++;
  renderArchivePage();
});
$$(".showcase-card").forEach((button, index) =>
  button.addEventListener("click", () => {
    if (showcaseBusy) return;
    if (index === 2) {
      stopHoverAdvance();
      jumpToGalleryProgress(GALLERY_VIEW_PROGRESS, false);
    } else {
      const collectionIndex = showcaseSlots[index];
      if (collectionIndex !== undefined) animateShowcaseChoice(collectionIndex);
    }
  }),
);

let revealTimer = 0;
function revealGalleryControls() {
  if (reduceMotion.matches) return;
  featured.classList.remove("is-revealing");
  // Reiniciar los fotogramas de la animación de entrada después del intercambio.
  void featured.offsetWidth;
  featured.classList.add("is-revealing");
  clearTimeout(revealTimer);
  revealTimer = setTimeout(
    () => featured.classList.remove("is-revealing"),
    920,
  );
}

// Las cartas cambian de tamaño de CONTENEDOR, no de escala de imagen.
// object-fit: cover recorta sin deformar al moverse entre rectángulos de distinta proporción.
function swapCollection(index) {
  const entry = sideEntries[index];
  if (!entry || swapBusy) return;
  const slot = sideSlots[index];
  const sideButton = $(".side-image", slot);
  if (!sideButton) return;
  const previous = {
    collectionIndex: serieActual,
    imageIndex: fotoActual,
    serie: colecciones[serieActual],
    foto: mainPhoto(),
  };
  if (entry.collectionIndex === serieActual && entry.imageIndex === fotoActual)
    return;
  if (reduceMotion.matches || galleryProgress > 0.65) {
    sideEntries[index] = previous;
    selectPhoto(entry.collectionIndex, entry.imageIndex, {
      preserveSides: true,
      syncShowcase: true,
    });
    renderSideSlot(index, previous);
    revealGalleryControls();
    return;
  }
  swapBusy = true;
  stopHoverAdvance();
  const fullRect = featured.getBoundingClientRect();
  const sideRect = sideButton.getBoundingClientRect();
  const oldSrc = featuredImage.currentSrc || featuredImage.src;
  const newSrc = $("img", sideButton).currentSrc || $("img", sideButton).src;

  function movingCard(src, from, to, klass) {
    const node = document.createElement("div");
    node.className = `swap-flyer ${klass}`;
    const image = document.createElement("img");
    image.src = src;
    image.alt = "";
    image.decoding = "async";
    image.style.objectFit = "cover";
    node.append(image);
    Object.assign(node.style, {
      left: `${from.left}px`,
      top: `${from.top}px`,
      width: `${from.width}px`,
      height: `${from.height}px`,
    });
    document.body.append(node);
    // El tamaño de la caja se interpola directamente, manteniendo la proporción de la foto.
    const animation = node.animate(
      [
        {
          left: `${from.left}px`,
          top: `${from.top}px`,
          width: `${from.width}px`,
          height: `${from.height}px`,
        },
        {
          left: `${to.left}px`,
          top: `${to.top}px`,
          width: `${to.width}px`,
          height: `${to.height}px`,
        },
      ],
      { duration: 950, easing: "cubic-bezier(.22,.8,.18,1)", fill: "forwards" },
    );
    return { node, animation };
  }

  const incoming = movingCard(newSrc, sideRect, fullRect, "swap-flyer-in");
  const outgoing = movingCard(oldSrc, fullRect, sideRect, "swap-flyer-out");
  featured.classList.add("is-swapping");
  slot.classList.add("is-swapping");
  sideEntries[index] = previous;
  // Preparar la nueva imagen a tamaño final DETRÁS de las cartas en movimiento.
  selectPhoto(entry.collectionIndex, entry.imageIndex, {
    preserveSides: true,
    syncShowcase: true,
  });
  renderSideSlot(index, previous);
  Promise.allSettled([
    incoming.animation.finished,
    outgoing.animation.finished,
  ]).then(() => {
    featured.classList.remove("is-swapping");
    slot.classList.remove("is-swapping");
    incoming.node.remove();
    outgoing.node.remove();
    swapBusy = false;
    revealGalleryControls();
  });
}

function updateCollectionIndex() {
  $$(".collection-row").forEach((btn) =>
    btn.setAttribute(
      "aria-pressed",
      String(Number(btn.dataset.collection) === serieActual),
    ),
  );
}

function specsFor(serie, foto) {
  const specs = [
    ["Colección", serie.titulo],
    ["Lugar", serie.lugar],
    ["Año", serie.anio],
    ["Cámara", serie.camara],
    ["Distancia focal", foto.lente],
    ["Apertura", foto.apertura],
    ["Velocidad", foto.velocidad],
    ["ISO", foto.iso],
  ];
  return specs.filter(([, value]) => value && value !== "Sin fecha indicada");
}

function updateFullscreenSpecs() {
  const serie = colecciones[serieActual];
  const foto = mainPhoto();
  $("#fullscreen-photo-index").textContent =
    `${fotoActual + 1}/${serie.fotos.length}`;
  const dl = $("#fullscreen-spec-list");
  dl.replaceChildren();
  specsFor(serie, foto).forEach(([label, value]) => {
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = value;
    dl.append(dt, dd);
  });
}

let overlayHidden = false;
function syncOverlayToggle() {
  if (!overlayToggle) return;
  overlayToggle.setAttribute("aria-pressed", String(overlayHidden));
  overlayToggle.setAttribute(
    "aria-label",
    overlayHidden
      ? "Mostrar textos y datos de la fotografía"
      : "Ocultar textos y datos de la fotografía",
  );
  sticky?.classList.toggle("is-text-hidden", overlayHidden);
}
overlayToggle?.addEventListener("click", () => {
  overlayHidden = !overlayHidden;
  syncOverlayToggle();
});

// Mantener el cursor sobre una flecha inicia una cuenta atrás circular.
// Al completar la vuelta cambia la foto y vuelve a cargar, hasta salir.
const HOLD_DURATION = 5000;
let holdTimeout = null;
let holdButton = null;
function stopHoverAdvance() {
  clearTimeout(holdTimeout);
  holdTimeout = null;
  holdButton?.classList.remove("is-counting");
  holdButton = null;
}
function beginHoverAdvance(button, direction) {
  if (
    reduceMotion.matches ||
    !matchMedia("(hover:hover) and (pointer:fine)").matches
  )
    return;
  stopHoverAdvance();
  holdButton = button;
  const round = () => {
    if (document.hidden || holdButton !== button || !button.matches(":hover")) {
      stopHoverAdvance();
      return;
    }
    button.classList.remove("is-counting");
    void button.offsetWidth; // Reinicia el trazo sin acumular progreso.
    button.classList.add("is-counting");
    holdTimeout = setTimeout(() => {
      if (
        holdButton !== button ||
        !button.matches(":hover") ||
        document.hidden
      ) {
        stopHoverAdvance();
        return;
      }
      stepPhoto(direction);
      round();
    }, HOLD_DURATION);
  };
  round();
}
[
  [-1, "#prev-photo"],
  [1, "#next-photo"],
].forEach(([step, selector]) => {
  const btn = $(selector);
  btn.addEventListener("click", () => {
    stepPhoto(step);
    if (holdButton === btn) beginHoverAdvance(btn, step);
  });
  btn.addEventListener("mouseenter", () => beginHoverAdvance(btn, step));
  btn.addEventListener("mouseleave", stopHoverAdvance);
  btn.addEventListener("blur", stopHoverAdvance);
});
document.addEventListener("visibilitychange", () => {
  if (document.hidden) stopHoverAdvance();
});

// La imagen central reemplaza el antiguo botón y el visor modal.
function enterPhotograph() {
  jumpToGalleryProgress(GALLERY_VIEW_PROGRESS, !reduceMotion.matches);
}
featureEnter.addEventListener("click", enterPhotograph);

window.addEventListener("keydown", (event) => {
  if (!["ArrowLeft", "ArrowRight", "Escape"].includes(event.key)) return;
  const focused = document.activeElement;
  if (focused?.matches("input, textarea, select") || focused?.isContentEditable)
    return;
  const stageRect = sticky.getBoundingClientRect();
  if (
    galleryProgress < 0.26 ||
    galleryProgress > 0.82 ||
    stageRect.bottom <= 0 ||
    stageRect.top >= innerHeight ||
    $("#menu-toggle").getAttribute("aria-expanded") === "true"
  )
    return;
  if (event.key === "Escape") {
    event.preventDefault();
    stopHoverAdvance();
    $("#archive-index").scrollIntoView({
      behavior: reduceMotion.matches ? "instant" : "smooth",
      block: "start",
    });
    return;
  }
  if (event.key === "ArrowLeft") {
    event.preventDefault();
    stepPhoto(-1);
  }
  if (event.key === "ArrowRight") {
    event.preventDefault();
    stepPhoto(1);
  }
});

// Retrato: si el archivo no existe, mostramos una tarjeta tipográfica.
const portrait = $(".portrait-card img");
portrait.addEventListener("error", () => {
  portrait.classList.add("is-missing");
  $(".portrait-fallback").classList.add("is-visible");
});
portrait.addEventListener("load", () => {
  portrait.classList.remove("is-missing");
  $(".portrait-fallback").classList.remove("is-visible");
});
if (portrait.complete && !portrait.naturalWidth)
  portrait.dispatchEvent(new Event("error"));

/* ============================================================
   MOVIMIENTO CINEMATOGRÁFICO
   Scroll: la imagen central aumenta de tamaño en el escenario.
   Puntero: ligera inercia en el encabezado y la galería.
   Sin librerías, con fallback para móviles y movimiento reducido.
   ============================================================ */
const runway = $("#gallery-runway");
const sticky = $("#gallery-sticky");
const hero = $(".hero");
const siteHeader = $(".site-header");
const cursorHalo = $(".cursor-halo");
const finePointer = matchMedia("(pointer: fine)");
const pointerTarget = { x: 0, y: 0 };
const pointerSmooth = { x: 0, y: 0 };
const pointerPosition = { x: -100, y: -100 };
const cursorSmooth = { x: -100, y: -100 };
let pointerActive = false;
let pointerFrame = 0;
let heroVisible = true;
let lastMotionTime = 0;

let galleryProgress = 0;
const sideSlots = $$(".side-slot");
const SIDE_LAYOUTS = {
  mobile: [
    [0.015, 0.25, 0.225, 0.31, -1, -0.15],
    [0.015, 0.6, 0.225, 0.27, -1, 0.32],
    [0.265, 0.74, 0.22, 0.155, -1, 0.68],
    [0.55, 0.145, 0.185, 0.15, 1, -0.46],
    [0.76, 0.25, 0.225, 0.31, 1, -0.2],
    [0.76, 0.6, 0.225, 0.27, 1, 0.3],
  ],
  desktop: [
    [0.02, 0.225, 0.225, 0.365, -1, -0.15],
    [0.02, 0.615, 0.225, 0.285, -1, 0.32],
    [0.27, 0.725, 0.213, 0.21, -1, 0.68],
    [0.59, 0.11, 0.14, 0.185, 1, -0.44],
    [0.755, 0.225, 0.225, 0.34, 1, -0.2],
    [0.755, 0.59, 0.225, 0.315, 1, 0.34],
  ],
};
const SIDE_SPREAD_X = [0.68, 0.51, 0.56, 0.48, 0.67, 0.59];
const SIDE_SPREAD_Y = [0.7, 0.55, 0.8, 0.75, 0.52, 0.65];
const BOX_PROPERTIES = ["left", "top", "width", "height"];
const smoothstep = (start, end, value) => {
  const t = clamp((value - start) / (end - start), 0, 1);
  return t * t * (3 - 2 * t);
};

function jumpToGalleryProgress(progress, animate = true) {
  const y = runway.getBoundingClientRect().top + scrollY;
  const travel = Math.max(0, runway.offsetHeight - innerHeight);
  scrollTo({
    top: y + travel * progress,
    behavior: animate ? "smooth" : "instant",
  });
}

let currentPhotoAspect = 1.6;
function updatePhotoAspect() {
  if (featuredImageFull?.naturalWidth && featuredImageFull.naturalHeight) {
    currentPhotoAspect = clamp(
      featuredImageFull.naturalWidth / featuredImageFull.naturalHeight,
      0.35,
      3.8,
    );
    scheduleScroll();
  }
}
featuredImageFull?.addEventListener("load", updatePhotoAspect);
if (featuredImageFull?.complete && featuredImageFull.naturalWidth)
  updatePhotoAspect();

let lastGalleryLayout = "";
function updateGalleryScroll() {
  const rect = runway.getBoundingClientRect();
  const travel = Math.max(1, rect.height - innerHeight);
  galleryProgress = clamp(-rect.top / travel, 0, 1);
  const bounds = sticky.getBoundingClientRect();
  const W = bounds.width,
    H = bounds.height;
  const layoutKey = `${W}:${H}:${galleryProgress}:${currentPhotoAspect}:${reduceMotion.matches}`;
  if (layoutKey === lastGalleryLayout) return;
  lastGalleryLayout = layoutKey;
  const mobile = W < 801;
  const growth = reduceMotion.matches
    ? galleryProgress >= 0.3
      ? 1
      : 0
    : smoothstep(0.005, 0.32, galleryProgress);
  const fade = smoothstep(0.56, 0.69, galleryProgress);
  const shrink = reduceMotion.matches
    ? galleryProgress > 0.77
      ? 1
      : 0
    : smoothstep(0.7, 0.96, galleryProgress);
  const aspect = clamp(currentPhotoAspect || 1.6, 0.35, 3.8);

  // El marco siempre se centra contra la dimensión REAL de la ventana sticky.
  const initial = mobile
    ? { left: W * 0.27, top: H * 0.34, width: W * 0.46, height: H * 0.34 }
    : { left: W * 0.27, top: H * 0.335, width: W * 0.46, height: H * 0.36 };
  const maxW = W * (mobile ? 0.89 : 0.83),
    maxH = H * (mobile ? 0.7 : 0.78);
  const bigW = Math.min(maxW, maxH * aspect),
    bigH = Math.min(maxH, maxW / aspect);
  const expanded = {
    left: (W - bigW) / 2,
    top: (H - bigH) / 2,
    width: bigW,
    height: bigH,
  };
  // El punto de llegada coincide con la portada central de la hilera de cinco.
  const rowW = W * (mobile ? 0.26 : 0.175),
    rowH = H * (mobile ? 0.155 : 0.215);
  const small = {
    left: (W - rowW) / 2,
    top: H * (mobile ? 0.51 : 0.5) - rowH / 2,
    width: rowW,
    height: rowH,
  };
  const active = {};
  for (const key of BOX_PROPERTIES) {
    active[key] = lerp(lerp(initial[key], expanded[key], growth), small[key], shrink);
  }
  Object.assign(featured.style, {
    left: `${active.left.toFixed(2)}px`,
    top: `${active.top.toFixed(2)}px`,
    width: `${active.width.toFixed(2)}px`,
    height: `${active.height.toFixed(2)}px`,
  });
  // En el estado ampliado nunca quedan barras artificiales; contain es íntegro.
  featured.style.setProperty(
    "--reveal-full",
    (growth * (1 - shrink)).toFixed(3),
  );
  featured.classList.toggle("is-compact-photo", mobile && active.height < 330);
  sticky.style.setProperty(
    "--fullscreen-info-opacity",
    (smoothstep(0.93, 1, growth) * (1 - fade)).toFixed(3),
  );
  sticky.style.setProperty("--u-controls-opacity", (1 - fade).toFixed(3));
  sticky.style.setProperty("--u-drop", `${(H * 0.05 * fade).toFixed(2)}px`);
  sticky.style.setProperty(
    "--handoff-opacity",
    smoothstep(0.76, 0.93, galleryProgress).toFixed(3),
  );
  sticky.classList.toggle("is-expanded", growth > 0.965 && shrink < 0.85);
  sticky.classList.toggle("is-gallery-retiring", fade > 0.02);
  sticky.classList.toggle("is-handoff", shrink > 0.25);
  featureEnter.disabled = growth > 0.96 || shrink > 0.25;
  featureEnter.setAttribute(
    "aria-label",
    growth > 0.96 ? "Fotografía ampliada" : "Ampliar fotografía",
  );
  featured.style.pointerEvents = shrink > 0.75 ? "none" : "";
  featured.inert = shrink > 0.75;
  featureControls.inert = fade > 0.02;

  // Un mismo progreso hace crecer el centro y expulsa los laterales por los márgenes.
  const seeds = mobile ? SIDE_LAYOUTS.mobile : SIDE_LAYOUTS.desktop;
  const spread = Math.pow(growth, 1.17);
  const gap = Math.max(9, W * 0.008);
  const visible = 1 - smoothstep(0.22, 0.38, galleryProgress);
  const mainRight = active.left + active.width,
    mainBottom = active.top + active.height;
  sideSlots.forEach((slot, i) => {
    const [x, y, w, h, sign, yDir] = seeds[i];
    const card = { left: W * x, top: H * y, width: W * w, height: H * h };
    card.left += sign * W * SIDE_SPREAD_X[i] * spread;
    card.top += H * yDir * SIDE_SPREAD_Y[i] * spread;
    // Protección secundaria de colisiones durante la fase inicial.
    const overlap =
      card.left < mainRight + gap &&
      card.left + card.width > active.left - gap &&
      card.top < mainBottom + gap &&
      card.top + card.height > active.top - gap;
    if (overlap) {
      if (sign < 0) card.left = active.left - gap - card.width;
      else card.left = mainRight + gap;
    }
    Object.assign(slot.style, {
      left: `${card.left}px`,
      top: `${card.top}px`,
      width: `${card.width}px`,
      height: `${card.height}px`,
      opacity: visible.toFixed(3),
    });
    slot.style.pointerEvents = visible < 0.16 ? "none" : "";
    slot.inert = visible < 0.16;
  });
}

let lastHeroProgress = -1;
function updateHeroScroll(height) {
  const progress = clamp(scrollY / (height * 0.98), 0, 1);
  if (progress === lastHeroProgress) return;
  lastHeroProgress = progress;
  hero.style.setProperty("--hero-shrink", (1 - progress * 0.53).toFixed(4));
  hero.style.setProperty("--hero-turn", `${(progress * 75).toFixed(2)}deg`);
  hero.style.setProperty("--hero-drift", `${(-progress * 105).toFixed(2)}px`);
  hero.style.setProperty(
    "--hero-disappear",
    (1 - smoothstep(0.1, 0.94, progress)).toFixed(4),
  );
  hero.style.setProperty(
    "--hero-veil-opacity",
    smoothstep(0.16, 0.84, progress).toFixed(4),
  );
  const headerProgress = smoothstep(0.03, 0.34, clamp(scrollY / height, 0, 1));
  siteHeader.style.setProperty("--header-shrink", headerProgress.toFixed(4));
  siteHeader.classList.toggle("is-compact", headerProgress > 0.6);
}

function scheduleScroll() {
  if (galleryAnimationFrame) return;
  galleryAnimationFrame = requestAnimationFrame(() => {
    const heroHeight = Math.max(1, hero.offsetHeight);
    updateGalleryScroll();
    updateHeroScroll(heroHeight);
    galleryAnimationFrame = 0;
  });
}
window.addEventListener("scroll", scheduleScroll, { passive: true });
window.addEventListener("resize", scheduleScroll);
reduceMotion.addEventListener("change", scheduleScroll);

// El bucle solo vive mientras el cursor o la inercia tienen movimiento pendiente.
function stopPointerAnimation() {
  cancelAnimationFrame(pointerFrame);
  pointerFrame = 0;
  lastMotionTime = 0;
  cursorHalo.classList.remove("is-visible");
}
function schedulePointer() {
  if (
    !pointerFrame &&
    pointerActive &&
    finePointer.matches &&
    !reduceMotion.matches &&
    !document.hidden
  ) {
    pointerFrame = requestAnimationFrame(animatePointer);
  }
}
function animatePointer(timestamp) {
  pointerFrame = 0;
  const rate = clamp(
    (timestamp - (lastMotionTime || timestamp)) / 16.67,
    0.3,
    3,
  );
  const ease = 1 - Math.pow(0.88, rate);
  pointerSmooth.x += (pointerTarget.x - pointerSmooth.x) * ease;
  pointerSmooth.y += (pointerTarget.y - pointerSmooth.y) * ease;
  cursorSmooth.x +=
    (pointerPosition.x - cursorSmooth.x) * (1 - Math.pow(0.75, rate));
  cursorSmooth.y +=
    (pointerPosition.y - cursorSmooth.y) * (1 - Math.pow(0.75, rate));
  if (heroVisible) {
    hero.style.setProperty(
      "--pointer-x",
      `${(pointerSmooth.x * 17).toFixed(2)}px`,
    );
    hero.style.setProperty(
      "--pointer-y",
      `${(pointerSmooth.y * 13).toFixed(2)}px`,
    );
  }
  cursorHalo.style.transform = `translate3d(${cursorSmooth.x}px,${cursorSmooth.y}px,0) translate(-50%,-50%)`;
  cursorHalo.classList.add("is-visible");
  lastMotionTime = timestamp;
  const pending =
    Math.abs(pointerPosition.x - cursorSmooth.x) > 0.1 ||
    Math.abs(pointerPosition.y - cursorSmooth.y) > 0.1 ||
    (heroVisible &&
      (Math.abs(pointerTarget.x - pointerSmooth.x) > 0.001 ||
        Math.abs(pointerTarget.y - pointerSmooth.y) > 0.001));
  if (pending) schedulePointer();
  else lastMotionTime = 0;
}
document.addEventListener(
  "pointermove",
  (event) => {
    if (
      !finePointer.matches ||
      reduceMotion.matches ||
      (event.pointerType && event.pointerType !== "mouse")
    )
      return;
    pointerPosition.x = event.clientX;
    pointerPosition.y = event.clientY;
    pointerTarget.x = (event.clientX / innerWidth - 0.5) * 2;
    pointerTarget.y = (event.clientY / innerHeight - 0.5) * 2;
    pointerActive = true;
    if (heroVisible) {
      hero.style.setProperty(
        "--mouse-x",
        `${(event.clientX / innerWidth) * 100}%`,
      );
      hero.style.setProperty(
        "--mouse-y",
        `${(event.clientY / innerHeight) * 100}%`,
      );
    }
    schedulePointer();
  },
  { passive: true },
);
document.addEventListener("pointerleave", () => {
  pointerActive = false;
  stopPointerAnimation();
});
document.addEventListener("pointerover", (event) => {
  if (finePointer.matches)
    cursorHalo.classList.toggle(
      "is-interactive",
      !!event.target.closest("a, button"),
    );
});

/* Ondas suaves detrás de la portada, inspiradas en la respuesta
   pictórica al ratón. Son un efecto Canvas 2D sencillo, no WebGL. */
const wavesCanvas = $("#hero-waves");
const wavesContext = wavesCanvas.getContext("2d");
let waves = [];
let wavesFrame = 0;
let lastWave = 0;
let waveScale = 1;
let wavesNeedResize = true;
function resizeWaves() {
  if (!wavesContext) return;
  const rect = hero.getBoundingClientRect();
  waveScale = Math.min(devicePixelRatio || 1, 2);
  wavesCanvas.width = Math.round(rect.width * waveScale);
  wavesCanvas.height = Math.round(rect.height * waveScale);
  wavesContext.setTransform(waveScale, 0, 0, waveScale, 0, 0);
  wavesNeedResize = false;
}
function stopWaves() {
  cancelAnimationFrame(wavesFrame);
  wavesFrame = 0;
  waves = [];
  wavesContext?.clearRect(
    0,
    0,
    wavesCanvas.width / waveScale,
    wavesCanvas.height / waveScale,
  );
}
function drawWaves(now) {
  if (
    !wavesContext ||
    reduceMotion.matches ||
    document.hidden ||
    !heroVisible
  ) {
    stopWaves();
    return;
  }
  wavesContext.clearRect(
    0,
    0,
    wavesCanvas.width / waveScale,
    wavesCanvas.height / waveScale,
  );
  waves = waves.filter((wave) => now - wave.start < 1350);
  waves.forEach((wave) => {
    const t = (now - wave.start) / 1350;
    for (let ring = 0; ring < 2; ring++) {
      const radius = 18 + t * 165 + ring * 23;
      const opacity = (0.13 * Math.pow(1 - t, 1.65)) / (ring + 1);
      wavesContext.beginPath();
      for (let i = 0; i <= 64; i++) {
        const theta = (i / 64) * Math.PI * 2;
        const uneven =
          1 +
          Math.sin(theta * 5 + wave.phase) * 0.038 +
          Math.cos(theta * 3 - wave.phase) * 0.02;
        const x = wave.x + Math.cos(theta) * radius * uneven;
        const y = wave.y + Math.sin(theta) * radius * uneven;
        if (i === 0) wavesContext.moveTo(x, y);
        else wavesContext.lineTo(x, y);
      }
      wavesContext.strokeStyle = `rgba(223,191,151,${opacity.toFixed(4)})`;
      wavesContext.lineWidth = 1.2;
      wavesContext.stroke();
    }
  });
  wavesFrame = waves.length ? requestAnimationFrame(drawWaves) : 0;
}
if (wavesContext) {
  addEventListener("resize", () => {
    wavesNeedResize = true;
  });
  hero.addEventListener(
    "pointermove",
    (event) => {
      if (
        !finePointer.matches ||
        reduceMotion.matches ||
        document.hidden ||
        (event.pointerType && event.pointerType !== "mouse")
      )
        return;
      const now = performance.now();
      if (now - lastWave < 105) return;
      if (wavesNeedResize) resizeWaves();
      const rect = hero.getBoundingClientRect();
      waves.push({
        x: event.clientX - rect.left,
        y: event.clientY - rect.top,
        start: now,
        phase: ((now % 900) / 900) * Math.PI * 2,
      });
      lastWave = now;
      if (!wavesFrame) wavesFrame = requestAnimationFrame(drawWaves);
    },
    { passive: true },
  );
}
reduceMotion.addEventListener("change", () => {
  stopHoverAdvance();
  cancelPhotoSlide();
  if (reduceMotion.matches) {
    stopPointerAnimation();
    stopWaves();
    hero.style.setProperty("--pointer-x", "0px");
    hero.style.setProperty("--pointer-y", "0px");
  } else schedulePointer();
});
finePointer.addEventListener("change", () => {
  if (!finePointer.matches) {
    stopPointerAnimation();
    stopWaves();
  }
});
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    stopPointerAnimation();
    stopWaves();
  } else schedulePointer();
});
const heroObserver = new IntersectionObserver(([entry]) => {
  heroVisible = entry.isIntersecting;
  if (!heroVisible) stopWaves();
  else schedulePointer();
});
heroObserver.observe(hero);

/* Menú móvil */
const menuButton = $("#menu-toggle");
const mobileMenu = $("#mobile-menu");
function toggleMobileMenu(force) {
  const hadMenuFocus = mobileMenu.contains(document.activeElement);
  const open =
    typeof force === "boolean"
      ? force
      : menuButton.getAttribute("aria-expanded") !== "true";
  menuButton.setAttribute("aria-expanded", String(open));
  menuButton.setAttribute("aria-label", open ? "Cerrar menú" : "Abrir menú");
  mobileMenu.inert = !open;
  document.body.classList.toggle("menu-is-open", open);
  if (!open && hadMenuFocus && innerWidth <= 800)
    menuButton.focus();
}
menuButton.addEventListener("click", () => toggleMobileMenu());
$$("#mobile-menu a").forEach((link) =>
  link.addEventListener("click", () => toggleMobileMenu(false)),
);
window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") toggleMobileMenu(false);
});
window.addEventListener("resize", () => {
  if (innerWidth > 800) toggleMobileMenu(false);
});

/* Aparición discreta de bloques mientras entran en pantalla */
const observer = new IntersectionObserver(
  (entries) =>
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in-view");
        observer.unobserve(entry.target);
      }
    }),
  { threshold: 0.08 },
);
$$(
  ".intro-statement, .films-header, .film-card, .about-grid, .contact h2",
).forEach((el) => {
  el.classList.add("scroll-reveal");
  observer.observe(el);
});

renderYearFilters();
renderArchivePage();
showPhoto({ animate: false });
scheduleScroll();

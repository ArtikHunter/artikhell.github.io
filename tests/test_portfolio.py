"""Browser regression checks. Run: python3 -m unittest discover -s tests -v."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import base64
import os
from pathlib import Path
import shutil
from threading import Thread
import unittest
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


class PortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT))
        )
        cls.server_thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"
        cls.playwright = sync_playwright().start()
        executable = os.environ.get("CHROMIUM_PATH") or shutil.which("chromium")
        launch = {"headless": True}
        if executable:
            launch["executable_path"] = executable
        cls.browser = cls.playwright.chromium.launch(**launch)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()

    def setUp(self):
        self.context = self.browser.new_context(
            viewport={"width": 1440, "height": 900}, reduced_motion="no-preference"
        )
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.route(
            "**/*",
            lambda route: route.continue_()
            if urlsplit(route.request.url).hostname == "127.0.0.1"
            else route.abort(),
        )
        self.page.add_init_script("Math.random = () => .42")
        self.page.goto(self.base_url, wait_until="networkidle")
        self.esperar_carga()

    def tearDown(self):
        try:
            self.assertEqual(self.errors, [], "Uncaught JavaScript errors")
        finally:
            self.context.close()

    def esperar_carga(self):
        """La pantalla de carga bloquea el scroll hasta que la página está lista."""
        self.page.wait_for_function(
            "document.documentElement.classList.contains('listo')", timeout=8000
        )

    def gallery(self, progress=0.44):
        # Un ajuste de scroll del navegador (anclaje, foco) puede mover la página justo
        # después de saltar: se reintenta el salto antes de dar la espera por fallida.
        for intento in range(4):
            self.page.evaluate(
                """p => {
                  const runway = document.querySelector('#gallery-runway');
                  scrollTo({top:runway.getBoundingClientRect().top+scrollY+
                    (runway.offsetHeight-innerHeight)*p, behavior:'instant'});
                }""",
                progress,
            )
            try:
                self.page.wait_for_function(
                    "p => Math.abs(galleryProgress - p) < .002", arg=progress,
                    timeout=4000 if intento < 3 else 30000,
                )
                return
            except Exception:
                if intento == 3:
                    raise

    def nuevo_contexto(self, **opciones):
        self.context.close()
        self.context = self.browser.new_context(**{"viewport": {"width": 1440, "height": 900}, **opciones})
        self.page = self.context.new_page()
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.route("**/*", lambda route: route.continue_()
                        if urlsplit(route.request.url).hostname == "127.0.0.1" else route.abort())
        self.page.goto(self.base_url, wait_until="networkidle")
        self.esperar_carga()

    def intro(self, progress):
        self.page.evaluate(
            """p => {
              const intro = document.querySelector('#inicio');
              scrollTo({top: intro.getBoundingClientRect().top + scrollY +
                (intro.offsetHeight - innerHeight) * p, behavior: 'instant'});
            }""",
            progress,
        )
        self.page.wait_for_function("p => Math.abs(introProgress - p) < .003", arg=progress)
        self.page.wait_for_timeout(60)

    def archive(self):
        self.page.locator("#archive-index").scroll_into_view_if_needed()
        self.page.wait_for_timeout(100)

    def test_closed_eye_and_tear_offer_an_unobstructed_photo(self):
        self.gallery()
        eye = self.page.locator("#toggle-overlay")
        arrows = self.page.locator(".feature-controls .circle-button")
        original_width = arrows.first.bounding_box()["width"]
        eye.click()
        self.assertEqual(eye.get_attribute("aria-pressed"), "true")
        self.page.wait_for_function(
            """() => ['.featured-titles', '#fullscreen-specs'].every(selector =>
                Number(getComputedStyle(document.querySelector(selector)).opacity) < .01)"""
        )
        self.page.wait_for_function(
            "getComputedStyle(document.querySelector('#toggle-overlay')).backgroundColor === 'rgba(0, 0, 0, 0)'"
        )
        self.assertEqual(eye.evaluate("el => getComputedStyle(el).backgroundColor"), "rgba(0, 0, 0, 0)")
        self.assertEqual(eye.evaluate("el => getComputedStyle(el).backdropFilter"), "none")
        self.page.wait_for_function(
            """() => Number(getComputedStyle(document.querySelector('.eye-closed')).opacity) > .9 &&
                Number(getComputedStyle(document.querySelector('.eye-open')).opacity) < .01"""
        )
        self.assertLess(arrows.first.bounding_box()["width"], original_width)
        self.assertTrue(arrows.evaluate_all(
            "buttons => buttons.every(el => getComputedStyle(el).backgroundColor === 'rgba(0, 0, 0, 0)')"
        ))
        self.assertTrue(self.page.locator("#tear-trigger").is_visible())
        normal_photo = self.page.locator("#featured").bounding_box()
        self.page.locator("#tear-trigger").hover()
        self.page.wait_for_function("document.body.classList.contains('photo-only')")
        # The controls fade while the photograph grows, without leaving the mode
        # when the enlarged photograph moves the droplet away from the pointer.
        self.page.wait_for_function("""() => {
            const opacity = Number(getComputedStyle(document.querySelector('.site-header')).opacity);
            return opacity > .05 && opacity < .95;
        }""")
        middle_photo = self.page.locator("#featured").bounding_box()
        self.assertGreater(middle_photo["height"], normal_photo["height"])
        self.page.wait_for_function("purePhotoBlend === 1")
        self.page.wait_for_function("Number(getComputedStyle(document.querySelector('.site-header')).opacity) < .01")
        self.assertIn("photo-only", self.page.locator("body").get_attribute("class"))
        large_photo = self.page.locator("#featured").bounding_box()
        self.assertGreater(large_photo["height"], normal_photo["height"] * 1.1)
        self.assertLess(middle_photo["height"], large_photo["height"])
        hidden = self.page.evaluate(
            """() => ['#toggle-overlay', '.feature-controls', '.site-header', '.cursor-mira'].every(selector => {
                let el = document.querySelector(selector), opacity = 1;
                while (el) {
                    const style = getComputedStyle(el);
                    if (style.visibility === 'hidden' || style.display === 'none') return true;
                    opacity *= Number(style.opacity);
                    el = el.parentElement;
                }
                return opacity < .01;
            })"""
        )
        self.assertTrue(hidden, "Only the photograph and its outside navigation hint should remain visible")
        self.assertEqual(self.page.locator("#tear-trigger").evaluate("el => getComputedStyle(el).cursor"), "none")
        # Sin indicaciones visibles: la ayuda de navegación queda para lectores de pantalla.
        hint = self.page.locator(".photo-navigation-hint")
        self.assertEqual(hint.text_content(), "Para navegar, usar flechas o las teclas A/D")
        self.assertLessEqual(hint.evaluate("el => el.getBoundingClientRect().width"), 1)
        source = self.page.locator("#featured-image").get_attribute("src")
        self.page.keyboard.press("d")
        self.assertNotEqual(self.page.locator("#featured-image").get_attribute("src"), source)
        self.page.keyboard.press("A")
        self.assertEqual(self.page.locator("#featured-image").get_attribute("src"), source)
        # Even a one-pixel move restores the previous mode, wherever the drop is.
        pointer = self.page.evaluate("purePhotoPointer")
        self.page.mouse.move(pointer["x"] + 1, pointer["y"])
        self.page.wait_for_function("!document.body.classList.contains('photo-only')")
        self.page.wait_for_function("""() => {
            const opacity = Number(getComputedStyle(document.querySelector('.site-header')).opacity);
            return opacity > .05 && opacity < .95;
        }""")
        self.page.wait_for_function("purePhotoBlend === 0")
        self.page.wait_for_function("Number(getComputedStyle(document.querySelector('.site-header')).opacity) > .99")
        restored = self.page.locator("#featured").bounding_box()
        self.assertAlmostEqual(restored["height"], normal_photo["height"], delta=1)
        self.assertNotEqual(self.page.locator("body").evaluate("el => getComputedStyle(el).cursor"), "none")
        self.assertEqual(eye.get_attribute("aria-pressed"), "true")
        eye.click()
        self.assertEqual(eye.get_attribute("aria-pressed"), "false")
        self.page.wait_for_function("Number(getComputedStyle(document.querySelector('.featured-titles')).opacity) > .9")

    def test_photo_only_mode_restores_controls_when_leaving_the_viewer(self):
        self.gallery()
        self.page.locator("#toggle-overlay").click()
        tear = self.page.locator("#tear-trigger")
        for exit_mode in ("Tab", "blur", "scroll", "Escape"):
            with self.subTest(exit=exit_mode):
                self.gallery()
                self.page.mouse.move(5, 5)
                # La foto termina de volver de su modo anterior antes de buscar la gota.
                self.page.wait_for_function("purePhotoBlend === 0")
                tear.wait_for(state="visible")
                tear.hover()
                self.page.wait_for_function("document.body.classList.contains('photo-only')")
                if exit_mode == "blur":
                    self.page.evaluate("window.dispatchEvent(new Event('blur'))")
                elif exit_mode == "scroll":
                    self.gallery(.82)
                else:
                    self.page.keyboard.press(exit_mode)
                self.page.wait_for_function("!document.body.classList.contains('photo-only')")
                self.assertNotEqual(self.page.locator("body").evaluate("el => getComputedStyle(el).cursor"), "none")
                self.assertEqual(self.page.locator("#toggle-overlay").get_attribute("aria-pressed"), "true")
        self.page.wait_for_function("document.querySelector('#archive-index').getBoundingClientRect().top < innerHeight")

    def test_photo_letter_navigation_ignores_inputs_and_shortcuts(self):
        self.gallery()
        source = self.page.locator("#featured-image").get_attribute("src")
        self.page.keyboard.press("D")
        self.assertNotEqual(self.page.locator("#featured-image").get_attribute("src"), source)
        self.page.keyboard.press("a")
        self.assertEqual(self.page.locator("#featured-image").get_attribute("src"), source)
        self.page.keyboard.press("Control+ArrowRight")
        self.assertEqual(self.page.locator("#featured-image").get_attribute("src"), source)
        self.page.evaluate("""() => {
            const input = document.createElement('input');
            input.id = 'navigation-test-input';
            input.style.cssText = 'position:fixed;top:100px;left:10px;z-index:999';
            document.body.append(input);
            input.focus();
        }""")
        self.page.keyboard.press("d")
        self.page.keyboard.press("ArrowRight")
        self.assertEqual(self.page.locator("#navigation-test-input").input_value(), "d")
        self.assertEqual(self.page.locator("#featured-image").get_attribute("src"), source)

    def test_touch_and_reduced_motion_can_use_the_closed_eye(self):
        self.context.close()
        self.context = self.browser.new_context(
            viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True,
            reduced_motion="reduce",
        )
        self.page = self.context.new_page()
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.route("**/*", lambda route: route.continue_()
                        if urlsplit(route.request.url).hostname == "127.0.0.1" else route.abort())
        self.page.goto(self.base_url, wait_until="networkidle")
        self.esperar_carga()
        self.gallery()
        eye = self.page.locator("#toggle-overlay")
        eye.tap()
        self.assertEqual(eye.get_attribute("aria-pressed"), "true")
        tear = self.page.locator("#tear-trigger")
        # El toque llega con retraso en móvil: esperar la gota evita que Playwright
        # desplace la página (y cambie el recorrido) mientras reintenta.
        tear.wait_for(state="visible")
        tear.tap()
        self.page.wait_for_function("document.body.classList.contains('photo-only')")
        tear.tap()
        self.page.wait_for_function("!document.body.classList.contains('photo-only')")
        before = self.page.locator("#featured-image").get_attribute("src")
        self.page.locator("#next-photo").tap()
        self.assertNotEqual(self.page.locator("#featured-image").get_attribute("src"), before)
        # Wait for the next photograph's framing before tapping its moving eye.
        self.page.wait_for_function("""() => {
            const image = document.querySelector('#featured-image-full');
            const box = image.getBoundingClientRect();
            return image.complete && image.naturalWidth > 0 &&
                Math.abs(box.width / box.height - image.naturalWidth / image.naturalHeight) < .002;
        }""")
        eye.tap()
        self.assertEqual(eye.get_attribute("aria-pressed"), "false")
        self.assertEqual(self.page.evaluate("document.documentElement.scrollWidth"), 390)

    def test_only_contact_has_a_visible_section_title(self):
        visibles = self.page.evaluate("""() => [...document.querySelectorAll('h2')]
            .filter(el => {
                const style = getComputedStyle(el), box = el.getBoundingClientRect();
                return style.display !== 'none' && style.visibility !== 'hidden' &&
                    box.width > 1 && box.height > 1 && !el.closest('.sr-only');
            })
            .map(el => el.textContent.trim())""")
        self.assertEqual(visibles, ["Contacto"])
        titulos = self.page.evaluate("""() => [...document.querySelectorAll('h1, h2, h3, nav a')]
            .filter(el => el.getBoundingClientRect().width > 1 && !el.closest('.sr-only'))
            .map(el => el.textContent.trim().replace(/[.:]$/, '').toLowerCase())""")
        for palabra in ("fotografía", "fotografías", "cine", "trayectoria", "sobre mí"):
            self.assertNotIn(palabra, titulos)

    def test_loader_finishes_and_unlocks_scroll(self):
        self.assertEqual(self.page.locator(".carga").count(), 1)
        inicio = self.page.evaluate("performance.now()")
        self.page.reload(wait_until="domcontentloaded")
        self.esperar_carga()
        self.assertLess(self.page.evaluate("performance.now()"), 7000)
        self.page.wait_for_function(
            "getComputedStyle(document.querySelector('.carga')).visibility === 'hidden'"
        )
        self.page.evaluate("scrollTo({top: 600, behavior: 'instant'})")
        self.page.wait_for_function("scrollY > 0")

    def test_loader_survives_a_missing_tv_image(self):
        for imagen in ("**/recursos/tv.webp", "**/recursos/tv-movil.webp"):
            self.page.route(imagen, lambda route: route.fulfill(status=404, body="missing"))
        self.page.reload(wait_until="networkidle")
        self.esperar_carga()
        self.assertEqual(self.page.locator(".carga").count(), 1)
        self.assertTrue(self.page.evaluate("document.querySelector('.tv').classList.contains('encendido')"))

    def test_tv_knob_changes_channel(self):
        canal = self.page.locator(".tv-canal")
        antes = canal.get_attribute("src")
        self.page.locator(".tv-perilla").click()
        self.page.wait_for_function(
            "src => document.querySelector('.tv-canal').getAttribute('src') !== src", arg=antes
        )
        self.assertEqual(self.page.evaluate("canalActual"), 1)

    def test_intro_reveals_name_and_summary(self):
        opacidad = "el => getComputedStyle(el).opacity"
        self.intro(0)
        self.assertEqual(self.page.locator(".tv-capa").evaluate(opacidad), "1")
        self.intro(0.7)
        self.assertEqual(self.page.locator(".tv-capa").evaluate(opacidad), "0")
        nombre = self.page.locator("#nombre").bounding_box()
        self.assertGreaterEqual(nombre["y"], 0)
        self.assertLessEqual(nombre["y"] + nombre["height"], 900)
        self.assertEqual(self.page.evaluate(
            "getComputedStyle(document.querySelector('.intro-escena')).getPropertyValue('--resumen').trim()"), "1")
        self.intro(1)
        self.assertNotEqual(self.page.locator(".retrato-capa").evaluate("el => getComputedStyle(el).clipPath"), "none")

    def test_intro_states_reverse_cleanly(self):
        leer = """() => {
            const estilo = getComputedStyle(document.querySelector('.intro-escena'));
            return ['--zoom', '--fundido', '--nombre', '--resumen', '--liquido']
              .map(nombre => estilo.getPropertyValue(nombre).trim())
              .concat([document.querySelector('#nombre').getBoundingClientRect().top.toFixed(1),
                       getComputedStyle(document.querySelector('.tv-capa')).opacity]);
        }"""
        self.intro(0.7)
        antes = self.page.evaluate(leer)
        self.intro(0.1)
        self.intro(0.7)
        self.assertEqual(self.page.evaluate(leer), antes)

    def test_reduced_motion_intro_is_static(self):
        self.context.close()
        self.context = self.browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        self.page = self.context.new_page()
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.route("**/*", lambda route: route.continue_()
                        if urlsplit(route.request.url).hostname == "127.0.0.1" else route.abort())
        self.page.goto(self.base_url, wait_until="networkidle")
        self.esperar_carga()
        self.assertNotEqual(self.page.locator(".intro-escena").evaluate("el => getComputedStyle(el).position"), "sticky")
        for selector in ("#nombre", ".resumen"):
            with self.subTest(selector=selector):
                elemento = self.page.locator(selector)
                elemento.scroll_into_view_if_needed()
                self.assertTrue(elemento.is_visible())
                self.assertEqual(elemento.evaluate("el => getComputedStyle(el).opacity"), "1")

    def test_ink_darkens_down_the_page(self):
        valores = self.page.evaluate("""() => [
            tintaPara({intro: 1, galeria: 0, cineTop: 5000, alto: 900}),
            tintaPara({intro: 1, galeria: 0.44, cineTop: 5000, alto: 900}),
            tintaPara({intro: 1, galeria: 1, cineTop: 5000, alto: 900}),
            tintaPara({intro: 1, galeria: 1, cineTop: 0, alto: 900}),
        ]""")
        for obtenido, esperado in zip(valores, (0.35, 0.62, 0.82, 1.0)):
            self.assertAlmostEqual(obtenido, esperado, places=2)
        self.assertEqual(valores, sorted(valores))

    def test_liquid_falls_back_without_webgl(self):
        self.page.add_init_script("""(() => {
            const original = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function (tipo, ...resto) {
                return /webgl/i.test(tipo) ? null : original.call(this, tipo, ...resto);
            };
        })()""")
        self.page.reload(wait_until="networkidle")
        self.esperar_carga()
        self.assertTrue(self.page.evaluate("document.documentElement.classList.contains('sin-webgl')"))
        self.assertIn("liquido.jpg", self.page.locator("#liquido").evaluate("el => getComputedStyle(el).backgroundImage"))

    def test_side_photos_float_and_turn(self):
        self.gallery(0.02)
        flotan = self.page.locator(".side-image").evaluate_all(
            "els => els.map(el => el.getAnimations().some(a => a.animationName === 'flotar'))")
        self.assertTrue(flotan)
        self.assertTrue(all(flotan))
        self.page.locator(".side-slot").first.hover()
        self.page.wait_for_function("document.querySelector('.side-slot').classList.contains('is-girando')")

    def test_reduced_motion_photos_stay_still(self):
        self.nuevo_contexto(reduced_motion="reduce")
        self.gallery(0.02)
        self.assertTrue(self.page.locator(".side-image").evaluate_all(
            "els => els.length > 0 && els.every(el => el.getAnimations().length === 0)"))

    def test_collection_index_has_no_counts_or_numbers(self):
        self.archive()
        filas = self.page.locator(".collection-row").evaluate_all("els => els.map(el => el.innerText)")
        self.assertTrue(filas)
        for fila in filas:
            with self.subTest(fila=fila):
                self.assertNotRegex(fila, r"\bfotos\b")
                self.assertNotRegex(fila, r"^\s*\d{2}\b")

    def test_films_show_year_duration_and_credit(self):
        esperados = self.page.evaluate("peliculas.map(p => [p.anio, p.duracion, p.credito].join(' · '))")
        self.assertTrue(esperados)
        datos = self.page.locator(".pelicula-datos").evaluate_all("els => els.map(el => el.textContent.trim())")
        self.assertEqual(datos, esperados)

    def test_video_embeds_only_when_available(self):
        self.assertEqual(self.page.locator(".pelicula-ver").count(), 0)
        self.page.evaluate("peliculas[0].video = 'https://youtu.be/abc123'; renderPeliculas()")
        boton = self.page.locator(".pelicula-ver").first
        boton.scroll_into_view_if_needed()
        boton.click()
        self.assertEqual(self.page.locator(".pelicula iframe").first.get_attribute("src"),
                         "https://www.youtube-nocookie.com/embed/abc123?autoplay=1")
        self.assertEqual(self.page.evaluate("urlIncrustada('https://www.youtube.com/watch?v=xyz9')"),
                         "https://www.youtube-nocookie.com/embed/xyz9?autoplay=1")
        self.assertEqual(self.page.evaluate("urlIncrustada('https://vimeo.com/76979871')"),
                         "https://player.vimeo.com/video/76979871?autoplay=1")
        self.assertIsNone(self.page.evaluate("urlIncrustada('https://example.com/video')"))

    def test_featured_film_opens_with_scroll(self):
        apertura = "getComputedStyle(document.querySelector('.pelicula-destacada')).getPropertyValue('--apertura').trim()"
        mover = """f => { const marco = document.querySelector('.pelicula-destacada .pelicula-marco');
            scrollTo({top: marco.getBoundingClientRect().top + scrollY - innerHeight * f, behavior: 'instant'}); }"""
        self.page.evaluate(mover, 0.97)
        self.page.wait_for_timeout(120)
        self.assertEqual(self.page.evaluate(apertura), "0")
        self.page.evaluate(mover, 0.3)
        self.page.wait_for_function(f"{apertura} === '1'")

    def test_career_filters_and_rows(self):
        self.page.locator("#trayectoria").scroll_into_view_if_needed()
        filas = self.page.locator(".fila")
        total = filas.count()
        self.assertGreater(total, 2)
        direccion = self.page.get_by_role("button", name="Dirección", exact=True)
        direccion.click()
        self.assertEqual(direccion.get_attribute("aria-pressed"), "true")
        roles = self.page.locator(".entrada:not([hidden])").evaluate_all("els => els.map(el => el.dataset.rol)")
        self.assertTrue(roles)
        self.assertTrue(all(rol == "direccion" for rol in roles))
        self.page.get_by_role("button", name="Todo", exact=True).click()
        self.assertEqual(self.page.locator(".entrada:not([hidden])").count(), total)
        fila = filas.first
        detalle = self.page.locator("#" + fila.get_attribute("aria-controls"))
        self.assertEqual(fila.get_attribute("aria-expanded"), "false")
        fila.click()
        self.assertEqual(fila.get_attribute("aria-expanded"), "true")
        self.assertTrue(detalle.is_visible())
        fila.click()
        self.assertEqual(fila.get_attribute("aria-expanded"), "false")
        self.assertFalse(detalle.is_visible())
        self.assertGreater(self.page.locator(".enlace[aria-disabled='true']").count(), 0)

    def test_channel_static_peaks_at_the_career_border(self):
        opacidad = "Number(getComputedStyle(document.querySelector('.estatica')).opacity)"
        mover = """f => { const seccion = document.querySelector('#trayectoria');
            scrollTo({top: seccion.getBoundingClientRect().top + scrollY - innerHeight * f, behavior: 'instant'}); }"""
        self.page.evaluate(mover, 0.5)
        self.page.wait_for_function(f"Math.abs({opacidad} - .55) < .02")
        self.page.evaluate(mover, 1.3)
        self.page.wait_for_function(f"{opacidad} < .01")

    def test_contact_form_sends_and_reports(self):
        envios = []
        estado = {"codigo": 200}

        def responder(route):
            envios.append(route.request)
            route.fulfill(status=estado["codigo"], content_type="application/json",
                          body='{"success":"true","message":"ok"}' if estado["codigo"] == 200 else '{"success":"false"}')

        self.page.route("https://formsubmit.co/**", responder)
        self.page.locator(".contacto-form").scroll_into_view_if_needed()
        enviar = self.page.locator(".contacto-enviar")
        enviar.click()
        self.page.wait_for_timeout(200)
        self.assertEqual(envios, [], "Un formulario vacío no se envía")

        def completar():
            self.page.fill("input[name=nombre]", "Ana")
            self.page.fill("input[name=email]", "ana@example.com")
            self.page.fill("textarea[name=mensaje]", "Hola")

        completar()
        enviar.click()
        self.page.wait_for_function("document.querySelector('.contacto-estado').textContent.includes('Mensaje enviado')")
        self.assertEqual(len(envios), 1)
        self.assertEqual(envios[0].url, "https://formsubmit.co/ajax/benbravod@gmail.com")
        cuerpo = envios[0].post_data_json
        self.assertEqual((cuerpo["nombre"], cuerpo["email"], cuerpo["mensaje"]), ("Ana", "ana@example.com", "Hola"))
        self.assertNotIn("_honey", cuerpo)
        self.assertEqual(self.page.input_value("input[name=nombre]"), "")
        self.assertFalse(enviar.is_disabled())

        estado["codigo"] = 500
        completar()
        enviar.click()
        self.page.wait_for_function("document.querySelector('.contacto-estado a[href=\"mailto:benbravod@gmail.com\"]') !== null")
        self.assertEqual(self.page.input_value("input[name=nombre]"), "Ana", "Un error no borra lo escrito")

    def test_contact_room_lights_up_from_the_lamp(self):
        luz = "getComputedStyle(document.querySelector('#contacto')).getPropertyValue('--luz').trim()"
        mover = """f => { const seccion = document.querySelector('#contacto');
            scrollTo({top: seccion.getBoundingClientRect().top + scrollY - innerHeight * f, behavior: 'instant'}); }"""
        self.page.evaluate(mover, 0.98)
        self.page.wait_for_timeout(120)
        self.assertEqual(self.page.evaluate(luz), "0")
        self.page.evaluate(mover, 0.2)
        self.page.wait_for_function(f"{luz} === '1'")

    def test_catalog_and_resources(self):
        catalog = self.page.evaluate("colecciones")
        self.assertTrue(catalog)
        self.assertEqual(len({item["id"] for item in catalog}), len(catalog))
        photos = set()
        for collection in catalog:
            self.assertTrue(collection["fotos"], collection["id"])
            photos.update(photo["archivo"] for photo in collection["fotos"])
        resources = photos | {
            "index.html", "style.css", "script.js", "colecciones.js", "perfil.jpg",
            "intro.js", "liquido.js", "secciones.js", "cursor.js", "peliculas.js", "trayectoria.js",
            "recursos/tv.webp", "recursos/tv-movil.webp", "recursos/retrato.jpg",
            "recursos/retrato-movil.jpg", "recursos/carga.jpg", "recursos/carta-ajuste.png",
            "recursos/textura-negro.jpg", "recursos/textura-crema.jpg", "recursos/textura-rojo.jpg",
            "recursos/fondo-tv.jpg", "recursos/liquido.jpg",
        }
        for filename in sorted(resources):
            with self.subTest(resource=filename):
                self.assertTrue((ROOT / filename).is_file())
                response = self.page.request.get(self.base_url + "/" + filename)
                self.assertEqual(response.status, 200)
                self.assertEqual(response.body(), (ROOT / filename).read_bytes())
        self.assertIn("Benjamín Bravo", self.page.title())

    def test_pagination_and_year_filters(self):
        catalog = self.page.evaluate("colecciones")
        self.archive()
        self.assertEqual(self.page.locator(".collection-row").count(), min(5, len(catalog)))
        self.page.locator("#page-next").click()
        total_pages = (len(catalog) + 4) // 5
        self.assertEqual(self.page.locator("#page-count").inner_text(), f"02 / {total_pages:02d}")
        self.assertEqual(self.page.locator(".collection-row").count(), min(5, len(catalog) - 5))
        for year in ("2025", "2026"):
            matching = [item for item in catalog if str(item["anio"]) == year]
            self.page.get_by_role("button", name=year, exact=True).click()
            self.assertEqual(self.page.locator(".collection-row").count(), min(5, len(matching)))
            self.assertEqual(self.page.locator("#page-next").is_disabled(), len(matching) <= 5)
            self.assertEqual(self.page.get_by_role("button", name=year, exact=True).get_attribute("aria-pressed"), "true")
            self.assertEqual(self.page.evaluate("String(colecciones[serieActual].anio)"), year)

    def test_photo_arrows_keyboard_and_expanded_animation(self):
        self.gallery()
        self.assertIn("is-expanded", self.page.locator("#gallery-sticky").get_attribute("class"))
        self.page.locator("#next-photo").click()
        self.assertTrue(self.page.locator("#featured-image").get_attribute("src").endswith("DR-2.jpg"))
        self.assertGreater(self.page.locator("#featured-image-full").evaluate("el => el.getAnimations().length"), 0)
        self.page.wait_for_function("document.querySelectorAll('.photo-slide-ghost').length === 0")
        self.assertEqual(self.page.locator("#featured-image-full").evaluate("el => el.getAnimations().length"), 0)
        self.page.locator("#prev-photo").click()
        self.page.keyboard.press("ArrowLeft")
        self.assertTrue(self.page.locator("#featured-image").get_attribute("src").endswith("DR-13.jpg"))
        self.page.keyboard.press("ArrowRight")
        self.assertTrue(self.page.locator("#featured-image").get_attribute("src").endswith("DR-1.jpg"))
        self.page.wait_for_function("document.querySelectorAll('.photo-slide-ghost').length === 0")

    def test_showcase_swap_and_off_page_selection(self):
        self.archive()
        side = self.page.locator('.showcase-card:not(.showcase-center)').first
        chosen = side.get_attribute("data-collection")
        title = self.page.evaluate("index => colecciones[Number(index)].titulo", chosen)
        side.click()
        self.page.wait_for_function("!showcaseBusy")
        self.assertEqual(self.page.locator("#featured-photo-title").inner_text(), title)
        self.assertEqual(self.page.locator(".showcase-ghost").count(), 0)
        self.page.locator("#page-next").click()
        target = self.page.locator(".collection-row").last
        expected = target.locator("strong").inner_text()
        target.click()
        self.page.wait_for_function("!showcaseBusy")
        self.assertEqual(self.page.locator("#featured-photo-title").inner_text(), expected)
        self.assertEqual(self.page.locator(".collection-row[aria-pressed=true]").count(), 1)
        self.page.locator("#page-prev").click()
        target = self.page.locator(".collection-row").last
        chosen = target.get_attribute("data-collection")
        self.assertFalse(self.page.evaluate("index => showcaseSlots.includes(Number(index))", chosen))
        expected = target.locator("strong").inner_text()
        target.click()
        self.page.wait_for_function("!showcaseBusy")
        self.assertEqual(self.page.locator("#featured-photo-title").inner_text(), expected)

    def test_filter_cancels_pending_showcase_swap(self):
        expected = self.page.evaluate("colecciones.find(item => String(item.anio) === '2025').titulo")
        self.archive()
        self.page.locator('.showcase-card:not(.showcase-center)').first.click()
        self.assertTrue(self.page.evaluate("showcaseBusy"))
        self.page.get_by_role("button", name="2025", exact=True).click()
        self.page.wait_for_timeout(1100)
        self.assertEqual(self.page.locator("#featured-photo-title").inner_text(), expected)
        self.assertEqual(self.page.get_by_role("button", name="2025", exact=True).get_attribute("aria-pressed"), "true")
        self.assertEqual(self.page.locator(".showcase-ghost").count(), 0)
        self.assertEqual(self.page.locator(".is-switching").count(), 0)

    def test_missing_photo_fallback_and_recovery(self):
        self.page.route("**/DR-1.jpg", lambda route: route.fulfill(status=404, body="missing"))
        self.page.reload(wait_until="networkidle")
        self.esperar_carga()
        self.page.wait_for_function("document.querySelector('#featured-fallback').classList.contains('is-visible')")
        self.assertIn("is-missing", self.page.locator("#featured-image").get_attribute("class") or "")
        self.assertIn("is-missing", self.page.locator("#featured-image-full").get_attribute("class") or "")
        self.gallery()
        self.assertEqual(self.page.locator("#featured-fallback").evaluate("el => getComputedStyle(el).opacity"), "1")
        self.assertEqual(self.page.locator("#featured-image-full").evaluate("el => getComputedStyle(el).opacity"), "0")
        self.page.locator("#next-photo").click()
        self.page.wait_for_function("!document.querySelector('#featured-fallback').classList.contains('is-visible')")
        self.page.wait_for_function("document.querySelector('#featured-image-full').naturalWidth > 0")
        self.assertNotIn("is-missing", self.page.locator("#featured-image-full").get_attribute("class") or "")

    def test_hidden_gallery_controls_are_inert(self):
        self.gallery()
        self.assertTrue(self.page.locator(".side-slot").evaluate_all("slots => slots.every(el => el.inert)"))
        self.assertFalse(self.page.locator(".feature-controls").evaluate("el => el.inert"))
        self.gallery(0.8)
        self.assertTrue(self.page.locator(".feature-controls").evaluate("el => el.inert"))
        self.gallery(1)
        self.assertTrue(self.page.locator("#featured").evaluate("el => el.inert"))

    def test_viewer_rejoins_the_real_collection_index(self):
        self.gallery()
        self.page.locator("#next-photo").click()
        self.page.wait_for_function("document.querySelectorAll('.photo-slide-ghost').length === 0")
        self.gallery(0.94)
        center = self.page.locator(".showcase-center")
        self.assertEqual(center.evaluate("el => getComputedStyle(el).visibility"), "hidden")
        self.assertEqual(self.page.locator("#featured").evaluate("el => getComputedStyle(el).opacity"), "1")
        self.gallery(0.96)
        alignment = self.page.evaluate("""() => {
          const photo = document.querySelector('#featured').getBoundingClientRect();
          const center = document.querySelector('.showcase-center').getBoundingClientRect();
          return ['left', 'top', 'width', 'height'].map(key => Math.abs(photo[key] - center[key]));
        }""")
        self.assertLess(max(alignment), 0.1, "Viewer must meet the actual index card without jumping")
        self.assertEqual(self.page.locator("#featured").evaluate("el => getComputedStyle(el).opacity"), "0")
        self.assertTrue(center.is_visible())
        self.assertTrue(center.locator("img").get_attribute("src").endswith("DR-2.jpg"))
        self.assertEqual(self.page.locator(".showcase-gallery").count(), 1)
        self.assertEqual(self.page.locator(".handoff-preview").count(), 0)
        center.click()
        self.page.wait_for_function("Math.abs(galleryProgress - .44) < .002")
        self.assertEqual(self.page.locator("#featured").evaluate("el => getComputedStyle(el).opacity"), "1")
        self.assertEqual(center.evaluate("el => getComputedStyle(el).visibility"), "hidden")

    def assert_single_photo_pixels(self):
        screenshot = base64.b64encode(self.page.screenshot()).decode()
        difference = self.page.evaluate("""async encoded => {
            const shot = new Image();
            shot.src = 'data:image/png;base64,' + encoded;
            await shot.decode();
            const actual = document.createElement('canvas');
            actual.width = innerWidth; actual.height = innerHeight;
            const observed = actual.getContext('2d');
            observed.drawImage(shot, 0, 0);
            const photo = document.querySelector('#featured-image-full');
            const box = photo.getBoundingClientRect();
            const expected = document.createElement('canvas');
            expected.width = innerWidth; expected.height = innerHeight;
            const reference = expected.getContext('2d');
            const scale = Math.max(box.width / photo.naturalWidth, box.height / photo.naturalHeight);
            const width = photo.naturalWidth * scale, height = photo.naturalHeight * scale;
            reference.drawImage(photo, box.left + (box.width - width)/2,
                box.top + (box.height - height)/2, width, height);
            let total = 0, samples = 0;
            for (const u of [.12, .26, .4, .55, .69, .84]) {
                for (const v of [.13, .29, .47, .65, .83]) {
                    const x = Math.floor(box.left + box.width * u);
                    const y = Math.floor(box.top + box.height * v);
                    if (x < 1 || y < 1 || x >= innerWidth-1 || y >= innerHeight-1) continue;
                    const a = observed.getImageData(x, y, 1, 1).data;
                    const b = reference.getImageData(x, y, 1, 1).data;
                    total += Math.abs(a[0]-b[0]) + Math.abs(a[1]-b[1]) + Math.abs(a[2]-b[2]);
                    samples += 3;
                }
            }
            return { samples, mean: total / Math.max(1, samples) };
        }""", screenshot)
        self.assertGreater(difference["samples"], 12)
        self.assertLess(difference["mean"], 3, "Visible pixels must match one cover image without a second framing")

    def test_scroll_draws_one_photo_through_growth_and_return(self):
        # A high-contrast pattern makes two superposed scales visibly different.
        pattern = self.page.evaluate("""() => {
            const canvas = document.createElement('canvas');
            canvas.width = 600; canvas.height = 400;
            const context = canvas.getContext('2d');
            context.fillStyle = '#17456b'; context.fillRect(0, 0, 600, 400);
            context.fillStyle = '#e38c2c';
            for (let x = 0; x < 600; x += 150) context.fillRect(x, 0, 75, 400);
            context.fillStyle = '#eeeeee'; context.beginPath();
            context.arc(300, 200, 96, 0, Math.PI*2); context.fill();
            context.strokeStyle = '#8b2034'; context.lineWidth = 28;
            context.beginPath(); context.moveTo(0, 70); context.lineTo(600, 330);
            context.moveTo(0, 330); context.lineTo(600, 70); context.stroke();
            return canvas.toDataURL('image/png').split(',')[1];
        }""")
        self.page.route("**/DR-1.jpg", lambda route: route.fulfill(
            status=200, content_type="image/png", body=base64.b64decode(pattern)))
        self.page.reload(wait_until="networkidle")
        self.esperar_carga()
        self.page.add_style_tag(content="""
            .featured-lower, .eye-control, .fullscreen-specs, .gallery-instructions,
            .site-header, #archive-index { visibility:hidden !important; }
            .featured-image-wrap::after { display:none !important; }
            #featured-image-full { animation:none !important; filter:none !important; }
        """)
        for width, height in ((1440, 900), (390, 844)):
            self.page.set_viewport_size({"width": width, "height": height})
            for progress in (.08, .16, .24, .44, .76, .84, .91, .84, .24, .08):
                with self.subTest(width=width, progress=progress):
                    self.gallery(progress)
                    self.assert_single_photo_pixels()
            self.gallery(.44)
            aspect = self.page.locator("#featured-image-full").evaluate(
                "el => ({ rendered:el.getBoundingClientRect().width/el.getBoundingClientRect().height, natural:el.naturalWidth/el.naturalHeight })")
            self.assertAlmostEqual(aspect["rendered"], aspect["natural"], delta=.002)

    def test_scrolling_during_photo_slide_removes_the_outgoing_layer(self):
        self.gallery()
        self.page.locator("#next-photo").click()
        self.assertEqual(self.page.locator(".photo-slide-ghost").count(), 1)
        source = self.page.locator("#featured-image-full").get_attribute("src")
        self.gallery(.2)
        self.assertEqual(self.page.locator(".photo-slide-ghost").count(), 0)
        self.assertEqual(self.page.locator("#featured-image-full").evaluate("el => el.getAnimations().length"), 0)
        self.assertEqual(self.page.locator("#featured-image-full").get_attribute("src"), source)
        self.page.add_style_tag(content="""
            .featured-lower, .eye-control, .fullscreen-specs, .gallery-instructions,
            .site-header, #archive-index { visibility:hidden !important; }
            .featured-image-wrap::after { display:none !important; }
            #featured-image-full { animation:none !important; filter:none !important; }
        """)
        self.assert_single_photo_pixels()

    def test_index_handoff_on_mobile_and_with_reduced_motion(self):
        for width in (390, 768):
            for reduced in ("reduce", "no-preference"):
                with self.subTest(width=width, reduced_motion=reduced):
                    self.page.set_viewport_size({"width": width, "height": 844})
                    self.page.emulate_media(reduced_motion=reduced)
                    self.gallery(1)
                    self.page.wait_for_function("getComputedStyle(document.querySelector('#featured')).opacity === '0'")
                    self.assertTrue(self.page.locator(".showcase-center").is_visible())
                    self.assertEqual(self.page.locator("#featured").evaluate("el => getComputedStyle(el).opacity"), "0")
                    self.assertTrue(self.page.locator("#featured").evaluate("el => el.inert"))
                    self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"), width)
                    self.gallery(0.44)
                    self.page.wait_for_function("getComputedStyle(document.querySelector('#featured')).opacity === '1'")
                    self.assertEqual(self.page.locator("#featured").evaluate("el => getComputedStyle(el).opacity"), "1")
                    self.assertEqual(self.page.locator(".showcase-center").evaluate("el => getComputedStyle(el).visibility"), "hidden")

    def test_tear_activates_after_a_continuous_mouse_approach_and_reentry(self):
        self.gallery()
        eye = self.page.locator("#toggle-overlay")
        eye.click()
        for attempt in range(2):
            with self.subTest(attempt=attempt):
                self.page.wait_for_function("purePhotoBlend === 0", timeout=1500)
                normal = self.page.locator("#featured").bounding_box()
                start = eye.bounding_box()
                drop = self.page.locator("#tear-trigger").bounding_box()
                start_x = start["x"] + start["width"] / 2
                start_y = start["y"] + start["height"] / 2
                end_x = drop["x"] + drop["width"] / 2
                end_y = drop["y"] + drop["height"] / 2
                self.page.mouse.move(start_x, start_y)
                # A person travels through the droplet's hit area before resting;
                # teleporting with locator.hover() used to hide the entry bug.
                for step in range(1, 21):
                    self.page.mouse.move(
                        start_x + (end_x - start_x) * step / 20,
                        start_y + (end_y - start_y) * step / 20,
                    )
                    self.page.wait_for_timeout(12)
                self.page.wait_for_function("purePhotoActive && purePhotoBlend === 1", timeout=1500)
                self.page.wait_for_function("Number(getComputedStyle(document.querySelector('.site-header')).opacity) < .01", timeout=1500)
                self.assertGreater(self.page.locator("#featured").bounding_box()["height"], normal["height"] * 1.1)
                self.assertEqual(self.page.locator("body").evaluate("el => getComputedStyle(el).cursor"), "none")
                self.page.wait_for_timeout(200)
                self.assertTrue(self.page.evaluate("purePhotoActive"), "Resting must preserve the enlarged photograph")
                self.page.mouse.move(end_x + 1, end_y)
                self.page.wait_for_function("!purePhotoActive && purePhotoBlend === 0", timeout=1500)
                self.page.wait_for_function("Number(getComputedStyle(document.querySelector('.site-header')).opacity) > .99", timeout=1500)
                self.assertEqual(eye.get_attribute("aria-pressed"), "true")
                self.assertNotEqual(self.page.locator("body").evaluate("el => getComputedStyle(el).cursor"), "none")
                self.page.wait_for_timeout(200)
                self.assertFalse(self.page.evaluate("purePhotoActive"), "A movement must exit without immediately reopening")

    def test_closed_eye_arrows_are_clear_and_still_navigate(self):
        self.gallery()
        self.page.locator("#toggle-overlay").click()
        arrow = self.page.locator("#next-photo")
        dimensions = arrow.evaluate("""el => ({
            hit: el.getBoundingClientRect().width,
            circle: parseFloat(getComputedStyle(el, '::before').width),
            glyph: parseFloat(getComputedStyle(el.querySelector('.arrow-glyph')).fontSize)
        })""")
        self.assertGreaterEqual(dimensions["hit"], 44)
        self.assertGreaterEqual(dimensions["circle"], 32)
        self.assertLess(dimensions["circle"], dimensions["hit"])
        self.assertGreaterEqual(dimensions["glyph"], 20)
        arrow.hover()
        self.page.wait_for_function("""width =>
            document.querySelector('#next-photo').getBoundingClientRect().width > width * 1.08
        """, arg=dimensions["hit"])
        before = self.page.locator("#featured-image-full").get_attribute("src")
        arrow.click()
        self.assertNotEqual(self.page.locator("#featured-image-full").get_attribute("src"), before)
        self.page.locator("#prev-photo").click()
        self.assertEqual(self.page.locator("#featured-image-full").get_attribute("src"), before)


if __name__ == "__main__":
    unittest.main()

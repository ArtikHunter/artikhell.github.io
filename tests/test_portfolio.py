"""Browser regression checks. Run: python3 -m unittest discover -s tests -v."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
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

    def tearDown(self):
        try:
            self.assertEqual(self.errors, [], "Uncaught JavaScript errors")
        finally:
            self.context.close()

    def gallery(self, progress=0.44):
        self.page.evaluate(
            """p => {
              const runway = document.querySelector('#gallery-runway');
              scrollTo({top:runway.getBoundingClientRect().top+scrollY+
                (runway.offsetHeight-innerHeight)*p, behavior:'instant'});
            }""",
            progress,
        )
        self.page.wait_for_function(
            "p => Math.abs(galleryProgress - p) < .002", arg=progress
        )

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
        self.page.locator("#tear-trigger").hover()
        self.page.wait_for_function("document.body.classList.contains('photo-only')")
        self.page.wait_for_timeout(400)
        # Keeping the invisible droplet's hit area preserves hover without flicker.
        self.assertIn("photo-only", self.page.locator("body").get_attribute("class"))
        hidden = self.page.evaluate(
            """() => ['#toggle-overlay', '.feature-controls', '.site-header', '.cursor-halo'].every(selector => {
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
        hint = self.page.locator(".photo-navigation-hint")
        self.assertEqual(hint.inner_text(), "Para navegar, usar flechas o las teclas A/D")
        self.assertTrue(hint.is_visible())
        photo = self.page.locator("#featured-image-full").bounding_box()
        note = hint.bounding_box()
        overlap = min(photo["x"] + photo["width"], note["x"] + note["width"]) - max(photo["x"], note["x"])
        self.assertLessEqual(overlap, 1, "Navigation hint must stay beside the photograph")
        source = self.page.locator("#featured-image").get_attribute("src")
        self.page.keyboard.press("d")
        self.assertNotEqual(self.page.locator("#featured-image").get_attribute("src"), source)
        self.page.keyboard.press("A")
        self.assertEqual(self.page.locator("#featured-image").get_attribute("src"), source)
        self.page.mouse.move(5, 5)
        self.page.wait_for_function("!document.body.classList.contains('photo-only')")
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
        self.gallery()
        eye = self.page.locator("#toggle-overlay")
        eye.tap()
        self.assertEqual(eye.get_attribute("aria-pressed"), "true")
        tear = self.page.locator("#tear-trigger")
        tear.tap()
        self.page.wait_for_function("document.body.classList.contains('photo-only')")
        tear.tap()
        self.page.wait_for_function("!document.body.classList.contains('photo-only')")
        before = self.page.locator("#featured-image").get_attribute("src")
        self.page.locator("#next-photo").tap()
        self.assertNotEqual(self.page.locator("#featured-image").get_attribute("src"), before)
        eye.tap()
        self.assertEqual(eye.get_attribute("aria-pressed"), "false")
        self.assertEqual(self.page.evaluate("document.documentElement.scrollWidth"), 390)

    def test_catalog_and_resources(self):
        catalog = self.page.evaluate("colecciones")
        self.assertTrue(catalog)
        self.assertEqual(len({item["id"] for item in catalog}), len(catalog))
        photos = set()
        for collection in catalog:
            self.assertTrue(collection["fotos"], collection["id"])
            photos.update(photo["archivo"] for photo in collection["fotos"])
        resources = photos | {"index.html", "style.css", "script.js", "colecciones.js", "perfil.jpg"}
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

    def test_pointer_animation_stops_when_idle(self):
        self.page.mouse.move(720, 400)
        self.page.wait_for_function("pointerFrame === 0", timeout=5000)
        self.assertIn("is-visible", self.page.locator(".cursor-halo").get_attribute("class"))
        self.page.mouse.move(800, 450)
        self.page.wait_for_function("pointerFrame === 0", timeout=5000)
        self.assertNotEqual(self.page.locator(".cursor-halo").evaluate("el => getComputedStyle(el).transform"), "none")

    def test_motion_preference_changes_do_not_accumulate_waves(self):
        self.page.emulate_media(reduced_motion="reduce")
        self.page.reload(wait_until="networkidle")
        self.page.wait_for_function("reduceMotion.matches")
        for x in range(200, 800, 100):
            self.page.mouse.move(x, 400)
            self.page.wait_for_timeout(115)
        self.assertEqual(self.page.evaluate("waves.length"), 0)
        self.assertEqual(self.page.evaluate("wavesFrame"), 0)
        self.page.emulate_media(reduced_motion="no-preference")
        self.page.wait_for_function("!reduceMotion.matches")
        self.page.mouse.move(850, 450)
        self.page.wait_for_function("waves.length > 0")
        self.page.emulate_media(reduced_motion="reduce")
        self.page.wait_for_function("waves.length === 0 && wavesFrame === 0 && pointerFrame === 0")

    def test_mobile_menu_escape_restores_focus(self):
        self.page.set_viewport_size({"width": 390, "height": 844})
        button = self.page.locator("#menu-toggle")
        button.click()
        self.assertEqual(button.get_attribute("aria-expanded"), "true")
        self.page.locator("#mobile-menu a").first.focus()
        self.page.keyboard.press("Escape")
        self.assertEqual(button.get_attribute("aria-expanded"), "false")
        self.assertTrue(button.evaluate("el => document.activeElement === el"))
        self.assertTrue(self.page.locator("#mobile-menu").evaluate("el => el.inert"))

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


if __name__ == "__main__":
    unittest.main()

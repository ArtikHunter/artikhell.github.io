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


if __name__ == "__main__":
    unittest.main()

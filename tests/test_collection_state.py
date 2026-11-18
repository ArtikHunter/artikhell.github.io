"""Collection previews keep their explored photo and move with document scrolling."""

import unittest

import test_portfolio as portfolio


class CollectionStateTests(unittest.TestCase):
    setUpClass = classmethod(portfolio.PortfolioTests.setUpClass.__func__)
    tearDownClass = classmethod(portfolio.PortfolioTests.tearDownClass.__func__)
    setUp = portfolio.PortfolioTests.setUp
    tearDown = portfolio.PortfolioTests.tearDown
    gallery = portfolio.PortfolioTests.gallery
    archive = portfolio.PortfolioTests.archive

    def test_swapping_collections_keeps_each_explored_photo(self):
        self.gallery()
        self.page.locator("#next-photo").click()
        self.page.locator("#next-photo").click()
        first_photo = self.page.locator("#featured-image").get_attribute("src")
        self.gallery(1)
        side = self.page.locator(".showcase-card:not(.showcase-center)").first
        second_index = side.get_attribute("data-collection")
        side.click()
        self.page.wait_for_function("!showcaseBusy")
        old_card = self.page.locator('.showcase-card[data-collection="0"]')
        self.assertEqual(old_card.locator("img").get_attribute("src"), first_photo)

        self.page.locator(".showcase-center").click()
        self.page.wait_for_function("Math.abs(galleryProgress - .44) < .002")
        self.page.locator("#next-photo").click()
        second_photo = self.page.locator("#featured-image").get_attribute("src")
        self.gallery(1)
        old_card.click()
        self.page.wait_for_function("!showcaseBusy")
        self.assertEqual(self.page.locator("#featured-image").get_attribute("src"), first_photo)
        self.assertEqual(self.page.locator(".showcase-center img").get_attribute("src"), first_photo)
        second_card = self.page.locator(f'.showcase-card[data-collection="{second_index}"]')
        self.assertEqual(second_card.locator("img").get_attribute("src"), second_photo)
        second_card.click()
        self.page.wait_for_function("!showcaseBusy")
        self.assertEqual(self.page.locator("#featured-image").get_attribute("src"), second_photo)

    def test_shuffle_images_follow_scroll_during_the_animation(self):
        for off_page in (False, True):
            with self.subTest(off_page=off_page):
                self.page.set_viewport_size({"width": 390 if off_page else 1440, "height": 900})
                self.gallery(1)
                if off_page:
                    self.page.locator("#page-next").click()
                    target = self.page.locator(".collection-row").last
                else:
                    target = self.page.locator(".showcase-card:not(.showcase-center)").first
                chosen = target.get_attribute("data-collection")
                target.click()
                self.page.wait_for_function("document.querySelector('.showcase-ghost') !== null")
                # Pause time, then scroll: a frame must stay anchored to its document position.
                self.page.evaluate("""async () => {
                    const animations = document.getAnimations();
                    animations.forEach(animation => animation.pause());
                    await Promise.all(animations.map(animation => animation.ready));
                }""")
                ghost = self.page.locator(".showcase-ghost").first
                before = ghost.bounding_box()["y"]
                scroll_before = self.page.evaluate("scrollY")
                self.page.evaluate("scrollBy({top: 120, behavior: 'instant'})")
                self.page.wait_for_timeout(40)
                delta = self.page.evaluate("scrollY") - scroll_before
                self.assertGreater(delta, 0)
                self.assertAlmostEqual(ghost.bounding_box()["y"] - before, -delta, delta=1)
                self.page.evaluate("document.getAnimations().forEach(animation => animation.play())")
                self.page.wait_for_function("!showcaseBusy")
                self.assertEqual(self.page.locator(".showcase-ghost").count(), 0)
                self.assertEqual(self.page.locator(".is-switching").count(), 0)
                self.assertEqual(self.page.evaluate("String(serieActual)"), chosen)

    def test_filters_and_off_page_selection_restore_the_explored_photo(self):
        self.page.emulate_media(reduced_motion="reduce")
        self.gallery()
        self.page.locator("#next-photo").click()
        self.page.locator("#next-photo").click()
        explored = self.page.locator("#featured-image").get_attribute("src")
        self.gallery(1)
        self.page.get_by_role("button", name="2025", exact=True).click()
        self.page.get_by_role("button", name="2026", exact=True).click()
        self.assertEqual(self.page.locator("#featured-image").get_attribute("src"), explored)
        self.page.get_by_role("button", name="Todos", exact=True).click()
        self.page.locator("#page-next").click()
        self.page.locator(".collection-row").last.click()
        self.page.wait_for_function("!showcaseBusy")
        self.page.locator("#page-prev").click()
        self.page.locator('.collection-row[data-collection="0"]').click()
        self.page.wait_for_function("!showcaseBusy")
        self.assertEqual(self.page.locator("#featured-image").get_attribute("src"), explored)
        self.assertEqual(self.page.locator(".showcase-center img").get_attribute("src"), explored)

    def test_resize_finishes_shuffle_without_stale_frames(self):
        self.gallery(1)
        side = self.page.locator(".showcase-card:not(.showcase-center)").first
        chosen = side.get_attribute("data-collection")
        side.click()
        self.page.wait_for_function("showcaseBusy")
        self.page.set_viewport_size({"width": 768, "height": 900})
        self.page.wait_for_function("!showcaseBusy")
        self.assertEqual(self.page.locator(".showcase-ghost").count(), 0)
        self.assertEqual(self.page.locator(".is-switching").count(), 0)
        self.assertEqual(self.page.evaluate("String(serieActual)"), chosen)
        self.page.wait_for_timeout(1050)
        self.assertEqual(self.page.evaluate("String(serieActual)"), chosen)


if __name__ == "__main__":
    unittest.main()

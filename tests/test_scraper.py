import unittest
from animal_scraper.scraper import WikipediaScraper
from animal_scraper.image_downloader import ImageDownloader
import os


class TestWikipediaScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = WikipediaScraper()
        self.html = self.scraper.fetch_html()
        self.animals = self.scraper.parse_animals(self.html)

    def test_parse_animals_has_results(self):
        # Check that at least one animal was parsed
        self.assertGreater(len(self.animals), 0, "No animals parsed from Wikipedia page.")

    def test_collateral_adjective_association(self):
        # Check that at least one known collateral adjective is correctly matched
        match = any("feline" in animal.adjectives and "cat" in animal.name.lower() for animal in self.animals)
        self.assertTrue(match, "Expected 'feline' adjective not associated with 'cat'.")

    def test_image_downloader_returns_valid_path(self):
        # Pick one known animal and test if its image is downloaded correctly
        downloader = ImageDownloader()
        test_animal_name = "Giraffe"
        image_path = downloader.download_image(test_animal_name)
        self.assertTrue(os.path.exists(image_path), f"Image not downloaded for {test_animal_name}")
        self.assertTrue(image_path.endswith(".jpg"), "Downloaded image is not a .jpg file")

    def test_image_downloader_uses_correct_filename(self):
        downloader = ImageDownloader()
        path = downloader.download_image("Giraffe")
        self.assertTrue("giraffe" in os.path.basename(path).lower())
        self.assertTrue(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()

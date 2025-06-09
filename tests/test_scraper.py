import unittest
from animal_scraper.scraper import WikipediaScraper

class TestWikipediaScraper(unittest.TestCase):
    def test_parse_animals(self):
        scraper = WikipediaScraper()
        html = scraper.fetch_html()
        animals = scraper.parse_animals(html)
        self.assertTrue(any("cat" in animal.name.lower() for animal in animals))
        self.assertTrue(any("feline" in animal.adjectives for animal in animals))

if __name__ == "__main__":
    unittest.main()

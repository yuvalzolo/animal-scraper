from animal_scraper.scraper import WikipediaScraper
from animal_scraper.image_downloader import ImageDownloader
from animal_scraper.html_generator import HTMLGenerator
import asyncio


def main():
    scraper = WikipediaScraper()
    html = scraper.fetch_html()
    animals = scraper.parse_animals(html)

    downloader = ImageDownloader()
    for animal in animals:
        image_path = downloader.download_image(animal.name).lower()
        animal.image_path = image_path

    html_gen = HTMLGenerator()
    html_gen.generate(animals)

if __name__ == "__main__":
    main()

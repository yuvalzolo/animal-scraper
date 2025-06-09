from scraper import WikipediaScraper
from image_downloader import ImageDownloader
from html_generator import HTMLGenerator

def main():
    scraper = WikipediaScraper()
    html = scraper.fetch_html()
    animals = scraper.parse_animals(html)

    downloader = ImageDownloader()
    for animal in animals:
        downloader.download_image(animal.name)

    html_gen = HTMLGenerator()
    html_gen.generate(animals)

if __name__ == "__main__":
    main()
